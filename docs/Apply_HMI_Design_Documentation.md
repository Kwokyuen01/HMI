# Apply.HMI 串口屏工程设计说明（PC移植版）

> **工程文件**: Apply.HMI  
> **目标平台**: PC端应用  
> **核心页面**: Page 0, 7, 8, 9  
> **移植说明**: Page 1-6为键盘/计算器/滑动条等输入辅助页面，PC端直接使用键盘输入替代

---

## 一、串口通讯协议

### ⚠️ 重要说明

**本协议基于下位机实际代码（ISR.c）分析得出，采用二进制编码方式！**

### 协议格式
```
[命令码 1字节] + [数据 N字节] = 总共6字节（固定长度）
```

### 命令定义

| 命令类型 | 命令码 (HEX) | 数据格式 | 数据长度 | 总长度 | 说明 |
|---------|-------------|---------|---------|--------|------|
| 频率设置（方式2） | 21 | 4字节二进制（小端序） | 4字节 | 6字节 | 直接输出模式 |
| 频率设置（方式1） | F2 | 4字节二进制（小端序） | 4字节 | 6字节 | 增益补偿模式 |
| 幅值设置 | 22 | 3字节二进制×100（小端序） | 3字节 | 6字节 | 设置输入电压 |
| 峰值设置 | 23 | 3字节二进制×100（小端序） | 3字节 | 6字节 | 设置输出电压 |
| Clear Buff | 01 | 固定格式：01 01 01 01 01 | 5字节 | 6字节 | 重置为默认值 |
| 建模命令 | F0 | 固定格式：F0 F0 F0 F0 24 | 5字节 | 6字节 | 频率扫描+识别 |
| 启动命令 | F1 | 固定格式：F1 F1 F1 F1 24 | 5字节 | 6字节 | 启动FFT循环 |

### 发送示例

**频率设置命令（方式2）**:
```c
// HMI代码（正确实现）
temp.val = fs.val           // 频率值（如1000）
printh 21                   // 命令码：0x21
printh temp.val & 0xFF      // 低字节：0xE8
printh (temp.val >> 8) & 0xFF     // 次低字节：0x03
printh (temp.val >> 16) & 0xFF    // 次高字节：0x00
printh (temp.val >> 24) & 0xFF    // 高字节：0x00
printh 00                   // 占位字节
```

实际串口输出：`21 E8 03 00 00 00` （设置频率为1000Hz）

**幅值设置命令**:
```c
// HMI代码（正确实现）
temp.val = vs.val * 100     // 电压×100（如3.5V → 350）
printh 22                   // 命令码：0x22
printh temp.val & 0xFF      // 低字节：0x5E
printh (temp.val >> 8) & 0xFF     // 次低字节：0x01
printh (temp.val >> 16) & 0xFF    // 次高字节：0x00
printh 00                   // 占位字节
printh 00                   // 占位字节
printh 00                   // 占位字节
```

实际串口输出：`22 5E 01 00 00 00 00` （设置幅值为3.5V）

**Clear Buff命令**:
```c
printh 01 01 01 01 01 01    // 固定6字节命令
```

实际串口输出：`01 01 01 01 01 01`

### 数据编码说明

1. **频率数据**：32位无符号整数（uint32），小端序
   - 范围：0 ~ 4,294,967,295 Hz
   - 示例：1000Hz → 0x000003E8 → 发送 E8 03 00 00

2. **电压数据**：24位整数×100，小端序
   - 实际电压 = 接收值 / 100.0
   - 范围：0.00 ~ 167772.15 V
   - 示例：3.5V → 350 → 0x00015E → 发送 5E 01 00

3. **小端序说明**：低位字节在前，高位字节在后
   - 0x12345678 → 发送顺序：78 56 34 12

---

## 二、Page 0 - 主菜单界面

### 界面布局
- **b0**: "基础任务(2)" 按钮
- **b1**: "基础任务(3、4)" 按钮
- **b2**: "发挥部分" 按钮
- **b8**: "RESET" 按钮
- **b7**: "串口调试" 按钮

### 控件详细信息

#### 按钮控件

**b0 - 基础任务(2)**
```
控件类型: 按钮 (att-43)
功能: 跳转到基础任务2页面
点击事件 (codesdown):
  // 跳转到Page 7或8
  page [目标页面ID]
```

**b1 - 基础任务(3、4)**
```
控件类型: 按钮 (att-43)
功能: 跳转到基础任务3、4页面
点击事件 (codesdown):
  // 跳转到对应页面
  page [目标页面ID]
```

**b2 - 发挥部分**
```
控件类型: 按钮 (att-43)
功能: 跳转到发挥功能页面
点击事件 (codesdown):
  // 跳转到发挥测试页
  page [目标页面ID]
```

**b8 - RESET**
```
控件类型: 按钮 (att-43)
功能: 系统重置
点击事件 (codesdown):
  // 发送clear buff命令
  printh 01 01 01 01 01 01
  // 重置所有变量
  // 停止所有定时器
```

**b7 - 串口调试**
```
控件类型: 按钮 (att-43)
功能: 打开串口调试页面
点击事件 (codesdown):
  // 跳转到Page 7或8
  page [串口页面ID]
```

### 页面事件代码

**页面加载事件 (codesload)**:
```c
// 初始化亮度变量
h0.val = dim
h1.val = dim
```

**定时器事件 (codestimer-9)**:
```c
// 旋转动画控制（每次+5度）
z0.val = z0.val + 5
if(z0.val == 360) {
  z0.val = 0         // 360度归零
}
if(z0.val == 215) {
  z0.val = 330       // 215度跳转到330度
}
```

