#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert Raw Law to Plaintext

This script reads a list of selected law titles and extracts the corresponding
law texts from the raw laws folder (title.docx or title.doc), saving them as plain text files.
"""

import argparse
import os
import re
from pathlib import Path

# 导入文档读取器
from utils.readers.docx_reader import read_docx_plaintext
from utils.readers.doc_reader import read_doc_plaintext

def read_titles_from_file(titles_file):
    """
    从文件中读取法律标题列表
    每行一个标题，忽略空行和注释行（以#开头）
    """
    titles = []
    try:
        with open(titles_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    titles.append(line)
        print(f"Read {len(titles)} titles from {titles_file}")
        return titles
    except Exception as e:
        print(f"Error reading titles file {titles_file}: {e}")
        return []

def find_law_file(title, raw_laws_folder):
    """
    根据标题在原始法律文件夹中查找对应的文件
    支持 .docx 和 .doc 格式
    文件名格式为: title.docx 或 title.doc
    """
    # 尝试不同的扩展名
    extensions = ['.docx', '.doc']
    
    # 首先在当前目录查找
    for ext in extensions:
        filename = title + ext
        file_path = os.path.join(raw_laws_folder, filename)
        
        if os.path.isfile(file_path):
            return file_path, ext[1:]  # 返回文件路径和扩展名（不带点）
    
    # 如果没有直接找到，尝试递归搜索
    for root, dirs, files in os.walk(raw_laws_folder):
        for ext in extensions:
            filename = title + ext
            if filename in files:
                return os.path.join(root, filename), ext[1:]
    
    return None, None

def clean_filename(title):
    """
    从标题生成安全的文件名（保留原格式，只移除不允许的字符）
    """
    # 移除或替换不允许的文件名字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', title)
    # 限制文件名长度
    if len(filename) > 200:
        name_part = filename[:200]
        # 确保不截断在中间
        last_underscore = name_part.rfind('_')
        if last_underscore > 0:
            filename = filename[:last_underscore]
        else:
            filename = name_part
    return filename + '.txt'

def save_plaintext(content, output_path):
    """
    保存纯文本内容到文件
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  Error saving to {output_path}: {e}")
        return False

