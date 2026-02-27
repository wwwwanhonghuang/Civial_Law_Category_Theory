import argparse
import os
from collections import defaultdict

def read_items_from_file(file_path):
    """
    从文件中读取条目，每行一个条目
    """
    items = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # 跳过空行
                    items.append(line)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return items

def parse_list(file_list_arg):
    """
    解析文件列表参数，支持文件和目录
    返回所有要处理的文件路径列表
    """
    files_to_process = []
    for item in file_list_arg:
        if os.path.isfile(item):
            files_to_process.append(item)
        elif os.path.isdir(item):
            # 如果是目录，获取目录下所有文件
            for root, dirs, filenames in os.walk(item):
                for filename in filenames:
                    files_to_process.append(os.path.join(root, filename))
        else:
            print(f"Warning: {item} is not a valid file or directory")
    return files_to_process

def vote_selection(file_list, ratio=2/3, output_file=None, verbose=False):
    """
    从多个文件中读取条目，选择出现次数超过比例阈值的条目
    
    Args:
        file_list: 要处理的文件列表
        ratio: 阈值比例 (默认 2/3)
        output_file: 输出文件路径 (可选)
        verbose: 是否打印详细信息
    """
    # 读取所有文件中的条目
    all_items = []
    file_item_counts = []
    
    for file_path in file_list:
        items = read_items_from_file(file_path)
        all_items.extend(items)
        file_item_counts.append((file_path, items))
        if verbose:
            print(f"Read {len(items)} items from {file_path}")
    
    # 统计每个条目出现的次数
    item_vote_count = defaultdict(int)
    for file_path, items in file_item_counts:
        # 使用set去除单个文件内的重复条目
        unique_items = set(items)
        for item in unique_items:
            item_vote_count[item] += 1
    
    # 计算阈值
    threshold = len(file_list) * ratio
    if verbose:
        print(f"\nTotal files: {len(file_list)}")
        print(f"Threshold: {threshold:.2f} ({ratio:.1%})")
    
    # 筛选达到阈值的条目
    selected_items = []
    for item, count in item_vote_count.items():
        if count >= threshold:
            selected_items.append(item)
    
    # 按字母顺序排序，使输出更整齐
    selected_items.sort()
    
    # 输出结果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in selected_items:
                f.write(item + '\n')
        print(f"Selected {len(selected_items)} items saved to {output_file}")
    else:
        print(f"\nSelected {len(selected_items)} items (appeared in >= {ratio:.1%} of files):")
        for item in selected_items:
            print(item)
    
    # 打印统计信息
    if verbose:
        print(f"\nVote statistics:")
        print(f"Total unique items: {len(item_vote_count)}")
        print(f"Items meeting threshold: {len(selected_items)}")
        
        # 显示投票分布
        vote_distribution = defaultdict(int)
        for count in item_vote_count.values():
            vote_distribution[count] += 1
        
        print("\nVote distribution:")
        for votes in sorted(vote_distribution.keys()):
            count = vote_distribution[votes]
            percentage = count / len(item_vote_count) * 100
            print(f"  {votes}/{len(file_list)} votes: {count} items ({percentage:.1f}%)")
    
    return selected_items

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Vote selection from multiple files - select items appearing in > threshold% of files')
    parser.add_argument("--file_list", nargs='+', required=True, 
                       help="List of files or directories containing items to vote on")
    parser.add_argument("--ratio", default=2/3, type=float, 
                       help="Vote threshold ratio (default: 2/3)")
    parser.add_argument("--output", required=False, type=str, default=None,
                       help="Output file path (optional)")
    parser.add_argument("--verbose", action="store_true",
                       help="Print verbose information")
    
    args = parser.parse_args()
    
    # 解析文件列表，获取所有要处理的文件
    files_to_process = parse_list(args.file_list)
    
    if not files_to_process:
        print("No files found to process!")
        exit(1)
    
    print(f"Found {len(files_to_process)} files to process")
    
    # 执行投票选择
    selected = vote_selection(files_to_process, args.ratio, args.output, args.verbose)