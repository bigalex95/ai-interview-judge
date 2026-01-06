# Находим OpenCV
find_package(OpenCV REQUIRED)

# Собираем список исходников
file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "include/*.hpp")

# Создаем модуль Python (это магия pybind11)
# ai_interview_cpp — так будет называться модуль в Python (import ai_interview_cpp)
pybind11_add_module(ai_interview_cpp
    ${SOURCES}
    ${HEADERS}
)

# Подключаем папки с хедерами
target_include_directories(ai_interview_cpp PRIVATE
    include
    ${OpenCV_INCLUDE_DIRS}
)

# Линкуем библиотеки
target_link_libraries(ai_interview_cpp PRIVATE
    ${OpenCV_LIBS}
)

# Указываем, куда положить скомпилированный файл (.so / .pyd)
# Положим его прямо в корень backend/services или backend/, чтобы Python его видел
# Пока положим в корень проекта для теста
set_target_properties(ai_interview_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/backend"
)
