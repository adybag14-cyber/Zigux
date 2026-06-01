# Zigux third-party archives

This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI
can validate locally before it falls back to network downloads.

## Current pinned Zig archive contract

- target: `x86_64-linux`
- channel: `0.17.0-dev.758+748e7c5e3`
- file: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`
- sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`
- self-test fixture digest marker: `3333333333333333333333333333333333333333333333333333333333333333`
- size: `59410844` bytes

## Validation

- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz --archive-target x86_64-linux`

## Bootstrap order

- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz` when that pinned archive is present.
- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before canonical release, mirror, or direct-download fallback.
- Before retrying the canonical release, mirror, or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL.
- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.
- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.

## Rules

- keep the filename exact so bootstrap can resolve the pinned archive without
  guessing
- repo-local pinned archive filename is part of the guarded bootstrap contract
- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz` in this directory
- duplicate-copy boundary: duplicate-suffix archives are rejected before staging
- update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json`
  changes the pinned target, channel, digest, or expected payload size
