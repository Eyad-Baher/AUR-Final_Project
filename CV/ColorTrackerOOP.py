import cv2
import numpy as np

class ColorTracker():

    def __init__(self):

        self.video_path = 0
        self.cap = cv2.VideoCapture(self.video_path)

        self.LOWER_BLUE = np.array([100, 100, 50])
        self.UPPER_BLUE = np.array([130, 255, 255])

        self.kernel = np.ones((5, 5), np.uint8)
        self.min_area = 1000  


    def process_mask(self, mask, frame):

        
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_centroids = []

        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    detected_centroids.append((cx, cy))

                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.putText(frame, f"X:{cx} Y:{cy}", (cx - 20, cy - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return detected_centroids, mask
            


    def run_tracker(self):

        if not self.cap.isOpened():
            print('Error camera couldn\'t open')
            return

        while True:

            ret, frame = self.cap.read()
            if not ret:
                return
            blur = cv2.GaussianBlur(frame, (5, 5), 0)
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV) 

            mask_blue = cv2.inRange(hsv,self.LOWER_BLUE,self.UPPER_BLUE)

            centroid, cleaned_mask = self.process_mask(mask_blue, frame)

            cv2.imshow('Subtask 2 - Shape Detector', frame)
            cv2.imshow('Mask Feed', cleaned_mask)

            if cv2.waitKey(1) == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    tracker = ColorTracker()
    tracker.run_tracker()