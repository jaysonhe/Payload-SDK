# DJI Payload SDK Python Binding

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

一个现代化的Python绑定库，为DJI Payload SDK提供简洁、高效的Python接口。

## ✨ 特性

- 🚀 **简洁易用**: 支持 `import psdk` 直接导入，无需复杂配置
- 🔧 **一键安装**: `python setup.py install` 即可完成所有配置
- 🎯 **类型安全**: 完整的类型提示支持，提升开发体验
- ⚡ **高性能**: 基于pybind11，接近原生C++性能
- 🔄 **异步支持**: 内置async/await支持，适合现代Python开发
- 📚 **丰富示例**: 从基础到高级的完整示例代码
- 🛠️ **开发友好**: 支持开发模式安装，代码修改即时生效

## 🚀 快速开始

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 18.04+)
- **Python**: 3.7 或更高版本
- **编译器**: GCC 7+ 或 Clang 10+
- **CMake**: 3.18 或更高版本

### 一键安装

```bash
# 1. 克隆或下载 DJI Payload SDK
git clone https://github.com/dji-sdk/Payload-SDK.git
cd Payload-SDK/python-binding

# 2. 一键安装（自动处理所有依赖）
python setup.py install

# 或者使用统一构建脚本（推荐）
python scripts/build.py
```

### 验证安装

```python
import psdk

# 检查版本和兼容性
print(f"PSDK Python Binding: {psdk.__version__}")
psdk.check_compatibility()
```

## 📖 基础使用

### 快速开始示例

```python
import psdk

# 方式1: 使用快速开始函数
sdk = psdk.quick_start(
    app_name="MyDroneApp",
    app_id="your_app_id",
    app_key="your_app_key", 
    app_license="your_license",
    developer_account="your_account@example.com"
)

# 方式2: 手动配置
app_info = psdk.AppInfo(
    app_name="MyDroneApp",
    app_id="your_app_id",
    app_key="your_app_key",
    app_license="your_license", 
    developer_account="your_account@example.com"
)

sdk = psdk.PSDK(app_info)
sdk.initialize()

# 使用各种功能模块
flight_controller = psdk.FlightController()
gimbal = psdk.GimbalManager()
camera = psdk.CameraManager()
```

### 飞行控制示例

```python
import psdk
import asyncio

async def flight_demo():
    # 初始化SDK
    sdk = psdk.quick_start(...)
    
    # 获取飞行控制器
    fc = psdk.flight_controller.FlightController()
    
    # 起飞
    await fc.takeoff()
    print("无人机已起飞")
    
    # 移动到指定位置
    await fc.move_to_position(x=10, y=10, z=20)
    print("已到达目标位置")
    
    # 降落
    await fc.land()
    print("无人机已降落")

# 运行示例
asyncio.run(flight_demo())
```

### 数据订阅示例

```python
import psdk

def on_attitude_data(data):
    print(f"姿态数据: roll={data.roll}, pitch={data.pitch}, yaw={data.yaw}")

def on_position_data(data):
    print(f"位置数据: lat={data.latitude}, lon={data.longitude}, alt={data.altitude}")

# 创建数据订阅器
subscriber = psdk.subscription.DataSubscriber()

# 订阅数据
subscriber.subscribe_attitude(callback=on_attitude_data, frequency=10)
subscriber.subscribe_position(callback=on_position_data, frequency=5)

# 开始订阅
subscriber.start()
```

### 云台控制示例

```python
import psdk

# 获取云台管理器
gimbal = psdk.gimbal.GimbalManager()

# 设置云台角度
gimbal.set_angle(pitch=-30, yaw=45, roll=0)

# 云台复位
gimbal.reset()

# 设置云台模式
gimbal.set_mode(psdk.gimbal.GimbalMode.FREE)
```

## 🛠️ 开发模式

对于开发者，推荐使用开发模式安装：

```bash
# 开发模式安装
python setup.py develop

# 或使用构建脚本
python scripts/build.py --dev

# 运行测试
python scripts/build.py --test

# 构建文档
python scripts/build.py --docs
```

开发模式的优势：
- 代码修改后无需重新安装
- 支持断点调试
- 实时错误检查

## 📁 项目结构

