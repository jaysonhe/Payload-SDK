"""
DJI Payload SDK Python Binding

A Pythonic wrapper for DJI Payload SDK, providing easy-to-use interfaces
for drone payload development.

Quick Start:
    >>> import psdk
    >>> 
    >>> # Initialize SDK
    >>> sdk = psdk.PSDK(app_info)
    >>> sdk.initialize()
    >>> 
    >>> # Use modules
    >>> gimbal = psdk.gimbal.GimbalManager()
    >>> camera = psdk.camera.CameraManager()
    >>> flight = psdk.flight_controller.FlightController()

Modules:
    - core: Core SDK functionality and initialization
    - flight_controller: Flight control and navigation
    - gimbal: Gimbal control and management
    - camera: Camera control and image capture
    - subscription: Real-time data subscription
    - waypoint: Waypoint mission planning
    - liveview: Live video streaming
    - utils: Utility functions and helpers
"""

from ._version import __version__, __sdk_version__
from .exceptions import PSDKError, PSDKInitError, PSDKTimeoutError
from .core import PSDK, AppInfo

# 导入主要模块，支持 psdk.module_name 的使用方式
from . import flight_controller
from . import gimbal  
from . import camera
from . import subscription
from . import utils

# 便捷导入，支持直接使用类名
from .core import PSDK
from .flight_controller import FlightController
from .gimbal import GimbalManager
from .camera import CameraManager
from .subscription import DataSubscriber

# 版本信息
__all__ = [
    # 版本信息
    '__version__',
    '__sdk_version__',
    
    # 异常类
    'PSDKError',
    'PSDKInitError', 
    'PSDKTimeoutError',
    
    # 核心类
    'PSDK',
    'AppInfo',
    
    # 主要功能类
    'FlightController',
    'GimbalManager',
    'CameraManager',
    'DataSubscriber',
    
    # 模块
    'flight_controller',
    'gimbal',
    'camera', 
    'subscription',
    'utils',
]

# 自动初始化检查
def _check_environment():
    """检查运行环境和依赖"""
    import sys
    import platform
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        raise RuntimeError("PSDK Python binding requires Python 3.7 or higher")
    
    # 检查操作系统
    if platform.system() != 'Linux':
        import warnings
        warnings.warn(
            "PSDK Python binding is primarily tested on Linux. "
            "Other platforms may have limited support.",
            UserWarning
        )
    
    # 检查核心C++模块是否可用
    try:
        from . import _psdk_core  # C++绑定模块
    except ImportError as e:
        raise ImportError(
            "Failed to import PSDK core module. "
            "Please ensure the package is properly installed. "
            f"Error: {e}"
        ) from e

# 执行环境检查
_check_environment()

# 提供便捷的快速开始函数
def quick_start(app_name: str, app_id: str, app_key: str, app_license: str, 
                developer_account: str, baud_rate: str = "921600") -> PSDK:
    """
    快速开始函数，简化SDK初始化流程
    
    Args:
        app_name: 应用名称
        app_id: 应用ID  
        app_key: 应用密钥
        app_license: 应用许可证
        developer_account: 开发者账户
        baud_rate: 波特率，默认921600
        
    Returns:
        PSDK: 已初始化的SDK实例
        
    Example:
        >>> sdk = psdk.quick_start(
        ...     app_name="MyApp",
        ...     app_id="12345", 
        ...     app_key="abcdef",
        ...     app_license="license_string",
        ...     developer_account="developer@example.com"
        ... )
        >>> # SDK已就绪，可以直接使用
    """
    app_info = AppInfo(
        app_name=app_name,
        app_id=app_id,
        app_key=app_key,
        app_license=app_license,
        developer_account=developer_account,
        baud_rate=baud_rate
    )
    
    sdk = PSDK(app_info)
    sdk.initialize()
    return sdk

# 设置日志级别的便捷函数
def set_log_level(level: str = "INFO"):
    """
    设置日志级别
    
    Args:
        level: 日志级别 ("DEBUG", "INFO", "WARNING", "ERROR")
    """
    import logging
    
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO, 
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    
    if level.upper() not in level_map:
        raise ValueError(f"Invalid log level: {level}")
    
    logging.basicConfig(
        level=level_map[level.upper()],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# 版本兼容性检查
def check_compatibility():
    """检查SDK版本兼容性"""
    from .core import get_sdk_version
    
    try:
        sdk_version = get_sdk_version()
        print(f"DJI PSDK Core Version: {sdk_version}")
        print(f"Python Binding Version: {__version__}")
        return True
    except Exception as e:
        print(f"Compatibility check failed: {e}")
        return False
