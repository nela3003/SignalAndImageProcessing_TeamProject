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



def find_waldo_fftconvolve(img, tplt, min_red, max_green, max_blue, min_dist_peak, thresh_peak,
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
    template = tplt.copy()
    template = np.fliplr(template)
    template = np.flipud(template)
    template -= np.mean(template)

    t1 = time.time()
    # Look for template, heatmap of template in different regions
    score = scipy.signal.fftconvolve(grayscale, template, mode='same')
    score = skimage.feature.corner_harris(score)

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


# ----
# Test Templates
image = './data/images/04.jpg'
image = plt.imread(image)
reds = ExtractRed(image, 200, 100, 100)
reds_grayscale = rgb2gray(reds)

# Waldo's shirt
stripe_template = reds_grayscale[1170:1191, 1143:1151]
stripe_template = StripeMotif(height=12, width=2, nber_stripe=6) # Works better when transposed???????

# Glasses
image_grayscale = rgb2gray(np.copy(image))
image_grayscale = image_grayscale - np.mean(image_grayscale)
#edges = feature.canny(image, sigma_edge)
glass_template = image_grayscale[1146:1154, 1144:1155]

# head
head_template = image_grayscale[1139:1160, 1142:1154]
# Get head from another image
head_template2 = plt.imread('./data/images/27.jpg')
head_template2 = rgb2gray(head_template2)
head_template2 = head_template2[746:780, 1340:1370]
head_template2 = tuple(skimage.transform.pyramid_gaussian(head_template2, downscale=3))
head_template2 = head_template2[1]

# One example
find_waldo_fftconvolve('./data/images/04.jpg', stripe_template, 150, 100, 100, 20, 0.2, 5, 10, extract_red=True)
find_waldo_fftconvolve('./data/images/04.jpg', glass_template, 200, 100, 100, 200, 0.2, 10, 10, extract_red=False)
find_waldo_fftconvolve('./data/images/03.jpg', head_template, 200, 100, 100, 200, 0.2, 10, 10, extract_red=False)



############# OPEN CV ####################
"""
http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html
"""

img = './data/images/04.jpg'
img = cv2.imread(img,0)
img2 = img.copy()
img2 = img2.astype('float32')
# Using crop
template = StripeMotif(height=25, width=2, nber_stripe=5)
template = template.astype('float32')



w, h = template.shape[::-1]
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

for meth in methods:
    print(meth)
    img = img2.copy()
    method = eval(meth)

    # Apply template Matching
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    cv2.rectangle(img,top_left, bottom_right, 255, 2)


    PlotHeatmap(img, res, title=meth)

    plt.show()