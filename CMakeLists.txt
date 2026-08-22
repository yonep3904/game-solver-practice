cmake_minimum_required(VERSION 3.15)

project(game_solver_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)


# -------------------------
# C++ implementation
# -------------------------

add_library(
    game_solver_cpp
    STATIC
    src/game_solver/cpp/src/connect_four_engine.cpp
    src/game_solver/cpp/src/mcts.cpp
)

target_include_directories(
    game_solver_cpp
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/game_solver/cpp/include
)

set_target_properties(
    game_solver_cpp
    PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)


# -------------------------
# Python bindings
# -------------------------

pybind11_add_module(
    _core
    src/game_solver/cpp/src/bindings.cpp
)

target_link_libraries(
    _core
    PRIVATE
    game_solver_cpp
)

target_compile_features(_core PRIVATE cxx_std_23)


# -------------------------
# Python installation
# -------------------------

install(
    TARGETS _core
    LIBRARY DESTINATION game_solver
)
