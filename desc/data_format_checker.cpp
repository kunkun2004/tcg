#include <bits/stdc++.h>

bool is_integer(const std::string &s) {
    std::istringstream iss(s);
    int num;
    char c;
    return iss >> num && !(iss >> c);
}

int main() {
    std::string line;
    std::vector<std::string> lines;

    // Read all input lines
    while (std::getline(std::cin, line)) {
        lines.push_back(line);
    }

    // Check if the number of lines is at least 3 (n + 2)
    if (lines.size() < 3) {
        std::cerr << "Error: Not enough lines." << std::endl;
        return 1;
    }

    // Check the first line
    if (!is_integer(lines[0])) {
        std::cerr << "Error: First line is not an integer." << std::endl;
        return 1;
    }

    int n = std::stoi(lines[0]);

    // Check if the number of lines is correct
    if (lines.size() != n + 2) {
        std::cerr << "Error: Incorrect number of lines." << std::endl;
        return 1;
    }

    // Check the next n lines
    for (int i = 1; i <= n; ++i) {
        std::istringstream iss(lines[i]);
        std::string token;
        int count = 0;
        while (iss >> token) {
            if (!is_integer(token)) {
                std::cerr << "Error: Line " << i << " contains non-integer values." << std::endl;
                return 1;
            }
            count++;
        }
        if (count != 4) {
            std::cerr << "Error: Line " << i << " does not contain exactly 4 integers." << std::endl;
            return 1;
        }
    }

    // Check the last line
    std::istringstream iss(lines[n + 1]);
    std::string token;
    int count = 0;
    while (iss >> token) {
        if (!is_integer(token)) {
            std::cerr << "Error: Last line contains non-integer values." << std::endl;
            return 1;
        }
        count++;
    }
    if (count != 2) {
        std::cerr << "Error: Last line does not contain exactly 2 integers." << std::endl;
        return 1;
    }

    // If all checks passed, return 0
    return 0;
}