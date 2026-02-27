#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DOC File Reader

This module provides functions to read text from .doc files.
Requires pywin32 on Windows or antiword on Linux/Mac.
"""

import os
import subprocess
import sys

def read_doc_plaintext_win32(file_path):
    """
    使用 win32com 读取 .doc 文件（Windows only）
    需要安装 pywin32: pip install pywin32
    """
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.visible = False
        
        try:
            doc = word.Documents.Open(os.path.abspath(file_path))
            content = doc.Content.Text
            doc.Close()
            return content
        except Exception as e:
            raise Exception(f"Error opening .doc file with Word: {e}")
        finally:
            word.Quit()
            
    except ImportError:
        raise Exception("pywin32 not installed. Please run: pip install pywin32")
    except Exception as e:
        raise Exception(f"Error reading .doc file with win32com: {e}")

def read_doc_plaintext_antiword(file_path):
    """
    使用 antiword 读取 .doc 文件（Linux/Mac）
    需要安装 antiword: 
        Ubuntu/Debian: sudo apt-get install antiword
        Mac: brew install antiword
    """
    try:
        # 检查 antiword 是否可用
        result = subprocess.run(['antiword', '-v'], 
                              capture_output=True, 
                              text=True)
        if result.returncode != 0:
            raise Exception("antiword not found")
            
        # 使用 antiword 读取 .doc 文件
        result = subprocess.run(['antiword', file_path], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"antiword error: {result.stderr}")
            
    except FileNotFoundError:
        raise Exception("antiword not installed. Please install antiword first.")
    except Exception as e:
        raise Exception(f"Error reading .doc file with antiword: {e}")

def read_doc_plaintext_catdoc(file_path):
    """
    使用 catdoc 读取 .doc 文件（Linux/Mac）
    需要安装 catdoc:
        Ubuntu/Debian: sudo apt-get install catdoc
        Mac: brew install catdoc
    """
    try:
        # 检查 catdoc 是否可用
        result = subprocess.run(['catdoc', '-v'], 
                              capture_output=True, 
                              text=True)
        
        # 使用 catdoc 读取 .doc 文件
        result = subprocess.run(['catdoc', file_path], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"catdoc error: {result.stderr}")
            
    except FileNotFoundError:
        raise Exception("catdoc not installed. Please install catdoc first.")
    except Exception as e:
        raise Exception(f"Error reading .doc file with catdoc: {e}")

def read_doc_plaintext_textutil(file_path):
    """
    使用 textutil 读取 .doc 文件（Mac only）
    textutil 是 Mac OS X 自带工具
    """
    try:
        # textutil 将 .doc 转换为 .txt
        temp_txt = file_path + '_temp.txt'
        
        result = subprocess.run([
            'textutil', 
            '-convert', 'txt', 
            '-output', temp_txt, 
            file_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # 读取生成的临时txt文件
            with open(temp_txt, 'r', encoding='utf-8') as f:
                content = f.read()
            # 删除临时文件
            os.remove(temp_txt)
            return content
        else:
            raise Exception(f"textutil error: {result.stderr}")
            
    except Exception as e:
        raise Exception(f"Error reading .doc file with textutil: {e}")

def read_doc_plaintext(file_path):
    """
    主函数：读取 .doc 文件并返回文本内容
    根据操作系统自动选择合适的方法
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.lower().endswith('.doc'):
        raise ValueError(f"File is not a .doc file: {file_path}")
    
    system = sys.platform
    
    # Windows 系统
    if system == 'win32':
        try:
            return read_doc_plaintext_win32(file_path)
        except Exception as e:
            print(f"Win32 method failed: {e}")
            print("Trying alternative methods...")
    
    # Mac 系统
    if system == 'darwin':
        # 尝试 textutil (Mac自带)
        try:
            return read_doc_plaintext_textutil(file_path)
        except Exception as e:
            print(f"textutil method failed: {e}")
        
        # 尝试 antiword
        try:
            return read_doc_plaintext_antiword(file_path)
        except Exception as e:
            print(f"antiword method failed: {e}")
    
    # Linux 系统
    if system.startswith('linux'):
        # 尝试 antiword
        try:
            return read_doc_plaintext_antiword(file_path)
        except Exception as e:
            print(f"antiword method failed: {e}")
        
        # 尝试 catdoc
        try:
            return read_doc_plaintext_catdoc(file_path)
        except Exception as e:
            print(f"catdoc method failed: {e}")
    
    raise Exception("No suitable method found to read .doc file")

# 简化版本：如果只需要基本功能，可以使用这个函数
def read_doc_simple(file_path):
    """
    简单的 .doc 文件读取器
    尝试使用二进制模式读取并提取文本（不完美，但不需要外部依赖）
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 尝试提取文本内容（非常简化的方法）
        # 这种方法只能提取部分文本，不推荐用于重要文档
        text = []
        i = 0
        while i < len(raw_data):
            # 寻找可打印字符
            if 32 <= raw_data[i] <= 126:  # ASCII可打印字符
                start = i
                while i < len(raw_data) and 32 <= raw_data[i] <= 126:
                    i += 1
                text.append(raw_data[start:i].decode('ascii', errors='ignore'))
            else:
                i += 1
        
        return '\n'.join(text)
    except Exception as e:
        raise Exception(f"Simple read failed: {e}")