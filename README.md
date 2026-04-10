# bing-keyword-image-downloader

一个基于 Python 的多来源关键词图片下载项目，同时也整理成了一个可供其他 agent 复用的 Claude skill。

## 项目链接

- GitHub 仓库：https://github.com/16Miku/image-downloader-skill
- ClawHub 页面：https://clawhub.ai/16miku/bing-keyword-image-downloader

它当前的核心能力是：
- 按关键词从多个来源收集图片候选（当前支持 Bing 和 DemoSource）
- 通过分页收集更大的候选池
- 对候选进行基础去重
- 顺序下载图片到本地目录
- 记录下载元数据与历史索引，避免重复下载
- 输出本次运行的来源统计与下载摘要

## 项目用途

这个项目适合以下场景：
- 学习关键词图片抓取的基本流程
- 学习如何从搜索结果页中提取候选资源链接
- 学习如何通过分页扩大候选池，提高总下载成功数量
- 学习如何记录下载元数据与历史索引，避免重复下载
- 作为一个可复用 skill，交给其他 agent 按关键词执行多来源图片批量下载任务

## 目录结构

```text
bing-keyword-image-downloader/
├── .gitignore
├── README.md
├── SKILL.md
├── evals/
│   └── evals.json
├── image_downloader/
│   ├── reporting.py
│   ├── storage.py
│   └── sources/
│       ├── bing.py
│       └── demo.py
├── scripts/
│   └── bing_image_downloader.py
└── tests/
    ├── test_bing_image_downloader.py
    └── test_integration_multisource.py
```

说明：
- `SKILL.md`：skill 的说明文档，定义何时触发、如何执行、如何汇报结果
- `scripts/bing_image_downloader.py`：CLI 主脚本，负责组织多来源收集、去重、下载与摘要输出
- `image_downloader/sources/`：不同来源的候选收集实现
- `image_downloader/storage.py`：下载记录、历史索引与重复跳过逻辑
- `image_downloader/reporting.py`：运行摘要构建
- `tests/test_bing_image_downloader.py`：主脚本与基础行为测试
- `tests/test_integration_multisource.py`：多来源流程集成测试
- `evals/evals.json`：skill 的示例评测用例
- `downloads/`：运行时生成的图片目录，已被 `.gitignore` 忽略，不纳入版本控制

## 环境要求

- Python 3
- [uv](https://github.com/astral-sh/uv)
- `requests`

本项目默认使用 `uv` 运行，不要求你提前全局安装依赖。

## 快速开始

在项目根目录执行。

### 下载 10 张图片

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 10 --pages 3
```

### 下载 50 张图片

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 50 --pages 5
```

### 下载 100 张图片

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 100 --pages 10
```

## 参数说明

- `keyword`：搜索关键词，例如 `cat`、`dog`、`landscape`
- `--limit`：目标下载数量
- `--pages`：抓取各来源候选时使用的结果页数，用来扩大候选池

推荐经验值：
- 10 张：`--pages 3`
- 50 张：`--pages 5`
- 100 张：`--pages 10`

如果你更看重“尽量下载满目标数量”，通常优先增加 `--pages`，而不是先改成并发下载。

当前 CLI 会固定使用 `bing` 和 `demo` 两个来源执行候选收集。

## 工作原理

脚本主要分为 4 个步骤：

1. 调用多个来源收集关键词图片候选（当前支持 Bing 和 DemoSource）
2. 合并候选并按图片 URL 做基础去重
3. 结合历史索引跳过此前已下载过的内容
4. 逐个尝试下载，并输出来源统计与本次运行摘要

为了提高总下载数量，脚本不会只依赖单页结果，而是会：
- 对每个来源按页抓取更多结果，扩大候选池
- 合并多个来源返回的候选内容
- 去重后顺序尝试下载，失败就跳过，继续使用后续候选补位
- 对已下载过的候选进行跳过，避免重复保存

这也是它比“只抓一页、只用单一来源再下载”的做法更容易下载满目标数量的原因。

## 输出位置

图片会保存到：

```text
downloads/<关键词>/
```

例如下载 `cat`：

```text
downloads/cat/
```

文件名按顺序编号，例如：
- `001.jpg`
- `002.jpg`
- `003.png`

目录下还会记录下载元数据与历史索引，供后续运行时判断是否应跳过重复候选。

## 常见失败原因

搜索结果中的原图通常来自第三方网站，而不是都由当前来源自己托管，因此常见失败并不意味着脚本崩溃。

常见原因包括：
- `403 Forbidden`
- SSL 证书错误
- 连接超时
- `404 Not Found`

这类失败出现时，脚本会继续尝试后续候选链接。

## 运行测试

### 单元测试

```bash
uv run --with requests python -m unittest tests.test_bing_image_downloader tests.test_models_and_sources tests.test_storage tests.test_integration_multisource -v
```

### 冒烟测试

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 10 --pages 3
```

## Skill 用法

如果这是作为 Claude skill 使用，核心说明见：

- `SKILL.md`

这个 skill 适用于：
- 按关键词批量下载公开图片到本地
- 想从 Bing 或当前脚本支持的多个来源收集图片候选
- 想保存 10、50、100 张关键词图片到本地
- 想通过增加页数或扩大候选池来提高最终成功数量
- 想复用现成脚本完成关键词图片批量下载任务，并获得保存目录与运行摘要
- 想避免重复下载之前已经保存过的内容

## 注意事项

- 本项目是“按关键词下载公开图片”的现成流程实现，不是通用全网图片下载器
- 当目标数量较大时，是否能下载满会受到第三方源站可访问性的影响
- 如果希望提高成功数量，优先增加 `--pages` 或扩大候选池
- `downloads/` 是运行产物，默认不提交到 Git 仓库

## License

当前仓库未单独声明许可证。如需开源发布，建议后续补充 `LICENSE` 文件。
