import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

def getLocs(tpData, event=0):
    recoDfs = tpData[0]
    truthDfs = tpData[1]

    recoDataList = recoDfs[event]
    truthDataList = truthDfs[event]

    recoLocList = np.array(recoDataList[['phi', 'theta']])
    truthLocList = np.array(truthDataList[['phi', 'theta']])

    return recoLocList, truthLocList   

def allRecoToTruthDists(recoLocList, truthLocList, event=0):

    #row i of recoToTruthDists gives reco i's distance to all truths
    #col j of recoToTruthDists gives truth j's distance to all recos

    #account for -pi, pi wrap around
    phiDiff = (recoLocList[:, None, 0] - truthLocList[None, :, 0] + np.pi) % (2 * np.pi) - np.pi
    thetaDiff = recoLocList[:, None, 1] - truthLocList[None, :, 1]
    
    recoToTruthDists = np.sqrt(phiDiff**2 + thetaDiff**2)

    return recoToTruthDists

# def assocRecoToTruthDists(recoToTruthDists, cutoff=0.1):

#     assocRecoIndices = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)
#     assocRecoToTruthDists = [recoToTruthDists[recoIndices, truthIndex] for truthIndex, recoIndices in enumerate(assocRecoIndices)]

#     assert(checkUniqueIndices(assocRecoToTruthDists))
#     return assocRecoToTruthDists

def checkUniqueIndices(assocRecoIndices):
    uniqueAssocRecoIndices = np.unique(np.concatenate(assocRecoIndices))

    isUnique = len(uniqueAssocRecoIndices) == len(np.concatenate(assocRecoIndices))

    #if not isUnique:
        #print(assocRecoIndices)
        #print(np.concatenate(assocRecoIndices))
    
    return isUnique

def getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1):
    numTruths = recoToTruthDists.shape[1]
    #print('numTruths', numTruths)

    assocRecoIndicesList = []

    for i in range(numTruths):
        currDists = recoToTruthDists[:, i]
        assocRecoIndices = np.where(currDists < cutoff)[0] #[0] to pull indices array out of (np.array([indices]))
        assocRecoIndicesList.append(assocRecoIndices)

    isUnique = checkUniqueIndices(assocRecoIndicesList)
    #if not isUnique:
        #print(f"WARNING: Some recos have been assigned to multiple truth's - cutoff is too large")
    #else:
        #print(f"SUCCESS: All recos have been uniquely assigned to a truth")
    #print(assocRecoIndicesList)

    return assocRecoIndicesList # a list containing a list of associated reco indices for each truth
                                # [ [Truth0s recoIndices], [Truth1s recoIndices], ... ]
                                # recoIndices are the row indice of the event's recoDf

def getTruthToRecoDict(recoLocList, truthLocList, assocRecoIndicesList):
    truthToRecoDict = {}

    # assocRecoIndicesList = [ [Event0s recoIndices], [Event1s recoIndices], ... ]
    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        if len(recoIndices) == 0:
            continue

        recoLocs = recoLocList[recoIndices]
        truthLoc = truthLocList[truthIndex]

        recoPhi = recoLocs[:, 0]
        recoTheta = recoLocs[:, 1]

        truthToRecoDict[tuple(truthLoc)] = {'phi':recoPhi, 'theta':recoTheta}

    return truthToRecoDict

def calcEventResolutions(recoLocList, truthLocList, assocRecoIndicesList, indiceType='TruthLoc'):
    # res is (reco - truth)/truth
    # get res for phi and theta separately

    truthResolutions = {}

    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        if len(recoIndices) == 0:
            #truthResolutions[truthIndex] = {'phi':None, 'theta':None}
            continue

        recoLocs = recoLocList[recoIndices]
        truthLoc = truthLocList[truthIndex]

        res = (recoLocs - truthLoc)#/np.abs(truthLoc) Dont divide as it creates an assymetry

        #first column is phi res, second is theta res
        phiRes = res[:, 0]
        thetaRes = res[:, 1]

        if indiceType == 'TruthLoc':
            truthResolutions[tuple(truthLoc)] = {'phi':phiRes, 'theta':thetaRes}
        elif indiceType == 'TruthIndex':
            truthResolutions[truthIndex] = {'phi':phiRes, 'theta':thetaRes}

    return truthResolutions


