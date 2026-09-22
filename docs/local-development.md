# Local development

## Scope and prerequisites

Task 224 provides dependency-free Python tooling and a disposable PostgreSQL/EVM stack. It does not implement backend/frontend packages, database migrations, contracts, or select a testnet/pinning provider. Those follow in Tasks 222, 225, 229, and 232. No Node.js installation is required for the current tooling; pin the chosen supported Node runtime and commit lockfiles when those packages are introduced. Anvil is a standalone local JSON-RPC server, not the future contract build tool.

Use Python 3.12, Git, and Docker Engine or Desktop (Linux containers) with Compose v2.20+. Start Docker first and allow several GB for image pulls/data. Commands work from any directory when invoking the script by path; subprocesses run in the repository root. On Windows use `py -3.12` instead of `python3`.

## Commands

```sh
python3 scripts/dev.py setup   # create .env once; never overwrite
python3 scripts/dev.py doctor  # Git, Python, Compose and daemon availability
python3 scripts/dev.py check   # compile tooling, unit tests, docs, local diffs
python3 scripts/dev.py up      # start services, wait, smoke-test
python3 scripts/dev.py smoke   # repeat SQL/RPC checks against running services
python3 scripts/dev.py status
python3 scripts/dev.py down    # stop/remove containers; keep DB volume
```

`build` and `test` are separately available and used by CI. They are real tooling compilation/tests, not placeholder application builds. New Markdown must be staged to be checked. Hosted CI additionally checks the full PR/push diff; see [CI notes](ci.md).

## Services and configuration

See the [README environment table](../README.md#environment-variables-and-secrets) and [.env.example](../.env.example). Only PostgreSQL's local password is consumed from the environment today. No application dotenv loader exists yet. Future apps must explicitly load configuration and validate it at startup.

| Service | Host endpoint | Docker-network endpoint | Lifetime |
| --- | --- | --- | --- |
| PostgreSQL 16.10 | `127.0.0.1:5432`, DB/user `musemint` | `db:5432` | Named volume `musemint-dev_postgres-data` |
| Anvil v1.3.1 | `http://127.0.0.1:8545`, chain ID 31337 | `http://chain:8545` | In-memory; reset on container stop/restart |

Ports bind only to loopback. The Docker-internal chain listener uses `0.0.0.0` so port forwarding works; it must never be exposed publicly. Do not run a second stack with the same project name/ports. A backend running in Docker must use service DNS rather than localhost in its connection URLs.

Anvil provides disposable funded test accounts. Their keys are public and unsafe outside this chain. No key is needed for the smoke probe, which only calls `eth_chainId`. If testing with a wallet later, use a separate development profile and reset its local activity after chain resets. Do not send actual assets.

PostgreSQL readiness uses `pg_isready`; smoke uses `psql` inside the DB container to create a temporary table, insert/select one row and roll back. This validates the local service, not future backend authentication, migrations or business behavior. No persistent schema is installed.

## Data and troubleshooting

- **Docker missing/unavailable:** install/start Docker, rerun `doctor`. Repository `check` still works without it.
- **Image pull failure:** verify Docker Hub/GHCR access and the release tags in Compose; retry `up`. Never silently substitute `latest`.
- **Port already allocated:** stop the conflicting local service, or deliberately update Compose, example URLs, smoke probe and docs together. The runner intentionally targets only fixed local RPC, not an environment-supplied public endpoint.
- **Startup fails:** inspect `python3 scripts/dev.py status`, then `docker compose --env-file .env logs db chain` locally. Logs may include operational details; sanitize before sharing. `up` leaves containers available for diagnosis; use `down` when finished.
- **Changed DB password does not apply:** existing volumes retain initialized credentials. Change the role password with PostgreSQL tooling and update URLs, or reset disposable data. Do not reset a DB containing needed work.
- **Chain state disappears:** expected after stopping Anvil. Redeploy local contracts when they exist and clear dependent local records; no automatic synchronization exists yet.

`down` intentionally never deletes DB volumes. Only after explicitly deciding to discard all local DB data, run the following destructive reset yourself:

```sh
# DANGER: irreversibly deletes this Compose project's local PostgreSQL data.
docker compose --env-file .env down --volumes
python3 scripts/dev.py up
```

This is not a backup/restore solution or production deployment. Keep local `.env`, data, generated files, real credentials and wallet keys out of Git. Ordinary PR CI uses only the committed public local defaults; deployment secrets belong in separately approved protected environments.
