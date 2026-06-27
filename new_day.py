#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新增一天的论文。用法：
  1) 复制 data/days/_template.json 为 data/days/YYYY-MM-DD.json，填入当天的 digests 和 papers；
     （或者直接由 Claude 生成当天文件）
  2) 运行：python3 new_day.py            （会对最新一天做查重检查）
     或   python3 new_day.py 2026-06-29  （指定对哪天查重）
  脚本会：① 跨全库查重，发现重复会警告；② 重建 data/index.json；③ 重新 build 内嵌数据。
板块定义在 data/categories.json，所有日期共用；如需增删板块，改它即可。
"""
import json, pathlib, subprocess, sys
import maintain
root = pathlib.Path(__file__).parent
data_dir = root / "data"
days_dir = data_dir / "days"

def _is_valid_day(p):
    """跳过模板和被标记删除的文件。"""
    if p.stem.startswith("_"):
        return False
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return False
    return not obj.get("_deleted") and bool(obj.get("papers"))

dates = sorted([p.stem for p in days_dir.glob("*.json") if _is_valid_day(p)], reverse=True)
if not dates:
    print("data/days/ 下没有任何日期文件。请先放入 YYYY-MM-DD.json。")
    sys.exit(1)

latest = dates[0]
target = sys.argv[1] if len(sys.argv) > 1 else latest

# ① 跨全库查重（针对 target 这天）
dups = maintain.check_duplicates(target)
if dups:
    print(f"⚠ 警告：{target} 发现 {len(dups)} 篇可能重复，请核对后再决定是否保留：")
    for t, why in dups:
        print(f"   - 《{t}》 {why}")
    print("  （查重仅警告，不自动删除；如确为重复请手动从当天文件移除。）")
else:
    print(f"✓ 查重通过：{target} 与历史无重复")

idx0 = json.loads((data_dir / "index.json").read_text(encoding="utf-8")) if (data_dir/"index.json").exists() else {}
index = {
    "title": idx0.get("title", "Query-物料相关性论文库"),
    "subtitle": idx0.get("subtitle", "Query–Material Relevance Research"),
    "latest": dates[0],
    "days": [{"date": d, "count": len(json.loads((days_dir/f"{d}.json").read_text(encoding='utf-8'))["papers"])} for d in dates],
}
(data_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"index.json 已更新：共 {len(dates)} 天，最新 {dates[0]}")

# 重新 build 内嵌数据
subprocess.run([sys.executable, str(root / "build.py")], check=True)
