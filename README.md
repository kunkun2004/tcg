# 本科毕业设计

## 简介
本项目旨在使用大模型生成OI题目的测试数据（Test Case Generator）。出题人需提供题面、数据格式判断程序和正确程序，并根据指引输入数据的额外需求（如树、图、递增性质等）。

## 思路
1. **分析题意**：总结测试数据的测试需求。
2. **提出构造方案**：根据每个测试需求，提出测试数据的构造方案。
3. **构造数据**：根据构造方案和输入数据格式，构造合理的数据。
4. **验证合法性**：测试数据的合法性，如果不合法则重新生成。
5. **整理打包**：整理并打包数据，返回给用户。

## 日志
11.17
- 完成项目简介和思路的编写。
- 开始编写代码框架。

11.18
- 完善代码框架的编写。
- 下一步：写prompt、写特殊输入类型的判断和生成。

3.13
- 增加智谱ai，完成基本功能