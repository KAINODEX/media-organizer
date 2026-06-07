# 从零发布一个 Agent Skill：以视频刮削为例

> 一个 688 行的开源项目，零竞品品类，推上 GitHub 就能被全球用户搜索安装。本文以「视频刮削整理」为真实案例，讲清楚 Agent Skill 到底是什么、和 Prompt 有什么本质区别、怎么开发测试发布。

## 一、先讲清楚这个场景：刮削到底是什么

很多人下载了一堆视频，扔在 NAS 里，文件夹长这样：

```
Downloads/
├── 【高清】Game.of.Thrones.S01E01/【高清】Game.of.Thrones.S01E01.1080p.mkv
├── 冰与火之歌第一季第二集/got.s1e2.1080p.bluray.mkv
├── Better.Call.Saul.101.mkv          ← 101 是第几季第几集？
├── 绝命毒师第1季第1集.mp4            ← 中文编号
├── 唐朝诡事录之长安01.mp4            ← 这是第几季？查了 TMDB 才知道是 S3
└── 1883.S01E01.1080p.WEB.H264-CAKES.chs.eng.mp4  ← 1883 是剧名还是年份？
```

**刮削**（scraping）这个词，在中文 Plex/Infuse 圈子里指的是：把混乱的文件名整理成媒体服务器能识别的规范格式，然后播放器自动从 TMDB 拉取海报、演员、集名等元数据。

但很多人误解了这个流程。实际上分两步：

```
实际流程：
  ① 重命名 + 整理目录结构（我的 skill 干的）
  ② 播放器从 TMDB 拉元数据（Infuse/VidHub/Plex 干的）
                      
技能只负责①。文件名里不需要写集名——S01E01 这把钥匙就够了。
```

**我的 skill 真正做的事情：**

1. 扫描目录，识别 7 种电视剧编号格式（S01E01、1x01、S01EP1、101、第1季第3集、剧名01.mp4、EP01）
2. 去 TMDB 查证：这到底是哪部剧？第几季？（不凭文件名瞎猜）
3. 生成整理计划，预览给用户确认
4. 执行改名和目录重组，输出规范结构：

```
TV Shows/剧名/Season 0X/剧名 S0XE0X.ext
```

**实测数据：** 97 集、3 个不同季节、3 种命名格式混在一起 → 0 错误，VidHub 完美识别。



## 二、Skill 到底是什么：用这个案例讲透

### 2.1 先看一段 Prompt 能不能干这个事

如果只写一段 Prompt 给 AI：

> "帮我把下载目录里的视频整理成 Infuse 格式"

AI 会怎么做？它会猜。猜剧名、猜季号、猜格式。遇到 `唐朝诡事录之长安01.mp4`，它可能猜这是第一季——因为文件名里有「01」。但实际上这是第三季（查 TMDB 才知道）。

**Prompt 的问题：**

- 没有工具：不能扫描文件系统、不能查 TMDB
- 没有流程约束：每次执行可能跳步或走样
- 没有标准输出：每次结果格式不同，无法复用
- 不能共享：别人没法「安装」一段 Prompt

### 2.2 Skill 多出了什么

Skill = Prompt + **工具** + **工作流** + **可分发**。看对比：

| | Prompt | Skill |
|---|--------|-------|
| 指令 | ✅ 一段文字 | ✅ SKILL.md 结构化指令 |
| 工具 | ❌ 无 | ✅ Python 脚本（scan.py, organize.py） |
| 工作流 | ❌ 靠 AI 自己发挥 | ✅ 强制 6 步：扫描→TMDB查证→命名→预览→确认→执行 |
| 可测试 | ❌ | ✅ dry-run 模式，反复验证 |
| 可分发 | ❌ | ✅ `npx skills add` 一键安装 |
| 跨 Agent | ❌ | ✅ Claude Code / Codex / Cline 等 16+ 平台 |

**Skill 的核心要素，用我们这个项目的实际结构来看：**

```
media-organizer/
├── SKILL.md              ← ① 入口：告诉 AI 什么时候激活、怎么干活
├── metadata.json         ← ② 元信息：版本、作者、关键词（中英双语搜索）
├── README.md             ← ③ 展示页：GitHub 上的门面
├── scripts/              ← ④ 工具：真正干活的代码
│   ├── scan.py           ←     扫描视频，输出 JSON
│   └── organize.py       ←     生成计划 + 执行改名
├── references/           ← ⑤ 参考：Infuse 命名规范
└── examples/             ← ⑥ 示例：整理前后对照
```

SKILL.md 里最关键的是**工作流**——不是模糊的「帮我整理」，而是硬编码的 6 个步骤，其中 TMDB 查证标记为 ⭐ 不可跳过。



## 三、开发过程：怎么从一个想法到能用的 Skill

### 3.1 从真实场景开始，不是从代码开始

不要先写 SKILL.md。先拿真实数据跑一遍：

