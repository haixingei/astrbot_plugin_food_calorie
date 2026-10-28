# 发布到 GitHub 与 AstrBot 插件市场

这份清单帮助你把本目录发布成可被其他人安装的插件。

## 1. 发布前替换占位信息

打开 `metadata.yaml`：

```yaml
author: "海星盖"
repo: "https://github.com/haixingei/astrbot_plugin_food_calorie"
```

至少修改：

- `author`：你的署名；
- `repo`：你的公开 GitHub 仓库地址；
- `display_name` / `desc`：可按需要润色。

`LICENSE` 里的版权人也可以改成你的名字或组织。

## 2. 本地初始化 Git 仓库

在本目录执行：

```bash
git init
git add .
git commit -m "feat: initial public release v1.2.0"
```

确认没有提交：

- `data/`、`config/`；
- 真实群号、QQ 号；
- `.env`、API Key、Token；
- `__pycache__`。

## 3. 创建 GitHub 仓库并推送

在 GitHub 新建空仓库，例如：

```text
astrbot_plugin_food_calorie
```

然后：

```bash
git branch -M main
git remote add origin https://github.com/haixingei/astrbot_plugin_food_calorie.git
git push -u origin main
```

建议在仓库 About 里填：

- Description：`AstrBot 插件：发食物图片时自然补充热量提示`
- Topics：`astrbot`、`astrbot-plugin`、`qqbot`、`calorie`、`vision`

## 4. 打版本标签

```bash
git tag v1.2.0
git push origin v1.2.0
```

在 GitHub Releases 里创建 `v1.2.0`，可以附上：

- CHANGELOG 摘要；
- 安装方式；
- 配置示例。

## 5. 提交 AstrBot 插件市场

在 AstrBot 插件市场的发布入口填写你的 GitHub 仓库地址，并确认：

- 仓库是公开的；
- 根目录有 `metadata.yaml`；
- `name` 与插件目录名一致；
- `version` 与 CHANGELOG/Release 一致；
- `repo` 是可访问的 GitHub URL；
- 插件能从干净 AstrBot 安装并加载。

不同版本的市场提交页面可能略有差异，按市场页面要求填写即可。

## 6. 发布前自测

```bash
python -m pytest -q
python -m py_compile main.py logic.py
```

在干净 AstrBot 环境里：

1. 安装插件；
2. 配置 `group_ids`；
3. 发食物图片；
4. 检查只回一条、自然、没有硬报；
5. 检查日志有注入记录；
6. 检查配置为空时不会在任何会话生效。

## 7. 版本维护

- 修改功能后更新 `metadata.yaml` 的 `version`；
- 在 `CHANGELOG.md` 记录；
- 重新打 tag；
- 让 AstrBot 市场重新抓取版本；
- 避免 force push 已发布 tag。

## 8. 发布后建议

- 在 README 顶部加入实际仓库地址；
- 开启 GitHub Issues；
- 在仓库设置里启用 private vulnerability reporting（如可用）；
- 不把用户群号/QQ 号写进 issue 模板或示例；
- 定期检查 AstrBot API 兼容性。