### 变量列表
| 变量ID | 类型 | 说明 | 初始值 |
|--------|------|------|--------|
| z0 | 整型 | 旋转角度控制 | 0 |
| h0 | 整型 | 亮度变量1 | dim |
| h1 | 整型 | 亮度变量2 | dim |
| tm0 | 定时器 | 主定时器 | - |

---

## 三、Page 7 - 串口通讯控制页（双参数）

### 界面布局
- **t13**: "串口通讯：待机中.." 状态文本（顶部居中）
- **t1**: "当前频率：" 标签
- **f0/t3**: 频率显示值（文本框，显示"newtxt"）
- **t6**: "频率设置：" 标签
- **频率输入框**: 数字输入
- **b1_freq**: "+" 按钮（频率增加）
- **b3_freq**: "应用" 按钮（应用频率设置）
- **t2**: "当前幅值：" 标签
- **v0/t0**: 幅值显示值（文本框，显示"newtxt"）
- **t5**: "幅值设置：" 标签
- **幅值输入框**: 数字输入（显示"0.00"）
- **b1_amp**: "+" 按钮（幅值增加）
- **b2_amp**: "应用" 按钮（应用幅值设置）
- **clear_buff**: "clear buff" 按钮
- **b5**: "返回" 按钮（右下角）
- **b0**: "启动/停止" 按钮（右上角）

### 控件详细信息

#### 文本控件

**t13 - 状态显示**
```
控件类型: 文本框 (att-38)
功能: 显示串口通讯状态
内容:
  - "串口通讯：待机中.." （state1.val==0）
  - "串口通讯：运行中.." （state1.val==1）
更新事件:
  if(state1.val == 1) {
    t13.txt = "串口通讯：运行中.."
  } else if(state1.val == 0) {
    t13.txt = "串口通讯：待机中.."
  }
```

**f0 - 当前频率显示**
```
控件类型: 文本框
功能: 显示当前生效的频率值
初始值: "newtxt"
更新时机:
  - 应用按钮点击后更新为输入值
  - Clear buff后重置为"newtxt"
```

**v0 - 当前幅值显示**
```
控件类型: 文本框
功能: 显示当前生效的幅值
初始值: "newtxt"
更新时机:
  - 应用按钮点击后更新为输入值
  - Clear buff后重置为"newtxt"
```

#### 输入框控件

**频率输入框**
```
控件类型: 数字输入框 (type=54)
功能: 输入目标频率值
变量: fs.val
属性:
  - txt_maxl: 文本最大长度
  - vvs1: 小数位数
PC移植方案:
  - 使用标准输入框
  - 支持键盘直接输入数字
  - 范围验证
```

**幅值输入框**
```
控件类型: 数字输入框 (type=54)
功能: 输入目标幅值
变量: vs.val
初始显示: "0.00"
属性:
  - 支持小数输入
PC移植方案:
  - 使用标准输入框
  - 支持小数点
  - 范围验证
```

#### 按钮控件

**b1_freq - 频率"+"按钮**
```
控件类型: 按钮
功能: 频率增加100
点击事件 (codesdown-5):
  if(state1.val == 1) {
    fs.val += 100      // 频率增加100
  }
PC移植方案:
  - 点击按钮增加数值
  - 或直接键盘输入
```

**b3_freq - 频率"应用"按钮**
```
控件类型: 按钮
功能: 应用频率设置并发送串口命令
点击事件 (codesdown-7):
  if(state1.val == 1) {
    beep 50                        // 蜂鸣器响50ms
    printh 21                      // 命令码：0x21
    printh fs.val & 0xFF           // 低字节
    printh (fs.val >> 8) & 0xFF    // 次低字节
    printh (fs.val >> 16) & 0xFF   // 次高字节
    printh (fs.val >> 24) & 0xFF   // 高字节
    printh 00                      // 占位字节
  }

下位机处理:
  // ISR.c中的实际处理代码
  case 0x21: {
    flag = 0;
    // 小端序读取4字节频率
    recv_freq = Receive_Buffer[1] + 
                (Receive_Buffer[2]<<8) + 
                (Receive_Buffer[3]<<16) + 
                (Receive_Buffer[4]<<24);
    start_2_output((float)recv_freq, recv_in_voltage);
    
    // 反馈到HMI显示（f0.txt控件）
    sprintf(tx_buffer,"%s=\"%ld Hz\"\xff\xff\xff", "f0.txt", recv_freq);
    PS_Uart_SendString(&UartPs0, tx_buffer);
  }

串口输出示例:
  输入频率: 1000
  输出: 21 E8 03 00 00 00
       (0x21 低→高: 1000=0x3E8)
```

**b1_amp - 幅值"+"按钮**
```
控件类型: 按钮
功能: 幅值增加（触发输入或增加值）
点击事件 (codesdown-5):
  if(state1.val == 1) {
    vs.val += [增量]
  }
```

