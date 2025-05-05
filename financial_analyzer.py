"""
Financial Analyzer for Stock Performance Model

This module handles financial metrics calculation and analysis.
"""

from typing import Dict, List, Any, Union, Optional
import numpy as np


class FinancialAnalyzer:
    """Class for analyzing financial data and calculating metrics."""
    
    def __init__(self, company_data: Dict, benchmark_data: Dict, peer_companies: List[Dict]):
        """
        Initialize the FinancialAnalyzer.
        
        Args:
            company_data: Dictionary containing company information and financials
            benchmark_data: Dictionary containing market benchmark information
            peer_companies: List of dictionaries containing peer company information
        """
        self.company_data = company_data
        self.benchmark_data = benchmark_data
        self.peer_companies = peer_companies
        
        # Results containers
        self.company_metrics = {}
        self.stock_returns = []
        self.alpha_analysis = []
        self.peer_comparison = {}
        self.dcf_valuation = {}
        self.underperformance_assessment = {}
    
    def calculate_financial_metrics(self) -> Dict[str, float]:
        """Calculate key financial metrics for the company."""
        # Ensure we have financials
        if not self.company_data.get("financials"):
            raise ValueError("No financial data available for analysis.")
        
        current_year = self.company_data["financials"][0]
        previous_year = self.company_data["financials"][1] if len(self.company_data["financials"]) > 1 else {}
        
        # Calculate key financial ratios
        metrics = {}
        
        # Prevent division by zero
        if current_year.get("revenue", 0) > 0:
            metrics["net_margin"] = current_year.get("netIncome", 0) / current_year.get("revenue", 1)
        else:
            metrics["net_margin"] = 0
            
        if current_year.get("totalEquity", 0) > 0:
            metrics["return_on_equity"] = current_year.get("netIncome", 0) / current_year.get("totalEquity", 1)
        else:
            metrics["return_on_equity"] = 0
            
        if current_year.get("totalAssets", 0) > 0:
            metrics["return_on_assets"] = current_year.get("netIncome", 0) / current_year.get("totalAssets", 1)
        else:
            metrics["return_on_assets"] = 0
        
        # Growth metrics (if previous year data is available)
        if previous_year and previous_year.get("revenue", 0) > 0:
            metrics["revenue_growth"] = (current_year.get("revenue", 0) - previous_year.get("revenue", 0)) / previous_year.get("revenue", 1)
        else:
            metrics["revenue_growth"] = 0
            
        if previous_year and previous_year.get("netIncome", 0) > 0:
            metrics["net_income_growth"] = (current_year.get("netIncome", 0) - previous_year.get("netIncome", 0)) / previous_year.get("netIncome", 1)
        else:
            metrics["net_income_growth"] = 0
        
        # Valuation metrics
        if current_year.get("shares_outstanding", 0) > 0 and current_year.get("netIncome", 0) != 0:
            metrics["pe_ratio"] = current_year.get("stock_price", 0) / (current_year.get("netIncome", 1) / current_year.get("shares_outstanding", 1))
        else:
            metrics["pe_ratio"] = 0
            
        if current_year.get("revenue", 0) > 0:
            metrics["price_to_sales"] = (current_year.get("stock_price", 0) * current_year.get("shares_outstanding", 0)) / current_year.get("revenue", 1)
        else:
            metrics["price_to_sales"] = 0
            
        if current_year.get("totalEquity", 0) > 0:
            metrics["price_to_book"] = (current_year.get("stock_price", 0) * current_year.get("shares_outstanding", 0)) / current_year.get("totalEquity", 1)
        else:
            metrics["price_to_book"] = 0
        
        # Enterprise value
        metrics["enterprise_value"] = (current_year.get("stock_price", 0) * current_year.get("shares_outstanding", 0)) + current_year.get("totalDebt", 0)
        
        # EV/EBITDA
        if current_year.get("ebitda", 0) > 0:
            metrics["ev_to_ebitda"] = metrics["enterprise_value"] / current_year.get("ebitda", 1)
        else:
            metrics["ev_to_ebitda"] = 0
        
        # Financial health metrics
        if current_year.get("totalEquity", 0) > 0:
            metrics["debt_to_equity"] = current_year.get("totalDebt", 0) / current_year.get("totalEquity", 1)
        else:
            metrics["debt_to_equity"] = 0
            
        if self.company_data.get("estimates", {}).get("target_price", 0) > 0:
            metrics["current_price_to_target"] = current_year.get("stock_price", 0) / self.company_data.get("estimates", {}).get("target_price", 1)
        else:
            metrics["current_price_to_target"] = 1  # Default to parity
        
        # Dividend metrics
        if current_year.get("stock_price", 0) > 0:
            metrics["dividend_yield"] = current_year.get("dividend_per_share", 0) / current_year.get("stock_price", 1)
        else:
            metrics["dividend_yield"] = 0
            
        if current_year.get("netIncome", 0) > 0 and current_year.get("shares_outstanding", 0) > 0:
            metrics["payout_ratio"] = (current_year.get("dividend_per_share", 0) * current_year.get("shares_outstanding", 0)) / current_year.get("netIncome", 1)
        else:
            metrics["payout_ratio"] = 0
        
        # Calculate EPS
        if current_year.get("shares_outstanding", 0) > 0:
            metrics["earnings_per_share"] = current_year.get("netIncome", 0) / current_year.get("shares_outstanding", 1)
        else:
            metrics["earnings_per_share"] = 0
        
        # Forward P/E
        if self.company_data.get("estimates", {}).get("next_year_eps", 0) > 0:
            metrics["forward_pe"] = current_year.get("stock_price", 0) / self.company_data.get("estimates", {}).get("next_year_eps", 1)
        else:
            metrics["forward_pe"] = 0
        
        # PEG ratio
        if metrics["pe_ratio"] > 0 and self.company_data.get("estimates", {}).get("long_term_growth_rate", 0) > 0:
            metrics["peg_ratio"] = metrics["pe_ratio"] / (self.company_data.get("estimates", {}).get("long_term_growth_rate", 0.01) * 100)
        else:
            metrics["peg_ratio"] = 0
        
        return metrics
    
    def calculate_stock_returns(self) -> List[Dict[str, Union[int, float]]]:
        """Calculate stock returns over time."""
        returns = []
        
        # Ensure we have at least 2 years of data
        if len(self.company_data["financials"]) < 2:
            return returns
        
        # Calculate yearly returns
        for i in range(len(self.company_data["financials"]) - 1):
            current_year = self.company_data["financials"][i]
            previous_year = self.company_data["financials"][i + 1]
            
            # Calculate price return
            if previous_year.get("stock_price", 0) > 0:
                price_return = (current_year.get("stock_price", 0) - previous_year.get("stock_price", 0)) / previous_year.get("stock_price", 1)
            else:
                price_return = 0
            
            # Calculate dividend return
            if previous_year.get("stock_price", 0) > 0:
                dividend_return = current_year.get("dividend_per_share", 0) / previous_year.get("stock_price", 1)
            else:
                dividend_return = 0
            
            # Calculate total return
            total_return = price_return + dividend_return
            
            returns.append({
                "year": current_year.get("year"),
                "price_return": price_return,
                "dividend_return": dividend_return,
                "total_return": total_return
            })
        
        return returns
    
    def calculate_alpha(self, company_returns: List[Dict]) -> List[Dict[str, Union[int, float]]]:
        """Calculate market-adjusted returns (Alpha)."""
        alpha = []
        
        for company_return in company_returns:
            # Find matching market return for the year
            market_return = next(
                (item for item in self.benchmark_data.get("market_index", []) if item.get("year") == company_return.get("year")), 
                None
            )
            
            if market_return:
                alpha.append({
                    "year": company_return.get("year"),
                    "alpha": company_return.get("total_return", 0) - market_return.get("return", 0)
                })
        
        return alpha
    
    def compare_to_peers(self, company_metrics: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Create a peer comparison analysis."""
        peer_medians = {}
        comparison = {}
        
        # Ensure we have peer data
        if not self.peer_companies:
            return comparison
        
        # Calculate industry medians for each metric
        metric_keys = list(self.peer_companies[0].get("current_metrics", {}).keys())
        for metric in metric_keys:
            values = sorted([peer.get("current_metrics", {}).get(metric, 0) for peer in self.peer_companies])
            
            if not values:
                continue
                
            middle = len(values) // 2
            
            if len(values) % 2 == 0 and len(values) > 1:
                peer_medians[metric] = (values[middle - 1] + values[middle]) / 2
            else:
                peer_medians[metric] = values[middle]
            
            # Map snake_case metrics to camelCase for comparison
            snake_to_camel = {
                "pe_ratio": "peRatio",
                "price_to_sales": "priceToSales",
                "price_to_book": "priceToBook",
                "ev_to_ebitda": "evToEbitda",
                "debt_to_equity": "debtToEquity",
                "return_on_equity": "returnOnEquity",
                "return_on_assets": "returnOnAssets",
                "net_margin": "netMargin",
                "revenue_growth": "revenueGrowth"
            }
            
            # Find the corresponding company metric
            company_metric = metric
            if metric in snake_to_camel.values():
                company_metric = {v: k for k, v in snake_to_camel.items()}.get(metric, metric)
            elif metric in snake_to_camel:
                company_metric = snake_to_camel[metric]
            
            # Get company value, using 0 as default if not found
            company_value = company_metrics.get(company_metric, 0)
            
            # Calculate relative performance (how far from median)
            if peer_medians[metric] != 0:
                percent_difference = ((company_value - peer_medians[metric]) / peer_medians[metric]) * 100
            else:
                percent_difference = 0
            
            comparison[metric] = {
                "company_value": company_value,
                "peer_median": peer_medians[metric],
                "percent_difference": percent_difference
            }
        
        return comparison
    
    def perform_dcf(self) -> Dict[str, Union[float, List[float]]]:
        """Perform discounted cash flow valuation."""
        # Ensure we have financial data
        if not self.company_data.get("financials"):
            raise ValueError("No financial data available for DCF analysis.")
        
        current_year = self.company_data["financials"][0]
        
        # Estimate company's cost of capital (WACC)
        equity_value = current_year.get("stock_price", 0) * current_year.get("shares_outstanding", 0)
        total_capital = equity_value + current_year.get("totalDebt", 0)
        
        if total_capital > 0:
            equity_weight = equity_value / total_capital
            debt_weight = 1 - equity_weight
        else:
            equity_weight = 1
            debt_weight = 0
        
        # Simplified CAPM for cost of equity (assuming Beta = 1.2)
        beta = 1.2
        cost_of_equity = self.benchmark_data.get("risk_free_rate", 0.035) + (beta * self.benchmark_data.get("market_risk_premium", 0.055))
        
        # Assumed cost of debt (simplified)
        tax_rate = 0.25  # 25% corporate tax rate
        cost_of_debt = 0.05 * (1 - tax_rate)  # 5% pre-tax cost of debt
        
        # Calculate WACC
        wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt)
        
        # Project future cash flows (5 years)
        projected_cash_flows = []
        base_cash_flow = current_year.get("cashFlow", 0)
        
        # If cash flow is non-positive, estimate it from net income
        if base_cash_flow <= 0:
            base_cash_flow = current_year.get("netIncome", 0) * 1.1  # Assume cash flow is 10% higher than net income
        
        # If we still don't have a positive cash flow, use a default percentage of revenue
        if base_cash_flow <= 0 and current_year.get("revenue", 0) > 0:
            base_cash_flow = current_year.get("revenue", 0) * 0.1  # Assume cash flow is 10% of revenue
        
        # If still no cash flow, can't perform DCF
        if base_cash_flow <= 0:
            return {
                "wacc": wacc,
                "projected_cash_flows": [],
                "present_value_cfs": [],
                "terminal_value": 0,
                "present_value_tv": 0,
                "enterprise_value": 0,
                "equity_value": 0,
                "implied_share_price": 0,
                "upside": 0
            }
        
        for year in range(1, 6):
            # Growth rate decreases gradually from the analyst estimate to a terminal rate
            growth_rate = self.company_data.get("estimates", {}).get("long_term_growth_rate", 0.1) * \
                          (1 - ((year - 1) * 0.1))
            
            base_cash_flow = base_cash_flow * (1 + growth_rate)
            projected_cash_flows.append(base_cash_flow)
        
        # Calculate present value of projected cash flows
        present_value_cfs = [cf / ((1 + wacc) ** (index + 1)) for index, cf in enumerate(projected_cash_flows)]
        
        # Calculate terminal value (Gordon Growth Model)
        terminal_growth_rate = 0.03  # 3% long-term growth assumption
        if wacc > terminal_growth_rate:
            terminal_value = (projected_cash_flows[4] * (1 + terminal_growth_rate)) / \
                           (wacc - terminal_growth_rate)
        else:
            # Fallback if wacc is too low
            terminal_value = projected_cash_flows[4] * 20  # Assume terminal value is 20x the final year cash flow
        
        # Discount terminal value to present
        present_value_tv = terminal_value / ((1 + wacc) ** 5)
        
        # Calculate enterprise value
        enterprise_value = sum(present_value_cfs) + present_value_tv
        
        # Calculate equity value
        equity_value = enterprise_value - current_year.get("totalDebt", 0)
        
        # Calculate implied share price
        if current_year.get("shares_outstanding", 0) > 0:
            implied_share_price = equity_value / current_year.get("shares_outstanding", 1)
        else:
            implied_share_price = 0
        
        # Calculate upside/downside
        if current_year.get("stock_price", 0) > 0:
            upside = (implied_share_price - current_year.get("stock_price", 0)) / current_year.get("stock_price", 1)
        else:
            upside = 0
        
        return {
            "wacc": wacc,
            "projected_cash_flows": projected_cash_flows,
            "present_value_cfs": present_value_cfs,
            "terminal_value": terminal_value,
            "present_value_tv": present_value_tv,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "implied_share_price": implied_share_price,
            "upside": upside
        }
    
    def assess_underperformance(self) -> Dict[str, Any]:
        """Assess the stock's underperformance based on multiple factors."""
        underperformance_factors = []
        underperformance_score = 0
        
        # 1. Check recent stock returns vs market
        if self.alpha_analysis and len(self.alpha_analysis) > 0:
            recent_alpha = self.alpha_analysis[0]["alpha"]
            if recent_alpha < -0.05:
                underperformance_factors.append(
                    f"Stock has underperformed the market by {(-recent_alpha * 100):.2f}% in the most recent year"
                )
                underperformance_score += 2
            elif recent_alpha < 0:
                underperformance_factors.append(
                    f"Stock has slightly underperformed the market by {(-recent_alpha * 100):.2f}% in the most recent year"
                )
                underperformance_score += 1
        
        # 2. Check valuation metrics vs peers
        valuation_metrics = ['peRatio', 'priceToSales', 'priceToBook', 'evToEbitda']
        for metric in valuation_metrics:
            if metric in self.peer_comparison:
                comparison = self.peer_comparison[metric]
                
                # For valuation metrics, higher than peer median might indicate overvalued (worse)
                if comparison["percent_difference"] < -15:
                    underperformance_factors.append(
                        f"{metric} is {abs(comparison['percent_difference']):.2f}% below peer median, "
                        "potentially indicating undervaluation"
                    )
                    underperformance_score -= 1  # This is actually positive for valuation
                elif comparison["percent_difference"] > 15:
                    underperformance_factors.append(
                        f"{metric} is {comparison['percent_difference']:.2f}% above peer median, "
                        "potentially indicating overvaluation"
                    )
                    underperformance_score += 1
        
        # 3. Check profitability metrics vs peers
        profitability_metrics = ['returnOnEquity', 'returnOnAssets', 'netMargin']
        for metric in profitability_metrics:
            if metric in self.peer_comparison:
                comparison = self.peer_comparison[metric]
                
                # For profitability metrics, lower than peer median is worse
                if comparison["percent_difference"] < -15:
                    underperformance_factors.append(
                        f"{metric} is {abs(comparison['percent_difference']):.2f}% below peer median"
                    )
                    underperformance_score += 1
        
        # 4. Check growth metrics vs peers
        growth_metrics = ['revenueGrowth']
        for metric in growth_metrics:
            if metric in self.peer_comparison:
                comparison = self.peer_comparison[metric]
                
                # For growth metrics, lower than peer median is worse
                if comparison["percent_difference"] < -15:
                    underperformance_factors.append(
                        f"{metric} is {abs(comparison['percent_difference']):.2f}% below peer median"
                    )
                    underperformance_score += 1
        
        # 5. Check DCF valuation
        if self.dcf_valuation and "upside" in self.dcf_valuation:
            if self.dcf_valuation["upside"] > 0.15:
                underperformance_factors.append(
                    f"DCF analysis suggests stock is undervalued by {(self.dcf_valuation['upside'] * 100):.2f}%"
                )
                underperformance_score -= 2  # This is actually positive
            elif self.dcf_valuation["upside"] < -0.15:
                underperformance_factors.append(
                    f"DCF analysis suggests stock is overvalued by {(-self.dcf_valuation['upside'] * 100):.2f}%"
                )
                underperformance_score += 2
        
        # 6. Check current price vs analyst target
        if "current_price_to_target" in self.company_metrics:
            price_to_target = self.company_metrics["current_price_to_target"]
            if price_to_target < 0.8:
                underperformance_factors.append(
                    f"Current price is {((1 - price_to_target) * 100):.2f}% below analyst target price"
                )
                underperformance_score -= 1  # This is actually positive for future returns
        
        # Determine overall assessment
        if underperformance_score >= 4:
            underperformance_assessment = "Significantly underperforming"
        elif underperformance_score >= 2:
            underperformance_assessment = "Moderately underperforming"
        elif underperformance_score >= 0:
            underperformance_assessment = "Slightly underperforming"
        elif underperformance_score >= -2:
            underperformance_assessment = "Performing in line with expectations"
        else:
            underperformance_assessment = "Outperforming expectations"
        
        return {
            "assessment": underperformance_assessment,
            "score": underperformance_score,
            "factors": underperformance_factors
        }
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run the full financial analysis."""
        # Calculate all metrics
        self.company_metrics = self.calculate_financial_metrics()
        self.stock_returns = self.calculate_stock_returns()
        self.alpha_analysis = self.calculate_alpha(self.stock_returns)
        self.peer_comparison = self.compare_to_peers(self.company_metrics)
        self.dcf_valuation = self.perform_dcf()
        self.underperformance_assessment = self.assess_underperformance()
        
        return {
            "company_metrics": self.company_metrics,
            "stock_returns": self.stock_returns,
            "alpha_analysis": self.alpha_analysis,
            "peer_comparison": self.peer_comparison,
            "dcf_valuation": self.dcf_valuation,
            "underperformance_assessment": self.underperformance_assessment
        }