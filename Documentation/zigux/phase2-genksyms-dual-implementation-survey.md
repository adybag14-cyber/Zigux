# Phase 2 Genksyms Dual-Implementation Survey

This note records the current roadmap-versus-repo state for the bounded Phase 2 `genksyms` lane.

## Roadmap anchor

Phase 2 names `scripts/genksyms/genksyms.c` as a primary Linux target and requires:

- selected dual implementations
- a wrapper-first path for parser-heavy tooling
- deterministic artifact checks

For `genksyms`, that means the live Zigux lane should stay reviewable as a bounded CLI and bridge packet until a later roadmap-backed step explicitly widens the scope.

## Current live packet

Current `master` does ship a real bounded `genksyms` packet:

- `scripts/zigux/genksyms.zig` parses the bounded command-line surface and emits a normalized bridge JSON plan for `scripts/genksyms/genksyms`
- `scripts/zigux/check-genksyms-bridge.py` replays the bounded C harness and Zig bridge twice, compares artifacts, and records `GENKSYMS_BRIDGE_DETERMINISM=pass`
- `scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py` keeps the checker, scripts index, closure note, validators, workflow route, Makefile route, and fixture packet aligned
- `zigux/tests/fixtures/genksyms_bridge/cases.json` currently carries a committed 26-case bridge packet covering clustered short flags, abbreviated long options, lone-dash passthrough, explicit terminators, missing short and long option arguments, stderr-normalized failure cases, and the bounded reference-file limit

That is real progress, and it matches the roadmap's wrapper-first requirement better than a speculative parser port would.

## Remaining bounded gaps

This packet is still intentionally smaller than full `scripts/genksyms/genksyms.c` parity.

What is already proved:

- bounded getopt-style CLI normalization
- bridge JSON stability
- repeat-run determinism for the bounded bridge packet
- coupled validator, Makefile, workflow, and closure-note coverage for the 26 committed bridge cases

What is not yet proved and should still be treated as C-owned:

- parsing of the C preprocessor token stream from stdin
- symbol-definition expansion and `.tmp_obj.ver` semantic parity
- the deeper parser and output behavior behind the native Linux tool

One narrower reviewability gap still remains inside the bounded wrapper packet itself:

- the usage banner in `scripts/zigux/genksyms.zig` preserves the broader Linux wording `[-adDTwqhVR]`, but the committed bounded bridge packet does not yet carry dedicated proof for `-a` or `-R`
- until a later bounded lane resolves that mismatch, reviewers should treat those flags as outside the proved Phase 2 bridge packet even though the help text still mirrors the Linux banner

## Recommended next bounded step

If the `genksyms` parser lane reopens, keep it small:

- either add explicit bounded review cases for the still-unproved `-a` and `-R` help-banner surface
- or trim the bridge banner to the actually proved wrapper scope

Do not treat either option as permission to claim full parser parity. The roadmap still says wrapper-first here, and the Linux C tool remains authoritative for parser-heavy behavior.