**b2_amp - 幅值"应用"按钮**
```
控件类型: 按钮
功能: 应用幅值设置并发送串口命令
点击事件 (codesdown-7):
  if(state1.val == 1) {
    beep 50                        // 蜂鸣器响50ms
    temp.val = vs.val * 100        // 电压×100转换为整数
    printh 22                      // 命令码：0x22
    printh temp.val & 0xFF         // 低字节
    printh (temp.val >> 8) & 0xFF  // 次低字节
    printh (temp.val >> 16) & 0xFF // 次高字节
    printh 00                      // 占位字节
    printh 00                      // 占位字节
    printh 00                      // 占位字节
  }

下位机处理:
  // ISR.c中的实际处理代码
  case 0x22: {
    flag = 0;
    // 小端序读取3字节，除以100得到实际电压
    recv_in_voltage = (Receive_Buffer[1] + 
                      (Receive_Buffer[2]<<8) + 
                      (Receive_Buffer[3]<<16)) / 100.0;
    start_2_output((float)recv_freq, recv_in_voltage);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "v0.txt", recv_in_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
  }

串口输出示例:
  输入幅值: 3.5V
  转换: 3.5 × 100 = 350 = 0x15E
  输出: 22 5E 01 00 00 00 00
       (0x22 低→高: 350=0x15E，后补0)
```

**b0 - 启动/停止按钮**
```
控件类型: 按钮
功能: 启动或停止串口通讯
点击事件 (codesdown):
  if(state1.val == 0) {
    state1.val = 1          // 设置为运行状态
    b0.txt = "停止"
    t13.txt = "串口通讯：运行中.."
  } else if(state1.val == 1) {
    state1.val = 0          // 设置为停止状态
    b0.txt = "启动"
    t13.txt = "串口通讯：待机中.."
    // 发送clear buff命令
    printh 01 01 01 01 01 01
  }
```

**clear_buff - Clear Buff按钮**
```
控件类型: 按钮
功能: 清空数据缓冲区，重置显示值
点击事件 (codesdown):
  if(state1.val == 1) {
    beep 50                      // 蜂鸣器响50ms
    printh 01 01 01 01 01 01     // 发送clear buff命令（固定格式）
    // 注意：显示值的重置由下位机反馈更新，不需要在HMI端手动设置
  }

下位机处理:
  // ISR.c中的实际处理代码
  case 0x01: {
    flag = 0;
    // 重置为默认值
    recv_out_voltage = 1;      // 输出电压 = 1V
    recv_in_voltage = 1;       // 输入电压 = 1V
    recv_freq = 1000;          // 频率 = 1000Hz
    
    start_2_output((float)recv_freq, recv_in_voltage);
    
    // 反馈所有默认值到HMI（自动更新显示）
    sprintf(tx_buffer, "%s=\"%d Hz\"\xff\xff\xff", "f0.txt", recv_freq);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "v0.txt", recv_in_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "vp0.txt", recv_out_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
  }

串口输出: 01 01 01 01 01 01 (固定6字节)
HMI接收反馈:
  - f0.txt="1000 Hz"\xff\xff\xff
  - v0.txt="1.00 V"\xff\xff\xff
  - vp0.txt="1.00 V"\xff\xff\xff
```

**b5 - 返回按钮**
```
控件类型: 按钮
功能: 返回主菜单
点击事件 (codesdown):
  // 保存当前状态
  // 跳转到Page 0
  page 0
```

### 变量列表
| 变量ID | 类型 | 说明 | 初始值 | 作用 |
|--------|------|------|--------|------|
| state1 | 整型 | 运行状态标志 | 0 | 0=停止, 1=运行 |
| fs | 整型 | 频率设置值 | 0 | 用于串口发送 |
| f0 | 文本 | 当前频率显示 | "newtxt" | 显示用 |
| vs | 整型 | 幅值设置值 | 0 | 用于串口发送 |
| v0 | 文本 | 当前幅值显示 | "newtxt" | 显示用 |
| t13 | 文本 | 状态文本 | "待机中.." | 状态提示 |

### 页面事件代码

**页面加载事件 (codesload)**:
```c
// 初始化状态为运行
state1.val = 1

// 初始化显示文本
if(state1.val == 1) {
  f0.txt = "newtxt"
  fs.val = 0
  v0.txt = "newtxt"
  vs.val = 0
}
```

**停止时清空 (codesdown)**:
```c
// 当停止按钮被点击且当前为运行状态
if(state1.val == 1) {
  // ... 切换到停止状态
} else if(state1.val == 0) {
  // 发送clear buff命令
  printh 01 01 01 01 01 01
}
```

---

## 四、Page 8 - 串口通讯控制页（三参数）

### 界面布局
与Page 7相同，但增加了峰峰值设置：
- **所有Page 7的控件**
- **t7**: "系统输出电压峰峰值设置：" 标签
- **t8**: "当前峰峰值：" 标签
- **vp0**: 峰峰值显示（文本框，显示"newtxt"）
- **t10**: "峰值设置：" 标签
- **峰值输入框**: 数字输入 (显示"0.00")
- **b1_peak**: "+" 按钮（峰值增加）
- **b2_peak**: "应用" 按钮（应用峰值设置）
- **t12**: "clear buff 接收等待中..." 文本

### 新增控件

**vp0 - 当前峰峰值显示**
```
控件类型: 文本框
功能: 显示当前生效的峰峰值
初始值: "newtxt"
更新时机:
  - 应用按钮点击后更新为输入值
  - Clear buff后重置为"newtxt"
```

**峰值输入框**
```
控件类型: 数字输入框 (type=54)
功能: 输入目标峰峰值
变量: vps.val
初始显示: "0.00"
属性:
  - 支持小数输入
```

**b1_peak - 峰值"+"按钮**
```
控件类型: 按钮
功能: 峰值增加
点击事件 (codesdown-5):
  if(state1.val == 1) {
    vps.val += [增量]
  }
```

