import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Ellipse
from plotting_helper_scripts.bin_processing import loadBinData, plot_populated_bins
from plotting_helper_scripts.seed_processing import loadSeeds, plotSeeds
from plotting_helper_scripts.sp_processing import loadSPData, plotSP
from plotting_helper_scripts.tp_processing import loadTrackParams, plotTruthTP3D, plotRecoTP3D
from plotting_helper_scripts.tpMetrics import getLocs, allRecoToTruthDists, getAssociatedRecoIndices, calcEventResolutions, checkUniqueIndices, plotResolutions

cutoff = 0.1

# Functions from the first script
def load():
    rDataPath = "Plotting/data/bins/r_bin_borders.csv"
    phiDataPath = "Plotting/data/bins/phi_bin_borders.csv"
    zDataPath = "Plotting/data/bins/z_bin_borders.csv"
    rho_bins, phi_bins, z_bins = loadBinData(rDataPath, phiDataPath, zDataPath, mergedRBins=True)
    binData = (rho_bins, phi_bins, z_bins)

    spFilePath = "Plotting/data/spacepoints/sp.csv"
    spData = loadSPData(spFilePath, binData)

    unfilteredSeedPath = "Plotting/data/seeds/UnfilteredSeeds.csv"
    filteredSeedPath = "Plotting/data/seeds/FilteredSeeds.csv"
    UnfilteredSeeds, FilteredSeeds = loadSeeds(unfilteredSeedPath, filteredSeedPath)
    seedData = {"uf": UnfilteredSeeds, "f": FilteredSeeds}

    recoPath = "Plotting/data/TrackParams/reconstructedTPs.csv"
    truthPath = "Plotting/data/TrackParams/truthTPs.csv"
    recoDfs, truthDfs = loadTrackParams(recoPath, truthPath)
    tpData = (recoDfs, truthDfs)

    return binData, spData, seedData, tpData

def plotTPDualAngleDistr(ax, recoData, truthData, cbar, event):
    ax.clear()

    xlims = (min(truthData["phi"]) - 0.1, max(truthData["phi"]) + 0.1)
    ylims = (min(truthData["theta"]) - 0.1, max(truthData["theta"]) + 0.1)

    h = ax.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])

    cbar.update_normal(h[3])

    ax.scatter(truthData["phi"], truthData["theta"], s=50, marker='x', color='red', label="Truth")
    ax.scatter(recoData["phi"], recoData["theta"], s=50, marker='x', color='pink', label="Reco")

    ax.set_title(f"Event {event}: {len(truthData)} truth and {len(recoData)} reco bound TPs")
    ax.set_xlabel(r"$\Phi$")
    ax.set_ylabel(r"$\Theta$")
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    ax.legend()

    for phi, phiVar, theta, thetaVar in zip(truthData["phi"], truthData["phi_var"], truthData["theta"], truthData["theta_var"]):
        #ellipse = Ellipse((phi, theta), np.sqrt(phiVar) * 1e2, np.sqrt(thetaVar) * 1e2, edgecolor='red', facecolor='none')
        ellipse = Ellipse((phi, theta), cutoff, cutoff, edgecolor='red', facecolor='none')
        ax.add_patch(ellipse)

def plot():
    ax.clear()
    ax2.clear()

    binData, spData, seedData, tpData = allData
    truthData = tpData[1][current_event]
    recoData = tpData[0][current_event]

    if toggle_states['bins']:
        plot_populated_bins(ax, spData, binData, current_event)
    if toggle_states['sp']:
        plotSP(ax, spData, current_event)
    if toggle_states['seeds']:
        plotSeeds(ax, seedData["uf"], current_event, style='dotted', colour='b', meas_z_vertex=toggle_states['meas_z_vertex'], matchToOrigin=toggle_states['matchToOrigin'])
        plotSeeds(ax, seedData["f"], current_event, style='solid', colour='g', meas_z_vertex=toggle_states['meas_z_vertex'], matchToOrigin=toggle_states['matchToOrigin'])
    if toggle_states['truth_tp']:
        plotTruthTP3D(ax, truthData)
    if toggle_states['reco_tp']:
        plotRecoTP3D(ax, recoData)

    ax.scatter(0, 0, 0, color='red', marker='x', s=100)
    ax.text2D(0.5, 0.95, f'Event {current_event}', ha='center', va='top', fontsize=14, transform=ax.transAxes)

    xlims = (min(truthData["phi"]) - 0.1, max(truthData["phi"]) + 0.1)
    ylims = (min(truthData["theta"]) - 0.1, max(truthData["theta"]) + 0.1)

    if 'cbar' not in plot.__dict__:
        h = ax2.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])
        cbar = fig.colorbar(h[3], ax=ax2)
        plot.cbar = cbar
    else:
        h = ax2.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])
        plot.cbar.update_normal(h[3])

    plotTPDualAngleDistr(ax2, recoData, truthData, plot.cbar, current_event)

    fig.canvas.draw_idle()

