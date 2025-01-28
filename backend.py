import cv2
import numpy as np

class Backend:

    def __init__(self, image, noise_kernel, close_kernel, blur_kernel, morph_kernel, area_thresh, roundness_thresh):
        # initialise variables from GUI, create kernels for later use
        # parameters here chosen from GUI, I'll put a pound symbol with "here" next to where they appear in the code
        self.image = image
        self.noise_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (noise_kernel, noise_kernel))
        self.close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (close_kernel, close_kernel))
        self.cropped_image = self.crop()    # "automatically" crops, cool!
        self.blur_kernel = (blur_kernel, blur_kernel)
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_kernel, morph_kernel))
        self.area_thresh = area_thresh
        self.roundness_thresh = roundness_thresh

    def crop(self):
        '''
        Most of this is fairly standard preprocessing. 
        The goal of this method is to take the raw image 
        selected by the use and crop it to fit the green square.

        I just read in the image, converted the colorspace, 
        color thresholded, performed morphological operations, and found the box using contours
        '''
        img = cv2.imread(self.image)    # here
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower = np.array([80, 24, 20])
        upper = np.array([130, 255, 255])
        isolate_green = cv2.inRange(img_hsv, lower, upper)

        rm_noise = cv2.morphologyEx(isolate_green, cv2.MORPH_OPEN, self.noise_kernel)   # here
        close_bounds = cv2.morphologyEx(rm_noise, cv2.MORPH_CLOSE, self.close_kernel)   # here

        grey_scale = cv2.cvtColor(cv2.bitwise_and(img, img, mask=close_bounds), cv2.COLOR_BGR2GRAY)
        adaptive_thresh = cv2.adaptiveThreshold(
            grey_scale, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 
            11,
            2
        )

        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        aspected_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[2]/cv2.boundingRect(cnt)[3] > (95/100) and cv2.boundingRect(cnt)[2]/cv2.boundingRect(cnt)[3] < (100/95)]
        border = max(aspected_contours, key=lambda cnt: cv2.contourArea(cnt))
        x, y, w, h = cv2.boundingRect(border)
        cropped = img[y:y+h, x:x+w]

        return cropped
        
    
    def count(self):
        '''
        In this method I actually count the barnacles in the cropped image. 

        I convert colorspaces again, pretty much convolve the image using a gaussian kernel 
        (this tends to increase performance of the edge detection),
        perform canny edge detection, clean up/chose some of the detected edges, 
        and filter the barnacle contours based on size and roundess. These parameters can be finetuned using the GUI.
        The contours are counted and overlayed on the image.
        '''
        img = self.cropped_image

        grey_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grey_scale, self.blur_kernel, 0) # here

        canny = cv2.Canny(blurred, 30, 150)

        cleaned_canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, self.morph_kernel) # here

        contours, _ = cv2.findContours(
            cleaned_canny, 
            cv2.RETR_TREE,    
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = [contour for contour in contours if cv2.contourArea(contour) > self.area_thresh] # here
        contours = [contour for contour in contours if (lambda area, perimeter: (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0)(
        cv2.contourArea(contour), cv2.arcLength(contour, True)) >= self.roundness_thresh]   # here
        num_contours = len(contours)

        overlayed = img.copy()
        cv2.drawContours(overlayed, contours, -1, (0, 255, 0), 2)

        return overlayed, num_contours