# -*- coding: utf-8 -*-
"""
主菜单界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
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
        tk.Frame(self, bg=COLOR_BG, height=40).pack()
        
        # 按钮容器
        button_frame = tk.Frame(self, bg=COLOR_BG)
        button_frame.pack(pady=30)
        
        # 创建菜单按钮（2行3列布局）
        buttons = [
            ("基础任务(2) - 双参数", lambda: self.navigate(7)),
            ("基础任务(3、4) - 三参数", lambda: self.navigate(8)),
            ("发挥部分 - 系统建模", lambda: self.navigate(9)),
            ("串口调试", lambda: self.navigate(7)),
            ("RESET", self.on_reset),
            ("退出程序", self.on_exit),
        ]
        
        for i, (text, command) in enumerate(buttons):
            row = i // 3
            col = i % 3
            # 设置不同按钮的背景色
            if text in ["RESET"]:
                bg_color = '#FF9800'  # 橙色
            elif text in ["退出程序"]:
                bg_color = '#F44336'  # 红色
            else:
                bg_color = '#2196F3'  # 蓝色
            
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                width=25
            )
            btn.grid(row=row, column=col, padx=20, pady=20, sticky='nsew')
        
        # 配置按钮大小一致
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, minsize=200)
        
        # 底部状态栏
        status_frame = tk.Frame(self, bg='#E0E0E0')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="欢迎使用 SA 串口上位机",
            font=FONT_STATUS,
            bg='#E0E0E0',
            fg=COLOR_TEXT
        )
        self.status_label.pack(pady=5)
    
    def on_reset(self):
        """重置按钮"""
        self.status_label.config(text="系统重置中...", fg=COLOR_WARNING)
        # 这里可以发送clear buff命令
        self.after(1000, lambda: self.status_label.config(
            text="系统已重置", fg=COLOR_SUCCESS
        ))
    
    def on_exit(self):
        """退出程序"""
        if tk.messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.master.master.destroy()  # 关闭主窗口

