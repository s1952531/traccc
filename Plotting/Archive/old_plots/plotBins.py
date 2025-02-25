import matplotlib.pyplot as plt
import numpy as np

def loadData():
# read data from z_bin_borders.csv
    with open("C:\\Users\\alasd\\Documents\\MPhys\\Plotting\\z_bin_borders.csv", "r") as file:
        #-2000,2000
        # z_bin_borders = [line.strip().split(',') for line in file]
        # update to convert to floats
        #z_bin_borders = [list(map(float, line.strip().split(','))) for line in file]

        z_bin_borders = []

        for line in file.readlines():
            vals = line.strip().split(',')
            for val in vals:
                z_bin_borders.append(float(val))
            
        #get all unique values
        z_bin_borders = list(set(z_bin_borders))

        #order the values
        z_bin_borders.sort()
        
        print(z_bin_borders)

    # read data from phi_bin_borders.csv
    with open("C:\\Users\\alasd\\Documents\\MPhys\\Plotting\\phi_bin_borders.csv", "r") as file:
        
        phi_bin_borders = []

        for line in file.readlines():
            vals = line.strip().split(',')
            for val in vals:
                phi_bin_borders.append(float(val))
            
        #get all unique values
        phi_bin_borders = list(set(phi_bin_borders))

        #order the values
        phi_bin_borders.sort()
        
        print(phi_bin_borders)

    # read data from r_bin_borders.csv
    with open("C:\\Users\\alasd\\Documents\\MPhys\\Plotting\\r_bin_borders.csv", "r") as file:
        r_bin_borders = [float(line.strip()) for line in file]
    
        r_bin_borders = [min(r_bin_borders), max(r_bin_borders)]

        print(r_bin_borders)

    return z_bin_borders, phi_bin_borders, r_bin_borders

def plotPlaneAtAngle(ax, theta):
    # Parameters
    r = np.linspace(0, 200, 50)  # Radial range
    z = np.linspace(-2000, 2000, 50)  # Height range
    r, z = np.meshgrid(r, z)  # Create a meshgrid

    # Convert to Cartesian coordinates
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    # Plot the plane
    ax.plot_surface(x, y, z, alpha=0.1, color='red', edgecolor='none')


def plot(fig, ax, z_bin_borders, phi_bin_borders, r_bin_borders):

    for phi_bin_boundary in phi_bin_borders:
        print("phi_bin_boundary", phi_bin_boundary)

        num_bins = len(phi_bin_borders) - 1 # first bin == last bin => minus 1
        bin_angles = np.linspace(0, 2*np.pi, num_bins)

        # plot the circles
        for i in range(0, len(r_bin_borders)):
            
            #print only the max
            # if i < len(r_bin_borders) - 1:
            #     continue

            #print only every 10
            if i % 50 != 0:
                continue

            radius = r_bin_borders[i]

            # plot circle using parametric eqns
            x = radius * np.cos(bin_angles)
            y = radius * np.sin(bin_angles)

            for z in z_bin_borders:
                z = np.ones_like(x) * float(z)

                ax.plot(x, y, z, c='r')

            
            # plot a line from the origin to the largest circle
            # angle = phi_bin_boundary + np.pi
            # x = [0, radius * np.cos(phi_bin_boundary)]
            # y = [0, radius * np.sin(phi_bin_boundary)]
            # z = [0, 0]
            
            # ax.plot(x, y, z, c='r')

            if phi_bin_boundary > 0 and phi_bin_boundary < np.pi/2:
                # plot plane at angle
                plotPlaneAtAngle(ax, phi_bin_boundary)
                

    # Add labels and title
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_zlabel("Z Coordinate")
    ax.set_title("3D Scatter Plot of Spacepoints")