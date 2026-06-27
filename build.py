#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把按日归档的数据内嵌进 data/papers.inline.js，
使 index.html 双击打开时也能用（file:// 下 fetch 被浏览器拦截）。
每次新增/修改某天数据后运行： python3 build.py
"""
import json, pathlib, shutil

root = pathlib.Path(__file__).parent
data_dir = root / "data"
days_dir = data_dir / "days"

categories = json.loads((data_dir / "categories.json").read_text(encoding="utf-8"))["categories"]
index = json.loads((data_dir / "index.json").read_text(encoding="utf-8"))

# 读入每一天的完整数据（index.json 里已是有效日期）
days = {}
for d in index["days"]:
    date = d["date"]
    days[date] = json.loads((days_dir / f"{date}.json").read_text(encoding="utf-8"))

payload = {
    "title": index["title"],
    "subtitle": index["subtitle"],
    "latest": index["latest"],
    "categories": categories,
    "index": index["days"],   # [{date, count}]
    "days": days,             # {date: {date,title,subtitle,digests,papers}}
}

inline_js = "window.PAPERS_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"
out = data_dir / "papers.inline.js"
out.write_text(inline_js, encoding="utf-8")

dist = root / "dist"
if dist.exists():
    shutil.rmtree(dist)
(dist / "data" / "days").mkdir(parents=True)

shutil.copy2(root / "index.html", dist / "index.html")
(dist / "data" / "papers.inline.js").write_text(inline_js, encoding="utf-8")
shutil.copy2(data_dir / "categories.json", dist / "data" / "categories.json")
shutil.copy2(data_dir / "index.json", dist / "data" / "index.json")
for d in index["days"]:
    date = d["date"]
    shutil.copy2(days_dir / f"{date}.json", dist / "data" / "days" / f"{date}.json")

print(f"已生成 {out.name} 和 dist/：{len(days)} 天，最新 {index['latest']}")
