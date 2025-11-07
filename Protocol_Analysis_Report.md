# 串口屏协议与下位机代码对比分析报告

> **分析日期**: 2025年
> **下位机平台**: Xilinx Zynq-7000 (ARM Cortex-A9)  
> **串口屏**: 陶晶驰 HMI  
> **波特率**: 115200

---

## ⚠️ 重要发现：协议不匹配！

**HMI文档中描述的协议格式与下位机实际实现完全不同！**

- **文档说明**: 数据以ASCII字符串形式传输
- **实际代码**: 数据以二进制（小端序）形式传输

---

## 一、完整协议对比表

### 1. 频率设置命令（方式2）

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令码** | 0x21 | 0x21 | ✅ 匹配 |
| **数据格式** | ASCII字符串（如"1000"） | 4字节二进制（小端序） | ❌ **不匹配** |
| **数据示例** | `21 31 30 30 30 24` | `21 E8 03 00 00 ??` | ❌ 完全不同 |
| **帧尾** | 0x24 | 任意（未检查） | ⚠️ 部分匹配 |
| **功能** | 设置频率 | 设置频率，调用start_2_output() | ✅ 匹配 |

**下位机实际代码**:
```c
case 0x21: {
    flag = 0;
    // 小端序读取4字节
    recv_freq = Receive_Buffer[1] + 
                (Receive_Buffer[2]<<8) + 
                (Receive_Buffer[3]<<16) + 
                (Receive_Buffer[4]<<24);
    start_2_output((float)recv_freq, recv_in_voltage);
    
    // 反馈到HMI显示
    sprintf(tx_buffer,"%s=\"%ld Hz\"\xff\xff\xff", "f0.txt", recv_freq);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    break;
}
```

**正确的发送示例**:
```python
# 设置频率为1000Hz
freq = 1000
cmd = bytes([0x21, 
             freq & 0xFF,           # 低字节: 0xE8
             (freq >> 8) & 0xFF,    # 次低字节: 0x03
             (freq >> 16) & 0xFF,   # 次高字节: 0x00
             (freq >> 24) & 0xFF,   # 高字节: 0x00
             0x00])                 # 占位字节（未使用）
# 实际输出: 21 E8 03 00 00 00
```

---

### 2. 频率设置命令（方式1）- 未记录！

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令码** | **无此命令** | 0xF2 | ❌ **文档缺失** |
| **数据格式** | - | 4字节二进制（小端序） | - |
| **功能** | - | 设置频率，调用start_1_output() | - |

**下位机实际代码**:
```c
case 0xF2: {
    flag = 0;
    recv_freq = Receive_Buffer[1] + 
                (Receive_Buffer[2]<<8) + 
                (Receive_Buffer[3]<<16) + 
                (Receive_Buffer[4]<<24);
    start_1_output((float)recv_freq, recv_out_voltage);  // 不同！
    
    sprintf(tx_buffer,"%s=\"%ld Hz\"\xff\xff\xff", "f0.txt", recv_freq);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    break;
}
```

**start_1_output vs start_2_output 区别**:
```c
// start_1_output: 使用增益补偿
void start_1_output(float freqency, float circuit_target_voltage){
    output_start();
    scan_out_start();
    set_freq_start(freqency);
    // 根据频率响应自动调整增益
    set_gain(get_fpga_output_amp(freqency, circuit_target_voltage) 
             / 10.0 / 0.52668 / 1.0102);
}

// start_2_output: 直接输出
void start_2_output(float freqency, float circuit_target_voltage){
    output_start();
    scan_out_start();
    set_freq_start(freqency);
    // 直接设置电压
    set_gain(circuit_target_voltage / 10.0 / 0.52668 / 1.0102);
}
```

---

### 3. 幅值设置命令

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令码** | 0x22 | 0x22 | ✅ 匹配 |
| **数据格式** | ASCII字符串（如"3.5"） | 3字节二进制 / 100.0 | ❌ **不匹配** |
| **数据示例** | `22 33 2E 35 24` | `22 5E 01 00 ?? ?? ??` | ❌ 完全不同 |
| **帧尾** | 0x24 | 任意（未检查） | ⚠️ 部分匹配 |

