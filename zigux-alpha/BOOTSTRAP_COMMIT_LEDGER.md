# Zigux Alpha Bootstrap Commit Ledger

This ledger turns the roadmap into the first product commit train.

## Commit Train

1. `docs(zigux-alpha): establish roadmap and folder charter`
- `zigux-alpha/README.md`
- `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

2. `docs(zigux): add documentation root, review checklist, and freeze map`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md`

3. `build(scripts/zigux): add bootstrap validation and toolchain checks`
- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/validate-bootstrap.py`

4. `test(zigux): establish differential-test root`
- `zigux/tests/README.md`

5. `ci(zigux): add bootstrap workflow`
- `.github/workflows/zigux-bootstrap.yml`

6. `feat(tools/lib): start phase-1 helper ports`
- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`

7. `test(zigux): add phase-1 helper harness and workflow gate`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/build.zig`
- `scripts/zigux/validate-phase1.py`
- `.github/workflows/zigux-bootstrap.yml`

8. `feat(tools/lib): expand phase-1 helper batch`
- `tools/lib/argv_split.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/hweight.zig`

9. `test(zigux): add phase-1 golden parity fixtures and artifact diff gate`
- `scripts/zigux/artifact_diff.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`
- `.github/workflows/zigux-bootstrap.yml`
