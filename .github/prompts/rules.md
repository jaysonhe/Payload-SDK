Rule 1: 始终使用上下文管理器管理资源
示例：
class HardwareResource:
    def __enter__(self):
        self.handle = acquire_hardware()
        return self.handle
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        release_hardware(self.handle)

Rule 2: 避免循环引用
示例：
class Parent:
    def __init__(self):
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        # ❌ 避免强引用循环
        # child.parent = self
        # ✅ 使用弱引用
        import weakref
        child.parent = weakref.ref(self)

Rule 3: 及时清理大对象
示例：
    def process_large_dataset():
        dataset = load_large_dataset()
        try:
            result = analyze(dataset)
            return result
        finally:
            del dataset  # 显式删除
            import gc
            gc.collect()  # 在必要时强制垃圾回收

Rule 4: 使用适当的数据结构
示例：
    from collections import deque
    from array import array

    # ✅ 对于数值数据，使用array而不是list
    sensor_values = array('f', [0.0] * 1000)  # 浮点数组

    # ✅ 对于队列操作，使用deque
    data_buffer = deque(maxlen=100)  # 固定大小的环形缓冲区

Rule 5: 避免不必要的字符串操作
示例：
    def format_log_message(level: str, message: str, timestamp: float) -> str:
    # ✅ 使用f-string，比%格式化和.format()更快
    return f"[