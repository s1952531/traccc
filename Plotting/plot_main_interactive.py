import matplotlib.pyplot as plt
from matplotlib.widgets import Button
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

def plot():
    ax.clear()  
    binData, spData, seedData, tpData = allData
    truthData = tpData[1][current_event]
    recoData = tpData[0][current_event]

    # Conditionally plot elements based on toggle state
    if toggle_states['bins']:
        plot_populated_bins(ax, spData, binData, current_event)
    if toggle_states['sp']:
        plotSP(ax, spData, current_event)
    if toggle_states['seeds']:
        plotSeeds(ax, seedData["uf"], current_event, style='dotted', colour='b')
        plotSeeds(ax, seedData["f"], current_event, style='solid', colour='g')
    if toggle_states['truth_tp']:
        plotTruthTP3D(ax, truthData)
    if toggle_states['reco_tp']:
        plotRecoTP3D(ax, recoData)

    # Mark reference points
    ax.scatter(0, 0, 0, color='red', marker='x', s=100)

    # Add heading with current event
    ax.text2D(0.5, 0.95, f'Event {current_event}', ha='center', va='top', fontsize=14, transform=ax.transAxes)

    fig.canvas.draw_idle()

def toggle_plot(key):
    def toggle(event):
        toggle_states[key] = not toggle_states[key]
        buttons[key].color = 'lightblue' if toggle_states[key] else 'lightgray'
        plot()
    return toggle

def change_event(direction):
    def on_click(event):
        global current_event
        total_events = len(allData[1])  # Assuming spData contains the number of events
        
        # Change event based on direction
        if direction == "next" and current_event < total_events - 1:
            current_event += 1
        elif direction == "prev" and current_event > 0:
            current_event -= 1

        plot()  # Redraw the plot with updated event
    return on_click

def main():
    global fig, ax, allData, current_event, toggle_states, buttons

    current_event = 0  # Initialize event counter

    # Create figure
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection='3d')

    # Load data
    allData = load()

    # Initial plot states
    toggle_states = {
        "bins": True,
        "sp": True,
        "seeds": True,
        "truth_tp": True,
        "reco_tp": True
    }

    # Plot initial event
    plot()

    # Adjust layout for buttons
    plt.subplots_adjust(bottom=0.4)

    # Button positions
    button_positions = {
        "bins": [0.1, 0.15, 0.1, 0.05],
        "sp": [0.22, 0.15, 0.1, 0.05],
        "seeds": [0.34, 0.15, 0.1, 0.05],
        "truth_tp": [0.46, 0.15, 0.1, 0.05],
        "reco_tp": [0.58, 0.15, 0.1, 0.05],
        "prev_event": [0.1, 0.05, 0.1, 0.05],
        "next_event": [0.22, 0.05, 0.1, 0.05]
    }

    # Create buttons
    buttons = {}
    for key, pos in button_positions.items():
        ax_button = plt.axes(pos)
        if key in ["prev_event", "next_event"]:
            btn = Button(ax_button, key.replace("_", " ").capitalize())
            btn.on_clicked(change_event("prev" if key == "prev_event" else "next"))
        else:
            btn = Button(ax_button, key.capitalize())
            btn.color = 'lightblue' if toggle_states[key] else 'lightgray'
            btn.on_clicked(toggle_plot(key))
        buttons[key] = btn

    plt.show()

if __name__ == "__main__":
    main()
