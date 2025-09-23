#!/usr/bin/env python
"""
Transfer Analysis Script for P2P Backup Simulation

This script analyzes transfer patterns from simulation runs,
automatically detecting whether it's single or parallel mode and
generating appropriate plots.

Usage:
    python analyze_transfers.py <filename>

Example:
    python analyze_transfers.py year_run.npz

This will load the file from the results/ directory and generate plots
based on the mode detected in the metadata.
"""

import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
from collections import defaultdict

# Set up plotting style
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def load_metrics(filename):
    """Load metrics from .npz file efficiently."""
    # Try to load the file directly as provided first
    try:
        data = np.load(filename)
        return process_data(data)
    except FileNotFoundError:
        pass

    # Remove .npz extension if provided
    if not filename.endswith(".npz"):
        filename = f"{filename}.npz"

    try:
        data = np.load(filename)
        return process_data(data)
    except FileNotFoundError:
        logging.error(f"Error: Data file '{filename}' not found.")
        sys.exit(1)


def process_data(data):
    """Process the numpy data into the expected format."""
    # Reconstruct the data structure
    result = {
        "metadata": {
            "parallel_enabled": bool(data["metadata_parallel_enabled"][0]),
            "total_nodes": int(data["metadata_total_nodes"][0]),
            "simulation_end_time": float(data["metadata_simulation_end_time"][0]),
            "data_loss_events": int(data["metadata_data_loss_events"][0]),
            "nodes_with_data_loss": int(data["metadata_nodes_with_data_loss"][0]),
        },
        "metrics": {},
    }

    # Keep numpy arrays directly for faster processing
    result["raw_data"] = data

    # Only reconstruct transfer completions (smaller dataset)
    if "transfer_times" in data:
        result["metrics"]["transfer_completions"] = []
        for i in range(len(data["transfer_times"])):
            result["metrics"]["transfer_completions"].append(
                [
                    float(data["transfer_times"][i]),
                    str(data["transfer_types"][i]),
                    float(data["transfer_durations"][i]),
                    str(data["uploaders"][i]),
                    str(data["downloaders"][i]),
                ]
            )
    else:
        result["metrics"]["transfer_completions"] = []

    # For large datasets, just store references to numpy arrays
    result["metrics"]["bandwidth_snapshots"] = "use_raw_data"  # Signal to use raw data
    result["metrics"][
        "simultaneous_transfers"
    ] = "use_raw_data"  # Signal to use raw data

    return result


def analyze_transfers_by_node(data):
    """Analyze transfer patterns by node."""
    transfers = data["metrics"]["transfer_completions"]

    # Count transfers per node (as uploader and downloader)
    upload_counts = defaultdict(int)
    download_counts = defaultdict(int)

    for transfer in transfers:
        time, transfer_type, duration, uploader, downloader = transfer
        upload_counts[uploader] += 1
        download_counts[downloader] += 1

    return upload_counts, download_counts


