# -*- coding: utf-8 -*-
"""
HMI上位机配置文件
"""

# 串口配置
SERIAL_PORT = 'COM3'  # Windows: 'COM3', Linux/Mac: '/dev/ttyUSB0'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1.0

# 窗口配置
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650
WINDOW_TITLE = "串口上位机"

# 颜色配置（基于RGB565转换）
COLOR_DEFAULT = '#C0C0C0'    # 50712 -> 灰色（默认按钮）
COLOR_ACTIVE = '#808480'     # 33808 -> 橙/红色（激活按钮）
COLOR_BG = '#F0F0F0'         # 背景色
COLOR_TEXT = '#000000'       # 文本颜色
COLOR_BUTTON = '#4CAF50'     # 通用按钮颜色
COLOR_STOP = '#F44336'       # 停止按钮颜色
COLOR_SUCCESS = '#4CAF50'    # 成功/运行中颜色
COLOR_WARNING = '#FF9800'    # 警告颜色

# 字体配置
FONT_TITLE = ('Arial', 16, 'bold')
FONT_LABEL = ('Arial', 12)
FONT_BUTTON = ('Arial', 11)
FONT_STATUS = ('Arial', 10)

# 默认值
DEFAULT_FREQ = 1000
DEFAULT_VOLTAGE = 1.0

