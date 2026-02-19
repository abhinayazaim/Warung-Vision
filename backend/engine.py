import numpy as np
from typing import List

class MonteCarloEngine:
    def __init__(self, num_simulations: int = 10000):
        self.num_simulations = num_simulations

    def simulate_cash_flows(self, initial_balance: float, cash_flows: List[float], days: int = 30, volatility_multiplier: float = 1.0) -> np.ndarray:
        # Calculate mean and std_dev based on history length
        if len(cash_flows) < 2:
            # Default Volatility Logic for single data point
            val = cash_flows[0] if cash_flows else 0.0
            mean_daily_flow = val
            # Default Volatility Factor of 20%
            std_dev_daily_flow = abs(val) * 0.20
        else:
            mean_daily_flow = np.mean(cash_flows)
            std_dev_daily_flow = np.std(cash_flows)

        # Apply multiplier
        std_dev_daily_flow *= volatility_multiplier

        # Generate random distribution (10,000 iterations)
        # We simulate the potential outcome of the cash flow
        # As per requirement: np.random.normal(mean, volatility, 10000)
        simulated_values = np.random.normal(mean_daily_flow, std_dev_daily_flow, self.num_simulations)
        
        # If we want to simulate "Final Balance", we add initial. 
        # But if initial_balance passed is 0, then we just get the flow distribution.
        return simulated_values + initial_balance

    def calculate_var(self, final_balances: np.ndarray, confidence_level: float = 0.95) -> float:
        # Calculate VaR (95%) as the 5th percentile of the simulated distribution.
        percentile = (1 - confidence_level) * 100
        var_value = np.percentile(final_balances, percentile)
        return float(var_value)

    def calculate_risk_score(self, final_balances: np.ndarray, initial_balance: float) -> float:
        # Risk score 0-100. Higher is safer? Or Higher is riskier?
        # Let's say Higher Score = Safer (Credit Score style).
        # Logic: Probability of ending with > 0 balance.
        
        prob_positive = np.mean(final_balances > 0)
        
        # If mean balance is growing, score is higher.
        growth_factor = np.mean(final_balances) / initial_balance if initial_balance > 0 else 1.0
        
        score = (prob_positive * 80) + (min(growth_factor, 1.5) * 13.33)
        return float(min(max(score, 0), 100))
