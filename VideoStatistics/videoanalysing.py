import cv2
import numpy as np


class SimpleVideoAnalyser:
    def __init__(self, file_path: str):
        self.video_obj = self._open_file(file_path)
        self.mean = None
        self.variance = None
        self.contrast = None
        self._calculate_measures()

    @staticmethod
    def _open_file(file_path: str):
        """ Opens video file """
        video_file = cv2.VideoCapture(file_path)
        return video_file

    def _calculate_measures(self):
        """ Calculates mean and std for every video frame and returns two arrays (3 x FRAME_COUNT) """
        frame_count = int(self.video_obj.get(cv2.CAP_PROP_FRAME_COUNT))

        self.mean = np.ndarray(shape=(3, frame_count))
        self.variance = np.ndarray(shape=(3, frame_count))
        self.contrast = np.zeros(shape=(1, frame_count))

        frame_ind = 0
        while self.video_obj.isOpened():
            read_successfully, frame = self.video_obj.read()

            if not read_successfully:
                break
            # Calculating mean and variance
            temp_mean, temp_variance = cv2.meanStdDev(frame)

            self.mean[:, frame_ind] = np.squeeze(np.flip(temp_mean))
            self.variance[:, frame_ind] = np.squeeze(np.flip(temp_variance))

            # Calculating image contrast
            img_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.contrast[0, frame_ind] = img_grey.std()

            frame_ind += 1

    def get_mean(self):
        """ Returns mean for every video frame as array (3 x FRAME_COUNT) """
        return self.mean

    def get_variance(self):
        """ Returns variance for every video frame as array (3 x FRAME_COUNT) """
        return self.variance

    def get_contrast(self):
        """ Returns contrast for every video frame and returns array (1 x FRAME_COUNT) """
        return self.contrast
