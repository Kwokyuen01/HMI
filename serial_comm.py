# -*- coding: utf-8 -*-
"""
串口通信模块
实现协议编码/解码和串口收发
"""

import serial
import struct
import threading
import time
from typing import Optional, Callable


class SerialComm:
    """串口通信类"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.is_connected = False
        self.receive_callback: Optional[Callable] = None
        self.receive_thread: Optional[threading.Thread] = None
        self.running = False
        
    def connect(self) -> bool:
        """连接串口"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.is_connected = True
            self.running = True
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            print(f"✓ 串口连接成功: {self.port} @ {self.baudrate}bps")
            return True
        except Exception as e:
            print(f"✗ 串口连接失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开串口"""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
        print("✓ 串口已断开")
    
    def set_receive_callback(self, callback: Callable):
        """设置接收回调函数"""
        self.receive_callback = callback
    
    def _receive_loop(self):
        """接收循环（在独立线程中运行）"""
        buffer = b''
        while self.running and self.serial and self.serial.is_open:
            try:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    buffer += data
                    
                    # 解析反馈命令（格式：控件名.属性="值"\xff\xff\xff）
                    while b'\xff\xff\xff' in buffer:
                        end_idx = buffer.find(b'\xff\xff\xff')
                        message = buffer[:end_idx].decode('utf-8', errors='ignore')
                        buffer = buffer[end_idx + 3:]  # 跳过结束符
                        
                        # 解析命令
                        if '=' in message:
                            parts = message.split('=', 1)
                            if len(parts) == 2:
                                obj_attr = parts[0].strip()
                                value = parts[1].strip().strip('"')
                                
                                if self.receive_callback:
                                    self.receive_callback(obj_attr, value)
                
                time.sleep(0.01)  # 避免CPU占用过高
            except Exception as e:
                print(f"接收数据错误: {e}")
                time.sleep(0.1)
    
    # ==================== 协议编码函数 ====================
    
    def send_freq_cmd(self, freq: int, mode: int = 2) -> bool:
        """
        发送频率设置命令
        Args:
            freq: 频率值（Hz）
            mode: 1=方式1(0xF2), 2=方式2(0x21)
        """
        try:
            cmd_code = 0xF2 if mode == 1 else 0x21
            # 构造6字节命令：命令码 + 4字节小端序频率 + 占位字节
            cmd = struct.pack('<BI', cmd_code, freq)  # 1字节+4字节=5字节
            cmd += b'\x00'  # 补齐到6字节
            self._send_raw(cmd)
            print(f"→ 发送频率命令: {freq}Hz (模式{mode}), HEX: {cmd.hex().upper()}")
            return True
        except Exception as e:
            print(f"✗ 发送频率命令失败: {e}")
            return False
    
    def send_voltage_cmd(self, voltage: float, cmd_type: str = 'amp') -> bool:
        """
        发送电压设置命令
        Args:
            voltage: 电压值（V）
            cmd_type: 'amp'=幅值(0x22), 'peak'=峰值(0x23)
        """
        try:
            cmd_code = 0x22 if cmd_type == 'amp' else 0x23
            # 电压×100转换为整数
            voltage_int = int(voltage * 100)
            # 构造6字节命令：命令码 + 3字节小端序 + 3个占位字节
            cmd = struct.pack('<B', cmd_code)  # 命令码
            cmd += struct.pack('<I', voltage_int)[:3]  # 取低3字节
            cmd += b'\x00\x00\x00'  # 补齐到6字节
            self._send_raw(cmd)
            print(f"→ 发送{'幅值' if cmd_type == 'amp' else '峰值'}命令: {voltage}V, HEX: {cmd.hex().upper()}")
            return True
        except Exception as e:
            print(f"✗ 发送电压命令失败: {e}")
            return False
    
    def send_clear_buff(self) -> bool:
        """发送清空缓冲命令"""
        try:
            cmd = b'\x01\x01\x01\x01\x01\x01'
            self._send_raw(cmd)
            print(f"→ 发送Clear Buff命令, HEX: {cmd.hex().upper()}")
            return True
        except Exception as e:
            print(f"✗ 发送Clear Buff命令失败: {e}")
            return False
    
    def send_modeling_cmd(self) -> bool:
        """发送建模命令"""
        try:
            cmd = b'\xF0\xF0\xF0\xF0\xF0\x24'
            self._send_raw(cmd)
            print(f"→ 发送建模命令, HEX: {cmd.hex().upper()}")
            return True
        except Exception as e:
            print(f"✗ 发送建模命令失败: {e}")
            return False
    
    def send_start_cmd(self) -> bool:
        """发送启动命令"""
        try:
            cmd = b'\xF1\xF1\xF1\xF1\xF1\x24'
            self._send_raw(cmd)
            print(f"→ 发送启动命令, HEX: {cmd.hex().upper()}")
            return True
        except Exception as e:
            print(f"✗ 发送启动命令失败: {e}")
            return False
    
    def _send_raw(self, data: bytes):
        """发送原始数据"""
        if self.serial and self.serial.is_open:
            self.serial.write(data)
            self.serial.flush()
        else:
            raise Exception("串口未连接")