```
python-binding/
├── psdk/                      # Python包源码
│   ├── __init__.py           # 主入口，支持 import psdk
│   ├── core.py               # 核心功能
│   ├── flight_controller/    # 飞行控制模块
│   ├── gimbal/              # 云台控制模块
│   ├── camera/              # 相机控制模块
│   └── subscription/        # 数据订阅模块
├── src/                     # C++绑定源码
├── examples/                # 示例代码
├── tests/                   # 测试代码
├── docs/                    # 文档
├── scripts/                 # 构建脚本
├── setup.py                 # 安装脚本
├── pyproject.toml          # 项目配置
└── README.md               # 本文档
```

## 📚 示例代码

我们提供了丰富的示例代码，涵盖从基础到高级的各种使用场景：

### 基础示例
- [基础设置](examples/quick_start/01_basic_setup.py) - SDK初始化和基本配置
- [飞行控制](examples/quick_start/02_flight_control.py) - 基础飞行操作
- [数据订阅](examples/quick_start/03_data_subscription.py) - 实时数据获取

### 高级示例
- [航点任务](examples/advanced/waypoint_mission.py) - 自动航点飞行
- [相机控制](examples/advanced/camera_control.py) - 相机参数设置和拍摄
- [实时处理](examples/advanced/real_time_processing.py) - 实时数据处理

### 集成示例
- [OpenCV集成](examples/integration/opencv_demo.py) - 图像处理集成
- [ROS桥接](examples/integration/ros_bridge.py) - ROS系统集成
- [异步编程](examples/integration/asyncio_demo.py) - 异步编程模式

## 🔧 高级配置

### 环境变量

```bash
# 指定PSDK根目录（通常自动检测）
export PSDK_ROOT=/path/to/Payload-SDK

# 设置构建并行数
export PARALLEL_JOBS=4

# 启用调试构建
export DEBUG_BUILD=1

# 自定义CMake参数
export CMAKE_ARGS="-DCMAKE_BUILD_TYPE=Release"
```

### 自定义构建

```bash
# 清理后重新构建
python scripts/build.py --clean

# 仅检查环境
python scripts/build.py --check-only

# 构建并运行测试
python scripts/build.py --test

# 详细输出
python scripts/build.py --verbose
```

## 🐛 故障排除

### 常见问题

#### 1. 导入错误
```
ImportError: Failed to import PSDK core module
```
**解决方案**:
- 确保已正确安装：`python setup.py install`
- 检查Python版本：需要3.7+
- 验证PSDK库路径：检查 `psdk_lib` 目录

#### 2. 编译错误
```
CMake Error: Could not find CMAKE_C_COMPILER
```
**解决方案**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential cmake

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install cmake
```

#### 3. 库依赖错误
```
error while loading shared libraries: libusb-1.0.so.0
```
**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install libusb-1.0-0-dev libopus-dev

# CentOS/RHEL
sudo yum install libusb1-devel opus-devel
```

#### 4. 权限错误
```
Permission denied: '/usr/local/lib/python3.x/site-packages/'
```
**解决方案**:
```bash
# 使用用户安装
python setup.py install --user

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate
python setup.py install
```

### 获取帮助

如果遇到问题，可以：

1. **检查环境**: `python scripts/build.py --check-only`
2. **查看日志**: 使用 `--verbose` 参数获取详细输出
3. **重新安装**: `python scripts/build.py --clean`
4. **提交Issue**: [GitHub Issues](https://github.com/dji-sdk/Payload-SDK/issues)

## 📄 API文档

完整的API文档请参考：
- [在线文档](https://developer.dji.com/payload-sdk/)
- [本地文档](docs/build/html/index.html) (运行 `python scripts/build.py --docs` 生成)

## 🤝 贡献

欢迎贡献代码！请参考：
- [贡献指南](CONTRIBUTING.md)
- [代码规范](docs/code_style.md)
- [开发环境设置](docs/development.md)

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [DJI Developer](https://developer.dji.com/)
- [Payload SDK 文档](https://developer.dji.com/payload-sdk/)
- [GitHub 仓库](https://github.com/dji-sdk/Payload-SDK)
- [技术支持](https://djisdksupport.zendesk.com/)

---

**注意**: 本Python绑定库是对DJI Payload SDK的封装，使用前请确保已获得相应的开发许可和设备授权。
