def findEventHeaderLines(filename):
    #get all lines sstarting with Event using enum
    eventHeaderLines = []
    with open(filename, 'r') as file:
        for i, line in enumerate(file):
            if line.startswith('Event'):
                eventHeaderLines.append(i)

    return eventHeaderLines

def getDataLines(filename):
    eventHeaderLines = findEventHeaderLines(filename)

    #get numLines in file
    with open(filename, 'r') as file:
        numLines = sum(1 for line in file)
    
    dataLines = []
    for i in range(len(eventHeaderLines)):
        if i < len(eventHeaderLines)-1:
            dataLines.append((eventHeaderLines[i]+1, eventHeaderLines[i+1]-2))
        else:
            dataLines.append((eventHeaderLines[i]+1, numLines-1))

    return dataLines
    
#print(getDataLines("/home/aholmes/MPhys/Plotting/data/TrackParams/reconstructedTPs.csv"))

# headerLines = findEventHeaderLines("/home/aholmes/MPhys/Plotting/data/seeds/FilteredSeeds.csv")

# dataLines = getDataLines("/home/aholmes/MPhys/Plotting/data/seeds/FilteredSeeds.csv")

# print(dataLines)