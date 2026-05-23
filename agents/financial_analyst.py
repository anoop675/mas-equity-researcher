from crewai import Agent
from tools.dcf_model import run_dcf_valuation
from config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

def create_financial_analyst_agent():
    return Agent(
        role="Senior Equity Research Analyst",
        goal=(
            "Build a DCF model from the financial data provided. "
            "Calculate WACC from beta. Output: intrinsic value, "
            "price target, and BUY/HOLD/SELL recommendation."
        ),
        backstory=(
            "You are a CFA charterholder who spent 10 years at Morgan Stanley "
            "covering tech stocks. You are known for conservative assumptions "
            "and never letting narrative override the numbers."
        ),
        tools=[run_dcf_valuation],
        llm="groq/llama-3.3-70b-versatile",
        verbose=True,
        allow_delegation=False,
    )