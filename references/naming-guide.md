# Infuse 命名规范参考

## 电视剧（TV Shows）

### 标准格式

Infuse 通过文件名中的 **SxxExx** 来识别季和集。

```
{剧名} S{季号:2位}E{集号:2位}.{扩展名}
```

### ✅ Infuse 能正确识别的格式

```
Breaking Bad S01E01.mkv
Game of Thrones S05E09.mkv
Better Call Saul S03E02.mp4
```

### ✅ 也支持的变形（但建议统一为标准格式）

```
Breaking Bad S01E01-E02.mkv     ← 多集合一文件
Breaking Bad S01E01 Pilot.mkv   ← 标题后有额外文字（会被忽略）
```

### ❌ Infuse 无法识别的格式

| 问题格式 | 为什么不行 |
|---------|-----------|
| `Breaking Bad 1x01.mkv` | 没有 SxxExx |
| `Breaking Bad 101.mkv` | 模糊，101 可以是 S01E01 或 S10E01 |
| `breaking.bad.episode.1.mkv` | 没有季号 |
| `第1季第3集.mp4` | 英文 Infuse 不认识中文集数标记 |
| `BB_S1_E1.mkv` | 格式不对，需要 S01E01 |

### 多季文件夹结构

```
TV Shows/
├── Show Name/
│   ├── Season 01/
│   │   └── Show Name S01E01.mkv
│   ├── Season 02/
│   │   └── Show Name S02E01.mkv
│   └── Specials/
│       └── Show Name S00E01.mkv    ← 特别篇/花絮用 S00
```

## 电影（Movies）

### 标准格式

```
{片名} ({年份}).{扩展名}
```

年份必须是四位数字，圆括号包裹。

### ✅ 正确

```
Inception (2010).mkv
The Matrix (1999).mkv
Everything Everywhere All at Once (2022).mp4
```

### ❌ 无法识别

| 问题格式 | 为什么不行 |
|---------|-----------|
| `Inception.2010.mkv` | 年份没用圆括号 |
| `Inception.mkv` | 缺少年份 |
| `Inception (10).mkv` | 年份不是四位 |

### 文件夹结构

```
Movies/
├── Inception (2010)/
│   └── Inception (2010).mkv
└── The Matrix (1999)/
    └── The Matrix (1999).mkv
```
