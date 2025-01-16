from openai import OpenAI
import argparse
import os
from dotenv import load_dotenv
import subprocess
import json
from typing import Any, Dict, List, Optional, Union
from loguru import logger
import time
from sample import *

load_dotenv()
api_key = os.getenv('API_KEY')

logger.add("tcg.log", rotation="50 MB", retention="10 days", level="DEBUG")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)
# [
#             {"role": "system", "content": "You are a helpful assistant"},
#             {"role": "user", "content": content},
#         ]
def chat(messages: List[str]) -> str:
    start_time = time.time()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=8192,
        temperature=0.7,
        stream=False
    )

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Time taken by api: {elapsed_time:.2f} seconds")

    return response.choices[0].message.content

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def compile_cpp(cpp_file_path: str) -> bool:
    try:
        output_file_path = cpp_file_path.replace('.cpp', '.exe')
        subprocess.run(['g++', cpp_file_path, '-o', output_file_path, '-std=gnu++11'], check=True)
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to compile {cpp_file_path}")
        return False

def run_program(program_path: str, input_data: str) -> str:
    try:
        result = subprocess.run([program_path], input=input_data, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()
    
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


def generate_test_cases(problem_statement: str, data_format_checker: str, correct_program: str, additional_requirements: dict) -> List[dict]:
    test_cases = []

    logger.info("start generate")

    # Step 1: 分析题意
    # messages = f"请分析以下题目的测试需求：\n{problem_statement}请总结出测试数据的测试需求。"
    messages = [{"role": "system", "content": "你是一个经验丰富的程序设计竞赛出题人。"},
                {"role": "user", "content": 
f"""请分析以下题目的测试需求，并总结出测试数据的测试需求。比如，如果寻找图的最短路，测试需求可能包括：
1. 图的规模达到题目中规定的最大值；
2. 图足够复杂，包含负权边、环等各种题目没有反对的情况；
3. 图是一个特殊的情况，比如只有一个点、只有一条边等；
4. 图是一个特殊的情况，比如是一个树、是一个DAG等。
请总结出测试数据的测试需求，以便生成测试数据。
注意：
测试需求不是详细的测试点要求，而是测试程序是否正确的一些基础情况、边界条件和特殊情况的总结。
以下是题目的具体描述：
{problem_statement}
"""},]

    test_requirements = chat(messages)
    
    logger.debug(f"测试需求：{test_requirements}")

    # Step 2: 提出构造方案
    messages += [{"role": "assistant", "content": test_requirements}]
    messages += [{"role": "user", "content": 
f"""请给出测试数据的构造方案。
注意：
- 1. 构造方案是测试点数据的具体的构造方法。
- 2. 构造方案要包含具体的构造方案，对于数据规模较大的测试点，应当是数据的特点、规律等。
- 3. 构造方案可以是一些特殊情况，也可以是一些边界情况。
- 4. 构造方案可以是一些随机数据，也可以是一些特殊数据。
- 5. 一个测试点不光可以包含一个重点，可以同时包含多个生成数据的策略。
- 6. 每个测试点的 ** 数据规模应当尽可能的大 ** ，以在尽量多的测试点中测试程序的性能。
- 7. 你不需要考虑预期输出，也不需要测试程序能否处理不正确数据格式。你的输入构造方案应该符合题目中的数据格式。

在输出方案时，你应当注意：
- 1. 方案应当尽可能详细具体，以便生成测试数据。在方案中应该包括一些关键数据的值，比如图的规模、边权的范围等。
- 2. 请你尽可能多的提出构造方案。对于之前提到的每个策略或情况，都生成 ** 5条以上 ** 的方案。
- 3. 你必须确保之前你提到的方案都输出相应的方案，否则你的方案可能不够全面。
- 4. 在输出方案之前，请你先思考一下，这些方案是否能够覆盖测试需求中提到的情况。

最后你要注意：你必须在每一个方案前后都输出一行全是“=”的分隔符，以便我们区分不同的方案。

以下是测试需求的具体描述：
- 样例题目描述：
{sample_problem_statement}
- 样例输出：
{sample_output}
这里的样例输出是一个较短的示例，你应该参考他的格式，根据当前的题目的具体情况和测试需求生成更多的方案。
"""}]

    construction_plans = chat(messages=messages)

    logger.debug(f"构造方案：{construction_plans}")

    # 通过写prompt让api返回特定格式的方案，再转换为list格式
    exit()
    # Step 3: 构造数据
    for plan in construction_plans:
        messages = f"根据以下构造方案：\n{plan}请构造符合以下数据格式的数据：\n{data_format_checker}"
        test_data = chat("\n".join(messages))

        # Step 4: 验证合法性
        if not is_valid_test_data(test_data, data_format_checker):
            continue

        # Step 5: 整理打包
        test_case = {
            "input": test_data,
            "output": run_correct_program(correct_program, test_data)
        }
        test_cases.append(test_case)

    return test_cases

def is_valid_test_data(test_data: str, data_format_checker: str) -> bool:
    checker_output_path = 'data_format_checker'
    if not compile_cpp(data_format_checker, checker_output_path):
        print("Failed to compile data format checker.")
        return False

    result = run_program(checker_output_path, test_data)
    return result == "Valid"

def run_correct_program(correct_program: str, test_data: str) -> str:
    correct_output_path = 'correct_program'
    if not compile_cpp(correct_program, correct_output_path):
        print("Failed to compile correct program.")
        return "Compilation Error"

    return run_program(correct_output_path, test_data)

def main():
    parser = argparse.ArgumentParser(description="Generate test cases for OI problems using DeepSeek API")
    parser.add_argument('--dir', type=str, default='desc', help='Problem description directory path to use')
    parser.add_argument('--ansdir', type=str, default='answer', help='Answer directory path to use')
    args = parser.parse_args()

    problem_statement_path = os.path.join(args.dir, 'problem_statement.txt')
    data_format_checker = os.path.join(args.dir, 'data_format_checker.cpp')
    correct_program = os.path.join(args.ansdir, 'correct_program.cpp')

    problem_statement = read_file(problem_statement_path)

    additional_requirements = {}  # 这里可以根据需要添加额外的要求

    test_cases = generate_test_cases(problem_statement, data_format_checker, correct_program, additional_requirements)
    print(json.dumps(test_cases, indent=4))

if __name__ == "__main__":
    main()