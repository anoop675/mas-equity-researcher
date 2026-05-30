import time
from crewai import Task, Crew, Process
from config import is_crypto
from agents.ticker_resolver import create_ticker_resolver_agent
from agents.data_gathering import create_data_gathering_agent
from agents.sentiment import create_sentiment_agent
from agents.financial_analyst import create_financial_analyst_agent
from agents.qa_reporter import create_qa_reporter_agent
from config import GROQ_API_KEY
import os

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


def run_equity_research(user_input: str) -> str:
    print(f"\n Please wait while I do my research...\n")

    resolver_agent = create_ticker_resolver_agent()
    data_agent = create_data_gathering_agent()
    sentiment_agent = create_sentiment_agent()
    analyst_agent = create_financial_analyst_agent()
    qa_agent = create_qa_reporter_agent()

    resolve_task = Task(
        description=f"""
            The user has requested research on: "{user_input}"

            Your job:
            1. Understand what company/asset the user is referring to.
               Examples:
               - "Apple" -> search for Apple Inc -> validate "AAPL"
               - "the EV company Elon runs" -> Tesla -> validate "TSLA"
               - "google" -> Alphabet -> validate "GOOGL"
               - "BTC" or "bitcoin" -> validate "BTC-USD"
               - "NVDA" -> directly validate "NVDA"

            2. Call search_ticker_by_name() with the company/asset name.
            3. Call validate_ticker() with the top result to confirm it exists.
            4. If the first result is wrong, try the next match.

            Return ONLY:
            - The final ticker symbol (e.g. "TSLA")
            - The full company name (e.g. "Tesla, Inc.")
            - A one-line explanation of why you chose this ticker
            - Whether it is a crypto asset (true/false)
        """,
        expected_output=(
            "A confirmed ticker symbol, full company name, "
            "one-line reasoning, and crypto flag. "
            "Example: TICKER: AAPL | NAME: Apple Inc. | "
            "REASON: User said Apple, matched Apple Inc. on NASDAQ | "
            "IS_CRYPTO: false"
        ),
        agent=resolver_agent,
    )

    data_task = Task(
        description="""
            Using the ticker resolved in the previous task:

            1. Call fetch_financial_statements() with the ticker.
            2. Call fetch_stock_price() with the ticker.
            3. Call query_10k_risks() with the ticker.

            Return all financial data in a structured format.
        """,
        expected_output=(
            "Complete financial data: statements, price, "
            "and top 5 risk factors."
        ),
        agent=data_agent,
        context=[resolve_task],
    )

    sentiment_task = Task(
        description="""
            Using the ticker resolved in the first task:

            1. Call get_yahoo_finance_news() with the ticker.
            2. Call get_google_news() with the ticker.
            3. Classify as Bullish / Neutral / Bearish with 3 reasons.
        """,
        expected_output=(
            "Sentiment classification with supporting evidence "
            "and a 2-sentence summary."
        ),
        agent=sentiment_agent,
        context=[resolve_task],
    )

    # analysis_task = Task(
    #     description="""
    #         Using financial data from the data task:
    #
    #         1. Extract FCF, beta, shares, debt, cash, growth rate.
    #         2. Calculate WACC = 0.04 + beta × 0.05
    #         3. Run run_dcf_valuation() with extracted values.
    #         4. Calculate upside vs current price.
    #         5. Issue BUY / HOLD / SELL recommendation.
    #     """,
    #     expected_output=(
    #         "DCF results, WACC, price target, and recommendation."
    #     ),
    #     agent=analyst_agent,
    #     context=[data_task],
    # )
    analysis_task = Task(
        description="""
            Using financial data from the data task:

            1. Extract these exact values:
               - free_cash_flow (use the raw number, no commas)
               - beta
               - shares_outstanding (use the raw number, no commas)
               - total_debt (use the raw number, no commas)
               - cash (use the raw number, no commas)
               - earnings_growth (use as growth_rate)

            2. Calculate WACC as a decimal number FIRST before calling the tool:
               WACC = 0.04 + beta x 0.05
               For beta=1.793: WACC = 0.04 + 1.793 x 0.05 = 0.12965
               Pass WACC as a plain decimal like 0.12965 NOT as a formula string.

            3. Run run_dcf_valuation() with terminal_growth_rate=0.03

            4. From the tool output, copy these EXACT values for the final answer:
               - enterprise_value: copy the exact number from enterprise_value field
               - equity_value: copy the exact number from equity_value field
               - intrinsic_per_share: copy the exact number from intrinsic_per_share field

            5. Calculate upside = (intrinsic_per_share / current_price) - 1
            6. BUY if upside > 0.15, HOLD if between -0.15 and 0.15, SELL if below -0.15

            Your final answer MUST include these exact lines:
            ENTERPRISE_VALUE: [number from tool]
            EQUITY_VALUE: [number from tool]
            INTRINSIC_PER_SHARE: [number from tool]
            RECOMMENDATION: [BUY/HOLD/SELL]
        """,
        expected_output=(
            "ENTERPRISE_VALUE, EQUITY_VALUE, INTRINSIC_PER_SHARE as exact numbers "
            "from the DCF tool output, plus WACC and RECOMMENDATION."
        ),
        agent=analyst_agent,
        context=[data_task],
    )

    # report_task = Task(
    #     description="""
    #         Generate the final PDF research report.
    #
    #         QA check:
    #         - Ticker and company name match
    #         - Numbers are internally consistent
    #         - Recommendation matches valuation
    #
    #         Call generate_investment_report_pdf() with all data.
    #         Return the PDF filename.
    #     """,
    #     expected_output="Path to the generated PDF file.",
    #     agent=qa_agent,
    #     context=[resolve_task, data_task, sentiment_task, analysis_task],
    # )
    report_task = Task(
        description="""
            Generate the final PDF research report.

            STEP 1 - Read exact DCF numbers:
            Call read_dcf_output() to get the exact numbers directly from file.
            Use ONLY these numbers for dcf_results. Do not use any numbers
            from the analyst agent text summary as they may contain errors.

            STEP 2 - QA consistency check:
            - target_price = intrinsic_per_share from read_dcf_output()
            - If target_price < current_price: recommendation = SELL
            - If target_price > current_price by more than 15%: recommendation = BUY
            - Otherwise: recommendation = HOLD

            STEP 3 - Generate PDF:
            Call generate_investment_report_pdf() with:
            - dcf_results using EXACTLY these keys:
              enterprise_value, intrinsic_per_share, equity_value
            - financial_highlights including:
              market_cap, revenue, net_income, free_cash_flow,
              total_debt, cash, shares_outstanding, pe_ratio, beta
            - All numbers as plain floats, no commas, no dollar signs

            Return the PDF filename.
        """,
        expected_output="Path to the generated PDF file.",
        agent=qa_agent,
        context=[resolve_task, data_task, sentiment_task, analysis_task],
    )

    crew = Crew(
        agents=[resolver_agent, data_agent, sentiment_agent, analyst_agent, qa_agent],
        tasks=[resolve_task, data_task, sentiment_task, analysis_task, report_task],
        process=Process.sequential,
        verbose=True,
        task_callback=lambda task: time.sleep(15),  # ← increased to 15s
    )

    # ── Retry up to 3 times on rate limit ──
    for attempt in range(3):
        try:
            return crew.kickoff(inputs={"user_input": user_input})
        except Exception as e:
            error = str(e).lower()
            if "rate_limit" in error or "429" in error or "too many" in error:
                wait = 60 * (attempt + 1)
                print(f"\nRate limit hit. Waiting {wait}s before retry {attempt + 1}/3...\n")
                time.sleep(wait)
            else:
                raise e

    return "Failed after 3 retries due to rate limits."