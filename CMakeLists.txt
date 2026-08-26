cmake_minimum_required(VERSION 3.20...4.4)

project(game_solver_cpp LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)


# -------------------------
# C++ implementation
# -------------------------

add_library(
    game_solver_cpp
    STATIC
    # ソースコードのパスはここに追加
    src/game_solver/cpp/src/sample.cpp
    src/game_solver/cpp/src/connect_four/engine.cpp
    src/game_solver/cpp/src/connect_four/mcts.cpp
)

target_compile_features(
    game_solver_cpp
    PUBLIC
    cxx_std_23
)

target_include_directories(
    game_solver_cpp
    PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/game_solver/cpp/include>
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
