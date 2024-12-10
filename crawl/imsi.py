import pandas as pd

df = pd.read_csv('./data.csv')

print(df.columns, '\n')
df.drop('총계 (￦)', axis=1, inplace=True)

print(df.columns)

df.to_csv('./data2.csv', index=False)
