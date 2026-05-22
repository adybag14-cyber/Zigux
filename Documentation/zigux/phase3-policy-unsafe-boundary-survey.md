# Phase 3 Policy and Unsafe Boundary Survey
This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.
## Status
- `PHASE3_SURVEY_PROVENANCE=connector-current-head-sha-unavailable-in-run`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-notifier-list-and-chrdev-layout-asserts-consumed-by-both-the-shared-abi-replays-and-the-focused-policy-starter-packet`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=733becd1482b8a514ead992d1158a52a8c47e6c1`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-plus-escalation-and-byte-decoders`
- `PHASE3_PANIC_POLICY_BLOB_SHA=d05afcf0c0ef4e5558f8d8094bedf831c413407c`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-plus-init-flow-owned-state-and-reset-gates`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=01a6b30ab444a9b6be66eb1fb3a0e3666f55863a`
- `PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig`
- `PHASE3_UNSAFE_POLICY_SCOPE=helper-local-unsafe-scope-relay-over-the-shared-narrow-decoder-plus-permits-and-audit-aliases`
- `PHASE3_UNSAFE_POLICY_BLOB_SHA=f9ff3f1a23fdb62863565c10a296ca05e7577b1f`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=7dfaf2bf737cb744442ec8596bd93d277d05f092`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge-with-explicit-audit-gates`
- `PHASE3_UNSAFE_BLOB_SHA=5134f64b89b1a2c7be8c32477ddf9888aba36cf6`
- `PHASE3_POLICY_SLICE_DOC_BLOB_SHA=ad68cc62ca4a7230cf5a98242372b49b2a7b02b9`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA=7cc6988f98f5c76b9ffd6ccfcdfa8802b1083fcd`
- `PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json`
- `PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `PHASE3_POLICY_PACKET_TEST_GATE=zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`
- `PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_POLICY_UNSAFE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-helper-local-policy-slice-and-the-directly-coupled-low-level-wrapper-packet`
- `PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-or-the-dedicated-policy-unsafe-survey-gate-drift-again`
## Roadmap Contract
Phase 3 is where Zigux starts defining permanent C and Zig boundary rules rather than only helper scaffolding.
For this lane, the roadmap-backed contract is still narrow:
- canonical layout assertions on the curated ABI bindings
- explicit panic policy modes
- explicit allocator policy modes and init ownership
- one narrow unsafe surface for raw pointers and MMIO
- shared ABI validation and replay gates that keep those rules reviewable
This lane does not justify broad runtime policy machinery on its own.
## Live Repo Reality
This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.
Current `master` now also carries `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, which exact-requires those helper and adjacent-note blob markers so this survey fails closed when the live `layout_assert`, `panic_policy`, `allocator_policy`, `unsafe_policy`, `mmio`, or `narrow` packet drifts.
The current tree still carries a real bounded policy-and-unsafe packet, but the live proof surface has split into a helper-local policy slice plus a directly coupled low-level-wrapper packet rather than the older shared-ABI-only reminder route:
- `zigux/helpers/layout_assert.zig` is still a small generic helper, but it now centralizes compile-time layout checks for `BoundaryHeader`, `ExportStatus`, `InteropPolicy`, `NotifierBlock`, `ChainPriorityIncrease`, `ListHead`, `HListHead`, `HListNode`, `ListBackLinkBreak`, and `HListPrevLinkBreak` plus the current panic, allocator, unsafe-scope, and notifier-result values, and it now also keeps the current chrdev notify ack-window policy budget-window delivery-window view, summary, budget-view, and budget-summary layouts explicit so those ABI structs and constants no longer live only in the shared replays.
- `zigux/helpers/panic_policy.zig` now keeps panic escalation explicit through `Escalation`, `escalationFor`, `causesImmediateHalt`, `emitsKernelBug`, and `permitsWarningOnlyContinuation`, while still rejecting unknown panic modes and nonzero reserved bytes through `modeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, and the paired `*PolicyBytes`, `*InteropPolicy`, and `*Byte` relays before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/helpers/allocator_policy.zig` keeps allocator mode, init ownership, owned-state setup, and reset requirements explicit through `InitFlow`, `initFlowFor`, `modeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `permitsGlobalFallbackPolicyBytes`, `initializesOwnedStatePolicyBytes`, and `requiresResetOnInitPolicyBytes` so unknown allocator modes, helper-owned initialization, arena reset requirements, and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.
- `zigux/helpers/unsafe_policy.zig` now relays its helper-local unsafe-scope decisions through `zigux/unsafe/narrow.zig` while keeping the unsafe capability split explicit through `AccessBoundary`, `accessBoundaryFor`, `permitsNoUnsafe`, `requiresDedicatedAudit`, `permitsVolatileMmio`, and `permitsRawPointerBridge`, including the newer scope and permits symmetry aliases that the helper-local policy starter packet and focused policy dump route both read back directly.
- `zigux/unsafe/narrow.zig` now keeps the raw-pointer bridge deliberately small and reviewable through `Surface`, `surfaceFor`, `isUnsafe`, `requiresDedicatedAudit`, `requireRawPointerBridgePolicyBytes`, `pointerAtInteropPolicyBytes`, `constPointerAtInteropPolicy`, `constSliceAtInteropPolicy`, `sliceAtInteropPolicyBytes`, `writeValueAtInteropPolicyBytes`, and the paired typed and raw-byte relays plus denial-path tests, while remaining a directly coupled narrow decoder rather than the sole proof route for the broader policy packet.
- `zigux/helpers/mmio.zig` keeps volatile register access explicit through `read`, `write`, `exchange`, and `writeMasked`, and it now gates typed and byte-policy MMIO access through `zigux/helpers/unsafe_policy.zig` via `readScoped`, `writeScoped`, `exchangeScoped`, `writeMaskedScoped`, `readInteropPolicy`, `writeInteropPolicy`, `exchangeInteropPolicy`, and `writeMaskedInteropPolicy`, plus the paired `*InteropPolicyBytes` relays so volatile-MMIO callers stay inside the bounded unsafe contract.
- `Documentation/zigux/phase3-policy-slice.md`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts/zigux/check-phase3-policy-dump.py` now keep the helper-local panic, allocator, and unsafe-policy decoders reviewable as one bounded packet through both the starter manifest route, the direct starter packet test route, and the focused policy dump route, with the dump replay now cross-checking the bounded raw-pointer bridge mutable-pointer, const-pointer, const-slice, and write entry points over the same policy records.
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` keep the directly coupled MMIO-plus-narrow wrapper packet explicit without implying broader Phase 3 completion.
The current tree still does not ship a dedicated `phase3_policy_unsafe` replay pair, but the live proof is no longer shared-ABI-slice-only. It is split between the helper-local policy starter packet, the direct starter packet test route, the focused policy dump route, the directly coupled low-level-wrapper packet, and the dedicated blob-marker survey guard. This note should stay tied to those current packet-local surfaces instead of using `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, or `scripts/zigux/validate-phase3.py` as its parking trigger.
## Ledger Alignment
This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`. That means this lane remains survey-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.
## Current Boundary Gap
Current same-family progress already includes helper-local explicit-byte decoding, explicit allocator init-flow reviewability, typed-policy relays, explicit panic escalation reviewability, explicit unsafe audit gates, the focused policy dump route, and the restored raw-pointer bridge helper family:
- the panic helper now names the escalation outcome through `Escalation` and keeps the typed, raw-byte, and `InteropPolicy` panic decisions aligned through `causesImmediateHalt*`, `emitsKernelBug*`, and `permitsWarningOnlyContinuation*` instead of forcing callers to infer those consequences from the enum values alone
- the allocator helper decodes ABI allocator-mode bytes explicitly, names caller-prepared versus helper-owned init flow through `InitFlow`, and rejects nonzero reserved bytes so shared callers do not have to rediscover caller ownership, helper-owned initialization, owned-state setup, global fallback, or arena-reset policy elsewhere in the packet
- the helper-local unsafe-policy relay now keeps the unsafe capability split explicit through `AccessBoundary`, `permitsNoUnsafe*`, `permitsVolatileMmio*`, and `permitsRawPointerBridge*`, while the narrow decoder owns the bounded raw-pointer bridge entrypoints and fail-closed denial paths without implying a broader helper-owned pointer facade
- the MMIO helper routes policy-aware reads and writes through explicit byte and typed `InteropPolicy` relays while keeping denied-scope accesses fail-closed instead of spreading that contract across unrelated callers
- the layout helper now keeps the canonical starter layouts, the notifier block, notifier priority-increase, malformed list-link layouts, the chrdev budget-window delivery-window layouts, and the interop plus notifier-result values explicit again, while the helper-local policy starter packet, direct starter packet test route, focused policy dump route, and directly coupled low-level-wrapper packet own the live replay and survey evidence
- there is no remaining packet-local substrate regression in this narrow helper lane; the same-lane follow-through is now the dedicated `scripts/zigux/validate-phase3-policy-unsafe-survey.py` blob-marker guard plus keeping this survey aligned if the helper-local policy starter packet, focused policy dump route, or directly coupled low-level-wrapper packet drifts again
## Next Bounded Step
- leave this lane parked unless `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, or `scripts/zigux/validate-phase3-policy-unsafe-survey.py` drifts again from this survey
- keep the next same-lane change to one packet-local note refresh or one validator-wording refresh tied only to this unsafe substrate slice and its dedicated blob-marker guard
- treat `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `scripts/zigux/validate-phase3.py` as adjacent or absent shared surfaces rather than parking triggers for this unsafe survey
- if the helper-local policy starter packet, focused policy dump route, directly coupled low-level-wrapper replay, either dedicated survey check, or any listed blob marker changes later, resurvey this note against the exact live files before claiming that surface here