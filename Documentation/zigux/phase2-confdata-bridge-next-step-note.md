# Phase 2 Confdata Bridge Next Step Note

`scripts/zigux/kconfig/confdata_bridge.zig` is already in a closed and internally aligned state on current `master`.

Current bridge evidence:
- `scripts/zigux/kconfig/confdata_bridge.zig` carries the current helper-local anchor packet, including the shared fixture-backed behaviors plus bridge-local unit checks for malformed quoted values, empty symbol output suppression, duplicate assignment overwrite, and last-state wins across unset/set transitions.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` still defines the current `11` shared `confdata_cases` replay packet only.
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, `scripts/zigux/check-kconfig-bridge.py`, and `scripts/zigux/validate-phase2-closure.py` all agree on that same `11`-case fixture packet and keep the broader helper-local anchor list explicit.
- `Documentation/zigux/phase2-closure.md` already describes the live `11-case` `confdata` packet as the current bounded closure surface.

Bounded next safe step for this bridge only:
- If `confdata_bridge.zig` needs to reopen, do not widen the parser surface generically.
- Promote exactly one already-landed helper-local invariant into the shared fixture packet by adding one new `confdata_cases` entry plus its paired `*_expected.json` output and then realigning only the `confdata` manifest/checker counts for that single behavior.
- The safest first candidates are the already-landed unit-test-only behaviors around malformed quoted values, duplicate symbol last-write-wins handling, or unset-to-set transition last-state handling.

This keeps the lane inside `confdata_bridge.zig` and turns any future reopen into a single replay-backed closure step instead of broader Phase 2 churn.
