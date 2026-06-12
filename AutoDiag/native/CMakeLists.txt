cmake_minimum_required(VERSION 3.16)
project(autodiag_native LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find libusb
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBUSB REQUIRED libusb-1.0)

# J2534 probe executable (Windows only)
if(WIN32)
  add_executable(j2534_native_probe j2534_native_probe.cpp)
  if(MSVC)
    target_compile_options(j2534_native_probe PRIVATE /W4 /EHsc)
  else()
    target_compile_options(j2534_native_probe PRIVATE -Wall -Wextra -Wpedantic)
  endif()
endif()
