from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import numpy as np
from engine import MonteCarloEngine

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    id: str
    amount: float
    date: str
    category: str

class AnalysisRequest(BaseModel):
    history: List[Transaction]
    volatility_multiplier: float = 1.0

class AnalysisResponse(BaseModel):
    risk_score: float
    var_95: float
    risk_level: str
    credit_limit_recommendation: float

@app.get("/")
def read_root():
    return {"message": "Welcome to Warung-Vision API"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_risk(request: AnalysisRequest):
    if not request.history:
        return {
            "risk_score": 0.0,
            "var_95": 0.0,
            "risk_level": "Unknown",
            "credit_limit_recommendation": 0.0
        }

    # 1. Process Transaction History
    # Convert to numpy array for easier calculation
    # We need daily net cash flow.
    
    # Sort by date
    sorted_history = sorted(request.history, key=lambda x: x.date)
    
    # Simple day aggregation
    # Assuming date is YYYY-MM-DD
    daily_flows: dict[str, float] = {}
    for tx in sorted_history:
        date = tx.date
        amount = tx.amount # Positive for income, negative for expense
        daily_flows[date] = daily_flows.get(date, 0.0) + amount

    flows = list(daily_flows.values())
    
    # Removed length check to allow single receipt analysis
    
    initial_balance = sum(flows) # Current balance proxy (assuming starting at 0)
    # If initial balance is negative, that's bad, but let's use it.
    
    # 2. Run Monte Carlo Simulation
    engine = MonteCarloEngine(num_simulations=10000) # Updated to 10000
    # Pass initial_balance=0 to get distribution of *flows* only (Next Period Projection)
    # This aligns with the "VaR of the receipt" expectation.
    simulated_flows = engine.simulate_cash_flows(0, flows, days=30, volatility_multiplier=request.volatility_multiplier)
    
    # 3. Calculate Metrics
    var_95 = engine.calculate_var(simulated_flows, confidence_level=0.95)
    risk_score = engine.calculate_risk_score(simulated_flows, initial_balance)

    # Determine Level
    risk_level = "High"
    if risk_score > 75:
        risk_level = "Low"
    elif risk_score > 40:
        risk_level = "Medium"

    risk_score_val = float(risk_score)
    var_95_val = float(var_95)

    # Calculate Credit Limit
    # Conservative rule: Limit = (Mean Monthly Flow - VaR) * 0.5
    # If VaR is high (lots of downside), limit is lower.
    # Note: var_95 from engine is the "5th percentile value", so it might be 200k (positive) or negative.
    # If simulated_flows mean is 300k, and var_95 is 200k. Limit = (300k - (300k-200k))? No.
    # Let's say Limit = 5th Percentile Value * Leverage Factor (e.g. 3x)? No too risky.
    # Safe Limit = (Mean Flow + 5th Percentile) / 2?
    # Let's use: Limit = var_95_val (The 5th percentile outcome) * 0.8
    # If 5th percentile is < 0, Limit = 0.
    
    credit_limit = max(0.0, var_95_val * 0.8)

    return {
        "risk_score": round(risk_score_val, 1),
        "var_95": round(var_95_val, 2),
        "risk_level": risk_level,
        "credit_limit_recommendation": round(credit_limit, -4) # Round to nearest 10k roughly
    }

def var_value_to_positive_loss(var_balance, initial_balance):
    # If 5th percentile is less than initial, the difference is the Value at Risk.
    if var_balance < initial_balance:
        return initial_balance - var_balance
    return 0.0

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
