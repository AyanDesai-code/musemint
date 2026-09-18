# Repository administration

Repository: https://github.com/AyanDesai-code/musemint

## Baseline settings

- Private visibility; do not make public without owner approval.
- Default branch: `main`.
- GitHub Issues enabled, with bug and feature templates.
- Wiki and GitHub Projects disabled; keep documentation in Git and track work in Issues.
- Squash merging enabled; merge commits and rebase merging disabled.
- Automatically delete merged branches; allow updating PR branches.

## Branch protection — blocked by GitHub plan

GitHub returned HTTP 403: "Upgrade to GitHub Pro or make this repository public to enable this feature." Protection is therefore **not enforced**. Follow the PR workflow voluntarily until the owner enables a supported plan. Do not treat these instructions as active protection.

After upgrading the owner account to GitHub Pro (or explicitly approving public visibility), apply protection to `main` in Settings > Branches:

- Require a pull request with at least one approving review.
- Dismiss stale approvals after new commits.
- Require conversation resolution and linear history.
- Apply to administrators as well.
- Disallow force pushes and branch deletion.
- The `CI` workflow defines a `Repository checks` job. Require its exact reported check name only after a successful hosted run.

At least one reviewer other than the PR author is needed for the approval policy. Ensure a collaborator is available before enabling it.

Equivalent REST request: `PUT /repos/AyanDesai-code/musemint/branches/main/protection`

```json
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
```

Verify the resulting policy using `GET /repos/AyanDesai-code/musemint/branches/main/protection`. After the [CI workflow](../.github/workflows/ci.yml) has run successfully, configure the exact successful check names and require the branch to be up to date before merging.
