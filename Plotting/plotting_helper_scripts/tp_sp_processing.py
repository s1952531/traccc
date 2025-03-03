
try:
    from tpMetrics import getAssociatedRecoIndices, getLocs, allRecoToTruthDists, calcEventResolutions
    from tp_processing import loadTrackParams
    from seed_processing import loadSeeds
except:
    from plotting_helper_scripts.tpMetrics import getAssociatedRecoIndices, getLocs, allRecoToTruthDists, calcEventResolutions
    from plotting_helper_scripts.tp_processing import loadTrackParams
    from plotting_helper_scripts.seed_processing import loadSeeds

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

def calc_unique_sp_fraction(eventRecoDf, recoIndices):
    # get a list of all spacepoints from the recoTPs
    recoTPs = eventRecoDf.iloc[recoIndices]
    recoSPB = recoTPs[["spB_x", "spB_y", "spB_z"]].values    
    recoSPM = recoTPs[["spM_x", "spM_y", "spM_z"]].values
    recoSPT = recoTPs[["spT_x", "spT_y", "spT_z"]].values

    #get list of (spB, spM, spT) tuples
    recoSPs = np.concatenate((recoSPB, recoSPM, recoSPT), axis=0)

    #convert to list of tuples as these are hashable
    recoSPs = [tuple(sp) for sp in recoSPs]
    uniqueRecoSPs = list(set(recoSPs))
    numUniqueSPs = len(uniqueRecoSPs)
    numTotalSPs = len(recoSPs)

    uniqueSPFrac = numUniqueSPs/numTotalSPs
    return uniqueSPFrac

def calc_shared_sp_fraction(eventRecoDf, recoIndices):
    uniqueSPFrac = calc_unique_sp_fraction(eventRecoDf, recoIndices)
    return 1 - uniqueSPFrac

def calc_shared_spSingle_fraction(eventRecoDf, recoIndices, spType):
    spType = spType.upper()
    # get a list of all spacepoints from the recoTPs
    recoTPs = eventRecoDf.iloc[recoIndices]
    recoSPs = recoTPs[[f"sp{spType}_x", f"sp{spType}_y", f"sp{spType}_z"]].values

    #convert to list of tuples as these are hashable
    recoSPs = [tuple(sp) for sp in recoSPs]

    uniqueRecoSPs = list(set(recoSPs))
    numUniqueSPs = len(uniqueRecoSPs)
    numTotalSPs = len(recoSPs)

    uniqueSPFrac = numUniqueSPs/numTotalSPs
    return 1 - uniqueSPFrac

def sp_sharing(ax, tpData, event, spType):
    recoDfs, _ = tpData

    eventRecoDf = recoDfs[event]

    recoLocList, truthLocList = getLocs(tpData, event)
    recoToTruthDists = allRecoToTruthDists(recoLocList, truthLocList, event)
    assocRecoIndicesList = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)

    redundancies = []
    spFractions = []
    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        numRecos = len(recoIndices)
        if numRecos > 1:
            redundancies.append(numRecos)
            if spType == 'combined':
                spFractions.append(calc_shared_sp_fraction(eventRecoDf, recoIndices))
            else:
                spFractions.append(calc_shared_spSingle_fraction(eventRecoDf, recoIndices, spType))

    #print(f"Event {event}: {len(spFractions)} sp{spType} fractions")
    ax.plot(spFractions, redundancies, 'x', color='red', markersize=10)

    return spFractions, redundancies

