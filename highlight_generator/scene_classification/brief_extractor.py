import cv2
import numpy as np

def extract_brief_descriptors(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # FAST keypoint detector
    fast = cv2.FastFeatureDetector_create()
    keypoints = fast.detect(gray, None)

    # BRIEF descriptor extractor
    brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
    keypoints, descriptors = brief.compute(gray, keypoints)

    return descriptors if descriptors is not None else np.array([])
