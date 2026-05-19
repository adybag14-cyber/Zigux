#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_LINES = (
    "# Zigux Alpha Bootstrap Commit Ledger",
    "This ledger turns the roadmap into the first product commit train.",
    "## Commit Train",
    "1. `docs(zigux-alpha): establish roadmap and folder charter`",
    "2. `docs(zigux): add documentation root, review checklist, and freeze map`",
    "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
    "4. `test(zigux): establish differential-test root`",
    "5. `ci(zigux): add bootstrap workflow`",
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "## Scope Note",
    "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
)

EXPECTED_COMMIT_NUMBERS = tuple(range(1, 26))


def collect_failures(root: Path) -> list[str]:
    ledger = (root / LEDGER_PATH).read_text(encoding="utf-8")
    failures: list[str] = []

    for line in REQUIRED_LINES:
        if line not in ledger:
            failures.append(f"missing:{line}")

    found_numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\. `", ledger, flags=re.MULTILINE)]
    if found_numbers != list(EXPECTED_COMMIT_NUMBERS):
        failures.append(
            "commit-train:"
            f"expected {list(EXPECTED_COMMIT_NUMBERS)} got {found_numbers}"
        )

    if ledger.count("## Scope Note") != 1:
        failures.append(f"scope-note-count:expected 1 got {ledger.count('## Scope Note')}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_ledger() -> str:
    return """# Zigux Alpha Bootstrap Commit Ledger

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

7. `test(zigux): add phase-1 helper harness and workflow gate`
- `zigux/tests/phase1_helpers.zig`

8. `feat(tools/lib): expand phase-1 helper batch`
- `tools/lib/argv_split.zig`

9. `test(zigux): add phase-1 golden parity fixtures and artifact diff gate`
- `scripts/zigux/artifact_diff.py`

10. `feat(tools/lib): add phase-1 memory and formatting helper ports`
- `tools/lib/slab.zig`

11. `feat(scripts/zigux): add bounded Phase 2 fixdep dual-implementation lane`
- `scripts/zigux/fixdep.zig`

12. `feat(tools/lib): complete bounded phase-1 helper coverage`
- `tools/lib/list_sort.zig`

13. `test(zigux): widen bounded fixdep parity fixtures`
- `zigux/tests/fixtures/fixdep/cases.json`

14. `feat(scripts/zigux): add bounded Phase 2 mk_elfconfig lane`
- `scripts/zigux/mk_elfconfig.zig`

15. `docs(zigux): close bounded phase-1 helper tranche`
- `Documentation/zigux/phase1-closure.md`

16. `test(zigux): harden phase-1 closure gates`
- `scripts/zigux/check-phase1-bench.py`

17. `ci(zigux): harden phase-1 closure workflow viability`
- `.github/workflows/zigux-bootstrap.yml`

18. `build(zigux): remove node-20-bound Zig action from phase-1 closure path`
- `scripts/zigux/install-zig.py`

19. `feat(scripts/zigux): start bounded Phase 2 genksyms lane`
- `scripts/zigux/genksyms_crc.zig`

20. `feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding`
- `scripts/zigux/kconfig/conf_bridge.zig`

21. `ci(zigux): add Phase 2 cross-arch build matrix`
- `scripts/zigux/check-phase2-cross.py`

22. `docs(zigux): close bounded Phase 2 toolchain tranche`
- `Documentation/zigux/phase2-closure.md`

23. `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane`
- `scripts/zigux/genksyms.zig`

24. `ci(zigux): widen Phase 2 closure matrix`
- `.github/workflows/zigux-bootstrap.yml`

25. `docs(zigux): reopen and close broadened Phase 2 tranche`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/artifact-diff.md`
- `scripts/zigux/README.md`
- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_ledger_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / LEDGER_PATH, _sample_ledger())

        if collect_failures(root):
            raise AssertionError("baseline ledger fixture should pass")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "25. `docs(zigux): reopen and close broadened Phase 2 tranche`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if "missing:25. `docs(zigux): reopen and close broadened Phase 2 tranche`" not in failures:
            raise AssertionError(f"missing commit 25 marker not reported: {failures}")
        if not any(item.startswith("commit-train:") for item in failures):
            raise AssertionError(f"commit-train drift not reported: {failures}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`\n",
                "4. `build(scripts/zigux): add bootstrap validation and toolchain checks`\n",
                1,
            ),
        )
        failures = collect_failures(root)
        if not any(item.startswith("commit-train:") for item in failures):
            raise AssertionError(f"renumbered commit train not reported: {failures}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(root / LEDGER_PATH, _sample_ledger().replace("## Scope Note\n\n", "", 1))
        failures = collect_failures(root)
        expected = "missing:## Scope Note"
        if expected not in failures:
            raise AssertionError(f"missing scope note heading not reported: {failures}")
        scope_count = "scope-note-count:expected 1 got 0"
        if scope_count not in failures:
            raise AssertionError(f"scope note count drift not reported: {failures}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = (
            "missing:Later lane-level expansion stays traceable through the roadmap, "
            "the live repo, and current lane notes until a reviewed continuation of this ledger lands."
        )
        if expected not in failures:
            raise AssertionError(f"missing scope follow-through not reported: {failures}")
        case_count += 1

    print("LANE01_BOOTSTRAP_LEDGER_PACKET_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 bootstrap ledger packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic ledger fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for item in failures:
            print(f"ERROR: {item}")
        return 1

    print("Lane 01 bootstrap ledger packet check passed.")
    print("LANE01_BOOTSTRAP_LEDGER_PACKET_COMMIT_COUNT=25")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())