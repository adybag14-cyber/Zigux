# Phase 12 Bootstrap Lane Contract

This note records the current Phase 12 portion of the bootstrap workflow without
rewriting the broader reminder packet or reopening the live workflow file in this
lane.

## Status

- `PHASE12_BOOTSTRAP_LANE=active`
- lane owner: `Lane 05`
- workflow anchor: `.github/workflows/zigux-bootstrap.yml`
- checker anchor: `scripts/zigux/check-phase12-bootstrap-contract.py`

## Current Bootstrap Contract

- the current bootstrap workflow still begins with `Compile current scripts`
- the current Phase 12 slice sits after the current Zig toolchain, Phase 2, Phase 1, Phase 4, Phase 7, Phase 10, and Phase 11 packets
- the current Phase 12 bootstrap segment reruns `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all` are current bootstrap-lane evidence on `master`
- the current bootstrap tail still ends with `make -C zigux phase8-validate`, `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, and `Check current docs-root sanity markers`
- the shipped docs guard is still the inline `Check current docs-root sanity markers` step from `.github/workflows/zigux-bootstrap.yml`
- `Check current Phase 12 build-only surface`, `Self-test current Phase 12 bootstrap docs sanity checker`, `Check current Phase 12 docs-root sanity markers`, `Self-test current Phase 12 bootstrap lane checker`, and `Check current Phase 12 bootstrap lane shape` belong to the active Lane 05 workflow review branch, not current `master`
- until the workflow changes again, Lane 05 should keep this contract companion aligned to the broader current-`master` bootstrap segment instead of the older smaller-tail packet or the active branch-only checker pair

## Next Bounded Step

If later Lane 05 work changes the live bootstrap shape again, refresh this note
and its checker in the same change.