**b2_peak - 峰值"应用"按钮**
```
控件类型: 按钮
功能: 应用峰值设置并发送串口命令
点击事件 (codesdown-7):
  if(state1.val == 1) {
    beep 50                        // 蜂鸣器响50ms
    temp.val = vps.val * 100       // 电压×100转换为整数
    printh 23                      // 命令码：0x23
    printh temp.val & 0xFF         // 低字节
    printh (temp.val >> 8) & 0xFF  // 次低字节
    printh (temp.val >> 16) & 0xFF // 次高字节
    printh 00                      // 占位字节
    printh 00                      // 占位字节
    printh 00                      // 占位字节
  }

下位机处理:
  // ISR.c中的实际处理代码
  case 0x23: {
    flag = 0;
    // 小端序读取3字节，除以100得到实际电压
    recv_out_voltage = (Receive_Buffer[1] + 
                       (Receive_Buffer[2]<<8) + 
                       (Receive_Buffer[3]<<16)) / 100.0;
    start_1_output((float)recv_freq, recv_out_voltage);  // 注意：使用方式1
    
    sprintf(tx_buffer, "%s=\"%.2f V\"\xff\xff\xff", "vp0.txt", recv_out_voltage);
    PS_Uart_SendString(&UartPs0, tx_buffer);
  }

注意: 峰值设置使用start_1_output()（增益补偿模式）

串口输出示例:
  输入峰值: 5.0V
  转换: 5.0 × 100 = 500 = 0x1F4
  输出: 23 F4 01 00 00 00 00
       (0x23 低→高: 500=0x1F4，后补0)
```

**t12 - 接收状态文本**
```
控件类型: 文本框
功能: 显示串口接收状态
内容:
  - "clear buff 接收等待中..."
  - "clear buff 接收完成"
  - 实时更新接收进度
```

**clear_buff - Clear Buff按钮 (Page 8版本)**
```
控件类型: 按钮
功能: 清空三个参数的数据缓冲区
点击事件 (codesdown):
  if(state1.val == 1) {
    beep 50                      // 蜂鸣器响50ms
    printh 01 01 01 01 01 01     // 发送clear buff命令（固定格式）
    // 注意：显示值由下位机反馈自动更新，包括：
    // - f0.txt="1000 Hz"
    // - v0.txt="1.00 V"
    // - vp0.txt="1.00 V"
  }

下位机处理: （与Page 7相同，见前面描述）
  - 重置频率为1000Hz，输入/输出电压为1V
  - 自动发送三个反馈命令更新HMI显示
```

### 变量列表
| 变量ID | 类型 | 说明 | 初始值 | 作用 |
|--------|------|------|--------|------|
| state1 | 整型 | 运行状态 | 0 | 0=停止, 1=运行 |
| fs | 整型 | 频率设置值 | 0 | 用于串口发送 |
| f0 | 文本 | 当前频率显示 | "newtxt" | 显示用 |
| vs | 整型 | 幅值设置值 | 0 | 用于串口发送 |
| v0 | 文本 | 当前幅值显示 | "newtxt" | 显示用 |
| vps | 整型 | 峰值设置值 | 0 | 用于串口发送 |
| vp0 | 文本 | 当前峰峰值显示 | "newtxt" | 显示用 |
| t12 | 文本 | 接收状态文本 | "接收等待中..." | 状态提示 |

### 页面事件代码

**页面加载事件 (codesload)**:
```c
// 初始化状态为运行
state1.val = 1

// 初始化三个参数显示
if(state1.val == 1) {
  f0.txt = "newtxt"
  fs.val = 0
  v0.txt = "newtxt"
  vs.val = 0
  vp0.txt = "newtxt"
  vps.val = 0
}
```

**清空缓冲事件 (codesdown)**:
```c
// clear buff按钮点击
if(state1.val == 1) {
  beep 50
  printh 01 01 01 01 01 01
  f0.txt = "newtxt"
  v0.txt = "newtxt"
  vp0.txt = "newtxt"
  fs.val = 0
  vs.val = 0
  vps.val = 0
}
```

---

## 五、Page 9 - 系统建模控制页

### 界面布局
- **t12**: "未知电路模型建模：待机中.." 状态文本（顶部）
- **b9**: "第一部分：一键学习" 按钮（灰色大按钮）
- **result**: "系统建模中... 请等待..." 文本（黑色背景，可隐藏）
- **t0**: "启动状态：未启动" 状态文本
- **b0**: "第二部分：启动探究装置" 按钮（灰色大按钮）
- **b7**: "返回" 按钮（右下角）

### 控件详细信息

#### 文本控件

**t12 - 页面标题/状态**
```
控件类型: 文本框
功能: 显示系统建模状态
内容:
  - "未知电路模型建模：待机中.." (b9.bco==50712)
  - "未知电路模型建模：运行中.." (b9.bco==33808)
更新时机:
  - b9按钮点击时动态更新
```

**result - 进度信息文本**
```
控件类型: 文本框
功能: 显示建模进度信息
内容:
  - "系统建模中... 请等待..."
  - 可能显示建模结果数据
样式:
  - 黑色背景
  - 白色或绿色文字
可见性控制:
  - vis result, 1  // 显示
  - vis result, 0  // 隐藏
```

**t0 - 启动状态**
```
控件类型: 文本框
功能: 显示第二部分的启动状态
内容:
  - "启动状态：未启动" (b0.bco==50712)
  - "启动状态：已启动" (b0.bco==33808)
更新时机:
  - b0按钮点击时动态更新
```

#### 按钮控件

