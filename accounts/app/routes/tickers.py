from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils import get_current_active_user, request
from app.dependencies import get_access_token, get_db
from app.schemas import Ticker, TickerCreate
from app.models import User

router = APIRouter()



@router.post(
    "/create_ticker",
    summary="Create new ticker",
    status_code=status.HTTP_201_CREATED,
    response_model=Ticker
)
async def create_ticker(
    data: TickerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    access_token = Depends(get_access_token)
):
    """
    Create new ticker. Sends request to tickers service with access token.
    """

    new_ticker = {
        "name": data.name,
        "volume": data.volume,
        "datetime": datetime.now().isoformat(),
    }

    response = await request(
        method="POST", url="/tickers", access_token=access_token, data=new_ticker
    )

    if response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )
