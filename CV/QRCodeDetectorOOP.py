import cv2
import numpy as np
from urllib.parse import parse_qs


class QRDecoder:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.detector = cv2.wechat_qrcode_WeChatQRCode()

        self.last_data = None
        self.reset_threshold = 30
        self.missing_count = 0

        self.show_display = True
        self.detection_interval = 3
        self.frame_count = 0
        self.preprocessed_frame = None
        self.res, self.points = [], []

    def trigger_event(self, x, y):
        ## still not done will publish to ROS 
        print(f"New event triggered at X: {x} and Y: {y}")

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

    def run_QR_decoder(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print('Video not found --- Exiting')
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            self.frame_count += 1

            if self.frame_count % self.detection_interval == 0 or self.preprocessed_frame is None:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.preprocessed_frame = self.clahe.apply(frame_gray)
                self.res, self.points = self.detector.detectAndDecode(self.preprocessed_frame)

            if self.res and self.points:
                self.missing_count = 0

                for payload, bbox in zip(self.res, self.points):
                    x, y = self.parse_QR_data(payload)

                    if x is not None and y is not None:

                        current_data = (x, y)

                        if self.last_data != current_data:
                            self.trigger_event(x, y)
                            self.last_data = current_data

                        if self.show_display:
                            pts = bbox.astype(np.int32).reshape((-1, 1, 2))
                            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

                            top_left_corner = tuple(pts[0][0])
                            cv2.putText(
                                frame,
                                f"X:{x} Y:{y}",
                                (top_left_corner[0], max(10, top_left_corner[1] - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 0),
                                2
                            )
            else:
                self.missing_count += 1
                if self.missing_count > self.reset_threshold:
                    self.last_data = None

            if self.show_display:
                cv2.imshow("Live Feed", frame)
                if cv2.waitKey(1) == 27:
                    break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    decoder = QRDecoder()
    decoder.run_QR_decoder()