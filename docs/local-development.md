# Local development

## Scope and prerequisites

Task 224 provides dependency-free Python tooling and a disposable PostgreSQL/EVM stack. It does not implement backend/frontend packages, database migrations, contracts, or select a testnet/pinning provider. Those follow in Tasks 222, 225, 229, and 232. No Node.js installation is required for the current tooling; pin the chosen supported Node runtime and commit lockfiles when those packages are introduced. Anvil is a standalone local JSON-RPC server, not the future contract build tool.

Use Python 3.12, Git, and Docker Engine or Desktop (Linux containers) with Compose v2.20+. Start Docker first and allow several GB for image pulls/data. Commands work from any directory when invoking the script by path; subprocesses run in the repository root. On Windows use `py -3.12` instead of `python3`.

## First-time setup

Clone with an authorized GitHub account, then run commands from the repository root:

```sh
git clone https://github.com/AyanDesai-code/musemint.git
cd musemint
python3 scripts/dev.py check
python3 scripts/dev.py setup
```

`check` needs only Python and Git: no `.env`, Docker, package installation, or provider credentials. It should report passing unit tests and documentation checks and exit successfully. There is no `npm install`, migration, frontend URL, or backend server to start at this stage.

`setup` creates `.env` from the committed example with owner-only permissions (`0600` on POSIX). If `.env` exists it is left unchanged, including its permissions; compare it with `.env.example` manually after pulling updates. Do not overwrite local settings or share the file. On Windows, use filesystem access controls appropriate to your account.

For the optional local services, review `.env`, start Docker, then run:

```sh
python3 scripts/dev.py doctor
docker compose --env-file .env -f compose.yaml config --quiet
python3 scripts/dev.py up
python3 scripts/dev.py status
```

`config --quiet` validates Compose interpolation without printing resolved credentials. `up` waits for PostgreSQL health and probes both services; success ends with `PostgreSQL read/write and local EVM chain ID checks passed.` Status should show a healthy `db` and running `chain` (Anvil has no Compose healthcheck). This does not validate any future application. Stop services with `python3 scripts/dev.py down` when finished.

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

### Environment variable reference

This inventory is based on [.env.example](../.env.example), [compose.yaml](../compose.yaml), [the dev runner](../scripts/dev.py), and [CI](../.github/workflows/ci.yml), not the proposed application specification. Values below are public, disposable local defaults, not production credentials.

| Variable | Example value | Required now? / consumer |
| --- | --- | --- |
| `POSTGRES_PASSWORD` | `musemint_local_only` | Required and nonempty for Compose commands; passed to PostgreSQL for initial database creation. Not needed for tooling checks. |
| `DATABASE_URL` | `postgresql://musemint:musemint_local_only@127.0.0.1:5432/musemint` | No; reserved for a future host-based backend/ORM. No current reader. |
| `RPC_URL` | `http://127.0.0.1:8545` | No; reserved for future app/contract tooling. The smoke probe hardcodes this address. |
| `CHAIN_ID` | `31337` | No; reserved for future apps. Compose and the smoke probe hardcode 31337 (`0x7a69` in JSON-RPC). |

Configuration loading and constraints:

- The runner requires a root `.env` file for every service command and invokes `docker compose --env-file .env -f compose.yaml` from the repository root. It does not load dotenv into Python or export the file into your shell; do not `source` it as part of setup.
- Exported shell variables take precedence over the env file for Compose interpolation. If your local password differs unexpectedly, check for an inherited `POSTGRES_PASSWORD` override without printing it into shared logs. Unset unintended overrides before retrying. Compose rejects an empty or missing password.
- Only the password is interpolated from this file today. `POSTGRES_USER=musemint` and `POSTGRES_DB=musemint` are fixed container settings in Compose, not supported `.env` overrides. Ports and Anvil chain ID are also fixed; editing `RPC_URL` or `CHAIN_ID` alone changes nothing in the running stack or smoke test.
- If changing the password, keep the reserved `DATABASE_URL` consistent and percent-encode special characters in its password component. Existing DB volumes keep the old initialized password; see troubleshooting below. Compose env-file quoting/interpolation also applies (notably to `$`); use a simple disposable local value unless you understand those rules.
- `.env` is ignored; `.env.example` is tracked. Confirm with `git check-ignore .env` and never force-add it. Do not print resolved Compose configuration or unsanitized connection URLs into issues.
- No application dotenv loader exists yet. Future apps must explicitly load and validate configuration at startup. There are no implemented IPFS, JWT, wallet signing, public RPC, analytics, or Sentry variables; add exact names and consumers when implementing those features. Never put backend secrets in browser-exposed variables.
- CI creates the same disposable `.env` via `setup`. Neither current CI job requires GitHub project secrets; it does not deploy anything.

### Service endpoints

| Service | Host endpoint | Docker-network endpoint | Lifetime |
| --- | --- | --- | --- |
| PostgreSQL 16.10 | `127.0.0.1:5432`, DB/user `musemint` | `db:5432` | Named volume `musemint-dev_postgres-data` |
| Anvil v1.3.1 | `http://127.0.0.1:8545`, chain ID 31337 | `http://chain:8545` | In-memory; reset on container stop/restart |

Ports bind only to loopback. The Docker-internal chain listener uses `0.0.0.0` so port forwarding works; it must never be exposed publicly. Do not run a second stack with the same project name/ports. A backend running in Docker must use service DNS rather than localhost in its connection URLs.

Anvil provides disposable funded test accounts. Their keys are public and unsafe outside this chain. No key is needed for the smoke probe, which only calls `eth_chainId`. If testing with a wallet later, use a separate development profile and reset its local activity after chain resets. Do not send actual assets.

PostgreSQL readiness uses `pg_isready`; smoke uses `psql` inside the DB container to create a temporary table, insert/select one row and roll back. This validates the local service, not future backend authentication, migrations or business behavior. No persistent schema is installed.

## Data and troubleshooting

- **Missing `.env` / required password error:** run `setup`, ensure `POSTGRES_PASSWORD` is nonempty, and remove unintended shell overrides. `setup` never repairs an existing file automatically.
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
