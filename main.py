import sys
import os
from dotenv import load_dotenv

api_key = os.getenv("GROQ_API_KEY", "")
if not api_key or api_key.strip() == "":
    print("ERROR: GROQ_API_KEY is missing or empty!")
    print("Set it in your .env file or as an environment variable.")
    sys.exit(1)

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["LITELLM_CACHE"] = "False"
os.environ["LITELLM_DROP_PARAMS"] = "True"  # drops unsupported params like cache_breakpoint

load_dotenv()

from orchestrator import run_equity_research

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    elif os.getenv("STOCK"):
        user_input = os.getenv("STOCK")
    else:
        user_input = "TSLA"

    print(f"\nResearching: {user_input}\n")
    result = run_equity_research(user_input)
    print(result)