# CI notes

## Current contract

The [CI workflow](../.github/workflows/ci.yml) runs on every pull request, pushes to `main`, and manual dispatch. The single job is named **Repository checks** and uses Ubuntu with Python 3.12. Run its tooling checks locally from the repository root:

```sh
python3 -m compileall -q scripts tests
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
git diff --check
```

Compilation checks Python syntax; it is not an application build or a distributable artifact. Unit tests cover the documentation checker, not marketplace functionality. There is currently no application package manifest, dependency lockfile, smart contract, deployment, or application build command. Do not add a successful no-op job that claims to build or test the application.

The Markdown checker uses only the Python standard library and inspects Git-tracked Markdown, including issue templates. Stage new documents before running it. It checks nonempty content, final newlines, trailing whitespace, and simple inline relative file links. It does not validate remote URLs, heading anchors, reference links, or full Markdown syntax.

## Diff checks

| Event | Whitespace comparison |
| --- | --- |
| Pull request | Merge-base diff between the event's base and head commits |
| Push to `main` | Previous push SHA to checked-out HEAD |
| Manual dispatch, initial push, or unavailable previous SHA | Latest commit only |

Checkout fetches full history for these comparisons. Locally, use `git diff --cached --check` for staged edits. After fetching the remote, use `git diff --check origin/main...HEAD` for committed PR changes. An empty working-tree diff alone does not validate committed changes.

## Security and operation

- Workflow token permissions are read-only (`contents: read`), and checkout does not persist credentials.
- Actions are pinned to full commit SHAs with release comments. Review and update both together when upgrading.
- No project secrets, wallets, RPC endpoints, or external AI services are needed for repository checks.
- Keep checks on `pull_request`; do not switch to `pull_request_target` to execute untrusted PR code with privileged credentials.
- Superseded runs for the same PR/ref are cancelled; the job has a five-minute timeout.
- There are no deployment steps, caches, or artifact uploads in this scaffold.

If no run appears, a maintainer should check repository Actions settings and any fork-run approval requirement. If a run fails, inspect the failed step and reproduce its command using Python 3.12. Do not post unsanitized logs in an issue.

## Application build/test extension checklist

Implement the following in the same PR that introduces the application stack:

1. Commit the package manifest and lockfile; pin a supported runtime in both local setup and CI.
2. Document exact install, lint, test, and production-build commands in [README](../README.md). Use the package manager's frozen/locked installation mode.
3. Add a separate job named **Application checks** with checkout, runtime setup, dependency installation, lint, tests, and build in that order. Keep the existing repository job.
4. Ensure failing tests or builds fail the job. Do not use `continue-on-error`, `|| true`, or success-only placeholder commands to simulate readiness.
5. Use deterministic fixtures and mocked AI/storage/RPC services for PR tests. Use test wallets and a local chain for contract tests; isolate any live testnet integration checks from untrusted PR code.
6. Add caches only once the runtime and lockfile are known. Key dependency caches by platform/runtime and lockfile; never cache credentials.
7. Upload build artifacts only when consumers need them, with a retention limit and no secrets or private user data. Keep deployment separate and subject to environment approval.
8. Exercise a successful hosted run and a failing-test case before requiring the new check. Update these notes and the issue templates if additional diagnostics are needed.

Application stack selection is intentionally unresolved; this checklist is an integration contract, not runnable application CI.

## Required checks and verification

Use the exact check names GitHub reports after a successful hosted run. Do not require an unimplemented **Application checks** job. Branch protection is currently documented as unavailable under the repository owner's plan; see [repository administration](repository-setup.md). CI configuration alone does not enforce merge protection.

Local validation does not prove that hosted runners, Actions policy, billing, or branch protection are configured. Verify the [Actions page](https://github.com/AyanDesai-code/musemint/actions/workflows/ci.yml) after syncing a workflow change. This workflow does not certify contract security, content rights, or production readiness.
