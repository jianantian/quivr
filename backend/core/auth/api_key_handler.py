from datetime import datetime

from fastapi import HTTPException
from models.settings import common_dependencies
from models.users import User
from pydantic import DateError


async def verify_api_key(
    api_key: str,
) -> bool:
    try:
        # Use UTC time to avoid timezone issues
        current_date = datetime.utcnow().date()
        commons = common_dependencies()
        result = commons["db"].get_active_api_key(api_key)

        if result.data is not None and len(result.data) > 0:
            api_key_creation_date = datetime.strptime(
                result.data[0]["creation_time"], "%Y-%m-%dT%H:%M:%S"
            ).date()

            # Check if the API key was created in the month of the current date
            if (api_key_creation_date.month == current_date.month) and (
                api_key_creation_date.year == current_date.year
            ):
                return True
        return False
    except DateError:
        return False


async def get_user_from_api_key(
    api_key: str,
) -> User:
    commons = common_dependencies()

    # Lookup the user_id from the api_keys table
    user_id_data = commons["db"].get_user_id_by_api_key(api_key)

    if not user_id_data.data:
        raise HTTPException(status_code=400, detail="Invalid API key.")

    user_id = user_id_data.data[0]["user_id"]

    # Lookup the email from the users table. Todo: remove and use user_id for credentials
    user_email_data = commons["db"].get_user_email(user_id)
    email = user_email_data.data[0]["email"] if user_email_data.data else None

    return User(email=email, id=user_id)
