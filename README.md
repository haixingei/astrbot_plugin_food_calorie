# 食物卡路里提醒（AstrBot 插件）

发食物/饮料图片时，给当前模型补一句「自然地聊一下热量」的提示，让 AI 用自己的口气回答。

**不单独抢回复、不调用外部视觉 API、不保存聊天数据。**

> 适合已经在 AstrBot 里使用支持图片的模型，并且希望「发图随手问热量」时得到一条自然回复的用户。

---

## ✨ 功能

- **只补提示，不抢回复**：插件不直接 `send_message`，图片和文字都走 AstrBot 正常聊天管线。
- **群聊只回一条**：如果使用会话合并插件，文字 + 图片会合并成一次请求，不会出现「热量卡片 + 普通回复」两条。
- **两种触发模式**：
  - `auto`：目标会话里发图就补提示，由模型判断是不是食物；
  - `keyword`：只有图片同时带「热量 / 多少卡 / 大卡」等词时才补提示。
- **自然口气**：默认提示要求模型用日常聊天口吻，不要列清单、不要用「识别到」「估算」这类报告体。
- **明确问热量时给数字**：命中关键词时，提示会要求回复里带一个大概数字。
- **安全白名单**：群聊必须配置群号；私聊必须显式开启并配置 QQ 白名单。
- **无数据库**：插件不保存图片、聊天正文、热量记录或用户画像。

## 工作原理

```text
群/私聊图片
   │
   ▼
AstrBot 正常聊天管线
   │
   ├─ 插件在 on_llm_request 阶段检查：
   │    1. 有图片？
   │    2. 会话在白名单？
   │    3. 触发模式/关键词命中？
   │
   └─ 命中 → 在本次 system prompt 末尾追加一小段提示
              （不写入聊天历史、不改数据库）
   │
   ▼
当前模型用自己的人格自然回复
```

插件不直接读取图片内容，也不调用任何视觉 API；图片由 **AstrBot 当前配置的模型**处理。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| AstrBot | `>= 4.0.0` |
| 平台 | 当前适配 `aiocqhttp`（QQ / OneBot） |
| 模型 | 必须支持图片输入；纯文本模型看不到图片，插件也不会额外生效 |
| Python 包 | 无额外第三方依赖 |

## 安装

### 方式一：AstrBot 插件市场

1. 打开 AstrBot 管理端 → **插件市场**；
2. 搜索 `食物卡路里` 或 `astrbot_plugin_food_calorie`；
3. 安装后进入插件配置；
4. 至少填写 `group_ids`（或显式开启私聊并填写 `private_ids`）；
5. 重启 AstrBot。

### 方式二：从 GitHub 手动安装

```bash
cd AstrBot/data/plugins
git clone https://github.com/haixingei/astrbot_plugin_food_calorie.git
```

然后重启 AstrBot。

### 方式三：解压安装

把本仓库文件夹放到：

```text
AstrBot/data/plugins/astrbot_plugin_food_calorie/
```

确保 `main.py`、`metadata.yaml`、`_conf_schema.json` 都在这个目录下，然后重启。

## 快速开始

### 1. 配置群号

在 AstrBot 管理端 → 插件 → 食物卡路里提醒：

```json
{
  "enable": true,
  "trigger_mode": "auto",
  "group_ids": ["你的群号"]
}
```

群号就是 QQ 群号，例如 `123456789`。

### 2. 私聊（可选）

默认 **不启用私聊**。如果需要：

```json
{
  "enable_private": true,
  "private_ids": ["你的QQ号"]
}
```

> 安全说明：私聊白名单为空时不会匹配任何私聊，不会因为忘记填而全局生效。

### 3. 重启并验证

重启 AstrBot 后，在配置的群里发一张食物图片，带一句：

> 这个大概多少卡？

如果模型支持图片，就会用自然口气回答。

插件默认日志会显示：

```text
[食物热量] 已把「自然聊热量」提示并入本次请求（群，明确问热量）
```

没有这条日志，就说明图片、会话或触发条件没有命中。

## 配置项

