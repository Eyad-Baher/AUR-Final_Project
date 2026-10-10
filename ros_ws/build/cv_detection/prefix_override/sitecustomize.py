import sys
if sys.prefix == 'C:\\ros_ws\\.pixi\\envs\\default':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = 'C:\\ros_ws\\install\\cv_detection'
