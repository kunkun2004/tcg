from openai import OpenAI
import argparse
import os
from dotenv import load_dotenv
import subprocess
import json
from typing import Any, Dict, List, Optional, Union
from loguru import logger
from chat import *

load_dotenv()
logger.add("tcg.log", rotation="50 MB", retention="10 days", level="DEBUG")

# [
#             {"role": "system", "content": "You are a helpful assistant"},
#             {"role": "user", "content": content},
#         ]

agent = Zhipu(os.getenv('ZHIPU_API_KEY'))
# agent = Deepseek(os.getenv('DS_API_KEY'))

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def compile_cpp(cpp_file_path: str):
    try:
        output_file_path = cpp_file_path.replace('.cpp', '.exe')
        subprocess.run(['g++', cpp_file_path, '-o', output_file_path, '-std=gnu++11'], check=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to compile {cpp_file_path}: {e}"
        logger.error(error_message)
        return False, error_message

def run_program(program_path: str, input_data: str) -> str:
    try:
        result = subprocess.run([program_path], input=input_data, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise
    
def extract_b_values(text):
    lines = text.splitlines()
    
    b_values = [] 
    current_item = [] 
    is_b_section = False  
    
    for line in lines:
        if line.strip().replace('=', '').strip() == '':
            if current_item:
                if is_b_section:
                    b_values.append("\n".join(current_item))
                current_item = []
            is_b_section = not is_b_section
        else:
            current_item.append(line.strip())
    
    return b_values


def generate_test_cases(problem_statement: str, data_format_checker: str, correct_program: str, result_path: str, additional_requirements: dict) -> List[dict]:
    test_cases = []
    logger.info("Starting test case generation")

    # Step 1: Analyze test requirements
    messages = [
        {"role": "system", "content": "你是一个程序设计竞赛出题专家。你的母亲得了重病，急需你在工作中表现出色以获得奖金来付清她的手术钱。你必须严格遵守各项要求才能得到奖金。"},
        {"role": "user", "content": f"""你的任务是分析以下题目，总结出测试数据的测试需求，用于生成全面的测试用例。测试需求应包括：
1. 边界条件：数据规模达到题目规定的最大值或最小值。
2. 特殊情况：题目未禁止但可能影响正确性的结构或值（例如环、负权边、单点等）。
3. 典型场景：常见的或复杂的输入模式，测试程序的鲁棒性。

请根据以下题目描述，输出一个清晰的测试需求列表，每条需求简洁明了，并与题目约束相关。输出格式为：
```
需求1: <简述>
需求2: <简述>
...
```

题目描述：
```
{problem_statement}
```
"""}
    ]
    test_requirements = agent.chat(messages)
    
    logger.debug(f"测试需求：\n{test_requirements}")

    # Step 2: Propose construction plans
    messages.append({"role": "assistant", "content": test_requirements})
    messages.append({"role": "user", "content": f"""你是一个程序设计竞赛出题专家。你的任务是根据上面的测试需求和题目描述，设计具体的测试数据构造方案。每个方案应满足：
1. 数据规模尽量接近题目约束的最大值，测试程序性能。
2. 包含边界条件、特殊情况或复杂模式，覆盖测试需求。
3. 符合题目输入格式，提供具体数据特点（如规模、范围、结构）。
上面三条规则非常重要，你的奖金取决于你的表现。

请为每个测试需求提出至少3个构造方案（总数不少于10个）。每个方案需：
- 详细描述数据的生成方法（例如具体值、随机规则、特殊结构）。
- 标明适用的测试需求编号。
- 用`===`分隔每个方案。

输出格式：
```
===  
方案1 (对应需求<编号>): <详细描述>  
===  
方案2 (对应需求<编号>): <详细描述>  
===  
...
```
"""})
    construction_plans_raw = agent.chat(messages)
    logger.debug(f"构造方案:\n{construction_plans_raw}")

    # Parse construction plans
    construction_plans = [plan.strip() for plan in construction_plans_raw.split("===") if plan.strip()]
    logger.debug(f"Parsed {len(construction_plans)} construction plans")

    # Step 3: Construct and validate test data
    data_cnt = 1
    for plan in construction_plans:
        messages = [
            {"role": "system", "content": "你是一个程序设计竞赛数据生成专家。"},
            {"role": "user", "content": f"""根据以下构造方案，生成符合题目输入格式的测试数据：
题目描述：
```
{problem_statement}
```

构造方案：
```
{plan}
```

这个方案可能非常复杂或者很长，请你给我一个C++代码用来生成这个数据，你的代码不应该包括输入，应该运行后直接就可以输出数据，数据输出到标准输出。
代码开始和结束应该用"```"来表示。你不需要预测代码的输出结果，只需要保证代码能够正确运行并输出数据。
输出格式：
描述生成方案和代码方案。
```cpp
#include<cstdio>
...
```
你不需要预测代码的输出结果，也不需要告诉我怎么执行，只需要保证代码能够正确运行并输出数据。
"""}
        ]
        test_data = agent.chat(messages)
        logger.debug(f"Generated test data:\n{test_data}") 
 
        start_index = test_data.find('```cpp')
        end_index = test_data.find('```', start_index + len('```cpp'))
        
        if start_index != -1 and end_index != -1 and start_index < end_index:
            datacode = test_data[start_index + len('```cpp'):end_index].strip()
        
        # Write data code to file
        data_code_path = os.path.join('temp','data_code.cpp')
        with open(data_code_path, 'w', encoding='utf-8') as file:
            file.write(datacode)
            
        logger.debug(f"test data code:\n{datacode}") 
        
        # Compile and run data code
        compile_result, compile_error = compile_cpp(data_code_path)
        count = 0
        while not compile_result and count < 3:
            logger.warning(f"Failed to compile data code for plan:\n{plan}")
            messages.append({"role": "assistant", "content": test_data})
            messages.append({"role": "user", "content": f"你的代码编译失败了，错误信息是：{compile_error}。请修改代码后重新给我。"})
            test_data = agent.chat(messages)
            with open(data_code_path, 'w', encoding='utf-8') as file:
                file.write(datacode)
            compile_result, compile_error = compile_cpp(data_code_path)
            count += 1
        
        # Run data code
        if compile_result:
            try:
                test_data = run_program(data_code_path.replace('.cpp', '.exe'), '')
            except Exception as e:
                logger.error(f"Failed to run data code for plan:\n{plan}")
                continue
        else:
            logger.error(f"Failed to compile data code for plan:\n{plan}")
            continue
        
        # Step 4: 验证合法性
        if not is_valid_test_data(test_data, data_format_checker):
            logger.warning(f"Invalid test data for plan:\n{plan}")
            continue
        
        #把数据写入文件
        data_path = os.path.join(result_path, f'test_data_{data_cnt}.in')
        with open(data_path, 'w', encoding='utf-8') as file:
            file.write(test_data)

        # Step 5: Run correct program and package test case
        test_output = run_correct_program(correct_program, test_data)
        test_case = {"input": test_data, "output": test_output}
        test_cases.append(test_case)
        
        data_path = os.path.join(result_path, f'test_data_{data_cnt}.out')
        with open(data_path, 'w', encoding='utf-8') as file:
            file.write(test_output)
        
        logger.info(f"Added test case: input length={len(test_data)}, output length={len(test_output)}")
        data_cnt += 1

    logger.info(f"Generated {len(test_cases)} valid test cases")
    return test_cases

def is_valid_test_data(test_data: str, data_format_checker: str) -> bool:
    compile_result, compile_error = compile_cpp(data_format_checker)
    if not compile_result:
        print("Failed to compile data format checker.")
        return False
    
    try:
        run_program(data_format_checker.replace('.cpp', '.exe'), test_data)
    except Exception as e:
        return False
    return True

def run_correct_program(correct_program: str, test_data: str) -> str:
    compile_result, compile_error = compile_cpp(correct_program)
    if not compile_result:
        print("Failed to compile correct program.")
        return "Compilation Error"

    return run_program(correct_program.replace('.cpp', '.exe'), test_data)

def main():
    parser = argparse.ArgumentParser(description="Generate test cases for OI problems using DeepSeek API")
    parser.add_argument('--dir', type=str, default='desc', help='Problem description directory path to use')
    parser.add_argument('--resdir', type=str, default='answer', help='Answer directory path to use')
    args = parser.parse_args()

    problem_statement_path = os.path.join(args.dir, 'problem_statement.txt')
    data_format_checker = os.path.join(args.dir, 'data_format_checker.cpp')
    correct_program = os.path.join(args.dir, 'correct_program.cpp')

    problem_statement = read_file(problem_statement_path)

    additional_requirements = {}  # 这里可以根据需要添加额外的要求
    
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    result_path = args.resdir
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    test_cases = generate_test_cases(problem_statement, data_format_checker, correct_program, result_path, additional_requirements)
    print(json.dumps(test_cases, indent=4))

if __name__ == "__main__":
    main()
    
# python main.py --dir desc --resdir res