| 字段 | 默认 | 说明 |
| --- | --- | --- |
| `enable` | `true` | 总开关。默认开启，但没配置白名单时不会生效 |
| `trigger_mode` | `auto` | `auto`：发图就补提示；`keyword`：带热量关键词才补 |
| `trigger_keywords` | 见下 | 命中后视为“明确在问热量”，要求回复带数字 |
| `group_ids` | `[]` | 生效群号白名单；为空时群聊不生效 |
| `enable_private` | `false` | 是否启用私聊 |
| `private_ids` | `[]` | 私聊 QQ 白名单；为空时不匹配任何私聊 |
| `hint` | `""` | 自定义追加提示；留空使用内置文案 |
| `log_injections` | `true` | 是否记录注入日志（不记录聊天正文） |

默认关键词：

```json
["卡路里", "热量", "多少卡", "大卡", "kcal", "会胖", "减肥", "吃了多少"]
```

完整说明见 [docs/CONFIGURATION.md](docs/CONFIGURATION.md)。

## 示例

**群聊（auto / keyword 均可）**

> 用户：[食物图片] 今天吃这个  
> AI：这盘大概七百多大卡吧，米饭和鸡腿占大头，青菜没多少～不过你吃得挺少的诶。

**明确问热量（会带数字）**

> 用户：[食物图片] 这个多少卡？  
> AI：我猜大概五百多大卡，主要是酱料和油炸的部分，光看图片只能估个大概。

**非食物图片**

> 用户：[表情包]  
> AI：照常接梗聊天，不会硬报热量。

## 它不做什么

- 不直接调用视觉模型或任何外部 API；
- 不直接发消息，不 `stop_event`；
- 不保存图片、聊天记录、热量数据；
- 不做营养学诊断，不替代专业建议；
- 不保证热量精确——图片看不到糖、油、酱料和隐藏配料。

## 隐私与安全

- 默认群白名单为空、私聊关闭，安装后不会自动在任何会话生效；
- 只会在命中的**单次模型请求**里追加提示，不写入聊天历史；
- 日志只记录“是否注入”，不记录聊天正文；
- 图片仍会经过 AstrBot 当前模型的正常处理流程，具体数据策略取决于你的模型供应商；
- 插件没有管理员命令，也不访问文件系统或网络。

详见 [docs/PRIVACY.md](docs/PRIVACY.md)。

## 常见问题

### 发了图但没反应？

1. 群号是否填在 `group_ids` 里？
2. 当前模型是否支持图片？
3. `trigger_mode=keyword` 时是否带了关键词？
4. 是否重启了 AstrBot？
5. 查看日志有没有 `[食物热量]` 注入记录。

### 会不会和群消息合并插件冲突？

不会。本插件只修改本次请求的 system prompt，不直接回复；文字和图片仍由 AstrBot / 会话合并插件统一处理。

### 会不会每次发图都强行报热量？

不会。`auto` 模式只是补提示，模型仍会自己判断是不是食物、值不值得聊；非食物图不会硬报。

### 热量数字准吗？

只能按图片可见内容粗略估算，隐藏的糖、油、酱料和份量都可能导致偏差。请把它当作聊天参考，不是营养数据。

## 开发与测试

```bash
python -m pip install pytest
python -m pytest -q
```

测试只覆盖 `logic.py` 的纯逻辑，不需要启动 AstrBot。

目录：

```text
astrbot_plugin_food_calorie/
├── main.py                 # AstrBot 插件入口
├── logic.py                # 纯逻辑（白名单/触发/提示拼装）
├── metadata.yaml           # 插件市场元数据
├── _conf_schema.json       # 配置 schema
├── README.md
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
├── tests/test_logic.py
├── examples/config.example.json
└── docs/
    ├── CONFIGURATION.md
    ├── PRIVACY.md
    └── PUBLISHING.md
```

## 发布信息

- 作者：海星盖
- 仓库：<https://github.com/haixingei/astrbot_plugin_food_calorie>
- 版本：v1.2.0
- 发布流程见 [docs/PUBLISHING.md](docs/PUBLISHING.md)

## License

MIT，见 [LICENSE](LICENSE)。

---

## English quick start

AstrBot plugin that appends a natural calorie hint to the current LLM request when a food image is sent. It does not send messages directly, call external vision APIs, or store chat data.

1. Install from the AstrBot plugin market or clone into `AstrBot/data/plugins/`.
2. Configure `group_ids` (required) and optionally `enable_private` + `private_ids`.
3. Restart AstrBot.
4. Send a food image in a configured chat. The current vision-capable model will answer naturally.

No extra Python dependencies. MIT licensed.
