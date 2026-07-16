#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研报组装主脚本"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import List, Optional

from markdown_helpers import (
    ensure_blank_lines,
    extract_images,
    get_md_files,
    list_images_in_dir,
    read_file,
    remove_images,
)


def parse_args():
    parser = argparse.ArgumentParser(description="组装最终深度研报")
    parser.add_argument("--code", required=True, help="目标公司股票代码")
    parser.add_argument("--name", required=True, help="目标公司名称")
    parser.add_argument("--industry", default="", help="所属行业")
    parser.add_argument("--input-dir", default="/workspace",
                        help="中间报告根目录")
    parser.add_argument("--output-dir", default="/workspace/final_output",
                        help="最终输出目录")
    parser.add_argument("--no-docx", action="store_true",
                        help="跳过 Word 转换")
    return parser.parse_args()


def find_file(base_dir: str, candidates: List[str]) -> Optional[str]:
    """从候选路径中找到第一个存在的文件"""
    for candidate in candidates:
        path = os.path.join(base_dir, candidate)
        if os.path.exists(path):
            return path
    return None


def extract_clean_section(content: str, skip_top_heading: bool = True) -> str:
    """提取内容并去掉顶级标题"""
    if not content:
        return ""
    lines = content.split("\n")
    if skip_top_heading and lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def copy_images_to_output(
    images: List[str],
    output_images_dir: str,
) -> List[str]:
    """复制图片到输出目录，返回新的图片相对路径列表"""
    os.makedirs(output_images_dir, exist_ok=True)
    copied = []
    for src in images:
        if not os.path.exists(src):
            continue
        filename = os.path.basename(src)
        dst = os.path.join(output_images_dir, filename)
        try:
            shutil.copy2(src, dst)
            copied.append(f"./images/{filename}")
        except Exception as e:
            print(f"  [警告] 复制图片失败 {src}: {e}")
    return copied


def normalize_image_paths(content: str, output_dir: str) -> str:
    """把图片路径规范化为 ./images/xxx 格式"""

    def replace(match):
        alt = match.group(1)
        path = match.group(2).strip()
        suffix = match.group(3)

        if path.startswith("http://") or path.startswith("https://"):
            return match.group(0)

        filename = os.path.basename(path)
        if not filename:
            return match.group(0)

        return f"![{alt}](./images/{filename}){suffix}"

    import re

    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)(\s*)")
    return pattern.sub(replace, content)


def build_summary_report(
    args,
    files: dict,
) -> str:
    """生成第一阶段汇总报告（简短版）"""
    lines = []
    lines.append(f"# {args.name}({args.code})财务研报汇总")
    lines.append("")
    lines.append(f"- 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 分析期间: 各章节报告已生成")
    lines.append(f"- 所属行业: {args.industry or '未指定'}")
    lines.append("")
    lines.append("## 一、公司基础信息")
    lines.append("")
    content = read_file(files.get("company_info", ""))
    lines.append(extract_clean_section(content) or "(暂无公司基础信息)")
    lines.append("")
    lines.append("## 二、股权信息")
    lines.append("")
    content = read_file(files.get("shareholder_info", ""))
    lines.append(extract_clean_section(content) or "(暂无股权信息)")
    lines.append("")
    lines.append("## 三、行业与竞争对手")
    lines.append("")
    content = read_file(files.get("industry_info", ""))
    lines.append(extract_clean_section(content) or "(暂无行业信息)")
    lines.append("")
    lines.append("## 四、财务分析与对比")
    lines.append("")
    files_list = [
        files.get("single_analysis"),
        files.get("compare_analysis"),
    ]
    for fp in files_list:
        if fp:
            lines.append(f"### {os.path.basename(os.path.dirname(fp))}")
            lines.append("")
            content = read_file(fp)
            lines.append(extract_clean_section(content) or "")
            lines.append("")
    lines.append("## 五、估值与预测")
    lines.append("")
    content = read_file(files.get("valuation", ""))
    lines.append(extract_clean_section(content) or "(暂无估值报告)")
    lines.append("")
    return "\n".join(lines)


