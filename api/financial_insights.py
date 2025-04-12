# api/financial_insights.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, constr
from services.fin_insight_service import get_financial_data

router = APIRouter(
    prefix="/financial_insights",
    tags=["financial_insights"],
    responses={404: {"description": "Not found"}},
)

# --- Data Models ---
class TickerInput(BaseModel):
    ticker: constr(strip_whitespace=True, to_lower=True)

@router.get("/")
async def get_financial_insights(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL)"),
    detailed: bool = Query(False, description="Get detailed financial information")
):
    try:
        ticker_input = ticker.strip().upper()
        if not ticker_input:
            raise HTTPException(status_code=400, detail="Ticker symbol cannot be empty")
            
        try:
            company_info = get_financial_data(ticker_input)
        except ValueError as ve:
            raise HTTPException(status_code=500, detail=str(ve))
        
        if company_info is None:
            raise HTTPException(status_code=404, detail=f"No data found for ticker: {ticker_input}")
            
        # Create the response
        response_data = {
            "ticker": ticker_input,
            "latest_price": company_info.get("latest_price", 0.0),
            "sentiment_summary": company_info.get("sentiment_summary", "N/A"),
            "financialHighlights": company_info.get("financialHighlights", {}),
            "rating": company_info.get("rating", "Unknown")
        }
        
        # If detailed information is requested, add more financial data
        if detailed:
            # Try to get more detailed data if available
            response_data.update({
                "income_statement": company_info.get("income_statement", {}),
                "balance_sheet": company_info.get("balance_sheet", {}),
                "cash_flow": company_info.get("cash_flow", {})
            })
            
        return response_data

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Unexpected error processing request for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")