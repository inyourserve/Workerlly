from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints import users, cities, city_check, rates, categories
from app.api.v1.endpoints.seeker import jobs, salary, status, wallet, profile, location

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(profile.router, prefix="/api/v1", tags=["profile"])
app.include_router(cities.router, prefix="/api/v1", tags=["Cities"])
app.include_router(
    categories.router, prefix="/api/v1", tags=["Categories/SubCategories"]
)
app.include_router(rates.router, prefix="/api/v1", tags=["Enter Rate"])
app.include_router(status.router, prefix="/api/v1", tags=["Status on/off"])
app.include_router(salary.router, prefix="/api/v1", tags=["Calculate Salary"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(wallet.router, prefix="/api/v1", tags=["wallet"])
app.include_router(location.router, prefix="/api/v1", tags=["Location"])
