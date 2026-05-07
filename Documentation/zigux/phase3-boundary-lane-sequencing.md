# Phase 3 Boundary Lane Sequencing

This note turns the current Phase 3 substrate on `master` into one bounded owner map so shared review surfaces stop blurring packet-local responsibility.

## Status

- `PHASE3_BOUNDARY_MAP_STATUS=active`
- `PHASE3_BOUNDARY_MAP_SCOPE=shared-abi-slice-plus-header-next-step-plus-export-uapi-plus-policy-unsafe-plus-low-level-wrapper`
- `PHASE3_LEDGER_ANCHOR=BOOTSTRAP_COMMIT_LEDGER.md entry 26 feat(zigux): start bounded Phase 3 abi substrate skeleton`
- `PHASE3_SHARED_ABI_OWNER=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_HEADER_NEXT_STEP_OWNER=Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `PHASE3_EXPORT_UAPI_OWNER=Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `PHASE3_POLICY_UNSAFE_OWNER=Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `PHASE3_LOW_LEVEL_WRAPPER_OWNER=Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `PHASE3_SHARED_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_SHARED_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_HEADER_CONSTANT_SURVEY=python3 scripts/zigux/survey-phase3-abi-constant-parity.py`

## Why This Note Exists

The roadmap and ledger both treat Phase 3 as the permanent C and Zigux boundary, not as one giant undifferentiated helper packet.

Live `master` now ships a shared ABI slice note plus four narrower packet-local notes:

- the shared ABI slice
- the dedicated `include/zigux/abi.h` next-step note
- the dedicated export/UAPI boundary survey
- the dedicated policy-and-unsafe boundary survey
- the dedicated low-level-wrapper boundary survey

That repo reality is already useful, but without one owner map the same shared Phase 3 summaries can read as though any nearby note owns all header growth, all helper growth, or all review wiring. This note narrows those claims back to the packet that actually owns them.

## Owner Map

### Shared ABI slice owner

`Documentation/zigux/phase3-abi-slice.md` owns the aggregate Phase 3 product boundary and the shared review packet for:

- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- curated bindings under `zigux/bindings/`
- helper surfaces under `zigux/helpers/`
- `zigux/unsafe/narrow.zig`
- the shared ABI replay and dump packet
- the shared manifest-backed `abi` slice wording

Use the shared ABI slice when the drift is about aggregate packet counts, broad scope wording, shared manifest-backed replay coverage, or the default `validate-phase3.py` and `run-phase3-checks.py --slug abi` route.

### Header-only next-step owner

`Documentation/zigux/phase3-abi-h-boundary-next-step.md` owns the bounded reviewability cue for `include/zigux/abi.h` and `zigux/bindings/abi.zig` when the live authoritative header grows faster than the smallest shipped dedicated survey.

Use the header-next-step note when the change is about:

- top-level `include/zigux/abi.h` family growth
- curated `zigux/bindings/abi.zig` family drift tied to that same header
- the dedicated baseline constant-parity survey in `scripts/zigux/survey-phase3-abi-constant-parity.py`
- the next safe header-family survey to add before more top-level surface lands

Do not treat this note as the owner of export/UAPI relay wording, policy bytes, or low-level-wrapper helper replay.

### Export/UAPI owner

`Documentation/zigux/phase3-export-uapi-boundary-survey.md` owns the starter export-shim and starter UAPI boundary wording plus the focused `zigux/tests/phase3_export_uapi_layout.zig` replay.

Use the export/UAPI survey when the change is about:

- `zigux/kernel/export_shim.zig`
- `zigux/uapi/version.zig`
- boundary-header relay wording
- explicit export-status normalization
- the focused `phase3_export_uapi_layout` replay
- packet-local starter boundary review wiring

Do not use the export/UAPI survey to claim ownership of broader `include/zigux/abi.h` family growth that already belongs to the shared ABI slice and the dedicated header-next-step note.

### Policy and unsafe owner

`Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` owns the bounded allocator-policy, panic-policy, MMIO-policy, and narrow-unsafe wording plus the packet-local byte-guard contract.

Use the policy-and-unsafe survey when the change is about:

- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/unsafe/narrow.zig`
- the policy-byte guard in `scripts/zigux/check-phase3-policy-byte-guards.py`
- packet-local truthfulness around `InteropPolicy` mode and reserved-byte handling

Do not use this survey to imply that a dedicated focused replay pair already exists when the current live packet is still nested under the shared ABI slice.

### Low-level-wrapper owner

`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` owns the focused atomic, barrier, and MMIO helper replay surface for the currently shipped low-level wrapper packet.

Use the low-level-wrapper survey when the change is about:

- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- focused replay coverage for signed atomic edges, compare-exchange behavior, barrier locality, or MMIO width and alignment behavior

Do not use this survey to claim ownership of the broader shared ABI compile, layout, or dump proof, which still belongs to the shared ABI slice.

## Shared Review Surfaces Are Not Owners

The shared review surfaces below keep Phase 3 reviewable, but they do not transfer packet ownership away from the notes above:

- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/run-phase3-checks.py`
- `zigux/Makefile`

If one of those shared surfaces drifts, fix the shared wording only after checking which packet-local owner actually moved first.

## Next-Step Routing

When a later run finds a new Phase 3 mismatch, route it through the smallest owner above:

- if `include/zigux/abi.h` or `zigux/bindings/abi.zig` grows at the top level, reopen the header-next-step note or the constant-parity survey
- if boundary-header relay helpers or starter UAPI wording moves, reopen the export/UAPI survey and the focused layout replay
- if panic, allocator, or unsafe policy bytes move, reopen the policy-and-unsafe survey and the policy-byte guard
- if atomic, barrier, or MMIO helper behavior moves, reopen the low-level-wrapper survey and the focused wrapper replay
- if the aggregate packet, manifest-backed replay, or shared route wording drifts, reopen the shared ABI slice or the shared validator-first review surface

This keeps Phase 3 follow-up bounded to the surface that actually changed instead of reopening the whole substrate every time one nearby packet moves.
