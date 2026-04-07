# bing-keyword-image-downloader

一个基于 Python 的 Bing 公开图片关键词批量下载项目，同时也整理成了一个可供其他 agent 复用的 Claude skill。

它的核心能力是：
- 按关键词从 Bing 图片搜索结果页提取图片原始链接
- 通过分页收集更大的候选链接池
- 顺序下载图片到本地目录
- 跳过 403、SSL、超时、404 等失败源站，继续尝试后续候选链接

## 项目用途

这个项目适合以下场景：
- 学习关键词图片抓取的基本流程
- 学习如何从搜索结果页中提取候选资源链接
- 学习如何通过分页扩大候选池，提高总下载成功数量
- 作为一个可复用 skill，交给其他 agent 按关键词执行 Bing 图片批量下载任务

## 目录结构

```text
bing-keyword-image-downloader/
├── .gitignore
├── README.md
├── SKILL.md
├── evals/
│   └── evals.json
├── scripts/
│   └── bing_image_downloader.py
└── tests/
    └── test_bing_image_downloader.py
```

说明：
- `SKILL.md`：skill 的说明文档，定义何时触发、如何执行、如何汇报结果
- `scripts/bing_image_downloader.py`：主脚本
- `tests/test_bing_image_downloader.py`：单元测试
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
- `--pages`：抓取的 Bing 结果页数

推荐经验值：
- 10 张：`--pages 3`
- 50 张：`--pages 5`
- 100 张：`--pages 10`

如果你更看重“尽量下载满目标数量”，通常优先增加 `--pages`，而不是先改成并发下载。

## 工作原理

脚本主要分为 3 个步骤：

1. 请求 Bing 图片搜索结果页
2. 从 HTML 中提取图片原始地址 `murl`
3. 逐个尝试下载，并把成功文件保存到本地

为了提高总下载数量，脚本不会只依赖单页结果，而是会：
- 分页抓取多个 Bing 图片结果页
- 去重后形成候选链接池
- 顺序尝试下载，失败就跳过，继续使用后续候选链接补位

这也是它比“只抓一页再下载”的做法更容易下载满目标数量的原因。

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

## 常见失败原因

Bing 搜索结果中的原图通常来自第三方网站，而不是都由 Bing 自己托管，因此常见失败并不意味着脚本崩溃。

常见原因包括：
- `403 Forbidden`
- SSL 证书错误
- 连接超时
- `404 Not Found`

这类失败出现时，脚本会继续尝试后续候选链接。

## 运行测试

### 单元测试

```bash
uv run --with requests python -m unittest tests/test_bing_image_downloader.py
```

### 冒烟测试

```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 10 --pages 3
```

## Skill 用法

如果这是作为 Claude skill 使用，核心说明见：

- `SKILL.md`

这个 skill 适用于：
- 按关键词从 Bing 图片搜索下载若干图片
- 想保存 10、50、100 张 Bing 搜索图片到本地
- 想通过分页抓取更多 Bing 图片候选链接
- 想复用现成脚本完成 Bing 图片批量下载任务

## 注意事项

- 本项目是“按关键词下载 Bing 公开图片”的专用实现，不是通用全网图片下载器
- 当目标数量较大时，是否能下载满会受到第三方源站可访问性的影响
- 如果希望提高成功数量，优先增加 `--pages`
- `downloads/` 是运行产物，默认不提交到 Git 仓库

## License

当前仓库未单独声明许可证。如需开源发布，建议后续补充 `LICENSE` 文件。