def sp_sharing_all_events(tpData, energy, spType):

    if spType == 'all':
        numEvents = len(tpData[0])
        spTypes = ['b', 'm', 't']
        fig, axes = plt.subplots(1, 4, figsize=(18, 6), sharey=True)
        fig.suptitle(f"Energy: {energy} GeV")
        
        for i, spType in enumerate(spTypes):
            ax = axes[i]
            spFractions, redundancies = [], []
            for event in range(numEvents):
                curr_spFractions, curr_redundancies = sp_sharing(ax, tpData, event, spType)
                spFractions.extend(curr_spFractions)
                redundancies.extend(curr_redundancies)
            
            ax.set_xlabel(f"Fraction of shared SP{spType.upper()}s (per truth)")
            ax.set_ylabel("Number of redundant recoTPs")
            ax.set_title(f"SP{spType.upper()} Sharing")
            ax.hist2d(spFractions, redundancies, bins=(20, 20))

        # use the last axis to plot the combined sp sharing
        ax = axes[-1]
        spFractions, redundancies = [], []
        for event in range(numEvents):
            curr_spFractions, curr_redundancies = sp_sharing(ax, tpData, event, 'combined')
            spFractions.extend(curr_spFractions)
            redundancies.extend(curr_redundancies)

        ax.set_xlabel(f"Fraction of shared SPs (per truth)")
        ax.set_ylabel("Number of redundant recoTPs")
        ax.set_title("Combined SP Sharing")
        hist = ax.hist2d(spFractions, redundancies, bins=(20, 20))

        #add colorbar to the right of the last plot
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(hist[3], cax=cax, label="Counts")
        
        plt.tight_layout()
    
    else:
        numEvents = len(tpData[0])

        fig, ax = plt.subplots(2, 1, sharex=True, figsize=(6, 8))
        fig.subplots_adjust(right=0.85)  # Leave space for colorbar
        fig.suptitle(f"Energy: {energy} GeV")
        
        spFractions, redundancies = [], []
        for event in range(numEvents):
            curr_spFractions, curr_redundancies = sp_sharing(ax[0], tpData, event, spType)
            spFractions.extend(curr_spFractions)
            redundancies.extend(curr_redundancies)

        if spType == 'combined':
            spType = ''
        ax[0].set_xlabel(f"Fraction of shared SP{spType}s (per truth)")
        ax[0].set_ylabel("Number of redundant recoTPs")

        ax[1].set_xlabel(f"Fraction of shared SP{spType}s (per truth)")
        ax[1].set_ylabel("Counts")

        hist = ax[0].hist2d(spFractions, redundancies, bins=(20, 20))

        #Manually add the colorbar to the right of the plot without shrinking it
        cbar_ax = fig.add_axes([0.87, 0.53, 0.02, 0.35])  # [left, bottom, width, height]
        fig.colorbar(hist[3], cax=cbar_ax, label="Counts")

        ax[1].hist(spFractions, bins=20, alpha=0.5)

        # Ensure both x-axes have the same limits
        ax[1].set_xlim(ax[0].get_xlim())

def get_spToWeightDict(seedData, event):
    unfilteredSeeds = seedData["uf"]
    filteredSeeds = seedData["f"]

    #contains a list for each event, each list contains all the seeds for that event
    unfilWeightList = []
    unfilWeightDict = {}
    for seed in unfilteredSeeds[event]:
        bx, by, bz, mx, my, mz, tx, ty, tz, weight, z_vertex = seed
        unfilWeightDict[(bx, by, bz, mx, my, mz, tx, ty, tz)] = weight
        unfilWeightList.append(weight)

    #print(set(unfilWeightList))

    filWeightList = []
    filWeightDict = {}
    for seed in filteredSeeds[event]:
        bx, by, bz, mx, my, mz, tx, ty, tz, weight, z_vertex = seed
        filWeightDict[(bx, by, bz, mx, my, mz, tx, ty, tz)] = weight
        filWeightList.append(weight)

    # print(set(filWeightList))

    # print(len(set(unfilWeightList)))
    # print(len(set(filWeightList)))

    # #print the items in the unfiltered seeds that are not in the filtered seeds
    # print(set(unfilWeightList) - set(filWeightList))

    # #print the items in the filtered seeds that are not in the unfiltered seeds
    # print(set(filWeightList) - set(unfilWeightList))

    return unfilWeightDict, filWeightDict
    
def get_tp_sp_weights(seedData, tpData, event):
    unfilWeightDict, filWeightDict = get_spToWeightDict(seedData, event)

    recoDfs, truthDfs = tpData

    eventRecoDf = recoDfs[event]
    eventTruthDf = truthDfs[event]

    recoLocList, truthLocList = getLocs(tpData, event)
    recoToTruthDists = allRecoToTruthDists(recoLocList, truthLocList, event)
    assocRecoIndicesList = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)

    truthIndexToWeightDict = {}
    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        if len(recoIndices) > 0:
            recoTPs = eventRecoDf.iloc[recoIndices]
            recoSPs = recoTPs[["spB_x", "spB_y", "spB_z", "spM_x", "spM_y", "spM_z", "spT_x", "spT_y", "spT_z"]].values
            #convert to tuple
            recoSPs = [tuple(sp) for sp in recoSPs]
            filTPWeights = [filWeightDict[sp] for sp in recoSPs]
            unfilTPWeights = [unfilWeightDict[sp] for sp in recoSPs]
            #print('\nfiltered weights', filTPWeights)
            #print('unfiltered weights', unfilTPWeights)
            truthIndexToWeightDict[truthIndex] = {'f' : filTPWeights, 'uf' : unfilTPWeights}

    return truthIndexToWeightDict

