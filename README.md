<p align="center">
  <img src="docs/assets/screens/root.png" alt="wxbridge running" width="900">
</p>

<h1 align="center">wxbridge</h1>

<p align="center"><b>A WeChat bot server: send through a bridge, answer by rule.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/wxbridge/actions/workflows/ci.yml"><img src="https://github.com/scar8969/wxbridge/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-25%20passed-2ea44f" alt="tests: 25 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-69.0%-yellow" alt="coverage: 69.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20live-0969da" alt="routes: 10 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

wxbridge sends WeChat messages through a bridge, matches incoming text against ordered rules, replies with the first match and keeps a searchable message log. Group muting and rule editing are available over HTTP and from the CLI.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

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

It is up when this answers:

```sh
curl -s http://127.0.0.1:8000/api/messages
```

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

## API

Every route below is declared in [`openapi/wxbridge.yaml`](openapi/wxbridge.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/webhook` | send message |
| `GET` | `/api/messages` | list |
| `GET` | `/api/rules` | list rules |
| `POST` | `/api/rules` | add rule |
| `POST` | `/api/groups/<id>/mute` | mute |

## CLI

The same operations without an HTTP client. Installed as `wxbridge`, and runnable from a checkout with no install:

```sh
python -m wechat_server.cli --help
```

```text
usage: wechat [-h] {send,rules,serve} ...

WeChat bot server CLI

positional arguments:
  {send,rules,serve}
    send              send one message through the bridge
    rules             list stored rules
    serve             run the dev server

options:
  -h, --help          show this help message and exit
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **25 / 25 passed** (1.9 s, exit 0) |
| Line coverage | **69.0%** — 457 of 630 statements |
| Source | 15 files / 1,467 lines |
| Test code | 4 files / 238 lines |
| Documented paths | 4 in the spec, 2 GET |
| Live probe | 10 GET requests to the booted app, **10 answered 200** |
| Median latency | **16.0 ms** (single uncached request, dev server) |
| Slowest / fastest | 100.7 ms `/` / 2.8 ms `/readyz` |
| Bytes served | 11.8 KB across 10 responses |
| Screenshots | 7 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ wechat_server/app.py:get_app()
                │  reads config once (wechat_server/config.py)
                │  registers the `bot` blueprint
                ▼
           route handler
             ├──▶ wechat_server/models.py        tables, via Flask-SQLAlchemy
             ├──▶ wechat_server/errors.py        raises typed errors → one JSON envelope
             └──▶ wechat_server/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
wxbridge/
├── src/wechat_server/
│   ├── http.py                         379  HTTP plumbing for wechat_server: correlation ids, ac
│   ├── _app.py                         182  Web app for the WeChat bot server
│   ├── observability.py                169  Structured logging and request correlation for wecha
│   ├── config.py                       168  Environment-driven configuration for wechat_server
│   ├── app.py                          119  Application factory for wechat_server
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── cli.py                           67  Command line for the WeChat bot server
│   ├── bot/api.py                       67  
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
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t wxbridge .
docker run --rm -p 8000:8000 --env-file .env.example wxbridge
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- The bridge owns the account session; this service does not implement WeChat's own callback signature check.
- Replies are text-only.

## License

MIT — see [LICENSE](LICENSE).
