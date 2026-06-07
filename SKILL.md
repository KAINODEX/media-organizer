---
name: media-organizer
description: |
  Media scraper & organizer — rename and sort messy video downloads into Infuse/Plex/VidHub/Jellyfin/Emby-ready structure. Auto-detects 7 episode numbering formats, verifies show names against TMDB.
  Natural-language discovery: "organize my downloaded videos for Infuse", "rename my messy TV show files", "my NAS downloads are a mess make them Plex-ready", "I need a media scraper for my videos", "整理下载的视频给Infuse", "帮我把视频刮削了", "NAS上的电视剧文件名乱七八糟帮我整理", "下载的视频怎么重命名才能被Infuse识别"
  Triggers: 刮削, 视频刮削, 整理视频, 整理剧集, 批量重命名, media scraper, organize media, rename videos, infuse naming, video organizer, tv show sorter, Plex rename, Jellyfin organizer, Emby scraper
---

# 📺 媒体文件整理助手

你的任务是把用户下载目录里混乱的视频文件整理成 Infuse 能完美识别的结构。

## 核心原则

- **查 TMDB 再改名**：不要凭文件名猜测。必须先查 TMDB 确定正确剧名、季号，再动手
- **尊重原始语言**：中文剧就用中文名，英文剧就用英文名，不翻译
- **标准格式**：电视剧用 `SxxExx` 格式，电影用 `(年份)` 格式
- **只动指定目录**：只在用户指定的目录内操作，不动其他目录
- **先预览后执行**：所有操作先 dry-run 展示计划，用户确认后再执行

## 目标结构

```
媒体库/
├── Movies/
│   ├── Inception (2010)/
│   │   └── Inception (2010).mkv
│   └── The Matrix (1999)/
│       └── The Matrix (1999).mkv
└── TV Shows/
    ├── Breaking Bad/
    │   ├── Season 01/
    │   │   ├── Breaking Bad S01E01.mkv
    │   │   └── Breaking Bad S01E02.mkv
    │   └── Season 02/
    │       └── Breaking Bad S02E01.mkv
    └── Game of Thrones/
        └── Season 01/
            └── Game of Thrones S01E01.mkv
```

## 工作流程

1. **扫描** — `python3 scripts/scan.py <目录>` 输出 JSON
2. **TMDB 查证** ⭐ — **这是最关键的一步，不可跳过**
   - 用剧名在 `themoviedb.org` 搜索，找到正确的 TMDB 条目
   - 确认：这部剧在 TMDB 上是独立条目，还是某部剧的某一季？
   - 确认：这是第几季？（不能猜，必须以 TMDB 为准）
   - 确认：TMDB 上的正确剧名是什么？（以此为准，不用文件名里的名字）
   - 查法：`curl -s "https://www.themoviedb.org/search?query=剧名"` 找到 TV ID → 查各季标题
3. **命名** — 以 TMDB 剧名为准，调用 `clean_show_name()`；必要时用 `--names` 映射修正
4. **预览** — `python3 scripts/organize.py --dry-run --base <目录> --names '<映射JSON>'`
5. **用户确认** — 展示计划，让用户审核
6. **执行** — 用户确认后，加 `--execute` 执行

## 电视剧命名规则

标准：`{Show Name} S{季号:02d}E{集号:02d}.{ext}`

能识别的变体 → 统一转为 S01E01：
- `Breaking.Bad.S01E01.mkv` → 已是标准格式，不动
- `Breaking Bad 1x01.mkv` → `Breaking Bad S01E01.mkv`
- `Breaking.Bad.101.mkv` → 需人工确认是 S01E01 还是 S10E01
- `breaking bad 第1季第3集.mp4` → `Breaking Bad S01E03.mp4`
- `Game.of.Thrones.S01.E01.mkv` → `Game of Thrones S01E01.mkv`

## 电影命名规则

标准：`{Movie Name} ({Year}).{ext}`

```
The.Matrix.1999.2160p.BluRay.x265.mkv → The Matrix (1999).mkv
```

## 工具

- `scripts/scan.py <目录>` — 扫描视频文件，输出 JSON 列表（自动识别 SxxExx、1x01、101、第1季等格式）
- `scripts/organize.py` — 读取 scan JSON，生成整理计划并执行
  - `--dry-run`（默认）：仅预览，不执行
  - `--execute`：执行实际改名和移动
  - `--base <目录>`：指定目标根目录
  - `--names '{"原文件名":"正确剧名",...}'`：手动指定剧名映射
- `references/naming-guide.md` — Infuse 完整命名规范
