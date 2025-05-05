"""
Stock Performance Evaluation Model with API Integration (Public API Version)

This model determines if a company's stock is underperforming by:
1. Pulling financial data from public APIs 
2. Analyzing fundamental financial metrics
3. Comparing to industry peers
4. Measuring against market benchmarks
5. Forecasting future performance

Date: May 5, 2025
"""

import os
from typing import Dict, Any, Optional

import requests
import yfinance as yf

# Import the component classes
from analyst_estimator import AnalystEstimator
from financial_analyzer import FinancialAnalyzer
from results_visualizer import ResultsVisualizer
from results_reporter import ResultsReporter


class StockPerformanceModel:
    """
    Main class that orchestrates the stock performance analysis process.
    """
    
    def __init__(self, ticker: str, api_key: str = None):
        """
        Initialize the Stock Performance Model with a ticker symbol.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            api_key: API key for Financial Modeling Prep API (optional)
        """
        self.ticker = ticker.upper()
        self.api_key = api_key or os.environ.get("FMP_API_KEY", "demo")

        # Components
        self.analyst_estimator = None
        self.financial_analyzer = None
        self.results_visualizer = None
        self.results_reporter = None
        
        # Data containers
        self.raw_data = {}
        self.analysis_results = {}
    
    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch data using public APIs (yfinance and Alpha Vantage).
        
        Returns:
            Dictionary with company data and analyst estimates
        """
        print(f"Fetching analyst and financial data for {self.ticker}...")
        
        # Fetch analyst estimates and company data
        self.analyst_estimator = AnalystEstimator(self.ticker, api_key=self.api_key)
        analyst_estimates, company_data = self.analyst_estimator.fetch_analyst_estimates()
        
        self.raw_data = {
            "analyst_estimates": analyst_estimates,
            "company_data": company_data
        }
        
        return self.raw_data
    
    def analyze_data(self) -> Dict[str, Any]:
        """
        Analyze the fetched data.
        
        Returns:
            Dictionary containing analysis results
        """
        print(f"Analyzing data for {self.ticker}...")
        
        if not self.raw_data:
            self.fetch_data()
        
        self.financial_analyzer = FinancialAnalyzer(
            company_data=self.raw_data["company_data"],
            benchmark_data={},
            peer_companies=[],
            analyst_estimates=self.raw_data["analyst_estimates"]
        )
        
        self.analysis_results = self.financial_analyzer.run_analysis()
        
        return self.analysis_results
    
    def visualize_results(self, output_path: Optional[str] = None) -> None:
        """
        Create visualizations of the analysis results.
        
        Args:
            output_path: Optional path to save visualizations
        """
        print(f"Creating visualizations for {self.ticker}...")
        
        if not self.analysis_results:
            self.analyze_data()
        
        self.results_visualizer = ResultsVisualizer(self.analysis_results)
        self.results_visualizer.create_charts(output_path)

    def report_results(self, output_path: Optional[str] = None) -> None:
        """
        Report the analysis results in a human-readable format.
        
        Args:
            output_path: Optional path to save the report
        """
        print(f"Reporting results for {self.ticker}...")
        
        if not self.analysis_results:
            self.analyze_data()
        
        self.results_reporter = ResultsReporter(self.analysis_results)
        self.results_reporter.generate_report(output_path)
    
if __name__ == "__main__":
    model = StockPerformanceModel("AAPL")
    model.fetch_data()
    model.analyze_data()
    model.visualize_results()
    model.report_results()