**b9 - 第一部分：一键学习**
```
控件类型: 按钮 (大按钮)
功能: 启动/停止系统建模学习过程
点击事件 (codesup-13):
  if(b9.bco == 50712) {
    // 按钮默认状态（灰色），点击启动建模
    t12.txt = "[运行中文本]"        // 更新状态文本
    vis result, 1                    // 显示建模进度文本
    b9.bco = 33808                   // 改变按钮颜色为激活状态（橙色/红色）
    beep 50                          // 蜂鸣器响50ms
    printh F0 F0 F0 F0 F0 24        // 发送建模启动命令
  } else {
    // 按钮激活状态，点击停止建模
    t12.txt = "[待机文本]"          // 恢复状态文本
    vis result, 0                    // 隐藏建模进度文本
    b9.bco = 50712                   // 恢复按钮颜色为默认灰色
    beep 50                          // 蜂鸣器响50ms
    printh F0 F0 F0 F0 F0 24        // 发送建模停止命令
  }

串口输出: F0 F0 F0 F0 F0 24 (固定命令)

颜色说明:
  50712 = 0xC618 (RGB565: 灰色，默认状态)
  33808 = 0x8410 (RGB565: 橙/红色，激活状态)
```

**b0 - 第二部分：启动探究装置**
```
控件类型: 按钮 (大按钮)
功能: 启动/停止探究装置
点击事件 (codesup-10):
  if(b0.bco == 50712) {
    // 按钮默认状态，点击启动
    b0.bco = 33808                   // 改变为激活颜色
    beep 50                          // 蜂鸣器响50ms
    printh F1 F1 F1 F1 F1 24        // 发送启动命令
    t0.txt = "[已启动文本]"         // 更新状态文本
  } else {
    // 按钮激活状态，点击停止
    b0.bco = 50712                   // 恢复默认颜色
    beep 50                          // 蜂鸣器响50ms
    printh F1 F1 F1 F1 F1 24        // 发送停止命令
    t0.txt = "[未启动文本]"         // 更新状态文本
  }

串口输出: F1 F1 F1 F1 F1 24 (固定命令)
```

**b7 - 返回**
```
控件类型: 按钮
功能: 返回主菜单
点击事件 (codesdown):
  // 停止所有运行中的任务
  if(b9.bco == 33808) {
    // 停止建模
    b9.bco = 50712
    vis result, 0
  }
  if(b0.bco == 33808) {
    // 停止装置
    b0.bco = 50712
  }
  // 跳转到Page 0
  page 0
```

### 变量列表
| 变量ID | 类型 | 说明 | 初始值 | 颜色值 |
|--------|------|------|--------|--------|
| b9.bco | 整型 | 建模按钮背景色 | 50712 | 灰色=50712, 激活=33808 |
| b0.bco | 整型 | 启动按钮背景色 | 50712 | 灰色=50712, 激活=33808 |
| t12 | 文本 | 页面状态文本 | "待机中.." | - |
| result | 文本 | 建模结果文本 | "" | 可隐藏控件 |
| t0 | 文本 | 启动状态文本 | "未启动" | - |

### 按钮颜色状态表

| 颜色值 (DEC) | 颜色值 (HEX) | RGB565 | 显示颜色 | 状态 |
|-------------|-------------|--------|---------|------|
| 50712 | 0xC618 | R=24, G=48, B=24 | 灰色 | 默认/未激活 |
| 33808 | 0x8410 | R=16, G=33, B=16 | 橙/红色 | 激活/运行中 |

### 页面事件代码

**建模按钮点击事件 (codesup-13)**:
```c
// HMI代码
// 点击"第一部分：一键学习"按钮
if(b9.bco == 50712) {
  // 默认状态，启动建模
  t12.txt = "未知电路模型建模：运行中.."
  vis result, 1              // 显示result控件
  b9.bco = 33808             // 改变按钮颜色为激活状态
  beep 50
  printh F0 F0 F0 F0 F0 24   // 发送建模命令（固定格式）
} else {
  // 已激活状态，停止建模
  t12.txt = "未知电路模型建模：待机中.."
  vis result, 0              // 隐藏result控件
  b9.bco = 50712             // 恢复按钮颜色为默认
  beep 50
  printh F0 F0 F0 F0 F0 24   // 发送停止命令（相同命令）
}

// 下位机处理 (ISR.c)
case 0xF0: {
  // 必须检查帧尾为0x24
  if(Receive_Buffer[5] == 0x24) {
    flag = 0;
    process_scan();    // 执行频率扫描（200Hz-500kHz）
    show_ui();         // 更新LCD显示FFT和波特图
    
    // 反馈滤波器类型识别结果
    sprintf(tx_buffer, "%s=\"Filter Type : %s\"\xff\xff\xff", 
            "result.txt", filter_type_to_string(Check_Filter_Type()));
    PS_Uart_SendString(&UartPs0, tx_buffer);
  }
}

process_scan()功能：
  - 第一段扫描: 200Hz - 50kHz, 步进25Hz
  - 第二段扫描: 50kHz - 500kHz, 步进300Hz
  - 校准点处理和滤波器类型识别
  - 结果包括: LPF(低通), HPF(高通), BPF(带通), BSF(带阻)等
```