def create_analysis_plot(data, filepath):
    """Create analysis plots showing the actual data."""

    transfers = data["metrics"]["transfer_completions"]
    total_transfers = len(transfers)
    total_nodes = data["metadata"]["total_nodes"]
    sim_time_years = data["metadata"]["simulation_end_time"] / (365.25 * 24 * 3600)
    raw_data = data["raw_data"]
    is_parallel = data["metadata"]["parallel_enabled"]
    mode_name = "Parallel" if is_parallel else "Single"

    # Create a 3x1 subplot layout (column format)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 16))
    fig.suptitle(
        f"{mode_name} Transfer Mode Analysis ({sim_time_years:.2f} years)",
        fontsize=16,
        fontweight="bold",
    )

    # 1. Always show cumulative transfers as the primary metric for both modes
    if transfers:
        transfer_times = [t[0] / (24 * 3600) for t in transfers]  # Convert to days
        transfer_cumulative = list(range(1, len(transfer_times) + 1))

        ax1.plot(
            transfer_times,
            transfer_cumulative,
            linewidth=2,
            alpha=0.8,
            label="Cumulative Transfers",
            color="#2E8B57",
        )

        # For parallel mode, add concurrent transfers as a secondary line
        if is_parallel and "sim_times" in raw_data and len(raw_data["sim_times"]) > 0:
            sample_step = max(1, len(raw_data["sim_times"]) // 2000)
            sim_times = raw_data["sim_times"][::sample_step] / (
                24 * 3600
            )  # Convert to days
            total_concurrent = (
                raw_data["sim_uploads"][::sample_step]
                + raw_data["sim_downloads"][::sample_step]
            )

            # Create secondary y-axis for concurrent transfers
            ax1_twin = ax1.twinx()
            ax1_twin.plot(
                sim_times,
                total_concurrent,
                linewidth=1,
                alpha=0.6,
                label="Concurrent Transfers",
                color="#FF6B6B",
                linestyle="--",
            )
            ax1_twin.set_ylabel("Concurrent Transfers", color="#FF6B6B")
            ax1_twin.tick_params(axis="y", labelcolor="#FF6B6B")

            # Add legend for both lines
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

            max_concurrent = (
                np.max(total_concurrent) if len(total_concurrent) > 0 else 0
            )
            ax1.set_title(
                f"Transfer Progress Over Time\nTotal: {total_transfers} transfers | Max Concurrent: {max_concurrent}"
            )
        else:
            ax1.set_title(
                f"Transfer Progress Over Time\nTotal: {total_transfers} transfers"
            )

        ax1.set_xlabel("Time (days)")
        ax1.set_ylabel("Cumulative Transfers")
        ax1.grid(True, alpha=0.3)

    # 2. Transfers per node
    upload_counts, download_counts = analyze_transfers_by_node(data)
    nodes = sorted(set(list(upload_counts.keys()) + list(download_counts.keys())))
    uploads = [upload_counts[node] for node in nodes]
    downloads = [download_counts[node] for node in nodes]

    x = np.arange(len(nodes))
    width = 0.35

    ax2.bar(x - width / 2, uploads, width, label="Uploads", alpha=0.8)
    ax2.bar(x + width / 2, downloads, width, label="Downloads", alpha=0.8)
    ax2.set_xlabel("Node")
    ax2.set_ylabel("Transfer Count")
    ax2.set_title("Transfers per Node")
    ax2.set_xticks(x)
    ax2.set_xticklabels(nodes, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Statistics summary
    avg_transfers_per_node = total_transfers / total_nodes if total_nodes > 0 else 0
    transfers_per_year = total_transfers / sim_time_years if sim_time_years > 0 else 0

    # Get bandwidth statistics
    avg_upload_util = 0
    avg_download_util = 0
    if "bw_times" in raw_data and len(raw_data["bw_times"]) > 0:
        sample_step = max(1, len(raw_data["bw_times"]) // 1000)
        bw_upload_used = raw_data["bw_upload_used"][::sample_step]
        bw_upload_capacity = raw_data["bw_upload_capacity"][::sample_step]
        bw_download_used = raw_data["bw_download_used"][::sample_step]
        bw_download_capacity = raw_data["bw_download_capacity"][::sample_step]

        avg_upload_util = (
            np.mean(bw_upload_used / np.maximum(bw_upload_capacity, 1)) * 100
        )
        avg_download_util = (
            np.mean(bw_download_used / np.maximum(bw_download_capacity, 1)) * 100
        )

    # Add concurrent transfer stats for parallel mode
    concurrent_stats = ""
    if is_parallel and "sim_times" in raw_data and len(raw_data["sim_times"]) > 0:
        sample_step = max(1, len(raw_data["sim_times"]) // 1000)
        concurrent_data = (
            raw_data["sim_uploads"][::sample_step]
            + raw_data["sim_downloads"][::sample_step]
        )
        max_concurrent = int(np.max(concurrent_data)) if len(concurrent_data) > 0 else 0
        avg_concurrent = (
            float(np.mean(concurrent_data)) if len(concurrent_data) > 0 else 0
        )
        concurrent_stats = f"""
    • Max Concurrent: {max_concurrent}
    • Avg Concurrent: {avg_concurrent:.1f}"""

    stats_text = f"""
    Simulation Statistics:
    • Total Transfers: {total_transfers:,}
    • Simulation Time: {sim_time_years:.2f} years
    • Total Nodes: {total_nodes}
    • Avg Transfers/Node: {avg_transfers_per_node:.1f}
    • Transfers/Year: {transfers_per_year:.1f}
    • Data Loss Events: {data['metadata']['data_loss_events']}
    """

    ax3.text(
        0.1,
        0.9,
        stats_text,
        transform=ax3.transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.5),
    )
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis("off")
    ax3.set_title("Summary Statistics")

    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches="tight")


def plot_single_mode_analysis(data, filepath):
    """Create analysis plots for single transfer mode."""
    create_analysis_plot(data, filepath)


def plot_parallel_mode_analysis(data, filepath):
    """Create analysis plots for parallel transfer mode."""
    create_analysis_plot(data, filepath)


def main():
    """Main function to analyze transfer data from a single simulation run."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        description="Analyze P2P transfer data from simulation run",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("filename", help="Simulation data file (.npz)")
    parser.add_argument(
        "--plot-name",
        action="store",
        default="plot.png",
        help="Name for the output plot",
    )
    args = parser.parse_args()

    if not args.filename:
        logging.error("Filename argument is required.")
        sys.exit(1)

    logging.info("P2P Transfer Analysis")
    logging.info("=" * 50)

    try:
        # Load the data
        data = load_metrics(args.filename)

        # Detect mode from metadata
        is_parallel = data["metadata"]["parallel_enabled"]
        mode_name = "parallel" if is_parallel else "single"

        logging.info(
            f"✓ Loaded {mode_name} mode data: {len(data['metrics']['transfer_completions'])} transfers"
        )
        logging.info(
            f"  Simulation time: {data['metadata']['simulation_end_time'] / (365.25 * 24 * 3600):.2f} years"
        )
        logging.info(f"  Total nodes: {data['metadata']['total_nodes']}")
        logging.info(f"  Data loss events: {data['metadata']['data_loss_events']}")

        logging.info(f"\nGenerating {mode_name} mode analysis plots...")

        # Generate appropriate plots based on detected mode
        if is_parallel:
            plot_parallel_mode_analysis(data, args.plot_name)
        else:
            plot_single_mode_analysis(data, args.plot_name)

        logging.info(f"\nAnalysis complete! File saved as {args.plot_name}")

    except FileNotFoundError:
        logging.error(f"Error: Data file '{args.filename}' not found.")
        logging.error("Make sure to run the simulation first and save metrics.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
