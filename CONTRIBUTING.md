# Contributing

## Issues

Use the bug report or feature request template in the GitHub issue tracker. Search existing issues first. Include acceptance criteria for implementation work; label and prioritize issues during triage. Keep credentials, seed phrases, private user information, and exploitable vulnerability details out of issues. Report sensitive security concerns directly to the repository owner through a private channel.

## Pull requests

1. Branch from current `main` using `feat/<short-name>`, `fix/<short-name>`, or `docs/<short-name>`.
2. Make focused changes with descriptive commits.
3. Open a pull request against `main`, linking the issue (for example, `Closes #123`).
4. Explain the change, validation performed, risks, and any documentation updates. Run `python3 -m unittest discover -s tests -v`, `python3 scripts/check_docs.py`, and `git diff --check` locally from the repository root. Application tests do not exist yet; describe any additional manual checks. Stage new Markdown files before running the documentation check so they are included.
5. Request review, address feedback, and squash merge. Delete the source branch after merge.

Do not commit generated dependencies, build outputs, secrets, or wallet keys. Use testnets and test wallets during development.

## CI readiness

The [CI workflow](.github/workflows/ci.yml) runs the **Repository checks** job for pull requests, pushes to `main`, and manual dispatch, with read-only permissions and no project secrets. It runs documentation checker regression tests and checks Markdown hygiene, relative file links, and commit whitespace; it is not an application test suite.

When the stack is selected, extend CI with application lint, test, and build jobs and document the corresponding local commands in README. Once checks have run successfully, configure their actual names as required status checks. Do not configure nonexistent check names: they can block all merges.

The intended branch policy and its current enforcement limitation are documented in [repository setup](docs/repository-setup.md).