**启动装置按钮点击事件 (codesup-10)**:
```c
// HMI代码
// 点击"第二部分：启动探究装置"按钮
if(b0.bco == 50712) {
  // 默认状态，启动装置
  b0.bco = 33808              // 激活颜色
  beep 50
  printh F1 F1 F1 F1 F1 24    // 发送启动命令（固定格式）
  t0.txt = "启动状态：已启动"
} else {
  // 已激活状态，停止装置
  b0.bco = 50712              // 默认颜色
  beep 50
  printh F1 F1 F1 F1 F1 24    // 发送停止命令（相同命令）
  t0.txt = "启动状态：未启动"
}

// 下位机处理 (ISR.c)
case 0xF1: {
  // 必须检查帧尾为0x24
  if(Receive_Buffer[5] == 0x24) {
    flag = 1;    // 启动主循环的FFT处理标志
  }
}

// 主循环 (main.c)
while(1) {
  if(flag){
    FFT_Start();      // 执行FFT分析
    show_ui();        // 更新LCD显示（FFT频谱+波特图）
    refresh_peaks();  // 刷新峰值检测（找出10个峰值）
    update_dds();     // 更新DDS输出（多频合成）
    sleep(2);         // 延时2秒
  }
}

功能说明:
  - 实时FFT频谱分析
  - 峰值检测（最多10个频率分量）
  - 自动生成多频合成波形
  - LCD实时显示频谱和波特图
```

---

## 六、串口通讯协议详细说明

### 1. 数据格式

#### 二进制编码数据帧（小端序）
所有数值参数（频率、幅值、峰值）均以**二进制小端序**形式发送，**不是ASCII**！

**示例1：发送频率（整数）**
```
设置频率 = 1000 (0x3E8)
串口输出: 21 E8 03 00 00 00
解析:
  21        - 命令码（频率设置）
  E8 03 00 00 - 1000的小端序表示
                E8 = 低字节 (232)
                03 = 次低字节 (3)
                00 = 次高字节
                00 = 高字节
  00        - 占位字节（第6字节，固定6字节长度）
```

**示例2：发送幅值（小数）**
```
设置幅值 = 3.5V
转换: 3.5 × 100 = 350 (0x15E)
串口输出: 22 5E 01 00 00 00 00
解析:
  22           - 命令码（幅值设置）
  5E 01 00     - 350的小端序表示（3字节）
                 5E = 低字节 (94)
                 01 = 次低字节 (1)
                 00 = 高字节
  00 00 00     - 占位字节（补齐到6字节）
```

**示例3：发送峰值（小数）**
```
设置峰值 = 5.0V
转换: 5.0 × 100 = 500 (0x1F4)
串口输出: 23 F4 01 00 00 00 00
解析:
  23           - 命令码（峰值设置）
  F4 01 00     - 500的小端序表示（3字节）
                 F4 = 低字节 (244)
                 01 = 次低字节 (1)
                 00 = 高字节
  00 00 00     - 占位字节
```

### 2. HMI命令发送函数

**printh 命令**（发送单字节）:
```c
printh 21                    // 发送单字节0x21
printh F0 F0 F0 F0 F0 24    // 发送6字节: 0xF0 0xF0 0xF0 0xF0 0xF0 0x24
```

**发送多字节变量**（小端序）:
```c
// 错误方式（原文档）：
prints fs.val, 0    // 这会发送ASCII字符串！错误！

// 正确方式（实际需要）：
printh fs.val & 0xFF           // 低字节
printh (fs.val >> 8) & 0xFF    // 次低字节
printh (fs.val >> 16) & 0xFF   // 次高字节
printh (fs.val >> 24) & 0xFF   // 高字节
```

**beep 命令**:
```c
beep 50    // 蜂鸣器响50毫秒
```

### 2.5 下位机反馈协议（HMI接收）

**反馈格式**:
```
控件名.属性="值"\xff\xff\xff
```

**结束符**: 必须以 `\xff\xff\xff` (3个0xFF字节)结束

**示例**:
```
f0.txt="1000 Hz"\xff\xff\xff       // 频率反馈
v0.txt="3.50 V"\xff\xff\xff        // 幅值反馈
vp0.txt="5.00 V"\xff\xff\xff       // 峰值反馈
result.txt="Filter Type : LPF"\xff\xff\xff  // 滤波器类型
```

**HMI接收处理**:
- HMI自动解析反馈命令
- 自动更新对应控件的属性
- 无需手动编写接收代码

### 3. 完整命令序列（修正版）

#### Page 7 - 频率应用（方式2）
```c
// HMI代码
if(state1.val == 1) {
  beep 50
  printh 21                      // 命令码
  printh fs.val & 0xFF           // 频率低字节
  printh (fs.val >> 8) & 0xFF    // 频率次低字节
  printh (fs.val >> 16) & 0xFF   // 频率次高字节
  printh (fs.val >> 24) & 0xFF   // 频率高字节
  printh 00                      // 占位字节
}

// 下位机响应: f0.txt="1000 Hz"\xff\xff\xff
```

#### Page 7 - 幅值应用
```c
// HMI代码
if(state1.val == 1) {
  beep 50
  temp.val = vs.val * 100        // 电压×100
  printh 22                      // 命令码
  printh temp.val & 0xFF         // 低字节
  printh (temp.val >> 8) & 0xFF  // 次低字节
  printh (temp.val >> 16) & 0xFF // 高字节（通常为0）
  printh 00                      // 占位字节
  printh 00                      // 占位字节
  printh 00                      // 占位字节
}

// 下位机响应: v0.txt="3.50 V"\xff\xff\xff
```

#### Page 8 - 峰值应用
```c
// HMI代码
if(state1.val == 1) {
  beep 50
  temp.val = vps.val * 100       // 电压×100
  printh 23                      // 命令码
  printh temp.val & 0xFF         // 低字节
  printh (temp.val >> 8) & 0xFF  // 次低字节
  printh (temp.val >> 16) & 0xFF // 高字节
  printh 00                      // 占位字节
  printh 00                      // 占位字节
  printh 00                      // 占位字节
}

// 下位机响应: vp0.txt="5.00 V"\xff\xff\xff
```

