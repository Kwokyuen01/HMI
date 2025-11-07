# -*- coding: utf-8 -*-
"""
三参数控制页面（频率+幅值+峰值）
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import *


class TripleParamControl(tk.Frame):
    """三参数控制页面"""
    
    def __init__(self, parent, serial_comm, navigate_callback):
        super().__init__(parent, bg=COLOR_BG)
        self.serial = serial_comm
        self.navigate = navigate_callback
        
        # 状态变量
        self.state1 = tk.IntVar(value=1)
        self.fs = tk.IntVar(value=1000)
        self.vs = tk.DoubleVar(value=1.0)
        self.vps = tk.DoubleVar(value=1.0)  # 峰值设置
        self.f0_text = tk.StringVar(value="1000 Hz")
        self.v0_text = tk.StringVar(value="1.00 V")
        self.vp0_text = tk.StringVar(value="1.00 V")  # 峰值显示
        
        self.setup_ui()
        self.setup_serial_callback()
    
    def setup_ui(self):
        """初始化UI"""
        # 顶部状态栏
        status_frame = tk.Frame(self, bg='#673AB7', height=50)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="串口通讯：运行中.. (三参数模式)",
            font=FONT_TITLE,
            bg='#673AB7',
            fg='white'
        )
        self.status_label.pack(pady=10)
        
        # 主控制区域（3列布局）
        main_frame = tk.Frame(self, bg=COLOR_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === 频率控制 ===
        freq_frame = tk.LabelFrame(
            main_frame,
            text="频率控制",
            font=FONT_LABEL,
            bg=COLOR_BG,
            bd=2,
            relief=tk.GROOVE
        )
        freq_frame.grid(row=0, column=0, padx=5, pady=10, sticky='nsew')
        
        tk.Label(freq_frame, text="当前频率:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Label(
            freq_frame,
            textvariable=self.f0_text,
            font=('Arial', 12, 'bold'),
            bg='#FFF3E0',
            fg='#E65100',
            width=12,
            relief=tk.SUNKEN
        ).pack(pady=5)
        
        tk.Label(freq_frame, text="设置:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Entry(
            freq_frame,
            textvariable=self.fs,
            font=FONT_LABEL,
            width=12,
            justify=tk.CENTER
        ).pack(pady=5)
        
        ttk.Button(
            freq_frame,
            text="+100",
            command=lambda: self.increment_value(self.fs, 100),
            bootstyle="info-outline",
            width=10
        ).pack(pady=3)
        
        ttk.Button(
            freq_frame,
            text="应用",
            command=self.apply_freq,
            bootstyle="success",
            width=10
        ).pack(pady=3)
        
        # === 幅值控制 ===
        amp_frame = tk.LabelFrame(
            main_frame,
            text="幅值控制",
            font=FONT_LABEL,
            bg=COLOR_BG,
            bd=2,
            relief=tk.GROOVE
        )
        amp_frame.grid(row=0, column=1, padx=5, pady=10, sticky='nsew')
        
        tk.Label(amp_frame, text="当前幅值:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Label(
            amp_frame,
            textvariable=self.v0_text,
            font=('Arial', 12, 'bold'),
            bg='#E8F5E9',
            fg='#2E7D32',
            width=12,
            relief=tk.SUNKEN
        ).pack(pady=5)
        
        tk.Label(amp_frame, text="设置:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Entry(
            amp_frame,
            textvariable=self.vs,
            font=FONT_LABEL,
            width=12,
            justify=tk.CENTER
        ).pack(pady=5)
        
        ttk.Button(
            amp_frame,
            text="+0.5",
            command=lambda: self.increment_value(self.vs, 0.5),
            bootstyle="info-outline",
            width=10
        ).pack(pady=3)
        
        ttk.Button(
            amp_frame,
            text="应用",
            command=self.apply_amp,
            bootstyle="success",
            width=10
        ).pack(pady=3)
        
        # === 峰值控制 ===
        peak_frame = tk.LabelFrame(
            main_frame,
            text="峰值控制",
            font=FONT_LABEL,
            bg=COLOR_BG,
            bd=2,
            relief=tk.GROOVE
        )
        peak_frame.grid(row=0, column=2, padx=5, pady=10, sticky='nsew')
        
        tk.Label(peak_frame, text="当前峰值:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Label(
            peak_frame,
            textvariable=self.vp0_text,
            font=('Arial', 12, 'bold'),
            bg='#FCE4EC',
            fg='#C2185B',
            width=12,
            relief=tk.SUNKEN
        ).pack(pady=5)
        
        tk.Label(peak_frame, text="设置:", font=FONT_LABEL, bg=COLOR_BG).pack(pady=5)
        tk.Entry(
            peak_frame,
            textvariable=self.vps,
            font=FONT_LABEL,
            width=12,
            justify=tk.CENTER
        ).pack(pady=5)
        
        ttk.Button(
            peak_frame,
            text="+0.5",
            command=lambda: self.increment_value(self.vps, 0.5),
            bootstyle="info-outline",
            width=10
        ).pack(pady=3)
        
        ttk.Button(
            peak_frame,
            text="应用",
            command=self.apply_peak,
            bootstyle="success",
            width=10
        ).pack(pady=3)
        
        # 配置grid权重
        for i in range(3):
            main_frame.grid_columnconfigure(i, weight=1)
        
        # 底部控制按钮
        bottom_frame = tk.Frame(self, bg=COLOR_BG)
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_stop_btn = ttk.Button(
            bottom_frame,
            text="停止",
            command=self.toggle_state,
            bootstyle="danger",
            width=15
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            bottom_frame,
            text="Clear Buff",
            command=self.clear_buff,
            bootstyle="warning",
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        self.receive_status = ttk.Label(
            bottom_frame,
            text="清空缓冲待机中...",
            font=FONT_STATUS
        )
        self.receive_status.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(
            bottom_frame,
            text="返回",
            command=lambda: self.navigate(0),
            bootstyle="secondary",
            width=15
        ).pack(side=tk.RIGHT, padx=10)
    
    def setup_serial_callback(self):
        """设置串口接收回调"""
        if self.serial:
            self.serial.set_receive_callback(self.on_serial_receive)
    
    def on_serial_receive(self, obj_attr, value):
        """串口接收回调"""
        if obj_attr == 'f0.txt':
            self.f0_text.set(value)
        elif obj_attr == 'v0.txt':
            self.v0_text.set(value)
        elif obj_attr == 'vp0.txt':
            self.vp0_text.set(value)
            self.receive_status.config(text="清空缓冲接收完成", fg=COLOR_SUCCESS)
    
    def increment_value(self, var, increment):
        """增加变量值"""
        if self.state1.get() == 1:
            current = var.get()
            var.set(current + increment)
    
    def apply_freq(self):
        """应用频率设置"""
        if self.state1.get() == 1:
            if self.serial and self.serial.is_connected:
                self.serial.send_freq_cmd(self.fs.get(), mode=2)
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def apply_amp(self):
        """应用幅值设置"""
        if self.state1.get() == 1:
            if self.serial and self.serial.is_connected:
                self.serial.send_voltage_cmd(self.vs.get(), cmd_type='amp')
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def apply_peak(self):
        """应用峰值设置"""
        if self.state1.get() == 1:
            if self.serial and self.serial.is_connected:
                self.serial.send_voltage_cmd(self.vps.get(), cmd_type='peak')
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def clear_buff(self):
        """清空缓冲"""
        if self.state1.get() == 1:
            if self.serial and self.serial.is_connected:
                self.receive_status.config(text="清空缓冲接收等待中...", fg=COLOR_WARNING)
                self.serial.send_clear_buff()
            else:
                messagebox.showwarning("警告", "串口未连接")
    
    def toggle_state(self):
        """切换启动/停止状态"""
        if self.state1.get() == 1:
            self.state1.set(0)
            self.start_stop_btn.config(text="启动", bootstyle="success")
            self.status_label.config(text="串口通讯：待机中.. (三参数模式)")
            if self.serial and self.serial.is_connected:
                self.serial.send_clear_buff()
        else:
            self.state1.set(1)
            self.start_stop_btn.config(text="停止", bootstyle="danger")
            self.status_label.config(text="串口通讯：运行中.. (三参数模式)")

