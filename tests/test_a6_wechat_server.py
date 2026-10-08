"""A6 wechat-server — tests. Run: pytest test_a6_wechat_server.py"""
import sys, os

import pytest

class FakeRule:
    def __init__(self, trigger, action="reply", params_json="{}"):
        self.trigger, self.action, self.params_json = trigger, action, params_json

def test_match_exact():
    from wechat_server.bot.handlers import match
    assert match(FakeRule("hi"), "hi")
    assert not match(FakeRule("hi"), "hello")

def test_match_prefix():
    from wechat_server.bot.handlers import match
    assert match(FakeRule("!weather*"), "!weather delhi")

def test_match_regex():
    from wechat_server.bot.handlers import match
    assert match(FakeRule("re:^!price\\s+\\d+$"), "!price 100")

def test_welcome_template():
    from wechat_server.bot.groups import welcome
    assert "Alice" in welcome(1, "Alice")

def test_bridge_mock():
    from wechat_server.bot.bridge import WechatBridge
    b = WechatBridge()
    assert b.send("alice", "hi") is True
    assert len(b.get_contacts()) >= 2
