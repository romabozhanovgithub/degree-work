from fastapi import HTTPException, status


NOT_ENOUGH_BALANCE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Not enough balance",
)
