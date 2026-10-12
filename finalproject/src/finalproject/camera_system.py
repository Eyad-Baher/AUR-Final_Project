import cv2
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class StreamReader(QThread):
    frame_ready = Signal(QImage)
    error = Signal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self._running = False
        self._cap = None

    def run(self):
        self._running = True
        cap = cv2.VideoCapture(self.url)
        self._cap = cap

        try:
            if not cap.isOpened():
                if self._running:
                    self.error.emit(f"Cannot open the link: {self.url}")
                return

            while self._running:
                ok, frame = cap.read()
                if not self._running:
                    break
                if not ok:
                    if self._running:
                        self.error.emit("Stream failed")
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                img = QImage(
                    rgb.data, w, h, ch * w, QImage.Format.Format_RGB888
                ).copy()
                self.frame_ready.emit(img)
        finally:
            cap.release()
            self._cap = None

    def stop(self):
        self._running = False
        # لا تستدعِ wait() هنا؛ قد يكون read() ما زال حاجزًا.
class StreamWidget(QLabel):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(500, 600)
        self.setText("Loading stream...")

        self.reader = StreamReader(url, self)
        self.reader.frame_ready.connect(self._update_frame)
        self.reader.error.connect(self.setText)

    def start(self):
        if not self.reader.isRunning():
            self.reader.start()

    def stop(self):
        self.reader.stop()

    def closeEvent(self, event):
        self.reader.stop()
        if self.reader.wait(1000):
            event.accept()
        else:
    
            self.reader.finished.connect(self.close)
            event.ignore()

    def _update_frame(self, img):
        pix = QPixmap.fromImage(img).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(pix)