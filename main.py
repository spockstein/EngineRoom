# main.py
from fastapi import FastAPI
import uvicorn
from api.financial_insights import router as financial_insights_router
from api.stock_quote import router as stock_quote_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 7171
    CORS_ORIGINS: str

    class Config:
        env_file = ".env"

    def get_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]

# Initialize settings
settings = Settings()

app = FastAPI(
    title="Financial Insights API",
    description="API for retrieving financial insights for stocks",
    version="1.0.0"
)

# Add CORS middleware with origins from environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(financial_insights_router)
app.include_router(stock_quote_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Financial Insights API!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.APP_HOST, 
        port=settings.APP_PORT, 
        reload=True
    )

