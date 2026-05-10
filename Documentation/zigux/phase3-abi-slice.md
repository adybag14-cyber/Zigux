# Phase 3 ABI Substrate Slice

This document starts the first bounded Phase 3 slice for Zigux.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=abi-substrate-skeleton`
- scope: first permanent C/Zigux boundary only
- product boundary:
  - `include/linux/zigux.h`
  - `include/zigux/abi.h`
  - `include/zigux/dev_t.h`
  - `zigux/bindings/abi.zig`
  - `zigux/bindings/dev_t.zig`
  - `zigux/bindings/notifier_abi.zig`
  - `zigux/kernel/export_shim.zig`
  - `zigux/helpers/*`
  - `zigux/unsafe/narrow.zig`
  - `zigux/uapi/version.zig`
  - `zigux/uapi/dev_t.zig`
  - `zigux/tests/phase3_abi.zig`
  - `zigux/tests/phase3_low_level_wrappers.zig`
- current export shim starter:
  - `PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice`
  - `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
  - `PHASE3_EXPORT_SHIM_BLOB_SHA=b90218a19052bee7edff9b3a3fd767e7c6b582b5`
  - current export-shim relay surface now keeps the named boundary-header relay, requested-header evaluation, explicit compatibility-tag relay, and explicit status packet surface through `Header`, `abi_version`, `header_size`, `HeaderCompatibility`, `HeaderAcceptance`, `HeaderEvaluation`, `CompatibilityDecision`, `versionedHeader`, `canonicalHeader`, `boundaryHeader`, `compatibleHeader`, `header`, `acceptHeader`, `headerCompatibility`, `compatibilityTag`, `canonicalizeHeader`, `evaluateHeader`, `compatibilityStatus`, `isCurrentAbiVersion`, `isCompatibleSize`, `isCanonicalSize`, `isCompatibleHeader`, `isCanonicalHeader`, `ok`, `errno`, `normalize`, and `isOk`
- current UAPI starter:
  - `PHASE3_UAPI_SCOPE=version-and-dev_t starters nested inside the ABI substrate slice`
  - `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
  - `PHASE3_UAPI_VERSION_BLOB_SHA=51cbc1e3c195f9de7e29ccaf498cf407c83a8a26`
  - current `version.zig` starter surface now stays limited to `Header`, `Compatibility`, `AcceptedHeader`, `HeaderEvaluation`, `abi_version`, `header_size`, `versionedHeader`, `canonicalHeader`, `boundaryHeader`, `compatibleHeader`, `isCurrentAbiVersion`, `isCompatibleSize`, `isCanonicalSize`, `compatibility`, `compatibilityTag`, `isCompatible`, `isCanonical`, `acceptHeader`, `canonicalizeHeader`, and `evaluateHeader`
  - `PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig`
  - `PHASE3_UAPI_DEV_T_BLOB_SHA=f346882bd50b5c2f8473a8f72be51bfd8117fcb4`
  - current `dev_t.zig` starter surface now stays limited to `minor_bits`, `minor_mask`, `major_max`, `encode`, `major`, `minor`, `rangeFits`, and `lastInRange`
- current export/UAPI survey shape:
  - `PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof`
  - current `master` keeps the packet-local `phase3-export-uapi-boundary-survey.md` note, the focused `phase3_export_uapi_layout` replay, the dedicated Linux `zigux.h` governance note, and the dedicated `validate-phase3-export-uapi-survey.py` checker nested under this shared ABI slice rather than a broader standalone `phase3_export_uapi*` replay family
  - current boundary evidence therefore lives in this shared ABI slice plus the packet-local export/UAPI survey note, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, the focused `phase3_export_uapi_layout` replay, `include/linux/zigux.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, and `zigux/uapi/dev_t.zig`
  - live manifest and make-route wiring also still carry `zigux/tests/phase3_export_uapi.zig`, `zigux/tests/phase3_export_uapi_build.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` as packet-local behavior and build-wrapper companions for that same starter proof, so the export/UAPI packet is no longer layout-only even though it remains nested under this shared ABI slice rather than reopening a standalone lane
  - docs-root tranche summaries should keep the export/UAPI boundary packet explicit as part of ledger entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, through this shared ABI slice, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, the focused `phase3_export_uapi_layout` replay, and clear boundary wording so the active Phase 3 packet does not collapse back into an ABI-plus-policy-only note when the boundary starter moves
- current shared ABI replay:
  - `PHASE3_ABI_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
  - `PHASE3_ABI_MANIFEST_FILE_COUNT=58`
  - `PHASE3_ABI_REPLAY_SCOPE=shared dump plus focused low-level wrapper, export-uapi layout, and validator-support replays`
  - the live `phase3_abi` packet now exercises the curated boundary header and export status root, bitmap and cpumask views, list and hlist views, err_ptr and xarray summaries, the current ida and minor-allocation/dev-region planning ladder, the notifier starter binding packet, and the currently shipped chrdev notify/ack delivery-budget guard families through the shared dump and layout harness
  - the focused syntax gate now fail-closes on fused top-level C header declarations in `include/zigux/abi.h` plus fused top-level `;pub const` declarations in `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, or `zigux/bindings/notifier_abi.zig` until the authoritative header and curated bindings bodies are split back into parse-clean lines
  - the current shared ABI packet also keeps the focused low-level-wrapper boundary packet explicit across `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/tests/phase3_low_level_wrappers.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` so the landed signed atomic edges, direct barrier-locality proof, helper-local MMIO interop-policy gates, and byte, 16-bit, 32-bit, and 64-bit MMIO replay stay reviewable beside the broader compile, layout, and dump packet
  - the current shared ABI packet also keeps the focused export/UAPI boundary replay explicit across `zigux/tests/phase3_export_uapi_layout.zig`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, and `Documentation/zigux/phase3-linux-zigux-header-governance.md` so the manifest-backed replay surface matches the shipped packet-local starter proof, including accepted-header canonicalization, requested-header evaluation, compatibility-status relays, and the starter `dev_t` constant plus range-parity evidence
  - the current shared ABI packet also keeps the direct export/UAPI behavior replay explicit across `zigux/tests/phase3_export_uapi.zig` and `zigux/tests/phase3_export_uapi_build.zig` so canonical-header parity, future-compatible acceptance, explicit compatibility-status relays, and starter `dev_t` encode-or-range parity stay reviewable beside the focused layout proof instead of being implied only by the shared dump or validator packet
  - the current shared ABI packet also keeps the focused validator-support packet explicit across `scripts/zigux/validate_phase3_selftest.py`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/check-phase3-readme-tooling-inventory.py`, `scripts/zigux/check-phase3-abi-dump-gate.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/phase3_catalog.py`, `scripts/zigux/phase3_check_lib.py`, `scripts/zigux/generate-phase3-check-wrappers.py`, and `scripts/zigux/run-phase3-checks.py` so the shared helper self-checks, dump-gate proof, tooling inventory audit, catalog audit, shared checker-library self-checks, wrapper-drift guard, and runner self-checks remain reviewable beside the main ABI replay
  - the current shared ABI packet also keeps the focused baseline constant-parity survey explicit across `Documentation/zigux/README.md`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json` through `scripts/zigux/survey-phase3-abi-constant-parity.py`
  - the current shared ABI packet also keeps the dedicated header-family survey explicit across `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, `include/zigux/abi.h`, and `zigux/bindings/abi.zig` so the already-landed `chrdev_notify_ack_window_policy_budget_window_delivery_window` foothold stays reviewable one bounded family proof at a time beside the broader constant-parity survey instead of disappearing into the larger header ladder
  - the current shared ABI packet also keeps the direct ABI interop route explicit through the shared `scripts/zigux/run-phase3-checks.py --slug abi` entrypoint, with `scripts/zigux/check-phase3-abi.py` retained only as the generated legacy wrapper alias, so the shared syntax, constant-parity, policy-byte, and bounded slug-backed interop replay route stays reviewable beside the Linux-style `make -C zigux phase3-abi` and `make -C zigux phase3` entrypoints
  - the current shared ABI packet also keeps the focused policy-and-unsafe survey packet explicit across `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, and `scripts/zigux/check-phase3-policy-byte-guards.py` so the narrow panic, allocator, MMIO, and unsafe-scope boundary wording stays reviewable without pretending the still-missing dedicated replay pair already exists

## Why this slice exists

Phase 3 is where Zigux stops being only helper and tool scaffolding and starts defining the real boundary between C and Zig.

The first correct move is not a broad runtime port.
It is a small substrate that makes future ports measurable:

- one C header pair
- curated Zig boundary bindings that keep the ABI root plus the `dev_t` and notifier starter surfaces reviewable
- one export-shim module
- explicit panic and allocator policies
- explicit atomic, barrier, and MMIO wrappers
- one narrow unsafe layer
- one shared C-vs-Zig layout gate plus one focused low-level wrapper replay

## Gates

1. validate slice shape
- `python3 scripts/zigux/validate-phase3.py`
- bounded ABI replay when unrelated Phase 3 slices are still in flight:
  `python3 scripts/zigux/validate-phase3.py --slug abi`

2. check the shared Phase 3 ABI interop packet and C-vs-Zig ABI layout parity
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `python3 scripts/zigux/check-phase3-abi.py`

3. run Zig substrate tests and the direct ABI dump replay
- `zig build phase3-test --build-file zigux/tests/build.zig`
- `zig build phase3-dump --build-file zigux/tests/build.zig`

4. catch fused top-level declarations across the authoritative `include/zigux/abi.h` boundary plus the curated `abi.zig`, `dev_t.zig`, and `notifier_abi.zig` packet before they hide inside the wider Phase 3 packet
- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test`

5. rerun the shared baseline constant-parity survey so the authoritative C header, curated Zig bindings, dump replay, C harness, and committed expected fixture keep naming the same rooted ABI values
- `python3 scripts/zigux/survey-phase3-abi-constant-parity.py`
- `python3 scripts/zigux/survey-phase3-abi-constant-parity.py --self-test`

6. rerun the dedicated header-family survey so the already-landed chrdev notify/ack window family foothold stays explicit across the authoritative C header and curated Zig bindings before broader `include/zigux/abi.h` growth lands
- `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test`

7. rerun the validator-support packet and its review-surface guard without duplicating the default route
- `python3 scripts/zigux/validate_phase3_selftest.py`
- `python3 scripts/zigux/check-phase3-selftest-surface.py --self-test`
- `python3 scripts/zigux/check-phase3-selftest-surface.py`
- `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test`
- `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py`
- `python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test`
- `python3 scripts/zigux/check-phase3-abi-dump-gate.py`
- `python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test`
- `python3 scripts/zigux/phase3_catalog.py --self-test`
- `python3 scripts/zigux/phase3_catalog.py --audit-doc-sync`
- `python3 scripts/zigux/phase3_check_lib.py --self-test`
- `python3 scripts/zigux/generate-phase3-check-wrappers.py --check`
- `python3 scripts/zigux/run-phase3-checks.py --self-test`
- `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-byte-guards.py`
- `python3 scripts/zigux/check-phase3-policy-byte-guards.py --self-test`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test`
- `python3 scripts/zigux/validate-phase3-export-uapi-survey.py`
- `python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test`
- `make -C zigux phase3-selftest`
- focused support-script safety check only; `make -C zigux phase3-validate` already invokes the underlying helper self-tests, README tooling inventory checks, catalog sanity checks, wrapper drift checks, shared catalog doc-sync auditing, and shared runner self-checks directly.

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Low-Level Wrapper Reality

The current Phase 3 low-level wrapper packet is still intentionally small, but it now carries direct focused proof alongside the shared ABI packet:

- `zigux/helpers/atomic.zig` now exposes `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchNand`, `fetchMin`, `fetchMax`, `compareExchange()`, and `compareExchangeWeak()`.
- `zigux/helpers/barrier.zig` now exposes `acquire`, `release`, `full`, and `acquireRelease()` through local compile-review scaffolding rather than a module-global fence word.
- `zigux/helpers/mmio.zig` now exposes `range`, `allowsInteropPolicyBytes`, `allowsInteropPolicy`, `requireInteropPolicyBytes`, `requireInteropPolicy`, `rangeInteropPolicyBytes`, `rangeInteropPolicy`, direct `read8` and `write8`, direct `read16` and `write16`, direct `read32` and `write32`, direct `read64` and `write64`, and the policy-gated `read*InteropPolicy*` and `write*InteropPolicy*` relays.
- `zigux/tests/phase3_low_level_wrappers.zig` now directly replays the shipped helper surface, including signed `fetchAdd` and `fetchSub`, signed `fetchMin` and `fetchMax`, monotonic strong `compareExchange()`, `acq_rel` strong `compareExchange()` mismatch handling, direct barrier-locality proof, non-`seq_cst` ordering, helper-local MMIO interop-policy gates, plus byte-addressed 16-bit, 32-bit, and 64-bit MMIO range descriptors and odd-offset MMIO behavior.
- the shared ABI packet still carries the wider compile, layout, dump proof.

## Interop rules

- `include/zigux/abi.h` is the authoritative C-facing layout surface for this slice.
- `zigux/bindings/abi.zig` must mirror it with `extern struct` layout, not approximate it.
- `include/zigux/dev_t.h` and `zigux/bindings/dev_t.zig` stay curated beside the ABI root so `dev_t` encode, decode, range policy, and last-in-range parity remain reviewable at the same boundary.
- `zigux/bindings/notifier_abi.zig` stays in the shared ABI packet so notifier-chain flags plus the starter head, block, view, and summary layouts do not drift outside the curated Phase 3 review surface.
- new boundary structs require committed fixture updates under `zigux/tests/fixtures/phase3_abi/`.
- export shims must return explicit status codes instead of hidden failure behavior.
- future bindings generators are allowed later, but this slice stays curated and reviewable.

## Linux Header Governance

The dedicated export/UAPI survey still tracks the starter boundary packet, but this shared ABI slice owns the broader header-growth rule for `include/linux/zigux.h` so neighboring export/UAPI and helper lanes do not compete for the same aggregation policy.

- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=include/linux/zigux.h remains the curated Linux-facing aggregation header for already-landed Phase 3 helper views and summaries, while canonical layout ownership stays in include/zigux/abi.h and include/zigux/dev_t.h and the packet-local export/UAPI survey only proves the starter boundary helpers it directly covers.`
- `PHASE3_C_HEADER_GROWTH_RULE=new top-level helpers or view families may land in include/linux/zigux.h only when the same change also updates this shared ABI note plus manifest-backed dump or focused replay evidence for the added surface, while the packet-local export/UAPI survey refresh stays limited to the starter-boundary subset it actually proves.`
- `include/linux/zigux.h` should relay and aggregate already-approved boundary helpers; it should not become a second source of truth for struct layout or policy definitions that belong in the curated ABI headers.
- when the Linux-facing relay needs `dev_t` minor-width aliases, it should aggregate `include/zigux/dev_t.h` rather than restating `ZIGUX_DEV_MINOR_BITS` or `ZIGUX_DEV_MINOR_MASK` locally, because those aliases already belong to the canonical `dev_t` boundary.

## Current Interop Gap

The roadmap's Phase 3 target is no longer blocked on a missing starter boundary. Live `master` already carries the explicit export shim, curated bindings roots, layout-backed replay, policy helpers, wrapper packet, narrow unsafe layer, and the starter `version.zig` plus `dev_t.zig` UAPI family that make the first permanent C/Zigux boundary reviewable.

- the live bindings packet is still concentrated in `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/notifier_abi.zig` even though `include/linux/zigux.h` now aggregates many already-approved helper views and summaries, and the Linux-facing relay still locally restates `ZIGUX_DEV_MINOR_BITS` and `ZIGUX_DEV_MINOR_MASK` instead of folding those aliases back under `include/zigux/dev_t.h`.
- `zigux/uapi/` now includes `version.zig` and `dev_t.zig`, so the shipped UAPI surface is no longer only the boundary-header contract, but it remains a starter packet rather than the wider exported family the long-term substrate will eventually need.
- the next honest interop-growth step therefore is not more wrapper-first churn inside the existing starter packet; it is a new top-level boundary family that lands with the shared ABI manifest, a focused replay or dump proof, and the shared review-surface refresh required by this note.
- until that happens, header aggregation alone should not be treated as Phase 3 interop closure, because the roadmap still expects explicit binding ownership, packet-local proof, and narrow reviewable growth for each added boundary family.

## Policy surfaces

Panic policy:
- explicit modes only: `abort`, `bug`, `warn`
- no implicit panic behavior in boundary helpers

Allocator policy:
- explicit modes only: `caller_provided`, `kernel_heap`, `arena`
- boundary code must be able to state whether it requires a caller allocator

Unsafe policy:
- raw pointer and volatile access stay inside `zigux/unsafe/narrow.zig` and `zigux/helpers/mmio.zig`
- new unsafe entry points must be justified and reviewed as boundary expansion

## Boundary

This slice does not claim:

- generated bindings
- full kernel UAPI exposure
- full runtime allocator integration
- driver ports
- scheduler ports
