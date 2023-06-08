import httpx

from app.core import settings


async def get_current_user(authorization: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.USER_INFO_URL,
            headers={"Authorization": authorization},
        )
        if response.status_code != 200:
            raise Exception(
                status_code=response.status_code,
                detail=response.json()["detail"],
            )
        return response.json()["id"]
