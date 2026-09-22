# MuseMint — AI Art NFT Marketplace (MVP)

[![CI](https://github.com/AyanDesai-code/musemint/actions/workflows/ci.yml/badge.svg)](https://github.com/AyanDesai-code/musemint/actions/workflows/ci.yml)

MuseMint is a planned marketplace where creators can turn AI-generated artwork into NFTs and collectors can discover and purchase them.

> **Status: planning / repository scaffold.** There is no runnable application, deployed marketplace, smart contract, or application test suite yet. Features below describe intended scope, not functionality available today.

## Contents

- [MVP scope](#mvp-scope)
- [Getting started](#getting-started)
- [Repository guide](#repository-guide)
- [Continuous integration](#continuous-integration)
- [Contributing and roadmap](#contributing-and-roadmap)
- [Safety and security](#safety-and-security)
- [License](#license)

## MVP scope

### Available today

| Deliverable | Current state |
| --- | --- |
| Project documentation | Setup, contribution workflow, scope, and open decisions |
| Repository CI | Python compilation, documentation checker tests, Markdown and whitespace checks |
| Issue intake | Bug report and feature request templates; blank issues disabled |
| Marketplace application | Not implemented; no deployment or supported wallet/network yet |

### Planned user flows

- Create or upload AI-generated artwork and preview it before minting.
- Connect a wallet and mint artwork with associated metadata.
- Browse artwork and view creator, provenance, ownership, and listing details.
- List and purchase NFTs, with clear transaction status and errors.

Implementation proposals should include acceptance criteria and be tracked in [GitHub Issues](https://github.com/AyanDesai-code/musemint/issues).

### Decisions still required

| Area | Open decisions |
| --- | --- |
| Application | Frontend/backend stack, authentication, and hosting |
| Blockchain | Chain, testnet, wallet integration, token standard, and marketplace contracts |
| AI generation | Provider, cost controls, usage terms, and moderation |
| Storage | Artwork and metadata persistence, availability, and privacy |
| Marketplace policy | Fees, creator rights, licensing, and prohibited content |

Start with a testnet and test wallets. Do not use real funds during MVP development. Production deployment, security review, and legal/policy decisions are not part of this repository scaffold.

## Getting started

### Prerequisites

- Git and access to this private repository through an authorized GitHub account.
- Python 3.12 for the dependency-free repository tooling (the CI version).
- For local services: Docker Engine/Desktop with Compose v2.20+ and a running daemon.
- Ports 5432 and 8545 available on localhost. Docker is not needed for tooling checks.

```sh
git clone https://github.com/AyanDesai-code/musemint.git
cd musemint
python3 scripts/dev.py check
# Optional local DB + EVM (no application server exists yet):
python3 scripts/dev.py setup
python3 scripts/dev.py doctor
python3 scripts/dev.py up
python3 scripts/dev.py status
python3 scripts/dev.py down
```

`up` starts PostgreSQL 16.10 and Anvil v1.3.1, waits for readiness, then checks SQL read/write and EVM chain ID 31337. `down` preserves database data; the chain is ephemeral. These local infrastructure choices do not select the production network or replace Task 225's Hardhat project. There are still no application dependencies, migrations, contract packages, or application build/run commands. `dev.py build` compiles Python tooling only; `dev.py test` runs its regression tests.

### Environment variables and secrets

`setup` copies [.env.example](.env.example) to ignored `.env` without overwriting an existing file. Current tooling checks need no configuration or secrets. Compose reads `.env` explicitly; shell variables override its values.

| Variable | Local value / purpose | Consumer |
| --- | --- | --- |
| `POSTGRES_PASSWORD` | `musemint_local_only` — public disposable password, never for shared/production DBs | Compose DB initialization |
| `DATABASE_URL` | `postgresql://musemint:musemint_local_only@127.0.0.1:5432/musemint` | Reserved for future host backend/ORM; not consumed yet |
| `RPC_URL` | `http://127.0.0.1:8545` | Reserved for future host backend/contracts; smoke check uses this fixed local address |
| `CHAIN_ID` | `31337` | Reserved for future apps; local chain and smoke check enforce 31337 |

The local stack fixes DB name/user to `musemint` and ports to 5432/8545. If changing the password, also update the future `DATABASE_URL` (URL-encode special characters). PostgreSQL initialization variables only apply to an empty volume. See [local development](docs/local-development.md) for service lifecycle, troubleshooting, and safe reset guidance.

No IPFS provider, public RPC, JWT signing, deployer, or error-tracking secrets are required yet. Add their exact names with the implementing packages; never invent working credentials. Keep backend tokens in ignored local files or deployment secret stores, never browser environment variables. Future live integration/deployment workflows must use protected GitHub environments, not PR secrets. Anvil accounts are publicly known test accounts: never fund them on public chains or import a real wallet.

## Repository guide

```text
.github/
  ISSUE_TEMPLATE/       Bug reports and feature proposals
  workflows/ci.yml     Tooling checks and local-service smoke CI
scripts/dev.py         Shared setup/build/test/service commands
compose.yaml           Loopback-only PostgreSQL and local EVM
.env.example           Disposable local configuration
scripts/check_docs.py  Dependency-free documentation checks
tests/                Documentation checker regression tests
docs/repository-setup.md
docs/ci.md            CI behavior and application build/test extension checklist
docs/mvp-spec.md       Proposed MVP API, data model, and acceptance criteria
CONTRIBUTING.md
README.md
```

- [MVP specification](docs/mvp-spec.md): proposed features, endpoints, six-table data model, NFT metadata, and acceptance criteria.
- [Contributing](CONTRIBUTING.md): issue and pull request workflow.
- [CI notes](docs/ci.md): check behavior, security, and the application build/test extension checklist.
- [Repository administration](docs/repository-setup.md): settings and branch protection limitations.
- [Report a bug](https://github.com/AyanDesai-code/musemint/issues/new?template=bug_report.md) or [propose a feature](https://github.com/AyanDesai-code/musemint/issues/new?template=feature_request.md).

## Continuous integration

[CI workflow](.github/workflows/ci.yml) runs on pull requests, pushes to `main`, and manual dispatch. Its **Repository checks** job:

1. Compiles repository Python tooling to check syntax (not an application build).
2. Runs the repository tooling regression tests with Python’s standard-library `unittest`.
3. Checks tracked Markdown files for empty content, a missing final newline, trailing whitespace, and broken relative file links.
4. Checks Git whitespace errors across the full PR diff or push diff. Manual runs, initial pushes, and pushes whose previous commit is unavailable check the latest commit instead.

Run `python3 scripts/dev.py check` locally before opening a PR. The separate **Local services smoke** job starts the same Compose stack and verifies SQL read/write and chain ID without external secrets. `git diff --check` checks unstaged edits; also use `git diff --cached --check` for staged edits and `git diff --check origin/main...HEAD` for committed PR changes (after `git fetch origin`). Stage new Markdown files with `git add <path>` first: the checker only inspects files tracked by Git. The link check covers inline relative file links; it does not validate heading anchors, reference-style links, or external URLs. Use explicit paragraphs rather than trailing spaces for line breaks.

CI has read-only repository permissions, cancels superseded runs on the same branch/PR, and requires no project secrets or third-party Python packages. It does **not** build an app, test smart contracts, or provide a security audit. Add stack-specific lint, test, and build jobs when code exists using the [CI extension checklist](docs/ci.md#application-buildtest-extension-checklist). Only require status checks in branch protection after their actual check names have run successfully; see [repository administration](docs/repository-setup.md).

### Troubleshooting checks

- **Clone returns “Repository not found”:** confirm your GitHub account has access and authenticate using your usual Git/GitHub CLI setup. Never put access tokens in repository files or clone URLs shared in issues.
- **`python3` is unavailable:** install Python 3.12; on Windows, use `py -3.12` in place of `python3` if using the Python launcher.
- **Documentation check fails:** use the reported file and line to remove trailing whitespace, add a final newline, or correct a relative link. Link paths are relative to the Markdown file containing them and are case-sensitive in Linux CI.
- **A new Markdown file is not checked:** stage it with Git and rerun the check.
- **Hosted CI fails:** open the [Actions workflow](https://github.com/AyanDesai-code/musemint/actions/workflows/ci.yml), inspect the failing step, and reproduce its command locally from the repository root. Maintainers can use **Run workflow** for a manual check when Actions is enabled.

## Contributing and roadmap

1. Resolve the stack, chain, provider, and storage decisions through issues.
2. Bootstrap the application and document reproducible local setup.
3. Implement the artwork-to-testnet-mint flow, then discovery and marketplace transactions.
4. Add automated tests, failure-path coverage, and security/policy review before any public launch.

### Reporting bugs and proposing work

Use the [bug report](https://github.com/AyanDesai-code/musemint/issues/new?template=bug_report.md) for reproducible documentation, CI, or implementation defects, and the [feature request](https://github.com/AyanDesai-code/musemint/issues/new?template=feature_request.md) for proposals and MVP tasks. Search existing issues first. Include reproduction steps and expected behavior for bugs, or scope, acceptance criteria, and a validation plan for features. Maintainers triage priority and dependencies; submitting a proposal does not make a technology choice an approved decision.

Use short-lived branches and pull requests to `main`. Link the relevant issue, describe validation, and follow [CONTRIBUTING.md](CONTRIBUTING.md). This is a sequencing guide, not a delivery-date commitment.

## Safety and security

Never commit API keys, private keys, seed phrases, credentials, or private user data. Use test wallets and placeholder values in `.env.example` when configuration is introduced. Sanitize logs and screenshots; transaction hashes and wallet addresses can reveal activity.

Only mint artwork you have the rights to use. Review AI-provider terms, content moderation, metadata persistence, and smart-contract security before public launch. Report sensitive vulnerabilities privately to the repository owner, not in public issues or pull requests.

## License

No open-source license has been selected. Repository access does not grant redistribution rights. Resolve code and artwork licensing before distribution or launch.
