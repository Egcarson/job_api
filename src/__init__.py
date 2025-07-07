from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from src.app.auth import auth
from src.app.errors import register_all_errors
from src.db.main import init_db
from src.app.router import users, jobs, application
from src.app.middlewares import register_all_middlewares


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"sever is starting ..........")
    await init_db()
    yield
    print(f"sever is shutting down ..........")
    print(f"sever has been stopped")

version = "v1.0"

app = FastAPI(
    title="Jobberman API",
    description="REST API for job search web app",
    version=version,
    lifespan=life_span,
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/mit"
    },
    contact={
        "name": "Godprevail Eseh",
        "email": "esehgodprevail@gmail.com",
        "url": "https://github.com/Egcarson?tab=repositories"
    },
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    openapi_url=f"/api/{version}/openapi.json"
)

#exception block
register_all_errors(app)
register_all_middlewares(app)

app.include_router(auth.auth_router, prefix=f'/api/{version}')
app.include_router(users.user_router, prefix=f'/api/{version}')
app.include_router(jobs.job_router, prefix=f'/api/{version}')
app.include_router(application.apps_router, prefix=f'/api/{version}')


@app.get('/')
async def root():
    return {"message": "Jobberman API"}
