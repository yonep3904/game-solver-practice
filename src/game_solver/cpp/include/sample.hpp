#pragma once

#include <string>
#include <vector>

namespace sample {

int add(int a, int b);

std::vector<int> double_values(const std::vector<int>& values);

class Counter {
  public:
    explicit Counter(int initial_value = 0);

    void increment();
    void add(int value);

    [[nodiscard]] int value() const;
    [[nodiscard]] std::string message() const;

  private:
    int value_;
};

} // namespace sample
