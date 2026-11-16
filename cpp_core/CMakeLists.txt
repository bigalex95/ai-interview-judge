find_package(OpenCV REQUIRED COMPONENTS core imgproc videoio)

# Pure C++ library: no Python dependency, so it can be unit-tested and
# benchmarked on its own.
add_library(ai_interview_core STATIC src/slide_detector.cpp)
target_include_directories(ai_interview_core PUBLIC include ${OpenCV_INCLUDE_DIRS})
target_link_libraries(ai_interview_core PUBLIC ${OpenCV_LIBS})
set_target_properties(ai_interview_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Python extension: `import ai_interview_cpp`
pybind11_add_module(ai_interview_cpp src/bindings.cpp)
target_link_libraries(ai_interview_cpp PRIVATE ai_interview_core)

# Put the built .so into <repo>/libs so the backend can import it
set_target_properties(ai_interview_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/libs"
)
