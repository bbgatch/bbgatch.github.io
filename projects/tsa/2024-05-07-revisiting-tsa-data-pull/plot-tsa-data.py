import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('tsa.csv')

sns.lineplot(data=df, x="Date", y="Passengers")
plt.show()