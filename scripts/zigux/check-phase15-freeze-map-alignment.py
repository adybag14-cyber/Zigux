#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")

REQUIRED_MARKERS = (
    "# Zigux Freeze Map",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "decision record ID",
    "required approver set",
    "automatic return-to-blocked trigger",
    "parity scorecard link or blocker record",
    "shared reminder surfaces that summarize freeze posture",
    "must describe missing validator, tests-root, or make-route companions as repo-reality gaps until those paths are directly materialized on `master`",
    "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "there is no silent exception path around the stay-in-C policy",
)


def collect_missing_markers(root: Path) -> list[str]:
    source = (root / FREEZE_MAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            missing.append(f"freeze_map:{marker}")
    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- decision record ID
- required approver set
- automatic return-to-blocked trigger
- parity scorecard link or blocker record
- shared reminder surfaces that summarize freeze posture
- must describe missing validator, tests-root, or make-route companions as repo-reality gaps until those paths are directly materialized on `master`
- direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- there is no silent exception path around the stay-in-C policy
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_freeze_map_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / FREEZE_MAP_PATH, _sample_freeze_map())

        if collect_missing_markers(root):
            raise AssertionError("baseline freeze-map fixture should pass")
        case_count += 1

        _write(
            root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "- `Documentation/zigux/phase15-architecture-council-review-process.md`\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = ["freeze_map:`Documentation/zigux/phase15-architecture-council-review-process.md`"]
        if missing != expected:
            raise AssertionError(f"unexpected review-process failure: {missing}")
        case_count += 1

        _write(
            root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace("- required approver set\n", "", 1),
        )
        missing = collect_missing_markers(root)
        if missing != ["freeze_map:required approver set"]:
            raise AssertionError(f"unexpected approver-set failure: {missing}")
        case_count += 1

        _write(
            root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "- parity scorecard link or blocker record\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        if missing != ["freeze_map:parity scorecard link or blocker record"]:
            raise AssertionError(f"unexpected parity-scorecard failure: {missing}")
        case_count += 1

        _write(
            root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "- must describe missing validator, tests-root, or make-route companions as repo-reality gaps until those paths are directly materialized on `master`\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "freeze_map:must describe missing validator, tests-root, or make-route companions as repo-reality gaps until those paths are directly materialized on `master`"
        ]
        if missing != expected:
            raise AssertionError(f"unexpected repo-reality-gap failure: {missing}")
        case_count += 1

        _write(
            root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "- there is no silent exception path around the stay-in-C policy\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        if missing != ["freeze_map:there is no silent exception path around the stay-in-C policy"]:
            raise AssertionError(f"unexpected stay-in-C failure: {missing}")
        case_count += 1

    print("PHASE15_FREEZE_MAP_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 freeze-map governance packet stays explicit."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/freeze-map.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic freeze-map fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("Phase 15 freeze-map alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
