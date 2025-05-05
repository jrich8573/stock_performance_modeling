"""
Results Visualizer for Stock Performance Model

This module handles visualization of analysis results.
"""

import matplotlib.pyplot as plt
from typing import Dict, List, Any


class ResultsVisualizer:
    """Class for visualizing stock performance analysis results."""
    
    def __init__(self, ticker: str, analysis_results: Dict[str, Any], company_data: Dict):
        """
        Initialize the ResultsVisualizer.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            analysis_results: Dictionary containing analysis results
            company_data: Dictionary containing company information and financials
        """
        self.ticker = ticker
        self.analysis_results = analysis_results
        self.company_data = company_data
    
    def create_visualizations(self, output_path: str = None) -> None:
        """
        Create visualizations of analysis results.
        
        Args:
            output_path: Path to save visualizations (default: ticker_analysis.png)
        """
        if output_path is None:
            output_path = f"{self.ticker}_analysis.png"
        
        # Create subplots
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Plot stock price vs benchmark
        self._plot_stock_vs_benchmark(axs[0, 0])
        
        # 2. Plot valuation metrics vs peers
        self._plot_valuation_metrics(axs[0, 1])
        
        # 3. Plot profitability metrics vs peers
        self._plot_profitability_metrics(axs[1, 0])
        
        # 4. Plot DCF valuation breakdown
        self._plot_dcf_breakdown(axs[1, 1])
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        print(f"Visualization saved as {output_path}")
    
    def _plot_stock_vs_benchmark(self, ax) -> None:
        """Plot stock price vs benchmark performance."""
        years = [item["year"] for item in self.company_data["financials"]]
        stock_prices = [item["stock_price"] for item in self.company_data["financials"]]
        
        # Normalize to start at 100
        if stock_prices and stock_prices[-1] > 0:
            norm_factor = 100 / stock_prices[-1]
            norm_stock_prices = [price * norm_factor for price in stock_prices]
            
            # Get benchmark returns
            benchmark_returns = {}
            for item in self.analysis_results.get("benchmark_data", {}).get("market_index", []):
                benchmark_returns[item["year"]] = item["return"]
            
            # Calculate cumulative benchmark performance
            bench_perf = 100
            norm_benchmark = []
            
            for year in sorted(years):
                if year in benchmark_returns:
                    bench_perf *= (1 + benchmark_returns[year])
                norm_benchmark.append(bench_perf)
            
            ax.plot(years, norm_stock_prices, 'b-', label=f"{self.ticker} Stock Price")
            ax.plot(years, norm_benchmark, 'r--', label="S&P 500")
            ax.set_title("Stock Performance vs S&P 500 (Normalized)")
            ax.set_xlabel("Year")
            ax.set_ylabel("Normalized Value (Start=100)")
            ax.legend()
            ax.grid(True)
    
    def _plot_valuation_metrics(self, ax) -> None:
        """Plot valuation metrics comparison vs peers."""
        metrics_to_plot = ["peRatio", "priceToSales", "priceToBook", "evToEbitda"]
        metrics_data = []
        
        for metric in metrics_to_plot:
            if metric in self.analysis_results.get("peer_comparison", {}):
                metrics_data.append({
                    "metric": metric,
                    "company": self.analysis_results["peer_comparison"][metric]["company_value"],
                    "peers": self.analysis_results["peer_comparison"][metric]["peer_median"]
                })
        
        if metrics_data:
            labels = [item["metric"] for item in metrics_data]
            company_values = [item["company"] for item in metrics_data]
            peer_values = [item["peers"] for item in metrics_data]
            
            x = range(len(labels))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], company_values, width, label=self.ticker)
            ax.bar([i + width/2 for i in x], peer_values, width, label='Peer Median')
            
            ax.set_title("Valuation Metrics Comparison")
            ax.set_ylabel("Value")
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend()
            ax.grid(True)
    
    def _plot_profitability_metrics(self, ax) -> None:
        """Plot profitability metrics comparison vs peers."""
        metrics_to_plot = ["returnOnEquity", "returnOnAssets", "netMargin"]
        metrics_data = []
        
        for metric in metrics_to_plot:
            if metric in self.analysis_results.get("peer_comparison", {}):
                metrics_data.append({
                    "metric": metric,
                    "company": self.analysis_results["peer_comparison"][metric]["company_value"] * 100,  # Convert to percentage
                    "peers": self.analysis_results["peer_comparison"][metric]["peer_median"] * 100  # Convert to percentage
                })
        
        if metrics_data:
            labels = [item["metric"] for item in metrics_data]
            company_values = [item["company"] for item in metrics_data]
            peer_values = [item["peers"] for item in metrics_data]
            
            x = range(len(labels))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], company_values, width, label=self.ticker)
            ax.bar([i + width/2 for i in x], peer_values, width, label='Peer Median')
            
            ax.set_title("Profitability Metrics Comparison (%)")
            ax.set_ylabel("Percentage")
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend()
            ax.grid(True)
    
    def _plot_dcf_breakdown(self, ax) -> None:
        """Plot DCF valuation breakdown."""
        dcf_valuation = self.analysis_results.get("dcf_valuation", {})
        
        if dcf_valuation and dcf_valuation.get("present_value_cfs") and dcf_valuation.get("present_value_tv", 0) > 0:
            pv_cfs = sum(dcf_valuation["present_value_cfs"])
            pv_tv = dcf_valuation["present_value_tv"]
            debt = self.company_data["financials"][0].get("totalDebt", 0)
            
            values = [pv_cfs, pv_tv, -debt]
            labels = ['PV of Cash Flows', 'PV of Terminal Value', 'Debt']
            colors = ['green', 'blue', 'red']
            
            ax.bar(labels, values, color=colors)
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            
            # Add equity value line
            equity_value = pv_cfs + pv_tv - debt
            ax.axhline(y=equity_value, color='purple', linestyle='--', linewidth=2)
            ax.text(0, equity_value * 1.05, f"Equity Value: ${equity_value/1e9:.2f}B", color='purple')
            
            ax.set_title("DCF Valuation Breakdown (in value)")
            ax.set_ylabel("Value")
            ax.grid(True)
    
    def create_summary_visualization(self, output_path: str = None) -> None:
        """
        Create a summary visualization focusing on the underperformance assessment.
        
        Args:
            output_path: Path to save visualization (default: ticker_summary.png)
        """
        if output_path is None:
            output_path = f"{self.ticker}_summary.png"
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        
        # 1. Plot underperformance score and assessment
        score = self.analysis_results.get("underperformance_assessment", {}).get("score", 0)
        assessment = self.analysis_results.get("underperformance_assessment", {}).get("assessment", "Unknown")
        
        # Create color mapping based on score
        color_map = {
            "Significantly underperforming": "red",
            "Moderately underperforming": "orange",
            "Slightly underperforming": "yellow",
            "Performing in line with expectations": "light green",
            "Outperforming expectations": "green"
        }
        
        ax1.barh(["Underperformance Score"], [score], color=color_map.get(assessment, "gray"))
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_xlim(-5, 5)  # Set limits for the score range
        ax1.set_title("Performance Assessment")
        ax1.set_xlabel("Score (Negative is Better)")
        ax1.grid(True, axis='x')
        
        # Add assessment text
        ax1.text(score + (0.5 if score >= 0 else -0.5), 0, assessment, 
                 verticalalignment='center', fontweight='bold')
        
        # 2. Plot key factors
        factors = self.analysis_results.get("underperformance_assessment", {}).get("factors", [])
        if factors:
            y_pos = range(len(factors))
            colors = []
            
            # Determine color for each factor based on whether it's positive or negative
            for factor in factors:
                if "undervalued" in factor.lower() or "below analyst target" in factor.lower():
                    colors.append("green")
                elif "overvalued" in factor.lower() or "underperformed" in factor.lower():
                    colors.append("red")
                else:
                    colors.append("gray")
            
            # Create placeholder values for the bars (just to show the colors)
            values = [1] * len(factors)
            
            ax2.barh(y_pos, values, align='center', color=colors)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels([])  # Hide the factor text as we'll add it manually
            ax2.set_title("Key Performance Factors")
            ax2.set_xticks([])  # Hide x axis
            
            # Add the factor text manually with better formatting
            for i, factor in enumerate(factors):
                ax2.text(0.1, i, factor, verticalalignment='center')
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        print(f"Summary visualization saved as {output_path}")