import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load data from CSV file
df = pd.read_csv('test.csv')

# Filter by module (replace 0 with your desired module_index)
#get the module with the most clusters
module_index = df['module_index'].value_counts().idxmax()
module_data = df[df['module_index'] == module_index]

# Plotting
plt.figure(figsize=(8, 6))
scatter = plt.scatter(module_data['channel0'], module_data['channel1'], c=module_data['cluster'], cmap='viridis')

# Labeling the plot
plt.title(f'Cluster Plot for Module {module_index}')
plt.xlabel('Channel 0')
plt.ylabel('Channel 1')
plt.show()
