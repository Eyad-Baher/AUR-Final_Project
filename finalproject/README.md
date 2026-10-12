# Robot Console

A graphical interface for controlling a robot and monitoring its status, built with **PySide6**. It displays the camera stream and robot data, and supports control through on-screen buttons, the keyboard, or a joystick.

## Features

- Displays the camera feed using `StreamWidget`.
- Shows the robot’s `X` and `Y` position, speed, heading, and QR target coordinates.
- Controls robot movement: forward, backward, left, right, and stop.
- Controls the gripper: open, close, raise, and lower.
- Switches between keyboard and joystick control modes.
- Uses PySide6 signals to send commands and update status information for gripper and movement.

## Interface

- **Camera feed:** Displayed at the top of the window. The current stream URL is `http://192.168.1.15:8080/video` change it with your url.
- **Status and target:** Shows position, speed, heading, and QR target coordinates.
- **Control buttons:** Control robot movement and the gripper.
- **Control mode:** Switches between keyboard and joystick input.

## Keyboard Controls

The application window must be focused to receive keyboard input.

| Key | Action |
|---|---|
| `↑` | Move forward |
| `↓` | Move backward |
| `←` | Move left |
| `→` | Move right |
| `Space` | Stop |
| `Q` | Open the gripper |
| `E` | Close the gripper |
| `W` | Raise the gripper |
| `S` | Lower the gripper |

## Joystick Controls

If a joystick is connected when the application starts, the program uses the first available device.

| Input | Action |
|---|---|
| Axis `0` | Move left and right |
| Axis `1` | Move forward and backward |
| Axis `3` | Raise and lower the gripper |
| Button `0` | Stop |
| Button `9` | Open the gripper |
| Button `10` | Close the gripper |

A dead zone of `0.2` filters out small joystick movements. The application reads joystick input every 20 milliseconds using a `QTimer`.

## Signals and Commands

User input is converted into text commands and sent through PySide6 signals:

- `command_signal`: Robot movement commands, such as `FORWARD` and `LEFT`.
- `command_gripper_signal`: Gripper commands, such as `OPEN` and `UP`.
- `status_update_signal`: Updates the robot status data.
- `Qr_code_signal`: Updates the QR target coordinates.

In the current version, `test_command_receiver` and `read_gripper_input` only print commands to the terminal. To control the robot hardware, connect these signals to the communication and control system used by your project.

## Requirements

- Python
- PySide6
- pygame
- The `camera_system` module containing `StreamWidget`
- An available camera stream at the configured URL

## Configure the Camera URL

Update the stream URL in `RobotConsole` to match your camera:

```python
self.stream = StreamWidget("http://192.168.1.15:8080/video")