import matplotlib.pyplot as plt

from plotting_helper_scripts.bin_processing import loadBinData, plot_populated_bins
from plotting_helper_scripts.seed_processing import loadSeeds, plotSeeds
from plotting_helper_scripts.sp_processing import loadSPData, plotSP
from plotting_helper_scripts.tp_processing import loadTrackParams, plotTruthTP3D, plotRecoTP3D

def load():
    # load bins
    rDataPath   = "Plotting/data/bins/r_bin_borders.csv"
    phiDataPath = "Plotting/data/bins/phi_bin_borders.csv"
    zDataPath   = "Plotting/data/bins/z_bin_borders.csv"
    rho_bins, phi_bins, z_bins = loadBinData(rDataPath, phiDataPath, zDataPath, mergedRBins=True)
    binData = (rho_bins, phi_bins, z_bins) #convenient container for passing around

    # load SP data
    spFilePath = "Plotting/data/spacepoints/sp.csv"
    spData = loadSPData(spFilePath, binData)

    # load seeds
    unfilteredSeedPath  = "Plotting/data/seeds/UnfilteredSeeds.csv"
    filteredSeedPath    = "Plotting/data/seeds/FilteredSeeds.csv"
    UnfilteredSeeds, FilteredSeeds = loadSeeds(unfilteredSeedPath, filteredSeedPath)
    seedData = {"uf" : UnfilteredSeeds, 
                "f" : FilteredSeeds}
    
    # load tp data
    recoPath = "Plotting/data/TrackParams/reconstructedTPs.csv"
    truthPath = "Plotting/data/TrackParams/truthTPs.csv"
    recoDfs, truthDfs = loadTrackParams(recoPath, truthPath)
    tpData = (recoDfs, truthDfs)

    return binData, spData, seedData, tpData

def plot(ax, allData, event=0):
    binData, spData, seedData, tpData = allData

    #plot populated bins
    plot_populated_bins(ax, spData, binData, event)

    #plot spacepoints
    plotSP(ax, spData, event)

    #plot seeds
    plotSeeds(ax, seedData["uf"], event=0, style='dotted', colour='b')
    plotSeeds(ax, seedData["f"], event=0, style='solid', colour='g')

    #plot truth track params
    truthData = tpData[1]
    plotTruthTP3D(ax, truthData[event])

    #plot reco track params
    recoData = tpData[0]
    plotRecoTP3D(ax, recoData[event])

def adjust_plt(ax):
    ax.view_init(elev=90, azim=-90)
    axlim = 1e-10
    ax.set_xlim(-axlim, axlim)
    ax.set_ylim(-axlim, axlim)
    ax.set_zlim(-axlim, axlim)

def main():
    
    event = 0

    # create plot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # load data
    binData, spData, seedData, tpData = load()
    allData = (binData, spData, seedData, tpData)

    # plot data
    plot(ax, allData)

    # adjust plot view
    # adjust_plt(ax)

    # debug output
    print("#unfiltered = ", len(seedData["uf"][event]))
    print("#filtered = ", len(seedData["f"][event]))

    #plot an X at the origin
    ax.scatter(0, 0, 0, color='red', marker='x', s=100)

    plt.show()


if __name__ == "__main__":
    main()
