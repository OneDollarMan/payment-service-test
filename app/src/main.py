from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.web import payment_router
from src.core.exceptions import PaymentNotFoundError

app = FastAPI()
app.include_router(payment_router)


@app.exception_handler(PaymentNotFoundError)
async def payment_not_found_handler(request: Request, exc: PaymentNotFoundError):
    return JSONResponse(status_code=404, content={"details": str(exc)})