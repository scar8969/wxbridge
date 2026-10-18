from flask import Blueprint, jsonify, request

from ..models import Contact, Message, Rule, db
from .bridge import get_bridge
from .groups import mute

bp = Blueprint("bot", __name__)


@bp.post("/api/webhook")
def webhook():
    d = request.get_json(force=True, silent=True) or {}
    ok = get_bridge().send(d.get("to", ""), d.get("text", ""))
    return jsonify({"status": "sent" if ok else "failed"})


@bp.get("/api/messages")
def messages():
    contact = request.args.get("contact", "")
    q = Message.query
    if contact:
        c = Contact.query.filter_by(name=contact).first()
        if c:
            q = q.filter_by(contact_id=c.id)
    msgs = [
        {
            "id": m.id,
            "direction": m.direction,
            "text": m.text,
            "at": m.at.isoformat() if m.at else "",
        }
        for m in q.order_by(Message.id.desc()).limit(50).all()
    ]
    return jsonify({"messages": msgs})


@bp.post("/api/rules")
def add_rule():
    d = request.get_json(force=True, silent=True) or {}
    r = Rule(
        trigger=d.get("trigger", ""),
        action=d.get("action", "reply"),
        params_json=str(d.get("params", {})),
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"id": r.id})


@bp.get("/api/rules")
def list_rules():
    return jsonify(
        {
            "rules": [
                {"id": r.id, "trigger": r.trigger, "action": r.action, "enabled": r.enabled}
                for r in Rule.query.all()
            ]
        }
    )


@bp.post("/api/groups/<int:gid>/mute")
def mute_member(gid):
    d = request.get_json(force=True, silent=True) or {}
    mute(gid, d.get("member", ""), d.get("minutes", 60))
    return jsonify({"status": "muted"})
