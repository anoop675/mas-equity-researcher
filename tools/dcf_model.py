'''
A DCF (Discounted Cash Flow) model answers, "What is this company worth TODAY based on the cash it will generate in the FUTURE?"
'''
from crewai.tools import tool

@tool("run_dcf_valuation")
def run_dcf_valuation(free_cash_flow: float, growth_rate: float, terminal_growth_rate: float,
                        wacc: float, shares_outstanding: int, total_debt: float, cash: float) -> dict:
    """Runs a 10-year DCF model. Returns intrinsic value per share, enterprise value, and each year's projected cash flow"""

    # Step 1: Project FCF for 10 years
    projected_fcf = []
    fcf = free_cash_flow

    for year in range(1, 11):
        # Blend: year 1 uses full growth_rate, year 10 uses terminal
        blend = year / 10
        rate = growth_rate * (1 - blend) + terminal_growth_rate * blend
        fcf = fcf * (1 + rate)
        projected_fcf.append(round(fcf, 2))

    # Step 2: Discount each year's FCF back to today
    # PV = FCF / (1 + wacc)^year
    pv_fcfs = [round(cf / (1 + wacc) ** (i + 1), 2) for i, cf in enumerate(projected_fcf)]

    # Step 3: Terminal Value
    # Uses the Gordon Growth Model: what's the company worth AFTER year 10?
    # TV = Final FCF × (1 + g) / (wacc - g)
    terminal_value = projected_fcf[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    pv_terminal_value = round(terminal_value / (1 + wacc) ** 10, 2)

    # Step 4: Enterprise Equity Value
    enterprise_value = sum(pv_fcfs) + pv_terminal_value
    # Equity value = what belongs to shareholders
    # (enterprise value minus debt, plus cash)
    equity_value = enterprise_value - total_debt + cash
    intrinsic_per_share = round(equity_value / shares_outstanding, 2)

    return {
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "intrinsic_per_share": intrinsic_per_share,
        "enterprise_value_billions": round(enterprise_value / 1e9, 2),
        "equity_value_billions": round(equity_value / 1e9, 2),
        "pv_terminal_value_billions": round(pv_terminal_value / 1e9, 2),
        "wacc_used": round(wacc, 5),
    }