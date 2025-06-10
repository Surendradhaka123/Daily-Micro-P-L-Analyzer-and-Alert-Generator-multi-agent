from typing import Dict
from pydantic import BaseModel
import json
import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

load_dotenv()

groq = Groq()



class InsightsGeneratorAgent:
    def __init__(self):
      pass

    def _build_prompt(self, date: str, anomalies: pd.DataFrame) -> str:
        prompt = f"""
                    You are a financial insights generator. Below is the anomaly report for {date} from a fulfillment center's daily financials:

                    Anomalies:
                    {anomalies.to_dict(orient='records')}

                    Each record includes:
                    - Line Item (e.g., Manpower, Packaging, CM1%, etc.)
                    - % of Revenue (actual % for the day)
                    - Target Range (expected % range)
                    - Status (always flagged if present)

                    Instructions:
                    - Mention CM1%/CM2% if they deviate and quantify the deviation.
                    - List all breaching line items and their impact.
                    - Identify top contributor(s).
                    - Write one clear, actionable recommendation.

                    Output must be 1 to 2 sentences max, in business language. Don't use any pleasantries or greetings.

                    example output: On Day 3, CM2% = 9.2% (below target). Power & Fuel = 14.1% (above max), Packaging = 8.5% (above max). Recommend reviewing energy efficiency and packaging supplier costs.
                                    On Day 5, CM1% = 61.0% (below threshold). Manpower = 29.5% (above max). Suggest reviewing staffing levels and shift optimization.
                    """
        return prompt

    def generate_insight(self, date: str, anomalies: pd.DataFrame) -> str:
        if anomalies.empty:
            return f"On {date}, all cost items were within expected thresholds."

        prompt = self._build_prompt(date, anomalies)
        chat_completion = groq.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        model="llama3-8b-8192",
        temperature=0.0,
    )
        response_text = chat_completion.choices[0].message.content.strip()
        return response_text

    def generate_all_insights(self, anomalies_df: pd.DataFrame) -> Dict[str, str]:
        insights = {}
        for date, group in anomalies_df.groupby("Date"):
            insight = self.generate_insight(date, group)
            insights[date] = insight
        return insights