def plot_resVsWeight(ax, seedData, tpData, event):
    recoLocList, truthLocList = getLocs(tpData, event)
    recoToTruthDists = allRecoToTruthDists(recoLocList, truthLocList, event)
    assocRecoIndicesList = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)
    truthResolutions = calcEventResolutions(recoLocList, truthLocList, assocRecoIndicesList, indiceType='TruthIndex')
    truthIndexToWeightDict = get_tp_sp_weights(seedData, tpData, event)

    #plot the resolutions against the weights
    weightList = []
    resPhiList = []
    resThetaList = []

    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        if len(recoIndices > 0):
            resPhi = truthResolutions[truthIndex]['phi']
            resTheta = truthResolutions[truthIndex]['theta']
            weight = truthIndexToWeightDict[truthIndex]['f']
            #ax[0].plot(weight, np.abs(resPhi), 'x', color='red', markersize=10)
            #ax[1].plot(weight, np.abs(resTheta), 'x', color='red', markersize=10)

            weightList.extend(weight)
            resPhiList.extend(np.abs(resPhi))
            resThetaList.extend(np.abs(resTheta))

    ax[0].set_xlabel("Weight")
    ax[0].set_ylabel("|Phi Resolution|")

    ax[1].set_xlabel("Weight")
    ax[1].set_ylabel("|Theta Resolution|")

    return weightList, resPhiList, resThetaList

def plot_resVsWeight_all_events(seedData, tpData, energy):
    numEvents = len(tpData[0])

    fig, axes = plt.subplots(1, 2, sharex=True, figsize=(6, 8))
    fig.suptitle(f"Energy: {energy} GeV")
    
    allEventWeights = []
    allEventResPhi = []
    allEventResTheta = []
    for event in range(numEvents):
        weightList, resPhiList, resThetaList = plot_resVsWeight(axes, seedData, tpData, event)
        allEventWeights.extend(weightList)
        allEventResPhi.extend(resPhiList)
        allEventResTheta.extend(resThetaList)

    #remove point where phiRes is >0.3
    allEventWeights = [weight for i, weight in enumerate(allEventWeights) if allEventResPhi[i] < 0.3]
    allEventResTheta = [res for i, res in enumerate(allEventResTheta) if allEventResPhi[i] < 0.3]
    allEventResPhi = [res for res in allEventResPhi if res < 0.3]

    #print number of phiRes over 0.3
    phiResOver0_3 = [res for res in allEventResPhi if res > 0.3]
    print(f"Number of phiRes over 0.3: {len(phiResOver0_3)}")

    numXbins = 10
    numYbins = 100
    from matplotlib.colors import LogNorm
    from matplotlib import colormaps
    from matplotlib.colors import Normalize
    
    cmap = colormaps.get_cmap('viridis') 

    axes[0].hist2d(allEventWeights, allEventResPhi, bins=(numXbins, numYbins), cmap=cmap)
    hist = axes[1].hist2d(allEventWeights, allEventResTheta, bins=(numXbins, numYbins), cmap=cmap)

    #set colorbar
    divider = make_axes_locatable(axes[1])
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(hist[3], cax=cax, label="Counts")

    #plot scatters
    alpha = 1
    axes[0].scatter(allEventWeights, allEventResPhi, color='red', s=10  , alpha=alpha)
    axes[1].scatter(allEventWeights, allEventResTheta, color='red', s=10, alpha=alpha)

    


    plt.tight_layout()


def test():
    energies = ['1', '10', '100']

    for energy in energies:
        recoPath = f"Plotting/data/{energy}GeV/TrackParams/reconstructedTPs.csv"
        truthPath = f"Plotting/data/{energy}GeV/TrackParams/truthTPs.csv"

        recoDfs, truthDataDfs = loadTrackParams(recoPath, truthPath)
        tpData = (recoDfs, truthDataDfs)

        #sp_sharing_all_events(tpData, energy, spType='all')

        # if energy != '10':
        #     continue

        # fig, ax = plt.subplots()
        # sp_sharing(ax, tpData, event=0)
        # plt.show()

        
        unfilteredSeedPath  = f"Plotting/data/{energy}GeV/seeds/UnfilteredSeeds.csv"
        filteredSeedPath    = f"Plotting/data/{energy}GeV/seeds/FilteredSeeds.csv"

        UnfilteredSeeds, FilteredSeeds = loadSeeds(unfilteredSeedPath, filteredSeedPath)
        seedData = {"uf" : UnfilteredSeeds, 
                    "f" : FilteredSeeds}
        
        #get_tp_sp_weights(seedData, tpData, event=1)
        #plot_resVsWeight(seedData, tpData, event=1)
        plot_resVsWeight_all_events(seedData, tpData, energy)

    plt.show()

test()