**下位机实际代码**:
```c
case 0x22: {
    flag = 0;
    // 小端序读取3字节，除以100得到实际电压
    recv_in_voltage = (Receive_Buffer[1] + 
                      (Receive_Buffer[2]<<8) + 
                      (Receive_Buffer[3]<<16)) / 100.0;
    start_2_output((float)recv_freq, recv_in_voltage);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "v0.txt", recv_in_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    break;
}
```

**正确的发送示例**:
```python
# 设置幅值为3.50V
amp = 3.5
amp_int = int(amp * 100)  # 350
cmd = bytes([0x22,
             amp_int & 0xFF,           # 0x5E
             (amp_int >> 8) & 0xFF,    # 0x01
             (amp_int >> 16) & 0xFF,   # 0x00
             0x00, 0x00, 0x00])        # 占位字节
# 实际输出: 22 5E 01 00 00 00 00
```

---

### 4. 峰峰值设置命令

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令码** | 0x23 | 0x23 | ✅ 匹配 |
| **数据格式** | ASCII字符串（如"5.0"） | 3字节二进制 / 100.0 | ❌ **不匹配** |
| **数据示例** | `23 35 2E 30 24` | `23 F4 01 00 ?? ?? ??` | ❌ 完全不同 |
| **功能** | 设置峰峰值 | 设置输出电压，调用start_1_output() | ✅ 匹配 |

**下位机实际代码**:
```c
case 0x23: {
    flag = 0;
    // 小端序读取3字节，除以100得到实际电压
    recv_out_voltage = (Receive_Buffer[1] + 
                       (Receive_Buffer[2]<<8) + 
                       (Receive_Buffer[3]<<16)) / 100.0;
    start_1_output((float)recv_freq, recv_out_voltage);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "vp0.txt", recv_out_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    break;
}
```

---

### 5. Clear Buff命令

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令格式** | `01 01 01 01 01 01` | `01 01 01 01 01 01` | ✅ **完全匹配** |
| **功能** | 清空缓冲区 | 重置所有参数为默认值 | ✅ 匹配 |

**下位机实际代码**:
```c
case 0x01: {
    flag = 0;
    // 重置为默认值
    recv_out_voltage = 1;      // 输出电压 = 1V
    recv_in_voltage = 1;       // 输入电压 = 1V
    recv_freq = 1000;          // 频率 = 1000Hz
    
    start_2_output((float)recv_freq, recv_in_voltage);
    
    // 反馈所有默认值到HMI
    sprintf(tx_buffer, "%s=\"%d Hz\"\xff\xff\xff", "f0.txt", recv_freq);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "v0.txt", recv_in_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "vp0.txt", recv_out_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    break;
}
```

---

### 6. 建模命令（一键学习）

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令格式** | `F0 F0 F0 F0 F0 24` | `F0 F0 F0 F0 F0 24` | ✅ **完全匹配** |
| **帧尾检查** | 未说明 | **必须是0x24** | ⚠️ 补充 |
| **功能** | 启动建模 | 执行频率扫描和滤波器识别 | ✅ 匹配 |

**下位机实际代码**:
```c
case 0xF0: {
    // 检查帧尾必须是0x24
    if(Receive_Buffer[5] == 0x24) {
        flag = 0;
        process_scan();    // 执行频率扫描
        show_ui();         // 更新LCD显示
        
        // 反馈滤波器类型识别结果
        sprintf(tx_buffer, "%s=\"Filter Type : %s\"\xff\xff\xff", 
                "result.txt", filter_type_to_string(Check_Filter_Type()));
        PS_Uart_SendString(&UartPs0, tx_buffer);
        break;
    }
}
```

**process_scan()功能**:
```c
void process_scan(void){
    // 设置初始增益
    set_gain(2.0 / 10.0 / 0.52668 / 1.0102);
    output_stop();
    scan_out_start();
    
    // 第一段扫描: 200Hz - 50kHz, 步进25Hz
    select_bram(1);
    set_linear_axis();
    set_freq_start(200);
    set_freq_step(25);
    set_freq_stop(50000);
    set_gain(0.5);
    set_wait(0.03);
    scan_start();
    
    // 第二段扫描: 50kHz - 500kHz, 步进300Hz
    select_bram(2);
    cancel_bram(1);
    set_linear_axis();
    set_freq_start(50000);
    set_freq_step(300);
    set_freq_stop(500000);
    set_gain(0.5);
    set_wait(0.03);
    scan_start();
    
    scan_out_stop();
    
    // 校准和滤波器类型识别
    cali0_point(1750);
    // ... 更多校准点
}
```

