# Stock Performance Evaluation Model

This Python package provides a comprehensive tool for evaluating stock performance by analyzing fundamental financial metrics, comparing to industry peers, measuring against market benchmarks, and forecasting future performance.

## Features

- **Automated Data Collection**: Automatically pulls financial data from public APIs when given a ticker symbol
- **Comprehensive Analysis**: Evaluates stock performance based on multiple factors:
  - Fundamental financial metrics (P/E ratio, ROE, EPS, etc.)
  - Historical stock returns and alpha analysis
  - Peer comparison across multiple metrics
  - Discounted Cash Flow (DCF) valuation
  - Growth and profitability analysis
- **Clear Assessment**: Provides a clear underperformance/outperformance assessment with specific factors contributing to the evaluation
- **Visualization**: Generates visual representations of the analysis results
- **Portfolio Analysis**: Supports analysis of multiple stocks and portfolios

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stock-performance-model.git
cd stock-performance-model

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.8 or higher
- Required packages:
  - pandas
  - numpy
  - requests
  - yfinance
  - matplotlib

## Usage

### Basic Usage

Analyze a single stock:

```python
from stock_performance_model import StockPerformanceModel

# Create model for Apple Inc.
model = StockPerformanceModel('AAPL')

# Run analysis
results = model.run_analysis()

# Print results
model.print_results()

# Generate visualizations
model.visualize_results()
```

### Command Line Interface

The package can also be used directly from the command line:

```bash
# Basic analysis
python stock_performance_model.py AAPL

# With visualization
python stock_performance_model.py AAPL --visualize

# With API key for Financial Modeling Prep (for more data)
python stock_performance_model.py AAPL --api_key YOUR_API_KEY
```

### Advanced Usage

See `example_usage.py` for examples of:
- Analyzing individual stocks
- Comparing multiple stocks
- Performing portfolio analysis

## Data Sources

The model uses the following data sources:

1. **Primary Source**: Financial Modeling Prep API
   - Provides financial statements, ratios, and company profiles
   - Free tier available, but API key required for full functionality

2. **Fallback Source**: Yahoo Finance (yfinance package)
   - Used when Financial Modeling Prep data is not available
   - No API key required, but fewer data points

## API Keys

For optimal results, obtain a free API key from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/):

1. Sign up for an account
2. Navigate to your dashboard
3. Get your API key
4. Pass the key to the StockPerformanceModel constructor

## Interpretation of Results

The underperformance assessment provides a score and classification:

- **Below -2**: "Outperforming expectations"
- **-2 to 0**: "Performing in line with expectations"
- **0 to 2**: "Slightly underperforming"
- **2 to 4**: "Moderately underperforming"
- **Above 4**: "Significantly underperforming"

The score is calculated based on:
- Stock returns vs market benchmarks
- Valuation metrics vs peer medians
- Profitability and growth comparisons
- DCF valuation vs current price
- Current price vs analyst targets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.