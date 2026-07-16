# -*- coding: utf-8 -*-
"""Markdown 处理辅助函数"""
import os
import re
from typing import Dict, List, Optional, Tuple


def read_file(filepath: str) -> str:
    """读取文件内容"""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_section(content: str, header_pattern: str) -> Optional[str]:
    """从 Markdown 内容中提取指定章节"""
    if not content:
        return None

    lines = content.split("\n")
    result = []
    in_section = False
    header_re = re.compile(header_pattern)

    for line in lines:
        if header_re.match(line):
            in_section = True
            result.append(line)
            continue
        if in_section:
            # 遇到相同或更高级别标题时停止
            if re.match(r"^#{1,3}\s+", line) and not header_re.match(line):
                if line.startswith("# ") or (line.startswith("## ") and not line.startswith("####")):
                    break
            result.append(line)

    return "\n".join(result).strip() if result else None


def extract_images(content: str) -> List[Tuple[str, str]]:
    """提取 Markdown 中的图片引用
    :return: [(alt_text, path), ...]
    """
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    return pattern.findall(content)


def remove_images(content: str) -> str:
    """移除所有图片引用"""
    pattern = re.compile(r"!\[[^\]]*\]\([^)]+\)\s*")
    return pattern.sub("", content).strip()


def rewrite_image_paths(content: str, old_prefix: str, new_prefix: str) -> str:
    """重写图片路径前缀"""
    pattern = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")

    def replace(match):
        alt = match.group(1)
        path = match.group(2)
        suffix = match.group(3)
        if path.startswith(old_prefix):
            new_path = new_prefix + path[len(old_prefix):]
            return alt + new_path + suffix
        return match.group(0)

    return pattern.sub(replace, content)


def split_by_h1(content: str) -> Dict[str, str]:
    """按一级标题分割 Markdown"""
    result = {}
    current_title = "preamble"
    current_content = []

    for line in content.split("\n"):
        if line.startswith("# ") and not line.startswith("## "):
            if current_content:
                result[current_title] = "\n".join(current_content).strip()
            current_title = line[2:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        result[current_title] = "\n".join(current_content).strip()

    return result


def split_by_h2(content: str) -> List[Tuple[str, str]]:
    """按二级标题分割 Markdown"""
    result = []
    current_title = ""
    current_content = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_content or current_title:
                result.append((current_title, "\n".join(current_content).strip()))
            current_title = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        result.append((current_title, "\n".join(current_content).strip()))

    return result


def ensure_blank_lines(content: str) -> str:
    """确保标题前后有空行"""
    lines = content.split("\n")
    result = []
    for i, line in enumerate(lines):
        if i > 0 and line.startswith("#") and not lines[i - 1].strip() == "":
            result.append("")
        result.append(line)
        if line.startswith("#") and i < len(lines) - 1 and not lines[i + 1].strip() == "":
            result.append("")
    return "\n".join(result)


def get_md_files(directory: str) -> List[str]:
    """获取目录下所有 Markdown 文件"""
    if not os.path.exists(directory):
        return []
    md_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".md"):
                md_files.append(os.path.join(root, f))
    return sorted(md_files)


def list_images_in_dir(directory: str) -> List[str]:
    """获取目录下所有 PNG 图片"""
    if not os.path.exists(directory):
        return []
    images = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                images.append(os.path.join(root, f))
    return sorted(images)