import numpy as np
import cv2 as cv


def normalize_g(f_data: np.array,  g_data: np.array):
    """ Makes mean and std for the g_data be the same as for f_data """
    f_mean, f_std = cv.meanStdDev(f_data)
    g_mean, g_std = cv.meanStdDev(g_data)

    # Calculating alpha (it means how we should correct g mean)
    alpha = f_mean / f_std * g_std - g_mean

    result = (g_data + alpha) / g_std * f_std

    return result


def calculate_l1(left_seq: np.array, right_seq: np.array):
    """ Calculates L1 distance between left and right sequences """
    elements_dist = np.abs(right_seq - left_seq)
    return np.sum(elements_dist) / elements_dist.shape[0]
