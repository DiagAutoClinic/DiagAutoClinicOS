cmake_minimum_required(VERSION 3.16)
project(autodiag_native_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(j2534_native_probe j2534_native_probe.cpp)

if(MSVC)
  target_compile_options(j2534_native_probe PRIVATE /W4 /EHsc)
else()
  target_compile_options(j2534_native_probe PRIVATE -Wall -Wextra -Wpedantic)
endif()
