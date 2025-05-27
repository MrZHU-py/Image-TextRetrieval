"""
extract_text.py

从指定 JSON 文件中提取所有条目的某个字段（如 text），
并写入 caption.txt 文件，每行对应一个字段值。

用法:
    python extract_text.py <字段名称> <JSON 文件路径>
例如:
    python extract_text.py text C:\\Users\\Mr.Zhu\\Desktop\\ICR\\ICR\\train\\long_itr_train.json
"""
import argparse
import json
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="从 JSON 文件中提取指定字段，写入 caption.txt"
    )
    parser.add_argument(
        "field",
        help="要提取的字段名称，例如 text"
    )
    parser.add_argument(
        "input_path",
        help="JSON 文件路径，文件内容按行存储单个 JSON 对象"
    )
    parser.add_argument(
        "--output",
        default="caption.txt",
        help="输出文件名，默认为 caption.txt"
    )
    return parser.parse_args()


def extract_field(field: str, input_path: str, output_path: str):
    # 确保输入文件存在
    if not os.path.isfile(input_path):
        print(f"错误：文件不存在: {input_path}")
        sys.exit(1)

    count = 0
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"跳过无效 JSON 行: {e}")
                continue
            # 提取字段值
            if field in data:
                value = data[field]
                fout.write(str(value).replace('\n', ' ') + "\n")
                count += 1
            else:
                print(f"行中不包含字段 '{field}'，已跳过。内容: {line}")
    print(f"已提取 {count} 条字段 '{field}' 到文件: {output_path}")


def main():
    args = parse_args()
    extract_field(args.field, args.input_path, args.output)

if __name__ == '__main__':
    main()
