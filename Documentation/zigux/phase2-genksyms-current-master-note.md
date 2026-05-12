# Phase 2 genksyms current-master note

This note records the bounded current-master `genksyms` bridge evidence so follow-up work stays anchored to the live Zigux tree instead of older dual-implementation expectations.

## Current repo evidence

- `scripts/zigux/README.md` names the live shared Phase 2 scripts-root helpers and says the broader `genksyms` checker packet should stay documented through reminder surfaces instead of being treated as shipped current-master tooling.
- `zigux/tests/fixtures/phase2_tool_manifest.json` still keeps `genksyms_bridge` inside the shared Phase 2 family list.
- `zigux/tests/fixtures/genksyms_bridge/` currently shows committed expected-output shard files such as `abbreviated_long_options_expected.json`, `explicit_option_terminator_expected.json`, `lone_dash_passthrough_expected.json`, and `positional_passthrough_expected.json`.
- current `master` does not materialize `scripts/zigux/genksyms.zig` or `scripts/zigux/check-genksyms-bridge.py`, so reminder surfaces should describe a fixture-backed bridge packet rather than a shipped direct replay.

## Bounded correction

- treat the current Phase 2 `genksyms` bridge packet as a fixture-backed closure surface until a real direct replay and checker land again.
- the next honest tool-only follow-up is to replace any remaining reviewer-facing or tests-root wording that still names `scripts/zigux/genksyms.zig` or `scripts/zigux/check-genksyms-bridge.py` as shipped current-master evidence.
