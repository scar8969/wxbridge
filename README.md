<p align="center">
  <img src="docs/assets/screens/root.png" alt="wxbridge running" width="900">
</p>

<h1 align="center">wxbridge</h1>

<p align="center"><b>A WeChat bot server: webhook in, rules out, groups under control.</b></p>

<p align="center">
  <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-25%20passed-2ea44f" alt="tests: 25 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-69.0%-yellow" alt="coverage: 69.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20answered-0969da" alt="routes: 10 answered"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

wxbridge sends WeChat messages through a bridge, matches incoming text against ordered rules, replies with the first match and keeps a searchable message log. Group muting and rule editing are available over HTTP and from the CLI.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Bot logic written inline in a handler is untestable and invisible. Separating the transport (a bridge that owns the account) from the policy (ordered rules with trigger patterns and replies) means a rule change is a row in a table, and a rule can be tested against a string without a phone.

## What it does

| Capability | How it works |
| --- | --- |
| **Rule engine** | Ordered triggers — exact, `prefix*` or `re:regex` — with replies; the first enabled match answers. |
| **Message bridge** | POST /api/webhook sends through the bridge and reports whether the send succeeded. |
| **Message log** | Every inbound and outbound message is stored, so a rule can be debugged against real traffic. |
| **Group administration** | POST /api/groups/<id>/mute toggles a group without editing configuration files. |

## Quickstart

```sh
git clone https://github.com/scar8969/wxbridge.git
cd wxbridge
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

The same work from the CLI:

```sh
python -m wechat_server.cli --help
```

Commands: `send`, `rules`, `serve`.

A first request:

```sh
curl -s http://127.0.0.1:8000/api/messages | head
```

## Requirements

- Python **3.11+** — CI runs 3.11, 3.12 and 3.13.
- Runtime dependencies: `Flask>=3.0`, `Flask-SQLAlchemy>=3.1`, `SQLAlchemy>=2.0`, `PyYAML>=6.0`, `itchat`.
- No JavaScript build step: every page is server-rendered Jinja.

## API

Every route below is in [`openapi/wxbridge.yaml`](openapi/wxbridge.yaml) and is exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/webhook` | send message |
| `GET` | `/api/messages` | list |
| `GET` | `/api/rules` | list rules |
| `POST` | `/api/groups/<id>/mute` | mute |

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/rules.png" alt="/rules" width="100%"><br><sub><code>/rules</code> &middot; 28.7 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/healthz.png" alt="/healthz" width="100%"><br><sub><code>/healthz</code> &middot; 8.4 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/livez.png" alt="/livez" width="100%"><br><sub><code>/livez</code> &middot; 7.3 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/metrics.png" alt="/metrics" width="100%"><br><sub><code>/metrics</code> &middot; 14.8 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/readyz.png" alt="/readyz" width="100%"><br><sub><code>/readyz</code> &middot; 7.7 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/version.png" alt="/version" width="100%"><br><sub><code>/version</code> &middot; 26.3 KB</sub></td>
</tr>
</table>

## Measured, not estimated

These numbers were produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **25 / 25 passed** (2.5 s, exit 0) |
| Line coverage | **69.0%** — 457 of 630 statements |
| Source | 15 files / 1,448 lines |
| Test code | 4 files / 238 lines |
| Documented paths | 4 in the spec, 2 GET |
| Live probe | 10 GET requests to the booted app, **10 answered 200** |
| Median latency | **16.0 ms** (single uncached request, dev server) |
| Slowest / fastest | 100.7 ms `/` / 2.8 ms `/readyz` |
| Bytes served | 11.8 KB across 10 responses |
| Screenshots | 7 captured |

## Architecture

```
wxbridge/
├── src/wechat_server/
│   ├── http.py                         379  HTTP plumbing for wechat_server: correlation ids, ac
│   ├── _app.py                         182  Web app for the WeChat bot server
│   ├── config.py                       171  Environment-driven configuration for wechat_server
│   ├── observability.py                169  Structured logging and request correlation for wecha
│   ├── app.py                          119  Application factory for wechat_server
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── bot/api.py                       67  
│   ├── cli.py                           63  Command line for the WeChat bot server
│   ├── bot/bridge.py                    53  In-process stand-in for an itchat client
│   ├── paths.py                         52  Filesystem layout for wechat_server
│   ├── bot/handlers.py                  38  
│   ├── models.py                        33  
├── openapi/wxbridge.yaml                  the contract of record
├── schema/wxbridge.sql                    the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `bot/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor set in `pyproject.toml` from the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 for every push to `main`, plus a container build. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deploy

```sh
docker build -t wxbridge .
docker run --rm -p 8000:8000 --env-file .env.example wxbridge
```

Configuration is environment-only — every variable is documented in [`.env.example`](.env.example), and the service refuses to start with a production secret missing.

## Limits, stated rather than hidden

- The bridge owns the account session; this service does not implement WeChat's own callback signature check.
- Replies are text-only.

## License

MIT — see [LICENSE](LICENSE).
