# 代码规范和规则

## 基础代码规范

### 1. PEP 8 基础规范（适配嵌入式环境）

```python
# 行长度：嵌入式环境建议更严格
MAX_LINE_LENGTH = 79  # 标准PEP 8
# 或者更严格的限制
MAX_LINE_LENGTH = 72  # 嵌入式环境推荐

# 缩进：使用4个空格
def embedded_function():
    if condition:
        process_data()
        return result

# 命名规范
class SensorManager:  # 类名：CapWords
    def read_temperature(self):  # 方法名：snake_case
        sensor_value = 0  # 变量名：snake_case
        MAX_RETRIES = 3   # 常量：UPPER_CASE

# 导入规范
# 标准库导入
import os
import sys
import time
from typing import Optional, List, Dict

# 第三方库导入
import numpy as np

# 本地模块导入
from .sensors import TemperatureSensor
from .utils import validate_range

# 避免使用 import *（嵌入式环境特别重要）
# from module import *  # ❌ 不推荐，增加内存占用 
 
# 内存管理规范
# ✅ 推荐：使用生成器减少内存占用
def read_sensor_data_generator(sensor_count: int):
    """使用生成器逐个产生数据，避免一次性加载大量数据"""
    for i in range(sensor_count):
        yield read_single_sensor(i)

# ❌ 不推荐：一次性创建大列表
def read_all_sensor_data(sensor_count: int):
    return [read_single_sensor(i) for i in range(sensor_count)]

# ✅ 推荐：及时释放大对象
def process_large_data():
    large_data = create_large_buffer()
    try:
        result = process(large_data)
        return result
    finally:
        del large_data  # 显式删除大对象

# ✅ 推荐：使用上下文管理器
class ResourceManager:
    def __enter__(self):
        self.resource = acquire_resource()
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        release_resource(self.resource)

# 性能优化规范

# ✅ 推荐：使用局部变量缓存频繁访问的属性
def process_sensor_data(self, data_list: List[float]) -> float:
    # 缓存方法引用，避免重复查找
    math_sqrt = math.sqrt
    len_data = len(data_list)
    
    total = 0.0
    for value in data_list:
        total += math_sqrt(value)
    
    return total / len_data

# ✅ 推荐：使用__slots__减少内存占用
class SensorReading:
    __slots__ = ['timestamp', 'value', 'sensor_id']
    
    def __init__(self, timestamp: float, value: float, sensor_id: int):
        self.timestamp = timestamp
        self.value = value
        self.sensor_id = sensor_id

# ✅ 推荐：避免不必要的对象创建
def format_sensor_data(readings: List[SensorReading]) -> str:
    # 使用列表推导式，比循环append更高效
    parts = [f"{r.sensor_id}:{r.value:.2f}" for r in readings]
    return ",".join(parts)

# 错误处理规范

# ✅ 推荐：具体的异常处理
class SensorError(Exception):
    """传感器相关错误基类"""
    pass

class SensorTimeoutError(SensorError):
    """传感器超时错误"""
    pass

class SensorCalibrationError(SensorError):
    """传感器校准错误"""
    pass

def read_sensor_with_retry(sensor_id: int, max_retries: int = 3) -> float:
    """带重试机制的传感器读取"""
    for attempt in range(max_retries):
        try:
            return read_sensor(sensor_id)
        except SensorTimeoutError:
            if attempt == max_retries - 1:
                raise
            time.sleep(0.1 * (attempt + 1))  # 指数退避
        except SensorCalibrationError:
            # 校准错误不重试
            raise
    
    raise SensorError(f"Failed to read sensor {sensor_id} after {max_retries} attempts")