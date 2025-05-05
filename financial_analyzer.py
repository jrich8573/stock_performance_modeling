### === financial_analyzer.py ===

from typing import Dict, List, Any, Optional


class FinancialAnalyzer:
    """Class for analyzing financial data and calculating metrics."""

    def __init__(self, company_data: Dict, benchmark_data: Dict, peer_companies: List[Dict], analyst_estimates: Dict):
        """
        Initialize the FinancialAnalyzer.

        Args:
            company_data: Dictionary containing company information and financials
            benchmark_data: Dictionary containing market benchmark information
            peer_companies: List of dictionaries containing peer company information
            analyst_estimates: Analyst estimates dictionary
        """
        self.company_data = company_data
        self.benchmark_data = benchmark_data
        self.peer_companies = peer_companies
        self.analyst_estimates = analyst_estimates

    def run_analysis(self) -> Dict[str, Any]:
        """
        Run the financial analysis.

        Returns:
            Dictionary containing analysis results
        """
        current_price = self.company_data.get("stock_price", 0)
        shares_outstanding = self.company_data.get("shares_outstanding", 0)
        net_income = self.company_data.get("net_income", 0)

        metrics = {}

        # Basic profitability
        metrics["earnings_per_share"] = (net_income / shares_outstanding) if shares_outstanding else 0

        # Forward valuation
        next_year_eps = self.analyst_estimates.get("next_year_eps", 0)
        metrics["forward_pe"] = (current_price / next_year_eps) if next_year_eps else 0

        # PEG ratio
        growth_rate = self.analyst_estimates.get("long_term_growth_rate", 0)
        metrics["peg_ratio"] = (metrics["forward_pe"] / (growth_rate * 100)) if growth_rate else 0

        # Target price analysis
        target_price = self.analyst_estimates.get("target_price", 0)
        metrics["price_to_target"] = (current_price / target_price) if target_price else 1

        # Simple DCF estimate (5 year growth + terminal value at 10% discount rate)
        cash_flow = net_income * 1.1 if net_income else 0
        discount_rate = 0.10
        dcf_value = 0

        if cash_flow:
            for year in range(1, 6):
                cash_flow *= (1 + growth_rate)
                dcf_value += cash_flow / ((1 + discount_rate) ** year)

            terminal_value = cash_flow * (1 + 0.03) / (discount_rate - 0.03)
            dcf_value += terminal_value / ((1 + discount_rate) ** 5)

            metrics["implied_share_price"] = dcf_value / shares_outstanding if shares_outstanding else 0
        else:
            metrics["implied_share_price"] = 0

        # Performance assessment
        assessment = "Performing in line with expectations"
        if metrics["price_to_target"] < 0.8:
            assessment = "Undervalued"
        elif metrics["price_to_target"] > 1.2:
            assessment = "Overvalued"

        results = {
            "metrics": metrics,
            "assessment": assessment
        }

        return results
