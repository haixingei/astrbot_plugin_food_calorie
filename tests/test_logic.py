from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import logic  # noqa: E402


def test_default_group_and_private_are_safe() -> None:
    assert logic.is_target_session(123, 456, [], False, []) is False
    assert logic.is_target_session(None, 456, [], True, []) is False


def test_group_whitelist() -> None:
    assert logic.is_target_session(123, 999, ["123"], False, []) is True
    assert logic.is_target_session(124, 999, ["123"], False, []) is False


def test_private_requires_enable_and_whitelist() -> None:
    assert logic.is_target_session(None, 456, [], True, ["456"]) is True
    assert logic.is_target_session(None, 789, [], True, ["456"]) is False
    assert logic.is_target_session(None, 456, [], False, ["456"]) is False


def test_explicit_intent_by_keyword_or_prefix() -> None:
    keywords = ["热量", "多少卡"]
    assert logic.is_explicit_intent("这个多少卡呀", keywords) is True
    assert logic.is_explicit_intent("这顿吃了多少", keywords) is False
    assert logic.is_explicit_intent("/热量 这盘", keywords) is True
    assert logic.is_explicit_intent("／卡路里", keywords) is True
    assert logic.is_explicit_intent("", keywords) is False


def test_normalize_mode_and_parse_list() -> None:
    assert logic.normalize_mode("keyword") == "keyword"
    assert logic.normalize_mode("always") == "auto"
    assert logic.normalize_mode(None) == "auto"
    assert logic.parse_list([" 123 ", "", 456]) == ["123", "456"]
    assert logic.parse_list("1, 2") == ["1", "2"]


def test_build_and_append_hint() -> None:
    normal = logic.build_hint("", False)
    explicit = logic.build_hint("", True)
    assert "大概多少大卡" in normal
    assert "务必给出一个大概数字" in explicit
    assert logic.append_hint("base", normal) == "base\n\n[图片提醒]\n" + normal
    assert logic.append_hint("", normal) == normal
