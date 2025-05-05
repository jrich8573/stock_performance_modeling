### === results_visualizer.py ===

import matplotlib.pyplot as plt
from typing import Dict, Any


class ResultsVisualizer:
    """Class for visualizing stock performance analysis results."""

    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize the ResultsVisualizer.

        Args:
            analysis_results: Dictionary containing analysis results
        """
        self.analysis_results = analysis_results

    def create_charts(self, output_path: str = None) -> None:
        """
        Create simple visualizations of the analysis results.

        Args:
            output_path: Path to save the visualizations (optional)
        """
        if output_path is None:
            output_path = "analysis_chart.png"

        metrics = self.analysis_results.get("metrics", {})

        labels = ["Forward P/E", "PEG Ratio", "Price to Target", "Implied Share Price"]
        values = [
            metrics.get("forward_pe", 0),
            metrics.get("peg_ratio", 0),
            metrics.get("price_to_target", 0),
            metrics.get("implied_share_price", 0)
        ]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(labels, values, color="skyblue")
        ax.set_title("Key Valuation Metrics")
        ax.set_ylabel("Values")
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        print(f"Chart saved as {output_path}")
