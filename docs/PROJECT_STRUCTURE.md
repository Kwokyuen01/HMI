# SA 串口上位机 - 项目结构说明

## 📁 文件组织

```
HMI/
├── main.py                   # 主程序入口，窗口管理和页面导航
├── config.py                 # 全局配置（串口、颜色、字体）
├── serial_comm.py            # 串口通信层（协议编码/解码）
│
├── ui_main_menu.py           # 主菜单页面（Page 0）
├── ui_dual_param.py          # 双参数控制（Page 7）
├── ui_triple_param.py        # 三参数控制（Page 8）
├── ui_modeling.py            # 系统建模（Page 9）
│
├── requirements.txt          # Python依赖包
├── README.md                 # 使用说明
└── PROJECT_STRUCTURE.md      # 本文件
```

## 🎨 UI模块说明

### `ui_main_menu.py` - 主菜单
- **类名**: `MainMenu`
- **功能**: 
  - 程序入口界面
  - 旋转动画效果
  - 导航到各功能页面
  - RESET和退出功能
- **特色**: 
  - 6个功能按钮
  - 自动旋转动画（模拟HMI的z0变量）
  - 状态栏显示

### `ui_dual_param.py` - 双参数控制
- **类名**: `DualParamControl`
- **对应**: 原HMI的Page 7
- **参数**: 
  - 频率设置（Hz）
  - 幅值设置（V）
- **命令**:
  - 0x21: 频率设置
  - 0x22: 幅值设置
  - 0x01: Clear Buff
- **特色**:
  - 实时显示当前值
  - 自动接收下位机反馈
  - 启动/停止状态切换

### `ui_triple_param.py` - 三参数控制
- **类名**: `TripleParamControl`
- **对应**: 原HMI的Page 8
- **参数**: 
  - 频率设置（Hz）
  - 幅值设置（V）
  - 峰值设置（V）
- **命令**:
  - 0x21: 频率设置
  - 0x22: 幅值设置
  - 0x23: 峰值设置
  - 0x01: Clear Buff
- **特色**:
  - 三列布局
  - 接收状态提示
  - 完整的反馈显示

### `ui_modeling.py` - 系统建模
- **类名**: `SystemModeling`
- **对应**: 原HMI的Page 9
- **功能**:
  - 第一部分：一键学习（频率扫描）
  - 第二部分：启动探究装置（FFT分析）
- **命令**:
  - 0xF0: 建模命令（扫描200Hz-500kHz）
  - 0xF1: 启动命令（FFT循环）
- **特色**:
  - 大按钮设计
  - 颜色状态指示（灰色↔橙色）
  - 结果显示区域

## 🔌 串口通信层

### `serial_comm.py`
- **类名**: `SerialComm`
- **功能**:
  - 串口连接/断开
  - 异步接收（独立线程）
  - 协议编码（二进制小端序）
  - 反馈解析（自动更新UI）

**主要方法**:
```python
connect()                           # 连接串口
disconnect()                        # 断开串口
send_freq_cmd(freq, mode)          # 发送频率命令
send_voltage_cmd(voltage, type)    # 发送电压命令
send_clear_buff()                   # 发送清空命令
send_modeling_cmd()                 # 发送建模命令
send_start_cmd()                    # 发送启动命令
```

## ⚙️ 配置文件

### `config.py`
- 串口配置: 端口号、波特率、超时
- 窗口配置: 尺寸、标题
- 颜色配置: 按钮、文本、背景
- 字体配置: 标题、标签、按钮
- 默认值: 频率、电压

## 🎨 UI设计规范

### 颜色方案
- **蓝色按钮** (#2196F3): 增加/调整操作
- **绿色按钮** (#4CAF50): 应用/启动操作
- **橙色按钮** (#FF9800): 警告/清空操作
- **红色按钮** (#F44336): 停止/退出操作
- **灰色按钮** (#757575): 返回/取消操作
- **浅灰按钮** (#C0C0C0): 默认状态大按钮

### 按钮属性
- `fg='white'`: 白色字体确保可读性
- `activebackground`: 鼠标悬停颜色
- `activeforeground='white'`: 悬停时保持白色字体
- `cursor='hand2'`: 鼠标指针变为手型
- `font=('Arial', 10-14, 'bold')`: 加粗字体

## 🔄 页面导航

### 导航ID对应关系
```
0 → MainMenu           (主菜单)
7 → DualParamControl   (双参数)
8 → TripleParamControl (三参数)
9 → SystemModeling     (建模)
```

### 导航方式
1. 主菜单按钮点击
2. 菜单栏选择
3. 页面底部"返回"按钮

## 📡 通信协议

### 数据编码
- **固定长度**: 所有命令6字节
- **字节序**: 小端序（低位在前）
- **电压编码**: 实际值×100
- **频率编码**: 直接32位整数

### 反馈格式
```
控件名.属性="值"\xff\xff\xff
```

示例:
```
f0.txt="1000 Hz"\xff\xff\xff
v0.txt="3.50 V"\xff\xff\xff
result.txt="Filter Type : LPF"\xff\xff\xff
```

## 🚀 运行流程

1. **启动** → `main.py`
2. **初始化** → 创建 `HMIApplication` 实例
3. **串口连接** → 弹出连接对话框
4. **创建页面** → 实例化所有UI模块
5. **显示主菜单** → `navigate(0)`
6. **用户操作** → 页面导航和命令发送
7. **接收反馈** → 异步线程处理
8. **更新UI** → 回调函数更新显示

## 🛠️ 开发建议

### 添加新页面
1. 创建新的UI模块文件（如 `ui_new_page.py`）
2. 继承 `tk.Frame` 类
3. 在 `main.py` 中导入
4. 在 `create_pages()` 中实例化
5. 分配导航ID

### 添加新命令
1. 在 `serial_comm.py` 中添加编码函数
2. 在对应UI模块中添加按钮
3. 绑定命令发送函数
4. 处理反馈回调

### 调试技巧
- 查看控制台输出（`→` 发送，`←` 接收）
- 使用离线模式测试UI
- 检查串口权限（Linux/Mac）
- 验证波特率匹配

## 📚 参考文档

- `Apply_HMI_Design_Documentation.md` - 完整HMI设计规范
- `README.md` - 使用说明和协议详解
- `SA.sdk/FFTCTR/src/ISR.c` - 下位机协议实现

---

**版本**: v2.0 (重构版)  
**更新内容**: 
- 重命名文件为规范命名
- 优化按钮颜色和可读性
- 移除启动脚本，简化运行方式
- 完善类名和模块命名

