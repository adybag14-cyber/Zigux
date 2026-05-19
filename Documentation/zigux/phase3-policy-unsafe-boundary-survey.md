# Phase 3 Policy and Unsafe Boundary Survey
This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.
## Status
- `PHASE3_SURVEY_PROVENANCE=connector-current-head-sha-unavailable-in-run`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-byte-and-field-asserts-consumed-by-shared-abi-replays`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=6a64770f7b801c063ebf72348ca140b44f8e1080`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-plus-escalation-and-byte-decoders`
- `PHASE3_PANIC_POLICY_BLOB_SHA=d05afcf0c0ef4e5558f8d8094bedf831c413407c`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-plus-init-flow-owned-state-and-reset-gates`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=01a6b30ab444a9b6be66eb1fb3a0e3666f55863a`
- `PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig`
- `PHASE3_UNSAFE_POLICY_SCOPE=helper-local-unsafe-scope-decoder-plus-permits-and-audit-aliases`
- `PHASE3_UNSAFE_POLICY_BLOB_SHA=7598cfcfb87a863dd40d60e5150fa8493d1dc8ed`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=140c792c323eaa69b9ceb6eb9e7e0ecf93f4cb23`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge-with-explicit-audit-gates`
- `PHASE3_UNSAFE_BLOB_SHA=0ce01e9d472d0a3ce651808dacb0219a225b4012`
- `PHASE3_POLICY_SLICE_DOC_BLOB_SHA=fefaca671e37ade8a5cc3aae3b843d858c7001b1`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA=e38183c47ceca74e307bba8293e8edc649ece057`
- `PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json`
- `PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-helper-local-policy-slice-and-the-directly-coupled-low-level-wrapper-packet`
- `PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-the-helper-local-policy-slice-or-the-directly-coupled-low-level-wrapper-survey-drifts-again`
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
The current tree still carries a real bounded policy-and-unsafe packet, but the live proof surface has split into a helper-local policy slice plus a directly coupled low-level-wrapper packet rather than the older shared-ABI-only reminder route:
- `zigux/helpers/layout_assert.zig` is still a small generic helper, but it now centralizes compile-time layout checks for `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` plus the current panic, allocator, and unsafe-scope byte values, and it now also keeps the current chrdev notify ack-window policy budget-window delivery-window view, summary, budget-view, and budget-summary layouts explicit so those ABI structs no longer live only in the shared replays.
- `zigux/helpers/panic_policy.zig` now keeps panic escalation explicit through `Escalation`, `escalationFor`, `causesImmediateHalt`, `emitsKernelBug`, and `permitsWarningOnlyContinuation`, while still rejecting unknown panic modes and nonzero reserved bytes through `modeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, and the paired `*PolicyBytes`, `*InteropPolicy`, and `*Byte` relays before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/helpers/allocator_policy.zig` keeps allocator mode, init ownership, owned-state setup, and reset requirements explicit through `InitFlow`, `initFlowFor`, `modeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `permitsGlobalFallbackPolicyBytes`, `initializesOwnedStatePolicyBytes`, and `requiresResetOnInitPolicyBytes` so unknown allocator modes, helper-owned initialization, arena reset requirements, and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.
- `zigux/helpers/unsafe_policy.zig` is now the helper-local unsafe-scope decoder that keeps the unsafe capability split explicit through `AccessBoundary`, `accessBoundaryFor`, `permitsNoUnsafe`, `requiresDedicatedAudit`, `permitsVolatileMmio`, and `permitsRawPointerBridge`, including the newer scope and permits symmetry aliases that the helper-local policy starter packet and focused policy dump route both read back directly.
- `zigux/unsafe/narrow.zig` now keeps the raw-pointer bridge deliberately small and reviewable through `Surface`, `surfaceFor`, `isUnsafe`, `requiresDedicatedAudit`, `requireRawPointerBridgePolicyBytes`, `pointerAtInteropPolicyBytes`, `sliceAtInteropPolicyBytes`, `writeValueAtInteropPolicyBytes`, and the paired typed and raw-byte relays plus denial-path tests, while remaining a directly coupled narrow decoder rather than the sole proof route for the broader policy packet.
- `zigux/helpers/mmio.zig` keeps volatile register access explicit through `read`, `write`, `exchange`, and `writeMasked`, and it now gates typed and byte-policy MMIO access through `zigux/helpers/unsafe_policy.zig` via `readScoped`, `writeScoped`, `exchangeScoped`, `writeMaskedScoped`, `readInteropPolicy`, `writeInteropPolicy`, `exchangeInteropPolicy`, `writeMaskedInteropPolicy`, and the paired `*InteropPolicyBytes` relays so volatile-MMIO callers stay inside the bounded unsafe contract.
- `Documentation/zigux/phase3-policy-slice.md`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts/zigux/check-phase3-policy-dump.py` now keep the helper-local panic, allocator, and unsafe-policy decoders reviewable as one bounded packet through both the starter manifest route and the focused policy dump route.
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` keep the directly coupled MMIO-plus-narrow wrapper packet explicit without implying broader Phase 3 completion.
The current tree still does not ship a dedicated `phase3_policy_unsafe` replay pair, but the live proof is no longer shared-ABI-slice-only. It is split between the helper-local policy starter packet, the focused policy dump route, and the directly coupled low-level-wrapper packet. This note should stay tied to those current packet-local surfaces instead of using `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, or `scripts/zigux/validate-phase3.py` as its parking trigger.
## Ledger Alignment
This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`. That means this lane remains survey-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.
## Current Boundary Gap
Current same-family progress already includes helper-local explicit-byte decoding, explicit allocator init-flow reviewability, typed-policy relays, explicit panic escalation reviewability, explicit unsafe audit gates, the focused policy dump route, and the restored raw-pointer bridge helper family:
- the panic helper now names the escalation outcome through `Escalation` and keeps the typed, raw-byte, and `InteropPolicy` panic decisions aligned through `causesImmediateHalt*`, `emitsKernelBug*`, and `permitsWarningOnlyContinuation*` instead of forcing callers to infer those consequences from the enum values alone
- the allocator helper decodes ABI allocator-mode bytes explicitly, names caller-prepared versus helper-owned init flow through `InitFlow`, and rejects nonzero reserved bytes so shared callers do not have to rediscover caller ownership, helper-owned initialization, owned-state setup, global fallback, or arena-reset policy elsewhere in the packet
- the helper-local unsafe decoder keeps the unsafe capability split explicit through `AccessBoundary`, `permitsNoUnsafe*`, `permitsVolatileMmio*`, and `permitsRawPointerBridge*`, while the narrow decoder now restores the bounded raw-pointer bridge entrypoints and fail-closed denial paths without implying a broader helper-owned pointer facade
- the MMIO helper routes policy-aware reads and writes through explicit byte and typed `InteropPolicy` relays while keeping denied-scope accesses fail-closed instead of spreading that contract across unrelated callers
- the layout helper now keeps the canonical starter layouts, the chrdev budget-window delivery-window layouts, and the interop byte values explicit again, while the helper-local policy starter packet, focused policy dump route, and directly coupled low-level-wrapper packet own the live replay and survey evidence
- there is no remaining packet-local substrate regression in this narrow helper lane; the same-lane follow-through is only to keep this survey aligned if the helper-local policy starter packet, focused policy dump route, or directly coupled low-level-wrapper packet drifts again
## Next Bounded Step
- leave this lane parked unless `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/mmio.zig`, or `zigux/unsafe/narrow.zig` drifts again from this survey
- keep the next same-lane change to one packet-local note refresh or one validator-wording refresh tied only to this unsafe substrate slice
- treat `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `scripts/zigux/validate-phase3.py` as adjacent or absent shared surfaces rather than parking triggers for this unsafe survey
- if the helper-local policy starter packet, focused policy dump route, directly coupled low-level-wrapper replay, or either dedicated survey check changes later, resurvey this note against the exact live files before claiming that surface here
