import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from ColorTrackerOOP import ColorTracker


class CVWorker(QThread):
    frame_ready = Signal(QImage)   
    detections = Signal(list)      

    def __init__(self, source=0):
        super().__init__()
        self.tracker = ColorTracker()
        self.cap = cv2.VideoCapture(source)
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            annotated, dets = self.tracker.process_frame(frame)

            rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()

            self.frame_ready.emit(img)   
            self.detections.emit(dets)   

    def stop(self):
        self.running = False
        self.wait()
        self.cap.release()