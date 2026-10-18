"""Web app for the WeChat bot server.

`template_folder` is resolved from this file, not from the package: `web/app.py`
lives one level below the project root, so a bare `Flask(__name__)` would look in
`web/templates/` and every page would 500 with TemplateNotFound.  The same applies
to `instance_path`, which keeps the SQLite file out of the package directory.
"""

import json
import os
import sys

from . import paths

if str(paths.PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(paths.PROJECT_ROOT))

from flask import Flask, jsonify, redirect, render_template, request, url_for

from .bot.api import bp
from .bot.bridge import get_bridge
from .bot.groups import mute
from .bot.handlers import handle
from .models import Contact, Message, Rule, db

APP_NAME = "\U0001f4ac wechat-server"
ACTIONS = ("reply", "api", "forward")


def _rule_rows():
    return Rule.query.order_by(Rule.id.desc()).all()


def _message_rows(limit=50):
    return Message.query.order_by(Message.id.desc()).limit(limit).all()


def _page_context(**extra):
    """Context every page needs; `form` is always defined for the rule form.

    `rules.html` renders a rule form on a plain GET, when nothing has been
    submitted yet, so a missing `form` would be an UndefinedError 500 on the page
    rather than on the POST that actually failed validation.
    """
    bridge = get_bridge()
    ctx = {
        "app_name": APP_NAME,
        "form": extra.pop("form", {}),
        "actions": ACTIONS,
        "rule_count": Rule.query.count(),
        "enabled_count": Rule.query.filter_by(enabled=1).count(),
        "message_count": Message.query.count(),
        "contact_count": Contact.query.count(),
        "muted_count": len(bridge.muted),
        "group_count": len(bridge.get_groups()),
    }
    ctx.update(extra)
    return ctx


def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(
        __name__, template_folder=str(paths.TEMPLATES_DIR), instance_path=str(paths.INSTANCE_DIR)
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "wechat.db")
    db.init_app(app)
    with app.app_context():
        paths.ensure_runtime_dirs()
        db.create_all()
    app.register_blueprint(bp)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            rules=_rule_rows(),
            messages=_message_rows(),
            contacts=Contact.query.order_by(Contact.id).all(),
            groups=get_bridge().get_groups(),
            muted=sorted(get_bridge().muted),
            **_page_context(),
        )

    @app.get("/rules")
    def rules():
        return render_template("rules.html", rules=_rule_rows(), **_page_context())

    @app.post("/rules/new")
    def create_rule():
        form = {
            "trigger": (request.form.get("trigger") or "").strip(),
            "action": (request.form.get("action") or "reply").strip(),
            "text": (request.form.get("text") or "").strip(),
        }
        if not form["trigger"]:
            return render_template(
                "rules.html",
                rules=_rule_rows(),
                error="trigger is required",
                form=form,
                **_page_context(),
            ), 400
        if form["action"] not in ACTIONS:
            return render_template(
                "rules.html",
                rules=_rule_rows(),
                error="unknown action: " + form["action"],
                form=form,
                **_page_context(),
            ), 400
        rule = Rule(
            trigger=form["trigger"],
            action=form["action"],
            params_json=json.dumps({"text": form["text"]} if form["text"] else {}),
        )
        db.session.add(rule)
        db.session.commit()
        return redirect(url_for("rules"))

    @app.post("/rules/<int:rid>/toggle")
    def toggle_rule(rid):
        rule = db.session.get(Rule, rid)
        if rule is None:
            return render_template("404.html", **_page_context()), 404
        rule.enabled = 0 if rule.enabled else 1
        db.session.commit()
        return redirect(url_for("rules"))

    @app.post("/rules/<int:rid>/delete")
    def delete_rule(rid):
        rule = db.session.get(Rule, rid)
        if rule is not None:
            db.session.delete(rule)
            db.session.commit()
        return redirect(url_for("rules"))

    @app.post("/groups/<group_id>/mute")
    def mute_group(group_id):
        mute(
            group_id,
            (request.form.get("member") or "").strip(),
            int(request.form.get("minutes") or 60),
        )
        return redirect(url_for("index"))

    @app.post("/simulate")
    def simulate():
        """Run `bot.handlers.handle` against typed text, the same path as a real message."""
        form = {"text": (request.form.get("text") or "").strip()}
        reply = handle(form["text"]) if form["text"] else None
        return render_template(
            "index.html",
            rules=_rule_rows(),
            messages=_message_rows(),
            contacts=Contact.query.order_by(Contact.id).all(),
            groups=get_bridge().get_groups(),
            muted=sorted(get_bridge().muted),
            form=form,
            sim={"text": form["text"], "reply": reply},
            **_page_context(),
        )

    @app.get("/api/health")
    def api_health():
        return jsonify({"status": "ok", "app": APP_NAME, "rules": Rule.query.count()})

    @app.errorhandler(404)
    def not_found(_exc):
        return render_template("404.html", **_page_context()), 404

    def _app_routes():
        return sorted((r.rule, r.endpoint) for r in app.url_map.iter_rules())

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), debug=False)

    return app


app = build_app()
