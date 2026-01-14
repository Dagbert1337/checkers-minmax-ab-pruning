import matplotlib.pyplot as plt
import pandas as pd
import re
import os
from typing import Optional

def parse_checkers_data(filename: str) -> pd.DataFrame:
    """
    Parses the checkers text data file into a Pandas DataFrame.
    
    Expected file format lines:
    - "Data for [heuristic_name] :"
    - "FOR DEPTH=[int]"
    - "FOR COLOR=[WHITE/BLACK]"
    - "rates : wins : [float], loses : [float], draws : [float]"
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return pd.DataFrame()

    data_list = []
    
    current_heuristic: Optional[str] = None
    current_depth: Optional[int] = None
    current_color: Optional[str] = None

    with open(filename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Detect Heuristic Name
        if line.startswith("Data for"):
            # Example: "Data for random_score :" -> "random_score"
            current_heuristic = line.split("Data for ")[1].replace(" :", "")

        # Detect Depth
        elif line.startswith("FOR DEPTH="):
            current_depth = int(line.split("=")[1])

        # Detect Color
        elif line.startswith("FOR COLOR="):
            current_color = line.split("=")[1]

        elif line.startswith("rates :"):
            # specific pattern to capture all 3 numbers at once
            match = re.search(r'wins : ([\d\.]+), loses : ([\d\.]+), draws : ([\d\.]+)', line)
            
            if match:
                wins = float(match.group(1))
                loses = float(match.group(2))
                draws = float(match.group(3))

                data_list.append({
                    "Heuristic": current_heuristic,
                    "Depth": current_depth,
                    "Color": current_color,
                    "Win Rate": wins,
                    "Loss Rate": loses,
                    "Draw Rate": draws
                })
            else:
                print(f"Warning: Could not parse rates line: {line}")
                
    return pd.DataFrame(data_list)


def plot_average_performance(df: pd.DataFrame):
    """
    Plot 1: Average Win Rate for each Heuristic (Bar Chart).
    Aggregates data across all depths and colors.
    """
    if df.empty: return

    # Group by Heuristic and calculate mean Win Rate
    heuristic_performance = df.groupby("Heuristic")["Win Rate"].mean().sort_values()

    plt.figure(figsize=(10, 6))
    bars = heuristic_performance.plot(kind='bar', color='skyblue', edgecolor='black')
    
    plt.title('Average Heuristic Performance (Win Rate)', fontsize=14)
    plt.ylabel('Average Win Rate (0.0 - 1.0)')
    plt.xlabel('Heuristic')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add numeric labels above bars
    for i, v in enumerate(heuristic_performance):
        plt.text(i, v + 0.01, f"{v:.2f}", ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('heuristic_performance.png')


def plot_depth_impact(df: pd.DataFrame):
    """
    Plot 2: Impact of Search Depth on Win Rate (Line Chart).
    Shows how 'thinking deeper' affects each heuristic.
    """
    if df.empty: return

    # Pivot table: Rows=Depth, Columns=Heuristic, Values=Win Rate
    pivot_depth = df.groupby(["Heuristic", "Depth"])["Win Rate"].mean().unstack(level=0)

    plt.figure(figsize=(10, 6))
    
    for column in pivot_depth.columns:
        plt.plot(pivot_depth.index, pivot_depth[column], marker='o', label=column, linewidth=2)

    plt.title('Impact of Search Depth on Win Rate', fontsize=14)
    plt.xlabel('Search Depth')
    plt.ylabel('Average Win Rate')
    plt.xticks(pivot_depth.index)  # Ensure x-axis shows integer depths
    plt.legend(title="Heuristic")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('depth_on_win_influence.png')


def plot_color_balance(df: pd.DataFrame):
    """
    Plot 3: Color Balance Analysis (Grouped Bar Chart).
    Compares Win Rate when playing as White vs Black.
    """
    if df.empty: return

    # Group by Heuristic and Color
    color_performance = df.groupby(["Heuristic", "Color"])["Win Rate"].mean().unstack()

    # Plot
    ax = color_performance.plot(kind='bar', figsize=(12, 6), color=['black', '#f0f0f0'], edgecolor='black')
    
    plt.title('Color Balance: Win Rate by Color', fontsize=14)
    plt.ylabel('Win Rate')
    plt.xlabel('Heuristic')
    plt.xticks(rotation=45)
    plt.legend(title="Bot Color")
    
    # Set background color to make white bars visible
    plt.gca().set_facecolor('lightgray')
    plt.tight_layout()
    plt.savefig('black_on_white_violence.png')


def main():
    # 1. Load Data
    filename = 'data.txt'
    print(f"Reading data from {filename}...")
    df = parse_checkers_data(filename)

    if not df.empty:
        print("Data loaded successfully. Generating plots...")
        
        # 2. Set Style
        plt.style.use('ggplot')

        # 3. Generate Plots
        plot_average_performance(df)
        plot_depth_impact(df)
        plot_color_balance(df)
        
        print("Done.")
    else:
        print("No data found or file is empty.")

if __name__ == "__main__":
    main()