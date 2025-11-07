# -*- coding: utf-8 -*-
"""
主菜单界面
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import *


class MainMenu(tk.Frame):
    """主菜单页面"""
    
    def __init__(self, parent, navigate_callback):
        super().__init__(parent, bg=COLOR_BG)
        self.navigate = navigate_callback
        self.setup_ui()
    
    def setup_ui(self):
        """初始化UI"""
        # 顶部间距
        tk.Frame(self, bg=COLOR_BG, height=60).pack()
        
        # 按钮容器（垂直布局）
        button_frame = tk.Frame(self, bg=COLOR_BG)
        button_frame.pack(expand=True, fill=tk.BOTH, padx=80, pady=20)
        
        # 创建菜单按钮（垂直排列）
        buttons = [
            ("基础任务(2) - 双参数控制", lambda: self.navigate(7)),
            ("基础任务(3、4) - 三参数控制", lambda: self.navigate(8)),
            ("发挥部分 - 系统建模", lambda: self.navigate(9)),
            ("串口调试", lambda: self.navigate(7)),
            ("RESET", self.on_reset),
            ("退出程序", self.on_exit),
        ]
        
        # 为不同按钮设置不同的 bootstyle
        bootstyles = {
            "基础任务(2) - 双参数控制": "primary",
            "基础任务(3、4) - 三参数控制": "info",
            "发挥部分 - 系统建模": "success",
            "串口调试": "secondary",
            "RESET": "warning",
            "退出程序": "danger"
        }
        
        for text, command in buttons:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                bootstyle=bootstyles.get(text, "primary"),
                width=50
            )
            btn.pack(fill=tk.X, pady=8, ipady=12)
        
        # 底部状态栏
        status_frame = tk.Frame(self, bg='#E0E0E0')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # self.status_label = tk.Label(
        #     status_frame,
        #     text="欢迎使用 SA 串口上位机",
        #     font=FONT_STATUS,
        #     bg='#E0E0E0',
        #     fg=COLOR_TEXT
        # )
        # self.status_label.pack(pady=5)
    
    def on_reset(self):
        """重置按钮"""
        messagebox.showinfo("系统重置", "系统已重置")
    
    def on_exit(self):
        """退出程序"""
        if tk.messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.master.master.destroy()  # 关闭主窗口

