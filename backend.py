import cv2
import numpy as np

class Backend:

    def __init__(self, image, noise_kernel, close_kernel, blur_kernel, morph_kernel, area_thresh, roundness_thresh):
        self.image = image
        self.noise_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (noise_kernel, noise_kernel))
        self.close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (close_kernel, close_kernel))
        self.cropped_image = self.crop()
        self.blur_kernel = (blur_kernel, blur_kernel)
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_kernel, morph_kernel))
        self.area_thresh = area_thresh
        self.roundness_thresh = roundness_thresh

    def crop(self):
        img = cv2.imread(self.image)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower = np.array([80, 24, 20])
        upper = np.array([130, 255, 255])
        isolate_green = cv2.inRange(img_hsv, lower, upper)

        rm_noise = cv2.morphologyEx(isolate_green, cv2.MORPH_OPEN, self.noise_kernel)
        close_bounds = cv2.morphologyEx(rm_noise, cv2.MORPH_CLOSE, self.close_kernel)

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

        #### CHECK THIS -- MOST LIKELY WILL NEED TO CHANGE
        aspected_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[2]/cv2.boundingRect(cnt)[3] > (95/100) and cv2.boundingRect(cnt)[2]/cv2.boundingRect(cnt)[3] < (100/95)]
        border = max(aspected_contours, key=lambda cnt: cv2.contourArea(cnt))
        x, y, w, h = cv2.boundingRect(border)
        cropped = img[y:y+h, x:x+w]

        return cropped
        
    
    def count(self):
        img = self.cropped_image

        grey_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grey_scale, self.blur_kernel, 0)

        canny = cv2.Canny(blurred, 30, 150)

        cleaned_canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, self.morph_kernel)

        contours, _ = cv2.findContours(
            cleaned_canny, 
            cv2.RETR_TREE,    
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = [contour for contour in contours if cv2.contourArea(contour) > self.area_thresh]
        contours = [contour for contour in contours if (lambda area, perimeter: (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0)(
        cv2.contourArea(contour), cv2.arcLength(contour, True)) >= self.roundness_thresh]
        num_contours = len(contours)

        overlayed = img.copy()
        cv2.drawContours(overlayed, contours, -1, (0, 255, 0), 2)

        return overlayed, num_contours