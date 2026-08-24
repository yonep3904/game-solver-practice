#include <iostream>

#include "sample.hpp"

int main() {
    const auto sum = sample::add(3, 5);
    std::cout << "Sum: " << sum << std::endl;

    const auto values = {1, 2, 3};
    const auto doubled_values = sample::double_values(values);
    std::cout << "Doubled values: ";
    for (int value : doubled_values) {
        std::cout << value << " ";
    }
    std::cout << std::endl;

    sample::Counter counter(10);
    counter.increment();
    counter.add(5);
    const auto current_value = counter.value();
    const auto message = counter.message();

    std::cout << "Counter value: " << current_value << std::endl;
    std::cout << "Counter message: " << message << std::endl;

    return 0;
}
