from crewai import Agent
from tools.pdf_generator import generate_investment_report_pdf
from config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

def create_qa_reporter_agent():
    return Agent(
        role="QA Analyst & Report Writer",
        goal=(
            "Fact-check all research for consistency, then generate "
            "the final PDF investment report using all gathered data."
        ),
        backstory=(
            "You were an equity research associate at Goldman Sachs. "
            "Every report you write passes compliance review first try. "
            "You catch errors others miss and write with clarity."
        ),
        tools=[generate_investment_report_pdf],
        llm="groq/llama-3.3-70b-versatile",
        verbose=True,
        allow_delegation=False,
    )