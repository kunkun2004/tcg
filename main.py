from openai import OpenAI
import argparse
import os
from dotenv import load_dotenv
import subprocess
import json
from typing import Any, Dict, List, Optional, Union
from loguru import logger
import time

load_dotenv()
api_key = os.getenv('API_KEY')

logger.add("tcg.log", rotation="50 MB", retention="10 days", level="INFO")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

def chat(content: str) -> str:
    start_time = time.time()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": content},
        ],
        max_tokens=4096,
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

def compile_cpp(cpp_file_path: str, output_file_path: str) -> bool:
    try:
        subprocess.run(['g++', cpp_file_path, '-o', output_file_path, '-std=gnu++11'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def run_program(program_path: str, input_data: str) -> str:
    try:
        result = subprocess.run([program_path], input=input_data, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def generate_test_cases(problem_statement: str, data_format_checker: str, correct_program: str, additional_requirements: dict) -> List[dict]:
    test_cases = []

    logger.info("start generate")

    # Step 1: 分析题意
    messages = f"请分析以下题目的测试需求：\n{problem_statement}请总结出测试数据的测试需求。"

    test_requirements = chat("\n".join(messages))

    logger.info(f"测试需求：{test_requirements}")

    # Step 2: 提出构造方案
    messages = f"根据以下测试需求：\n{test_requirements}请提出测试数据的构造方案。"
    construction_plans = chat("\n".join(messages)).split("\n")

    logger.info(f"构造方案：{construction_plans}")

    # 通过写prompt让api返回特定格式的方案，再转换为list格式

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
    parser.add_argument('--dir', type=str, required=True, help='Problem description directory path to use')
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