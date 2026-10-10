import cv2
import numpy as np
from urllib.parse import parse_qs


class QRDecoder:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.detector = cv2.wechat_qrcode_WeChatQRCode()
        self.callback = None
        self.last_data = None
        self.reset_threshold = 30
        self.missing_count = 0

        self.show_display = True
        self.detection_interval = 3
        self.frame_count = 0
        self.preprocessed_frame = None
        self.res, self.points = (), ()


    def trigger_event(self, x, y):
        if self.callback:
                self.callback(x, y)

    def parse_QR_data(self, payload):
        try:
            parsed_data = parse_qs(payload.upper())

            if 'X' in parsed_data and 'Y' in parsed_data:
                x_val = float(parsed_data['X'][0])
                y_val = float(parsed_data['Y'][0])
                return x_val, y_val
        except (ValueError, IndexError):
            pass

        return None, None

    def process_frame(self, frame, draw=True):
        self.frame_count += 1

        if self.frame_count % self.detection_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = self.clahe.apply(gray)
            self.res, self.points = self.detector.detectAndDecode(gray)

        if len(self.res) > 0 and len(self.points) > 0:
            self.missing_count = 0

            for payload, bbox in zip(self.res, self.points):
                x, y = self.parse_QR_data(payload)
                if x is None:
                    continue

                if self.last_data != (x, y):
                    self.last_data = (x, y)
                    self.trigger_event(x, y)

                if draw:
                    pts = bbox.astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                    tl = tuple(pts[0][0])
                    cv2.putText(
                        frame,
                        f"X:{x} Y:{y}",
                        (tl[0], max(10, tl[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
        else:
            self.missing_count += 1
            if self.missing_count > self.reset_threshold:
                self.last_data = None

        return frame