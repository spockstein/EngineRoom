# main.py
from fastapi import FastAPI
import uvicorn
from api.financial_insights import router as financial_insights_router
from api.stock_quote import router as stock_quote_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Financial Insights API",
    description="API for retrieving financial insights for stocks",
    version="1.0.0"
)

# Allow CORS for specific origins
origins = [
    "https://localhost:4201",  # Allow your frontend app
    "https://127.0.0.1:4201",  # Allow your frontend app
    "https://0.0.0.0:4201",
    "https://localhost:4001",  # Allow your frontend app
    "https://127.0.0.1:4001",  # Allow your frontend app
    "https://0.0.0.0:4001",
    "https://108.35.175.76:4201",
    "https://108.35.175.76:4001",
    "https://codebuildcode:4001",
    "https://codebuildcode:4201",
    "[https://codebuildcode.com](https://codebuildcode.com):4201",
    "https://localhost",  # Allow your frontend app
    "https://127.0.0.1",  # Allow your frontend app
    "https://0.0.0.0",
    "https://localhost:4001",  # Allow your frontend app
    "https://127.0.0.1:4001",  # Allow your frontend app
    "https://0.0.0.0:4001",
    "https://108.35.175.76",
    "https://108.35.175.76:4001",
    "https://codebuildcode:4001",
    "https://codebuildcode",
    "[https://codebuildcode.com](https://codebuildcode.com)"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(financial_insights_router)
app.include_router(stock_quote_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Financial Insights API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7171, reload=True)
