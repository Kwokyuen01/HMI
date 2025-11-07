# -*- coding: utf-8 -*-
"""
Page 0 - 主菜单界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import *


class MainMenu(tk.Frame):
    """主菜单页面"""
    
    def __init__(self, parent, navigate_callback):
        super().__init__(parent, bg=COLOR_BG)
        self.navigate = navigate_callback
        self.rotation_angle = 0
        self.setup_ui()
        # 启动旋转动画
        self.start_rotation_animation()
    
    def setup_ui(self):
        """初始化UI"""
        # 标题
        title = tk.Label(
            self, 
            text="SA 系统控制平台",
            font=('Arial', 24, 'bold'),
            bg=COLOR_BG,
            fg='#2196F3'
        )
        title.pack(pady=40)
        
        # 旋转动画标签（模拟原HMI的z0旋转）
        self.rotation_label = tk.Label(
            self,
            text="⚙",
            font=('Arial', 48),
            bg=COLOR_BG,
            fg='#9E9E9E'
        )
        self.rotation_label.pack(pady=20)
        
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
            
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Arial', 11, 'bold'),
                width=18,
                height=3,
                bg=bg_color,
                fg='white',
                activebackground=bg_color,
                activeforeground='white',
                command=command,
                relief=tk.RAISED,
                bd=3,
                cursor='hand2'
            )
            btn.grid(row=row, column=col, padx=15, pady=15)
        
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
    
    def start_rotation_animation(self):
        """启动旋转动画（模拟原HMI的z0.val自增）"""
        self.rotation_angle += 5
        if self.rotation_angle >= 360:
            self.rotation_angle = 0
        elif self.rotation_angle == 215:
            self.rotation_angle = 330  # 原HMI逻辑
        
        # 更新旋转效果（通过改变字符模拟）
        symbols = ['⚙', '◎', '◉', '●', '◉', '◎']
        symbol_idx = (self.rotation_angle // 60) % len(symbols)
        self.rotation_label.config(text=symbols[symbol_idx])
        
        # 每100ms更新一次
        self.after(100, self.start_rotation_animation)
    
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

