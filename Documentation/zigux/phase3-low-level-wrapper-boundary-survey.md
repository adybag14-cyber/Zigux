# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current atomic, barrier, MMIO, and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-nand-fetch-min-fetch-max-compare-exchange-compare-exchange-weak`
- `PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed`
- `PHASE3_ATOMIC_BLOB_SHA=70c698b99a2282aa3c394431a0a786762725a134`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair`
- `PHASE3_BARRIER_STATUS=local-caller-state-and-handoff-probes-landed`
- `PHASE3_BARRIER_BLOB_SHA=782616269d5003960cf3f6b7ef2a3ce502ddb3ed`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=range-range-interop-policy-byte-read8-write8-read16-write16-read32-write32-read64-write64`
- `PHASE3_MMIO_STATUS=byte-16-bit-32-bit-and-64-bit-mmio-through-narrow-pointer-bridge`
- `PHASE3_MMIO_BLOB_SHA=1fbf2e247fb62987644e52ac8888ac278ca4c225`
- `PHASE3_NARROW_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_NARROW_UNSAFE_SCOPE=address-byte-offset-align1-pointer-slice-const-pointer-write-and-interop-policy-unsafe-scope-byte-decoders`
- `PHASE3_NARROW_UNSAFE_STATUS=align1-raw-pointer-bridge-plus-explicit-unsafe-scope-byte-policy`
- `PHASE3_NARROW_UNSAFE_BLOB_SHA=62633e99b42c92d95a6e582df92fce6e8b0fb9cb`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_TEST_SCOPE=focused-atomic-barrier-mmio-replay-plus-signed-atomic-edges-acq-rel-strong-compare-exchange-mismatch-barrier-locality-barrier-acquire-release-handoff-non-seq-cst-ordering-byte-scoped-mmio-range-raw-pointer-bridge-policy-gates-and-byte-16-bit-32-bit-and-64-bit-mmio-range-replay`
- `PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface-and-barrier-handoff`
- `PHASE3_LOW_LEVEL_TEST_BLOB_SHA=ea47ed7408b5481604eeeb3c4d6bd9de5f13082c`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b`
- `PHASE3_ABI_EXPECTED_BLOB_SHA=6e0dae21e5811aedabe51370de1c16a104636d7d`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=d0fb9cad4d58308f09d74db641872d54e81c30a0`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=635507800ae7f50dcdc1d0f98b61c9254a5b9efc`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_BOUNDARY_SCOPE=focused-low-level-replay-plus-shared-abi-compile-layout-dump-packet`
- `PHASE3_BOUNDARY_GAP=focused-low-level-replay-now-covers-signed-fetch-and-min-max-edges-plus-monotonic-and-acq-rel-strong-compare-exchange-mismatch-non-seq-cst-ordering-byte-scoped-mmio-range-raw-pointer-bridge-policy-gates-byte-16-bit-32-bit-and-64-bit-mmio-range-direct-barrier-locality-and-barrier-acquire-release-handoff-while-shared-abi-packet-still-carries-the-broader-compile-layout-and-dump-proof`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-the-focused-replay-and-the-shared-abi-packet-aligned-when-helper-surface-moves`

## Roadmap Contract

Phase 3 is where Zigux starts defining the permanent C and Zigux boundary instead of only helper scaffolding.

For this lane, the roadmap requirements are still narrow:

- approved atomic, barrier, and MMIO wrappers
- explicit narrow-unsafe review instead of hidden raw-pointer expansion
- compile, layout, dump, and focused replay evidence that tells reviewers exactly how much of the low-level wrapper family is actually proven on current `master`

That still does not require a broad kernel-style low-level helper family. It does require the repo to say clearly which low-level wrappers are already shipped, which focused replay is real, which helper-local MMIO policy gates are explicit, which narrow-unsafe bridge is actually pinned, and which broader proof still comes from the shared ABI packet.

## Live Repo Reality

This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for this directly coupled low-level wrapper packet.

The current tree carries a real low-level wrapper packet:

