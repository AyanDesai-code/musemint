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
| Repository CI | Documentation checker tests, Markdown checks, and Git whitespace checks |
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
- Python 3.12 for the dependency-free repository checks (the CI version).

```sh
git clone https://github.com/AyanDesai-code/musemint.git
cd musemint
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
git diff --check
```

There are no application dependencies to install, environment variables to configure, or app build/run/test commands yet. Once a stack is selected, document its prerequisites, setup, `.env.example` placeholders, and exact commands here alongside its implementation. Do not add real credentials to examples.

## Repository guide

```text
.github/
  ISSUE_TEMPLATE/       Bug reports and feature proposals
  workflows/ci.yml     Repository CI skeleton
scripts/check_docs.py  Dependency-free documentation checks
tests/                Documentation checker regression tests
docs/repository-setup.md
docs/mvp-spec.md       Proposed MVP API, data model, and acceptance criteria
CONTRIBUTING.md
README.md
```

- [MVP specification](docs/mvp-spec.md): proposed features, endpoints, six-table data model, NFT metadata, and acceptance criteria.
- [Contributing](CONTRIBUTING.md): issue and pull request workflow.
- [Repository administration](docs/repository-setup.md): settings and branch protection limitations.
- [Report a bug](https://github.com/AyanDesai-code/musemint/issues/new?template=bug_report.md) or [propose a feature](https://github.com/AyanDesai-code/musemint/issues/new?template=feature_request.md).

## Continuous integration

[CI workflow](.github/workflows/ci.yml) runs on pull requests, pushes to `main`, and manual dispatch. Its **Repository checks** job:

1. Runs the documentation checker regression tests with Python’s standard-library `unittest`.
2. Checks tracked Markdown files for empty content, a missing final newline, trailing whitespace, and broken relative file links.
3. Checks Git whitespace errors across the full PR diff or push diff. Manual runs, initial pushes, and pushes whose previous commit is unavailable check the latest commit instead.

Run all three check commands from [Getting started](#getting-started) locally before opening a PR. `git diff --check` checks unstaged edits; also use `git diff --cached --check` for staged edits and `git diff --check origin/main...HEAD` for committed PR changes (after `git fetch origin`). Stage new Markdown files with `git add <path>` first: the checker only inspects files tracked by Git. The link check covers inline relative file links; it does not validate heading anchors, reference-style links, or external URLs. Use explicit paragraphs rather than trailing spaces for line breaks.

CI has read-only repository permissions, cancels superseded runs on the same branch/PR, and requires no project secrets or third-party Python packages. It does **not** build an app, test smart contracts, or provide a security audit. Add stack-specific lint, test, and build jobs when code exists. Only require status checks in branch protection after their actual check names have run successfully; see [repository administration](docs/repository-setup.md).

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
