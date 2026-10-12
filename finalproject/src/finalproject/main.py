import sys
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,QGroupBox
import pygame
from PySide6.QtGui import QPixmap
from .camera_system import StreamWidget   

class RobotConsole(QWidget):
    move_signal = Signal(str,bool)
    move_gripper_signal = Signal(str,bool)
    command_signal = Signal(str)
    command_gripper_signal = Signal(str)
    status_update_signal = Signal(float, float, float, float)
    Qr_code_signal = Signal(float, float)    
    def __init__(self):
        super().__init__()
        # Initialize joystick
        pygame.init()
        pygame.joystick.init()

        self.joystick = None

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.control_mode = "keyboard"  # Default control mode

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.read_joystick)
        self.check_timer.timeout.connect(self.read_keyboard)
        self.check_timer.timeout.connect(self.read_gripper)
        self.check_timer.start(20)

        
#----------------------------------------------------------------------------- 

#-----------------------------------------------------------------------------

        self.setWindowTitle("Robot Console")
        self.resize(1000, 700)
        #movement states
        self.keys={
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "stop": False
        }
        self.gripper_keys={
            "open": False,
            "close": False,
            "up": False,
            "down": False
        }
        self.move_signal.connect(self.update_movement)
        self.move_gripper_signal.connect(self.update_movement_gripper)
        self.status_update_signal.connect(self.update_status_labels)
        self.Qr_code_signal.connect(self.update_qr_code)
#---------------------------------------------------------------------------
        # Create labels for robot status
        self.x_label = QLabel("X: 0.00 m")
        self.y_label = QLabel("Y: 0.00 m")
        self.speed_label = QLabel("Speed: 0.00 m/s")
        self.heading_label = QLabel("Heading: 0°")
        self.target_label = QLabel("QR Target: x: 0.00 m, y: 0.00 m")
#------------------------------------------------------------------------------
        # Create label for camera feed
        self.stream = StreamWidget("http://192.168.1.15:8080/video")#url of ip streaming

        self.stream.start()
#----------------------------------------------------------------------------
        # Create layout for status labels
        status_layout = QVBoxLayout()
        status_layout.addWidget(self.x_label)
        status_layout.addWidget(self.y_label)
        status_layout.addWidget(self.speed_label)
        status_layout.addWidget(self.heading_label)
        status_layout.addWidget(self.target_label)
        box_status=QGroupBox("status & target...")
        box_layout=QVBoxLayout()
        box_layout.addLayout(status_layout) 
        box_status.setLayout(box_layout)       
        box_status.setMinimumSize(200,150)
        box_status.setMaximumWidth(150)
#---------------------------------------------------------------------------
        # Set buttons for robot control
        self.forward_button = QPushButton("↑")
        self.backward_button = QPushButton("↓")
        self.left_button = QPushButton("←")
        self.right_button = QPushButton("→")
        self.stop_button = QPushButton("Stop")
#--------------------------------------------------------------------------
        #grippers
        self.gripper_open_button = QPushButton("Open")
        self.gripper_close_button = QPushButton("Close")
        self.up_gripper_button = QPushButton("Up")
        self.down_gripper_button = QPushButton("Down")
#--------------------------------------------------------------------------        
        #gripper button layout
        gripper_layout_child = QHBoxLayout()
        gripper_layout_child.addWidget(self.gripper_open_button)
        gripper_layout_child.addWidget(self.gripper_close_button)
        gripper_layout=QVBoxLayout()
        gripper_layout.addWidget(self.up_gripper_button)
        gripper_layout.addLayout(gripper_layout_child)
        gripper_layout.addWidget(self.down_gripper_button)
#--------------------------------------------------------------------------
        self.keyboard_mode_button = QPushButton("Keyboard Mode")
        self.joystick_mode_button = QPushButton("Joystick Mode")
        self.keyboard_mode_button.setCheckable(True)
        self.joystick_mode_button.setCheckable(True)

        self.keyboard_mode_button.setChecked(True)
        self.keyboard_mode_button.clicked.connect(lambda: self.set_control_mode("keyboard"))
        self.joystick_mode_button.clicked.connect(lambda: self.set_control_mode("joystick"))
#---------------------------------------------------------------------------
        self.command_signal.connect(self.test_command_receiver)
        self.command_gripper_signal.connect(self.read_gripper_input)
#----------------------------------------------------------------------------
        #forward movement
        self.forward_button.pressed.connect(
            lambda: self.move_signal.emit(
                "forward", True
            )
        )

        self.forward_button.released.connect(
            lambda: self.move_signal.emit(
                "forward", False
            )
        )
#----------------------------------------------------------------------------
        #backward movement
        self.backward_button.pressed.connect(
            lambda: self.move_signal.emit(
                "backward", True
            )
        )

        self.backward_button.released.connect(
            lambda: self.move_signal.emit(
                "backward", False
            )
        )
#---------------------------------------------------------------------------


        #left movement
        self.left_button.pressed.connect(
            lambda: self.move_signal.emit(
                "left", True
            )
        )
        self.left_button.released.connect(
            lambda: self.move_signal.emit(
                "left", False
            )
        )