#### Page 7/8 - Clear Buff
```c
// HMI代码
if(state1.val == 1) {
  beep 50
  printh 01 01 01 01 01 01    // 固定6字节命令
  // 显示由下位机反馈自动更新，无需手动设置
}

// 下位机响应（三条）:
// f0.txt="1000 Hz"\xff\xff\xff
// v0.txt="1.00 V"\xff\xff\xff
// vp0.txt="1.00 V"\xff\xff\xff
```

#### Page 9 - 建模命令
```c
// HMI代码
beep 50
printh F0 F0 F0 F0 F0 24    // 固定命令

// 下位机响应:
// result.txt="Filter Type : LPF"\xff\xff\xff
// （可能的类型: LPF, HPF, BPF, BSF等）
```

#### Page 9 - 启动命令
```c
// HMI代码
beep 50
printh F1 F1 F1 F1 F1 24    // 固定命令

// 下位机响应: 启动FFT循环，无直接反馈
// 通过flag=1激活main()循环中的FFT处理
```

### 4. 协议总结表（修正版）

| 命令 | 命令码 | 数据长度 | 数据类型 | 数据编码 | 总长度 | HEX示例 (1000Hz) |
|------|--------|---------|---------|---------|--------|-----------------|
| 频率设置（方式2） | 0x21 | 4字节 | uint32 | 小端序 | 6字节 | `21 E8 03 00 00 00` |
| 频率设置（方式1） | 0xF2 | 4字节 | uint32 | 小端序 | 6字节 | `F2 E8 03 00 00 00` |
| 幅值设置 | 0x22 | 3字节 | int×100 | 小端序 | 6字节 | `22 5E 01 00 ...` (3.5V) |
| 峰值设置 | 0x23 | 3字节 | int×100 | 小端序 | 6字节 | `23 F4 01 00 ...` (5.0V) |
| Clear Buff | 0x01 | 5字节 | 固定 | - | 6字节 | `01 01 01 01 01 01` |
| 建模命令 | 0xF0 | 5字节 | 固定 | 帧尾0x24 | 6字节 | `F0 F0 F0 F0 F0 24` |
| 启动命令 | 0xF1 | 5字节 | 固定 | 帧尾0x24 | 6字节 | `F1 F1 F1 F1 F1 24` |

**关键说明**:
- **所有命令固定6字节长度**
- 频率/幅值/峰值使用**二进制小端序**，不是ASCII
- 电压值需要**×100**转换为整数
- 0xF2命令未在原文档中记录，但下位机已实现
- 0xF0和0xF1**必须检查第6字节为0x24**

---

## 七、PC端移植实现要点

### 1. 串口通讯模块

**发送函数实现**:
```python
# Python示例
import serial

def send_freq_command(freq_value):
    """发送频率设置命令"""
    cmd = bytes([0x21])  # 帧头
    cmd += str(freq_value).encode('ascii')  # 频率值（ASCII）
    cmd += bytes([0x24])  # 帧尾
    serial_port.write(cmd)

def send_amp_command(amp_value):
    """发送幅值设置命令"""
    cmd = bytes([0x22])  # 帧头
    cmd += str(amp_value).encode('ascii')  # 幅值（ASCII）
    cmd += bytes([0x24])  # 帧尾
    serial_port.write(cmd)

def send_peak_command(peak_value):
    """发送峰值设置命令"""
    cmd = bytes([0x23])  # 帧头
    cmd += str(peak_value).encode('ascii')  # 峰值（ASCII）
    cmd += bytes([0x24])  # 帧尾
    serial_port.write(cmd)

def send_clear_buff():
    """发送清空缓冲命令"""
    cmd = bytes([0x01, 0x01, 0x01, 0x01, 0x01, 0x01])
    serial_port.write(cmd)

def send_modeling_command():
    """发送建模命令"""
    cmd = bytes([0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0x24])
    serial_port.write(cmd)

def send_start_command():
    """发送启动命令"""
    cmd = bytes([0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0x24])
    serial_port.write(cmd)
```

### 2. 状态管理

**关键状态变量**:
```python
class SystemState:
    def __init__(self):
        self.state1 = 0           # 运行状态 (0=停止, 1=运行)
        self.fs = 0               # 频率设置值
        self.f0 = "newtxt"        # 频率显示值
        self.vs = 0               # 幅值设置值
        self.v0 = "newtxt"        # 幅值显示值
        self.vps = 0              # 峰值设置值 (仅Page 8)
        self.vp0 = "newtxt"       # 峰值显示值 (仅Page 8)
        self.b9_color = 50712     # 建模按钮颜色
        self.b0_color = 50712     # 启动按钮颜色
```

### 3. 输入验证

**数值验证函数**:
```python
def validate_freq(value):
    """验证频率输入"""
    try:
        freq = float(value)
        if freq < 0 or freq > 100000:  # 假设范围
            return False, "频率范围: 0-100000"
        return True, freq
    except:
        return False, "请输入有效数字"

def validate_amp(value):
    """验证幅值输入"""
    try:
        amp = float(value)
        if amp < 0 or amp > 10:  # 假设范围
            return False, "幅值范围: 0-10"
        # 限制小数位数
        amp = round(amp, 2)
        return True, amp
    except:
        return False, "请输入有效数字"
```

### 4. UI反馈

