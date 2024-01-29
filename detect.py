import cv2
import numpy as np
import logging

class LogoDetector:
    def __init__(self, obj_img, area_ratio_thresh=0.05, matcher_ratio_thresh=0.75, minHessian=400):
        self.obj_img = obj_img
        self.detector = cv2.xfeatures2d_SURF.create(hessianThreshold=minHessian)
        self.matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
        self.area_ratio_thresh = area_ratio_thresh
        self.ratio_thresh = matcher_ratio_thresh

        self.obj_corners = np.empty((4,1,2), dtype=np.float32)
        self.obj_corners[0,0,0] = 0
        self.obj_corners[0,0,1] = 0
        self.obj_corners[1,0,0] = self.obj_img.shape[1]
        self.obj_corners[1,0,1] = 0
        self.obj_corners[2,0,0] = self.obj_img.shape[1]
        self.obj_corners[2,0,1] = self.obj_img.shape[0]
        self.obj_corners[3,0,0] = 0
        self.obj_corners[3,0,1] = self.obj_img.shape[0]

        self.keypoints_obj, self.descriptors_obj = self.detector.detectAndCompute(self.obj_img, None)

    def detect(self, scene_img):
        #-- Check if scene image is valid
        if scene_img is None or scene_img.shape[0] == 0 or scene_img.shape[1] == 0:
            return False
        
        try:
            #-- Step 1: Detect the keypoints using SURF Detector, compute the descriptors
            keypoints_scene, descriptors_scene = self.detector.detectAndCompute(scene_img, None)

            #-- Step 2: Matching descriptor vectors with a FLANN based matcher
            # Since SURF is a floating-point descriptor NORM_L2 is used
            knn_matches = self.matcher.knnMatch(self.descriptors_obj, descriptors_scene, 2)

            #-- Filter matches using the Lowe's ratio test
            good_matches = []
            for m,n in knn_matches:
                if m.distance < self.ratio_thresh * n.distance:
                    good_matches.append(m)

            #-- Localize the object
            obj = np.empty((len(good_matches),2), dtype=np.float32)
            scene = np.empty((len(good_matches),2), dtype=np.float32)
            for i in range(len(good_matches)):
                #-- Get the keypoints from the good matches
                obj[i,0] = self.keypoints_obj[good_matches[i].queryIdx].pt[0]
                obj[i,1] = self.keypoints_obj[good_matches[i].queryIdx].pt[1]
                scene[i,0] = keypoints_scene[good_matches[i].trainIdx].pt[0]
                scene[i,1] = keypoints_scene[good_matches[i].trainIdx].pt[1]

            H, _ =  cv2.findHomography(obj, scene, cv2.RANSAC)
            if H is None:
                return False

            #-- Get the corners from the image_1 ( the object to be "detected" )
            scene_corners = cv2.perspectiveTransform(self.obj_corners, H)

            # calculate the area of the object in the scene
            area = cv2.contourArea(scene_corners)

            # calculate the ratio of the area of the object to the area of the scene
            ratio = area / (scene_img.shape[0] * scene_img.shape[1])

            result = ratio > self.area_ratio_thresh

            if result:
                logging.debug("LogoDetector: Detected")
                logging.debug("LogoDetector: Area: %f", area)
                logging.debug("LogoDetector: Scene Area: %f", scene_img.shape[0] * scene_img.shape[1])
                logging.debug("LogoDetector: Area Ratio: %f", ratio)
            return result
        except cv2.error as e:
            logging.warning("LogoDetector: OpenCV Error: %s, returning False", e)
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logo = cv2.imread("origin.png")
    detector = LogoDetector(logo)

    img = cv2.imread("example.png")

    if detector.detect(img):
        print("unlock")
    else:
        print("lock")