'''
A DCF (Discounted Cash Flow) model answers, "What is this company worth TODAY based on the cash it will generate in the FUTURE?"
'''
from crewai.tools import tool

import json
import os
from crewai.tools import tool

@tool("run_dcf_valuation")
def run_dcf_valuation(free_cash_flow: float, growth_rate: float, terminal_growth_rate: float,
                      wacc: float, shares_outstanding: int, total_debt: float, cash: float) -> dict:
    """Runs a 10-year DCF model. Returns intrinsic value per share and enterprise value."""

    projected_fcf = []
    fcf = free_cash_flow
    for year in range(1, 11):
        blend = year / 10
        rate = growth_rate * (1 - blend) + terminal_growth_rate * blend
        fcf = fcf * (1 + rate)
        projected_fcf.append(round(fcf, 2))

    pv_fcfs = [round(cf / (1 + wacc) ** (i + 1), 2) for i, cf in enumerate(projected_fcf)]
    terminal_value = projected_fcf[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    pv_terminal_value = round(terminal_value / (1 + wacc) ** 10, 2)
    enterprise_value = sum(pv_fcfs) + pv_terminal_value
    equity_value = enterprise_value - total_debt + cash
    intrinsic_per_share = round(equity_value / shares_outstanding, 2)

    result = {
        "enterprise_value":          round(enterprise_value, 2),
        "equity_value":              round(equity_value, 2),
        "intrinsic_per_share":       intrinsic_per_share,
        "enterprise_value_billions": round(enterprise_value / 1e9, 2),
        "equity_value_billions":     round(equity_value / 1e9, 2),
        "pv_terminal_value_billions": round(pv_terminal_value / 1e9, 2),
        "wacc_used":                 round(wacc, 5),
    }

    # Saving result to file so QA agent can read it directly
    os.makedirs("reports", exist_ok=True)
    with open("reports/dcf_output.json", "w") as f:
        json.dump(result, f)

    return result

# Add this to tools/dcf_model.py

@tool("read_dcf_output")
def read_dcf_output() -> dict:
    """
    Reads the DCF output saved by run_dcf_valuation.
    Use this to get the EXACT numbers without risk of misreading.
    """
    try:
        with open("reports/dcf_output.json", "r") as f:
            return json.load(f)
    except Exception:
        return {"error": "DCF output file not found. run_dcf_valuation has to be runned first."}