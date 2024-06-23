import os
import pandas as pd

recs = os.listdir('recommendations')
recs = [rec for rec in recs if rec != 'trial0']
csvs = [os.path.join('recommendations', rec, 'eval', 'results.csv') for rec in recs]

for csv in csvs:
  df = pd.read_csv(csv)

  # Step 2: Round all numerical columns to 3 decimal places
  df = df.round(3)

  # Step 3 (optional): Save the DataFrame back to a CSV file
  df.to_csv(csv, index=False)