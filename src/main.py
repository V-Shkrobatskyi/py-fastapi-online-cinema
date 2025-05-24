import uvicorn
from fastapi import FastAPI

from routes import accounts_router, profiles_router, movies_router, carts_router

app = FastAPI(
    title="Online cinema",
    description="Online Cinema project based on FastAPI and SQLAlchemy",
)

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(movies_router, prefix="/movies", tags=["movies"])
app.include_router(carts_router, prefix="/carts", tags=["carts"])


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
