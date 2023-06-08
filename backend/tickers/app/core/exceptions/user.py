from fastapi import HTTPException, status


class InvalidAuthorizationTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization Token",
        )
