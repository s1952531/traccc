import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np

try:#__name__ == "__main__":
    from findEventHeaderLines import getDataLines
except:
    from plotting_helper_scripts.findEventHeaderLines import getDataLines


def loadTrackParams(recoPath, truthPath):

    # print cwd
    import os
    print(os.getcwd())
    print(recoPath)
    print(truthPath)

    recoDataLines = getDataLines(recoPath)
    truthDataLines = getDataLines(truthPath)

    assert len(recoDataLines) == len(truthDataLines), "Reco and truth paths must be the same length"
    numEvents = len(recoDataLines)

    #both paths have csv of has x, y, z; phi, phi_var, theta, theta_var
    
    #i want to have x, y, z, phi, phi_var, theta, theta_var as names of the cols
    #global track dir params: x, y, z; phi, phi_var, theta, theta_var; spB_x, spB_y, spB_z, spM_x, spM_y, spM_z, spT_x, spT_y, spT_z
    col_names = ["x", "y", "z", "phi", "phi_var", "theta", "theta_var", "spB_x", "spB_y", "spB_z", "spM_x", "spM_y", "spM_z", "spT_x", "spT_y", "spT_z"]
    
    recoDfs = []
    truthDfs = []

    for event in range(numEvents):
        eventFirstLine = (recoDataLines[event][0], truthDataLines[event][0])
        nRowsInEvent = (recoDataLines[event][1]+1 -recoDataLines[event][0], truthDataLines[event][1]+1 -truthDataLines[event][0])

        # print("\nEvent: ", event)
        # print("Reco first line: ", eventFirstLine[0])
        # print("Reco num rows: ", nRowsInEvent[0])

        # print("Truth first line: ", eventFirstLine[1])
        # print("Truth num rows: ", nRowsInEvent[1])

        recoDfs.append(pd.read_csv(recoPath, names=col_names, dtype=float, skiprows=eventFirstLine[0], nrows=nRowsInEvent[0]))
        truthDfs.append(pd.read_csv(truthPath, names=col_names, dtype=float, skiprows=eventFirstLine[1], nrows=nRowsInEvent[1]))

    return recoDfs, truthDfs

def plotTrackParamsSingleAngleDistr(tpData, angle):
    #plot distribution of reco phi around truth phi

    recoData = tpData[0]
    truthData = tpData[1]
    
    angle = angle.lower()

    isEta = False

    if angle == 'eta':
        isEta = True
        angle = 'theta'
        latexAngle = r'$\eta$'
    elif angle == "phi":
        latexAngle = r'$\Phi$'
    elif angle == "theta":
        latexAngle = r'$\Theta$'
        
    numPlots = len(truthData[angle])
    fig, ax = plt.subplots(1, numPlots, figsize=(10, 5), sharex=True, sharey=True)

    #with binwidth = sqrt phi_var
    #for each truth phi plot the dist of reco phi
    i = 0
    for truthAngle in truthData[angle]:
        if isEta:
            eta = -np.log(np.tan(truthAngle/2))
            ax[i].set_title(f"{latexAngle}={eta:.4f}\n{r'$\Theta$'}={truthAngle:.4f}", fontsize=10)
            truthAngle = eta
        else:
            ax[i].set_title(f"{latexAngle}={truthAngle:.4f}", fontsize=10)
        
        #center around truthPhi
        if isEta:
            recoPhis = -np.log(np.tan(recoData[angle]/2)) - truthAngle
        else:
            recoPhis = recoData[angle] - truthAngle
        ax[i].hist(recoPhis, bins=500, histtype='step', label=f"Truth {angle}: {truthAngle}")

        i+=1

def plotTPDualAngleDistr(tpData):
    recoData = tpData[0]
    truthData = tpData[1]
    
    xlims = (min(truthData["phi"])-0.1, max(truthData["phi"])+0.1)
    ylims = (min(truthData["theta"])-0.1, max(truthData["theta"])+0.1)


    #def 2D plot
    plt.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])
    plt.colorbar()
    plt.scatter(truthData["phi"], truthData["theta"], s=50, marker='x', color='red')
    plt.scatter(recoData["phi"], recoData["theta"], s=50, marker='x', color='pink')

    plt.title(f"{len(truthData)} truth and {len(recoData)} reco bound TPs")
    plt.xlabel(r"$\Phi$")
    plt.ylabel(r"$\Theta$")
    plt.tight_layout()

    #for each truthTP plot an ellipse of stdDevs around it
    #loop over rows in truthData

    phiVals = truthData["phi"].values
    phiStdDevs = np.sqrt(truthData["phi_var"].values)

    thetaVals = truthData["theta"].values
    thetaStdDevs = np.sqrt(truthData["theta_var"].values)

    for phi, phiStdDev, theta, thetaStdDev in zip(phiVals, phiStdDevs, thetaVals, thetaStdDevs):
        print(phi, theta)
        ellipse = Ellipse((phi, theta), phiStdDev*1e2, thetaStdDev*1e2, edgecolor='red', facecolor='none')
        #ellipse = Ellipse((phi, theta), 0.1, 0.1, edgecolor='red', facecolor='none')

        plt.gca().add_artist(ellipse)

def plotTruthTP3D(ax, truthData):
    #plot a line from origin to truthTP xyz

    for i in range(len(truthData)):
        xyz = truthData.iloc[i][["x", "y", "z"]].values

        #extrapolate this so that proj onto xy plane is 200
        xyRadius = np.linalg.norm(xyz[:2])
        scale = 200/xyRadius
        xyz = xyz * scale

        ax.plot([0, xyz[0]], [0, xyz[1]], [0, xyz[2]], color='blue', lw=5, alpha=0.2)

def plotRecoTP3D(ax, recoData):
    #plot a line from origin to recoTP xyz

    for i in range(len(recoData)):
        xyz = recoData.iloc[i][["x", "y", "z"]].values

        #extrapolate this so that proj onto xy plane is 200
        xyRadius = np.linalg.norm(xyz[:2])
        scale = 200/xyRadius
        xyz = xyz * scale

        ax.plot([0, xyz[0]], [0, xyz[1]], [0, xyz[2]], color='pink', lw=5, alpha=0.2, linestyle='dotted')


def test():
    recoPath = "Plotting/data/TrackParams/reconstructedTPs.csv"
    truthPath = "Plotting/data/TrackParams/truthTPs.csv"

    event = 0

    recoDfs, truthDataDfs = loadTrackParams(recoPath, truthPath)

    numEvents = len(recoDfs)
    for event in range(numEvents):

        recoData = recoDfs[event]
        truthData = truthDataDfs[event]

        tpData = (recoData, truthData)


        #plotTrackParamsSingleAngleDistr(tpData, "phi")
        #plotTrackParamsSingleAngleDistr(tpData, "theta")
        plotTrackParamsSingleAngleDistr(tpData, "eta")
        #plt.show()

        #plotTPDualAngleDistr(tpData)

        plt.show()

#test()