---

### 7. 启动命令（启动探究装置）

| 项目 | HMI文档描述 | 下位机实际实现 | 匹配度 |
|------|------------|--------------|--------|
| **命令格式** | `F1 F1 F1 F1 F1 24` | `F1 F1 F1 F1 F1 24` | ✅ **完全匹配** |
| **帧尾检查** | 未说明 | **必须是0x24** | ⚠️ 补充 |
| **功能** | 启动装置 | 设置flag=1，启动FFT循环 | ✅ 匹配 |

**下位机实际代码**:
```c
case 0xF1: {
    // 检查帧尾必须是0x24
    if(Receive_Buffer[5] == 0x24) {
        flag = 1;    // 启动主循环的FFT处理
        break;
    }
}
```

**主循环代码（main.c）**:
```c
int main(void)
{
    // ... 初始化代码 ...
    
    while(1)
    {
        if(flag){
            FFT_Start();      // 执行FFT分析
            show_ui();        // 更新LCD显示
            refresh_peaks();  // 刷新峰值检测
            update_dds();     // 更新DDS输出
            sleep(2);
        }
    }
    return 0;
}
```

---

## 二、下位机反馈协议（HMI文档未记录）

### 反馈格式

下位机向HMI发送的反馈数据格式：
```
控件名.属性="值"\xff\xff\xff
```

### 反馈示例

| 控件 | 发送内容 | 说明 |
|------|---------|------|
| f0.txt | `f0.txt="1000 Hz"\xff\xff\xff` | 频率显示（<1kHz） |
| f0.txt | `f0.txt="1.50 kHz"\xff\xff\xff` | 频率显示（1kHz-1MHz） |
| f0.txt | `f0.txt="2.50 MHz"\xff\xff\xff` | 频率显示（≥1MHz） |
| v0.txt | `v0.txt="3.50 V"\xff\xff\xff` | 输入电压显示 |
| vp0.txt | `vp0.txt="5.00 V"\xff\xff\xff` | 输出电压显示 |
| result.txt | `result.txt="Filter Type : LPF"\xff\xff\xff` | 滤波器类型识别结果 |

### 结束符说明

- `\xff\xff\xff` (3个0xFF字节) 是陶晶驰HMI的**固定结束符**
- 所有发送到HMI的字符串命令都必须以此结尾

---

## 三、完整协议修正版

### 实际协议格式总结

| 命令码 | 命令名称 | 数据格式 | 数据长度 | 帧尾 | 总长度 |
|--------|---------|---------|---------|------|--------|
| 0x21 | 频率设置（方式2） | 4字节小端序 uint32 | 4 | 任意 | 6字节 |
| 0xF2 | 频率设置（方式1） | 4字节小端序 uint32 | 4 | 任意 | 6字节 |
| 0x22 | 幅值设置（输入） | 3字节小端序 int÷100 | 3 | 任意 | 6字节 |
| 0x23 | 峰值设置（输出） | 3字节小端序 int÷100 | 3 | 任意 | 6字节 |
| 0x01 | Clear Buff | 固定格式 | 5 | 0x01 | 6字节 |
| 0xF0 | 建模命令 | 固定格式 | 4 | **0x24** | 6字节 |
| 0xF1 | 启动命令 | 固定格式 | 4 | **0x24** | 6字节 |

### PC端正确实现（Python）

