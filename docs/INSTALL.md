# 安装和运行指南

## 📦 安装依赖

```bash
cd /Users/kwokyuen/Downloads/SA/SA/HMI
pip3 install -r requirements.txt
```

或者单独安装：

```bash
pip3 install pyserial ttkbootstrap
```

## 🚀 运行程序

```bash
python3 main.py
```

## 🎨 ttkbootstrap 主题

程序默认使用 **flatly** 主题（现代、简洁）

### 可用主题列表

在 `main.py` 中修改主题：

```python
root = ttk.Window(
    themename="flatly",  # 修改这里
)
```

**亮色主题**:
- `flatly` ⭐ 推荐 - 扁平化设计，现代简洁
- `cosmo` - Bootstrap风格
- `litera` - 清爽简洁
- `minty` - 薄荷绿色调
- `pulse` - 紫色主题
- `sandstone` - 沙色调
- `yeti` - 蓝白配色

**暗色主题**:
- `darkly` - 暗黑模式
- `cyborg` - 科技感暗黑
- `superhero` - 超级英雄风格
- `solar` - 太阳能色调

## 🎯 按钮样式 (bootstyle)

### 主要样式
- `primary` - 蓝色（主要操作）
- `success` - 绿色（成功/启动）
- `info` - 青色（信息）
- `warning` - 橙色（警告）
- `danger` - 红色（危险/停止）
- `secondary` - 灰色（次要操作）

### 样式变体
- `primary-outline` - 空心按钮
- `success-link` - 链接样式

## 🖼️ 界面效果

### 主菜单
- 6个大按钮垂直排列
- 不同颜色表示不同功能
- 现代化扁平设计

### 控制页面
- 蓝色边框按钮（+100, +0.5）
- 绿色实心按钮（应用）
- 红色按钮（停止）
- 橙色按钮（Clear Buff）
- 灰色按钮（返回）

## 🔧 问题排查

### 1. ttkbootstrap 安装失败

```bash
# 确保pip是最新版本
pip3 install --upgrade pip

# 重新安装
pip3 install ttkbootstrap --upgrade
```

### 2. 主题不生效

检查 main.py 中是否正确使用：
```python
import ttkbootstrap as ttk
root = ttk.Window(themename="flatly")
```

### 3. 按钮样式不显示

确保使用 `bootstyle` 参数：
```python
ttk.Button(text="按钮", bootstyle="success")
```

## 📚 更多主题预览

访问 ttkbootstrap 官方文档查看所有主题效果：
https://ttkbootstrap.readthedocs.io/

