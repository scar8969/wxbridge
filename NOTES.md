== curl ==
# POST /api/webhook  {"to":"alice","text":"hello"}
# GET  /api/messages?contact=alice
# POST /api/rules  {"trigger":"!price","action":"api","params":{"url":"https://…","template":"BTC: {price}"}}
# GET  /api/rules
# POST /api/groups/1/mute  {"member":"bob","minutes":60}
# CLI: wechat send alice "hello"

== session plan ==
# Session 1: bridge (mock) + router (exact/prefix/regex) → tests
# Session 2: groups (welcome/mute/kick) + api → tests
# Session 3: web templates + cli → screenshots → README → CI/Docker/Pages → tag
