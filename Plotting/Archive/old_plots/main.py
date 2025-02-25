import plotSP
import plotBins

import matplotlib.pyplot as plt

# Create a 3D scatter plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

plotSP.plot(fig, ax)
z_bin_borders, phi_bin_borders, r_bin_borders = plotBins.loadData()
#plotBins.plot(fig, ax, z_bin_borders, phi_bin_borders, r_bin_borders)

#limit plots view to 200, 200, 2000
ax.set_xlim(-200, 200)
ax.set_ylim(-200, 200)
ax.set_zlim(-2000, 2000)

plt.show()
