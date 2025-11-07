# -*- coding: utf-8 -*-
"""
SA 串口上位机主程序
基于HMI设计文档的Python实现
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys

from config import *
from serial_comm import SerialComm
from ui_main_menu import MainMenu
from ui_dual_param import DualParamControl
from ui_triple_param import TripleParamControl
from ui_modeling import SystemModeling


class HMIApplication:
    """HMI主应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # 串口通信对象
        self.serial_comm: SerialComm = None
        
        # 页面容器
        self.pages = {}
        self.current_page = None
        
        # 初始化UI
        self.setup_menu()
        self.setup_container()
        self.show_connection_dialog()
        
    def setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="重新连接串口", command=self.reconnect_serial)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        
        # 页面菜单
        page_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="页面", menu=page_menu)
        page_menu.add_command(label="主菜单 (Page 0)", command=lambda: self.navigate(0))
        page_menu.add_command(label="双参数控制 (Page 7)", command=lambda: self.navigate(7))
        page_menu.add_command(label="三参数控制 (Page 8)", command=lambda: self.navigate(8))
        page_menu.add_command(label="系统建模 (Page 9)", command=lambda: self.navigate(9))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="协议说明", command=self.show_protocol_info)
        
    def setup_container(self):
        """设置页面容器"""
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # 创建所有页面（延迟到串口连接后）
        # 这样可以确保串口对象已经初始化
        pass
    
    def show_connection_dialog(self):
        """显示串口连接对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("串口连接设置")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        tk.Label(
            frame,
            text="串口连接配置",
            font=('Arial', 14, 'bold'),
            fg='#2196F3'
        ).pack(pady=10)
        
        # 串口设置
        settings_frame = tk.Frame(frame)
        settings_frame.pack(pady=10)
        
        tk.Label(settings_frame, text="串口号:", font=FONT_LABEL).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        port_var = tk.StringVar(value=SERIAL_PORT)
        port_entry = tk.Entry(settings_frame, textvariable=port_var, font=FONT_LABEL, width=15)
        port_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(settings_frame, text="波特率:", font=FONT_LABEL).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        baud_var = tk.IntVar(value=SERIAL_BAUDRATE)
        baud_combo = ttk.Combobox(
            settings_frame,
            textvariable=baud_var,
            values=[9600, 19200, 38400, 57600, 115200, 230400],
            font=FONT_LABEL,
            width=13,
            state='readonly'
        )
        baud_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # 提示信息
        tip_label = tk.Label(
            frame,
            text="提示：Linux/Mac使用 /dev/ttyUSB0\nWindows使用 COM3",
            font=FONT_STATUS,
            fg='#757575',
            justify=tk.LEFT
        )
        tip_label.pack(pady=5)
        
        # 按钮
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=15)
        
        def on_connect():
            port = port_var.get()
            baud = baud_var.get()
            
            if not port:
                messagebox.showerror("错误", "请输入串口号")
                return
            
            # 创建串口对象并连接
            self.serial_comm = SerialComm(port, baud, SERIAL_TIMEOUT)
            if self.serial_comm.connect():
                messagebox.showinfo("成功", f"串口连接成功\n{port} @ {baud}bps")
                dialog.destroy()
                self.create_pages()
                self.navigate(0)
            else:
                messagebox.showerror("错误", "串口连接失败，请检查串口号和设备连接")
        
        def on_skip():
            """跳过连接（离线模式）"""
            if messagebox.askyesno("离线模式", "跳过串口连接将进入离线演示模式\n部分功能将不可用，确定吗？"):
                self.serial_comm = None
                dialog.destroy()
                self.create_pages()
                self.navigate(0)
        
        tk.Button(
            btn_frame,
            text="连接",
            font=FONT_BUTTON,
            width=10,
            bg=COLOR_SUCCESS,
            fg='white',
            command=on_connect
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="跳过（离线）",
            font=FONT_BUTTON,
            width=12,
            bg='#9E9E9E',
            fg='white',
            command=on_skip
        ).pack(side=tk.LEFT, padx=10)
        
    def create_pages(self):
        """创建所有页面"""
        self.pages[0] = MainMenu(self.container, self.navigate)
        self.pages[7] = DualParamControl(self.container, self.serial_comm, self.navigate)
        self.pages[8] = TripleParamControl(self.container, self.serial_comm, self.navigate)
        self.pages[9] = SystemModeling(self.container, self.serial_comm, self.navigate)
    
    def navigate(self, page_num: int):
        """导航到指定页面"""
        if page_num not in self.pages:
            messagebox.showerror("错误", f"页面 {page_num} 不存在")
            return
        
        # 隐藏当前页面
        if self.current_page is not None:
            self.current_page.pack_forget()
        
        # 显示新页面
        self.current_page = self.pages[page_num]
        self.current_page.pack(fill=tk.BOTH, expand=True)
        
        print(f"✓ 导航到 Page {page_num}")
    
    def reconnect_serial(self):
        """重新连接串口"""
        if self.serial_comm:
            self.serial_comm.disconnect()
        self.show_connection_dialog()
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
SA 串口上位机 v1.0

基于陶晶驰串口屏的Python移植版本

功能：
• 双参数控制（频率+幅值）
• 三参数控制（频率+幅值+峰值）
• 系统建模与识别
• 实时FFT频谱分析

协议：二进制小端序，固定6字节命令
波特率：115200 bps

© 2024 SA Project
        """
        messagebox.showinfo("关于", about_text.strip())
    
    def show_protocol_info(self):
        """显示协议说明"""
        protocol_text = """
串口通讯协议说明

命令格式：固定6字节

命令列表：
• 0x21: 频率设置（方式2）- 4字节小端序
• 0xF2: 频率设置（方式1）- 4字节小端序
• 0x22: 幅值设置 - 3字节×100小端序
• 0x23: 峰值设置 - 3字节×100小端序
• 0x01: Clear Buff - 01 01 01 01 01 01
• 0xF0: 建模命令 - F0 F0 F0 F0 F0 24
• 0xF1: 启动命令 - F1 F1 F1 F1 F1 24

反馈格式：
控件名.属性="值"\\xff\\xff\\xff

示例：
f0.txt="1000 Hz"\\xff\\xff\\xff
        """
        messagebox.showinfo("协议说明", protocol_text.strip())
    
    def on_close(self):
        """关闭应用程序"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            if self.serial_comm:
                self.serial_comm.disconnect()
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = HMIApplication(root)
    
    # 绑定关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()

