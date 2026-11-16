# GoogleTest (pinned release for reproducible builds)
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(unit_tests test_slide_detector.cpp)
target_link_libraries(unit_tests PRIVATE ai_interview_core GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(unit_tests)
