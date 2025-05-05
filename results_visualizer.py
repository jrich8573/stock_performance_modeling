import matplotlib.pyplot as plt
from typing import Dict, Any


class ResultsVisualizer:
    """Class for visualizing stock performance analysis results."""

    def __init__(self, analysis_results: Dict[str, Any]):
        self.analysis_results = analysis_results

    def create_charts(self, output_path: str = None) -> None:
        """Create visualizations."""
        if output_path is None:
            output_path = "stock_analysis.png"

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))

        self._plot_financial_metrics(axs[0])
        self._plot_peer_comparison(axs[1])

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        print(f"Visualization saved to {output_path}")

    def _plot_financial_metrics(self, ax):
        """Plot key financial metrics."""
        metrics = self.analysis_results.get("company_metrics", {})

        labels = ["Forward P/E", "PEG Ratio", "ROE %", "Net Margin %", "Revenue Growth %"]
        values = [
            metrics.get("forward_pe", 0),
            metrics.get("peg_ratio", 0),
            metrics.get("return_on_equity", 0) * 100,
            metrics.get("net_margin", 0) * 100,
            metrics.get("revenue_growth", 0) * 100,
        ]

        ax.bar(labels, values)
        ax.set_title("Key Financial Metrics")
        ax.set_ylabel("Value")
        ax.grid(True, axis='y')

    def _plot_peer_comparison(self, ax):
        """Plot company vs peers."""
        peer_data = self.analysis_results.get("peer_performance", {})
        company_pe = self.analysis_results.get("company_metrics", {}).get("forward_pe", 0)
        peer_pe = peer_data.get("peer_pe_median", 0)

        company_growth = self.analysis_results.get("company_metrics", {}).get("revenue_growth", 0)
        peer_growth = peer_data.get("peer_growth_median", 0)

        labels = ["Forward P/E", "Growth Rate %"]
        company_values = [company_pe, company_growth * 100]
        peer_values = [peer_pe, peer_growth * 100]

        x = range(len(labels))
        width = 0.35

        ax.bar([i - width/2 for i in x], company_values, width, label="Company")
        ax.bar([i + width/2 for i in x], peer_values, width, label="Peer Median")
        ax.set_title("Company vs Peer Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(True, axis='y')
