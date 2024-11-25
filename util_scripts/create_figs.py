import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('./data/scores.csv')

# Change values in the `Algorithm` column to their uppercase version
df['Algorithm'] = df['Algorithm'].str.upper()

# Set style for publication
plt.style.use('seaborn-paper')

# Increase the default font sizes
plt.rcParams.update({
    'font.size': 14,          # Increase base font size
    'axes.labelsize': 16,     # Axis labels
    'axes.titlesize': 18,     # Subplot titles
    'xtick.labelsize': 14,    # X-axis tick labels
    'ytick.labelsize': 14,    # Y-axis tick labels
    'legend.fontsize': 14,    # Legend text
    'legend.title_fontsize': 16  # Legend title
})

# Create figure with three subplots side by side
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.subplots_adjust(wspace=0.2)

# Define metrics to plot
metrics = ['uc', 'dm', 'mc', 'uc_dm_mc']

# Define colors for algorithms
colors = {'M0': 'green', 'M1': 'blue', 'M2': 'red'}

# Define markers for metrics
markers = {'uc': 's', 'dm': '^', 'mc': '*', 'uc_dm_mc': 'o'}

# Define line styles
line_style = '--'

# Plot for each user configuration
for idx, config in enumerate(['c1', 'c2', 'c3']):
    ax = axes[idx]
    config_data = df[df['User_Config'] == config]
    
    # Plot each algorithm
    for alg in ['M0', 'M1', 'M2']:
        alg_data = config_data[config_data['Algorithm'] == alg]
        
        # Plot each metric
        for metric in metrics:
            ax.plot(alg_data['time'], alg_data[metric], 
                   marker=markers[metric],
                   linestyle=line_style,
                   color=colors[alg],
                   label=f'{alg}-{metric}',
                   markersize=10)
    
    # Customize the subplot
    ax.set_title(f'User Configuration: {config}', fontsize=18, pad=10)
    ax.set_xlabel('Time Frame')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_ylim(0.3, 1.05)
    
    # Only add y-label to the first subplot
    if idx == 0:
        ax.set_ylabel('Score')
    
    # Clean up x-ticks
    ax.set_xticks(range(len(alg_data['time'].unique())))
    ax.set_xticklabels(alg_data['time'].unique())

# Create custom legend
# First legend for algorithms
legend_elements_alg = [plt.Line2D([0], [0], color=color, label=alg, linestyle=line_style)
                      for alg, color in colors.items()]
# Second legend for metrics
legend_elements_metrics = [plt.Line2D([0], [0], color='black', marker=marker, 
                                    label=metric, linestyle='none', markersize=10)
                         for metric, marker in markers.items()]

# Place legends below the subplots
fig.legend(legend_elements_alg, colors.keys(), 
          title='Algorithms',
          loc='center left',
          bbox_to_anchor=(0.5, 0.08),
          ncol=3,
          frameon=True,
          prop={'style': 'italic'})

fig.legend(legend_elements_metrics, markers.keys(),
          title='Metrics',
          loc='center right',
          bbox_to_anchor=(0.5, 0.08),
          ncol=4,
          frameon=True)

# Adjust layout to make room for legends at the bottom
plt.tight_layout()
plt.subplots_adjust(bottom=0.25)

# Save the figure
# plt.savefig('./figs/performance_comparison_mat.png', 
plt.savefig('./reco_chart.png',
            format='png', 
            dpi=300, 
            bbox_inches='tight')

plt.close()