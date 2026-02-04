from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import ocr, models, benchmark
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="High-performance OCR API using VLM models"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    origins_list = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    print(f"Allowed Origins: {origins_list}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["ocr"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(benchmark.router, prefix="/api/v1/benchmark", tags=["benchmark"])

@app.get("/")
def root():
    return {"message": "Welcome to VLLM-OCR API", "docs": "/docs"}
