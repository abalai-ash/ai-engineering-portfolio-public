cmake_minimum_required(VERSION 3.16)

project(embedded_sensor_fault_management LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(sensor_controller_lib
    src/fault_manager.cpp
    src/measurement_validator.cpp
    src/sensor_controller.cpp
    src/simulated_sensor.cpp
    src/watchdog.cpp
)

target_include_directories(sensor_controller_lib PUBLIC src)

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(sensor_controller_lib PRIVATE
        -Wall
        -Wextra
        -Wpedantic
    )
endif()

add_executable(sensor_controller_demo src/main.cpp)

target_link_libraries(sensor_controller_demo PRIVATE sensor_controller_lib)

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(sensor_controller_demo PRIVATE
        -Wall
        -Wextra
        -Wpedantic
    )
endif()
