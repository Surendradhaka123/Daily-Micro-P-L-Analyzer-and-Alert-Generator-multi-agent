import pandas as pd
from typing import List, Dict
from datetime import datetime
import os
from agent3 import InsightsGeneratorAgent
from alert import AlertInsightDispatcherAgent
from dotenv import load_dotenv
load_dotenv()

APP_PASSWORD = os.getenv("APP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")


#Agent 1: Data Ingestion Agent
class DataIngestionAgent:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_and_process_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.file_path)

        # Calculate CM1 and CM2
        df["CM1"] = df["Revenue"] - df["Manpower"] - df["Packaging"]
        df["CM1%"] = df["CM1"] / df["Revenue"] * 100

        df["Other Costs"] = df[["Power and Fuel", "FC Rent", "Equipment Rentals", "Overheads"]].sum(axis=1)
        df["CM2"] = df["CM1"] - df["Other Costs"]
        df["CM2%"] = df["CM2"] / df["Revenue"] * 100

        return df
    
#Agent 2: P&L Analyzer Agent
class PnLAnalyzerAgent:
    def __init__(self, log_file="flagged_anomalies_log.csv"):
        self.log_file = log_file
        self.target_ranges = {
            "Manpower": (25, 27),
            "Packaging": (5, 7),
            "Power and Fuel": (10, 12),
            "FC Rent": (15, 18),
            "Equipment Rentals": (5, 8),
            "Overheads": (10, 12),
            "CM1%": (65, 70),
            "CM2%": (15, 30),
        }

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        logs = []

        for idx, row in df.iterrows():
            revenue = row["Revenue"]
            day = row["Day"]

            for item, (low, high) in self.target_ranges.items():
                if "%" in item:
                    val = row[item]
                    threshold_low, threshold_high = (low - 3, high + 3)
                else:
                    val = (row[item] / revenue) * 100
                    threshold_low, threshold_high = low, high

                if not (threshold_low <= val <= threshold_high):
                    logs.append({
                        "Date": f"Day {day}",
                        "Line Item": item,
                        "% of Revenue": round(val, 2),
                        "Target Range": f"{low}-{high}%",
                        "Status": "Flagged"
                    })

        flagged_df = pd.DataFrame(logs)
        self.save_anomalies_log(flagged_df)

        return flagged_df
    
    def save_anomalies_log(self, df: pd.DataFrame):
        if df.empty:
            print("✅ No anomalies to log.")
            return

        if not os.path.exists(self.log_file):
            df.to_csv(self.log_file, index=False)
        else:
            existing = pd.read_csv(self.log_file)
            combined = pd.concat([existing, df], ignore_index=True)
            combined.to_csv(self.log_file, index=False)

        print(f"✅ Anomalies saved to: {self.log_file}")


# Agent 4: Alert Dispatcher Agent
class AlertDispatcherAgent:
    def dispatch_alerts(self, df: pd.DataFrame) -> List[Dict]:
        alerts = []
        for _, row in df.iterrows():
            cm2 = row["CM2%"]
            day = row["Day"]

            if cm2 < 12:
                color = "🔴"
            elif 12 <= cm2 < 15:
                color = "🟡"
            elif 15 <= cm2 <= 30:
                color = "🟢"
            else:
                color = "🔵"

            alerts.append({
                "Day": f"Day {day}",
                "CM2%": round(cm2, 2),
                "Color Code": color
            })

        return alerts



def run_case_study_pipeline(file_path: str):
    # Agent 1: Data Load
    print("------------Agent 1: Data Ingestion--------------")
    ingestion_agent = DataIngestionAgent(file_path)
    df = ingestion_agent.load_and_process_data()
    print("Data Loaded and Processed:\n", df.head())

    # Agent 2: Analysis
    print("------------Agent 2: P&L Analysis--------------")
    analyzer_agent = PnLAnalyzerAgent()
    anomaly_df = analyzer_agent.analyze(df)
    print("Flagged Anomalies:\n", anomaly_df)

    # Agent 3: Insight Generation
    print("------------Agent 3: Insights Generation--------------")
    insights_agent = InsightsGeneratorAgent()
    insights = insights_agent.generate_all_insights(anomaly_df)
    print("Generated Insights:", insights)

    # Agent 4: Alert Dispatch
    print("------------Agent 4: Alert Dispatch--------------")
    dispatcher_agent = AlertDispatcherAgent()
    alerts = dispatcher_agent.dispatch_alerts(df)

    return {
        "Processed Data": df,
        "Anomalies Log": anomaly_df,
        "Insights": insights,
        "Alerts": alerts
    }

results = run_case_study_pipeline("Entreprenuer in Residence _ EIR _ Case Study 2 - Day Wise PnL copy.csv")
alert = AlertInsightDispatcherAgent(sender_email=SENDER_EMAIL, app_password=APP_PASSWORD)
alert.dispatch_digest(results["Insights"], results["Alerts"], recipient="")