cmake_minimum_required(VERSION 3.20)
project(ThruGame LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Werror)
endif()

# Core static library
file(GLOB_RECURSE THRU_CORE_HEADERS "ThruCore/include/*.h")
file(GLOB_RECURSE THRU_CORE_SOURCES "ThruCore/src/*.cpp")

add_library(ThruCore STATIC
    ${THRU_CORE_HEADERS}
    ${THRU_CORE_SOURCES}
)

target_include_directories(ThruCore PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/ThruCore/include>
)

target_include_directories(ThruCore SYSTEM PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/third_party>
)

# Tests executable
file(GLOB TEST_SOURCES "tests/*.cpp")

add_executable(thru_tests
    ${TEST_SOURCES}
)

target_include_directories(thru_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/ThruCore/include
)

target_include_directories(thru_tests SYSTEM PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party
)

target_link_libraries(thru_tests PRIVATE
    ThruCore
)
