import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Ellipse
from plotting_helper_scripts.bin_processing import loadBinData, plot_populated_bins
from plotting_helper_scripts.seed_processing import loadSeeds, plotSeeds
from plotting_helper_scripts.sp_processing import loadSPData, plotSP
from plotting_helper_scripts.tp_processing import loadTrackParams, plotTruthTP3D, plotRecoTP3D

def load():
    # Load bins
    rDataPath   = "Plotting/data/bins/r_bin_borders.csv"
    phiDataPath = "Plotting/data/bins/phi_bin_borders.csv"
    zDataPath   = "Plotting/data/bins/z_bin_borders.csv"
    rho_bins, phi_bins, z_bins = loadBinData(rDataPath, phiDataPath, zDataPath, mergedRBins=True)
    binData = (rho_bins, phi_bins, z_bins)  

    # Load SP data
    spFilePath = "Plotting/data/spacepoints/sp.csv"
    spData = loadSPData(spFilePath, binData)

    # Load seeds
    unfilteredSeedPath  = "Plotting/data/seeds/UnfilteredSeeds.csv"
    filteredSeedPath    = "Plotting/data/seeds/FilteredSeeds.csv"
    UnfilteredSeeds, FilteredSeeds = loadSeeds(unfilteredSeedPath, filteredSeedPath)
    seedData = {"uf": UnfilteredSeeds, "f": FilteredSeeds}

    # Load track parameters
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

def plot():
    ax.clear()  # Clear the 3D plot
    ax2.clear()  # Clear the 2D histogram plot
    
    binData, spData, seedData, tpData = allData
    truthData = tpData[1][current_event]
    recoData = tpData[0][current_event]

    # Conditionally plot elements based on toggle state for 3D plot
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

    # Mark reference points
    ax.scatter(0, 0, 0, color='red', marker='x', s=100)

    # Add heading with current event
    ax.text2D(0.5, 0.95, f'Event {current_event}', ha='center', va='top', fontsize=14, transform=ax.transAxes)

    # Now plot the 2D histogram on ax2, using the original plotTPDualAngleDistr function
    xlims = (min(truthData["phi"]) - 0.1, max(truthData["phi"]) + 0.1)
    ylims = (min(truthData["theta"]) - 0.1, max(truthData["theta"]) + 0.1)
    
    # Create a colorbar for the 2D plot, only if it doesn't already exist
    if 'cbar' not in plot.__dict__:
        h = ax2.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])
        cbar = fig.colorbar(h[3], ax=ax2)
        plot.cbar = cbar
    else:
        h = ax2.hist2d(recoData["phi"], recoData["theta"], bins=10, cmap='viridis', range=[xlims, ylims])
        plot.cbar.update_normal(h[3])

    # Call the function to update the 2D plot with scatter and ellipses
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
    total_events = len(allData[1])  # Assuming spData contains the number of events
    
    # Change event based on key press
    if event.key == 'right' and current_event < total_events - 1:
        current_event += 1
    elif event.key == 'left' and current_event > 0:
        current_event -= 1

    plot()  # Redraw the plot with updated event

def main():
    global fig, ax, ax2, allData, current_event, toggle_states, buttons

    current_event = 0  # Initialize event counter

    # Create figure
    fig = plt.figure(figsize=(12, 6))
    
    # Create the 3D plot axis
    ax = fig.add_subplot(121, projection='3d')
    
    # Create the 2D histogram axis
    ax2 = fig.add_subplot(122)

    # Load data
    allData = load()

    # Initial plot states
    toggle_states = {
        "bins": True,
        "sp": True,
        "seeds": True,
        "truth_tp": True,
        "reco_tp": True,
        "meas_z_vertex": True,  # New toggle state for measured Z vertices
        "matchToOrigin": False  # New toggle state for matchToOrigin
    }

    # Plot initial event
    plot()

    # Adjust layout for buttons
    plt.subplots_adjust(bottom=0.4)

    # Create buttons for toggling plots
    button_positions = {
        "bins": [0.1, 0.15, 0.1, 0.05],
        "sp": [0.22, 0.15, 0.1, 0.05],
        "seeds": [0.34, 0.15, 0.1, 0.05],
        "truth_tp": [0.46, 0.15, 0.1, 0.05],
        "reco_tp": [0.58, 0.15, 0.1, 0.05],
        "meas_z_vertex": [0.7, 0.15, 0.1, 0.05],  # New button for measured Z vertices
        "matchToOrigin": [0.82, 0.15, 0.1, 0.05]  # Button for matchToOrigin
    }

    # Create buttons
    buttons = {}
    for key, pos in button_positions.items():
        ax_button = plt.axes(pos)
        btn = Button(ax_button, key.capitalize())
        btn.color = 'lightblue' if toggle_states[key] else 'lightgray'
        btn.on_clicked(toggle_plot(key))
        buttons[key] = btn

    # Connect the key press event
    fig.canvas.mpl_connect('key_press_event', change_event)

    plt.show()

if __name__ == "__main__":
    main()
