# Phase 3 Interop Boundary Lane Sequencing

This note turns the current Phase 3 substrate evidence on `master` into one bounded anti-overlap map for scheduled interop-boundary lanes.

It is a coordination artifact, not a new helper tranche and not a claim that deeper helper-family growth is approved.

## Current posture

- `PHASE3_STATUS=active-substrate-packet`
- `PHASE3_SEQUENCE=interop-boundary-lane-anti-overlap`
- shared validation routes already present on `master`: `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3.py --slug abi`, `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `zig build phase3-test --build-file zigux/tests/build.zig`, and `zig build phase3-dump --build-file zigux/tests/build.zig`
- the shared packet anchor remains `Documentation/zigux/phase3-abi-slice.md` plus `zigux/tests/fixtures/phase3_abi_manifest.json`
- packet-local substrate notes already exist for export/UAPI, policy/unsafe, low-level wrappers, and the header-only next-step boundary, while the missing dedicated policy/unsafe replay pair remains a separate same-family gap

## Why this note exists

The current Phase 3 packet already has real product evidence, but it is split across a shared ABI slice and several packet-local substrate notes.

That split is useful and roadmap-correct, but without one owner map nearby scheduled runs can still reopen the same substrate surfaces from different directions:

- shared ABI slice wording and manifest-backed interop summary work
- export/UAPI starter boundary wording and the focused `phase3_export_uapi_layout` replay
- policy/unsafe survey maintenance versus the still-missing dedicated focused replay pair
- low-level wrapper packet truthfulness versus broader ABI parity work
- header-only next-step notes for `include/zigux/abi.h` growth versus packet-local helper or replay backlog

## Lane map

### 1. Shared ABI and curated bindings lane

Use the shared ABI lane when the work is about the canonical interop packet as a whole.

Own:

- `Documentation/zigux/phase3-abi-slice.md`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`

Do not use this lane for packet-local export/UAPI wording, low-level-wrapper survey maintenance, policy/unsafe note maintenance, or the missing dedicated policy/unsafe replay pair unless the shared ABI slice can no longer summarize those surfaces honestly.

### 2. Export/UAPI packet lane

Use the export/UAPI lane when the work is about the starter boundary relay, starter UAPI helper, Linux-facing aggregation header wording, or the focused shared boundary-header layout replay.

Own:

- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `zigux/kernel/export_shim.zig`
- `zigux/uapi/version.zig`
- `include/linux/zigux.h` when the change is about starter boundary wording or explicit export/UAPI entry points
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`

Do not use this lane to claim broader helper-family semantic growth once a surface is no longer just starter export/UAPI boundary plumbing, and do not consume shared ABI parity backlog here just because the same headers are nearby.

### 3. Policy/unsafe survey-maintenance lane

Use the policy/unsafe survey lane when the work is about packet-local truthfulness for the currently shipped panic, allocator, MMIO, unsafe-scope, or byte-guard note and checker packet.

Own:

- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/check-phase3-policy-byte-guards.py`

This lane may repair note markers, packet-local wording, or guard coverage for the already-landed shared ABI packet, but it should not claim the still-missing dedicated focused replay pair.

### 4. Policy/unsafe focused replay lane

Use the focused replay lane only when the work is about landing the missing dedicated policy/unsafe replay pair and the minimum manifest or validator follow-through that makes that pair real.

Own the future same-family gap around:

- the dedicated `phase3_policy_unsafe` replay and build entrypoints once they land
- the minimal `zigux/tests/fixtures/phase3_abi_manifest.json` updates required to name that replay
- the smallest shared `scripts/zigux/validate-phase3.py` or packet-local note follow-through required once the replay pair becomes real

Do not use this lane for broader policy machinery, helper-family expansion, or packet-local survey maintenance that belongs to the survey-maintenance lane above.

### 5. Low-level-wrapper packet lane

Use the low-level-wrapper lane when the work is about the bounded atomic, barrier, and MMIO helper packet plus its focused replay and survey note.

Own:

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

Do not use this lane to reopen shared ABI constant parity, export/UAPI starter wording, or packet-local policy/unsafe backlog unless the low-level-wrapper packet itself stops matching current `master`.

### 6. Header-growth next-step lane

Use the header-growth lane only when the work is about one bounded next-step note for live `include/zigux/abi.h` or curated binding growth.

Own:

- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- header-only next-step wording tied to `include/zigux/abi.h` and `zigux/bindings/abi.zig`

Do not use this lane to consume shared ABI parity work, packet-local replay backlog, or export/UAPI note maintenance just because those surfaces also depend on the authoritative header.

### 7. Shared summary and owner-map lane: `P3-X10`

Use this sequencing lane only when the owner split itself has drifted across shared review surfaces.

Own:

- `Documentation/zigux/phase3-interop-boundary-lane-sequencing.md`
- at most one shared summary surface when the owner split blurs, such as `Documentation/zigux/README.md`, `zigux/tests/README.md`, or `Documentation/zigux/review-checklist.md`

Do not use this lane to edit packet-local helpers, focused replays, manifest payloads, or validator behavior that belongs to one of the owning lanes above.

## Current anti-overlap correction

The strongest current Phase 3 sequencing rule is simple:

- keep packet-local truthfulness, replay, and checker changes inside the owning lane above
- use `P3-X10` only when the shared owner split or one shared summary surface has drifted
- if `include/linux/zigux.h` or `include/zigux/abi.h` grows, refresh the owning packet note plus the smallest shared surface it actually claims instead of letting header growth imply review coverage elsewhere

## Recommended next-step order

1. the owning packet lane when one note, manifest, checker, or focused replay stops matching current `master`
2. the shared ABI lane only when the shared manifest, curated bindings, syntax guard, or baseline constant-parity packet drifts
3. the header-growth next-step lane only when `include/zigux/abi.h` or the curated bindings grow again without a fresh bounded note
4. `P3-X10` only when docs-root, tests-root, or reviewer-facing guidance blurs the owner split again

## Anti-overlap rule

If a scheduled Phase 3 run is assigned one substrate lane, keep the work inside that packet plus the smallest unavoidable shared touch.

If `P3-X10` is assigned, do not consume packet-local replay, validator, or helper backlog just because the shared sequencing lane has spare room.
