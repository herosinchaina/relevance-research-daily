# 相关性论文日报 · Relevance Research Daily

一个每日整理「相关性判别」及相关方向最新学术/业界论文的网页。论文以**综述/总结**形式呈现，按类别分页浏览——点哪个类别，页面就只显示该类别的论文。

## 目录结构

```
relevance-research-daily/
├─ index.html              # 网页主文件
├─ build.py                # 把 papers.json 内嵌进 inline.js（双击打开用）
├─ data/
│  ├─ papers.json          # ★ 论文数据，每天更新这个文件
│  └─ papers.inline.js     # 自动生成，请勿手改
└─ README.md
```

## 当前板块

- **相关性判别 Relevance** — 相关性建模、标注、评估与排序
- **强化学习 RL** — 策略优化、奖励建模、RLHF/RLAIF 及与排序检索的交叉
- **大语言模型 LLM** — 检索增强、相关性幻觉、长上下文与对齐
- **信息检索 IR** — 稠密/稀疏检索、重排序、端到端搜索

想增删板块，编辑 `data/papers.json` 里的 `categories` 即可。

## 怎么打开

两种方式都行：

1. **直接双击 `index.html`** — 会读取 `data/papers.inline.js` 里的内嵌数据。
2. **本地服务器**（推荐，改完 json 立即生效）：
   ```bash
   cd relevance-research-daily
   python3 -m http.server 8000
   # 浏览器打开 http://localhost:8000
   ```

## 每天怎么更新论文

1. 编辑 `data/papers.json`，在 `papers` 数组里增/改论文。每篇格式：
   ```json
   {
     "category": "relevance",            // 必须是 categories 里的某个 id
     "title": "论文中文标题",
     "source": "机构 / 作者",
     "venue": "发表/预印 出处",
     "tag": "细分标签",
     "summary": "2~4 句的综述总结，讲清动机与做法",
     "contrib": "① …；② …；③ …  核心贡献要点"
   }
   ```
   把 `meta.lastUpdated` 改成当天日期。
2. 运行一次 `python3 build.py` 重新生成内嵌数据（只在你用双击方式打开时需要）。

> 也可以直接让我（Claude）来做：每天说一句「整理今天的相关性论文」，我会把当天 10 篇以上写成综述、归好类、更新进 `papers.json` 并重新 build。

## 设计

杂志卡片风格：每篇一张卡片，板块用颜色区分（相关性=蓝、RL=橙、LLM=紫、IR=绿）。顶部分类切换为**单类别视图**，一次只看一个方向，避免信息过载。
