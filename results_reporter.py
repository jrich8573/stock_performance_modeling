"""
Results Reporter for Stock Performance Model

This module handles reporting of analysis results.
"""

from typing import Dict, List, Any, Optional


class ResultsReporter:
    """Class for reporting stock performance analysis results."""
    
    def __init__(self, ticker: str, analysis_results: Dict[str, Any], company_data: Dict):
        """
        Initialize the ResultsReporter.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            analysis_results: Dictionary containing analysis results
            company_data: Dictionary containing company information and financials
        """
        self.ticker = ticker
        self.analysis_results = analysis_results
        self.company_data = company_data
    
    def print_results(self) -> None:
        """Print the analysis results in a readable format."""
        print("\n" + "="*40)
        print(f"STOCK PERFORMANCE ANALYSIS: {self.ticker}")
        print("="*40)
        
        print(f"\nCompany: {self.company_data['name']} ({self.ticker})")
        print(f"Sector: {self.company_data['sector']}")
        print(f"Industry: {self.company_data['industry']}")
        
        print("\n--- KEY FINANCIAL METRICS ---")
        company_metrics = self.analysis_results.get("company_metrics", {})
        if company_metrics:
            print(f"P/E Ratio: {company_metrics.get('pe_ratio', 0):.2f}")
            print(f"Forward P/E: {company_metrics.get('forward_pe', 0):.2f}")
            print(f"PEG Ratio: {company_metrics.get('peg_ratio', 0):.2f}")
            print(f"Return on Equity: {(company_metrics.get('return_on_equity', 0) * 100):.2f}%")
            print(f"Net Margin: {(company_metrics.get('net_margin', 0) * 100):.2f}%")
            print(f"Revenue Growth: {(company_metrics.get('revenue_growth', 0) * 100):.2f}%")
            print(f"Debt to Equity: {company_metrics.get('debt_to_equity', 0):.2f}")
        
        print("\n--- STOCK RETURNS ---")
        stock_returns = self.analysis_results.get("stock_returns", [])
        for year_return in stock_returns:
            print(f"Year {year_return.get('year', '')}: {(year_return.get('total_return', 0) * 100):.2f}% total return")
        
        print("\n--- ALPHA ANALYSIS ---")
        alpha_analysis = self.analysis_results.get("alpha_analysis", [])
        for year_alpha in alpha_analysis:
            print(f"Year {year_alpha.get('year', '')}: {(year_alpha.get('alpha', 0) * 100):.2f}% excess return vs market")
        
        print("\n--- DCF VALUATION ---")
        dcf_valuation = self.analysis_results.get("dcf_valuation", {})
        if dcf_valuation:
            print(f"WACC: {(dcf_valuation.get('wacc', 0) * 100):.2f}%")
            print(f"Implied Share Price: ${dcf_valuation.get('implied_share_price', 0):.2f}")
            
            # Get current price from the company data
            current_price = 0
            if self.company_data.get('financials') and len(self.company_data['financials']) > 0:
                current_price = self.company_data['financials'][0].get('stock_price', 0)
            
            print(f"Current Price: ${current_price:.2f}")
            print(f"Upside/Downside: {(dcf_valuation.get('upside', 0) * 100):.2f}%")
        
        print("\n--- PEER COMPARISON HIGHLIGHTS ---")
        peer_comparison = self.analysis_results.get("peer_comparison", {})
        for metric, comparison in peer_comparison.items():
            print(f"{metric}: {comparison.get('company_value', 0):.2f} (Peer median: {comparison.get('peer_median', 0):.2f}, "
                  f"Diff: {comparison.get('percent_difference', 0):.2f}%)")
        
        print("\n--- UNDERPERFORMANCE ASSESSMENT ---")
        underperformance_assessment = self.analysis_results.get("underperformance_assessment", {})
        if underperformance_assessment:
            print(f"Overall Assessment: {underperformance_assessment.get('assessment', '')}")
            print(f"Underperformance Score: {underperformance_assessment.get('score', 0)}")
            print("\nKey Factors:")
            for factor in underperformance_assessment.get('factors', []):
                print(f"- {factor}")
                
        # Print a summary recommendation
        print("\n--- SUMMARY RECOMMENDATION ---")
        if underperformance_assessment:
            assessment = underperformance_assessment.get('assessment', '')
            score = underperformance_assessment.get('score', 0)
            
            if score < -2:
                print("BUY: The stock is outperforming expectations and shows strong potential.")
            elif score >= -2 and score < 0:
                print("HOLD/ACCUMULATE: The stock is performing in line with expectations with some positive indicators.")
            elif score >= 0 and score < 2:
                print("HOLD/WATCH: The stock is slightly underperforming but not significantly concerning.")
            elif score >= 2 and score < 4:
                print("REDUCE: The stock is moderately underperforming and may warrant caution.")
            else:
                print("SELL/AVOID: The stock is significantly underperforming across multiple metrics.")
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a detailed investment report as a formatted string.
        
        Args:
            output_path: Optional path to save the report as a text file
            
        Returns:
            The report as a formatted string
        """
        report = []
        
        # Add report header
        report.append("="*80)
        report.append(f"INVESTMENT ANALYSIS REPORT: {self.company_data['name']} ({self.ticker})")
        report.append("="*80)
        report.append("")
        
        # Add executive summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-"*80)
        
        underperformance = self.analysis_results.get("underperformance_assessment", {})
        assessment = underperformance.get("assessment", "")
        score = underperformance.get("score", 0)
        
        # Determine recommendation based on score
        if score < -2:
            recommendation = "BUY"
            rec_rationale = "The stock is outperforming expectations and shows strong potential."
        elif score >= -2 and score < 0:
            recommendation = "HOLD/ACCUMULATE"
            rec_rationale = "The stock is performing in line with expectations with some positive indicators."
        elif score >= 0 and score < 2:
            recommendation = "HOLD/WATCH"
            rec_rationale = "The stock is slightly underperforming but not significantly concerning."
        elif score >= 2 and score < 4:
            recommendation = "REDUCE"
            rec_rationale = "The stock is moderately underperforming and may warrant caution."
        else:
            recommendation = "SELL/AVOID"
            rec_rationale = "The stock is significantly underperforming across multiple metrics."
        
        # Add recommendation and summary
        report.append(f"Recommendation: {recommendation}")
        report.append(f"Performance Assessment: {assessment}")
        report.append(f"Underperformance Score: {score}")
        report.append("")
        report.append(rec_rationale)
        report.append("")
        
        # Add key performance factors
        if underperformance.get("factors"):
            report.append("Key Performance Factors:")
            for factor in underperformance.get("factors", []):
                report.append(f"- {factor}")
            report.append("")
        
        # Add company overview
        report.append("COMPANY OVERVIEW")
        report.append("-"*80)
        report.append(f"Company: {self.company_data['name']} ({self.ticker})")
        report.append(f"Sector: {self.company_data['sector']}")
        report.append(f"Industry: {self.company_data['industry']}")
        report.append("")
        
        # Add financial metrics
        report.append("FINANCIAL METRICS")
        report.append("-"*80)
        company_metrics = self.analysis_results.get("company_metrics", {})
        if company_metrics:
            report.append(f"P/E Ratio: {company_metrics.get('pe_ratio', 0):.2f}")
            report.append(f"Forward P/E: {company_metrics.get('forward_pe', 0):.2f}")
            report.append(f"PEG Ratio: {company_metrics.get('peg_ratio', 0):.2f}")
            report.append(f"Return on Equity: {(company_metrics.get('return_on_equity', 0) * 100):.2f}%")
            report.append(f"Net Margin: {(company_metrics.get('net_margin', 0) * 100):.2f}%")
            report.append(f"Revenue Growth: {(company_metrics.get('revenue_growth', 0) * 100):.2f}%")
            report.append(f"Debt to Equity: {company_metrics.get('debt_to_equity', 0):.2f}")
            report.append(f"Dividend Yield: {(company_metrics.get('dividend_yield', 0) * 100):.2f}%")
            report.append("")
        
        # Add stock returns
        report.append("STOCK RETURNS")
        report.append("-"*80)
        stock_returns = self.analysis_results.get("stock_returns", [])
        if stock_returns:
            for year_return in stock_returns:
                report.append(f"Year {year_return.get('year', '')}: {(year_return.get('total_return', 0) * 100):.2f}% total return")
            report.append("")
        
        # Add alpha analysis
        report.append("MARKET-ADJUSTED PERFORMANCE (ALPHA)")
        report.append("-"*80)
        alpha_analysis = self.analysis_results.get("alpha_analysis", [])
        if alpha_analysis:
            for year_alpha in alpha_analysis:
                report.append(f"Year {year_alpha.get('year', '')}: {(year_alpha.get('alpha', 0) * 100):.2f}% excess return vs market")
            report.append("")
        
        # Add DCF valuation
        report.append("DISCOUNTED CASH FLOW VALUATION")
        report.append("-"*80)
        dcf_valuation = self.analysis_results.get("dcf_valuation", {})
        if dcf_valuation:
            report.append(f"WACC: {(dcf_valuation.get('wacc', 0) * 100):.2f}%")
            
            # Get projected cash flows
            if dcf_valuation.get("projected_cash_flows"):
                report.append("Projected Cash Flows:")
                for i, cf in enumerate(dcf_valuation.get("projected_cash_flows", [])):
                    report.append(f"  Year {i+1}: ${cf/1e6:.2f}M")
            
            report.append(f"Terminal Value: ${dcf_valuation.get('terminal_value', 0)/1e9:.2f}B")
            report.append(f"Enterprise Value: ${dcf_valuation.get('enterprise_value', 0)/1e9:.2f}B")
            report.append(f"Equity Value: ${dcf_valuation.get('equity_value', 0)/1e9:.2f}B")
            report.append(f"Implied Share Price: ${dcf_valuation.get('implied_share_price', 0):.2f}")
            
            # Get current price from the company data
            current_price = 0
            if self.company_data.get('financials') and len(self.company_data['financials']) > 0:
                current_price = self.company_data['financials'][0].get('stock_price', 0)
            
            report.append(f"Current Price: ${current_price:.2f}")
            report.append(f"Upside/Downside: {(dcf_valuation.get('upside', 0) * 100):.2f}%")
            report.append("")
        
        # Add peer comparison
        report.append("PEER COMPARISON")
        report.append("-"*80)
        peer_comparison = self.analysis_results.get("peer_comparison", {})
        
        # First, list the peer companies
        if self.company_data.get("peer_companies"):
            report.append("Peer Companies:")
            for peer in self.company_data.get("peer_companies", []):
                report.append(f"- {peer.get('name', '')} ({peer.get('ticker', '')})")
            report.append("")
        
        # Then, add the comparison metrics
        if peer_comparison:
            report.append("Valuation Metrics vs Peers:")
            for metric in ["peRatio", "priceToSales", "priceToBook", "evToEbitda"]:
                if metric in peer_comparison:
                    comparison = peer_comparison[metric]
                    report.append(f"{metric}: {comparison.get('company_value', 0):.2f} (Peer median: {comparison.get('peer_median', 0):.2f}, "
                               f"Diff: {comparison.get('percent_difference', 0):.2f}%)")
            report.append("")
            
            report.append("Profitability Metrics vs Peers:")
            for metric in ["returnOnEquity", "returnOnAssets", "netMargin", "revenueGrowth"]:
                if metric in peer_comparison:
                    comparison = peer_comparison[metric]
                    report.append(f"{metric}: {comparison.get('company_value', 0):.2f} (Peer median: {comparison.get('peer_median', 0):.2f}, "
                               f"Diff: {comparison.get('percent_difference', 0):.2f}%)")
            report.append("")
        
        # Add investment conclusion
        report.append("INVESTMENT CONCLUSION")
        report.append("-"*80)
        report.append(f"Recommendation: {recommendation}")
        report.append(f"Assessment: {assessment}")
        report.append("")
        report.append(rec_rationale)
        report.append("")
        
        if underperformance.get("factors"):
            report.append("Key Factors Influencing This Recommendation:")
            for factor in underperformance.get("factors", []):
                report.append(f"- {factor}")
        
        # Add disclaimer
        report.append("")
        report.append("="*80)
        report.append("DISCLAIMER")
        report.append("This report is for informational purposes only and does not constitute investment advice.")
        report.append("Always conduct your own research and consult with a financial advisor before making investment decisions.")
        report.append("="*80)
        
        # Convert report list to string
        report_str = "\n".join(report)
        
        # Save to file if output path is provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_str)
            print(f"Report saved to {output_path}")
        
        return report_str