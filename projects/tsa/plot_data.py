import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('tsa.csv')

plt.plot(df['Date'], df['Passengers'])
plt.savefig('tsa.png')
# plt.show()
