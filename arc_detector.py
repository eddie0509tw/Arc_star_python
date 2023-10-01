import numpy as np

class ArcDetector:
    def __init__(self, img, min_radius, max_radius, step, threshold):
        self.img = img
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.step = step
        self.threshold = threshold

        self.sae = np.zeros(2,self.img.shape[0], self.img.shape[1])
        self.sae_lastest = np.zeros(2,self.img.shape[0], self.img.shape[1])

    def detect_corner(self):
        