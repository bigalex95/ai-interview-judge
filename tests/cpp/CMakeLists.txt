# Подключаем GoogleTest через FetchContent (стандартный паттерн)
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
# Для Windows иногда нужно форсировать shared/static настройки, 
# но для начала оставим дефолт
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Включаем тестирование
enable_testing()

# Собираем все .cpp файлы из этой папки (тут будут наши тесты)
file(GLOB TEST_SOURCES "*.cpp")

# Создаем исполняемый файл для тестов
add_executable(unit_tests ${TEST_SOURCES})

# Линкуем с нашей основной библиотекой и GTest
# Важно: мы линкуем ai_interview_cpp, чтобы тестировать его функции
target_link_libraries(unit_tests PRIVATE
    ai_interview_cpp
    GTest::gtest_main
)

# Регистрируем тест в системе CTest
include(GoogleTest)
gtest_discover_tests(unit_tests)
