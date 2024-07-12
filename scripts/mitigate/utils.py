import numpy as np


def calculateLinearProbability(logprob):
    return np.round(np.exp(logprob) * 100)
