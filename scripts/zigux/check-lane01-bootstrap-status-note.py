#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

ROADMAP_REL = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"

STATUS_NOTE_LINES = (
    "## Bootstrap Status Note",
    "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
    "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
)

ORDERED_HEADINGS = (
    "## Purpose",
    "## Bootstrap Status Note",
    "## Inputs Reviewed",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    roadmap_path = root / ROADMAP_REL
    if not roadmap_path.exists():
        return [f"missing_file:{ROADMAP_REL}"]

    roadmap = _read(roadmap_path)
    for marker in STATUS_NOTE_LINES:
        if marker not in roadmap:
            issues.append(f"roadmap:missing:{marker}")

    positions: list[tuple[str, int]] = []
    for heading in ORDERED_HEADINGS:
        position = roadmap.find(heading)
        if position == -1:
            issues.append(f"roadmap:missing:{heading}")
        positions.append((heading, position))

    if not issues:
        ordered_positions = [position for _, position in positions]
        if ordered_positions != sorted(ordered_positions):
            issues.append("roadmap:order:bootstrap_status_note_packet")

    return issues


def _seed(root: Path, *, include_status_note: bool = True) -> None:
    lines = [
        "# ZAR to Zigux Product Roadmap",
        "",
        "## Purpose",
        "",
        "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.",
        "",
    ]
    if include_status_note:
        lines.extend(
            [
                "## Bootstrap Status Note",
                "",
                STATUS_NOTE_LINES[1],
                "",
                STATUS_NOTE_LINES[2],
                "",
            ]
        )
    lines.extend(
        [
            "## Inputs Reviewed",
            "",
            "Placeholder packet for focused checker validation.",
            "",
        ]
    )
    _write(root / ROADMAP_REL, "\n".join(lines))


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"lane01-bootstrap-status-note-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_bootstrap_status_note_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        _seed(root, include_status_note=False)
        _assert_only(
            validate(root),
            [
                "roadmap:missing:## Bootstrap Status Note",
                f"roadmap:missing:{STATUS_NOTE_LINES[1]}",
                f"roadmap:missing:{STATUS_NOTE_LINES[2]}",
                "roadmap:missing:## Bootstrap Status Note",
            ],
            "missing_status_note_packet",
        )
        case_count += 1

        _seed(root)
        path = root / ROADMAP_REL
        _write(path, _read(path).replace(f"{STATUS_NOTE_LINES[1]}\n", "", 1))
        _assert_only(
            validate(root),
            [f"roadmap:missing:{STATUS_NOTE_LINES[1]}"],
            "missing_status_baseline_sentence",
        )
        case_count += 1

        _seed(root)
        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "\n## Bootstrap Status Note\n\nThis roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.\n\nFor later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.\n\n## Inputs Reviewed\n",
                "\n## Inputs Reviewed\n\n## Bootstrap Status Note\n\nThis roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.\n\nFor later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["roadmap:order:bootstrap_status_note_packet"],
            "misordered_status_note_heading",
        )
        case_count += 1

    print("LANE01_BOOTSTRAP_STATUS_NOTE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_STATUS_NOTE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap Bootstrap Status Note aligned with current master guidance."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("LANE01_BOOTSTRAP_STATUS_NOTE=fail")
        print("LANE01_BOOTSTRAP_STATUS_NOTE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("LANE01_BOOTSTRAP_STATUS_NOTE_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_STATUS_NOTE=pass")
    print(f"LANE01_BOOTSTRAP_STATUS_NOTE_REQUIRED_MARKER_COUNT={len(STATUS_NOTE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
