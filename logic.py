"""纯逻辑辅助：不依赖 AstrBot，便于单元测试和复用。"""

from __future__ import annotations

from collections.abc import Iterable

DEFAULT_HINT = (
    "图片里如果是食物或饮料，就用你平时的口气自然地聊一下是什么、大概多少大卡，"
    "像随口说的那样（比如「这个大概五百多大卡吧」）；对方问热量时一定要给个大概数字。"
    "不要列清单、不要用「识别到」「估算」「根据图片」这类词，也别把热量说成报告。"
    "如果图里不是吃的或者看不清，就别硬猜。"
)

COMMAND_PREFIXES = ("/热量", "／热量", "/卡路里", "／卡路里", "/kcal", "/热量查询")
VALID_MODES = {"auto", "keyword"}


def normalize_mode(value: object) -> str:
    """把配置里的触发模式收敛到 auto/keyword。"""
    mode = str(value or "auto").strip().lower()
    return mode if mode in VALID_MODES else "auto"


def parse_list(value: object) -> list[str]:
    """把配置里的列表/单个值统一成去空白字符串列表。"""
    if value is None:
        return []
    if isinstance(value, str):
        values: Iterable[object] = value.split(",")
    elif isinstance(value, Iterable):
        values = value
    else:
        values = [value]
    return [str(item).strip() for item in values if str(item).strip()]


def is_explicit_intent(text: str, keywords: Iterable[str]) -> bool:
    """用户是否明确在问热量：指令前缀或关键词命中。"""
    raw = str(text or "").strip()
    if not raw:
        return False
    if any(raw.startswith(prefix) for prefix in COMMAND_PREFIXES):
        return True
    low = raw.lower()
    return any(str(keyword).strip().lower() in low for keyword in keywords if str(keyword).strip())


def is_target_session(
    group_id: object,
    sender_id: object,
    group_ids: Iterable[str],
    enable_private: bool,
    private_ids: Iterable[str],
) -> bool:
    """判断当前消息是否在允许的会话里。

    安全默认：群白名单为空时群聊不生效；私聊必须显式打开并命中 QQ 白名单。
    空 private_ids 不表示“所有私聊”，避免安装后意外全局生效。
    """
    group = str(group_id or "").strip()
    if group:
        return group in {str(item).strip() for item in group_ids if str(item).strip()}
    if not enable_private:
        return False
    sender = str(sender_id or "").strip()
    allowed = {str(item).strip() for item in private_ids if str(item).strip()}
    return bool(sender and sender in allowed)


def build_hint(custom_hint: object, explicit: bool) -> str:
    """生成要追加的提示文本。"""
    hint = str(custom_hint or "").strip() or DEFAULT_HINT
    if explicit:
        hint += "\n（对方已经明确在问热量，回复里务必给出一个大概数字。）"
    return hint


def append_hint(system_prompt: object, hint: str) -> str:
    """把提示追加到系统提示末尾，保持空提示时也安全。"""
    base = str(system_prompt or "").rstrip()
    if not base:
        return hint.strip()
    return base + "\n\n[图片提醒]\n" + hint.strip()
