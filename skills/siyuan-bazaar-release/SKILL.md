---
name: siyuan-bazaar-release
description: "Use when publishing or updating a SiYuan community plugin through GitHub Releases and the SiYuan Bazaar index, including first-time onboarding, later version releases, package.zip validation, local workspace deployment, and post-release verification."
---

# SiYuan Bazaar Release

Use this skill for a real SiYuan plugin release. Treat the plugin repository, its build scripts, the GitHub Release, and the Bazaar index as separate release surfaces.

## Start With Context

1. Read `git status --short --branch`, applicable `AGENTS.md`, recent release commits, `package.json`, `plugin.json`, the build/package scripts, and the release workflow.
2. Preserve unrelated dirty work. If the release commit is specified, build from that exact commit in a clean temporary worktree when the current worktree is dirty.
3. Inspect the current `siyuan-note/bazaar` repository before editing it. Determine whether the index is `plugins.txt`, `plugins.json`, or another file in the current revision; do not copy an older template blindly.
4. Confirm the repository owner/name, default branch, tag convention, release asset name, and required manifest fields from the live repository and official Bazaar checks.

## Release Branches

Choose exactly one path:

- **First-time Bazaar onboarding**: the repository is not in the current Bazaar index. Prepare and submit a Bazaar PR that adds exactly this one repository, then wait for the package check and merge/deployment status.
- **Subsequent plugin release**: the repository is already indexed. Build and publish the new GitHub Release with the plugin version as the tag; do not open a duplicate Bazaar PR.
- **Local update only**: when the user asks for immediate local availability, deploy the validated build into the requested SiYuan workspace and report the reload step. This does not replace the public GitHub Release.

If the version, release path, target workspace, or permission to push is missing, stop before mutation and ask for it.

## Build And Package Gate

1. Keep the version in `package.json` and `plugin.json` synchronized unless the repository documents a different source of truth. Check any fallback/runtime version constants too.
2. Run the repository's narrow tests, smoke checks, production build, and package validator. The final `package.zip` must come from the same clean commit as the tag.
3. Inspect the archive, not only the source tree. At minimum verify `plugin.json`, the compiled entry files, `icon.png`, `preview.png` when required, `README.md`, `LICENSE`, and any repository-specific assets.
4. Parse the packaged `plugin.json` and compare it with the source manifest: `name`, repository `url`, `version`, and display metadata must match. Check the Bazaar size and required-file constraints reported by its current PR checks.
5. Record the package SHA-256 and the commit SHA before publishing.

## GitHub Release

1. Create the release tag using the repository's existing convention (`vX.Y.Z` or `X.Y.Z`). Point it at the validated commit.
2. Publish a non-draft, non-prerelease GitHub Release with `package.zip` attached. Use the repository changelog as the release body; do not rely on a stale generated note.
3. Verify the remote tag resolves to the intended commit and `gh release view` shows the expected asset name, size, and digest.

Never overwrite an existing tag or release until the user explicitly authorizes replacement and the target commit/assets are rechecked.

## Bazaar Onboarding

For the first release only:

1. Fork or branch `siyuan-note/bazaar` according to the current contribution instructions.
2. Add one plugin repository to the current index file, preserving ordering and formatting. Keep one package addition per PR.
3. Open the PR with the plugin repository and release URL. Do not claim Bazaar availability until the automated package check passes and the PR is merged/deployed.
4. If the check fails, fix the plugin repository's release, manifest, or assets and update the same PR; do not open a replacement PR.

For later releases, monitor the Bazaar check/deployment job after publishing. Bazaar refresh can be scheduled, so distinguish `release uploaded` from `marketplace index deployed`.

## Local SiYuan Deployment

When requested, use the repository-native deploy command or script. Validate the source build first, deploy atomically if the script supports it, then read the installed `plugin.json` and compare the installed compiled-entry hash with the clean build. Report the absolute workspace path and tell the user to reload SiYuan.

## Stop Conditions

Stop before publishing when any of these is true:

- the package manifest and source manifest disagree;
- the package is built from a different commit than the proposed tag;
- required release assets are absent, oversized, or stale;
- the Bazaar index format or onboarding status cannot be determined;
- an existing tag/release points at a different commit;
- unrelated dirty changes make the release boundary ambiguous;
- GitHub authentication or required permissions are unavailable.

## Completion Gate

The task is complete only when the requested public release or onboarding action is verified, the package digest and commit are recorded, local deployment (if requested) is confirmed, and any Bazaar PR/check/deployment state is reported separately from the GitHub Release state.

## Official References

- SiYuan plugin sample release and first-time Bazaar instructions: https://github.com/siyuan-note/plugin-sample/blob/main/README_zh_CN.md
- SiYuan community Bazaar repository and checks: https://github.com/siyuan-note/bazaar
