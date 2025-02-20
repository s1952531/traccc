import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
from matplotlib.animation import FuncAnimation

from findEventHeaderLines import getDataLines

def loadTrackParams(recoPath, truthPath):
    recoDataLines = getDataLines(recoPath)
    truthDataLines = getDataLines(truthPath)

    assert len(recoDataLines) == len(truthDataLines), "Reco and truth paths must be the same length"
    
    numEvents = len(recoDataLines)
    col_names = ["x", "y", "z", "phi", "phi_var", "theta", "theta_var"]
    
    recoDfs, truthDfs = [], []

    for event in range(numEvents):
        eventFirstLine = (recoDataLines[event][0], truthDataLines[event][0])
        nRowsInEvent = (recoDataLines[event][1] + 1 - recoDataLines[event][0], 
                        truthDataLines[event][1] + 1 - truthDataLines[event][0])

        recoDfs.append(pd.read_csv(recoPath, names=col_names, dtype=float, skiprows=eventFirstLine[0], nrows=nRowsInEvent[0]))
        truthDfs.append(pd.read_csv(truthPath, names=col_names, dtype=float, skiprows=eventFirstLine[1], nrows=nRowsInEvent[1]))

    return recoDfs, truthDfs

def plotTPDualAngleDistr(ax, recoData, truthData, cbar, event):
    ax.clear()

    xlims = (min(truthData["phi"]) - 0.1, max(truthData["phi"]) + 0.1)
    ylims = (min(truthData["theta"]) - 0.1, max(truthData["theta"]) + 0.1)

    h = ax.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])

    # Update the colorbar
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
        ellipse = Ellipse((phi, theta), np.sqrt(phiVar) * 1e2, np.sqrt(thetaVar) * 1e2, edgecolor='red', facecolor='none')
        ax.add_patch(ellipse)

def test():
    recoPath = "Plotting/data/TrackParams/reconstructedTPs.csv"
    truthPath = "Plotting/data/TrackParams/truthTPs.csv"

    recoDfs, truthDfs = loadTrackParams(recoPath, truthPath)
    numEvents = len(recoDfs)

    fig, ax = plt.subplots(figsize=(8, 6))
    event_index = [0]  # Mutable list to track event index

    # Create initial plot and colorbar
    h = ax.hist2d(recoDfs[0]["phi"], recoDfs[0]["theta"], bins=10, cmap='viridis')
    cbar = fig.colorbar(h[3], ax=ax)

    def update(event):
        plotTPDualAngleDistr(ax, recoDfs[event_index[0]], truthDfs[event_index[0]], cbar, event_index[0])
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == "right":
            event_index[0] = (event_index[0] + 1) % numEvents
        elif event.key == "left":
            event_index[0] = (event_index[0] - 1) % numEvents
        update(event_index[0])

    fig.canvas.mpl_connect("key_press_event", on_key)
    
    update(0)
    plt.show()

test()