def plotResolutions(truthResolutions):
    fig, ax = plt.subplots(2, len(truthResolutions), figsize=(10, 5))#, sharex=True, sharey=True)

    plotCounter = 0
    for truthLoc, res in truthResolutions.items():
        phiRes = res['phi']
        thetaRes = res['theta']

        ax[0, plotCounter].hist(phiRes, bins=5, alpha=0.5, label='phi', color='blue')
        ax[1, plotCounter].hist(thetaRes, bins=5, alpha=0.5, label='theta', color='orange')
        ax[0, plotCounter].set_title(f"Truth @{truthLoc} ({len(phiRes)} recos)")
        ax[1, plotCounter].set_title(f"Truth @{truthLoc} ({len(phiRes)} recos)")
        ax[0, plotCounter].legend()
        ax[1, plotCounter].legend()

        plotCounter += 1

    #plt.show()

def getDictForAllEvents(tpData, dict_getter):
    #getter_for_dict_to_extend: calcEventResolutions or getTruthToRecoDict
     
    numEvents = len(tpData[0]) # i.e. len of recoDfs
    #print(numEvents)

    #get a dict of truthResolutions across all events
    extended_dict = {} # e.g. for calcEventResolutions {(truthPhi, truthTheta): {'phi':phiRes, 'theta':thetaRes}}

    #key_counter = 0
    for event in range(numEvents):
        recoLocList, truthLocList = getLocs(tpData, event)
        recoToTruthDists = allRecoToTruthDists(recoLocList, truthLocList, event)
        assocRecoIndicesList = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)
        event_dict = dict_getter(recoLocList, truthLocList, assocRecoIndicesList)
        #print(len(event_dict.keys()))
        # if len(event_dict.keys()) == 5:
        #     print(event)
        # key_counter += len(event_dict.keys())
        extended_dict = {**extended_dict, **event_dict}

    #print('key_counter', key_counter)
    return extended_dict

def getNumRecosPerTruth(truthToRecoDict):
    # truthToRecoDict[tuple(truthLoc)] = {'phi':recoPhi, 'theta':recoTheta}

    numRecosPerTruth = {truthLoc: {'phi':len(reco['phi']), 'theta':len(reco['theta'])} for truthLoc, reco in truthToRecoDict.items()}

    return numRecosPerTruth


def plotRedundancyVsAngleRange(numRecosPerTruth, energy):
    # truthToRecoDict[tuple(truthLoc)] = {'phi':recoPhi, 'theta':recoTheta}

    truthPhis = [key[0] for key in numRecosPerTruth.keys()]
    numRecosPerPhiTruth = [value['phi'] for value in numRecosPerTruth.values()]

    truthThetas = [key[1] for key in numRecosPerTruth.keys()]
    numRecosPerThetaTruth = [value['theta'] for value in numRecosPerTruth.values()]

    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    fig.suptitle(f"Redundancy vs Angle: {energy}GeV")

    ax[0].scatter(truthPhis, numRecosPerPhiTruth)
    ax[0].set_xlabel(r"$\Phi$")
    ax[0].set_ylabel("Number of reco TPs")

    ax[1].scatter(truthThetas, numRecosPerThetaTruth)
    ax[1].set_xlabel(r"$\Theta$")
    ax[1].set_ylabel("Number of reco TPs")

def plotRedundancyVsBinnedTheta(ax, numRecosPerTruth, energy, num_bins=10):

    truthThetas = [key[1] for key in numRecosPerTruth.keys()]
    numRecosPerThetaTruth = [value['theta'] for value in numRecosPerTruth.values()]

    # Define bins
    bins = np.linspace(min(truthThetas), max(truthThetas), num_bins + 1)
    bin_indices = np.digitize(truthThetas, bins) - 1  # Get bin index for each theta

    # Compute mean and standard error of mean (SEM) per bin
    mean_recos = []
    sem_recos = []
    for j in range(num_bins):
        bin_data = [numRecosPerThetaTruth[i] for i in range(len(bin_indices)) if bin_indices[i] == j]
        if len(bin_data) > 0:
            mean_recos.append(np.mean(bin_data))
            sem_recos.append(np.std(bin_data) / np.sqrt(len(bin_data)))  # SEM calculation

    # Plot
    bin_centers = (bins[:-1] + bins[1:]) / 2  # Midpoint of each bin
    ax.bar(bin_centers, mean_recos, width=(bins[1] - bins[0]), align='center', \
           yerr=sem_recos, ecolor=energy_colours[energy], capsize=5, color='none', edgecolor=energy_colours[energy], label=energy)
    ax.set_xlabel(r"$\Theta$ (binned)")
    ax.set_ylabel("Mean number of reco TPs")
    ax.legend()
    #ax.set_title(f"Redundancy vs Binned Theta {energy}GeV")
    #plt.show()

    return ax