```python
import serial
import struct

class ZynqController:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
    
    def send_freq_mode2(self, freq_hz):
        """发送频率设置命令（方式2：直接输出）"""
        cmd = bytearray(6)
        cmd[0] = 0x21
        cmd[1:5] = struct.pack('<I', int(freq_hz))  # 小端序uint32
        cmd[5] = 0x00  # 占位
        self.ser.write(cmd)
        print(f"发送频率命令（方式2）: {freq_hz}Hz -> {cmd.hex()}")
    
    def send_freq_mode1(self, freq_hz):
        """发送频率设置命令（方式1：增益补偿）"""
        cmd = bytearray(6)
        cmd[0] = 0xF2
        cmd[1:5] = struct.pack('<I', int(freq_hz))  # 小端序uint32
        cmd[5] = 0x00  # 占位
        self.ser.write(cmd)
        print(f"发送频率命令（方式1）: {freq_hz}Hz -> {cmd.hex()}")
    
    def send_amplitude_input(self, voltage):
        """发送幅值设置命令（输入电压）"""
        cmd = bytearray(6)
        cmd[0] = 0x22
        volt_int = int(voltage * 100)  # 转换为整数（*100）
        cmd[1:4] = struct.pack('<I', volt_int)[0:3]  # 小端序，取低3字节
        cmd[4:6] = [0x00, 0x00]  # 占位
        self.ser.write(cmd)
        print(f"发送幅值命令: {voltage}V -> {cmd.hex()}")
    
    def send_peak_output(self, voltage):
        """发送峰峰值设置命令（输出电压）"""
        cmd = bytearray(6)
        cmd[0] = 0x23
        volt_int = int(voltage * 100)
        cmd[1:4] = struct.pack('<I', volt_int)[0:3]
        cmd[4:6] = [0x00, 0x00]
        self.ser.write(cmd)
        print(f"发送峰值命令: {voltage}V -> {cmd.hex()}")
    
    def send_clear_buff(self):
        """发送清空缓冲命令"""
        cmd = bytes([0x01, 0x01, 0x01, 0x01, 0x01, 0x01])
        self.ser.write(cmd)
        print(f"发送Clear Buff命令")
    
    def send_modeling_start(self):
        """发送建模命令（一键学习）"""
        cmd = bytes([0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0x24])
        self.ser.write(cmd)
        print(f"发送建模命令")
    
    def send_start_device(self):
        """发送启动命令（启动探究装置）"""
        cmd = bytes([0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0x24])
        self.ser.write(cmd)
        print(f"发送启动命令")
    
    def read_feedback(self):
        """读取下位机反馈"""
        if self.ser.in_waiting:
            data = self.ser.read(self.ser.in_waiting)
            # 查找\xff\xff\xff结束符
            parts = data.split(b'\xff\xff\xff')
            for part in parts:
                if part:
                    try:
                        feedback = part.decode('utf-8', errors='ignore')
                        print(f"收到反馈: {feedback}")
                    except:
                        pass

# 使用示例
if __name__ == "__main__":
    ctrl = ZynqController('/dev/ttyUSB0')  # Linux
    # ctrl = ZynqController('COM3')  # Windows
    
    # 示例1: 设置频率为1000Hz（方式2）
    ctrl.send_freq_mode2(1000)
    
    # 示例2: 设置幅值为3.5V
    ctrl.send_amplitude_input(3.5)
    
    # 示例3: 清空缓冲
    ctrl.send_clear_buff()
    
    # 示例4: 启动建模
    ctrl.send_modeling_start()
    
    # 读取反馈
    import time
    time.sleep(0.5)
    ctrl.read_feedback()
```

---

## 四、关键差异总结

### 1. 数据编码方式

| 方面 | HMI文档 | 实际代码 |
|------|---------|---------|
| 编码方式 | ASCII字符串 | 二进制（小端序） |
| 频率1000Hz | `31 30 30 30` (4字节ASCII) | `E8 03 00 00` (4字节二进制) |
| 幅值3.5V | `33 2E 35` (3字节ASCII) | `5E 01 00` (3字节二进制×100) |

### 2. 命令完整性

| 命令 | HMI文档 | 实际代码 | 状态 |
|------|---------|---------|------|
| 0x21 频率 | ✅ 有记录 | ✅ 实现 | ⚠️ 格式错误 |
| 0xF2 频率 | ❌ **无记录** | ✅ 实现 | ❌ **缺失文档** |
| 0x22 幅值 | ✅ 有记录 | ✅ 实现 | ⚠️ 格式错误 |
| 0x23 峰值 | ✅ 有记录 | ✅ 实现 | ⚠️ 格式错误 |
| 0x01 清空 | ✅ 有记录 | ✅ 实现 | ✅ **完全匹配** |
| 0xF0 建模 | ✅ 有记录 | ✅ 实现 | ✅ **完全匹配** |
| 0xF1 启动 | ✅ 有记录 | ✅ 实现 | ✅ **完全匹配** |

### 3. 功能对应关系

