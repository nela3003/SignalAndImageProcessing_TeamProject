# -*- coding: utf-8 -*-
"""
Signal and Image Processing 2017 by Raphael Sznitman.
Team Project
- Livio Baetscher
- Manuela Haefliger
- Marc-Antoine Jacques
Python Version: 3.6.1
"""

"""
Maybe try a two pass approach: - first use convolution to detect possible positions
                               - wherever there is signal, use circle fitting in the cropped neighbourhood to detect the glasses
"""

from preprocessing_utils import *

# ===============================================================
# =             Method 1 : With convolution                     =
# ===============================================================


def find_waldo_fftconvolve(img, template, min_red, max_green, max_blue, min_dist_peak, thresh_peak,
                           max_nber_peak, size_box, extract_red=True, plot=True):
    """
    Returns a list of possible positions of waldo in an image file. Search is done by fftconvolution with a template.
    :param img: path to an RGB image file
    :param template: a 2D (grayscale) numpy array used for searching waldo. /!\ gets flipped to obtain same effect as a 
    correlation.
    :param extract_red: boolean, should the convolution be performed on red pixels only?
    :param min_red: numeric, minimum value in R channel to class a pixel as red
    :param max_green: numeric, maximum value in G channel to class a pixel as red
    :param max_blue: numeric, maximum value in B channel to class a pixel as red
    :param min_dist_peak: int, minimal distance between peaks of detection in pixel
    :param thresh_peak: float, relative intensity of a peak compare to max intensity
    :param max_nber_peak: int, max number of peaks
    :param size_box: int, size of the box for plotting Waldo's position
    :param plot: boolean, print the plots?
    :return: a 2D numpy array with Waldo's most probable positions
    """
    image = plt.imread(img)
    # Isolate red pixels
    if extract_red:
        reds = ExtractRed(image, min_red, max_green, max_blue)
        grayscale = rgb2gray(reds)
        if plot:
            PlotHeatmap(image, reds, title='Binarized Red Pixels map', bar=False)
    else:
        grayscale = rgb2gray(image)

    grayscale -= np.mean(grayscale)
    # If use a non-symmetric template, flip it if for convolution (so that it does the same as correlation)
    template = np.fliplr(template)
    template = np.flipud(template)
    template -= np.mean(template)

    t1 = time.time()
    # Look for template, heatmap of template in different regions
    score = scipy.signal.fftconvolve(grayscale, template, mode='same')

    # Isolate peaks
    peak_positions = feature.corner_peaks(score, min_distance=min_dist_peak, indices=True, threshold_rel=thresh_peak,
                                          num_peaks=max_nber_peak)
    t2 = time.time()
    print('Elapsed time: {:03f}'.format(t2 - t1))
    if plot:
        PlotHeatmap(image, score, title='Convolution score')

    # Draw a rectangle at the position of the peaks -> this is slow and redundant, could be improved
    if plot:
        peak_positions_img = feature.corner_peaks(score, min_distance=min_dist_peak, indices=False,
                                              threshold_rel=thresh_peak, num_peaks=max_nber_peak)
        for pos in peak_positions:
            DrawRectangle(peak_positions_img, pos[0], pos[1], size_box)
        PlotHeatmap(image, peak_positions_img, title='Most probable positions of Waldo', bar=False)
    return peak_positions
