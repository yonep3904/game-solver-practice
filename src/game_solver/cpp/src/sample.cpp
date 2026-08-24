#include "sample.hpp"

#include <string>
#include <vector>

namespace sample {

int add(int a, int b) {
    return a + b;
}

std::vector<int> double_values(const std::vector<int>& values) {
    std::vector<int> result;
    result.reserve(values.size());

    for (const int value : values) {
        result.push_back(value * 2);
    }

    return result;
}

Counter::Counter(int initial_value) : value_(initial_value) {}

void Counter::increment() {
    ++value_;
}

void Counter::add(int value) {
    value_ += value;
}

int Counter::value() const {
    return value_;
}

std::string Counter::message() const {
    return "Current value: " + std::to_string(value_);
}

}  // namespace sample
