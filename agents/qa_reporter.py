from crewai import Agent
from tools.pdf_generator import generate_investment_report_pdf
from config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

from tools.dcf_model import read_dcf_output
from tools.pdf_generator import generate_investment_report_pdf

def create_qa_reporter_agent():
    return Agent(
        role="QA Analyst & Report Writer",
        goal=(
            "Read the DCF output file directly, verify consistency, "
            "then generate the final PDF report."
        ),
        backstory=(
            "You were an equity research associate at Goldman Sachs. "
            "You always verify numbers from the source file before writing reports."
        ),
        tools=[read_dcf_output, generate_investment_report_pdf],
        llm="groq/llama-3.3-70b-versatile",
        verbose=True,
        allow_delegation=False,
    )