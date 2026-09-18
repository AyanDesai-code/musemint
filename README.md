# MuseMint — AI Art NFT Marketplace (MVP)

MuseMint is a planned marketplace where creators can turn AI-generated artwork into NFTs and collectors can discover and purchase them.

> **Status: planning / repository scaffold.** There is no runnable application, deployed marketplace, smart contract, or application test suite yet. Features below describe intended scope, not functionality available today.

## MVP scope

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
docs/repository-setup.md
CONTRIBUTING.md
README.md
```

- [Contributing](CONTRIBUTING.md): issue and pull request workflow.
- [Repository administration](docs/repository-setup.md): settings and branch protection limitations.
- [Report a bug](https://github.com/AyanDesai-code/musemint/issues/new?template=bug_report.md) or [propose a feature](https://github.com/AyanDesai-code/musemint/issues/new?template=feature_request.md).

## Continuous integration

[CI workflow](.github/workflows/ci.yml) runs on pull requests, pushes to `main`, and manual dispatch. Its **Repository checks** job:

1. Checks tracked Markdown files for empty content, a missing final newline, trailing whitespace, and broken relative file links.
2. Checks the latest commit for Git whitespace errors.

Run `python3 scripts/check_docs.py` and `git diff --check` locally before opening a PR. The link check covers inline relative file links; it does not validate heading anchors, reference-style links, or external URLs. Use explicit paragraphs rather than trailing spaces for line breaks.

CI has read-only repository permissions, cancels superseded runs on the same branch/PR, and requires no project secrets or third-party Python packages. It does **not** build an app, test smart contracts, or provide a security audit. Add stack-specific lint, test, and build jobs when code exists. Only require status checks in branch protection after their actual check names have run successfully; see [repository administration](docs/repository-setup.md).

## Contributing and roadmap

1. Resolve the stack, chain, provider, and storage decisions through issues.
2. Bootstrap the application and document reproducible local setup.
3. Implement the artwork-to-testnet-mint flow, then discovery and marketplace transactions.
4. Add automated tests, failure-path coverage, and security/policy review before any public launch.

Use short-lived branches and pull requests to `main`. Link the relevant issue, describe validation, and follow [CONTRIBUTING.md](CONTRIBUTING.md). This is a sequencing guide, not a delivery-date commitment.

## Safety and security

Never commit API keys, private keys, seed phrases, credentials, or private user data. Use test wallets and placeholder values in `.env.example` when configuration is introduced. Sanitize logs and screenshots; transaction hashes and wallet addresses can reveal activity.

Only mint artwork you have the rights to use. Review AI-provider terms, content moderation, metadata persistence, and smart-contract security before public launch. Report sensitive vulnerabilities privately to the repository owner, not in public issues or pull requests.

## License

No open-source license has been selected. Repository access does not grant redistribution rights. Resolve code and artwork licensing before distribution or launch.
