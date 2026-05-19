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

## Rules

- keep the filename exact so bootstrap can resolve the pinned archive without
  guessing
- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory
- update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json`
  changes the pinned target, channel, digest, or expected payload size
