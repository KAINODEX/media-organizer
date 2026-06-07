#!/usr/bin/env python3
"""
根据 scan.py 的 JSON 输出，生成整理计划并执行。

用法：
  python3 scan.py /下载目录 | python3 organize.py --dry-run    # 预览计划
  python3 scan.py /下载目录 | python3 organize.py --execute     # 执行整理
  python3 organize.py --execute --base /媒体库 < scan.json     # 指定目标根目录

工作流程：
  1. 读取 scan JSON → 自动分组（电视剧按剧名+季，电影单独）
  2. 智能提取剧名（去掉 SxxExx、分辨率标签、点号转空格）
  3. 输出操作计划（mkdir + mv）
  4. --execute 模式执行实际操作
"""

import json, sys, os, re, argparse
from collections import defaultdict
from pathlib import Path

# ── 质量/编码标签（需要从剧名中剥离） ──
NOISE_TAGS = [
    'HD1080p', 'HD720p', 'HD2160p',  # 常见拼接格式
    '1080p', '2160p', '4K', '720p', '480p',
    'BluRay', 'Blu-ray', 'WEB-DL', 'WEBRip', 'HDTV', 'WEB',
    'HDR', 'HDR10', 'HDR10+', 'DV', 'Dolby Vision',
    'x264', 'x265', 'HEVC', 'AVC', 'H264', 'H265',
    'AAC', 'AC3', 'DTS', 'TrueHD', 'Atmos', 'DDP', 'DDP5', 'DDP7',
    'AMZN', 'NF', 'DSNP', 'HBO', 'Hulu', 'AppleTV',
    'REMUX', 'PROPER', 'REPACK', 'EXTENDED', 'UNCUT', 'DC',
    '10bit', '8bit', 'SDR',
    '内封', '内嵌', '官中', '中字', '双语',
    'CHD', 'WiKi', 'FRDS', 'CMCT', 'HQC', 'MTeam',
]

# ── 中文前缀清理 ──
CHINESE_PREFIX = re.compile(r'^【[^】]*】|^\［[^］]*］')

# 季/集标记（从文件名中移除）
SE_MARKERS = re.compile(
    r'[Ss]\d{1,2}\s*[Ee][Pp]\s*\d{1,3}' # S01EP01 / S01EP1
    r'|[Ss]\d{1,2}\s*[Ee]\d{1,2}'       # S01E01
    r'|\d{1,2}\s*[xX]\s*\d{1,2}'       # 1x01
    r'|[Ss]\d{1,2}\s*\.\s*[Ee]\d{1,2}' # S01.E01
    r'|[Ss]eason\s*\d{1,2}\s*[Ee]p?\s*\d{1,2}'  # Season 1 Episode 1
    r'|第\s*\d{1,2}\s*季.*?第\s*\d{1,2}\s*集'   # 第1季第3集
    r'|[Ee][Pp]?\s*\d{1,2}'             # EP01
    r'|(?<!\d)\d{3,4}(?!\d|[pPiI])'    # 101 格式
    r'|\d{2,3}$'                        # 末尾裸数字 01-999（剧名01.mp4 格式）
)

YEAR_PATTERN = re.compile(r'(?:19|20)\d{2}')  # 年份

# Title case: 这些小词在标题中保持小写（除非是首词或尾词）
SMALL_WORDS = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor',
               'on', 'at', 'to', 'by', 'in', 'of', 'with', 'from',
               'is', 'vs', 'de', 'la', 'le', 'von', 'van'}


def title_case(text):
    """智能 Title Case：小词保持小写，其余首字母大写"""
    words = text.split()
    if not words:
        return text
    result = []
    for i, w in enumerate(words):
        low = w.lower()
        if i == 0 or i == len(words) - 1 or low not in SMALL_WORDS:
            result.append(w[0].upper() + w[1:].lower() if len(w) > 1 else w.upper())
        else:
            result.append(low)
    return ' '.join(result)


def clean_show_name(filename, name_map=None):
    """从文件名中提取干净的剧名/片名"""
    # 先检查是否有手动映射
    if name_map and filename in name_map:
        return name_map[filename]

    name = os.path.splitext(filename)[0]
    name = CHINESE_PREFIX.sub('', name)

    # 移除季/集标记
    name = SE_MARKERS.sub(' ', name)

    # 移除年份标记
    name = YEAR_PATTERN.sub(' ', name)

    # 移除已知噪音标签
    for tag in NOISE_TAGS:
        name = re.sub(rf'\b{re.escape(tag)}\b', ' ', name, flags=re.I)

    # 点号、下划线 → 空格
    name = name.replace('.', ' ').replace('_', ' ')

    # 压缩空格，trim
    name = re.sub(r'\s+', ' ', name).strip()

    # 智能 Title Case
    name = title_case(name)

    return name if name else None


