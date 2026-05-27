# Phase 2 Closure Validator Process-Output Gap

This note records the current Lane 22 truthfulness gap between the live
genksyms manifest packet and the narrower process-output packet still embedded
in `scripts/zigux/validate-phase2-closure.py` on current `master`.

## Current Live Packet

- authority packet:
  - `zigux/tests/fixtures/genksyms_bridge/manifest.json`
  - `scripts/zigux/validate-phase2-closure.py`
  - `Documentation/zigux/phase2-closure.md`
- manifest-backed process-output packet count: `10`
- closure-validator process-output packet count: `9`

## Current Mismatch

- `zigux/tests/fixtures/genksyms_bridge/manifest.json` includes:
  - `abbreviated_unexpected_long_help_argument_expected.json`
- `scripts/zigux/validate-phase2-closure.py` currently omits:
  - `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`
- `Documentation/zigux/phase2-closure.md` still omits the same fixture from the
  closure-side process-output roster.

## Why This Matters

- the current validator packet can drift behind the live manifest-backed fixture
  roster without an explicit shared reminder surface calling that out
- future Lane 22 or Lane 24 follow-through needs one direct place to confirm
  that the omission is known current-master state rather than a silently missed
  packet member

## Next Safe Step

- restack `scripts/zigux/validate-phase2-closure.py` so
  `GENKSYMS_PROCESS_OUTPUT_RELS`, `EXPECTED_MANIFEST_FIXTURE_ROSTER`, and
  `EXPECTED_GENKSYMS_MANIFEST["process_output_packet"]` all include
  `abbreviated_unexpected_long_help_argument_expected.json`
- then restack the paired closure-side reminder surface in
  `Documentation/zigux/phase2-closure.md` if that file still lags the widened
  validator packet on the then-current `master` head
