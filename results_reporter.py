### === results_reporter.py ===

from typing import Dict, Any, Optional


class ResultsReporter:
    """Class for reporting stock performance analysis results."""

    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize the ResultsReporter.

        Args:
            analysis_results: Dictionary containing analysis results
        """
        self.analysis_results = analysis_results

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a report from the analysis results.

        Args:
            output_path: Optional path to save the report as a text file

        Returns:
            The report as a formatted string
        """
        report_lines = []

        report_lines.append("=" * 50)
        report_lines.append("STOCK PERFORMANCE ANALYSIS REPORT")
        report_lines.append("=" * 50)

        metrics = self.analysis_results.get("metrics", {})
        assessment = self.analysis_results.get("assessment", "")

        report_lines.append("\n--- KEY METRICS ---")
        report_lines.append(f"Forward P/E: {metrics.get('forward_pe', 0):.2f}")
        report_lines.append(f"PEG Ratio: {metrics.get('peg_ratio', 0):.2f}")
        report_lines.append(f"Price to Target: {metrics.get('price_to_target', 0):.2f}")
        report_lines.append(f"Implied Share Price (DCF): {metrics.get('implied_share_price', 0):.2f}")

        report_lines.append("\n--- ASSESSMENT ---")
        report_lines.append(f"Performance Assessment: {assessment}")

        # Save to file if needed
        report_str = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(report_str)
            print(f"Report saved to {output_path}")

        return report_str

    def print_report(self) -> None:
        """
        Print the generated report to the console.
        """
        report = self.generate_report()
        print(report)


if __name__ == "__main__":
    # Example usage
    dummy_results = {
        "metrics": {
            "forward_pe": 15.3,
            "peg_ratio": 1.5,
            "price_to_target": 0.85,
            "implied_share_price": 120.0
        },
        "assessment": "Undervalued"
    }

    reporter = ResultsReporter(dummy_results)
    reporter.print_report()