def build_deep_report(
    args,
    files: dict,
    output_dir: str,
) -> str:
    """生成最终深度研报"""
    lines = []
    lines.append(f"# {args.name}({args.code})深度财务研报分析")
    lines.append("")
    lines.append(f"**评级**: 待综合分析后给出")
    lines.append(f"**行业**: {args.industry or '未指定'}")
    lines.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 一、公司概况
    lines.append("## 一、公司概况")
    lines.append("")
    lines.append("### 1.1 公司简介")
    lines.append("")
    company_info = read_file(files.get("company_info", ""))
    cleaned = extract_clean_section(company_info)
    if cleaned:
        lines.append(cleaned)
    else:
        lines.append("(暂无公司基础信息)")
    lines.append("")

    lines.append("### 1.2 主营业务与核心竞争力")
    lines.append("")
    business_info = read_file(files.get("business_info", ""))
    cleaned = extract_clean_section(business_info)
    if cleaned:
        lines.append(cleaned)
    else:
        lines.append("(暂无主营业务信息)")
    lines.append("")

    lines.append("### 1.3 股权结构")
    lines.append("")
    shareholder_info = read_file(files.get("shareholder_info", ""))
    cleaned = extract_clean_section(shareholder_info)
    if cleaned:
        lines.append(cleaned)
    else:
        lines.append("(暂无股权信息)")
    lines.append("")

    # 二、行业分析
    lines.append("## 二、行业分析")
    lines.append("")
    industry_info = read_file(files.get("industry_info", ""))
    if industry_info:
        lines.append(normalize_image_paths(extract_clean_section(industry_info), output_dir))
    else:
        lines.append("(暂无行业信息)")
    lines.append("")

    # 三、财务分析（单公司）
    lines.append("## 三、财务分析")
    lines.append("")
    lines.append("### 3.1 财务趋势分析")
    lines.append("")
    single_report = read_file(files.get("single_analysis", ""))
    if single_report:
        lines.append(normalize_image_paths(extract_clean_section(single_report), output_dir))
    else:
        lines.append("(暂无单公司分析报告)")
    lines.append("")

    # 四、对比分析
    lines.append("## 四、对比分析")
    lines.append("")
    compare_report = read_file(files.get("compare_analysis", ""))
    if compare_report:
        lines.append(normalize_image_paths(extract_clean_section(compare_report), output_dir))
    else:
        lines.append("(暂无对比分析报告)")
    lines.append("")

    # 五、估值与预测
    lines.append("## 五、估值与预测")
    lines.append("")
    valuation = read_file(files.get("valuation", ""))
    cleaned = extract_clean_section(valuation)
    if cleaned:
        lines.append(normalize_image_paths(cleaned, output_dir))
    else:
        lines.append("(暂无估值报告)")
    lines.append("")

    # 六、投资建议
    lines.append("## 六、投资建议")
    lines.append("")
    lines.append("### 6.1 综合评价")
    lines.append("")
    lines.append(f"基于公司基本面、行业地位、财务表现、对比分析和估值结果，")
    lines.append(f"对 {args.name} 进行综合评价。")
    lines.append("")
    lines.append("### 6.2 投资评级")
    lines.append("")
    lines.append("**评级**: 增持 / 中性 (基于综合分析)")
    lines.append("")
    lines.append("### 6.3 主要风险")
    lines.append("")
    lines.append("- 宏观经济波动风险")
    lines.append("- 行业竞争加剧风险")
    lines.append("- 政策变化风险")
    lines.append("- 公司经营风险")
    lines.append("")

    # 七、数据来源与免责声明
    lines.append("## 七、数据来源与免责声明")
    lines.append("")
    lines.append("### 数据来源")
    lines.append("")
    lines.append("1. 财务报表数据：东方财富-数据中心-年报季报-业绩快报")
    lines.append("2. 行业数据：公开行业研究报告及财经数据库")
    lines.append("3. 竞争对手数据：上市公司公开披露的财务报告")
    lines.append("4. 主营业务：互联网公开信息")
    lines.append("")
    lines.append("### 免责声明")
    lines.append("")
    lines.append("本报告由自动化分析流程生成，仅供参考，不构成任何投资建议。")
    lines.append("投资者应根据自身情况独立判断，并自行承担投资风险。")
    lines.append("")

    return "\n".join(lines)


