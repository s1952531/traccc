import numpy as np

from plotting_helper_scripts.findEventHeaderLines import getDataLines

def loadSeeds(unfilteredSeedPath, filteredSeedPath):


    # read in seed info from unfiltered seed file
    with open(unfilteredSeedPath, "r") as file:
        dataLines = getDataLines(unfilteredSeedPath)
        #print(dataLines)

        #bx, by, bz, mx, my, mz, tx, ty, tz, weight, z_vertex
        UnfilteredSeeds = [] #contains a list for each event, each list contains all the seeds for that event

        #for each event
        for start, end in dataLines:
            #reset fileptr
            file.seek(0)

            event_unfiltered_seeds = []
            for i, line in enumerate(file):
                if i >= start and i <= end:
                    values = line.strip().split(',')
                    values = [float(value) for value in values]
                    event_unfiltered_seeds.append(values)

            # get all unique entries
            #print(len(event_unfiltered_seeds))
            event_unfiltered_seeds = list(set([tuple(seed) for seed in event_unfiltered_seeds]))
            #print(len(event_unfiltered_seeds))
            
            UnfilteredSeeds.append(event_unfiltered_seeds)

    # read in seed info from filtered seed file
    with open(filteredSeedPath, "r") as file:
        dataLines = getDataLines(filteredSeedPath)

        #print(dataLines)

        #bx, by, bz, mx, my, mz, tx, ty, tz, weight, z_vertex
        FilteredSeeds = []

        #for each event
        for start, end in dataLines:
            #reset fileptr
            file.seek(0)

            event_filtered_seeds = []
            for i, line in enumerate(file):
                if i >= start and i <= end:
                    values = line.strip().split(',')
                    values = [float(value) for value in values]
                    event_filtered_seeds.append(values)

            # get all unique entries
            #print(len(event_filtered_seeds))
            event_filtered_seeds = list(set([tuple(seed) for seed in event_filtered_seeds]))
            #print(len(event_filtered_seeds))
            
            FilteredSeeds.append(event_filtered_seeds)

    return UnfilteredSeeds, FilteredSeeds

#plot the seeds on ax
def plotSeeds(ax, seeds, event, style, colour='random', meas_z_vertex=True, matchToOrigin=False):


    # plot line between each seed spacepoints and the vertex
    seedCounter = 0
    colourList = []
    for seed in seeds[event]:

        if colour == 'random':
            #make each seed a different colour
            while True:
                colour = np.random.rand(3,) 
                #print(colour)
                if tuple(colour) not in colourList:
                    colourList.append(tuple(colour))
                    break

        bx, by, bz, mx, my, mz, tx, ty, tz, weight, z_vertex = seed
        if not meas_z_vertex:
            z_vertex = 0
        seedPoints = [(0, 0, z_vertex), (bx, by, bz), (mx, my, mz), (tx, ty, tz)]
        seedXs = [point[0] for point in seedPoints]
        seedYs = [point[1] for point in seedPoints]
        seedZs = [point[2] for point in seedPoints]
        if matchToOrigin:
            #remove z vertex from all z values
            seedZs = [z - z_vertex for z in seedZs]
        ax.plot(seedXs, seedYs, seedZs, c=colour, ls=style)
    
        seedCounter += 1

#loadSeeds("/home/aholmes/MPhys/Plotting/data/seeds/FilteredSeeds.csv", "")