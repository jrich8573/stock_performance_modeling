"""
Stock Performance Evaluation Model with API Integration

This model determines if a company's stock is underperforming by:
1. Pulling financial data from public APIs 
2. Analyzing fundamental financial metrics
3. Comparing to industry peers
4. Measuring against market benchmarks
5. Forecasting future performance

Date: May 5, 2025
"""

import os
import argparse
from typing import Dict, List, Any, Optional

# Import the component classes
from data_fetcher import DataFetcher
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
            api_key: API key for Financial Modeling Prep API (default: None)
        """
        self.ticker = ticker.upper()
        self.api_key = api_key or os.environ.get("FMP_API_KEY", "demo")
        
        # Component instances
        self.data_fetcher = None
        self.financial_analyzer = None
        self.results_visualizer = None
        self.results_reporter = None
        
        # Data and results containers
        self.raw_data = {}
        self.analysis_results = {}
    
    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch all necessary data for the analysis.
        
        Returns:
            Dictionary containing all fetched data
        """
        print(f"Fetching data for {self.ticker}...")
        
        # Create data fetcher
        self.data_fetcher = DataFetcher(self.ticker, self.api_key)
        
        # Fetch all data
        self.raw_data = self.data_fetcher.fetch_all_data()
        
        return self.raw_data
    
    def analyze_data(self) -> Dict[str, Any]:
        """
        Analyze the fetched data.
        
        Returns:
            Dictionary containing analysis results
        """
        print(f"Analyzing data for {self.ticker}...")
        
        # Ensure we have data
        if not self.raw_data:
            self.fetch_data()
        
        # Create financial analyzer
        self.financial_analyzer = FinancialAnalyzer(
            self.raw_data["company_data"],
            self.raw_data["benchmark_data"],
            self.raw_data["peer_companies"]
        )
        
        # Run analysis
        self.analysis_results = self.financial_analyzer.run_analysis()
        
        return self.analysis_results
    
    def visualize_results(self, output_path: Optional[str] = None) -> None:
        """
        Create visualizations of the analysis results.
        
        Args:
            output_path: Optional path to save visualizations
        """
        print(f"Creating visualizations for {self.ticker}...")
        
        # Ensure we have analysis results
        if not self.analysis_results:
            self.analyze_data()
        
        # Create results visualizer