# 1. Создаем папку для сборки
mkdir build
cd build

# 2. Генерируем Makefile через CMake
# CMake скачает pybind11, найдет Python и OpenCV.
cmake ..

# 3. Компилируем (используем все ядра процессора -j)
make -j$(nproc)