#---------------------------------------------------------------------------
        #right movement
        self.right_button.pressed.connect(
            lambda: self.move_signal.emit(
                "right", True
            )
        )
        self.right_button.released.connect(
            lambda: self.move_signal.emit(
                "right", False
            )
        )
#--------------------------------------------------------------------------
        #stop movement
        self.stop_button.pressed.connect(lambda: self.move_signal.emit("stop", True))
        self.stop_button.released.connect(lambda: self.move_signal.emit("stop", False))
#---------------------------------------------------------------------------
        #gripper movement
        self.gripper_open_button.pressed.connect(lambda: self.move_gripper_signal.emit("open", True))
        self.gripper_open_button.released.connect(lambda: self.move_gripper_signal.emit("open", False))
        self.gripper_close_button.pressed.connect(lambda: self.move_gripper_signal.emit("close", True))
        self.gripper_close_button.released.connect(lambda: self.move_gripper_signal.emit("close", False))
        self.up_gripper_button.pressed.connect(lambda: self.move_gripper_signal.emit("up", True))
        self.up_gripper_button.released.connect(lambda: self.move_gripper_signal.emit("up", False))
        self.down_gripper_button.pressed.connect(lambda: self.move_gripper_signal.emit("down", True))
        self.down_gripper_button.released.connect(lambda: self.move_gripper_signal.emit("down", False))        
#---------------------------------------------------------------------------        
        # Create layout for control buttons
        control_row = QHBoxLayout()
        control_row.addWidget(self.left_button)
        control_row.addWidget(self.stop_button)
        control_row.addWidget(self.right_button)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.forward_button)
        control_layout.addLayout(control_row)
        control_layout.addWidget(self.backward_button)
    


        mode_label = QLabel("Control Mode:")
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.keyboard_mode_button)
        mode_layout.addWidget(self.joystick_mode_button)
#---------------------------------------------------------------------------

        self.setFocusPolicy(Qt.StrongFocus)
        all_control_layout = QHBoxLayout()
        all_control_layout.addLayout(control_layout)
        all_control_layout.addLayout(gripper_layout)
        box_control=QGroupBox("controls")
        box_control.setLayout(all_control_layout)
        box_control.setMaximumHeight(200)
        robot_status_control=QHBoxLayout()
        robot_status_control.addWidget(box_status)
        robot_status_control.addWidget(box_control)
        main_layout = QVBoxLayout(self)
        left_layout = QVBoxLayout()
        left_layout.addLayout(mode_layout)
        left_layout.addLayout(robot_status_control)
        main_layout.addWidget(self.stream)
        main_layout.addLayout(left_layout)
        
