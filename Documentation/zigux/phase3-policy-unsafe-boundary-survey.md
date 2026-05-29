# Phase 3 Policy and Unsafe Boundary Survey
This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status
- `PHASE3_SURVEY_PROVENANCE=connector-current-head-sha-unavailable-in-run`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-notifier-list-and-chrdev-layout-asserts-consumed-by-both-the-shared-abi-replays-and-the-focused-policy-starter-packet`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=2b17f9d48cfe4f3a6b22bd0aafed4fb614c3b20e`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-plus-escalation-and-byte-decoders`
- `PHASE3_PANIC_POLICY_BLOB_SHA=f4f3377fd3a467113cf06db6758535f62e91b8e5`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-plus-init-flow-owned-state-and-reset-gates`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=852cd5edc75a4b83cc7f9cbda70136c37e96c909`
- `PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig`
- `PHASE3_UNSAFE_POLICY_SCOPE=helper-local-unsafe-scope-relay-over-the-shared-narrow-decoder-plus-access-boundary-surface-and-permit-audit-aliases`
- `PHASE3_UNSAFE_POLICY_BLOB_SHA=131221814ce388037afa658d0d6903d4319c4e4a`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=b8986ad267a8fe9cbcea57ee8a7a610a2c7c3195`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge-with-explicit-audit-gates`
- `PHASE3_UNSAFE_BLOB_SHA=0a2bfa31a3fc061f9ec24bc0975cde8ce41e1f62`
- `PHASE3_POLICY_SLICE_DOC_BLOB_SHA=07a0a34ed9b2d5b1794862a441e540c82302faf3`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA=53a1da8b3bccbd08cb5232178ec14e436b0eaa88`
- `PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json`
- `PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `PHASE3_POLICY_PACKET_TEST_GATE=zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig`
- `PHASE3_POLICY_PACKET_MAKE_GATE=make -C zigux phase3-policy-starter-packet-test`
- `PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py`
- `PHASE3_POLICY_DUMP_MAKE_GATE=make -C zigux phase3-policy-dump`
- `PHASE3_POLICY_UNSAFE_REPLAY_GATE=python3 scripts/zigux/check-phase3-policy-unsafe-replay.py`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_POLICY_UNSAFE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `PHASE3_POLICY_UNSAFE_REPLAY_PATH=zigux/tests/phase3_policy_unsafe.zig`
- `PHASE3_POLICY_UNSAFE_REPLAY_BUILD_PATH=zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_POLICY_UNSAFE_REPLAY_TEST_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_POLICY_UNSAFE_REPLAY_MAKE_GATE=make -C zigux phase3-policy-unsafe-test`
- `PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-further-policy-unsafe-gap-beyond-keeping-the-helper-local-packet-dedicated-replay-pair-and-the-directly-coupled-low-level-wrapper-packet-aligned`
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

The live bounded packet is currently split across four directly coupled proof surfaces:
- `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/mmio.zig`, and `zigux/unsafe/narrow.zig`, which keep layout, panic, allocator, unsafe-scope, MMIO, and raw-pointer-bridge policy explicit in helper-local code.
- `Documentation/zigux/phase3-policy-slice.md`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `scripts/zigux/check-phase3-policy-starter-packet.py`, and `zigux/tests/phase3_policy_starter_packet_build.zig`, which keep the helper-local starter packet reviewable through the direct starter-packet route and its `make -C zigux phase3-policy-starter-packet-test` wrapper.
- `zigux/tests/phase3_policy_unsafe.zig`, `zigux/tests/phase3_policy_unsafe_build.zig`, and `scripts/zigux/check-phase3-policy-unsafe-replay.py`, which now provide a dedicated replay pair and packet-local checker for shared interop-policy records, helper-versus-narrow gate alignment, fail-closed require paths, and the resulting panic, allocator, and unsafe-surface consequences without reopening the starter packet or low-level wrapper packet.
- `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, `scripts/zigux/check-phase3-policy-dump.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig`, which keep the focused dump replay and the directly coupled MMIO-plus-narrow wrapper packet explicit beside the dedicated survey guard.

Current `master` also keeps `zigux/Makefile` plus `.github/workflows/zigux-bootstrap.yml` explicit with both the direct `zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig` replay and the returned `make -C zigux phase3-policy-unsafe-test` wrapper, so this survey should treat those support routes as current bounded packet evidence rather than leaving the dedicated policy-unsafe replay implicit behind the Zig-only route.

This note should stay tied to those current packet-local surfaces instead of using `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, or `scripts/zigux/validate-phase3.py` as its parking trigger.

## Ledger Alignment
This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`. That means this lane remains survey-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.

## Current Boundary Gap
There is no remaining packet-local product gap to open inside this lane today. The live need is truthfulness and alignment:
- keep the helper-local policy slice, dedicated `phase3_policy_unsafe` replay pair, packet-local replay checker, focused policy dump route, directly coupled low-level-wrapper packet, returned `make -C zigux phase3-policy-unsafe-test` wrapper, and workflow-backed replay route describing the same shipped surface
- keep the survey validator tracking the files and support routes that now form the real bounded packet
- avoid claiming that the older shared-ABI reminder path is still the only proof route when current `master` already ships a dedicated replay pair with direct, make-backed, and workflow-backed evidence

## Next Bounded Step
- leave this lane parked unless `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_policy_unsafe.zig`, `zigux/tests/phase3_policy_unsafe_build.zig`, `scripts/zigux/check-phase3-policy-unsafe-replay.py`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, or `scripts/zigux/validate-phase3-policy-unsafe-survey.py` drifts again from this survey
- keep the next same-lane change to one packet-local note refresh or one validator-wording refresh tied only to this unsafe substrate slice and its dedicated blob-marker guard
- treat `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `scripts/zigux/validate-phase3.py` as adjacent shared surfaces rather than parking triggers for this unsafe survey
- if the helper-local policy starter packet, dedicated policy-unsafe replay pair, focused policy dump route, directly coupled low-level-wrapper replay, returned `make -C zigux phase3-policy-unsafe-test` wrapper, workflow-backed replay route, either dedicated survey check, or any listed blob marker changes later, resurvey this note against the exact live files before claiming that surface here