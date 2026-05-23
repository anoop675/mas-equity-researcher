from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL, MANAGER_MODEL

def get_agent_llm():
    """Llama3 hosted on groq is used by all 4 agents"""
    return ChatGroq(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.1, # near-deterministic choice of words (for correct and consistent math calculations)
        max_tokens=4096,
    )

def get_manager_llm():
    """Used by the CrewAI orchestrator to decide which agent does what and in what order"""
    return f"groq/llama-3.3-70b-versatile"

def single_zero_shot_test_llm(prompt: str):
    """Used to test the llm (a single zero-shot inference)"""
    return f"groq/llama-3.3-70b-versatile"