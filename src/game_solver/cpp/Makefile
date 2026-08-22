CXX ?= c++
CXXFLAGS ?= -std=c++23 -Wall -Wextra -Wpedantic -Werror -O2
CPPFLAGS ?= -Iinclude
BUILD_DIR ?= build

LOGIC_SOURCES := src/connect_four_engine.cpp src/mcts.cpp
TEST_SOURCES := tests/connect_four_engine_test.cpp
TEST_BINARY := $(BUILD_DIR)/connect_four_engine_test

.PHONY: all test clean

all: $(TEST_BINARY)

$(TEST_BINARY): $(LOGIC_SOURCES) $(TEST_SOURCES) | $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $^ -o $@

$(BUILD_DIR):
	mkdir -p $@

test: $(TEST_BINARY)
	./$(TEST_BINARY)

clean:
	rm -rf $(BUILD_DIR)
