# 整理前后对照

## 电视剧场景 1：每个文件都在单独文件夹里

```
整理前：
  下载/
    【高清】Game.of.Thrones.S01E01/
      └── 【高清】Game.of.Thrones.S01E01.1080p.mkv
    冰与火之歌第一季第二集/
      └── got.s1e2.1080p.bluray.mkv
    Game of Thrones 1x03/
      └── game.of.thrones.103.hdtv.mkv

整理后：
  TV Shows/
    Game of Thrones/
      Season 01/
        ├── Game of Thrones S01E01.mkv
        ├── Game of Thrones S01E02.mkv
        └── Game of Thrones S01E03.mkv
```

要点：识别出同一个剧、同一季，从散落文件夹中提取出来，统一命名。

## 电视剧场景 2：文件名用数字代替 SxxExx

```
整理前：
  下载/
    Better.Call.Saul.101.mkv       ← 101 可能是 S01E01
    Better.Call.Saul.102.mkv
    Better.Call.Saul.201.mkv       ← 201 可能是 S02E01

整理后：
  TV Shows/
    Better Call Saul/
      Season 01/
        ├── Better Call Saul S01E01.mkv
        └── Better Call Saul S01E02.mkv
      Season 02/
        └── Better Call Saul S02E01.mkv
```

要点：`101` → 拆成 `S01E01`（第一季第一集）。但 `110` 就模糊了——是 S01E10 还是 S11E00？这种需要让用户确认。

## 电视剧场景 3：中文集数标记

```
整理前：
  下载/
    绝命毒师第1季第1集.mp4
    绝命毒师第1季第2集.mp4
    绝命毒师第2季第1集.mp4

整理后：
  TV Shows/
    Breaking Bad/
      Season 01/
        ├── Breaking Bad S01E01.mp4
        └── Breaking Bad S01E02.mp4
      Season 02/
        └── Breaking Bad S02E01.mp4
```

要点：从中文「第x季第x集」提取数字，剧名保持英文（查 TMDB 或让用户提供英文名）。

## 电影场景：混在电视剧堆里

```
整理前：
  下载/
    The.Matrix.1999.2160p.mkv
    Inception.2010.BluRay.mkv
    breaking.bad.s01e01.mkv
    breaking.bad.s01e02.mkv

整理后：
  Movies/
    The Matrix (1999)/
      └── The Matrix (1999).mkv
    Inception (2010)/
      └── Inception (2010).mkv
  TV Shows/
    Breaking Bad/
      Season 01/
        ├── Breaking Bad S01E01.mkv
        └── Breaking Bad S01E02.mkv
```

要点：根据文件名特征自动分类——有年份 → 电影，有 SxxExx → 电视剧。
