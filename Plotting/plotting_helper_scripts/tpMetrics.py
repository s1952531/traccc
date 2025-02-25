import numpy as np

def calcEuclideanDists(tpData):
    recoData = tpData[0]
    truthData = tpData[1]

    recoPhis = recoData['phi']
    truthPhis = truthData['phi']

    recoThetas = recoData['theta']
    truthThetas = truthData['theta']

    distList = [] 

    #for each truth, calculate the euclidean distance to each reco
    for truthPhi, truthTheta in zip(truthPhis, truthThetas):
        phiDiff = truthPhi - recoPhis
        thetaDiff = truthTheta - recoThetas

        distList.append(np.linalg.norm([phiDiff, thetaDiff], axis=0))
    
    return distList

def associateRecosToTruths(tpData):
    recoData = tpData[0]
    truthData = tpData[1]

    distList = calcEuclideanDists(tpData)

    #for each reco, find the closest truth
    for recoIndice in len(recoData):
        