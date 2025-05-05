import requests
import yfinance as yf
from typing import Dict, Tuple


class AnalystEstimator:
    """
    Analyst estimator using public APIs (yfinance, Alpha Vantage).
    """

    def __init__(self, ticker: str, api_key: str = "demo"):
        self.ticker = ticker
        self.api_key = api_key

    def fetch_analyst_estimates(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Fetch analyst estimates and basic company data.

        Returns:
            Tuple of (analyst estimates dict, company data dict)
        """
        estimates = {
            "next_year_eps": 0,
            "long_term_growth_rate": 0.1,
            "target_price": 0
        }
        
        company_data = {}

        # --- Attempt 1: yfinance ---
        try:
            ticker_obj = yf.Ticker(self.ticker)
            info = ticker_obj.info

            current_price = info.get("currentPrice", 0)
            next_year_eps = info.get("forwardEps") or 0
            growth_rate = info.get("earningsGrowth") or info.get("revenueGrowth") or 0.1
            target_price = info.get("targetMeanPrice") or (current_price * 1.1)

            estimates.update({
                "next_year_eps": next_year_eps,
                "long_term_growth_rate": growth_rate,
                "target_price": target_price
            })

            company_data.update({
                "shares_outstanding": info.get("sharesOutstanding", 0),
                "net_income": info.get("netIncomeToCommon", 0),
                "stock_price": current_price
            })

            print(f"Fetched analyst estimates and company data for {self.ticker} using yfinance")
            return estimates, company_data

        except Exception as e:
            print(f"yfinance fetch failed: {e}")

        # --- Attempt 2: Alpha Vantage ---
        try:
            av_endpoint = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={self.ticker}&apikey={self.api_key}"
            response = requests.get(av_endpoint)
            response.raise_for_status()
            av_data = response.json()

            if av_data:
                eps = float(av_data.get("EPS", 0))
                pe = float(av_data.get("PERatio", 0))
                target_price = float(av_data.get("AnalystTargetPrice", 0))

                growth_rate = min(pe / 15, 0.3) if pe > 0 else 0.1

                estimates.update({
                    "next_year_eps": eps * (1 + growth_rate),
                    "long_term_growth_rate": growth_rate,
                    "target_price": target_price if target_price > 0 else 0
                })

                company_data.update({
                    "shares_outstanding": float(av_data.get("SharesOutstanding", 0)),
                    "net_income": float(av_data.get("NetIncomeTTM", 0)),
                    "stock_price": float(av_data.get("PreviousClose", 0))
                })

                print(f"Fetched analyst estimates and company data for {self.ticker} using Alpha Vantage")
                return estimates, company_data

        except Exception as e:
            print(f"Alpha Vantage fetch failed: {e}")

        # --- Fallback ---
        print(f"Using default estimates for {self.ticker}")
        return estimates, company_data
