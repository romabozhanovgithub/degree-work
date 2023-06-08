import httpx

from app.core import settings


async def get_current_user(
    authorization: str | None = None, http_bearer: str | None = None
) -> str:
    if authorization is None and http_bearer is None:
        raise Exception(
            status_code=401,
            detail="Unauthorized",
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.VERIFY_TOKEN_URL,
            headers={"Authorization": authorization or http_bearer},
        )
        if response.status_code != 200:
            raise Exception(
                status_code=response.status_code,
                detail=response.json()["detail"],
            )
        return response.json()["id"]