def toggle_plot(key):
    def toggle(event):
        toggle_states[key] = not toggle_states[key]
        buttons[key].color = 'lightblue' if toggle_states[key] else 'lightgray'
        plot()
    return toggle

def change_event(event):
    global current_event
    total_events = len(allData[1])

    if event.key == 'right' and current_event < total_events - 1:
        current_event += 1
    elif event.key == 'left' and current_event > 0:
        current_event -= 1

    plot()

# Functions from the second script
class EventNavigator:
    def __init__(self, tpData):
        self.tpData = tpData
        self.numEvents = len(tpData[0])
        self.event = 0
        self.cutoff = cutoff
        self.recoLocList, self.truthLocList = getLocs(self.tpData, self.event)
        self.recoToTruthDists = allRecoToTruthDists(self.recoLocList, self.truthLocList, self.event)
        self.truthsRecoIndices = getAssociatedRecoIndices(self.recoToTruthDists, cutoff=self.cutoff)
        self.eventRes = calcEventResolutions(self.recoLocList, self.truthLocList, self.truthsRecoIndices)
        self.fig, self.ax = plt.subplots(2, len(self.eventRes), figsize=(10, 5))
        self.plotResolutions()

    def plotResolutions(self):
        plotCounter = 0
        for truthLoc, res in self.eventRes.items():
            #print type of tuple truthLoc
            phiRes = res['phi']
            thetaRes = res['theta']

            self.ax[0, plotCounter].clear()
            self.ax[1, plotCounter].clear()

            self.ax[0, plotCounter].hist(phiRes, bins=10, alpha=0.5, label='phi', color='blue')
            self.ax[1, plotCounter].hist(thetaRes, bins=10, alpha=0.5, label='theta', color='orange')
            self.ax[0, plotCounter].set_title(f"Truth @{truthLoc} ({len(phiRes)} recos)")
            self.ax[1, plotCounter].set_title(f"Truth @{truthLoc} ({len(phiRes)} recos)")
            self.ax[0, plotCounter].legend()
            self.ax[1, plotCounter].legend()

            plotCounter += 1

        self.fig.suptitle(f"Event {self.event}", fontsize=16)
        self.fig.canvas.draw()

    def on_key_press(self, event):
        if event.key == 'right':
            self.event = (self.event + 1) % self.numEvents
        elif event.key == 'left':
            self.event = (self.event - 1) % self.numEvents
        self.recoLocList, self.truthLocList = getLocs(self.tpData, self.event)
        self.recoToTruthDists = allRecoToTruthDists(self.recoLocList, self.truthLocList, self.event)
        self.truthsRecoIndices = getAssociatedRecoIndices(self.recoToTruthDists, cutoff=self.cutoff)
        self.eventRes = calcEventResolutions(self.recoLocList, self.truthLocList, self.truthsRecoIndices)
        self.plotResolutions()


def main():
    global fig, ax, ax2, allData, current_event, toggle_states, buttons

    current_event = 0

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122)

    allData = load()

    toggle_states = {
        "bins": True,
        "sp": True,
        "seeds": True,
        "truth_tp": True,
        "reco_tp": True,
        "meas_z_vertex": True,
        "matchToOrigin": False
    }

    plot()

    plt.subplots_adjust(bottom=0.4)

    button_positions = {
        "bins": [0.1, 0.15, 0.1, 0.05],
        "sp": [0.22, 0.15, 0.1, 0.05],
        "seeds": [0.34, 0.15, 0.1, 0.05],
        "truth_tp": [0.46, 0.15, 0.1, 0.05],
        "reco_tp": [0.58, 0.15, 0.1, 0.05],
        "meas_z_vertex": [0.7, 0.15, 0.1, 0.05],
        "matchToOrigin": [0.82, 0.15, 0.1, 0.05]
    }

    buttons = {}
    for key, pos in button_positions.items():
        ax_button = plt.axes(pos)
        btn = Button(ax_button, key.capitalize())
        btn.color = 'lightblue' if toggle_states[key] else 'lightgray'
        btn.on_clicked(toggle_plot(key))
        buttons[key] = btn

    fig.canvas.mpl_connect('key_press_event', change_event)

    event_navigator = EventNavigator(allData[3])  # EventNavigator for 1D histograms
    event_navigator.fig.canvas.mpl_connect('key_press_event', event_navigator.on_key_press)

    plt.show()

if __name__ == "__main__":
    main()
