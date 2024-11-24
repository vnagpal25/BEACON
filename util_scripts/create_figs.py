import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D

df = pd.read_csv(
    'C:\\Users\\2002v\\Desktop\\Fall2024\\AI4S\\MealRec\\BEACON\\scores.csv')
# print(df.head())


def create_score_plots(df, score_columns):
    """
    Create three subplots for different time periods showing multiple scores

    Parameters:
    df: pandas DataFrame with columns [User_Config, time, Algorithm] + score columns
    score_columns: list of score column names to plot
    """
    # Define style parameters
    # Different markers for each score
    markers = ['s', '^', '*', 'o', 'D', 'v', 'p']
    colors = {'m2': 'red', 'm1': 'blue', 'm0': 'green'}
    times = sorted(df['time'].unique())
    configs = sorted(df['User_Config'].unique())
    algorithms = sorted(df['Algorithm'].unique())

    # Create figure with three subplots - increased figure width to accommodate legend
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    # fig.suptitle(
    #     'Score Comparison Across Configurations and Algorithms', fontsize=14, y=1.05)

    # Plot for each time period
    for idx, config in enumerate(configs):
        ax = axes[idx]
        config_data = df[df['User_Config'] == config]

        # Plot each algorithm and score combination
        for algorithm in algorithms:
            alg_data = config_data[config_data['Algorithm'] == algorithm]
            color = colors.get(algorithm.lower(), 'black')

            # Plot each score
            for score_idx, score in enumerate(score_columns):
                y_values = alg_data[score].values
                x_values = pd.Categorical(alg_data['time']).codes

                ax.plot(x_values, y_values,
                        label=f'{algorithm}-{score}',
                        color=color,
                        marker=markers[score_idx % len(markers)],
                        linestyle='--',
                        markersize=8)

        # Customize the subplot
        ax.set_title(f'User Configuration: {config}')
        ax.set_xticks(range(len(times)))
        ax.set_xticklabels(times)
        ax.set_xlabel('Time Frame')
        ax.set_ylabel('Score')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_ylim(0.3, 1.05)

    # Create custom legend handles
    # Algorithm legend (colors)
    algorithm_handles = [Line2D([0], [0], color=colors[alg.lower()], linestyle='--',
                                marker='o', label=alg) for alg in algorithms]

    # Score legend (markers)
    score_handles = [Line2D([0], [0], color='black', marker=markers[idx],
                            linestyle='none', label=score)
                     for idx, score in enumerate(score_columns)]

    # Add both legends with clear separation
    fig.legend(handles=algorithm_handles,
               loc='center right',
               # Place algorithm legend slightly higher
               bbox_to_anchor=(0.5, 0.08),
               ncol=len(algorithms),
               title='Algorithms',
               fontsize=10)

    fig.legend(handles=score_handles,
               loc='center left',
               # Place score legend slightly lower
               bbox_to_anchor=(0.5, 0.08),
               ncol=min(len(score_columns), 4),  # Up to 4 scores per row
               title='Metrics',
               fontsize=10)

    # Adjust layout with extra space at bottom for legend
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.2)  # Make room for legend at bottom

    return fig, axes


score_columns = ['uc', 'dm', 'mc', 'uc_dm_mc']
fig, axes = create_score_plots(df, score_columns)
plt.savefig('reco_chart.png', bbox_inches='tight')
# plt.show()
