# -*- coding: utf-8 -*-
"""强制设置中文字体（matplotlib 渲染支持中文）"""
import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# 添加已知的中文字体
font_paths = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]

for fp in font_paths:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass

# 设置中文字体优先级
plt.rcParams["font.sans-serif"] = [
    "Hiragino Sans GB",
    "STHeiti",
    "STHeiti Medium",
    "STHeiti Light",
    "PingFang SC",
    "Heiti SC",
    "SimHei",
    "Microsoft YaHei",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "sans-serif"

print("已注册中文字体:", plt.rcParams["font.sans-serif"][:3])