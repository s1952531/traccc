import numpy as np
from plotting_helper_scripts.findEventHeaderLines import getDataLines

class SP:
    def __init__(self, x, y, z):
        # Cartesian coordinates
        self.cartCoord = (x, y, z)
        
        # Cylindrical coordinates
        self.cylCoord = None

        # Find the bin which the point belongs to
        self.bin = None

    def set_cylCoord(self):
        x, y, z = self.cartCoord
        rho = np.sqrt(x**2 + y**2)  # Radial distance
        phi = np.arctan2(y, x)  # Angle in radians
        self.cylCoord = (rho, phi, z)

    def set_bin(self, rho_bins, phi_bins, z_bins):
        """
        Finds the bin indices for the cylindrical coordinates of the point.
        """

        rho, phi, z = self.cylCoord 

        # Find the bin indices
        rho_index = next((i for i, (low, high) in enumerate(rho_bins) if low <= rho < high), None)
        phi_index = next((i for i, (low, high) in enumerate(phi_bins) if low <= phi < high), None)
        z_index = next((i for i, (low, high) in enumerate(z_bins) if low <= z < high), None)
        
        # If any index is None, the point is out of bounds i.e. not in a bin
        if rho_index is None or phi_index is None or z_index is None:
            self.bin = None
        else:
            # Store the bin as a tuple of indices
            self.bin = (rho_index, phi_index, z_index)

def loadSPData(spFilePath, binData):
    with open(spFilePath, "r") as file:

        dataLines = getDataLines(spFilePath)
        #print('dataLines', dataLines)
        spList = []

        #for each event
        for start, end in dataLines:
            #print(start, end)
            event_spList = []
            for i, line in enumerate(file):
                #print(i, line)
                #print(f'\tLine: {i}')
                #print(line)
                if i >= start and i <= end:
                    values = line.strip().split(',')
                    values = [float(value) for value in values]
                    sp = SP(*values)
                    sp.set_cylCoord()
                    sp.set_bin(*binData)
                    event_spList.append(sp)
                #reset file ptr
            file.seek(0)
            
            #print(len(event_spList))
            spList.append(event_spList)

    # with open(spFilePath, "r") as file:
    #     spList = []
    #     for line in file.readlines():
    #         values = line.strip().split(',')
    #         values = [float(value) for value in values]
    #         sp = SP(*values)
    #         sp.set_cylCoord()
    #         sp.set_bin(*binData)
    #         spList.append(sp)

    return spList

def plotSP(ax, spList, event):
    for sp in spList[event]:
        if sp.bin is not None:
            ax.scatter(*sp.cartCoord, c='r', marker='o')
        else:
            ax.scatter(*sp.cartCoord, c='g', marker='o')