**按钮颜色变化**:
```python
# RGB565转RGB888
def rgb565_to_rgb888(rgb565):
    r = ((rgb565 >> 11) & 0x1F) << 3
    g = ((rgb565 >> 5) & 0x3F) << 2
    b = (rgb565 & 0x1F) << 3
    return (r, g, b)

# 示例：50712(灰色) → (192, 192, 192)
#       33808(橙色) → (128, 132, 128)

def update_button_color(button, is_active):
    """更新按钮颜色"""
    if is_active:
        button.background_color = rgb565_to_rgb888(33808)
    else:
        button.background_color = rgb565_to_rgb888(50712)
```

## 八、事件流程图

### Page 7/8 应用按钮流程

```
用户输入频率 → 点击"应用"按钮
         ↓
检查 state1.val == 1?
         ↓ 是
播放蜂鸣器 (50ms)
         ↓
构造命令帧:
  [0x21] + ASCII(频率值) + [0x24]
         ↓
发送到串口
         ↓
更新UI显示
f0.txt = 输入值
         ↓
完成
```

### Page 9 建模按钮流程

```
用户点击"一键学习"按钮
         ↓
检查 b9.bco == 50712? (灰色=未激活)
         ↓ 是 (启动建模)
更新状态文本: "运行中.."
显示 result 控件
改变按钮颜色: 33808 (橙色)
播放蜂鸣器 (50ms)
发送: F0 F0 F0 F0 F0 24
         ↓
         ← 否 (停止建模)
更新状态文本: "待机中.."
隐藏 result 控件
恢复按钮颜色: 50712 (灰色)
播放蜂鸣器 (50ms)
发送: F0 F0 F0 F0 F0 24
         ↓
完成
```

---

## 九、移植检查清单

### 必须实现的功能
- [x] **Page 0**: 主菜单按钮跳转
- [x] **Page 7**: 频率/幅值设置与串口发送
- [x] **Page 8**: 频率/幅值/峰值设置与串口发送
- [x] **Page 9**: 一键建模与启动控制（按钮颜色切换）
- [x] **状态管理**: state1变量控制运行/停止状态
- [x] **串口协议**: 
  - 频率命令 (21 + ASCII + 24)
  - 幅值命令 (22 + ASCII + 24)
  - 峰值命令 (23 + ASCII + 24)
  - Clear Buff (01 01 01 01 01 01)
  - 建模命令 (F0 F0 F0 F0 F0 24)
  - 启动命令 (F1 F1 F1 F1 F1 24)
- [x] **按钮颜色状态**: 50712(灰色)↔33808(激活)

### 输入验证规则
- [ ] 频率范围: 待确定（根据实际硬件）
- [ ] 幅值范围: 0.00 - 待确定
- [ ] 峰值范围: 0.00 - 待确定
- [ ] 小数位数: 2位
- [ ] 负数支持: 支持（代码中有处理）

### UI交互
- [ ] 文本框键盘输入（替代原数字键盘页面）
- [ ] "+"按钮增加数值功能
- [ ] "应用"按钮发送串口命令
- [ ] "Clear Buff"按钮清空显示
- [ ] "启动/停止"按钮切换状态
- [ ] 建模/启动按钮颜色切换
- [ ] 状态文本实时更新

### 可选优化功能
- [ ] 旋转动画（Page 0的z0动画）
- [ ] 亮度调节（h0, h1变量）
- [ ] 定时器周期状态检查
- [ ] 串口数据接收与显示
- [ ] 历史数据记录
- [ ] 配置保存/加载

---

## 十、快速参考

### 串口命令速查表

| 功能 | HEX命令 | ASCII示例 | 备注 |
|------|---------|----------|------|
| 设置频率1000 | `21 31 30 30 30 24` | 0x21 "1000" 0x24 | Page 7/8 |
| 设置幅值3.5 | `22 33 2E 35 24` | 0x22 "3.5" 0x24 | Page 7/8 |
| 设置峰值5.0 | `23 35 2E 30 24` | 0x23 "5.0" 0x24 | 仅Page 8 |
| 清空缓冲 | `01 01 01 01 01 01` | - | Page 7/8 |
| 启动建模 | `F0 F0 F0 F0 F0 24` | - | Page 9 |
| 启动装置 | `F1 F1 F1 F1 F1 24` | - | Page 9 |

### 变量速查表

| 变量 | 类型 | 页面 | 说明 |
|------|------|------|------|
| state1 | int | 7/8 | 0=停止, 1=运行 |
| fs | int | 7/8 | 频率设置值 |
| f0 | str | 7/8 | 频率显示("newtxt") |
| vs | int | 7/8 | 幅值设置值 |
| v0 | str | 7/8 | 幅值显示("newtxt") |
| vps | int | 8 | 峰值设置值 |
| vp0 | str | 8 | 峰值显示("newtxt") |
| b9.bco | int | 9 | 建模按钮颜色 |
| b0.bco | int | 9 | 启动按钮颜色 |
| z0 | int | 0 | 旋转角度(0-360) |

### 颜色速查表

| 颜色值(DEC) | 颜色值(HEX) | RGB888近似 | 用途 |
|------------|------------|-----------|------|
| 50712 | 0xC618 | (192, 192, 192) | 默认灰色 |
| 33808 | 0x8410 | (128, 132, 128) | 激活橙/红色 |

---

**文档版本**: v3.0 (完整串口协议版)  
**更新内容**: 基于HMI源码的真实事件代码  
**移植平台**: PC端应用（替代陶晶驰串口屏）
