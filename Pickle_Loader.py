import pickle
from scipy.interpolate import UnivariateSpline
import numpy as np
import matplotlib.pyplot as plt


def main():
    with open('data.pickle', 'rb') as f:
        data = pickle.load(f)
    with open('spline.pickle', 'rb') as f:
        spline = pickle.load(f)

    print(spline([500, 501, 502]))


if __name__ == '__main__':
    main()
