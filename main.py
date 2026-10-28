"""食物卡路里提醒：发食物图片时，给模型补一句自然聊热量的提示。

插件不直接发消息、不调用视觉 API、不保存聊天内容；只在本次模型请求的
system prompt 末尾追加一小段提示，让模型用当前人格自然回答。
"""

from __future__ import annotations

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.core.message.components import Image

try:  # AstrBot 以包方式加载时走相对导入
    from .logic import (
        append_hint,
        build_hint,
        is_explicit_intent,
        is_target_session,
        normalize_mode,
        parse_list,
    )
except ImportError:  # 本地单文件调试时兜底
    from logic import (  # type: ignore[no-redef]
        append_hint,
        build_hint,
        is_explicit_intent,
        is_target_session,
        normalize_mode,
        parse_list,
    )


class FoodCaloriePlugin(Star):
    """发图/问热量时，给模型补一句自然回答提示（不直接回复）。"""

    def __init__(self, context: Context, config: dict | None = None) -> None:
        super().__init__(context)
        cfg = config or {}
        self.enabled = bool(cfg.get("enable", True))
        self.trigger_mode = normalize_mode(cfg.get("trigger_mode", "auto"))
        self.keywords = parse_list(cfg.get("trigger_keywords") or [])
        self.group_ids = set(parse_list(cfg.get("group_ids") or []))
        self.enable_private = bool(cfg.get("enable_private", False))
        self.private_ids = set(parse_list(cfg.get("private_ids") or []))
        self.hint = str(cfg.get("hint") or "").strip()
        self.log_injections = bool(cfg.get("log_injections", True))

        logger.info(
            "[食物热量] 已加载（提示注入模式）：%s 群=%s 私聊=%s 关键词=%d个",
            self.trigger_mode,
            sorted(self.group_ids) or "未配置",
            "开" if self.enable_private else "关",
            len(self.keywords),
        )

    # ------------------------------------------------------------ 触发判断
    def _is_target_session(self, event: AstrMessageEvent) -> bool:
        return is_target_session(
            event.get_group_id(),
            event.get_sender_id(),
            self.group_ids,
            self.enable_private,
            self.private_ids,
        )

    def _explicit_intent(self, text: str) -> bool:
        return is_explicit_intent(text, self.keywords)

    @staticmethod
    def _has_image(event: AstrMessageEvent) -> bool:
        try:
            return any(isinstance(comp, Image) for comp in event.get_messages())
        except Exception:
            return False

    # ---------------------------------------------------------------- hook
    @filter.on_llm_request()
    async def inject_calorie_hint(self, event: AstrMessageEvent, req) -> None:
        if not self.enabled:
            return
        if event.get_extra("_food_calorie_hint_added"):
            return  # 同一条消息只补一次
        if not self._has_image(event):
            return
        if not self._is_target_session(event):
            return

        text = (event.message_str or "").strip()
        explicit = self._explicit_intent(text)
        if self.trigger_mode == "keyword" and not explicit:
            return

        req.system_prompt = append_hint(req.system_prompt, build_hint(self.hint, explicit))
        event.set_extra("_food_calorie_hint_added", True)

        if self.log_injections:
            logger.info(
                "[食物热量] 已把「自然聊热量」提示并入本次请求（%s，%s）",
                "群" if str(event.get_group_id() or "") else "私聊",
                "明确问热量" if explicit else "带图自动提醒",
            )
