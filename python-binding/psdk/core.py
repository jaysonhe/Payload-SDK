"""
DJI PSDK Core Module

This module provides the core functionality for DJI Payload SDK Python binding,
including SDK initialization, configuration management, and basic operations.
"""

import logging
import threading
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

# 导入C++绑定模块（将由pybind11生成）
try:
    from . import _psdk_core
except ImportError:
    # 开发时的占位符
    _psdk_core = None

from .exceptions import PSDKError, PSDKInitError, PSDKTimeoutError

# 配置日志
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """平台类型枚举"""
    LINUX = "linux"
    RTOS = "rtos"
    UNKNOWN = "unknown"

class AppType(Enum):
    """应用类型枚举"""
    BIG_SCREEN = 1
    MOBILE = 2

@dataclass
class AppInfo:
    """应用信息配置类"""
    app_name: str
    app_id: str
    app_key: str
    app_license: str
    developer_account: str
    baud_rate: str = "921600"
    app_type: AppType = AppType.BIG_SCREEN
    
    def __post_init__(self):
        """验证配置参数"""
        if not all([self.app_name, self.app_id, self.app_key, 
                   self.app_license, self.developer_account]):
            raise ValueError("All app info fields are required")
        
        if self.baud_rate not in ["115200", "230400", "460800", "921600"]:
            raise ValueError(f"Invalid baud rate: {self.baud_rate}")

class PSDK:
    """
    DJI Payload SDK 主类
    
    这是Python绑定的核心类，负责SDK的初始化、配置和生命周期管理。
    
    Example:
        >>> app_info = AppInfo(
        ...     app_name="MyApp",
        ...     app_id="12345",
        ...     app_key="abcdef",
        ...     app_license="license_string",
        ...     developer_account="developer@example.com"
        ... )
        >>> sdk = PSDK(app_info)
        >>> sdk.initialize()
        >>> # 使用SDK功能...
        >>> sdk.cleanup()
    """
    
    def __init__(self, app_info: AppInfo):
        """
        初始化PSDK实例
        
        Args:
            app_info: 应用配置信息
        """
        self.app_info = app_info
        self._initialized = False
        self._lock = threading.Lock()
        self._callbacks: Dict[str, Callable] = {}
        
        logger.info(f"Created PSDK instance for app: {app_info.app_name}")
    
    def initialize(self) -> None:
        """
        初始化SDK
        
        Raises:
            PSDKInitError: 初始化失败时抛出
        """
        with self._lock:
            if self._initialized:
                logger.warning("SDK already initialized")
                return
            
            try:
                logger.info("Initializing DJI Payload SDK...")
                
                if _psdk_core is None:
                    raise PSDKInitError("Core module not available")
                
                # 调用C++层初始化
                result = _psdk_core.initialize(
                    app_name=self.app_info.app_name,
                    app_id=self.app_info.app_id,
                    app_key=self.app_info.app_key,
                    app_license=self.app_info.app_license,
                    developer_account=self.app_info.developer_account,
                    baud_rate=self.app_info.baud_rate,
                    app_type=self.app_info.app_type.value
                )
                
                if not result:
                    raise PSDKInitError("SDK initialization failed")
                
                self._initialized = True
                logger.info("SDK initialized successfully")
                
            except Exception as e:
                logger.error(f"SDK initialization failed: {e}")
                raise PSDKInitError(f"Failed to initialize SDK: {e}") from e
    
    def cleanup(self) -> None:
        """清理SDK资源"""
        with self._lock:
            if not self._initialized:
                return
            
            try:
                logger.info("Cleaning up SDK resources...")
                
                if _psdk_core:
                    _psdk_core.cleanup()
                
                self._initialized = False
                self._callbacks.clear()
                
                logger.info("SDK cleanup completed")
                
            except Exception as e:
                logger.error(f"SDK cleanup failed: {e}")
    
    def is_initialized(self) -> bool:
        """检查SDK是否已初始化"""
        return self._initialized
    
    def get_sdk_version(self) -> str:
        """获取SDK版本信息"""
        if _psdk_core:
            return _psdk_core.get_version()
        return "Unknown"
    
    def get_platform_type(self) -> PlatformType:
        """获取平台类型"""
        if _psdk_core:
            platform_str = _psdk_core.get_platform_type()
            try:
                return PlatformType(platform_str.lower())
            except ValueError:
                return PlatformType.UNKNOWN
        return PlatformType.UNKNOWN
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        注册事件回调
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        self._callbacks[event_type] = callback
        logger.debug(f"Registered callback for event: {event_type}")
    
    def unregister_callback(self, event_type: str) -> None:
        """
        取消注册事件回调
        
        Args:
            event_type: 事件类型
        """
        if event_type in self._callbacks:
            del self._callbacks[event_type]
            logger.debug(f"Unregistered callback for event: {event_type}")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, '_initialized') and self._initialized:
            self.cleanup()

# 全局SDK实例（单例模式）
_global_sdk_instance: Optional[PSDK] = None
_global_sdk_lock = threading.Lock()

def get_global_sdk() -> Optional[PSDK]:
    """获取全局SDK实例"""
    return _global_sdk_instance

def set_global_sdk(sdk: PSDK) -> None:
    """设置全局SDK实例"""
    global _global_sdk_instance
    with _global_sdk_lock:
        _global_sdk_instance = sdk

def get_sdk_version() -> str:
    """获取SDK版本（便捷函数）"""
    if _psdk_core:
        return _psdk_core.get_version()
    return "Unknown"

def get_platform_type() -> PlatformType:
    """获取平台类型（便捷函数）"""
    if _psdk_core:
        platform_str = _psdk_core.get_platform_type()
        try:
            return PlatformType(platform_str.lower())
        except ValueError:
            return PlatformType.UNKNOWN
    return PlatformType.UNKNOWN

# 便捷的初始化函数
def initialize_sdk(app_info: AppInfo) -> PSDK:
    """
    便捷的SDK初始化函数
    
    Args:
        app_info: 应用配置信息
        
    Returns:
        PSDK: 已初始化的SDK实例
    """
    sdk = PSDK(app_info)
    sdk.initialize()
    set_global_sdk(sdk)
    return sdk
