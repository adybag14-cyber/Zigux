# Phase 12 Focused Replay Surface Sync

This note keeps the active Phase 12 shared-versus-focused libbpf replay packet reviewable when contributor-facing wording changes.

It exists because the same bounded replay contract now spans the shared validator, the focused replay checker, the scripts-root flow note, the tests-root guide, the contract note, the Makefile route, and the dedicated build shard. Small wording drift across those surfaces has been a recurring same-lane maintenance risk.

## Scope

Use this note when a Phase 12 change touches any of these surfaces:

- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase12-shared-replay-contract.md`
- `scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `scripts/zigux/check-phase12-shared-replay-contract.py`
- `scripts/zigux/validate-phase12.py`
- `zigux/tests/phase12_libbpf_only_build.zig`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `zigux/tests/phase12_libbpf_manifest.json`

## Shared Contract

Keep these two ideas explicit together:

- `make -C zigux phase12` and `zig build test --build-file zigux/tests/phase12_build.zig --summary all` are the shared Phase 12 tranche replay.
- the focused libbpf-only shard remains separate through `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`, `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`, and the named `zig build --build-file zigux/tests/phase12_libbpf_only_build.zig phase12-libbpf-focused-replay --summary all` alias.

If one surface names only the direct focused replay while another names both the direct replay and the alias, treat that as packet drift and repair it before calling the Phase 12 note stack reviewable.

## Update Order

When the focused replay wording changes, update in this order:

1. `Documentation/zigux/phase12-shared-replay-contract.md`
2. `scripts/zigux/README.md`
3. `zigux/tests/README.md`
4. `scripts/zigux/check-phase12-libbpf-focused-replay.py`
5. `scripts/zigux/check-phase12-shared-replay-contract.py`
6. `scripts/zigux/validate-phase12.py`
7. `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` if the replay entrypoints themselves changed
8. `Documentation/zigux/phase12-libbpf-segment-survey.md` and `zigux/tests/phase12_libbpf_manifest.json` if the focused shard changed what bounded evidence it owns

This order keeps the contract note first, the contributor-facing surfaces next, and the fail-closed guard stack last.

## Drift Checks

Before treating a focused replay refresh as complete, confirm all of these still agree:

- the shared replay remains validator-first through `make -C zigux phase12-validate` before `make -C zigux phase12`
- the focused libbpf-only shard still stays outside the shared `phase12` wrapper
- the direct focused replay command is present where the packet still names the shard explicitly
- the named `phase12-libbpf-focused-replay` alias is present on every surface that describes rerunning that same focused shard by name
- the focused replay checker and the shared contract checker still both name the same tests-root and contract-note agreement surface
- the broader `scripts/zigux/validate-phase12.py` marker set still matches the published contributor wording instead of silently accepting duplicate or missing alias text

## Review Use

This note is intentionally small. It is a maintenance aid for the active Phase 12 complex-driver and heavy-helper packet, not a new product claim.

If the packet changes beyond this shared-versus-focused boundary, return to the packet-local survey note, manifest, checker, or validator that owns that deeper evidence instead of expanding this note into a second roadmap summary.
