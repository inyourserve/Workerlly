from fastapi import HTTPException, Depends

from app.api.v1.endpoints.users import get_current_user


def role_required(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if required_role not in current_user["roles"]:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user

    return role_checker
