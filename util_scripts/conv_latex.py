import os
import pandas as pd

recs = os.listdir('recommendations')
recs = [rec for rec in recs if rec != 'trial0']
csvs = [(os.path.join('recommendations', rec, 'eval', 'results.csv'), trial_num)
        for trial_num, rec in enumerate(recs, 1)]

latex_string = ""
for csv, trial_num in csvs:
    df = pd.read_csv(csv)
    max_cols = list(df.max()[:-1])
    df.iloc[1], df.iloc[2] = df.iloc[2].copy(), df.iloc[1].copy()
    for index, row in df.iterrows():
        row_data = ""
        for i, el in enumerate(row[:-1]):
          if el == max_cols[i]:
            row_data += f" & \\textbf{{{el}}}"
          else:
            row_data += f"& {el}"
        latex_string += row_data + r" \\" + "\n"

    latex_string += "\\midrule" + "\n"
print(latex_string)
