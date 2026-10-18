import json
import re


def match(rule, text: str) -> bool:
    trigger = rule.trigger or ""
    if trigger.startswith("re:"):
        try:
            return bool(re.search(trigger[3:], text, re.I))
        except re.error:
            return False
    if trigger.endswith("*"):
        return text.lower().startswith(trigger[:-1].lower())
    return text.lower() == trigger.lower()


def handle(msg_text: str):
    """Return the reply for `msg_text`, or None when no enabled rule matches."""
    from ..models import Rule

    for rule in Rule.query.filter_by(enabled=1).all():
        if match(rule, msg_text):
            params = json.loads(rule.params_json or "{}")
            if rule.action == "reply":
                return params.get("text", "ok")
            if rule.action == "api":
                import urllib.request

                try:
                    with urllib.request.urlopen(params["url"], timeout=10) as r:
                        data = json.loads(r.read())
                        return params.get("template", "{value}").format(**data)
                except Exception:
                    return "API error"
            if rule.action == "forward":
                return f"forwarded: {msg_text}"
    return None
