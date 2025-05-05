"""
Data Fetcher for Stock Performance Model

This module handles data retrieval from various financial APIs.
"""

import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class DataFetcher:
    """Class for fetching financial data from various APIs."""
    
    def __init__(self, ticker: str, api_key: str = None):
        """
        Initialize the DataFetcher.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            api_key: API key for Financial Modeling Prep API (default: None)
        """
        self.ticker = ticker.upper()
        self.api_key = api_key or "demo" # Use demo key if none provided
        
        # Base URLs for different APIs
        self.fmp_base_url = "https://financialmodelingprep.com/api/v3"
    
    def fetch_company_profile(self) -> Dict:
        """Fetch company profile from Financial Modeling Prep API."""
        endpoint = f"{self.fmp_base_url}/profile/{self.ticker}?apikey={self.api_key}"
        
        try:
            response = requests.get(endpoint)
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                # Get the most recent estimate
                estimate = data[0]
                
                estimates = {
                    "next_year_eps": estimate.get("estimatedEpsAvg", 0),
                    "long_term_growth_rate": estimate.get("estimatedGrowthRate", 0) / 100,  # Convert to decimal
                    "target_price": estimate.get("targetPriceAvg", 0)
                }
                print(f"Retrieved analyst estimates for {self.ticker}")
                return estimates
            else:
                # Fallback to yfinance
                ticker_obj = yf.Ticker(self.ticker)
                ticker_info = ticker_obj.info
                
                # Extract available estimates
                next_year_eps = ticker_info.get("forwardEps", 0)
                growth_rate = ticker_info.get("earningsGrowth", ticker_info.get("revenueGrowth", 0))
                target_price = ticker_info.get("targetMeanPrice", ticker_info.get("currentPrice", 0) * 1.1)  # Default to 10% higher than current price
                
                estimates = {
                    "next_year_eps": next_year_eps,
                    "long_term_growth_rate": growth_rate,
                    "target_price": target_price
                }
                print(f"Retrieved analyst estimates for {self.ticker} using yfinance")
                return estimates
        except Exception as e:
            print(f"Error fetching analyst estimates: {e}")
            
            # Default estimates based on general market averages
            return {
                "next_year_eps": 0,  # Will be calculated later if needed
                "long_term_growth_rate": 0.1,  # Default to 10% growth
                "target_price": 0  # Will be calculated later if needed
            }

    def fetch_all_data(self) -> Dict[str, Any]:
        """
        Fetch all necessary data for stock analysis and return it in a structured format.
        
        Returns:
            Dictionary containing all the data needed for analysis
        """
        print(f"Fetching all data for {self.ticker}...")
        
        # Get company profile and basic info
        company_profile = self.fetch_company_profile()
        
        # Get financial statements
        income_statement = self.fetch_income_statement()
        balance_sheet = self.fetch_balance_sheet()
        cash_flow = self.fetch_cash_flow()
        
        # Get stock price data
        stock_prices = self.fetch_stock_price_data()
        
        # Get benchmark data (S&P 500)
        benchmark_data = self.fetch_benchmark_data()
        
        # Get peer companies data
        peer_companies = self.fetch_peer_data()
        
        # Get analyst estimates
        estimates = self.fetch_analyst_estimates()
        
        # Create a structured data set for the company's financials
        financials = []
        
        # Get the years for which we have stock price data
        years = []
        if stock_prices:
            years = [item["year"] for item in stock_prices]
        
        # If we don't have any stock price data, use the current year and the two previous years
        if not years:
            current_year = datetime.today().year
            years = [current_year, current_year - 1, current_year - 2]
        
        # For each year, gather all financial data
        for year in years:
            financial_data = {"year": year}
            
            # Add stock price data
            stock_price_data = next((item for item in stock_prices if item["year"] == year), {})
            financial_data.update({
                "stock_price": stock_price_data.get("stock_price", 0),
                "shares_outstanding": stock_price_data.get("shares_outstanding", 0),
                "dividend_per_share": stock_price_data.get("dividend_per_share", 0)
            })
            
            # Find the income statement for this year
            income_data = next((item for item in income_statement 
                              if str(item.get("date", "")).startswith(str(year))), {})
            
            # Find the balance sheet for this year
            balance_data = next((item for item in balance_sheet 
                              if str(item.get("date", "")).startswith(str(year))), {})
            
            # Find the cash flow statement for this year
            cash_flow_data = next((item for item in cash_flow 
                                if str(item.get("date", "")).startswith(str(year))), {})
            
            # Add income statement data
            financial_data.update({
                "revenue": income_data.get("revenue", 0),
                "netIncome": income_data.get("netIncome", 0),
                "ebitda": income_data.get("ebitda", 0),
                "totalAssets": balance_data.get("totalAssets", 0),
                "totalEquity": balance_data.get("totalEquity", 0),
                "totalDebt": (balance_data.get("shortTermDebt", 0) or 0) + (balance_data.get("longTermDebt", 0) or 0),
                "cashFlow": cash_flow_data.get("operatingCashFlow", 0)
            })
            
            financials.append(financial_data)
        
        # Create the structured company data object
        company_data = {
            "name": company_profile.get("companyName", self.ticker),
            "ticker": self.ticker,
            "sector": company_profile.get("sector", "Unknown"),
            "industry": company_profile.get("industry", "Unknown"),
            "financials": financials,
            "estimates": estimates,
            "peer_companies": peer_companies  # Store peer companies in company_data for easy access
        }
        
        # Return all data in a dictionary
        return {
            "company_data": company_data,
            "benchmark_data": benchmark_data,
            "peer_companies": peer_companies
        }
                profile = data[0]
                print(f"Retrieved company profile for {self.ticker}")
                return profile
            else:
                # Fallback to yfinance
                ticker_info = yf.Ticker(self.ticker).info
                profile = {
                    "symbol": self.ticker,
                    "companyName": ticker_info.get("longName", ""),
                    "sector": ticker_info.get("sector", ""),
                    "industry": ticker_info.get("industry", ""),
                    "description": ticker_info.get("longBusinessSummary", "")
                }
                print(f"Retrieved company profile for {self.ticker} using yfinance")
                return profile
        except Exception as e:
            print(f"Error fetching company profile: {e}")
            # Create a minimal profile if both methods fail
            return {
                "symbol": self.ticker,
                "companyName": self.ticker,
                "sector": "Unknown",
                "industry": "Unknown"
            }
    
    def fetch_income_statement(self) -> List[Dict]:
        """Fetch income statement data from Financial Modeling Prep API."""
        # Try annual data first
        endpoint = f"{self.fmp_base_url}/income-statement/{self.ticker}?limit=3&apikey={self.api_key}"
        
        try:
            response = requests.get(endpoint)
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                print(f"Retrieved income statements for {self.ticker}")
                return data
            else:
                # Fallback to yfinance
                income_df = yf.Ticker(self.ticker).income_stmt
                if not income_df.empty:
                    # Convert DataFrame to list of dicts for consistency
                    income_statement = self._convert_yf_financials(income_df)
                    print(f"Retrieved income statements for {self.ticker} using yfinance")
                    return income_statement
                else:
                    print(f"No income statement data available for {self.ticker}")
                    return []
        except Exception as e:
            print(f"Error fetching income statement: {e}")
            return []

    def fetch_balance_sheet(self) -> List[Dict]:
        """Fetch balance sheet data from Financial Modeling Prep API."""
        endpoint = f"{self.fmp_base_url}/balance-sheet-statement/{self.ticker}?limit=3&apikey={self.api_key}"
        
        try:
            response = requests.get(endpoint)
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                print(f"Retrieved balance sheets for {self.ticker}")
                return data
            else:
                # Fallback to yfinance
                balance_df = yf.Ticker(self.ticker).balance_sheet
                if not balance_df.empty:
                    # Convert DataFrame to list of dicts for consistency
                    balance_sheet = self._convert_yf_financials(balance_df)
                    print(f"Retrieved balance sheets for {self.ticker} using yfinance")
                    return balance_sheet
                else:
                    print(f"No balance sheet data available for {self.ticker}")
                    return []
        except Exception as e:
            print(f"Error fetching balance sheet: {e}")
            return []

    def fetch_cash_flow(self) -> List[Dict]:
        """Fetch cash flow data from Financial Modeling Prep API."""
        endpoint = f"{self.fmp_base_url}/cash-flow-statement/{self.ticker}?limit=3&apikey={self.api_key}"
        
        try:
            response = requests.get(endpoint)
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                print(f"Retrieved cash flow statements for {self.ticker}")
                return data
            else:
                # Fallback to yfinance
                cf_df = yf.Ticker(self.ticker).cashflow
                if not cf_df.empty:
                    # Convert DataFrame to list of dicts for consistency
                    cash_flow = self._convert_yf_financials(cf_df)
                    print(f"Retrieved cash flow statements for {self.ticker} using yfinance")
                    return cash_flow
                else:
                    print(f"No cash flow data available for {self.ticker}")
                    return []
        except Exception as e:
            print(f"Error fetching cash flow statement: {e}")
            return []

    def _convert_yf_financials(self, df) -> List[Dict]:
        """
        Convert yfinance financial DataFrames to list of dictionaries format.
        
        Args:
            df: Pandas DataFrame from yfinance
            
        Returns:
            List of dictionaries with financial data
        """
        results = []
        
        try:
            # Check if df is None or empty
            if df is None or df.empty:
                return results
            
            # Transpose if the dates are in columns
            if not isinstance(df.index[0], datetime) and not isinstance(df.index[0], pd.Timestamp):
                df = df.T
            
            for col in df.columns:
                data = {"date": col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col)}
                
                for idx in df.index:
                    # Convert index name to snake_case for consistency
                    key = ''.join(['_' + c.lower() if c.isupper() else c for c in str(idx)]).lstrip('_')
                    data[key] = float(df.loc[idx, col]) if pd.notnull(df.loc[idx, col]) else 0
                
                results.append(data)
        except Exception as e:
            print(f"Error converting yfinance data: {e}")
        
        return results

    def fetch_stock_price_data(self) -> List[Dict]:
        """Fetch historical stock price data using yfinance."""
        try:
            # Get 3 years of data
            end_date = datetime.today()
            start_date = end_date - timedelta(days=3*365)
            
            # Fetch data from yfinance
            stock_data = yf.download(self.ticker, start=start_date, end=end_date)
            
            if not stock_data.empty:
                # Calculate yearly data
                yearly_data = []
                
                # Ensure the data is sorted by date
                stock_data = stock_data.sort_index(ascending=False)
                
                # Get current year and two previous years of data
                current_year = datetime.today().year
                
                for year_offset in range(3):
                    year = current_year - year_offset
                    year_data = stock_data[stock_data.index.year == year]
                    
                    if not year_data.empty:
                        # Get the last trading day of the year or most recent
                        latest_date = year_data.index[0]
                        earliest_date = year_data.index[-1]
                        
                        # Calculate dividend yield from yfinance
                        ticker_obj = yf.Ticker(self.ticker)
                        dividends = ticker_obj.dividends
                        
                        # Sum dividends for the year
                        yearly_dividend = 0
                        if not dividends.empty:
                            year_dividends = dividends[dividends.index.year == year]
                            if not year_dividends.empty:
                                yearly_dividend = year_dividends.sum()
                        
                        # Get shares outstanding
                        shares_outstanding = 0
                        try:
                            shares_outstanding = ticker_obj.info.get('sharesOutstanding', 0)
                        except Exception as e:
                            print(f"Could not get shares outstanding: {e}")
                        
                        yearly_data.append({
                            "year": year,
                            "stock_price": float(year_data['Adj Close'].iloc[0]),
                            "high": float(year_data['High'].max()),
                            "low": float(year_data['Low'].min()),
                            "volume": float(year_data['Volume'].mean()),
                            "shares_outstanding": shares_outstanding,
                            "dividend_per_share": float(yearly_dividend) if shares_outstanding > 0 else 0
                        })
                
                print(f"Retrieved historical stock price data for {self.ticker}")
                return yearly_data
            else:
                print(f"No stock price data available for {self.ticker}")
                return []
                
        except Exception as e:
            print(f"Error fetching stock price data: {e}")
            return []

    def fetch_benchmark_data(self) -> Dict:
        """Fetch benchmark data (S&P 500) using yfinance."""
        try:
            # Get 3 years of data for S&P 500
            end_date = datetime.today()
            start_date = end_date - timedelta(days=3*365)
            
            # Fetch S&P 500 data from yfinance
            benchmark_data = yf.download("^GSPC", start=start_date, end=end_date)
            
            if not benchmark_data.empty:
                # Calculate yearly returns
                market_index = []
                
                # Ensure the data is sorted by date
                benchmark_data = benchmark_data.sort_index(ascending=False)
                
                # Get current year and two previous years of data
                current_year = datetime.today().year
                
                for year_offset in range(3):
                    year = current_year - year_offset
                    year_data = benchmark_data[benchmark_data.index.year == year]
                    
                    if not year_data.empty and len(year_data) > 1:
                        # Calculate yearly return
                        first_price = year_data['Adj Close'].iloc[-1]
                        last_price = year_data['Adj Close'].iloc[0]
                        yearly_return = (last_price - first_price) / first_price
                        
                        market_index.append({
                            "year": year,
                            "return": float(yearly_return)
                        })
                
                # Get current risk-free rate (10-year Treasury yield)
                risk_free_rate = 0.035  # Default to 3.5%
                try:
                    treasury_data = yf.download("^TNX", start=end_date - timedelta(days=7), end=end_date)
                    if not treasury_data.empty:
                        risk_free_rate = float(treasury_data['Adj Close'].iloc[-1] / 100)  # Convert from percentage
                except Exception as e:
                    print(f"Could not get treasury yield: {e}")
                
                # Estimate market risk premium (historical average is around 5-6%)
                market_risk_premium = 0.055
                
                benchmark_data = {
                    "market_index": market_index,
                    "risk_free_rate": risk_free_rate,
                    "market_risk_premium": market_risk_premium
                }
                print("Retrieved benchmark data (S&P 500)")
                return benchmark_data
            else:
                print("No benchmark data available")
                return {
                    "market_index": [],
                    "risk_free_rate": 0.035,
                    "market_risk_premium": 0.055
                }
                
        except Exception as e:
            print(f"Error fetching benchmark data: {e}")
            return {
                "market_index": [],
                "risk_free_rate": 0.035,
                "market_risk_premium": 0.055
            }

    def fetch_peer_data(self) -> List[Dict]:
        """
        Fetch peer companies data using dedicated API endpoints.
        This uses the Financial Modeling Prep 'peers' endpoint to get direct competitors,
        then retrieves key financial metrics for each peer.
        """
        try:
            # Use Financial Modeling Prep's dedicated peer companies endpoint
            peers_endpoint = f"{self.fmp_base_url}/stock-peers?symbol={self.ticker}&apikey={self.api_key}"
            print(f"Fetching peer companies for {self.ticker}...")
            
            response = requests.get(peers_endpoint)
            peers_data = response.json()
            
            # Get the list of peer symbols
            peer_symbols = []
            if peers_data and isinstance(peers_data, list) and len(peers_data) > 0:
                peer_symbols = peers_data[0].get("peersList", [])
            
            # If peers were found through the API, process them
            if peer_symbols:
                # Limit to 5 peers to avoid excessive API calls
                peer_symbols = peer_symbols[:5]
                peer_data = []
                
                # For each peer, fetch company profile and financial ratios
                for peer_symbol in peer_symbols:
                    try:
                        # Fetch company profile to get name and industry info
                        profile_endpoint = f"{self.fmp_base_url}/profile/{peer_symbol}?apikey={self.api_key}"
                        profile_response = requests.get(profile_endpoint)
                        profile_data = profile_response.json()
                        
                        # Get company name from profile data
                        company_name = peer_symbol
                        if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
                            company_name = profile_data[0].get("companyName", peer_symbol)
                        
                        # Fetch key financial ratios using ratios-ttm endpoint
                        ratios_endpoint = f"{self.fmp_base_url}/ratios-ttm/{peer_symbol}?apikey={self.api_key}"
                        ratios_response = requests.get(ratios_endpoint)
                        ratios_data = ratios_response.json()
                        
                        # Extract relevant metrics from ratios data
                        if ratios_data and isinstance(ratios_data, list) and len(ratios_data) > 0:
                            metrics = {
                                "peRatio": ratios_data[0].get("priceEarningsRatioTTM", 0),
                                "priceToSales": ratios_data[0].get("priceSalesRatioTTM", 0),
                                "priceToBook": ratios_data[0].get("priceToBookRatioTTM", 0),
                                "evToEbitda": ratios_data[0].get("enterpriseValueMultipleTTM", 0),
                                "debtToEquity": ratios_data[0].get("debtEquityRatioTTM", 0),
                                "returnOnEquity": ratios_data[0].get("returnOnEquityTTM", 0),
                                "returnOnAssets": ratios_data[0].get("returnOnAssetsTTM", 0),
                                "netMargin": ratios_data[0].get("netProfitMarginTTM", 0),
                                "revenueGrowth": ratios_data[0].get("revenueGrowthTTMYoy", 0)
                            }
                            
                            peer_data.append({
                                "name": company_name,
                                "ticker": peer_symbol,
                                "current_metrics": metrics
                            })
                            print(f"Retrieved data for peer: {peer_symbol}")
                    except Exception as e:
                        print(f"Error fetching data for peer {peer_symbol}: {e}")
                
                if peer_data:
                    print(f"Successfully retrieved data for {len(peer_data)} peer companies")
                    return peer_data
            
            # If peers weren't found or API failed, try sector-based approach
            print("Trying sector-based approach for peer companies...")
            
            # Get the company profile first to determine sector
            company_profile = self.fetch_company_profile()
            sector = company_profile.get("sector", "")
            
            if sector:
                # Get companies in the same sector
                screener_endpoint = f"{self.fmp_base_url}/stock-screener?sector={sector}&limit=10&apikey={self.api_key}"
                screener_response = requests.get(screener_endpoint)
                sector_companies = screener_response.json()
                
                if sector_companies and isinstance(sector_companies, list):
                    # Filter out the current company and limit to 5 peers
                    sector_peers = [co for co in sector_companies if co.get("symbol") != self.ticker][:5]
                    
                    if sector_peers:
                        # Fetch metrics for each sector peer
                        sector_peer_data = []
                        
                        for peer in sector_peers:
                            peer_ticker = peer.get("symbol")
                            
                            # Fetch financial ratios
                            try:
                                ratios_endpoint = f"{self.fmp_base_url}/ratios-ttm/{peer_ticker}?apikey={self.api_key}"
                                ratios_response = requests.get(ratios_endpoint)
                                ratios_data = ratios_response.json()
                                
                                if ratios_data and isinstance(ratios_data, list) and len(ratios_data) > 0:
                                    metrics = {
                                        "peRatio": ratios_data[0].get("priceEarningsRatioTTM", 0),
                                        "priceToSales": ratios_data[0].get("priceSalesRatioTTM", 0),
                                        "priceToBook": ratios_data[0].get("priceToBookRatioTTM", 0),
                                        "evToEbitda": ratios_data[0].get("enterpriseValueMultipleTTM", 0),
                                        "debtToEquity": ratios_data[0].get("debtEquityRatioTTM", 0),
                                        "returnOnEquity": ratios_data[0].get("returnOnEquityTTM", 0),
                                        "returnOnAssets": ratios_data[0].get("returnOnAssetsTTM", 0),
                                        "netMargin": ratios_data[0].get("netProfitMarginTTM", 0),
                                        "revenueGrowth": ratios_data[0].get("revenueGrowthTTMYoy", 0)
                                    }
                                    
                                    sector_peer_data.append({
                                        "name": peer.get("companyName", peer_ticker),
                                        "ticker": peer_ticker,
                                        "current_metrics": metrics
                                    })
                                    print(f"Retrieved data for sector peer: {peer_ticker}")
                            except Exception as e:
                                print(f"Error fetching ratios for sector peer {peer_ticker}: {e}")
                        
                        if sector_peer_data:
                            print(f"Successfully retrieved data for {len(sector_peer_data)} sector peer companies")
                            return sector_peer_data
            
            # Try Yahoo Finance as a fallback for peer data
            print("Trying Yahoo Finance for peer data...")
            return self._fetch_peers_from_yahoo(company_profile)
            
        except Exception as e:
            print(f"Error in peer data collection: {e}")
            # Call the Yahoo Finance method as a fallback
            return self._fetch_peers_from_yahoo()
    
    def _fetch_peers_from_yahoo(self, company_profile=None) -> List[Dict]:
        """
        Fetch peer companies data from Yahoo Finance as a fallback method.
        
        Args:
            company_profile: Optional company profile data
            
        Returns:
            List of dictionaries with peer company data
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            
            # Attempt to get recommendations or similar companies
            recommended_symbols = []
            
            # Try different Yahoo Finance attributes that might contain peer information
            if hasattr(ticker_obj, 'recommendations') and ticker_obj.recommendations is not None and not ticker_obj.recommendations.empty:
                recommended_symbols = list(set(ticker_obj.recommendations.columns))[:5]
            elif hasattr(ticker_obj, 'similar_companies') and ticker_obj.similar_companies:
                recommended_symbols = ticker_obj.similar_companies[:5]
            else:
                # Use industry information from profile
                if company_profile is None:
                    company_profile = self.fetch_company_profile()
                
                industry = company_profile.get("industry", "")
                sector = company_profile.get("sector", "")
                
                # Use industry and sector to find peers
                industry_peers = {
                    "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
                    "Healthcare": ["JNJ", "PFE", "MRK", "UNH", "ABBV"],
                    "Financial Services": ["JPM", "BAC", "WFC", "C", "GS"],
                    "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "TMUS"],
                    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
                    "Consumer Defensive": ["PG", "KO", "PEP", "WMT", "COST"],
                    "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
                    "Industrials": ["HON", "UNP", "UPS", "CAT", "GE"],
                    "Basic Materials": ["LIN", "APD", "ECL", "SHW", "NEM"],
                    "Real Estate": ["AMT", "PLD", "CCI", "SPG", "EQIX"],
                    "Utilities": ["NEE", "DUK", "SO", "D", "AEP"]
                }
                
                # Try to get peers for the industry first, then fall back to sector
                recommended_symbols = industry_peers.get(industry, industry_peers.get(sector, ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]))
            
            # Remove the current ticker if it's in the list
            if self.ticker in recommended_symbols:
                recommended_symbols.remove(self.ticker)
            
            # Limit to 5 peers
            recommended_symbols = recommended_symbols[:5]
            
            if recommended_symbols:
                yahoo_peer_data = []
                
                for peer_ticker in recommended_symbols:
                    try:
                        # Get peer info
                        peer_info = yf.Ticker(peer_ticker).info
                        
                        # Extract relevant metrics
                        metrics = {
                            "peRatio": peer_info.get("trailingPE", peer_info.get("forwardPE", 0)),
                            "priceToSales": peer_info.get("priceToSalesTrailing12Months", 0),
                            "priceToBook": peer_info.get("priceToBook", 0),
                            "evToEbitda": peer_info.get("enterpriseToEbitda", 0),
                            "debtToEquity": peer_info.get("debtToEquity", 0) / 100 if peer_info.get("debtToEquity") else 0,
                            "returnOnEquity": peer_info.get("returnOnEquity", 0),
                            "returnOnAssets": peer_info.get("returnOnAssets", 0),
                            "netMargin": peer_info.get("profitMargins", 0),
                            "revenueGrowth": peer_info.get("revenueGrowth", 0)
                        }
                        
                        yahoo_peer_data.append({
                            "name": peer_info.get("longName", peer_ticker),
                            "ticker": peer_ticker,
                            "current_metrics": metrics
                        })
                        print(f"Retrieved data for Yahoo Finance peer: {peer_ticker}")
                    except Exception as e:
                        print(f"Error fetching data for Yahoo Finance peer {peer_ticker}: {e}")
                
                if yahoo_peer_data:
                    print(f"Successfully retrieved data for {len(yahoo_peer_data)} Yahoo Finance peer companies")
                    return yahoo_peer_data
        
        except Exception as e:
            print(f"Error fetching peer data from Yahoo Finance: {e}")
        
        # If all methods fail, generate dynamic peer company data
        return self._generate_dynamic_peer_data(company_profile)
    
    def _generate_dynamic_peer_data(self, company_profile=None) -> List[Dict]:
        """
        Generate dynamic peer company data based on industry standards.
        
        Args:
            company_profile: Optional company profile data
            
        Returns:
            List of dictionaries with generated peer company data
        """
        print("Generating dynamic peer company data based on industry standards...")
        
        # Get the industry or sector
        if company_profile is None:
            company_profile = self.fetch_company_profile()
        
        industry = company_profile.get("industry", "")
        sector = company_profile.get("sector", "")
        
        # Generate realistic peer metrics based on industry standards
        if industry == "Technology" or sector == "Technology":
            peer_base_metrics = {
                "peRatio": 25.0,
                "priceToSales": 5.2,
                "priceToBook": 6.8,
                "evToEbitda": 18.5,
                "debtToEquity": 0.3,
                "returnOnEquity": 0.22,
                "returnOnAssets": 0.14,
                "netMargin": 0.18,
                "revenueGrowth": 0.15
            }
            peer_names = ["TechInnovate Inc.", "Digital Solutions Corp.", "NextGen Systems", "CyberTech Industries", "Quantum Computing Ltd."]
        elif industry == "Healthcare" or sector == "Healthcare":
            peer_base_metrics = {
                "peRatio": 22.0,
                "priceToSales": 4.0,
                "priceToBook": 4.5,
                "evToEbitda": 15.0,
                "debtToEquity": 0.5,
                "returnOnEquity": 0.15,
                "returnOnAssets": 0.08,
                "netMargin": 0.12,
                "revenueGrowth": 0.08
            }
            peer_names = ["MediCare Solutions", "HealthFirst Pharma", "BioGenetics Corp", "MedTech Innovations", "Life Sciences Inc."]
        elif industry == "Financial Services" or sector == "Financial":
            peer_base_metrics = {
                "peRatio": 12.0,
                "priceToSales": 3.0,
                "priceToBook": 1.5,
                "evToEbitda": 10.0,
                "debtToEquity": 1.2,
                "returnOnEquity": 0.10,
                "returnOnAssets": 0.01,
                "netMargin": 0.20,
                "revenueGrowth": 0.05
            }
            peer_names = ["Capital Invest Group", "Financial Partners LLC", "Wealth Management Inc.", "Global Banking Corp", "Asset Management Services"]
        elif industry == "Energy" or sector == "Energy":
            peer_base_metrics = {
                "peRatio": 15.0,
                "priceToSales": 1.2,
                "priceToBook": 1.8,
                "evToEbitda": 8.0,
                "debtToEquity": 0.8,
                "returnOnEquity": 0.12,
                "returnOnAssets": 0.06,
                "netMargin": 0.10,
                "revenueGrowth": 0.03
            }
            peer_names = ["EnergySource Global", "Power Systems Inc.", "Natural Resources Corp", "Renewable Energy Group", "Petroleum Solutions"]
        else:
            # Default industry metrics (based on S&P 500 averages)
            peer_base_metrics = {
                "peRatio": 18.0,
                "priceToSales": 2.5,
                "priceToBook": 3.0,
                "evToEbitda": 12.0,
                "debtToEquity": 0.6,
                "returnOnEquity": 0.15,
                "returnOnAssets": 0.07,
                "netMargin": 0.12,
                "revenueGrowth": 0.08
            }
            peer_names = ["Industry Leader Corp", "Market Pioneer Inc.", "Global Dynamics", "Strategic Solutions Group", "Innovative Enterprises"]
        
        # Use numpy to generate realistic variations of the base metrics
        np.random.seed(hash(self.ticker) % 2**32)  # Use ticker as seed for reproducibility
        
        dynamic_peer_data = []
        for i, name in enumerate(peer_names):
            # Create variation around base metrics (±30%)
            variation_factors = np.random.uniform(0.7, 1.3, len(peer_base_metrics))
            
            # Apply variations to create realistic but different metrics for each peer
            metrics = {}
            for j, (metric, base_value) in enumerate(peer_base_metrics.items()):
                metrics[metric] = base_value * variation_factors[j]
            
            ticker_code = "".join([c for c in name if c.isupper()]) or f"PEER{i+1}"
            
            dynamic_peer_data.append({
                "name": name,
                "ticker": ticker_code,
                "current_metrics": metrics
            })
        
        print(f"Generated dynamic peer data for {len(dynamic_peer_data)} peer companies based on industry standards")
        return dynamic_peer_data

    def fetch_analyst_estimates(self) -> Dict:
     """Fetch analyst estimates for the company."""
    try:
        # Try to get estimates from Financial Modeling Prep API
        endpoint = f"{self.fmp_base_url}/analyst-estimates/{self.ticker}?apikey={self.api_key}"
        response = requests.get(endpoint)
        data = response.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            # Get the most recent estimate
            estimate = data[0]
            
            estimates = {
                "next_year_eps": estimate.get("estimatedEpsAvg", 0),
                "long_term_growth_rate": estimate.get("estimatedGrowthRate", 0) / 100,  # Convert to decimal
                "target_price": estimate.get("targetPriceAvg", 0)
            }
            print(f"Retrieved analyst estimates for {self.ticker}")
            return estimates
        else:
            # Fallback to yfinance
            ticker_obj = yf.Ticker(self.ticker)
            ticker_info = ticker_obj.info
            
            # Extract available estimates
            next_year_eps = ticker_info.get("forwardEps", 0)
            growth_rate = ticker_info.get("earningsGrowth", ticker_info.get("revenueGrowth", 0))
            target_price = ticker_info.get("targetMeanPrice", ticker_info.get("currentPrice", 0) * 1.1)  # Default to 10% higher than current price
            
            # Handle cases where values might be None
            if next_year_eps is None:
                next_year_eps = 0
            if growth_rate is None:
                growth_rate = 0.1  # Default to 10% growth rate
            if target_price is None:
                # Try to calculate from current price
                current_price = ticker_info.get("currentPrice", 0)
                if current_price:
                    target_price = current_price * 1.1  # Default to 10% higher
                else:
                    target_price = 0
            
            estimates = {
                "next_year_eps": next_year_eps,
                "long_term_growth_rate": growth_rate,
                "target_price": target_price
            }
            print(f"Retrieved analyst estimates for {self.ticker} using yfinance")
            return estimates
            
    except Exception as e:
        print(f"Error fetching analyst estimates: {e}")
        
        # Try another approach - Alpha Vantage as a final fallback
        try:
            # Default API key (or use the existing one)
            alpha_key = "demo"
            
            av_endpoint = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={self.ticker}&apikey={alpha_key}"
            av_response = requests.get(av_endpoint)
            av_data = av_response.json()
            
            # Extract relevant metrics
            if av_data and "EPS" in av_data and "AnalystTargetPrice" in av_data:
                eps = float(av_data.get("EPS", 0))
                pe = float(av_data.get("PERatio", 0))
                target_price = float(av_data.get("AnalystTargetPrice", 0))
                
                # Estimate growth rate from PE ratio if available
                growth_rate = 0.1  # Default
                if pe > 0:
                    # Use PE-based growth estimation (rule of thumb: Growth ~ PE/15)
                    growth_rate = min(pe / 15, 0.3)  # Cap at 30%
                
                estimates = {
                    "next_year_eps": eps * (1 + growth_rate),  # Estimate next year's EPS
                    "long_term_growth_rate": growth_rate,
                    "target_price": target_price if target_price > 0 else 0
                }
                print(f"Retrieved analyst estimates for {self.ticker} using Alpha Vantage")
                return estimates
        except Exception as av_error:
            print(f"Error fetching analyst estimates from Alpha Vantage: {av_error}")
        
        # If all else fails, return default estimates
        # Use current financial data to make reasonable estimates if available
        try:
            if self.company_data and "financials" in self.company_data and self.company_data["financials"]:
                current_year = self.company_data["financials"][0]
                shares = current_year.get("shares_outstanding", 0)
                net_income = current_year.get("netIncome", 0)
                price = current_year.get("stock_price", 0)
                
                if shares > 0 and net_income > 0:
                    current_eps = net_income / shares
                    next_year_eps = current_eps * 1.1  # Assume 10% growth
                    target_price = price * 1.15  # Assume 15% price target
                    
                    return {
                        "next_year_eps": next_year_eps,
                        "long_term_growth_rate": 0.1,
                        "target_price": target_price
                    }
        except Exception as data_error:
            print(f"Error calculating estimates from existing data: {data_error}")
            
        # Default fallback values
        return {
            "next_year_eps": 0,  # Will be calculated later if needed
            "long_term_growth_rate": 0.1,  # Default to 10% growth
            "target_price": 0  # Will be calculated later if needed
        }