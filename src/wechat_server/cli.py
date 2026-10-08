"""Command line for the WeChat bot server.

Every import past argparse is deferred into the command body, so `cli.py --help`
works before Flask, SQLAlchemy or an itchat session exists on the machine -- --help
must not need a database.
"""
import argparse

def cmd_send(args):
    from .bot.bridge import get_bridge
    ok = get_bridge().send(args.to, args.text)
    print("[wechat] sent to %s %s" % (args.to, "ok" if ok else "failed"))
    return 0 if ok else 1

def cmd_rules(args):
    from ._app import app
    from .models import Rule
    with app.app_context():
        rows = Rule.query.order_by(Rule.id).all()
        if not rows:
            print("[wechat] no rules configured")
            return 0
        for r in rows:
            state = "on" if r.enabled else "off"
            print("[wechat] #%s %r -> %s %s" % (r.id, r.trigger, r.action, state))
    return 0

def cmd_serve(args):
    from ._app import app
    app.run(host=args.host, port=args.port, debug=False)
    return 0

def main(argv=None):
    p = argparse.ArgumentParser(prog="wechat", description="WeChat bot server CLI")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("send", help="send one message through the bridge")
    s.add_argument("to")
    s.add_argument("text")
    s.set_defaults(func=cmd_send)

    r = sub.add_parser("rules", help="list stored rules")
    r.set_defaults(func=cmd_rules)

    v = sub.add_parser("serve", help="run the dev server")
    v.add_argument("--host", default="127.0.0.1")
    v.add_argument("--port", type=int, default=8000)
    v.set_defaults(func=cmd_serve)

    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        return 1
    return args.func(args) or 0