1. 扫描 NAS 上混乱的下载目录
2. 发现 scan.py 只能识别 4 种格式，漏了 3 种 → 补齐
3. 跑 organize.py 预览 → 21 集被拆成 21 部不同的剧 → 修剧名提取逻辑
4. 文件夹名和 TMDB 对不上 → 加入 TMDB 查证步骤
5. 1883（Yellowstone 前传）被当成年份删掉了 → 修正则
6. H264 里的 264 被当集号 → 修正则

**核心经验：不要闭门造车。拿真实数据跑，哪里坏了修哪里。**

整个开发过程，每次改动都在真实 NAS 上跑 dry-run，确认计划正确才 execute。97 个文件、0 错误后才算完成。

### 3.2 命名和搜索：让零竞品优势最大化

推上 GitHub 之前，先查 skills.sh（Agent Skill 的官方市场）上有没有竞品。

我用 20 个关键词搜了一遍：`infuse`、`media organizer`、`plex rename`、`刮削`、`视频整理`……**全部 0 结果。**

这是这个品类在 skills.sh 上的第一个 Skill。所以命名策略很关键：

- **包名叫 `media-organizer`**（技术准确，不误导）
- **描述里「刮削」排第一**（中文用户最高频搜索词）
- **关键词中英双语**（`media scraper`、`video organizer`、`刮削`、`批量重命名`……共 19 个）
- **兼容性标记**：Agent Skills 开放标准，支持 Claude Code、Codex、Cline 等 16+ agent

不要用文艺名字（虽然想过「司书」这样的典故名），就用品类名本身。零竞品时，搜索词就是你最好的品牌。

### 3.3 发布流程：三步上线

```bash
# 1. 初始化标准包结构
npx skills init media-organizer

# 2. 推 GitHub
gh repo create media-organizer --public --push

# 3. 安装到自己机器上（顺便触发 skills.sh 收录）
npx skills add KAINODEX/media-organizer -g -y
```

推上去那一刻，skills.sh 就开始收录。用户搜「刮削」就能找到。



## 四、别人怎么用

Skill 的发现和安装有两种路径。这一点和传统软件很不同——用户不需要记住 skill 叫什么名字。

### 路径一：知道名字，直接装

如果从文章、社交媒体、朋友推荐知道了 `media-organizer`，直接一行命令：

```bash
npx skills add KAINODEX/media-organizer
```

### 路径二：只知道场景，让 AI 自己找

大多数用户并不知道有没有这个 skill、叫什么名字。他们只是有一个需求。这时直接告诉 Claude Code 就行了：

> 「我 NAS 上下载了好多视频，文件名乱七八糟的，帮我整理成 Infuse 能识别的格式」

Claude Code 内置了一个叫 `find-skills` 的 skill，它会拿你的需求去 skills.sh 上搜索，找到匹配的 skill，然后问你要不要安装。整个过程不需要你知道 skill 名字。

```
你的需求 → Claude Code → find-skills → skills.sh 搜索 → 找到 media-organizer → 一键安装
```

这背后是 Agent Skills 生态的设计哲学：**用户描述场景，AI 负责发现和安装工具。**

### 触发

在 Claude Code（或任何支持 Agent Skills 的 agent）里说：

```
整理视频
organize my downloads
刮削
media scraper
```

### 完整流程（AI 自动执行）

```
1. 扫描目录 → 输出 19 个视频文件 JSON
2. TMDB 查证 → 确认是 2 部剧（Yellowstone + 1883），各 S1
3. 生成计划 → 预览改名和目录结构
4. 用户确认 → 
5. 执行 → 19 个文件，0 错误
```

**结果：**

```
Downloads/TV Shows/
├── 1883/Season 01/         10 集
├── Yellowstone/Season 01/   9 集
└── 唐朝诡事录/
    ├── Season 01/          36 集
    ├── Season 02/          40 集
    └── Season 03/          21 集
```

打开 VidHub/Infuse，海报、集名、演员全部自动出来。



## 五、关键洞察

**1. Skill 不是高级 Prompt，是「装了工具的 AI」。** Prompt 只能给建议，Skill 能执行。差距在于有没有可调用的脚本和强制的工作流。

**2. 开发 Skill 的正确姿势：真实数据驱动。** 不要先写完整设计文档，拿真实 NAS 目录跑，哪里报错修哪里。我们的 688 行代码里，至少一半是在真实数据上踩坑后补的。

**3. 发布即市场。** skills.sh 不是审核制，推到 GitHub 就自动收录。品类空白时，描述和关键词就是你唯一的 SEO。

**4. 跨平台是标配。** Agent Skills 是一个开放标准（agentskills.io），不是 Claude 独占。写一次，16+ agent 都能用。



## 附：项目地址

- GitHub: https://github.com/KAINODEX/media-organizer
- skills.sh: https://skills.sh/KAINODEX/media-organizer
- 安装: `npx skills add KAINODEX/media-organizer`



*写于 2026 年 6 月 7 日，用 Claude Code + 自建的 media-organizer skill 整理了自己的 NAS。*