def plotMultiEventRes(tpData, energy):
    #truthResolutions[truthIndex] = {'phi':phiRes, 'theta':thetaRes}

    #get a dict of truthResolutions across all events
    truthResDict = getDictForAllEvents(tpData, calcEventResolutions) # {(truthPhi, truthTheta): {'phi':phiRes, 'theta':thetaRes}}

    # truthPhis = [key[0] for key in truthResDict.keys()]
    # truthThetas = [key[1] for key in truthResDict.keys()]

    # # Calculate the range for the first element (truthPhi)
    # min_phi = min(truthPhis)
    # max_phi = max(truthPhis)
    # truthPhiRange = (min_phi, max_phi)

    # truthPhiBins = np.arange(truthPhiRange*, 0.01)

    # # Calculate the range for the second element (truthTheta)
    # min_theta = min(truthThetas)
    # max_theta = max(truthThetas)
    # truthThetaRange = (min_theta, max_theta)

    # truthThetaBins = np.arange(truthThetaRange*, 0.01)

    #get res data
    #print('truthResDict.values()', truthResDict.values())
    phiRes = [res['phi'] for res in truthResDict.values()]
    phiRes = np.concatenate(phiRes)
    #print(len(truthPhis))
    #print(len(phiRes))
    #print([len(res) for res in phiRes])

    thetaRes = [res['theta'] for res in truthResDict.values()]
    thetaRes = np.concatenate(thetaRes)
    #print(len(truthThetas))
    #print(len(thetaRes))
    #print([len(res) for res in thetaRes])

    fig, ax = plt.subplots(1, 2)

    binEnergyDict = {'1':{'phi':200, 'theta':100}, 
                     '10':{'phi':75, 'theta':50}, 
                     '100':{'phi':200, 'theta':150}}

    fig.suptitle(f"Angle Resolutions: {energy}GeV")
    for i in range(2):
        # Main histogram
        phiCounts, _, _ = ax[i].hist(phiRes, bins=binEnergyDict[energy]['phi'], alpha=0.5, label='phi', color='blue')
        thetaCounts, _, _ = ax[i].hist(thetaRes, bins=binEnergyDict[energy]['theta'], alpha=0.5, label='theta', color='orange')

        # Add error bars for standard deviation
        ax[i].errorbar(0, np.max(phiCounts)/2, xerr=np.std(phiRes), fmt='o', color='blue', label='std dev')
        ax[i].errorbar(0, np.max(thetaCounts)/2, xerr=np.std(thetaRes), fmt='o', color='orange', label='std dev')

        ax[i].set_title("Angle Resolution")
        ax[i].legend()

        if i == 1:
            ax[i].set_ylim(0, 7)
            ax[i].set_title("Zoomed Angle Resolution")

        plt.legend()

    # fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    # phiCounts, _, _ = ax[0].hist(phiRes, bins=1000, alpha=0.5, label='phi', color='blue')
    # ax[0].errorbar(0, np.max(phiCounts)/2, xerr=np.std(phiRes), fmt='o', color='black', label='std dev')

    # thetaCounts, _, _ =ax[1].hist(thetaRes, bins=1000, alpha=0.5, label='theta', color='orange')
    # ax[1].errorbar(0, np.max(thetaCounts)/2, xerr=np.std(thetaRes), fmt='o', color='black', label='std dev')
    # ax[0].set_title("Phi Resolution")
    # ax[1].set_title("Theta Resolution")
    # ax[0].legend()
    # ax[1].legend()

    # # plot 2D histograms for res vs angles
    # fig, ax = plt.subplots(1, 2, figsize=(10, 10))

    # ax[0].hist2d(truthPhis, phiRes, bins=(len(truthPhiBins), 20), cmap='viridis')
    # ax[0].set_xlabel(r"$\Phi$")
    # ax[0].set_ylabel(r"$\Phi Resolution$")

    # ax[1].hist2d(truthThetas, thetaRes, bins=(len(truthThetaBins), 20), cmap='viridis')
    # ax[1].set_xlabel(r"$\Theta$")

    #plt.show()

def calcSpBDist(recoDfs, assocRecoIndicesList, event):
    EventRecoDf = recoDfs[event]
    
    recos_spB_dists = {}
    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        if len(recoIndices) == 0:
            continue
        assocRecoData = (EventRecoDf.iloc[recoIndices])
        recos_spB_locs = np.array(assocRecoData[["spB_x", "spB_y", "spB_z"]])
        recos_spB_dists[truthIndex] = (np.linalg.norm(recos_spB_locs, axis=1))

    return recos_spB_dists

