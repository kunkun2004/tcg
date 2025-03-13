#include <iostream>
#include <cstdlib>
#include <ctime>

int main() {
    srand(time(0)); // 初始化随机数种子

    int n = 5; // 生成5块地毯
    std::cout << n << std::endl; // 输入地毯数量

    // 生成每块地毯的信息
    for (int i = 0; i < n; ++i) {
        int a = rand() % 100; // 随机生成左下角的x坐标
        int b = rand() % 100; // 随机生成左下角的y坐标
        int g = 1 + rand() % 10; // 随机生成x轴方向的长度
        int k = 1 + rand() % 10; // 随机生成y轴方向的长度
        std::cout << a << " " << b << " " << g << " " << k << std::endl; // 输出地毯信息
    }

    // 生成查询坐标，确保它在所有地毯之外
    int query_x = 1000; // 一个较大的x坐标值
    int query_y = 1000; // 一个较大的y坐标值
    std::cout << query_x << " " << query_y << std::endl; // 输出查询坐标

    return 0;
}