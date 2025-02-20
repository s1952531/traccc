import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def loadBinData(rDataPath, phiDataPath, zDataPath, mergedRBins=False):

    with open(rDataPath, "r") as file:
        
        file.readline() # skip header
        rho_values = [float(line.strip()) for line in file]
        
        # if rho is 1,2,3 make it (1,2), (2,3), (3,4)
        r_bin_borders = [(rho_values[i], rho_values[i + 1]) for i in range(len(rho_values) - 1)]

        if mergedRBins:
            r_bin_borders = [(r_bin_borders[0][0], r_bin_borders[-1][1])]
        
        #print(r_bin_borders)

    with open(phiDataPath, "r") as file:
        file.readline() # skip header
        phi_bin_borders = []
        for line in file.readlines():
            range_str = line.strip().split(',')
            phi_bin_borders.append(tuple([float(value) for value in range_str]))
            #print(phi_bin_borders)

        #print(phi_bin_borders)

    with open(zDataPath, "r") as file:
        file.readline() # skip header
        z_bin_borders = []
        for line in file.readlines():
            range_str = line.strip().split(',')
            z_bin_borders.append(tuple([float(value) for value in range_str]))

        #print(z_bin_borders)

    return r_bin_borders, phi_bin_borders, z_bin_borders

def plot_single_cylinder_bin(ax, plottedFaces, rho_range,  phi_range, z_range, color='blue', alpha=0.03):
    """
    Plot a single 3D bin of a cylinder on the provided axis.

    :param ax: The 3D axis to which the bin is added.
    :param phi_range: Tuple of (phi_min, phi_max) in radians.
    :param rho_range: Tuple of (rho_min, rho_max).
    :param z_range: Tuple of (z_min, z_max).
    :param color: Color of the bin faces (default: blue).
    :param alpha: Transparency of the bin faces (default: 0.1).
    """
    phi_min, phi_max = phi_range
    rho_min, rho_max = rho_range
    z_min, z_max = z_range

    # Define the bin's vertices in cylindrical coordinates
    vertices = []
    for z in [z_min, z_max]:  # For bottom and top faces
        for phi in [phi_min, phi_max]:
            for rho in [rho_min, rho_max]:
                x = rho * np.cos(phi)
                y = rho * np.sin(phi)
                vertices.append([x, y, z])

    # Connect the vertices to form the faces of the bin
    faces = [
        [vertices[0], vertices[1], vertices[3], vertices[2]],  # Bottom face
        [vertices[4], vertices[5], vertices[7], vertices[6]],  # Top face
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # Side face 1
        [vertices[1], vertices[3], vertices[7], vertices[5]],  # Side face 2
        [vertices[3], vertices[2], vertices[6], vertices[7]],  # Side face 3
        [vertices[2], vertices[0], vertices[4], vertices[6]],  # Side face 4
    ]

    if faces not in plottedFaces: #ensures bin not plotted twice
        plottedFaces.append(faces)

        # Create a Poly3DCollection to visualize the faces
        poly = Poly3DCollection(faces, alpha=alpha, edgecolor='k', facecolor=color)
        
        # Add the collection of faces to the axis
        ax.add_collection3d(poly)

        # Set plot limits based on the range of rho and z
        max_rho = rho_max
        ax.set_xlim([-max_rho, max_rho])
        ax.set_ylim([-max_rho, max_rho])
        ax.set_zlim([z_min, z_max])

        # Set axis labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

def populateBins(spData):
    populated_bins = []
    for sp in spData:
        if sp.bin is not None:
            populated_bins.append(sp.bin)

    return populated_bins

def plot_populated_bins(ax, spData, binData, event):
    populated_bins = populateBins(spData[event])

    rho_bins, phi_bins, z_bins = binData

    #plot populated bins
    plottedFaces = [] # stores the faces of bins that have been plotted
    for bin in populated_bins:
        rho_range = rho_bins[bin[0]]
        phi_range = phi_bins[bin[1]]
        z_range = z_bins[bin[2]]

        plot_single_cylinder_bin(ax, plottedFaces, rho_range, phi_range, z_range) 

"""example usage..."""
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')

# rDataPath = 
# phiDataPath = 
# zDataPath =

# r_bin_borders, phi_bin_borders, z_bin_borders = loadBinData(rDataPath, phiDataPath, zDataPath, mergedRBins=True)
# bin_rho_border = r_bin_borders[0]
# bin_phi_border = phi_bin_borders[10]
# bin_z_border = z_bin_borders[0]

# bin_borders = (bin_rho_border, bin_phi_border, bin_z_border)

# print("ARGS", bin_borders)
# plot_single_cylinder_bin(ax, [], *bin_borders)
# plt.show()

