import os
from typing import Dict, Any, Optional, List
import yfinance as yf

from analyst_estimator import AnalystEstimator
from financial_analyzer import FinancialAnalyzer
from results_visualizer import ResultsVisualizer
from results_reporter import ResultsReporter


class StockPerformanceModel:
    def __init__(self, ticker: str, api_key: str = None):
        self.ticker = ticker.upper()
        self.api_key = api_key or os.environ.get("FMP_API_KEY", "demo")

        self.analyst_estimator = None
        self.financial_analyzer = None
        self.results_visualizer = None
        self.results_reporter = None

        self.raw_data = {}
        self.analysis_results = {}

    def fetch_data(self) -> Dict[str, Any]:
        print(f"Fetching data for {self.ticker}...")

        self.analyst_estimator = AnalystEstimator(self.ticker, api_key=self.api_key)
        analyst_estimates, company_data = self.analyst_estimator.fetch_analyst_estimates()

        self.raw_data = {
            "analyst_estimates": analyst_estimates,
            "company_data": company_data
        }

        return self.raw_data

    def fetch_peer_data(self) -> List[Dict[str, Any]]:
        """Fetch peer company metrics for comparison."""
        peers = []

        try:
            ticker_obj = yf.Ticker(self.ticker)
            industry = ticker_obj.info.get("industry", "")
            sector = ticker_obj.info.get("sector", "")

            print(f"Fetching peer companies in industry: {industry}")

            # For simplicity, use similar companies from the same sector (real version should have real peer tickers)
            sp500 = yf.Ticker("^GSPC").constituents
            potential_peers = [t for t in sp500 if t != self.ticker]

            # Select up to 5 random peers for now
            for peer_ticker in potential_peers[:5]:
                peer_estimator = AnalystEstimator(peer_ticker, api_key=self.api_key)
                analyst_estimates, company_data = peer_estimator.fetch_analyst_estimates()

                peers.append({
                    "ticker": peer_ticker,
                    "metrics": analyst_estimates,
                    "company_data": company_data
                })

        except Exception as e:
            print(f"Failed to fetch peer data: {e}")

        return peers

    def analyze_data(self) -> Dict[str, Any]:
        print(f"Analyzing data for {self.ticker}...")

        if not self.raw_data:
            self.fetch_data()

        # Fetch peer companies
        peer_data = self.fetch_peer_data()

        self.financial_analyzer = FinancialAnalyzer(
            company_data=self.raw_data["company_data"],
            benchmark_data={},
            peer_companies=peer_data,
            analyst_estimates=self.raw_data["analyst_estimates"]
        )

        self.analysis_results = self.financial_analyzer.run_analysis()

        # Compare to peers
        self.analyze_peer_performance(peer_data)

        return self.analysis_results

    def analyze_peer_performance(self, peer_data: List[Dict[str, Any]]) -> None:
        """Determine if stock is underperforming compared to peers."""
        company_pe = self.analysis_results["metrics"].get("forward_pe", 0)
        company_growth = self.analysis_results["metrics"].get("peg_ratio", 0)

        peer_pes = [peer["metrics"].get("next_year_eps", 0) for peer in peer_data if peer["metrics"].get("next_year_eps", 0) > 0]
        peer_growths = [peer["metrics"].get("long_term_growth_rate", 0) for peer in peer_data if peer["metrics"].get("long_term_growth_rate", 0) > 0]

        if peer_pes:
            peer_pe_median = sum(peer_pes) / len(peer_pes)
        else:
            peer_pe_median = 0

        if peer_growths:
            peer_growth_median = sum(peer_growths) / len(peer_growths)
        else:
            peer_growth_median = 0

        peer_assessment = "In Line"
        if company_pe > peer_pe_median * 1.2:
            peer_assessment = "Higher Valuation than Peers"
        elif company_pe < peer_pe_median * 0.8:
            peer_assessment = "Lower Valuation than Peers"

        if company_growth < peer_growth_median * 0.8:
            peer_assessment += " + Lower Growth Potential"

        self.analysis_results["peer_performance"] = {
            "peer_pe_median": peer_pe_median,
            "peer_growth_median": peer_growth_median,
            "peer_assessment": peer_assessment
        }

    def visualize_results(self, output_path: Optional[str] = None) -> None:
        if not self.analysis_results:
            self.analyze_data()

        self.results_visualizer = ResultsVisualizer(self.analysis_results)
        self.results_visualizer.create_charts(output_path)

    def report_results(self, output_path: Optional[str] = None) -> None:
        if not self.analysis_results:
            self.analyze_data()

        self.results_reporter = ResultsReporter(self.analysis_results)
        self.results_reporter.print_report()
