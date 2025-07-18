#!/usr/bin/env python3
"""
DJI PSDK Python Binding - 统一构建脚本

这个脚本提供了一键式构建和安装体验，自动处理依赖检查、环境配置和错误处理。

使用方法:
    python scripts/build.py                    # 标准构建和安装
    python scripts/build.py --dev              # 开发模式安装
    python scripts/build.py --clean            # 清理后重新构建
    python scripts/build.py --test             # 构建后运行测试
    python scripts/build.py --docs             # 构建文档
    python scripts/build.py --check-only       # 仅检查环境，不构建
"""

import os
import sys
import argparse
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

class Colors:
    """终端颜色定义"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class BuildError(Exception):
    """构建错误异常"""
    pass

class PSDKBuilder:
    """PSDK Python绑定构建器"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.python_binding_dir = root_dir / "python-binding"
        self.psdk_root = root_dir
        
        # 检查目录结构
        if not self.python_binding_dir.exists():
            raise BuildError(f"Python binding directory not found: {self.python_binding_dir}")
        
        if not (self.psdk_root / "psdk_lib").exists():
            raise BuildError(f"PSDK library directory not found: {self.psdk_root / 'psdk_lib'}")
    
    def print_status(self, message: str, color: str = Colors.BLUE):
        """打印状态信息"""
        print(f"{color}{Colors.BOLD}[INFO]{Colors.END} {message}")
    
    def print_success(self, message: str):
        """打印成功信息"""
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS]{Colors.END} {message}")
    
    def print_warning(self, message: str):
        """打印警告信息"""
        print(f"{Colors.YELLOW}{Colors.BOLD}[WARNING]{Colors.END} {message}")
    
    def print_error(self, message: str):
        """打印错误信息"""
        print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.END} {message}")
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   capture_output: bool = False) -> Tuple[int, str, str]:
        """运行命令"""
        if cwd is None:
            cwd = self.python_binding_dir
            
        self.print_status(f"Running: {' '.join(cmd)}")
        
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, cwd=cwd, capture_output=True, text=True, check=False
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, cwd=cwd, check=False)
                return result.returncode, "", ""
        except FileNotFoundError as e:
            raise BuildError(f"Command not found: {cmd[0]}") from e
    
    def check_python_version(self):
        """检查Python版本"""
        self.print_status("Checking Python version...")
        
        if sys.version_info < (3, 7):
            raise BuildError(
                f"Python 3.7 or higher is required. "
                f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
            )
        
        self.print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    def check_cmake(self):
        """检查CMake"""
        self.print_status("Checking CMake...")
        
        returncode, stdout, stderr = self.run_command(
            ["cmake", "--version"], capture_output=True
        )
        
        if returncode != 0:
            raise BuildError(
                "CMake not found. Please install CMake 3.18 or higher.\n"
                "Ubuntu/Debian: sudo apt install cmake\n"
                "CentOS/RHEL: sudo yum install cmake\n"
                "macOS: brew install cmake"
            )
        
        version_line = stdout.split('\n')[0]
        self.print_success(f"Found {version_line}")
    
    def check_compiler(self):
        """检查编译器"""
        self.print_status("Checking compiler...")
        
        if platform.system() == "Linux":
            returncode, stdout, stderr = self.run_command(
                ["gcc", "--version"], capture_output=True
            )
            
            if returncode != 0:
                raise BuildError(
                    "GCC compiler not found. Please install build tools:\n"
                    "Ubuntu/Debian: sudo apt install build-essential\n"
                    "CentOS/RHEL: sudo yum groupinstall 'Development Tools'"
                )
            
            version_line = stdout.split('\n')[0]
            self.print_success(f"Found {version_line}")
        
        elif platform.system() == "Windows":
            # 检查Visual Studio或MinGW
            vs_found = False
            try:
                returncode, _, _ = self.run_command(
                    ["cl"], capture_output=True
                )
                if returncode == 0:
                    vs_found = True
                    self.print_success("Found Visual Studio compiler")
            except:
                pass
            
            if not vs_found:
                try:
                    returncode, stdout, _ = self.run_command(
                        ["gcc", "--version"], capture_output=True
                    )
                    if returncode == 0:
                        version_line = stdout.split('\n')[0]
                        self.print_success(f"Found MinGW: {version_line}")
                    else:
                        raise BuildError("No suitable compiler found")
                except:
                    raise BuildError(
                        "No suitable compiler found. Please install:\n"
                        "- Visual Studio 2019 or later with C++ tools, or\n"
                        "- MinGW-w64 via MSYS2"
                    )
    
    def check_dependencies(self):
        """检查Python依赖"""
        self.print_status("Checking Python dependencies...")
        
        required_packages = [
            ("pybind11", "2.10.0"),
            ("numpy", "1.19.0"),
        ]
        
        missing_packages = []
        
        for package, min_version in required_packages:
            try:
                __import__(package)
                self.print_success(f"Found {package}")
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.print_warning(f"Missing packages: {', '.join(missing_packages)}")
            self.print_status("Installing missing packages...")
            
            cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
            returncode, _, stderr = self.run_command(cmd, capture_output=True)
            
            if returncode != 0:
                raise BuildError(f"Failed to install dependencies: {stderr}")
            
            self.print_success("Dependencies installed successfully")
    
    def check_system_libraries(self):
        """检查系统库"""
        if platform.system() != "Linux":
            return
            
        self.print_status("Checking system libraries...")
        
        # 检查libusb
        returncode, _, _ = self.run_command(
            ["pkg-config", "--exists", "libusb-1.0"], capture_output=True
        )
        
        if returncode != 0:
            self.print_warning(
                "libusb-1.0 not found. Some features may not work.\n"
                "Install with: sudo apt install libusb-1.0-0-dev"
            )
        else:
            self.print_success("Found libusb-1.0")
        
        # 检查opus
        returncode, _, _ = self.run_command(
            ["pkg-config", "--exists", "opus"], capture_output=True
        )
        
        if returncode != 0:
            self.print_warning(
                "opus not found. Audio features may not work.\n"
                "Install with: sudo apt install libopus-dev"
            )
        else:
            self.print_success("Found opus")
    
    def clean_build(self):
        """清理构建文件"""
        self.print_status("Cleaning build files...")
        
        clean_dirs = [
            "build",
            "dist", 
            "*.egg-info",
            "__pycache__",
            ".pytest_cache",
        ]
        
        for pattern in clean_dirs:
            for path in self.python_binding_dir.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    self.print_status(f"Removed directory: {path}")
                elif path.is_file():
                    path.unlink()
                    self.print_status(f"Removed file: {path}")
        
        self.print_success("Build files cleaned")
    
    def build_package(self, dev_mode: bool = False):
        """构建包"""
        self.print_status(f"Building package ({'development' if dev_mode else 'release'} mode)...")
        
        # 设置环境变量
        env = os.environ.copy()
        env["PSDK_ROOT"] = str(self.psdk_root)
        
        if dev_mode:
            cmd = [sys.executable, "setup.py", "develop"]
        else:
            cmd = [sys.executable, "setup.py", "install"]
        
        returncode, _, stderr = self.run_command(cmd, capture_output=False)
        
        if returncode != 0:
            raise BuildError(f"Build failed: {stderr}")
        
        self.print_success("Package built successfully")
    
    def run_tests(self):
        """运行测试"""
        self.print_status("Running tests...")
        
        test_dir = self.python_binding_dir / "tests"
        if not test_dir.exists():
            self.print_warning("No tests directory found, skipping tests")
            return
        
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
        returncode, _, stderr = self.run_command(cmd, capture_output=False)
        
        if returncode != 0:
            self.print_warning(f"Some tests failed: {stderr}")
        else:
            self.print_success("All tests passed")
    
    def build_docs(self):
        """构建文档"""
        self.print_status("Building documentation...")
        
        docs_dir = self.python_binding_dir / "docs"
        if not docs_dir.exists():
            self.print_warning("No docs directory found, skipping documentation build")
            return
        
        # 安装文档依赖
        cmd = [sys.executable, "-m", "pip", "install", "-e", ".[docs]"]
        returncode, _, _ = self.run_command(cmd, capture_output=True)
        
        if returncode != 0:
            self.print_warning("Failed to install documentation dependencies")
            return
        
        # 构建文档
        cmd = ["make", "html"]
        returncode, _, stderr = self.run_command(cmd, cwd=docs_dir, capture_output=False)
        
        if returncode != 0:
            self.print_warning(f"Documentation build failed: {stderr}")
        else:
            self.print_success("Documentation built successfully")
            docs_output = docs_dir / "build" / "html" / "index.html"
            if docs_output.exists():
                self.print_status(f"Documentation available at: {docs_output}")
    
    def verify_installation(self):
        """验证安装"""
        self.print_status("Verifying installation...")
        
        try:
            # 测试导入
            returncode, stdout, stderr = self.run_command([
                sys.executable, "-c", 
                "import psdk; print(f'PSDK Python binding {psdk.__version__} imported successfully')"
            ], capture_output=True)
            
            if returncode != 0:
                raise BuildError(f"Import test failed: {stderr}")
            
            self.print_success(stdout.strip())
            
            # 运行兼容性检查
            returncode, stdout, stderr = self.run_command([
                sys.executable, "-c",
                "import psdk; psdk.check_compatibility()"
            ], capture_output=True)
            
            if returncode == 0:
                self.print_success("Compatibility check passed")
            else:
                self.print_warning(f"Compatibility check failed: {stderr}")
                
        except Exception as e:
            raise BuildError(f"Installation verification failed: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="DJI PSDK Python Binding Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build.py                 # 标准构建和安装
  python scripts/build.py --dev           # 开发模式安装
  python scripts/build.py --clean --test  # 清理、构建并测试
  python scripts/build.py --check-only    # 仅检查环境
        """
    )
    
    parser.add_argument("--dev", action="store_true", 
                       help="Install in development mode")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build files before building")
    parser.add_argument("--test", action="store_true",
                       help="Run tests after building")
    parser.add_argument("--docs", action="store_true",
                       help="Build documentation")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check environment, don't build")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # 查找项目根目录
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent  # python-binding目录
    
    # 如果脚本在scripts子目录中，需要再向上一级找到Payload-SDK根目录
    if root_dir.name == "python-binding":
        psdk_root = root_dir.parent
    else:
        psdk_root = root_dir
    
    try:
        builder = PSDKBuilder(psdk_root)
        
        print(f"{Colors.CYAN}{Colors.BOLD}DJI PSDK Python Binding Builder{Colors.END}")
        print(f"{Colors.CYAN}================================{Colors.END}\n")
        
        # 环境检查
        builder.check_python_version()
        builder.check_cmake()
        builder.check_compiler()
        builder.check_dependencies()
        builder.check_system_libraries()
        
        if args.check_only:
            builder.print_success("Environment check completed successfully!")
            return
        
        # 清理
        if args.clean:
            builder.clean_build()
        
        # 构建
        builder.build_package(dev_mode=args.dev)
        
        # 验证安装
        builder.verify_installation()
        
        # 测试
        if args.test:
            builder.run_tests()
        
        # 文档
        if args.docs:
            builder.build_docs()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Build completed successfully!{Colors.END}")
        
        # 使用说明
        print(f"\n{Colors.CYAN}Quick Start:{Colors.END}")
        print(f"  {Colors.WHITE}import psdk{Colors.END}")
        print(f"  {Colors.WHITE}sdk = psdk.quick_start(...){Colors.END}")
        print(f"  {Colors.WHITE}# Your code here{Colors.END}")
        
        if args.dev:
            print(f"\n{Colors.YELLOW}Development Mode:{Colors.END}")
            print(f"  {Colors.WHITE}You can now edit the source code and changes will be reflected immediately.{Colors.END}")
        
    except BuildError as e:
        print(f"\n{Colors.RED}{Colors.BOLD}Build failed:{Colors.END} {e}")
        
        # 提供常见问题解决方案
        print(f"\n{Colors.YELLOW}Common Solutions:{Colors.END}")
        print(f"  1. Ensure all dependencies are installed")
        print(f"  2. Check that you're in the correct directory")
        print(f"  3. Try running with --clean to remove old build files")
        print(f"  4. Check the error message above for specific issues")
        
        sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Build interrupted by user{Colors.END}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}Unexpected error:{Colors.END} {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
