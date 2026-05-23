# Zigux third-party archives

This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI
can validate locally before it falls back to network downloads.

## Current pinned Zig archive contract

- target: `x86_64-linux`
- channel: `0.17.0-dev.87+9b177a7d2`
- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`
- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`
- size: `58159088` bytes

## Validation

- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`

## Bootstrap order

- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.
- Before retrying the direct-download or community-mirror path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` tries the direct `ziglang.org` download URL before `community-mirrors.txt`.
- If the direct download still fails or produces a mismatched archive, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt`.
- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.

## Rules

- keep the filename exact so bootstrap can resolve the pinned archive without
  guessing
- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory
- update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json`
  changes the pinned target, channel, digest, or expected payload size