def generate_docx(md_path: str, docx_path: str) -> bool:
    """调用 pandoc 生成 docx"""
    try:
        cmd = [
            "pandoc",
            md_path,
            "-o",
            docx_path,
            "--standalone",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Word 文档已生成: {docx_path}")
            return True
        else:
            print(f"  [警告] pandoc 转换失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("  [警告] 未安装 pandoc，跳过 Word 转换")
        return False


def main():
    args = parse_args()
    args.input_dir = os.path.abspath(args.input_dir)
    args.output_dir = os.path.abspath(args.output_dir)

    os.makedirs(args.output_dir, exist_ok=True)
    images_dir = os.path.join(args.output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    print("=" * 60)
    print("研报组装任务")
    print("=" * 60)
    print(f"目标公司: {args.name} ({args.code})")
    print(f"所属行业: {args.industry}")
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output_dir}")
    print("=" * 60)

    # 1. 定位所有输入文件
    print("\n[1/4] 定位输入文件...")
    files = {
        "company_info": find_file(args.input_dir, [
            f"data/report/公司信息数据.md",
            "data/report/公司信息.md",
        ]),
        "business_info": find_file(args.input_dir, [
            "data/report/主营业务与核心竞争力.md",
            "data/report/主营业务.md",
        ]),
        "shareholder_info": find_file(args.input_dir, [
            "data/report/股东信息数据.md",
            "data/report/股东信息.md",
        ]),
        "industry_info": find_file(args.input_dir, [
            "data/report/竞争对手与行业均值数据.md",
            "data/report/行业分析.md",
        ]),
        "single_analysis": find_file(args.input_dir, [
            f"analyze_agent_outputs/{args.code}_{args.name}/最终分析报告.md",
        ]),
        "compare_analysis": find_file(args.input_dir, [
            f"compare_company_report_outputs/{args.code}_{args.name}_vs_competitors/最终分析报告.md",
        ]),
        "valuation": find_file(args.input_dir, [
            "data/report/估值与预测模型.md",
            "data/report/估值报告.md",
        ]),
    }
    for key, path in files.items():
        if path:
            print(f"  ✅ {key}: {path}")
        else:
            print(f"  ⚠️ {key}: 未找到")

    # 2. 复制所有图片
    print("\n[2/4] 复制图片...")
    all_images = []
    image_dirs = [
        f"analyze_agent_outputs/{args.code}_{args.name}",
        f"compare_company_report_outputs/{args.code}_{args.name}_vs_competitors",
    ]
    for d in image_dirs:
        full_path = os.path.join(args.input_dir, d)
        if os.path.exists(full_path):
            all_images.extend(list_images_in_dir(full_path))
    copied = copy_images_to_output(all_images, images_dir)
    print(f"  复制了 {len(copied)} 张图片到 {images_dir}")

    # 3. 生成汇总报告和深度研报
    print("\n[3/4] 生成 Markdown 研报...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary_md = build_summary_report(args, files)
    summary_path = os.path.join(args.output_dir, f"财务研报汇总_{timestamp}.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    print(f"  ✅ 汇总报告: {summary_path}")

    deep_md = build_deep_report(args, files, args.output_dir)
    deep_path = os.path.join(args.output_dir, f"深度财务研报分析_{timestamp}.md")
    with open(deep_path, "w", encoding="utf-8") as f:
        f.write(deep_md)
    print(f"  ✅ 深度研报: {deep_path}")

    # 4. 可选：转换为 Word
    if not args.no_docx:
        print("\n[4/4] 转换为 Word...")
        docx_path = deep_path.replace(".md", ".docx")
        generate_docx(deep_path, docx_path)
    else:
        print("\n[4/4] 跳过 Word 转换")

    print("\n" + "=" * 60)
    print("✅ 研报组装完成")
    print(f"输出目录: {args.output_dir}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())