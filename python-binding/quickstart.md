# DJI Payload SDK Python Binding 快速开始指南

欢迎使用DJI Payload SDK Python绑定！本指南将帮助您在几分钟内完成从安装到运行第一个程序的完整流程。

## 📋 目录

- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [验证安装](#验证安装)
- [第一个程序](#第一个程序)
- [常用功能示例](#常用功能示例)
- [故障排除](#故障排除)
- [下一步](#下一步)

## 🔧 系统要求

在开始之前，请确保您的系统满足以下要求：

### 必需条件
- **操作系统**: Linux (推荐 Ubuntu 18.04 或更高版本)
- **Python**: 3.7 或更高版本
- **编译器**: GCC 7+ 或 Clang 10+
- **CMake**: 3.18 或更高版本

### 检查系统环境

```bash
# 检查Python版本
python3 --version
# 输出示例: Python 3.8.10

# 检查CMake版本
cmake --version
# 输出示例: cmake version 3.20.1

# 检查GCC版本
gcc --version
# 输出示例: gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0
```

### 安装系统依赖

如果缺少必要的工具，请根据您的系统安装：

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y build-essential cmake
sudo apt install -y libusb-1.0-0-dev libopus-dev  # 可选，用于USB和音频功能
```

#### CentOS/RHEL
```bash
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3 python3-pip python3-devel
sudo yum install -y cmake
sudo yum install -y libusb1-devel opus-devel  # 可选
```

## 🚀 快速安装

### 步骤1: 获取源码

```bash
# 克隆DJI Payload SDK仓库
git clone https://github.com/dji-sdk/Payload-SDK.git

# 进入Python绑定目录
cd Payload-SDK/python-binding
```

### 步骤2: 一键安装

我们提供了三种安装方式，推荐使用方式1：

#### 方式1: 使用统一构建脚本（推荐）

```bash
# 一键安装，自动处理所有依赖和配置
python3 scripts/build.py

# 如果需要详细输出，可以使用verbose模式
python3 scripts/build.py --verbose
```

#### 方式2: 使用传统setup.py

```bash
# 安装Python依赖
pip3 install -r requirements.txt

# 构建和安装
python3 setup.py install
```

#### 方式3: 开发模式安装（适合开发者）

```bash
# 开发模式安装，代码修改后无需重新安装
python3 scripts/build.py --dev

# 或者
python3 setup.py develop
```

### 安装过程说明

安装过程中，脚本会自动执行以下操作：

1. ✅ **环境检查**: 验证Python版本、CMake、编译器等
2. ✅ **依赖安装**: 自动安装pybind11、numpy等Python依赖
3. ✅ **路径检测**: 自动查找DJI PSDK根目录和库文件
4. ✅ **平台适配**: 根据系统架构选择合适的库文件
5. ✅ **编译构建**: 使用CMake和pybind11编译C++绑定
6. ✅ **安装验证**: 自动验证安装是否成功

## ✅ 验证安装

安装完成后，让我们验证一切是否正常工作：

### 基础验证

```bash
# 测试导入
python3 -c "import psdk; print('✅ PSDK导入成功')"

# 检查版本
python3 -c "import psdk; print(f'PSDK版本: {psdk.__version__}')"

# 运行兼容性检查
python3 -c "import psdk; psdk.check_compatibility()"
```

### 详细验证

创建一个测试文件 `test_installation.py`：

```python
#!/usr/bin/env python3
"""安装验证脚本"""

import psdk

def main():
    print("🔍 DJI PSDK Python绑定安装验证")
    print("=" * 50)
    
    # 检查版本信息
    print(f"✅ Python绑定版本: {psdk.__version__}")
    
    try:
        # 检查核心SDK版本
        sdk_version = psdk.get_sdk_version()
        print(f"✅ 核心SDK版本: {sdk_version}")
    except Exception as e:
        print(f"⚠️  无法获取SDK版本: {e}")
    
    try:
        # 检查平台类型
        platform = psdk.get_platform_type()
        print(f"✅ 平台类型: {platform}")
    except Exception as e:
        print(f"⚠️  无法获取平台类型: {e}")
    
    # 检查模块可用性
    modules = ['core', 'flight_controller', 'gimbal', 'camera', 'subscription']
    for module in modules:
        try:
            getattr(psdk, module)
            print(f"✅ 模块 {module} 可用")
        except AttributeError:
            print(f"⚠️  模块 {module} 不可用")
    
    print("\n🎉 安装验证完成！")

if __name__ == "__main__":
    main()
```

运行验证脚本：

```bash
python3 test_installation.py
```

## 🎯 第一个程序

现在让我们编写第一个使用DJI PSDK的Python程序！

### 创建应用配置

首先，您需要在DJI开发者网站注册应用并获取必要的凭证。然后创建配置文件 `my_first_app.py`：

```python
#!/usr/bin/env python3
"""我的第一个DJI PSDK Python程序"""

import psdk
import time

def main():
    print("🚁 欢迎使用DJI Payload SDK Python绑定！")
    
    # 配置应用信息（请替换为您的实际信息）
    app_info = psdk.AppInfo(
        app_name="MyFirstApp",
        app_id="your_app_id_here",           # 替换为您的App ID
        app_key="your_app_key_here",         # 替换为您的App Key
        app_license="your_app_license_here", # 替换为您的App License
        developer_account="your_email@example.com",  # 替换为您的开发者账户
        baud_rate="921600"
    )
    
    try:
        # 方式1: 使用快速开始函数
        print("📡 正在初始化SDK...")
        sdk = psdk.quick_start(
            app_name=app_info.app_name,
            app_id=app_info.app_id,
            app_key=app_info.app_key,
            app_license=app_info.app_license,
            developer_account=app_info.developer_account
        )
        
        print("✅ SDK初始化成功！")
        
        # 获取基本信息
        print(f"📊 SDK版本: {sdk.get_sdk_version()}")
        print(f"🖥️  平台类型: {sdk.get_platform_type()}")
        
        # 简单的功能演示
        print("\n🎮 功能模块演示:")
        
        # 飞行控制器
        try:
            flight_controller = psdk.FlightController()
            print("✅ 飞行控制器模块已加载")
        except Exception as e:
            print(f"⚠️  飞行控制器模块加载失败: {e}")
        
        # 云台管理器
        try:
            gimbal = psdk.GimbalManager()
            print("✅ 云台管理器模块已加载")
        except Exception as e:
            print(f"⚠️  云台管理器模块加载失败: {e}")
        
        # 相机管理器
        try:
            camera = psdk.CameraManager()
            print("✅ 相机管理器模块已加载")
        except Exception as e:
            print(f"⚠️  相机管理器模块加载失败: {e}")
        
        print("\n🎉 第一个程序运行成功！")
        print("💡 提示: 要使用具体功能，请确保无人机已连接并且应用已获得相应权限。")
        
    except psdk.PSDKInitError as e:
        print(f"❌ SDK初始化失败: {e}")
        print("💡 请检查应用配置信息是否正确，以及设备连接状态。")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
    
    finally:
        print("\n👋 程序结束")

if __name__ == "__main__":
    main()
```

### 运行第一个程序

```bash
python3 my_first_app.py
```

**注意**: 在实际运行前，请确保：
1. 已在DJI开发者网站注册应用并获得有效的App ID、App Key和App License
2. 将代码中的占位符替换为您的实际凭证
3. 如果要测试硬件功能，请确保设备已正确连接

## 📚 常用功能示例

### 数据订阅示例

```python
#!/usr/bin/env python3
"""数据订阅示例"""

import psdk
import time

def attitude_callback(data):
    """姿态数据回调函数"""
    print(f"姿态数据 - Roll: {data.roll:.2f}°, Pitch: {data.pitch:.2f}°, Yaw: {data.yaw:.2f}°")

def position_callback(data):
    """位置数据回调函数"""
    print(f"位置数据 - 纬度: {data.latitude:.6f}, 经度: {data.longitude:.6f}, 高度: {data.altitude:.2f}m")

def main():
    # 初始化SDK
    sdk = psdk.quick_start(
        app_name="DataSubscriptionDemo",
        app_id="your_app_id",
        app_key="your_app_key",
        app_license="your_license",
        developer_account="your_account@example.com"
    )
    
    try:
        # 创建数据订阅器
        subscriber = psdk.subscription.DataSubscriber()
        
        # 订阅姿态数据（10Hz）
        subscriber.subscribe_attitude(callback=attitude_callback, frequency=10)
        
        # 订阅位置数据（5Hz）
        subscriber.subscribe_position(callback=position_callback, frequency=5)
        
        # 开始订阅
        subscriber.start()
        print("📡 数据订阅已开始，按Ctrl+C停止...")
        
        # 运行30秒
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        # 停止订阅
        if 'subscriber' in locals():
            subscriber.stop()
        print("👋 数据订阅已停止")

if __name__ == "__main__":
    main()
```

### 云台控制示例

```python
#!/usr/bin/env python3
"""云台控制示例"""

import psdk
import time

def main():
    # 初始化SDK
    sdk = psdk.quick_start(
        app_name="GimbalControlDemo",
        app_id="your_app_id",
        app_key="your_app_key", 
        app_license="your_license",
        developer_account="your_account@example.com"
    )
    
    try:
        # 获取云台管理器
        gimbal = psdk.gimbal.GimbalManager()
        
        print("🎥 云台控制演示开始...")
        
        # 云台复位
        print("🔄 云台复位中...")
        gimbal.reset()
        time.sleep(3)
        
        # 设置云台角度
        print("📐 设置云台角度: Pitch=-30°, Yaw=45°")
        gimbal.set_angle(pitch=-30, yaw=45, roll=0)
        time.sleep(3)
        
        # 设置云台模式
        print("🎮 设置云台为自由模式")
        gimbal.set_mode(psdk.gimbal.GimbalMode.FREE)
        time.sleep(2)
        
        # 回到中心位置
        print("🎯 云台回中")
        gimbal.set_angle(pitch=0, yaw=0, roll=0)
        time.sleep(3)
        
        print("✅ 云台控制演示完成")
        
    except Exception as e:
        print(f"❌ 云台控制错误: {e}")

if __name__ == "__main__":
    main()
```

### 异步编程示例

```python
#!/usr/bin/env python3
"""异步编程示例"""

import psdk
import asyncio

async def flight_demo():
    """异步飞行演示"""
    try:
        # 初始化SDK
        sdk = psdk.quick_start(
            app_name="AsyncFlightDemo",
            app_id="your_app_id",
            app_key="your_app_key",
            app_license="your_license", 
            developer_account="your_account@example.com"
        )
        
        # 获取飞行控制器
        fc = psdk.flight_controller.FlightController()
        
        print("🚁 异步飞行演示开始...")
        
        # 起飞
        print("🛫 起飞中...")
        await fc.takeoff()
        print("✅ 起飞完成")
        
        # 移动到指定位置
        print("📍 移动到目标位置...")
        await fc.move_to_position(x=10, y=10, z=20)
        print("✅ 已到达目标位置")
        
        # 悬停5秒
        print("⏸️  悬停5秒...")
        await asyncio.sleep(5)
        
        # 降落
        print("🛬 降落中...")
        await fc.land()
        print("✅ 降落完成")
        
        print("🎉 异步飞行演示完成")
        
    except Exception as e:
        print(f"❌ 飞行演示错误: {e}")

def main():
    # 运行异步函数
    asyncio.run(flight_demo())

if __name__ == "__main__":
    main()
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 导入错误

**问题**: `ImportError: Failed to import PSDK core module`

**解决方案**:
```bash
# 检查安装是否成功
python3 -c "import psdk"

# 如果失败，重新安装
cd Payload-SDK/python-binding
python3 scripts/build.py --clean
python3 scripts/build.py
```

#### 2. 编译错误

**问题**: `CMake Error: Could not find CMAKE_C_COMPILER`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install build-essential cmake

# CentOS/RHEL  
sudo yum groupinstall "Development Tools"
sudo yum install cmake
```

#### 3. 库依赖错误

**问题**: `error while loading shared libraries: libusb-1.0.so.0`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install libusb-1.0-0-dev libopus-dev

# CentOS/RHEL
sudo yum install libusb1-devel opus-devel
```

#### 4. 权限错误

**问题**: `Permission denied: '/usr/local/lib/python3.x/site-packages/'`

**解决方案**:
```bash
# 方案1: 使用用户安装
python3 setup.py install --user

# 方案2: 使用虚拟环境（推荐）
python3 -m venv psdk_env
source psdk_env/bin/activate
python3 setup.py install
```

#### 5. 应用配置错误

**问题**: `PSDKInitError: SDK initialization failed`

**解决方案**:
1. 检查App ID、App Key、App License是否正确
2. 确认开发者账户邮箱正确
3. 验证应用是否已在DJI开发者网站激活
4. 检查设备连接状态

### 获取详细错误信息

如果遇到问题，可以启用详细日志：

```python
import psdk
import logging

# 启用详细日志
psdk.set_log_level("DEBUG")
logging.basicConfig(level=logging.DEBUG)

# 然后运行您的代码
```

### 环境检查工具

使用内置的环境检查工具：

```bash
# 仅检查环境，不进行安装
python3 scripts/build.py --check-only

# 详细输出模式
python3 scripts/build.py --check-only --verbose
```

## 🎓 下一步

恭喜！您已经成功完成了DJI PSDK Python绑定的快速开始。接下来您可以：

### 1. 深入学习

- 📖 **阅读完整文档**: 查看 `docs/` 目录下的详细API文档
- 🏗️ **了解架构**: 阅读 `Arch.md` 了解完整的架构设计
- 📝 **查看示例**: 浏览 `examples/` 目录下的丰富示例代码

### 2. 实践项目

- 🚁 **基础飞行控制**: 实现自动起飞、悬停、降落
- 📷 **相机控制**: 实现拍照、录像、参数调节
- 🎯 **航点任务**: 创建自动航点飞行任务
- 📡 **数据处理**: 实时处理飞行数据和传感器数据

### 3. 高级功能

- 🔄 **异步编程**: 使用async/await实现高效的异步操作
- 🖼️ **图像处理**: 集成OpenCV进行实时图像处理
- 🤖 **AI集成**: 结合机器学习框架实现智能功能
- 🌐 **网络通信**: 实现远程控制和数据传输

### 4. 开发贡献

- 🐛 **报告问题**: 在GitHub上提交issue
- 💡 **功能建议**: 提出新功能需求
- 🔧 **代码贡献**: 提交pull request
- 📚 **文档改进**: 帮助完善文档

### 5. 社区资源

- 🌐 **官方网站**: [DJI Developer](https://developer.dji.com/)
- 📖 **技术文档**: [Payload SDK文档](https://developer.dji.com/payload-sdk/)
- 💬 **技术支持**: [DJI SDK支持](https://djisdksupport.zendesk.com/)
- 🐙 **GitHub仓库**: [Payload-SDK](https://github.com/dji-sdk/Payload-SDK)

## 📞 获取帮助

如果您在使用过程中遇到任何问题：

1. **查看文档**: 首先查看相关文档和示例代码
2. **搜索问题**: 在GitHub Issues中搜索类似问题
3. **提交Issue**: 如果问题未解决，请提交详细的issue
4. **联系支持**: 通过官方技术支持渠道获取帮助

---

**祝您使用愉快！🎉**

开始您的DJI无人机开发之旅吧！如果您创建了有趣的项目，欢迎与社区分享。
