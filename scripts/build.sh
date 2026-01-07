#!/bin/bash
# 1. Create build directory
mkdir -p build
cd build

# 2. Generate Makefile via CMake
# CMake will download pybind11, find Python and OpenCV.
cmake ..

# 3. Compile (use all CPU cores with -j)
make -j$(nproc)