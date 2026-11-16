cmake_minimum_required(VERSION 3.14)
project(ai_interview_judge VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Default to an optimized build; the slide detector is pixel-heavy and a
# plain (unoptimized) build is an order of magnitude slower.
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

option(BUILD_TESTS "Build C++ unit tests (GoogleTest, run with ctest)" OFF)
option(BUILD_BENCHMARKS "Build the slide detector throughput benchmark" OFF)

# Python is required by pybind11
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# C++ core (static library) + Python module
add_subdirectory(cpp_core)

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests/cpp)
endif()

if(BUILD_BENCHMARKS)
    add_subdirectory(benchmarks)
endif()
