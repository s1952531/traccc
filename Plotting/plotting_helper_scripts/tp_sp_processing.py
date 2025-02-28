
try:
    from tpMetrics import getAssociatedRecoIndices, getLocs, allRecoToTruthDists
    from tp_processing import loadTrackParams
except:
    from plotting_helper_scripts.tpMetrics import getAssociatedRecoIndices, getLocs, allRecoToTruthDists
    from plotting_helper_scripts.tp_processing import loadTrackParams

import matplotlib.pyplot as plt

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

def sp_sharing_all_events(tpData):
    numEvents = len(tpData[0])

    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("Fraction of shared SPs (per truth)")
    ax.set_ylabel("Number of redundant recoTPs")
    
    spFractions, redundancies = [], []
    for event in range(numEvents):
        curr_spFractions, curr_redundancies = sp_sharing(ax, tpData, event)
        spFractions.extend(curr_spFractions)
        redundancies.extend(curr_redundancies)

    plt.hist2d(spFractions, redundancies, bins=(20, 20), cmap='gray')
    plt.colorbar()
def test():
    energies = ['1', '10', '100']

    for energy in energies:
        recoPath = f"Plotting/data/{energy}GeV/TrackParams/reconstructedTPs.csv"
        truthPath = f"Plotting/data/{energy}GeV/TrackParams/truthTPs.csv"

        recoDfs, truthDataDfs = loadTrackParams(recoPath, truthPath)
        tpData = (recoDfs, truthDataDfs)

        sp_sharing_all_events(tpData)

    plt.show()

test()