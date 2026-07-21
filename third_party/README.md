# Zigux third-party archives

This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI
can validate locally before it falls back to network downloads.

## Current pinned Zig archive contract

- policy targets: `x86_64-linux`, `x86_64-windows`
- repo-local Lane 05 staging target: `x86_64-linux`
- channel: `0.17.0-dev.1443+6c25d2bd5`
- canonical release: [adybag14-cyber/zig `upstream-6c25d2bd58e4`](https://github.com/adybag14-cyber/zig/releases/tag/upstream-6c25d2bd58e4)
- file: `third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz`
- parts: `third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz.parts`
- sha256: `4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9`
- Linux size: `59093540` bytes
- Windows file: `zig-x86_64-windows-0.17.0-dev.1443+6c25d2bd5.zip`
- Windows sha256: `0c538cabcea1ef1d114b99f6e9f3099d4c4c22070daa19819511b783c5f40211`
- Windows size: `103440485` bytes
- policy: `scripts/zigux/zig-toolchain-policy.json`
- duplicate-copy boundary: `zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5 (1).tar.xz`

## Validation

- `scripts/zigux/check_zig_toolchain.zig`
- `scripts/zigux/stage_pinned_zig_archive.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `zig test scripts/zigux/toolchain_policy.zig` — policy parsing and version evaluation
- `zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz --archive-target x86_64-linux`

## Bootstrap order

- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz` when that pinned archive is present.
- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `zig run scripts/zigux/stage_pinned_zig_archive.zig` before canonical release, mirror, or direct-download fallback.
- Before retrying the canonical release, mirror, or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to the rolling canonical [`adybag14-cyber/zig`](https://github.com/adybag14-cyber/zig) release (`upstream-6c25d2bd58e4`) before `community-mirrors.txt` and the direct `ziglang.org` download URL.
- `scripts\zigux/check_lane05_local_first_archive_workflow.zig` and `scripts\zigux/check_lane05_local_archive_readme.zig` are the shipped reminder guards for that local-first archive path.
- `scripts\zigux/check_lane05_install_zig_archive_verification.zig`, `scripts\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\zigux/check_lane05_stage_helper_selftest.zig` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.

## Git LFS

Pinned `.tar.xz` archives and `.tar.xz.parts/` shards are tracked with Git LFS (see `.gitattributes`).
Clone with `git lfs pull` when working offline with the repo-local archive contract.

## Rules

- keep the filename exact so bootstrap can resolve the pinned archive without guessing
- repo-local pinned archive filename is part of the guarded bootstrap contract
- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5 (1).tar.xz` in this directory
- duplicate-copy boundary: duplicate-suffix archives are rejected before staging
- update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json` changes the pinned target, channel, digest, or expected payload size