# app/main.py
# FastAPI app setup: exception handlers, middleware, and API routers.
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from app.api.v1 import router as v1_router
from app.core.exceptions import ExceptionHandler, BaseAppException
from app.utils.logger import get_logger
from app.core.middleware import JWTMiddleware
from starlette.middleware.cors import CORSMiddleware # New import

logger = get_logger()
exception_handler = ExceptionHandler(logger)

app = FastAPI()

# New CORS Middleware
origins = [
    "http://localhost:3000", # Next.js development server default
    "http://localhost:3001", # Next.js development server port in docker
    "http://localhost:3002", # Next.js development server alternate port
    "http://localhost:5173", # Vite development server
    # You can add other origins here for production or other environments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers for consistent error responses
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    return await exception_handler.handle_app_exception(request, exc)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return await exception_handler.handle_http_exception(request, exc)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return await exception_handler.handle_generic_exception(request, exc)

# No-op JWT middleware placeholder (kept in place for future auth)
app.add_middleware(JWTMiddleware)

# Versioned API router
app.include_router(v1_router.api_router, prefix="/api/v1")