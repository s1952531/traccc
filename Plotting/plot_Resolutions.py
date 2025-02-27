import numpy as np
import matplotlib.pyplot as plt
from plotting_helper_scripts.tp_processing import loadTrackParams
from plotting_helper_scripts.tpMetrics import getLocs, allRecoToTruthDists, getAssociatedRecoIndices, calcEventResolutions, checkUniqueIndices, plotResolutions

class EventNavigator:
    def __init__(self, tpData):
        self.tpData = tpData
        self.numEvents = len(tpData[0])
        self.event = 0
        self.recoLocList, self.truthLocList = getLocs(self.tpData, self.event)
        self.recoToTruthDists = allRecoToTruthDists(self.recoLocList, self.truthLocList, self.event)
        self.truthsRecoIndices = getAssociatedRecoIndices(self.recoToTruthDists, cutoff=0.1)
        self.eventRes = calcEventResolutions(self.recoLocList, self.truthLocList, self.truthsRecoIndices, self.event)
        self.fig, self.ax = plt.subplots(2, len(self.eventRes), figsize=(10, 5))
        self.plotResolutions()

    def plotResolutions(self):
        plotCounter = 0
        for truthIndex, res in self.eventRes.items():
            phiRes = res['phi']
            thetaRes = res['theta']

            self.ax[0, plotCounter].clear()
            self.ax[1, plotCounter].clear()

            self.ax[0, plotCounter].hist(phiRes, bins=5, alpha=0.5, label='phi', color='blue')
            self.ax[1, plotCounter].hist(thetaRes, bins=5, alpha=0.5, label='theta', color='orange')
            self.ax[0, plotCounter].set_title(f"Truth {truthIndex} ({len(phiRes)} recos)")
            self.ax[1, plotCounter].set_title(f"Truth {truthIndex} ({len(phiRes)} recos)")
            self.ax[0, plotCounter].legend()
            self.ax[1, plotCounter].legend()

            plotCounter += 1

        # Update the event title dynamically
        self.fig.suptitle(f"Event {self.event}", fontsize=16)

        self.fig.canvas.draw()

    def on_key_press(self, event):
        if event.key == 'right':
            self.event = (self.event + 1) % self.numEvents
        elif event.key == 'left':
            self.event = (self.event - 1) % self.numEvents
        self.recoLocList, self.truthLocList = getLocs(self.tpData, self.event)
        self.recoToTruthDists = allRecoToTruthDists(self.recoLocList, self.truthLocList, self.event)
        self.truthsRecoIndices = getAssociatedRecoIndices(self.recoToTruthDists, cutoff=0.1)
        self.eventRes = calcEventResolutions(self.recoLocList, self.truthLocList, self.truthsRecoIndices, self.event)
        self.plotResolutions()

def main():
    # load tp data
    recoPath = "Plotting/data/TrackParams/reconstructedTPs.csv"
    truthPath = "Plotting/data/TrackParams/truthTPs.csv"
    recoDfs, truthDfs = loadTrackParams(recoPath, truthPath)
    tpData = (recoDfs, truthDfs)

    navigator = EventNavigator(tpData)

    # Connect the key press event
    navigator.fig.canvas.mpl_connect('key_press_event', navigator.on_key_press)

    plt.show()

main()