- `zigux/helpers/atomic.zig` exposes `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchNand`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`, with helper-local tests still carrying a few atomic edge cases beyond the focused replay.
- `zigux/helpers/barrier.zig` exposes `acquire`, `release`, `full`, and `acquireRelease()` through local compiler-barrier wrappers, with helper-local caller-state and acquire-release handoff probes while direct locality proof now also appears in the focused replay.
- `zigux/helpers/mmio.zig` exposes `range`, `allowsInteropPolicyBytes`, `allowsInteropPolicy`, `requireInteropPolicyBytes`, `requireInteropPolicy`, `rangeInteropPolicyBytes`, `rangeInteropPolicy`, `rangeInteropPolicyByte`, direct `read*` and `write*` accessors, and policy-gated `read*InteropPolicy*` and `write*InteropPolicy*` relays, all routed through the narrow pointer bridge in `zigux/unsafe/narrow.zig`, with helper-local tests keeping the explicit MMIO interop-policy byte and typed policy gates, the byte-scoped and typed `range*InteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*` relays, and the struct gates reviewable beside the focused raw-access and policy-gated replay.
- `zigux/unsafe/narrow.zig` exposes `addressOf`, `byteOffset`, `pointerAt`, `constSliceAt`, `constPointerAt`, and `writeValueAt`, with the explicit unsafe-scope decoders `scopeFromInteropPolicyBytes`, `scopeFromInteropPolicy`, `scopeFromByte`, `recognizes*`, and `permits*`, with helper-local tests keeping the raw-pointer bridge plus the interop-policy unsafe-scope bytes reviewable beside the focused MMIO replay.
- `zigux/tests/phase3_low_level_wrappers.zig` now directly proves the shipped helper surface, including `fetchNand`, signed atomic arithmetic and min/max edges, monotonic strong `compareExchange()`, `acq_rel` strong `compareExchange()` mismatch handling, weak compare-exchange coverage, explicit barrier-locality and acquire-release handoff replay, the typed `rangeInteropPolicy` helper, the byte-scoped `rangeInteropPolicyByte` helper, positive typed `write8InteropPolicy` and `read8InteropPolicy`, `write16InteropPolicy` and `read16InteropPolicy`, `write32InteropPolicy` and `read32InteropPolicy`, and `write64InteropPolicy` and `read64InteropPolicy` MMIO policy relays, positive `write8InteropPolicyBytes` and `read8InteropPolicyBytes` plus `write32InteropPolicyByte` and `read32InteropPolicyByte` byte-scoped MMIO policy relays, the denial paths for `rangeInteropPolicy`, `rangeInteropPolicyByte`, `read32InteropPolicy`, `write16InteropPolicy`, `read8InteropPolicyBytes`, `read32InteropPolicyByte`, `write32InteropPolicyByte`, and `write64InteropPolicyBytes`, the raw-pointer-bridge policy gate replay, non-`seq_cst` ordering, plus byte-addressed 16-bit, 32-bit, and 64-bit MMIO range descriptors and odd-offset MMIO behavior.
- The shared compile, layout, and dump proof for this packet still lives in `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/expected.json`, and `zigux/tests/fixtures/phase3_abi_manifest.json`.

## Ledger Alignment

This low-level wrapper packet still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That keeps this lane inside shared-packet survey and validator maintenance rather than a new helper tranche.

## Current Boundary Gap

The live gap is no longer helper absence and it is no longer the absence of a dedicated replay.

The current reviewability gap is narrower:

- the helper files already ship the bounded atomic, barrier, MMIO, and narrow-unsafe surface listed above
- the repo now has a dedicated focused replay for the shipped low-level helper operations in `zigux/tests/phase3_low_level_wrappers.zig`
- the repo also has helper-local tests in `zigux/unsafe/narrow.zig` and `zigux/helpers/mmio.zig` that keep the raw-pointer bridge plus the explicit MMIO interop-policy byte, typed policy gates, typed range, read, and write relays, and struct gates reviewable where those narrower unsafe and policy surfaces actually live
- the focused replay now covers `fetchNand`, signed `fetchAdd` and `fetchSub`, signed `fetchMin` and `fetchMax`, monotonic strong `compareExchange()`, `acq_rel` strong `compareExchange()` mismatch handling, the typed `rangeInteropPolicy` helper, the byte-scoped `rangeInteropPolicyByte` helper, positive typed `write8InteropPolicy` and `read8InteropPolicy`, `write16InteropPolicy` and `read16InteropPolicy`, `write32InteropPolicy` and `read32InteropPolicy`, and `write64InteropPolicy` and `read64InteropPolicy` MMIO policy relays, positive `write8InteropPolicyBytes` and `read8InteropPolicyBytes` plus `write32InteropPolicyByte` and `read32InteropPolicyByte` byte-scoped MMIO policy relays, the denial paths for `rangeInteropPolicy`, `rangeInteropPolicyByte`, `read32InteropPolicy`, `write16InteropPolicy`, `read8InteropPolicyBytes`, `read32InteropPolicyByte`, `write32InteropPolicyByte`, and `write64InteropPolicyBytes`, the raw-pointer-bridge pointer, slice, const-pointer, and write relays plus their denial paths, byte/16-bit/32-bit/64-bit MMIO range descriptors, non-`seq_cst` atomic orderings, direct barrier-locality proof, direct barrier acquire-release handoff proof, and the byte-addressed alignment handoff for odd-offset 16-bit, 32-bit, and 64-bit MMIO
- the shared ABI packet remains the broader compile, layout, and dump proof surface for this family

That repo reality still fits the roadmap's wrapper-first posture, but it also means this survey needs to keep the widened focused replay, the helper-local MMIO policy gates, and the narrow-unsafe bridge explicit instead of letting that evidence collapse back into generic MMIO prose.

## Next Bounded Step

- leave this lane parked unless one of the directly coupled helper files, the focused replay, or the shared ABI proof files moves again
- if the helper surface grows, refresh both this survey and the dedicated replay before claiming broader closure
- keep any follow-up inside the same replay-or-validator packet unless a separate lane explicitly opens low-level wrapper implementation work
