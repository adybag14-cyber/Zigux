# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` already carries the newer bounded `fixdep` packet.

## Current repo evidence

- `scripts/zigux/check-fixdep-diff.py` validates the live ten-case packet, including `sample_escaped_colon`, `sample_concatenated`, `sample_comment_only_stdout_full`, `sample_missing_dep_stdout_full`, and `sample_output_write`.
- `zigux/tests/fixtures/fixdep/cases.json` names that same ten-case packet and uses `stdout_mode: "dev_full"` on the three bounded `/dev/full` write-failure replays.
- `Documentation/zigux/artifact-diff.md` and `Documentation/zigux/phase2-closure.md` both describe the same ten-case artifact packet on current `master`.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.

## Bounded drift

- `scripts/zigux/check-phase2-fixdep-gate.py` still expects the older `Documentation/zigux/artifact-diff.md` wording for `sample_escaped_hash_comment_chain_expected.txt` and a seven-case packet.
- That makes the dedicated shared `fixdep` gate stale against the live docs-and-fixtures packet even though the broader `fixdep` closure surfaces already agree with each other.

## Next safe step

1. Update only `ARTIFACT_DIFF_MARKERS` in `scripts/zigux/check-phase2-fixdep-gate.py` so they match the live `artifact-diff.md` wording for `sample_concatenated_expected.txt`, `sample_output_write_expected.txt`, and the current ten-case `cases.json` packet.
2. Re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test` and `python3 scripts/zigux/check-phase2-fixdep-gate.py`.
3. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen parser behavior in `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet while correcting this drift.