| HMI按钮 | 预期命令 | 实际下位机处理 | 功能实现 |
|---------|---------|---------------|---------|
| 频率"应用" | 0x21 (文档格式) | 0x21 (二进制格式) | ✅ 可实现 |
| 幅值"应用" | 0x22 (文档格式) | 0x22 (二进制格式) | ✅ 可实现 |
| 峰值"应用" | 0x23 (文档格式) | 0x23 (二进制格式) | ✅ 可实现 |
| Clear Buff | 0x01×6 | 0x01×6 | ✅ **完全兼容** |
| 一键学习 | 0xF0×5+0x24 | 0xF0×5+0x24 | ✅ **完全兼容** |
| 启动装置 | 0xF1×5+0x24 | 0xF1×5+0x24 | ✅ **完全兼容** |

---

## 五、HMI工程需要修改的地方

### 原始HMI代码（错误）

```c
// Page 7 - 频率"应用"按钮（原文档描述）
if(state1.val == 1) {
  beep 50
  printh 21            // 帧头
  prints fs.val, 0     // ASCII字符串！错误！
  printh 24            // 帧尾
}
```

### 修正后的HMI代码（正确）

```c
// Page 7 - 频率"应用"按钮（修正版）
if(state1.val == 1) {
  beep 50
  printh 21                        // 帧头
  printh fs.val & 0xFF             // 低字节
  printh (fs.val >> 8) & 0xFF      // 次低字节
  printh (fs.val >> 16) & 0xFF     // 次高字节
  printh (fs.val >> 24) & 0xFF     // 高字节
  printh 00                        // 占位字节
}
```

### 幅值/峰值设置修正

```c
// Page 7 - 幅值"应用"按钮（修正版）
if(state1.val == 1) {
  beep 50
  temp.val = vs.val * 100          // 转换为整数×100
  printh 22                        // 帧头
  printh temp.val & 0xFF           // 低字节
  printh (temp.val >> 8) & 0xFF    // 次低字节
  printh (temp.val >> 16) & 0xFF   // 次高字节（通常为0）
  printh 00                        // 占位字节
  printh 00                        // 占位字节
  printh 00                        // 占位字节
}
```

---

## 六、验证建议

### 1. 串口调试步骤

1. **连接硬件**：PC ↔ USB转TTL ↔ Zynq UART0
2. **串口参数**：115200, 8N1, 无流控
3. **发送测试命令**：
   ```
   21 E8 03 00 00 00     # 设置频率1000Hz
   22 5E 01 00 00 00 00  # 设置幅值3.5V
   01 01 01 01 01 01     # 清空缓冲
   F0 F0 F0 F0 F0 24     # 启动建模
   ```
4. **观察反馈**：
   ```
   f0.txt="1000 Hz"\xff\xff\xff
   v0.txt="3.50 V"\xff\xff\xff
   ```

### 2. 测试工具推荐

- **串口调试助手**：支持HEX发送/接收
- **Python PySerial**：上面提供的代码
- **Logic Analyzer**：分析实际串口波形

### 3. 关键检查点

- ✅ 小端序正确（低字节在前）
- ✅ 电压值需要×100
- ✅ 固定命令（0x01, 0xF0, 0xF1）格式完全一致
- ✅ 反馈包含`\xff\xff\xff`结束符

---

## 七、结论

### ✅ 可以控制下位机！

虽然HMI文档中的协议描述完全错误，但通过分析下位机源码，我们找到了**实际有效的协议格式**。

### ⚠️ 必须修改的内容

1. **HMI工程代码**：
   - 将ASCII发送方式改为二进制发送
   - 频率/幅值/峰值都需要按照小端序编码
   - 电压值需要×100

2. **PC端实现**：
   - 使用上面提供的Python代码
   - 或根据协议修正版实现其他语言版本

3. **文档更新**：
   - Apply_HMI_Design_Documentation.md需要全面修订
   - 更新为二进制协议格式

### ✅ 已验证的命令

- **0x01 Clear Buff**：文档和代码完全一致 ✅
- **0xF0 建模命令**：文档和代码完全一致 ✅
- **0xF1 启动命令**：文档和代码完全一致 ✅

### ⚠️ 需要重新实现的命令

- **0x21 频率设置**：需要改为二进制格式
- **0x22 幅值设置**：需要改为二进制格式（×100）
- **0x23 峰值设置**：需要改为二进制格式（×100）
- **0xF2 频率设置**：文档缺失，需要补充

---

**报告完成时间**: 2025年  
**分析工具**: 下位机源码分析 + 协议逆向  
**下一步**: 更新HMI工程代码或直接使用PC端Python实现

