#!/usr/bin/env python3
"""
扫描指定目录下的视频文件，输出 JSON。

增强版：尝试从文件名中提取季号、集号、年份。
"""
import os, json, sys, re

VIDEO_EXT = {'.mkv', '.mp4', '.m4v', '.avi', '.mov', '.wmv', '.flv', '.webm'}

# 常见的 S01E01 / 1x01 / S1.E1 / 第1季第3集 等等模式
SE_PATTERNS = [
    re.compile(r'[Ss](\d{1,2})\s*[Ee](\d{1,2})'),        # S01E01
    re.compile(r'(\d{1,2})\s*[xX]\s*(\d{1,2})'),          # 1x01
    re.compile(r'[Ss](\d{1,2})\s*\.\s*[Ee](\d{1,2})'),    # S01.E01
    re.compile(r'[Ss]eason\s*(\d{1,2}).*?[Ee]p?\s*(\d{1,2})', re.I),  # Season 1 Episode 1
    re.compile(r'第\s*(\d{1,2})\s*季.*?第\s*(\d{1,2})\s*集'),  # 第1季第3集
    re.compile(r'[Ss](\d{1,2})\s*[Ee][Pp]\s*(\d{1,3})'),    # S01EP01 / S01EP1
    re.compile(r'[Ee][Pp]?\s*(\d{1,2})'),                  # EP01 / E01 (只有集号，没有季号)
    # 纯数字集号: 101→S01E01, 110→S01E10, 201→S02E01, 1001→S10E01
    # 3位(sXEE)或4位(sXXEE)，排除年份(19xx/20xx)和常见分辨率(720/1080/2160/4320)
    re.compile(r'(?<=[^A-Za-z0-9])([1-9]\d?)(\d{2})(?!\d|[pPiI])'),
    # 裸数字编号: 剧名01.mp4 → 纯集号（前有非字母数字，排除开头纯数字剧名和codec号）
    re.compile(r'(?<=[^A-Za-z0-9])(\d{2,3})\.(?:mp4|mkv|m4v|avi|mov|wmv|flv|webm)$', re.I),
]

# 年份模式
YEAR_PATTERN = re.compile(r'[\[\(\.\s]((?:19|20)\d{2})[\]\)\.\s]')

def detect_season_episode(filename):
    """尝试从文件名提取季号和集号。返回 (season, episode) 或 (None, None)"""
    for pat in SE_PATTERNS:
        m = pat.search(filename)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                s, e = int(groups[0]), int(groups[1])
                # 过滤：排除年份误匹配 (如 1999→s=19,e=99 或 2010→s=20,e=10)
                full = int(str(s) + f"{e:02d}")
                if 1900 <= full <= 2099:
                    continue
                return s, e
            elif len(groups) == 1:
                return None, int(groups[0])  # 只有集号
    return None, None

def detect_year(filename):
    """从文件名提取四位年份。返回 year 或 None"""
    m = YEAR_PATTERN.search(filename)
    return int(m.group(1)) if m else None

def scan(directory):
    files = []
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in VIDEO_EXT:
                fullpath = os.path.join(root, f)
                size_mb = os.path.getsize(fullpath) / (1024 * 1024)
                season, episode = detect_season_episode(f)
                year = detect_year(f)
                files.append({
                    "path": fullpath,
                    "filename": f,
                    "ext": ext,
                    "size_mb": round(size_mb, 1),
                    "season": season,
                    "episode": episode,
                    "year": year,
                    "is_tv": season is not None or episode is not None,
                    "is_movie": year is not None and season is None
                })
    return files

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    if not os.path.isdir(target):
        print(f"❌ 不是有效目录: {target}", file=sys.stderr)
        sys.exit(1)
    results = scan(target)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    tv = sum(1 for r in results if r['is_tv'])
    mv = sum(1 for r in results if r['is_movie'])
    print(f"\n共 {len(results)} 个视频文件（电视剧 {tv}，电影 {mv}）", file=sys.stderr)
