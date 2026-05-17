#!/usr/bin/env python3
"""Guard the bounded Phase 4 reversible-delivery exact-pin follow-through."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
README = Path("zigux/tests/README.md")
REPO_REALITY_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")

STATUS_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=4`",
)

TARGET_MARKERS = (
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
)

NOTE_MARKERS = STATUS_MARKERS + TARGET_MARKERS + (
    "The stale Phase 4 repo-reality warning in `zigux/tests/README.md` is now closed",
    "The next honest same-family follow-through is to run the dedicated exact-pin pass",
    "The current direct readback now keeps the rollback-owner reminder, the review-checklist handoff, the tests-root route inventory, the new dedicated exact-pin checker",
)

README_MARKERS = (
    "current broader Phase 4 packet reminder",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "historical provenance that still needs one exact-pin refresh",
)

WARNING_MARKERS = (
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "The stale Phase 4 repo-reality warning in `zigux/tests/README.md` is now closed",
    "The next honest same-family follow-through is to run the dedicated exact-pin pass",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=4",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    readme = read(root, README)
    repo_warning = read(root, REPO_REALITY_WARNING)
    require(note, NOTE_MARKERS, NOTE.as_posix())
    require(readme, README_MARKERS, README.as_posix())
    require(repo_warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    note_targets = "\n".join(f"  * {item}" for item in TARGET_MARKERS)
    write(
        root / NOTE,
        "# Phase 4 Reversible Delivery Evidence\n\n"
        "The stale Phase 4 repo-reality warning in `zigux/tests/README.md` is now closed.\n\n"
        "The next honest same-family follow-through is to run the dedicated exact-pin pass.\n\n"
        "* `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`\n"
        "* `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=4`\n\n"
        "The current direct readback now keeps the rollback-owner reminder, the review-checklist handoff, the tests-root route inventory, the new dedicated exact-pin checker, and the directly readable validator, lab-matrix, and local-only perf companions explicit without pretending those paths are absent on current `master`.\n\n"
        f"{note_targets}\n",
    )
    write(
        root / README,
        "# zigux/tests\n\n"
        "  * current broader Phase 4 packet reminder: `scripts/zigux/check-phase4-reversible-delivery-pins.py`\n"
        "  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance that still needs one exact-pin refresh\n",
    )
    write(
        root / REPO_REALITY_WARNING,
        "#!/usr/bin/env python3\n"
        "DIRECT_READBACK_PACKET = (\n"
        "    \"scripts/zigux/check-phase4-reversible-delivery-pins.py\",\n"
        ")\n"
        "NOTE_REQ = (\n"
        "    \"The stale Phase 4 repo-reality warning in `zigux/tests/README.md` is now closed\",\n"
        "    \"The next honest same-family follow-through is to run the dedicated exact-pin pass\",\n"
        "    \"PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true\",\n"
        "    \"PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=4\",\n"
        ")\n",
    )


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-reversible-delivery-pins-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(root / NOTE, read(root, NOTE).replace(STATUS_MARKERS[0], "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=false`"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note pin-checker marker drift to fail")

        fixture_root(root)
        write(root / NOTE, read(root, NOTE).replace(TARGET_MARKERS[0], "`Documentation/zigux/not-the-right-file.md`"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note target drift to fail")

        fixture_root(root)
        write(root / README, read(root, README).replace(README_MARKERS[0], "broader packet wording drifted"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected README drift to fail")

    print("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass")
    print(f"PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REVERSIBLE_DELIVERY_PINS=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REVERSIBLE_DELIVERY_PINS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
