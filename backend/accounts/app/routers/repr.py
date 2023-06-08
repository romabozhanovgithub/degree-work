from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from app.core.utils import templates

router = APIRouter(prefix="/repr", tags=["repr"])


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/google")
async def google():
    return HTMLResponse("<body><a href='/auth/google/login'>Log In</a></body>")


@router.get("/google/token")
async def google_callback():
    return HTMLResponse(
        """
            <script>
                function send(){
                    var req = new XMLHttpRequest();
                    req.onreadystatechange = function() {
                        if (req.readyState === 4) {
                            console.log(req.response);
                            if (req.response["result"] === true) {
                                window.localStorage.setItem('jwt', req.response["access_token"]);
                            }
                        }
                    }
                    req.withCredentials = true;
                    req.responseType = 'json';
                    req.open("get", "/auth/google?"+window.location.search.substr(1), true);
                    req.send("");

                }
            </script>
            <button onClick="send()">Get FastAPI JWT Token</button>
        """
    )


@router.get("/deposit")
async def deposit(request: Request):
    return templates.TemplateResponse(
        "payment/deposit.html", {"request": request}
    )