def append_to_merged_file(content, title, merged_file_path):
    """
    将内容追加到合并文件中，并添加标题分隔符
    """
    try:
        with open(merged_file_path, 'a', encoding='utf-8') as f:
            # 添加分隔符和标题
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"# {title}\n")
            f.write("=" * 80 + "\n\n")
            f.write(content)
            f.write("\n\n")
        return True
    except Exception as e:
        print(f"  Error appending to merged file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert selected raw laws (doc/docx) to plaintext files')
    parser.add_argument("--file_titles_selected_laws", required=True, type=str,
                       help="Path to the file containing selected law titles (one per line)")
    parser.add_argument("--output_folder", required=False, type=str, default="./data/law_text",
                       help="Output folder for plaintext law files (default: ./data/law_text)")
    parser.add_argument("--raw_laws_folder", required=True, type=str,
                       help="Folder containing raw law .doc/.docx files")
    parser.add_argument("--output_merged_file", action="store_true",
                       help="If set, concatenate all files into a merged.txt file")
    parser.add_argument("--verbose", action="store_true",
                       help="Print verbose information")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Converting Selected Laws (doc/docx) to Plaintext")
    print("=" * 60)
    
    # 读取选定的法律标题
    titles = read_titles_from_file(args.file_titles_selected_laws)
    if not titles:
        print("No titles found. Exiting.")
        return
    
    # 确保输出文件夹存在
    os.makedirs(args.output_folder, exist_ok=True)
    
    # 如果需要合并文件，初始化合并文件
    merged_file_path = None
    if args.output_merged_file:
        merged_file_path = os.path.join(args.output_folder, "merged.txt")
        # 清空或创建合并文件
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            f.write("# Merged Law Texts\n")
            f.write(f"# Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total laws: {len(titles)}\n")
            f.write("# " + "=" * 70 + "\n\n")
        print(f"Merged file will be saved to: {merged_file_path}")
    
    # 统计信息
    found_count = 0
    not_found_count = 0
    error_count = 0
    docx_count = 0
    doc_count = 0
    
    # 创建日志文件
    log_file = os.path.join(args.output_folder, "conversion_log.txt")
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Law Title Conversion Log\n")
        log.write("=" * 50 + "\n\n")
        log.write(f"Raw laws folder: {args.raw_laws_folder}\n")
        log.write(f"Supported formats: .docx, .doc\n")
        log.write(f"Merge to single file: {args.output_merged_file}\n\n")
        
        # 处理每个标题
        for i, title in enumerate(titles, 1):
            print(f"\n[{i}/{len(titles)}] Processing: {title}")
            log.write(f"\n--- Processing: {title} ---\n")
            
            # 查找对应的原始法律文件 (title.docx 或 title.doc)
            file_path, file_ext = find_law_file(title, args.raw_laws_folder)
            
            if file_path:
                print(f"  Found: {file_path} (format: {file_ext})")
                log.write(f"  Found: {file_path} (format: {file_ext})\n")
                
                try:
                    # 根据文件扩展名选择合适的读取器
                    if file_ext == 'docx':
                        content = read_docx_plaintext(file_path)
                        docx_count += 1
                    elif file_ext == 'doc':
                        content = read_doc_plaintext(file_path)
                        doc_count += 1
                    else:
                        raise Exception(f"Unsupported file format: {file_ext}")
                    
                    if content and content.strip():
                        # 生成输出文件名
                        output_filename = clean_filename(title)
                        output_path = os.path.join(args.output_folder, output_filename)
                        
                        # 保存单个文件
                        if save_plaintext(content, output_path):
                            print(f"  Saved to: {output_path}")
                            log.write(f"  Saved to: {output_path}\n")
                            found_count += 1
                            
                            # 如果需要合并，追加到合并文件
                            if merged_file_path:
                                if append_to_merged_file(content, title, merged_file_path):
                                    print(f"  Appended to merged file")
                                else:
                                    print(f"  Warning: Failed to append to merged file")
                        else:
                            print(f"  ERROR: Failed to save file")
                            log.write(f"  ERROR: Failed to save file\n")
                            error_count += 1
                    else:
                        print(f"  ERROR: Extracted content is empty")
                        log.write(f"  ERROR: Extracted content is empty\n")
                        error_count += 1
                        
                except Exception as e:
                    error_msg = str(e)
                    print(f"  ERROR: Failed to read {file_ext} file: {error_msg}")
                    
                    # 提供更友好的错误提示
                    if "antiword" in error_msg or "catdoc" in error_msg:
                        print("  " + "-" * 50)
                        print("  Please install required tools:")
                        print("  Ubuntu/Debian: sudo apt-get install antiword catdoc")
                        print("  CentOS/RHEL:   sudo yum install epel-release && sudo yum install antiword catdoc")
                        print("  macOS:         brew install antiword catdoc")
                        print("  " + "-" * 50)
                    
                    log.write(f"  ERROR: Failed to read {file_ext} file: {error_msg}\n")
                    error_count += 1
            else:
                expected_paths = [
                    os.path.join(args.raw_laws_folder, title + ".docx"),
                    os.path.join(args.raw_laws_folder, title + ".doc")
                ]
                print(f"  NOT FOUND: tried {expected_paths[0]} and {expected_paths[1]}")
                log.write(f"  NOT FOUND: tried {expected_paths[0]} and {expected_paths[1]}\n")
                not_found_count += 1
            
            if args.verbose:
                print(f"  Progress: Found: {found_count}, Not found: {not_found_count}, Errors: {error_count}")
                print(f"  Format stats: .docx: {docx_count}, .doc: {doc_count}")
    
    # 打印总结
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Total titles processed: {len(titles)}")
    print(f"Successfully converted: {found_count}")
    print(f"  - .docx files: {docx_count}")
    print(f"  - .doc files: {doc_count}")
    print(f"Not found: {not_found_count}")
    print(f"Errors: {error_count}")
    print(f"\nOutput folder: {args.output_folder}")
    
    if merged_file_path and found_count > 0:
        # 获取合并文件大小
        file_size = os.path.getsize(merged_file_path)
        print(f"Merged file: {merged_file_path} (size: {file_size} bytes)")
    
    print(f"Log file: {log_file}")
    
    # 创建摘要文件
    summary_file = os.path.join(args.output_folder, "conversion_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("Law Text Conversion Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Titles file: {args.file_titles_selected_laws}\n")
        f.write(f"Raw laws folder: {args.raw_laws_folder}\n")
        f.write(f"Supported formats: .docx, .doc\n")
        f.write(f"Output folder: {args.output_folder}\n")
        f.write(f"Merge to single file: {args.output_merged_file}\n\n")
        f.write(f"Total titles: {len(titles)}\n")
        f.write(f"Successfully converted: {found_count}\n")
        f.write(f"  - .docx files: {docx_count}\n")
        f.write(f"  - .doc files: {doc_count}\n")
        f.write(f"Not found: {not_found_count}\n")
        f.write(f"Errors: {error_count}\n")
        
        if merged_file_path and found_count > 0:
            f.write(f"\nMerged file: {merged_file_path}\n")
            f.write(f"Merged file size: {os.path.getsize(merged_file_path)} bytes\n")
        
        # 列出未找到的文件
        if not_found_count > 0:
            f.write("\n\nFiles not found:\n")
            f.write("-" * 20 + "\n")
            for title in titles:
                file_path, _ = find_law_file(title, args.raw_laws_folder)
                if not file_path:
                    f.write(f"{title}.docx or {title}.doc\n")
    
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()