def calcMeanDist(recoDfs, assocRecoIndicesList, event):
    EventRecoDf = recoDfs[event]
    
    recos_mean_dists = {}
    for truthIndex, recoIndices in enumerate(assocRecoIndicesList):
        if len(recoIndices) == 0:
            continue
        assocRecoData = (EventRecoDf.iloc[recoIndices])
        recos_spB_locs = np.array(assocRecoData[["spB_x", "spB_y", "spB_z"]])
        recos_spB_dists = (np.linalg.norm(recos_spB_locs, axis=1))
        recos_spM_locs = np.array(assocRecoData[["spM_x", "spM_y", "spM_z"]])
        recos_spM_dists = (np.linalg.norm(recos_spM_locs, axis=1))
        recos_spT_locs = np.array(assocRecoData[["spT_x", "spT_y", "spT_z"]])
        recos_spT_dists = (np.linalg.norm(recos_spT_locs, axis=1))
        recos_mean_dists[truthIndex] = np.mean([recos_spB_dists, recos_spM_dists, recos_spT_dists], axis=0)

    return recos_mean_dists

def plot_spB_dist_vs_res(ax, tpData, event):
    recoDfs, truthDfs = tpData

    recoLocList, truthLocList = getLocs(tpData, event)
    recoToTruthDists = allRecoToTruthDists(recoLocList, truthLocList, event)
    assocRecoIndicesList = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)
    recos_spB_dists_dict = calcSpBDist(recoDfs, assocRecoIndicesList, event)
    truthResolutions_dict = calcEventResolutions(recoLocList, truthLocList, assocRecoIndicesList, indiceType='TruthIndex')

    max_ys = {}
    recos_mean_dist_dict = {'phi':[], 'theta':[]}
    abs_val_truthRes_dict = {'phi':[], 'theta':[]}
    for i, angle in enumerate(['phi', 'theta']):
        max_ys[angle] = 0
        for recos_spB_dists, truthResolutions in zip(recos_spB_dists_dict.values(), truthResolutions_dict.values()):
            ax[i].scatter(recos_spB_dists, np.abs(truthResolutions[angle]))
            #ax[i].hist2d(recos_spB_dists, np.abs(truthResolutions[angle]), bins=(10, 10), cmap='viridis')
            ax[i].set_xlabel("spB dist")
            ax[i].set_ylabel(f"|{angle} res|")

            y_max = np.max(np.abs(truthResolutions[angle]))
            if y_max > max_ys[angle]:
                max_ys[angle] = y_max

            recos_mean_dist_dict[angle].extend(recos_spB_dists)
            abs_val_truthRes_dict[angle].extend(np.abs(truthResolutions[angle]))
        
    return max_ys, recos_mean_dist_dict, abs_val_truthRes_dict

def plot_sp_mean_dist_vs_res(ax, tpData, event):
    recoDfs, _ = tpData

    recoLocList, truthLocList = getLocs(tpData, event)
    recoToTruthDists = allRecoToTruthDists(recoLocList, truthLocList, event)
    assocRecoIndicesList = getAssociatedRecoIndices(recoToTruthDists, cutoff=0.1)
    recos_mean_dists_dict = calcMeanDist(recoDfs, assocRecoIndicesList, event)
    truthResolutions_dict = calcEventResolutions(recoLocList, truthLocList, assocRecoIndicesList, indiceType='TruthIndex')

    max_ys = {}
    recos_mean_dist_dict = {'phi':[], 'theta':[]}
    abs_val_truthRes_dict = {'phi':[], 'theta':[]}
    for i, angle in enumerate(['phi', 'theta']):
        max_ys[angle] = 0
        for recos_mean_dists, truthResolutions in zip(recos_mean_dists_dict.values(), truthResolutions_dict.values()):
            ax[i].scatter(recos_mean_dists, np.abs(truthResolutions[angle]))
            #ax[i].hist2d(recos_mean_dists, np.abs(truthResolutions[angle]), bins=(10, 10), cmap='viridis')
            ax[i].set_xlabel("sp mean dist")
            ax[i].set_ylabel(f"|{angle} res|")
            
            y_max = np.max(np.abs(truthResolutions[angle]))
            if y_max > max_ys[angle]:
                max_ys[angle] = y_max

            recos_mean_dist_dict[angle].extend(recos_mean_dists)
            abs_val_truthRes_dict[angle].extend(np.abs(truthResolutions[angle]))
    
    return max_ys, recos_mean_dist_dict, abs_val_truthRes_dict
    
