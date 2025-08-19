from training.config import ALL_STATS_PATH
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import os
import json

def defeat_rate_plot():
    # Check if the stats file exists
    if os.path.exists(ALL_STATS_PATH):
        with open(ALL_STATS_PATH, "r") as f:
            all_stats_data = json.load(f)

        # Prepare data for pandas
        data = []
        for checkpoint, stats in all_stats_data.items():
            checkpoint_num = int(checkpoint.split("_")[1])
            for player, values in stats.items():
                data.append({
                    "checkpoint": checkpoint_num,
                    "player": player,
                    "overall_defeat_rate": values["overall_defeat_rate"],
                    "first_player_defeat_rate": values["first_player_defeat_rate"],
                    "second_player_defeat_rate": values["second_player_defeat_rate"]
                })

        df = pd.DataFrame(data)

        # Reshape dataframe for seaborn
        df_melted = df.melt(
            id_vars=["checkpoint", "player"],
            value_vars=["overall_defeat_rate", "first_player_defeat_rate", "second_player_defeat_rate"],
            var_name="defeat_type",
            value_name="defeat_rate"
        )

        # Plot a line chart for each player
        for player_name in df["player"].unique():
            plt.figure(figsize=(10, 5))
            player_data = df_melted[df_melted["player"] == player_name]
            sns.lineplot(
                data=player_data,
                x="checkpoint",
                y="defeat_rate",
                hue="defeat_type",
                marker="o"
            )
            plt.title(f"Defeat Rates Evolution - {player_name}")
            plt.xlabel("Checkpoint")
            plt.ylabel("Defeat Rate")
            plt.ylim(0, 1)
            plt.grid(True, alpha=0.3)
            plt.legend(title="Defeat Type")
            plt.show()
    else:
        print(f"{ALL_STATS_PATH} does not exist. No plots to display.")