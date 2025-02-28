
try:
    from tpMetrics import getAssociatedRecoIndices, getLocs, allRecoToTruthDists
    from tp_processing import loadTrackParams
except:
    from plotting_helper_scripts.tpMetrics import getAssociatedRecoIndices, getLocs, allRecoToTruthDists
    from plotting_helper_scripts.tp_processing import loadTrackParams

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

def calc_unique_sp_fraction(eventRecoDf, recoIndices):
    # get a list of all spacepoints from the recoTPs
    recoTPs = eventRecoDf.iloc[recoIndices]
    recoSPs = recoTPs[["spB_x", "spB_y", "spB_z", "spM_x", "spM_y", "spM_z", "spT_x", "spT_y", "spT_z"]]
    recoSPs = recoSPs.values
    recoSPs = recoSPs.flatten() # flatten the list of lists because we want to count unique SPs
    uniqueRecoSPs = list(set(recoSPs))
    numUniqueSPs = len(uniqueRecoSPs)
    numTotalSPs = len(recoSPs)

    uniqueSPFrac = numUniqueSPs/numTotalSPs
    return uniqueSPFrac

def calc_shared_sp_fraction(eventRecoDf, recoIndices):
    uniqueSPFrac = calc_unique_sp_fraction(eventRecoDf, recoIndices)
    return 1 - uniqueSPFrac

def sp_sharing(ax, tpData, event):
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
            spFractions.append(calc_shared_sp_fraction(eventRecoDf, recoIndices))

    print(f"Event {event}: {len(spFractions)} sp fractions")
    ax.plot(spFractions, redundancies, 'x')
    #print(list(zip(spFractions, redundancies)))

    return spFractions, redundancies

def sp_sharing_all_events(tpData, energy):
    numEvents = len(tpData[0])

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(6, 8))
    fig.subplots_adjust(right=0.85)  # Leave space for colorbar
    fig.suptitle(f"Energy: {energy} GeV")

    ax[0].set_xlabel("Fraction of shared SPs (per truth)")
    ax[0].set_ylabel("Number of redundant recoTPs")

    ax[1].set_xlabel("Fraction of shared SPs (per truth)")
    ax[1].set_ylabel("Counts")


    
    spFractions, redundancies = [], []
    for event in range(numEvents):
        curr_spFractions, curr_redundancies = sp_sharing(ax[0], tpData, event)
        spFractions.extend(curr_spFractions)
        redundancies.extend(curr_redundancies)

    hist = ax[0].hist2d(spFractions, redundancies, bins=(20, 20))

    #Manually add the colorbar to the right of the plot without shrinking it
    cbar_ax = fig.add_axes([0.87, 0.53, 0.02, 0.35])  # [left, bottom, width, height]
    fig.colorbar(hist[3], cax=cbar_ax, label="Counts")

    ax[1].hist(spFractions, bins=20, alpha=0.5)

    # Ensure both x-axes have the same limits
    ax[1].set_xlim(ax[0].get_xlim())

def test():
    energies = ['1', '10', '100']

    for energy in energies:
        recoPath = f"Plotting/data/{energy}GeV/TrackParams/reconstructedTPs.csv"
        truthPath = f"Plotting/data/{energy}GeV/TrackParams/truthTPs.csv"

        recoDfs, truthDataDfs = loadTrackParams(recoPath, truthPath)
        tpData = (recoDfs, truthDataDfs)

        sp_sharing_all_events(tpData, energy)

    plt.show()

test()