#---------------------------------------------------------------------------
    def set_control_mode(self, mode):

        # Stop current movement first

        self.control_mode = mode

        if mode == "keyboard":

            self.keyboard_mode_button.setChecked(True)
            self.joystick_mode_button.setChecked(False)

        elif mode == "joystick":

            self.keyboard_mode_button.setChecked(False)
            self.joystick_mode_button.setChecked(True)


    def update_movement(self, direction, state):
        if direction not in self.keys:
            return
        self.keys[direction] = state
        self.update_button_visual(direction, state)

        commands = []
        if self.keys["forward"]:
            commands.append("FORWARD")
        if self.keys["backward"]:
            commands.append("BACKWARD")
        if self.keys["left"]:
            commands.append("LEFT")
        if self.keys["right"]:
            commands.append("RIGHT")
        if self.keys["stop"]:
            commands.append("STOP")
        if commands:
            self.command_signal.emit("+".join(commands))

    def update_movement_gripper(self, direction, state):
        if direction not in self.gripper_keys:
            return
        self.gripper_keys[direction] = state
        self.update_button_visual(direction, state)

        commands = []
        if self.gripper_keys["open"]:
            commands.append("OPEN")
        if self.gripper_keys["close"]:
            commands.append("CLOSE")
        if self.gripper_keys["up"]:
            commands.append("UP")
        if self.gripper_keys["down"]:
            commands.append("DOWN")
        if commands:
            self.command_gripper_signal.emit("+".join(commands))

    #keyboard events
    def keyPressEvent(self, event):
        if self.control_mode != "keyboard":
            return
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key_Up:
            self.keys["forward"] = True
        elif event.key() == Qt.Key_Down:

            self.keys["backward"] = True
        elif event.key() == Qt.Key_Left:

            self.keys["left"] = True
        elif event.key() == Qt.Key_Right:

            self.keys["right"] = True
        elif event.key() == Qt.Key_Space:
            self.keys["stop"] = True
        elif event.key() == Qt.Key_Q:
            self.gripper_keys["open"] = True
        elif event.key() == Qt.Key_E:
            self.gripper_keys["close"] = True
        elif event.key() == Qt.Key_W:
            self.gripper_keys["up"] = True
        elif event.key() == Qt.Key_S:
            self.gripper_keys["down"] = True

    def keyReleaseEvent(self, event):
        if self.control_mode != "keyboard":
            return
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key_Up:
            self.keys["forward"] = False
        elif event.key() == Qt.Key_Down:
            self.keys["backward"] = False
        elif event.key() == Qt.Key_Left:
            self.keys["left"] = False
        elif event.key() == Qt.Key_Right:
            self.keys["right"] = False
        elif event.key() == Qt.Key_Space:
            self.keys["stop"] = False
        elif event.key() == Qt.Key_Q:
            self.gripper_keys["open"] = False
        elif event.key() == Qt.Key_E:
            self.gripper_keys["close"] = False
        elif event.key() == Qt.Key_W:
            self.gripper_keys["up"] = False
        elif event.key() == Qt.Key_S:
            self.gripper_keys["down"] = False

    def read_keyboard(self):
        if self.control_mode != "keyboard":
            return
        if self.keys["forward"]:
            self.move_signal.emit("forward", True)
        else:
            self.move_signal.emit("forward", False)
        if self.keys["backward"]:
            self.move_signal.emit("backward", True)
        else:
            self.move_signal.emit("backward", False)
        if self.keys["left"]:
            self.move_signal.emit("left",True)
        else:
            self.move_signal.emit("left",False)
        if self.keys["right"]:
            self.move_signal.emit("right",True)
        else:
            self.move_signal.emit("right",False)

    def read_gripper(self):
        if self.control_mode != "keyboard":
            return
        if self.gripper_keys["open"]:
            self.move_gripper_signal.emit("open", True)
        else:
            self.move_gripper_signal.emit("open", False)
        if self.gripper_keys["close"]:
            self.move_gripper_signal.emit("close", True)
        else:
            self.move_gripper_signal.emit("close", False)
        if self.gripper_keys["up"]:
            self.move_gripper_signal.emit("up", True)
        else:
            self.move_gripper_signal.emit("up", False)
        if self.gripper_keys["down"]:
            self.move_gripper_signal.emit("down", True)
        else:
            self.move_gripper_signal.emit("down", False)

    def read_joystick(self):

        if self.joystick is None:
            return
        if self.control_mode != "joystick":
            return
        pygame.event.pump()

        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)
        y_2 = self.joystick.get_axis(3)
        deadzone = 0.2

        # Forward / Backward
        if y < -deadzone:
            self.move_signal.emit("forward", True)

        elif y > deadzone:
            self.move_signal.emit("backward", True)

        else:
            self.move_signal.emit("forward", False)
            self.move_signal.emit("backward", False)

        # Left / Right
        if x < -deadzone:
            self.move_signal.emit("left", True)

        elif x > deadzone:
            self.move_signal.emit("right", True)

        else:
            self.move_signal.emit("left", False)
            self.move_signal.emit("right", False)
        if self.joystick.get_button(0):  
            self.move_signal.emit("stop", True)
        else:
            self.move_signal.emit("stop", False)
        
        if y_2 < -deadzone:
                self.move_gripper_signal.emit("up", True)
        
        elif y_2 > deadzone:
                self.move_gripper_signal.emit("down", True)
        
        else:
            self.move_gripper_signal.emit("up", False)
            self.move_gripper_signal.emit("down", False)
        if self.joystick.get_button(9):
            self.move_gripper_signal.emit("open", True)
        else:
            self.move_gripper_signal.emit("open", False)
        if self.joystick.get_button(10):
            self.move_gripper_signal.emit("close", True)
        else:
            self.move_gripper_signal.emit("close", False)
    def update_button_visual(self, direction, state):
        if direction == "forward":
            self.forward_button.setDown(state)
        elif direction == "backward":
            self.backward_button.setDown(state)
        elif direction == "left":
            self.left_button.setDown(state)
        elif direction == "right":
            self.right_button.setDown(state)
        elif direction == "stop":
            self.stop_button.setDown(state)
        elif direction == "open":
            self.gripper_open_button.setDown(state)
        elif direction == "close":
            self.gripper_close_button.setDown(state)
        elif direction == "up":
            self.up_gripper_button.setDown(state)
        elif direction == "down":
            self.down_gripper_button.setDown(state)

    def update_status_labels(self, x, y, speed, heading):
        self.x_label.setText(f"X: {x:.2f} m")
        self.y_label.setText(f"Y: {y:.2f} m")
        self.speed_label.setText(f"Speed: {speed:.2f} m/s")
        self.heading_label.setText(f"Heading: {heading:.0f}°")
    
    def update_qr_code(self, x, y):
        self.target_label.setText(f"QR Code: x: {x:.2f} m, y: {y:.2f} m")

    def test_command_receiver(self, command):
        print("Command received:", command)
    def read_gripper_input(self,command):
        print("Gripper Command received:", command)

    def closeEvent(self, event):
            self.stream.stop()
            event.accept()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = RobotConsole()
    window.show()
    window.Qr_code_signal.emit(10,15)
    window.status_update_signal.emit(0.2,0.5,90,910)
    window.setFocus()
    sys.exit(app.exec())
    