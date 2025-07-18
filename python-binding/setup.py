#!/usr/bin/env python3
"""
DJI Payload SDK Python Binding Setup Script

This script provides intelligent build configuration with automatic dependency
detection and platform-specific optimizations.

Usage:
    python setup.py install          # 标准安装
    python setup.py develop          # 开发模式安装
    python setup.py build_ext        # 仅构建扩展
    python setup.py clean --all      # 清理构建文件
    
Environment Variables:
    PSDK_ROOT: Path to DJI PSDK root directory (auto-detected if not set)
    CMAKE_ARGS: Additional CMake arguments
    PARALLEL_JOBS: Number of parallel build jobs (default: auto-detect)
    DEBUG_BUILD: Set to 1 for debug build
"""

import os
import sys
import platform
import subprocess
import multiprocessing
from pathlib import Path
from typing import List, Dict, Optional

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.develop import develop

# 版本信息
__version__ = "1.0.0"

class CMakeExtension(Extension):
    """CMake扩展类"""
    
    def __init__(self, name: str, sourcedir: str = ""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    """智能CMake构建类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.psdk_root = self._find_psdk_root()
        self.build_jobs = self._get_build_jobs()
        
    def _find_psdk_root(self) -> Path:
        """自动查找PSDK根目录"""
        # 1. 检查环境变量
        if "PSDK_ROOT" in os.environ:
            root = Path(os.environ["PSDK_ROOT"])
            if self._validate_psdk_root(root):
                return root
                
        # 2. 从当前目录向上查找
        current = Path(__file__).parent.absolute()
        while current != current.parent:
            if self._validate_psdk_root(current):
                return current
            current = current.parent
            
        # 3. 检查相对路径
        possible_paths = [
            Path(".."),  # python-binding在Payload-SDK内部
            Path("../.."),  # 可能的嵌套结构
            Path("."),  # 当前目录就是根目录
        ]
        
        for path in possible_paths:
            abs_path = (Path(__file__).parent / path).resolve()
            if self._validate_psdk_root(abs_path):
                return abs_path
                
        raise RuntimeError(
            "Cannot find DJI PSDK root directory. "
            "Please set PSDK_ROOT environment variable or ensure "
            "this script is run from within the Payload-SDK directory structure."
        )
    
    def _validate_psdk_root(self, path: Path) -> bool:
        """验证PSDK根目录"""
        required_items = [
            "psdk_lib/include",
            "psdk_lib/lib", 
            "CMakeLists.txt"
        ]
        return all((path / item).exists() for item in required_items)
    
    def _get_build_jobs(self) -> int:
        """获取构建并行数"""
        if "PARALLEL_JOBS" in os.environ:
            try:
                return int(os.environ["PARALLEL_JOBS"])
            except ValueError:
                pass
        return min(multiprocessing.cpu_count(), 8)  # 限制最大并行数
    
    def _get_cmake_args(self) -> List[str]:
        """获取CMake参数"""
        cmake_args = []
        
        # 基础配置
        cmake_args.extend([
            f"-DPSDK_ROOT_DIR={self.psdk_root}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
        ])
        
        # 构建类型
        build_type = "Debug" if os.environ.get("DEBUG_BUILD") == "1" else "Release"
        cmake_args.append(f"-DCMAKE_BUILD_TYPE={build_type}")
        
        # 平台特定配置
        if platform.system() == "Linux":
            cmake_args.extend([
                "-DCMAKE_CXX_COMPILER=g++",
                "-DCMAKE_C_COMPILER=gcc",
            ])
        elif platform.system() == "Windows":
            cmake_args.extend([
                "-G", "Visual Studio 16 2019",
                "-A", "x64",
            ])
        elif platform.system() == "Darwin":
            cmake_args.extend([
                "-DCMAKE_OSX_DEPLOYMENT_TARGET=10.14",
            ])
            
        # 用户自定义参数
        if "CMAKE_ARGS" in os.environ:
            cmake_args.extend(os.environ["CMAKE_ARGS"].split())
            
        return cmake_args
    
    def _get_build_args(self) -> List[str]:
        """获取构建参数"""
        build_args = ["--config", "Release"]
        
        if platform.system() == "Windows":
            build_args.extend([
                "--", f"/m:{self.build_jobs}"
            ])
        else:
            build_args.extend([
                "--", f"-j{self.build_jobs}"
            ])
            
        return build_args
    
    def _check_dependencies(self):
        """检查构建依赖"""
        print("Checking build dependencies...")
        
        # 检查CMake
        try:
            cmake_version = subprocess.check_output(
                ["cmake", "--version"], 
                universal_newlines=True
            ).split('\n')[0]
            print(f"✓ Found {cmake_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "CMake is required but not found. "
                "Please install CMake 3.18 or higher."
            )
        
        # 检查编译器
        if platform.system() == "Linux":
            try:
                gcc_version = subprocess.check_output(
                    ["gcc", "--version"],
                    universal_newlines=True
                ).split('\n')[0]
                print(f"✓ Found {gcc_version}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError("GCC compiler not found.")
                
        # 检查pybind11
        try:
            import pybind11
            print(f"✓ Found pybind11 {pybind11.__version__}")
        except ImportError:
            raise RuntimeError(
                "pybind11 is required but not found. "
                "Install with: pip install pybind11"
            )
    
    def build_extension(self, ext: CMakeExtension):
        """构建扩展"""
        print(f"Building extension: {ext.name}")
        print(f"PSDK Root: {self.psdk_root}")
        
        # 检查依赖
        self._check_dependencies()
        
        # 创建构建目录
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        build_temp = Path(self.build_temp) / ext.name
        build_temp.mkdir(parents=True, exist_ok=True)
        
        # CMake配置
        cmake_args = self._get_cmake_args()
        cmake_args.extend([
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
        ])
        
        # 执行CMake配置
        print("Configuring with CMake...")
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args,
            cwd=build_temp
        )
        
        # 执行构建
        print(f"Building with {self.build_jobs} parallel jobs...")
        build_args = self._get_build_args()
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args,
            cwd=build_temp
        )
        
        print("✓ Build completed successfully!")

class CustomInstall(install):
    """自定义安装命令"""
    
    def run(self):
        print("Installing DJI PSDK Python binding...")
        super().run()
        self._post_install()
    
    def _post_install(self):
        """安装后处理"""
        print("Running post-installation setup...")
        
        # 验证安装
        try:
            import psdk
            print(f"✓ PSDK Python binding {psdk.__version__} installed successfully!")
            
            # 运行兼容性检查
            if psdk.check_compatibility():
                print("✓ Compatibility check passed!")
            else:
                print("⚠ Compatibility check failed. Please check your installation.")
                
        except ImportError as e:
            print(f"✗ Installation verification failed: {e}")
            sys.exit(1)

class CustomDevelop(develop):
    """自定义开发模式安装"""
    
    def run(self):
        print("Installing DJI PSDK Python binding in development mode...")
        super().run()
        print("✓ Development installation completed!")
        print("You can now edit the source code and changes will be reflected immediately.")

def read_requirements(filename: str) -> List[str]:
    """读取requirements文件"""
    req_file = Path(__file__).parent / filename
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

def get_long_description() -> str:
    """获取长描述"""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python binding for DJI Payload SDK"

# 主要设置
if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        sys.exit(1)
    
    # 扩展模块
    ext_modules = [
        CMakeExtension("psdk._psdk_core", sourcedir="src"),
    ]
    
    # 安装要求
    install_requires = [
        "numpy>=1.19.0",
        "pybind11>=2.10.0",
    ]
    
    # Python 3.7兼容性
    if sys.version_info < (3, 8):
        install_requires.append("typing-extensions>=4.0.0")
    
    setup(
        name="psdk",
        version=__version__,
        author="DJI SDK Team",
        author_email="dev@dji.com",
        description="Python binding for DJI Payload SDK",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        url="https://github.com/dji-sdk/Payload-SDK",
        packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
        ext_modules=ext_modules,
        cmdclass={
            "build_ext": CMakeBuild,
            "install": CustomInstall,
            "develop": CustomDevelop,
        },
        install_requires=install_requires,
        extras_require={
            "dev": read_requirements("requirements-dev.txt"),
            "docs": read_requirements("requirements-docs.txt"),
            "examples": read_requirements("requirements-examples.txt"),
        },
        python_requires=">=3.7",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: C++",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        zip_safe=False,
        include_package_data=True,
        package_data={
            "psdk": ["*.so", "*.dll", "*.dylib", "py.typed"],
        },
    )
