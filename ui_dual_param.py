# -*- coding: utf-8 -*-
"""
双参数控制页面（频率+幅值）
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import *


class DualParamControl(tk.Frame):
    """双参数控制页面"""
    
    def __init__(self, parent, serial_comm, navigate_callback):
        super().__init__(parent, bg=COLOR_BG)
        self.serial = serial_comm
        self.navigate = navigate_callback
        
        # 状态变量
        self.state1 = tk.IntVar(value=1)  # 0=停止, 1=运行
        self.fs = tk.IntVar(value=1000)    # 频率设置值
        self.vs = tk.DoubleVar(value=1.0)  # 幅值设置值
        self.f0_text = tk.StringVar(value="1000 Hz")  # 当前频率显示
        self.v0_text = tk.StringVar(value="1.00 V")   # 当前幅值显示
        
        self.setup_ui()
        self.setup_serial_callback()
    
    def setup_ui(self):
        """初始化UI"""
        # 顶部状态栏
        status_frame = tk.Frame(self, bg='#2196F3', height=50)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="串口通讯：运行中..",
            font=FONT_TITLE,
            bg='#2196F3',
            fg='white'
        )
        self.status_label.pack(pady=10)
        
        # 主控制区域
        main_frame = tk.Frame(self, bg=COLOR_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === 频率控制 ===
        freq_frame = tk.LabelFrame(
            main_frame,
            text="频率控制",
            font=FONT_LABEL,
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            bd=2,
            relief=tk.GROOVE
        )
        freq_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # 当前频率显示
        tk.Label(freq_frame, text="当前频率:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Label(
            freq_frame,
            textvariable=self.f0_text,
            font=('Arial', 14, 'bold'),
            bg='#FFF3E0',
            fg='#E65100',
            width=15,
            relief=tk.SUNKEN
        ).pack(pady=5)
        
        # 频率设置
        tk.Label(freq_frame, text="频率设置:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        freq_entry = tk.Entry(
            freq_frame,
            textvariable=self.fs,
            font=FONT_LABEL,
            width=15,
            justify=tk.CENTER
        )
        freq_entry.pack(pady=5)
        
        # 频率按钮
        freq_btn_frame = tk.Frame(freq_frame, bg=COLOR_BG)
        freq_btn_frame.pack(pady=10)
        
        ttk.Button(
            freq_btn_frame,
            text="+100",
            command=lambda: self.increment_value(self.fs, 100),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            freq_btn_frame,
            text="应用",
            command=self.apply_freq,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # === 幅值控制 ===
        amp_frame = tk.LabelFrame(
            main_frame,
            text="幅值控制",
            font=FONT_LABEL,
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            bd=2,
            relief=tk.GROOVE
        )
        amp_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        # 当前幅值显示
        tk.Label(amp_frame, text="当前幅值:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Label(
            amp_frame,
            textvariable=self.v0_text,
            font=('Arial', 14, 'bold'),
            bg='#E8F5E9',
            fg='#2E7D32',
            width=15,
            relief=tk.SUNKEN
        ).pack(pady=5)
        
        # 幅值设置
        tk.Label(amp_frame, text="幅值设置:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        amp_entry = tk.Entry(
            amp_frame,
            textvariable=self.vs,
            font=FONT_LABEL,
            width=15,
            justify=tk.CENTER
        )
        amp_entry.pack(pady=5)
        
        # 幅值按钮
        amp_btn_frame = tk.Frame(amp_frame, bg=COLOR_BG)
        amp_btn_frame.pack(pady=10)
        
        ttk.Button(
            amp_btn_frame,
            text="+0.5",
            command=lambda: self.increment_value(self.vs, 0.5),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            amp_btn_frame,
            text="应用",
            command=self.apply_amp,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # 底部控制按钮
        bottom_frame = tk.Frame(self, bg=COLOR_BG)
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_stop_btn = ttk.Button(
            bottom_frame,
            text="停止",
            command=self.toggle_state,
            width=15
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            bottom_frame,
            text="Clear Buff",
            command=self.clear_buff,
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            bottom_frame,
            text="返回",
            command=lambda: self.navigate(0),
            width=15
        ).pack(side=tk.RIGHT, padx=10)
    
    def setup_serial_callback(self):
        """设置串口接收回调"""
        if self.serial:
            self.serial.set_receive_callback(self.on_serial_receive)
    
    def on_serial_receive(self, obj_attr, value):
        """串口接收回调"""
        # 更新显示值
        if obj_attr == 'f0.txt':
            self.f0_text.set(value)
            print(f"← 接收频率反馈: {value}")
        elif obj_attr == 'v0.txt':
            self.v0_text.set(value)
            print(f"← 接收幅值反馈: {value}")
    
    def increment_value(self, var, increment):
        """增加变量值"""
        if self.state1.get() == 1:
            current = var.get()
            var.set(current + increment)
    
    def apply_freq(self):
        """应用频率设置"""
        if self.state1.get() == 1:
            freq = self.fs.get()
            if self.serial and self.serial.is_connected:
                self.serial.send_freq_cmd(freq, mode=2)
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def apply_amp(self):
        """应用幅值设置"""
        if self.state1.get() == 1:
            amp = self.vs.get()
            if self.serial and self.serial.is_connected:
                self.serial.send_voltage_cmd(amp, cmd_type='amp')
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def clear_buff(self):
        """清空缓冲"""
        if self.state1.get() == 1:
            if self.serial and self.serial.is_connected:
                self.serial.send_clear_buff()
                # 下位机会反馈默认值，自动更新显示
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def toggle_state(self):
        """切换启动/停止状态"""
        if self.state1.get() == 1:
            # 当前运行 -> 停止
            self.state1.set(0)
            self.start_stop_btn.config(text="启动")
            self.status_label.config(text="串口通讯：待机中..")
            # 发送clear buff
            if self.serial and self.serial.is_connected:
                self.serial.send_clear_buff()
        else:
            # 当前停止 -> 运行
            self.state1.set(1)
            self.start_stop_btn.config(text="停止")
            self.status_label.config(text="串口通讯：运行中..")

