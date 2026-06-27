#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""维护工具集：跨全库查重。被 new_day.py 调用，也可单独运行检查。

查重（dedup）：跨所有日期，检测同一篇论文被重复收录。判定依据：
  ① 归一化标题相同/高度相似（去空格、标点、大小写，及去掉 arXiv/会议等版本噪声词）；
  ② 提取到的 arXiv 编号相同；
  ③ url 指向同一 arXiv 论文（不同版本视为同一篇）。

注：历史数据「满一年清理详解」功能已按需求取消，数据永久保留。
  下方 purge_old_explains 函数保留备用，但默认不再被调用。
"""
import json, pathlib, re, datetime

root = pathlib.Path(__file__).parent
days_dir = root / "data" / "days"

def norm_title(t):
    """标题归一化：转小写、去除空白与标点、去掉常见版本/来源噪声。"""
    t = t.lower()
    # 去掉 arXiv 版本号、年份、会议名等噪声
    t = re.sub(r"arxiv|预印本|preprint|v\d+|\(.*?\)|（.*?）", " ", t)
    t = re.sub(r"[\s\-_/:：·,，。.、《》\"'\[\]()]+", "", t)
    return t

def arxiv_id(s):
    """从 url 或标题里提取 arXiv 编号（如 1711.08611），提不到返回 None。"""
    if not s:
        return None
    m = re.search(r"(\d{4}\.\d{4,5})", s)
    return m.group(1) if m else None

def _similar(a, b):
    """两个归一化标题是否高度相似（一个包含另一个，且较短的占比够高）。"""
    if not a or not b:
        return False
    if a == b:
        return True
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    return short in long and len(short) / len(long) >= 0.8

def load_all_days(exclude_date=None):
    """返回 {date: dayobj}，跳过模板/作废文件。"""
    out = {}
    for p in days_dir.glob("*.json"):
        if p.stem.startswith("_") or p.stem == exclude_date:
            continue
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if obj.get("_deleted") or not obj.get("papers"):
            continue
        out[p.stem] = obj
    return out

def build_seen_index(days):
    """汇总历史所有论文的 (归一化标题, arXiv号) 指纹。"""
    seen = []  # [(date, title, norm, axid)]
    for date, obj in days.items():
        for p in obj["papers"]:
            seen.append((date, p["title"], norm_title(p["title"]),
                         arxiv_id(p.get("url")) or arxiv_id(p["title"])))
    return seen

def check_duplicates(target_date):
    """检查 target_date 这天的论文是否与历史（含当天内部）重复。返回重复列表。"""
    days = load_all_days()
    if target_date not in days:
        return []
    target = days[target_date]
    history = build_seen_index({d: o for d, o in days.items() if d != target_date})

    dups = []
    intra_norms = {}  # 当天内部查重
    for p in target["papers"]:
        n = norm_title(p["title"])
        ax = arxiv_id(p.get("url")) or arxiv_id(p["title"])
        # 与历史比
        for (hdate, htitle, hn, hax) in history:
            if (ax and hax and ax == hax) or _similar(n, hn):
                dups.append((p["title"], f"与 {hdate} 的《{htitle}》重复"))
                break
        else:
            # 与当天内部已出现的比
            for (pt, pn, pax) in [(v[0], v[1], v[2]) for v in intra_norms.values()]:
                if (ax and pax and ax == pax) or _similar(n, pn):
                    dups.append((p["title"], f"与当天的《{pt}》重复"))
                    break
            else:
                intra_norms[p["title"]] = (p["title"], n, ax)
    return dups

def purge_old_explains(today=None, max_age_days=365):
    """删除满 max_age_days 天（含）的日期文件里每篇的 explain，打标 explainPurged。
    即「只保留一年」：距今 >= 365 天的当天详解被清理，综述与卡片保留。"""
    if today is None:
        today = datetime.date.today()
    elif isinstance(today, str):
        today = datetime.date.fromisoformat(today)
    purged = []
    for p in days_dir.glob("*.json"):
        if p.stem.startswith("_"):
            continue
        try:
            d = datetime.date.fromisoformat(p.stem)
        except ValueError:
            continue
        if (today - d).days >= max_age_days:
            obj = json.loads(p.read_text(encoding="utf-8"))
            if obj.get("explainPurged"):
                continue
            removed = 0
            for paper in obj.get("papers", []):
                if "explain" in paper:
                    del paper["explain"]
                    removed += 1
            obj["explainPurged"] = True
            p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
            purged.append((p.stem, removed))
    return purged

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        dups = check_duplicates(date)
        if dups:
            print(f"⚠ 发现 {len(dups)} 篇重复：")
            for t, why in dups:
                print(f"  - 《{t}》 {why}")
        else:
            print("✓ 无重复")
    elif len(sys.argv) > 1 and sys.argv[1] == "purge":
        today = sys.argv[2] if len(sys.argv) > 2 else None
        res = purge_old_explains(today)
        print("清理结果：", res if res else "无超期文件")
