
import numpy as np
from scipy.signal import convolve2d
from scipy.misc import imsave
from scipy.spatial import cKDTree

import matplotlib


def run_relative_accuracy_metrics(refDSM, testDSM, refMask, testMask, plot=None):

    PLOTS_ENABLE = True
    if plot is None: PLOTS_ENABLE = False

    # Compute relative vertical accuracy

    # Evaluate only in overlap region
    evalMask = refMask & testMask

    # Calculate Z-RMS Error
    delta = testDSM - refDSM
    delta = delta*evalMask
    zrmse = np.sqrt(np.sum(delta * delta) / delta.size)

    # Generate relative vertical accuracy plots
    if PLOTS_ENABLE:
        errorMap = delta
        delta[evalMask == 0] = np.nan
        plot.make(errorMap, 'Terrain Model - Height Error', 581, saveName="relVertAcc_hgtErr", colorbar=True)

        errorMap[errorMap > 5] = 5
        errorMap[errorMap < -5] = -5
        plot.make(errorMap, 'Terrain Model - Height Error', 582, saveName="relVertAcc_hgtErr_clipped", colorbar=True)



    # Compute relative horizontal accuracy

    # Find region edge pixels
    kernel = np.ones((3, 3), np.int)
    refEdge = convolve2d(refMask.astype(np.int), kernel, mode="same", boundary="symm")
    testEdge = convolve2d(testMask.astype(np.int), kernel, mode="same", boundary="symm")
    refEdge = (refEdge < 9) & refMask
    testEdge = (testEdge < 9) & testMask
    refPts = refEdge.nonzero()
    testPts = testEdge.nonzero()

    # Use KD Tree to find test point nearest each reference point
    tree = cKDTree(np.transpose(testPts))
    dist, indexes = tree.query(np.transpose(refPts))

    hrmse = np.sqrt(np.sum(dist * dist) / dist.size)

    # Generate relative horizontal accuracy plots
    if PLOTS_ENABLE:
        plot.make(refEdge, 'Reference Model Perimeters', 591, saveName="relHorzAcc_edgeMapRef")
        plot.make(testEdge, 'Test Model Perimeters', 592, saveName="relHorzAcc_edgeMapTest")

        plt = plot.make(None,'Relative Horizontal Accuracy')
        plt.plot(refPts[0], refPts[1], 'r.', markersize=1)
        plt.plot(testPts[0], testPts[1], 'b.', markersize=1)
        plt.plot((refPts[0], testPts[0][indexes]), (refPts[1], testPts[1][indexes]), 'k', linewidth=0.1)
        plot.save("relHorzAcc_nearestPoints")
        #imsave("plots//refMask.gif", refMask.astype(np.int) * 255)
        #imsave("plots//testMask.gif", testMask.astype(np.int) * 255)
        #imsave("plots//refEdge.gif", refEdge.astype(np.int) * 255)
        #imsave("plots//testEdge.gif", testEdge.astype(np.int) * 255)

    metrics = {
        'zrmse': zrmse,
        'hrmse': hrmse
    }
    return metrics
