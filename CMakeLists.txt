cmake_minimum_required(VERSION 3.14)
project(ai_interview_judge VERSION 0.1.0 LANGUAGES CXX)

# Используем стандарт C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Опция: Сборка тестов (по умолчанию выключена, включим когда будем тестить)
option(BUILD_TESTS "Build tests" OFF)

# Находим Python (критично для pybind11)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Находим pybind11 (uv add pybind11 не ставит его в систему, 
# поэтому мы будем использовать FetchContent или подмодуль. 
# Самый надежный способ для Modern C++ — FetchContent).
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# Добавляем наш C++ модуль (подпапка)
add_subdirectory(cpp_core)
