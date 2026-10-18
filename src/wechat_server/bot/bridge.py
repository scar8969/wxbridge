"""In-process stand-in for an itchat client.

The real bridge needs a logged-in WeChat session and a network socket, neither of
which exists in CI.  Every method here is local state, so the web app, the CLI and
the tests all exercise the same object graph without one.
"""

import threading

__all__ = ["WechatBridge", "get_bridge"]


class WechatBridge:
    """Mock itchat client: contacts, groups, mute set, send()."""

    def __init__(self):
        self._cbs = []
        self.contacts = {"alice": "Alice", "bob": "Bob"}
        self.groups = {"g1": "Dev Team"}
        self.muted = set()

    def on_message(self, cb):
        self._cbs.append(cb)

    def send(self, to, text):
        return True

    def get_contacts(self):
        return [{"wxid": k, "name": v, "is_group": False} for k, v in self.contacts.items()]

    def get_groups(self):
        return [{"wxid": k, "name": v, "is_group": True} for k, v in self.groups.items()]

    def is_muted(self, member):
        return member in self.muted


_bridge = None
_lock = threading.Lock()


def get_bridge():
    """Process-wide singleton.

    `bot.groups.mute()` and `bot.api` must mutate the SAME bridge, otherwise the
    mute set and the sent messages live in two different objects.
    """
    global _bridge
    with _lock:
        if _bridge is None:
            _bridge = WechatBridge()
    return _bridge