def group_and_plan(files, base_dir, name_map=None):
    """将扫描结果分组，生成操作计划"""
    plans = []
    warnings = []

    # ── 分组电影 ──
    movies = [f for f in files if f['is_movie'] and not f['is_tv']]
    for m in movies:
        name = clean_show_name(m['filename'], name_map)
        year = m['year']
        if not name:
            warnings.append(f"⚠️  无法提取片名: {m['filename']}")
            continue
        movie_dir = f"{name} ({year})" if year else name
        target_path = os.path.join(base_dir, 'Movies', movie_dir,
                                   f"{name} ({year}){m['ext']}" if year else f"{name}{m['ext']}")
        plans.append({
            'type': 'movie',
            'source': m['path'],
            'target': target_path,
            'mkdir': os.path.dirname(target_path),
        })

    # ── 分组电视剧 ──
    tv_shows = [f for f in files if f['is_tv']]
    # 按剧名分组
    by_show = defaultdict(list)
    unnamed = []
    for ep in tv_shows:
        name = clean_show_name(ep['filename'], name_map)
        if name and len(name) > 1:
            by_show[name].append(ep)
        else:
            unnamed.append(ep)

    for show_name, episodes in by_show.items():
        # 按季分组
        by_season = defaultdict(list)
        for ep in episodes:
            s = ep['season'] or 1  # 缺省当第1季
            by_season[s].append(ep)

        for season_num, eps in by_season.items():
            eps.sort(key=lambda e: e['episode'] or 0)
            for ep in eps:
                ep_num = ep['episode'] or 0
                target_path = os.path.join(
                    base_dir, 'TV Shows', show_name,
                    f'Season {season_num:02d}',
                    f'{show_name} S{season_num:02d}E{ep_num:02d}{ep["ext"]}'
                )
                plans.append({
                    'type': 'tv',
                    'source': ep['path'],
                    'target': target_path,
                    'mkdir': os.path.dirname(target_path),
                    'show': show_name,
                    'season': season_num,
                    'episode': ep_num,
                })

    # 未识别剧名的单独报告
    if unnamed:
        warnings.append(f"⚠️  {len(unnamed)} 个文件无法自动提取剧名，已跳过：")
        for u in unnamed:
            warnings.append(f"    - {u['filename']}")

    return plans, warnings


def print_plan(plans, warnings, base_dir):
    """用可读格式输出整理计划"""
    print(f"📂 目标目录: {base_dir}\n")

    if not plans:
        print("✅ 没有需要整理的文件")
        return

    # 按类型统计
    movies = [p for p in plans if p['type'] == 'movie']
    tv = [p for p in plans if p['type'] == 'tv']
    shows = defaultdict(list)
    for p in tv:
        shows[p['show']].append(p)

    print(f"🎬 电影: {len(movies)} 部")
    for p in movies:
        print(f"   {os.path.basename(p['source'])}")
        print(f"   → {os.path.relpath(p['target'], base_dir)}")
        print()

    print(f"📺 电视剧: {len(tv)} 集 ({len(shows)} 部)")
    for show, eps in shows.items():
        seasons = sorted(set(e['season'] for e in eps))
        s_range = f"S{seasons[0]}" if len(seasons) == 1 else f"S{seasons[0]}-S{seasons[-1]}"
        print(f"   {show}  {s_range}  ({len(eps)} 集)")
        for e in eps:
            print(f"     S{e['season']:02d}E{e['episode']:02d} ← {os.path.basename(e['source'])}")

    print(f"\n📁 将创建 {len(set(p['mkdir'] for p in plans))} 个目录")
    print(f"📦 将移动 {len(plans)} 个文件")

    for w in warnings:
        print(f"\n{w}")


def execute_plan(plans, dry_run=True):
    """执行整理计划"""
    created_dirs = set()
    moved = 0
    errors = 0

    for i, p in enumerate(plans):
        if dry_run:
            continue

        try:
            if p['mkdir'] not in created_dirs:
                os.makedirs(p['mkdir'], exist_ok=True)
                created_dirs.add(p['mkdir'])

            if os.path.exists(p['target']):
                print(f"⚠️  目标已存在，跳过: {os.path.basename(p['target'])}")
                continue

            os.rename(p['source'], p['target'])
            moved += 1

            if (i + 1) % 10 == 0:
                print(f"   ... {i + 1}/{len(plans)}")

        except OSError as e:
            print(f"❌ 移动失败: {os.path.basename(p['source'])} → {e}")
            errors += 1

    if not dry_run:
        print(f"\n✅ 移动完成: {moved} 个文件, {errors} 个错误")


def main():
    parser = argparse.ArgumentParser(description='媒体文件整理工具')
    parser.add_argument('--base', default=os.getcwd(),
                        help='目标根目录 (默认: 当前目录)')
    parser.add_argument('--execute', action='store_true',
                        help='执行实际操作 (默认仅预览)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='仅预览计划，不执行 (默认)')
    parser.add_argument('--json', type=str,
                        help='从 JSON 文件读取 scan 结果 (默认从 stdin)')
    parser.add_argument('--names', type=str,
                        help='名称映射 JSON: {"原文件名": "正确剧名", ...}')
    args = parser.parse_args()

    # 读取 scan 数据
    if args.json:
        with open(args.json) as f:
            files = json.load(f)
    else:
        files = json.load(sys.stdin)

    # 读取名称映射
    name_map = None
    if args.names:
        try:
            name_map = json.loads(args.names)
        except json.JSONDecodeError:
            # 可能是文件路径
            if os.path.exists(args.names):
                with open(args.names) as f:
                    name_map = json.load(f)

    base_dir = os.path.abspath(args.base)

    # 生成计划
    plans, warnings = group_and_plan(files, base_dir, name_map)

    # 输出
    print_plan(plans, warnings, base_dir)

    if args.execute:
        print("\n" + "=" * 50)
        print("🚀 开始执行...\n")
        execute_plan(plans, dry_run=False)
    else:
        print("\n💡 以上为预览。确认无误后加 --execute 执行。")


if __name__ == '__main__':
    main()
