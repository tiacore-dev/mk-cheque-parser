from fastapi import FastAPI

from .get_cheques_route import cheque_router


def register_routes(app: FastAPI):
    app.include_router(cheque_router, prefix="/api", tags=["Cheques"])
