import cv2
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

from .qr_detector_oop import QRDecoder


class CVNode(Node):

    def __init__(self):
        super().__init__('cv_node')

        self.qr_publisher = self.create_publisher(PoseStamped, '/qr/destination', 10)

        self.qr_detector = QRDecoder()
        self.qr_detector.callback = self.publish_qr

        self.cap = cv2.VideoCapture("http://192.168.1.11:8080/video")
        if not self.cap.isOpened():
            self.get_logger().error('Camera could not be opened')

        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        self.qr_detector.process_frame(frame, draw=False)

    def publish_qr(self, x, y):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        msg.pose.position.x = x
        msg.pose.position.y = y
        self.qr_publisher.publish(msg)
        self.get_logger().info(f'QR destination: X={x}, Y={y}')

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CVNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()