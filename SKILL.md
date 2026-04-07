---
name: bing-keyword-image-downloader
description: 当用户需要按关键词从 Bing 公开图片搜索结果中批量下载图片时使用。遇到类似“帮我从 Bing 按关键词下载 10 张图片”“批量抓取 Bing 图片”“按关键词保存 Bing 图片到本地”这类请求时，应主动使用这个 skill。它专门处理基于关键词的 Bing 图片搜索、分页收集候选链接、跳过失败源站并保存到本地目录的工作流。
---

# Bing 关键词图片批量下载

这个 skill 用于复用当前目录中的 `scripts/bing_image_downloader.py` 脚本，让其他 agent 能稳定完成“按关键词从 Bing 公开图片结果中批量下载图片”的任务。

## 何时使用
当用户明确提出以下类型需求时，优先使用本 skill：
- 按关键词从 Bing 图片搜索下载若干图片
- 想保存 10、50、100 张 Bing 搜索图片到本地
- 想通过分页抓取更多 Bing 图片候选链接
- 想复用现成脚本完成 Bing 图片批量下载任务

如果用户要的是：
- 其他搜索引擎图片下载
- 图像识别、去重、分类
- 非关键词方式（例如固定页面 URL）

则这个 skill 不是最佳选择。

## 依赖文件
- 主脚本：`scripts/bing_image_downloader.py`
- 测试文件：`tests/test_bing_image_downloader.py`

## 工作流程
按下面顺序执行：

1. 读取用户需求中的关键词、目标数量、页数。
2. 如果用户没给页数，按下面经验值选择：
   - 10 张：`--pages 3`
   - 50 张：`--pages 5`
   - 100 张：`--pages 10`
3. 使用 `uv run --with requests python` 运行脚本。
4. 检查输出中：
   - 成功下载数量
   - 候选链接数量
   - 失败原因（常见为 403、SSL、超时）
5. 向用户汇报：
   - 实际保存目录
   - 成功数量
   - 是否达到目标数量
   - 如未达标，说明通常是第三方源站拒绝访问而非脚本崩溃

## 推荐命令模板

### 下载 10 张
```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 10 --pages 3
```

### 下载 50 张
```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 50 --pages 5
```

### 下载 100 张
```bash
uv run --with requests python "scripts/bing_image_downloader.py" "cat" --limit 100 --pages 10
```

## 参数映射规则
- 用户说“下载 10 张” → `--limit 10`
- 用户说“下载 50 张” → `--limit 50`
- 用户说“下载 100 张” → `--limit 100`
- 用户没说页数时，按上面的推荐默认值设置 `--pages`
- 用户明确给出页数时，尊重用户输入

## 输出说明
脚本会把结果保存到：
```text
downloads/<关键词>/
```

例如关键词 `cat` 会保存到：
```text
downloads/cat/
```

文件名按顺序编号，例如：
- `001.jpg`
- `002.jpg`
- `003.png`

## 常见问题解释
### 为什么会出现下载失败？
因为 Bing 页面里的原图通常来自第三方网站，不是都由 Bing 自己托管。第三方站点可能拒绝脚本访问，常见错误：
- `403 Forbidden`
- SSL 证书错误
- 连接超时
- 404 Not Found

### 为什么加大 `--pages` 后下载数量会提高？
因为脚本会抓更多结果页，收集更大的候选链接池。即使其中一部分链接失效，仍然可以用后面的候选补位。

## 给用户的汇报模板
完成后可按下面结构回复用户：

```text
已执行 Bing 图片批量下载。
- 关键词：<关键词>
- 目标数量：<limit>
- 抓取页数：<pages>
- 候选链接数：<候选数量>
- 实际成功下载：<成功数量>
- 保存目录：downloads/<关键词>/

如果存在失败链接，通常是第三方图片源拒绝访问，不影响脚本继续补充后续候选。
```

## 注意事项
- 这是一个“按关键词下载 Bing 公开图片”的专用 skill，不要扩展解释成通用全网图片下载器。
- 优先复用现有脚本，不要重复手写新下载器，除非用户明确要求修改或升级脚本。
- 当用户要求“提高下载数量”时，优先建议增加 `--pages`，而不是先改成并发下载。
