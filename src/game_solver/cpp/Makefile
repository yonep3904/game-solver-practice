CXX := g++

CPPFLAGS := -Iinclude
CXXFLAGS := -std=c++23 -Wall -Wextra -Wpedantic -O2 -MMD -MP

BUILD_DIR := build
SRC_DIR := src
TEST_DIR := test

SOURCES := $(filter-out $(SRC_DIR)/bindings.cpp,$(wildcard $(SRC_DIR)/*.cpp))
TEST_SOURCES := $(wildcard $(TEST_DIR)/*.cpp)

OBJECTS := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(SOURCES))
DEPS := $(OBJECTS:.o=.d) $(BUILD_DIR)/main.d

MAIN_TARGET := $(BUILD_DIR)/main
TEST_TARGET := $(BUILD_DIR)/test


.PHONY: all run test clean

all: $(MAIN_TARGET)

$(MAIN_TARGET): $(OBJECTS) $(BUILD_DIR)/main.o
	$(CXX) $(CXXFLAGS) $^ -o $@

$(BUILD_DIR)/main.o: main.cpp | $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(TEST_TARGET): $(OBJECTS) $(TEST_SOURCES) | $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(OBJECTS) $(TEST_SOURCES) -o $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $@

run: $(MAIN_TARGET)
	./$(MAIN_TARGET)

test: $(TEST_TARGET)
	./$(TEST_TARGET)

clean:
	rm -rf $(BUILD_DIR)

-include $(DEPS)
