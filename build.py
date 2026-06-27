#!/usr/bin/env python3
"""把 data/papers.json 内嵌进 data/papers.inline.js，
使 index.html 既能用本地服务器打开，也能直接双击打开。
每次更新完 papers.json 后运行： python3 build.py
"""
import json, pathlib

root = pathlib.Path(__file__).parent
src = root / "data" / "papers.json"
out = root / "data" / "papers.inline.js"

data = json.loads(src.read_text(encoding="utf-8"))
js = "window.PAPERS_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n"
out.write_text(js, encoding="utf-8")
print(f"已生成 {out.name}（{len(data['papers'])} 篇论文，更新日期 {data['meta']['lastUpdated']}）")
