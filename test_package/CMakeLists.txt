cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()


find_package(Qt5Widgets)

add_executable(qtbasetest test.cpp)
target_link_libraries(qtbasetest Qt5::Widgets)

