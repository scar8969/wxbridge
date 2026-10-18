"""Group helpers: welcome text and member mute."""


def welcome(group_id, member):
    return f"Welcome {member}! 👋"


def mute(group_id, member, minutes):
    """Add `member` to the bridge mute set and report what was done."""
    from .bridge import get_bridge

    get_bridge().muted.add(member)
    return {"group": group_id, "member": member, "minutes": minutes}
