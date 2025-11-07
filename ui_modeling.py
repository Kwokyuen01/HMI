# -*- coding: utf-8 -*-
"""
系统建模控制页面
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import *


class SystemModeling(tk.Frame):
    """系统建模页面"""
    
    def __init__(self, parent, serial_comm, navigate_callback):
        super().__init__(parent, bg=COLOR_BG)
        self.serial = serial_comm
        self.navigate = navigate_callback
        
        # 按钮状态（通过颜色值判断）
        self.b9_active = False  # 建模按钮状态
        self.b0_active = False  # 启动按钮状态
        
        self.setup_ui()
        self.setup_serial_callback()
    
    def setup_ui(self):
        """初始化UI"""
        # 顶部标题
        title_frame = tk.Frame(self, bg='#3F51B5', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        self.title_label = tk.Label(
            title_frame,
            text="未知电路模型建模：待机中..",
            font=('Arial', 18, 'bold'),
            bg='#3F51B5',
            fg='white'
        )
        self.title_label.pack(pady=15)
        
        # 主控制区域
        main_frame = tk.Frame(self, bg=COLOR_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # === 第一部分：一键学习 ===
        section1_frame = tk.Frame(main_frame, bg=COLOR_BG)
        section1_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            section1_frame,
            text="第一部分：系统识别",
            font=('Arial', 14, 'bold'),
            bg=COLOR_BG,
            fg='#3F51B5'
        ).pack(pady=10)
        
        self.b9_modeling_btn = ttk.Button(
            section1_frame,
            text="一键学习（启动建模）",
            command=self.toggle_modeling,
            width=40
        )
        self.b9_modeling_btn.pack(pady=10, ipady=10)
        
        # 建模结果显示区
        self.result_frame = tk.Frame(
            section1_frame,
            bg='#000000',
            bd=2,
            relief=tk.SUNKEN
        )
        self.result_frame.pack(fill=tk.X, pady=10)
        self.result_frame.pack_forget()  # 初始隐藏
        
        self.result_label = tk.Label(
            self.result_frame,
            text="系统建模中... 请等待...",
            font=('Arial', 12),
            bg='#000000',
            fg='#00FF00',
            pady=15
        )
        self.result_label.pack()
        
        # 分隔线
        tk.Frame(main_frame, bg='#BDBDBD', height=2).pack(fill=tk.X, pady=30)
        
        # === 第二部分：启动探究装置 ===
        section2_frame = tk.Frame(main_frame, bg=COLOR_BG)
        section2_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            section2_frame,
            text="第二部分：实时分析",
            font=('Arial', 14, 'bold'),
            bg=COLOR_BG,
            fg='#3F51B5'
        ).pack(pady=10)
        
        self.start_status_label = tk.Label(
            section2_frame,
            text="启动状态：未启动",
            font=FONT_LABEL,
            bg=COLOR_BG,
            fg='#757575'
        )
        self.start_status_label.pack(pady=5)
        
        self.b0_start_btn = ttk.Button(
            section2_frame,
            text="启动探究装置",
            command=self.toggle_start,
            width=40
        )
        self.b0_start_btn.pack(pady=10, ipady=10)
        
        # 底部返回按钮
        bottom_frame = tk.Frame(self, bg=COLOR_BG)
        bottom_frame.pack(fill=tk.X, padx=40, pady=20)
        
        ttk.Button(
            bottom_frame,
            text="返回主菜单",
            command=self.on_return,
            width=20
        ).pack(side=tk.RIGHT)
    
    def setup_serial_callback(self):
        """设置串口接收回调"""
        if self.serial:
            self.serial.set_receive_callback(self.on_serial_receive)
    
    def on_serial_receive(self, obj_attr, value):
        """串口接收回调"""
        if obj_attr == 'result.txt':
            # 显示滤波器类型识别结果
            self.result_label.config(text=value, fg='#00FF00')
            print(f"← 接收建模结果: {value}")
    
    def toggle_modeling(self):
        """切换建模状态"""
        if not self.b9_active:
            # 启动建模
            self.b9_active = True
            self.b9_modeling_btn.config(text="停止建模")
            self.title_label.config(text="未知电路模型建模：运行中..")
            self.result_frame.pack(fill=tk.X, pady=10)  # 显示结果区
            self.result_label.config(text="系统建模中... 请等待...", fg='#FFFF00')
            
            # 发送建模命令
            if self.serial and self.serial.is_connected:
                self.serial.send_modeling_cmd()
            else:
                messagebox.showwarning("警告", "串口未连接")
        else:
            # 停止建模
            self.b9_active = False
            self.b9_modeling_btn.config(text="一键学习（启动建模）")
            self.title_label.config(text="未知电路模型建模：待机中..")
            self.result_frame.pack_forget()  # 隐藏结果区
            
            # 发送停止命令（相同命令，由下位机判断）
            if self.serial and self.serial.is_connected:
                self.serial.send_modeling_cmd()
    
    def toggle_start(self):
        """切换启动状态"""
        if not self.b0_active:
            # 启动装置
            self.b0_active = True
            self.b0_start_btn.config(text="停止探究装置")
            self.start_status_label.config(
                text="启动状态：已启动",
                fg=COLOR_SUCCESS
            )
            
            # 发送启动命令
            if self.serial and self.serial.is_connected:
                self.serial.send_start_cmd()
                messagebox.showinfo(
                    "提示",
                    "探究装置已启动\n下位机将执行：\n- FFT频谱分析\n- 峰值检测\n- 多频合成\n- LCD实时显示"
                )
            else:
                messagebox.showwarning("警告", "串口未连接")
        else:
            # 停止装置
            self.b0_active = False
            self.b0_start_btn.config(text="启动探究装置")
            self.start_status_label.config(
                text="启动状态：未启动",
                fg='#757575'
            )
            
            # 发送停止命令
            if self.serial and self.serial.is_connected:
                self.serial.send_start_cmd()
    
    def on_return(self):
        """返回主菜单"""
        # 停止所有运行中的任务
        if self.b9_active:
            self.toggle_modeling()
        if self.b0_active:
            self.toggle_start()
        
        self.navigate(0)

