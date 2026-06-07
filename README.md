# 🎬 Media Scraper · 视频刮削整理

Organize messy video downloads into Infuse/VidHub/Plex-ready structure. Auto-detects 7 episode numbering formats, verifies show names against TMDB, renames and sorts into canonical directory layout.

扫描混乱的下载目录，对照 TMDB 确定正确命名，自动整理为 Infuse/VidHub/Plex 可识别的规范结构。

## 快速开始 / Quick Start

```bash
# Install
npx skills add <your-username>/media-organizer

# Usage (tell your AI agent)
整理视频
organize my downloads
media organizer
```

## 兼容性 / Compatibility

| Agent | Support |
|-------|---------|
| Claude Code | ✅ Native |
| Claude.ai | ✅ Native |
| Claude API | ✅ Native |
| Codex / OpenCode | ✅ Agent Skills standard ([agentskills.io](https://agentskills.io)) |
| Other agents | ✅ Any agent implementing the Agent Skills spec |

## 功能 / Features

- 🔍 **7 format detection**: S01E01, 1x01, S01EP1, 101, 第1季第3集, 剧名01.mp4, EP01
- 🌐 **TMDB verification**: Looks up correct show name and season number before renaming
- 📂 **Canonical structure**: `TV Shows/Show Name/Season 0X/Show Name S0XE0X.ext`
- 👁️ **Preview before execute**: `--dry-run` to review, `--execute` to apply
- 🏷️ **Name mapping**: `--names` for abbreviations, Chinese→English, etc.
- 🛡️ **Safe**: Only operates within the specified directory

## 工具 / Tools

| Script | Purpose |
|--------|---------|
| `scripts/scan.py <dir>` | Scan video files, output JSON |
| `scripts/organize.py` | Generate plan and execute |

## 验证 / Verified

Tested with 97 real media files across 3 seasons with 3 different naming formats — 0 errors.

## 许可 / License

MIT
