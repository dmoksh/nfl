from vega_datasets import data
import pandas as pd



df = data.population()

print(df['age'].idxmax())
print(df.iloc[df['age'].idxmax()]['year'])