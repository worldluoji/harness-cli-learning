# -*- coding: utf-8 -*-
"""运行财务可视化的 wrapper，先注册中文字体再调用 visualize_financial.py"""
import sys
import os

# 1. 强制设置中文字体
sys.path.insert(0, os.path.dirname(__file__))
import setup_fonts  # noqa: F401

# 2. 切换到 script 目录
skill_dir = "/Users/Admin/workspace/python/claude-agent-sdk-demo/claude-agent/.claude/skills/financial_visualization/scripts"
os.chdir(skill_dir)
sys.path.insert(0, skill_dir)

# 3. Monkey-patch CHINESE_FONTS 之前，先 import
import chart_generator
# 覆盖默认的中文字体列表（必须包含系统中已有的中文字体名）
chart_generator.CHINESE_FONTS = [
    "Hiragino Sans GB",
    "STHeiti",
    "STHeiti Medium",
    "STHeiti Light",
    "PingFang SC",
    "Heiti SC",
    "SimHei",
    "Microsoft YaHei",
    "Noto Sans CJK JP",
    "DejaVu Sans",
]
# 同时也修改 setup_chinese_font 的实现以使用 sans-serif 列表
_original_setup = chart_generator.setup_chinese_font

def patched_setup_chinese_font():
    import matplotlib.pyplot as plt
    plt.rcParams["axes.unicode_minus"] = False
    # 直接使用 sans-serif 列表（已在 setup_fonts 中设置）
    plt.rcParams["font.family"] = "sans-serif"
    return "sans-serif (CJK fallback)"

chart_generator.setup_chinese_font = patched_setup_chinese_font

# 4. 模拟 __main__ 运行
import visualize_financial
visualize_financial.main()