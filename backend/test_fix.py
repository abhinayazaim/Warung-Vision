import numpy as np
import sys
import os

# Add current directory to path so we can import engine
sys.path.append(os.getcwd())

from engine import MonteCarloEngine

def test_single_receipt():
    flows = [306000.0]
    
    engine = MonteCarloEngine(num_simulations=10000)
    # Pass 0 to get flow distribution as per main.py update
    simulated_flows = engine.simulate_cash_flows(0, flows)
    
    var_95 = engine.calculate_var(simulated_flows, 0.95)
    
    print(f"Mean Flow: {np.mean(simulated_flows):.2f}")
    print(f"Std Dev: {np.std(simulated_flows):.2f}")
    print(f"VaR (5th percentile): {var_95:.2f}")
    
    # Expected: Roughly 200k - 250k
    # 306000 * (1 - 1.645 * 0.2) = 306000 * 0.671 = 205326
    if 180000 <= var_95 <= 260000:
        print("PASS: VaR is within expected range.")
    else:
        print("FAIL: VaR out of range.")

if __name__ == "__main__":
    test_single_receipt()
