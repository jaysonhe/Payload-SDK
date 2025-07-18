cmake_minimum_required(VERSION 3.18)
project(psdk_python_binding)

# 设置C++标准
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 构建类型
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# 编译选项
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_definitions(DEBUG_BUILD)
    set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")
else()
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
endif()

# 查找PSDK根目录
if(NOT DEFINED PSDK_ROOT_DIR)
    # 尝试自动检测
    get_filename_component(PSDK_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
    if(NOT EXISTS "${PSDK_ROOT_DIR}/psdk_lib")
        message(FATAL_ERROR "Cannot find PSDK root directory. Please set PSDK_ROOT_DIR")
    endif()
endif()

message(STATUS "PSDK Root Directory: ${PSDK_ROOT_DIR}")

# 验证PSDK目录结构
set(PSDK_INCLUDE_DIR "${PSDK_ROOT_DIR}/psdk_lib/include")
set(PSDK_LIB_DIR "${PSDK_ROOT_DIR}/psdk_lib/lib")

if(NOT EXISTS "${PSDK_INCLUDE_DIR}")
    message(FATAL_ERROR "PSDK include directory not found: ${PSDK_INCLUDE_DIR}")
endif()

if(NOT EXISTS "${PSDK_LIB_DIR}")
    message(FATAL_ERROR "PSDK library directory not found: ${PSDK_LIB_DIR}")
endif()

# 检测目标平台架构
if(NOT DEFINED TARGET_ARCH)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
        set(TARGET_ARCH "x86_64-linux-gnu-gcc")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
        set(TARGET_ARCH "aarch64-linux-gnu-gcc")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm")
        # 检测是否为硬浮点
        execute_process(
            COMMAND ${CMAKE_C_COMPILER} -dumpmachine
            OUTPUT_VARIABLE COMPILER_MACHINE
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        if(COMPILER_MACHINE MATCHES "gnueabihf")
            set(TARGET_ARCH "arm-linux-gnueabihf-gcc")
        else()
            set(TARGET_ARCH "arm-linux-gnueabi-gcc")
        endif()
    else()
        message(WARNING "Unknown architecture: ${CMAKE_SYSTEM_PROCESSOR}, defaulting to x86_64")
        set(TARGET_ARCH "x86_64-linux-gnu-gcc")
    endif()
endif()

message(STATUS "Target Architecture: ${TARGET_ARCH}")

# 设置PSDK库路径
set(PSDK_LIBRARY_PATH "${PSDK_LIB_DIR}/${TARGET_ARCH}")
if(NOT EXISTS "${PSDK_LIBRARY_PATH}")
    message(FATAL_ERROR "PSDK library not found for architecture: ${PSDK_LIBRARY_PATH}")
endif()

# 查找Python和pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

# 检查pybind11版本
if(pybind11_VERSION VERSION_LESS "2.10.0")
    message(FATAL_ERROR "pybind11 version 2.10.0 or higher is required")
endif()

message(STATUS "Python Version: ${Python_VERSION}")
message(STATUS "pybind11 Version: ${pybind11_VERSION}")

# 包含目录
include_directories(
    ${PSDK_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/adapters
    ${CMAKE_CURRENT_SOURCE_DIR}/src/utils
)

# 查找所有源文件
file(GLOB_RECURSE BINDING_SOURCES
    "src/*.cpp"
    "src/*.hpp"
)

# 排除测试文件
list(FILTER BINDING_SOURCES EXCLUDE REGEX ".*test.*")

message(STATUS "Found binding sources: ${BINDING_SOURCES}")

# 创建pybind11模块
pybind11_add_module(_psdk_core ${BINDING_SOURCES})

# 设置模块属性
set_target_properties(_psdk_core PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    VISIBILITY_INLINES_HIDDEN ON
    PREFIX "${PYTHON_MODULE_PREFIX}"
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
)

# 链接PSDK库
target_link_libraries(_psdk_core PRIVATE
    "${PSDK_LIBRARY_PATH}/libpayloadsdk.a"
)

# 系统依赖库
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_link_libraries(_psdk_core PRIVATE
        pthread
        rt
        dl
        m
    )
    
    # 查找并链接USB库
    find_library(USB_LIBRARY usb-1.0)
    if(USB_LIBRARY)
        target_link_libraries(_psdk_core PRIVATE ${USB_LIBRARY})
        message(STATUS "Found USB library: ${USB_LIBRARY}")
    else()
        message(WARNING "USB library not found, some features may not work")
    endif()
    
    # 查找并链接OPUS库
    find_library(OPUS_LIBRARY opus)
    if(OPUS_LIBRARY)
        target_link_libraries(_psdk_core PRIVATE ${OPUS_LIBRARY})
        message(STATUS "Found OPUS library: ${OPUS_LIBRARY}")
    else()
        message(WARNING "OPUS library not found, audio features may not work")
    endif()
endif()

# 编译定义
target_compile_definitions(_psdk_core PRIVATE
    VERSION_INFO="${EXAMPLE_VERSION_INFO}"
    PYBIND11_DETAILED_ERROR_MESSAGES
)

# 优化设置
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(_psdk_core PRIVATE
        -O3
        -ffast-math
        -march=native
    )
endif()

# 安装规则
install(TARGETS _psdk_core
    LIBRARY DESTINATION psdk
    ARCHIVE DESTINATION psdk
    RUNTIME DESTINATION psdk
)

# 开发模式支持
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    # 添加调试符号
    target_compile_options(_psdk_core PRIVATE -g)
    
    # 启用地址消毒器（可选）
    option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
    if(ENABLE_ASAN)
        target_compile_options(_psdk_core PRIVATE -fsanitize=address)
        target_link_options(_psdk_core PRIVATE -fsanitize=address)
    endif()
endif()

# 生成编译数据库（用于IDE支持）
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 打印配置摘要
message(STATUS "=== Build Configuration Summary ===")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Python: ${Python_EXECUTABLE}")
message(STATUS "pybind11: ${pybind11_VERSION}")
message(STATUS "PSDK Root: ${PSDK_ROOT_DIR}")
message(STATUS "Target Arch: ${TARGET_ARCH}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "===================================")

# 自定义目标：清理
add_custom_target(clean-all
    COMMAND ${CMAKE_BUILD_TOOL} clean
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}/CMakeFiles
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/CMakeCache.txt
    COMMENT "Cleaning all build files"
)

# 自定义目标：安装开发依赖
add_custom_target(install-dev-deps
    COMMAND ${Python_EXECUTABLE} -m pip install -e ".[dev]"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Installing development dependencies"
)

# 自定义目标：运行测试
add_custom_target(test-python
    COMMAND ${Python_EXECUTABLE} -m pytest tests/ -v
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS _psdk_core
    COMMENT "Running Python tests"
)
