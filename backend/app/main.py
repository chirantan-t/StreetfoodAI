"""
Main FastAPI Application Entrypoint for StreetFoodAI.
Handles CORS, database initialization, model warmup, and routing.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
torch.set_num_threads(2)

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.database.session import init_db
from backend.app.api.routes import router as api_router, get_predictor, get_nutrition_svc

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and load model into memory once
    print("Initializing StreetFoodAI backend services...")
    init_db()
    print("Database tables initialized.")

    # Warm up model and nutrition cache
    predictor = get_predictor()
    nutrition = get_nutrition_svc()
    print(f"Model ready: {predictor.model_name} ({predictor.num_classes} categories)")
    print(f"Nutrition database loaded ({len(nutrition.foods)} items)")

    yield

    # Shutdown
    print("Shutting down StreetFoodAI backend...")

app = FastAPI(
    title="StreetFoodAI API",
    description="Explainable Deep Learning Framework for Indian Street Food Recognition and Nutritional Estimation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to StreetFoodAI API",
        "docs_url": "/docs",
        "health_check": "/api/health",
        "supported_foods": "/api/foods"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
