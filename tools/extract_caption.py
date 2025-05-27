"""
extract_caption.py

从已清洗的文本文件中提取每行内容，即每行的 tab 后文本。
如果行尾缺少中文标点（句号、问号、感叹号等），则补充句号。

用法:
    python extract_caption.py <文件路径> [--output <输出文件>]
示例:
    python extract_caption.py COCO_captions.txt --output cleaned_captions.txt
"""
import argparse
import os
import sys
import re

def parse_args():
    parser = argparse.ArgumentParser(
        description="从已清洗的文本文件中提取纯文本并补全标点"
    )
    parser.add_argument(
        "input_path",
        help="输入文件路径，每行格式如 ID	文本"
    )
    parser.add_argument(
        "--output", "-o",
        default="captions.txt",
        help="输出文件名，默认 captions.txt"
    )
    return parser.parse_args()

def ensure_ending_punct(text: str) -> str:
    # 中文常见结束标点
    if re.search(r'[。！？]$', text):
        return text
    return text + '。'

def extract_captions(input_path: str, output_path: str):
    if not os.path.isfile(input_path):
        print(f"错误：文件不存在 {input_path}")
        sys.exit(1)

    count = 0
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            parts = line.strip().split("	", 1)
            if len(parts) != 2:
                continue
            text = parts[1].strip()
            text = ensure_ending_punct(text)
            fout.write(text + "\n")
            # 统计处理的行数
            count += 1
    print(f"已处理 {count} 行，结果写入 {output_path}")

if __name__ == '__main__':
    args = parse_args()
    extract_captions(args.input_path, args.output)
