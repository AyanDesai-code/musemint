# Contributing

## Issues

Use the bug report or feature request template in the GitHub issue tracker. Search existing issues first. Include acceptance criteria for implementation work; label and prioritize issues during triage. Keep credentials, seed phrases, private user information, and exploitable vulnerability details out of issues. Report sensitive security concerns directly to the repository owner through a private channel.

## Pull requests

1. Branch from current `main` using `feat/<short-name>`, `fix/<short-name>`, or `docs/<short-name>`.
2. Make focused changes with descriptive commits.
3. Open a pull request against `main`, linking the issue (for example, `Closes #123`).
4. Explain the change, validation performed, risks, and any documentation updates. If tests do not exist yet, state that explicitly and describe manual checks.
5. Request review, address feedback, and squash merge. Delete the source branch after merge.

Do not commit generated dependencies, build outputs, secrets, or wallet keys. Use testnets and test wallets during development.

## CI readiness

When the stack is selected, add GitHub Actions workflows for pull requests and pushes to `main`, with least-privilege permissions. Document local lint, test, and build commands in README. Once checks have run successfully, configure their actual names as required status checks. Do not configure nonexistent check names: they can block all merges.

The intended branch policy and its current enforcement limitation are documented in [repository setup](docs/repository-setup.md).