def layerAnalysis(tpData, energy):
    """Code for Layer Analysis"""
    fig, spBDistAx = plt.subplots(2, 2, figsize=(10, 5), sharex=True, sharey=False)
    fig.suptitle(f"layer analysis: {energy}GeV")
    numEvents = len(tpData[0])

    max_ys_spB = {'phi':[], 'theta':[]}
    max_ys_mean = {'phi':[], 'theta':[]}
    recos_mean_dist_dict_spB = {'phi':[], 'theta':[]}
    recos_mean_dist_dict_mean = {'phi':[], 'theta':[]}
    abs_val_truthRes_dict_spB = {'phi':[], 'theta':[]}
    abs_val_truthRes_dict_mean = {'phi':[], 'theta':[]}

    for event in range(numEvents):
        curr_max_ys_spB, curr_spB_recos_mean_dist, curr_spB_abs_val_truthRes = plot_spB_dist_vs_res(spBDistAx[0], tpData, event)
        curr_max_ys_mean, curr_mean_recos_mean_dist, curr_mean_abs_val_truthRes = plot_sp_mean_dist_vs_res(spBDistAx[1], tpData, event)

        for angle in ['phi', 'theta']:
            max_ys_spB[angle].append(curr_max_ys_spB[angle])
            max_ys_mean[angle].append(curr_max_ys_mean[angle])
            recos_mean_dist_dict_spB[angle].extend(curr_spB_recos_mean_dist[angle])
            recos_mean_dist_dict_mean[angle].extend(curr_mean_recos_mean_dist[angle])
            abs_val_truthRes_dict_spB[angle].extend(curr_spB_abs_val_truthRes[angle])
            abs_val_truthRes_dict_mean[angle].extend(curr_mean_abs_val_truthRes[angle])


    for i, angle in enumerate(['phi', 'theta']):
        #sort and get the 90th percentile
        percentile = 0.9
        max_ys_spB[angle] = sorted(max_ys_spB[angle])
        max_ys_mean[angle] = sorted(max_ys_mean[angle])
        max_ys_spB[angle] = max_ys_spB[angle][int(percentile*len(max_ys_spB[angle]))]
        max_ys_mean[angle] = max_ys_mean[angle][int(percentile*len(max_ys_mean[angle]))]

        spBDistAx[0, i].set_ylim(0, (max_ys_spB[angle]))
        spBDistAx[1, i].set_ylim(0, (max_ys_mean[angle]))

    #plot 2D histograms for res vs angles
    fig, ax = plt.subplots(2, 2, figsize=(10, 5), sharex=True)
    fig.suptitle(f"layer analysis: {energy}GeV")
    #plot spB and means as before

    for i, angle in enumerate(['phi', 'theta']):
        ax[0, i].hist2d(recos_mean_dist_dict_spB[angle], abs_val_truthRes_dict_spB[angle], bins=(50, 500), cmap='viridis')
        ax[0, i].set_xlabel("spB dist")
        ax[0, i].set_ylabel(f"|{angle} res|")
        ax[0, i].set_ylim(0, (max_ys_spB[angle]))

        ax[1, i].hist2d(recos_mean_dist_dict_mean[angle], abs_val_truthRes_dict_mean[angle], bins=(50, 500), cmap='viridis')
        ax[1, i].set_xlabel("sp mean dist")
        ax[1, i].set_ylabel(f"|{angle} res|")
        ax[1, i].set_ylim(0, (max_ys_mean[angle]))

def redundancyVsAngle(ax, tpData, energy):
    truthResDict = getDictForAllEvents(tpData, calcEventResolutions)

    numRecosPerTruth = getNumRecosPerTruth(truthResDict)
    plotRedundancyVsAngleRange(numRecosPerTruth, energy)
    plotRedundancyVsBinnedTheta(ax, numRecosPerTruth, energy, num_bins=10)

#global stuff
energies = ['1', '10', '100']
friendlyColours = plt.cm.Set1(np.linspace(0, 1, len(energies)))
energy_colours = {energy: friendlyColours[i] for i, energy in enumerate(energies)}

if __name__ == "__main__":
    from tp_processing import loadTrackParams

    def test():
        # load tp data
        _, redundancyBarAx = plt.subplots()
        for energy in energies:

            recoPath = f"Plotting/data/{energy}GeV/TrackParams/reconstructedTPs.csv"
            truthPath = f"Plotting/data/{energy}GeV/TrackParams/truthTPs.csv"
            recoDfs, truthDfs = loadTrackParams(recoPath, truthPath)
            tpData = (recoDfs, truthDfs)

            
            #layerAnalysis(tpData, energy)
            plotMultiEventRes(tpData, energy)
            #redundancyVsAngle(redundancyBarAx, tpData, energy)
            

        plt.show()

    test()
        