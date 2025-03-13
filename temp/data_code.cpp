#include <iostream>
#include <vector>

int main() {
    // 输出地毯数量
    std::cout << 3 << std::endl;
    
    // 输出每张地毯的信息，这里构造编号为3的地毯在编号为1的地毯下面的情况
    // 地毯1
    std::cout << "0 0 3 3" << std::endl;
    // 地毯2
    std::cout << "1 1 3 3" << std::endl;
    // 地毯3（在1下面）
    std::cout << "-1 -1 5 5" << std::endl;
    
    // 输出查询点的坐标
    std::cout << "2 2" << std::endl;
    
    return 0;
}