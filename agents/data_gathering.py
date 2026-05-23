from crewai import Agent
from tools.yfinance_tool import fetch_financial_statements, fetch_stock_price
from tools.vector_store import query_10k_risks
from config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

def create_data_gathering_agent():
    return Agent(
        role="Financial Data Analyst",
        goal=(
            "Retrieve complete, accurate financial data for any stock ticker. "
            "Always fetch: financial statements, current price, AND 10-K risks."
        ),
        backstory=(
            "You are a data specialist at a quant hedge fund. "
            "You are obsessive about data accuracy — you never pass "
            "incomplete or estimated numbers downstream."
        ),
        tools=[
            fetch_financial_statements,
            fetch_stock_price,
            query_10k_risks,
        ],
        llm="groq/llama-3.3-70b-versatile",
        verbose=True, # prints agent's thinking to terminal
        allow_delegation=False, # this agent does its own work
        max_iter=5, # max tool calls before giving up
    )