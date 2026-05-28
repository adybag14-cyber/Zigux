#!/usr/bin/env python3
"""Fail-closed checker for the Lane 01 bootstrap-ledger Scope Note packet."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


TARGET = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
HEADING = "## Scope Note"
NEXT_HEADING = "## Release-Planning Continuation"
REQUIRED_LINES = (
    "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
)
ORDER_HEADINGS = ("## Commit Train", "## Scope Note", "## Release-Planning Continuation")


def load_text(root: Path) -> str:
    path = root / TARGET
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing required file: {TARGET}")


def ensure_once(text: str, needle: str) -> None:
    count = text.count(needle)
    if count != 1:
        raise SystemExit(f"expected exactly one occurrence of {needle!r}, found {count}")


def ensure_order(text: str, headings: tuple[str, ...]) -> None:
    position = -1
    for heading in headings:
        next_position = text.find(heading)
        if next_position == -1:
            raise SystemExit(f"missing required heading: {heading}")
        if next_position <= position:
            raise SystemExit("section order mismatch for " + " -> ".join(headings))
        position = next_position


def extract_scope_note_lines(text: str) -> tuple[str, ...]:
    lines = text.splitlines()
    try:
        start_index = lines.index(HEADING)
    except ValueError as exc:
        raise SystemExit(f"missing required heading: {HEADING}") from exc

    try:
        end_index = lines.index(NEXT_HEADING, start_index + 1)
    except ValueError as exc:
        raise SystemExit(f"missing required heading: {NEXT_HEADING}") from exc

    body_lines = [line for line in lines[start_index + 1 : end_index] if line.strip()]
    return tuple(body_lines)


def validate(root: Path) -> None:
    text = load_text(root)
    ensure_once(text, HEADING)
    ensure_order(text, ORDER_HEADINGS)
    for line in REQUIRED_LINES:
        ensure_once(text, line)

    body_lines = extract_scope_note_lines(text)
    if body_lines != REQUIRED_LINES:
        raise SystemExit(
            "Scope Note body drifted; expected exactly the two bounded Phase 2 reminder lines"
        )


def write_sample_root(destination: Path) -> None:
    target = destination / TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            (
                "# Zigux Alpha Bootstrap Commit Ledger",
                "",
                "This ledger turns the roadmap into the first product commit train.",
                "",
                "## Commit Train",
                "",
                "1. `docs(zigux-alpha): establish roadmap and folder charter`",
                "",
                "## Scope Note",
                "",
                REQUIRED_LINES[0],
                REQUIRED_LINES[1],
                "",
                "## Release-Planning Continuation",
                "",
                "- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.",
                "",
            )
        ),
        encoding="utf-8",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane01_ledger_scope_note_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        validate(root)

        missing_heading = root / TARGET
        missing_heading.write_text(
            missing_heading.read_text(encoding="utf-8").replace(HEADING + "\n\n", ""),
            encoding="utf-8",
        )
        try:
            validate(root)
        except SystemExit:
            pass
        else:
            raise AssertionError("missing heading case should fail")

        write_sample_root(root)
        duplicate_line = root / TARGET
        duplicate_line.write_text(
            duplicate_line.read_text(encoding="utf-8") + REQUIRED_LINES[0] + "\n",
            encoding="utf-8",
        )
        try:
            validate(root)
        except SystemExit:
            pass
        else:
            raise AssertionError("duplicate line case should fail")

        write_sample_root(root)
        reordered = root / TARGET
        reordered.write_text(
            reordered.read_text(encoding="utf-8").replace(
                "## Commit Train\n\n1. `docs(zigux-alpha): establish roadmap and folder charter`\n\n## Scope Note",
                "## Scope Note\n\n"
                + REQUIRED_LINES[0]
                + "\n"
                + REQUIRED_LINES[1]
                + "\n\n## Commit Train",
            ),
            encoding="utf-8",
        )
        try:
            validate(root)
        except SystemExit:
            pass
        else:
            raise AssertionError("reordered heading case should fail")

        write_sample_root(root)
        extra_line = root / TARGET
        extra_line.write_text(
            extra_line.read_text(encoding="utf-8").replace(
                REQUIRED_LINES[1],
                REQUIRED_LINES[1] + "\n- Extra drift line.",
            ),
            encoding="utf-8",
        )
        try:
            validate(root)
        except SystemExit:
            pass
        else:
            raise AssertionError("extra scope note line case should fail")

        write_sample_root(root)
        missing_trailing_heading = root / TARGET
        missing_trailing_heading.write_text(
            missing_trailing_heading.read_text(encoding="utf-8").replace(
                NEXT_HEADING + "\n\n- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.\n",
                "",
            ),
            encoding="utf-8",
        )
        try:
            validate(root)
        except SystemExit:
            pass
        else:
            raise AssertionError("missing trailing heading case should fail")

    print("LANE01_BOOTSTRAP_LEDGER_SCOPE_NOTE_SELF_TEST=pass")
    print("LANE01_BOOTSTRAP_LEDGER_SCOPE_NOTE_SELF_TEST_CASES=5")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0
    if args.self_test:
        run_self_test()
        return 0

    validate(args.root)
    print("LANE01_BOOTSTRAP_LEDGER_SCOPE_NOTE=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_SCOPE_NOTE_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print("LANE01_BOOTSTRAP_LEDGER_SCOPE_NOTE_SECTION_ORDER=CommitTrain->ScopeNote->ReleasePlanningContinuation")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(str(exc), file=sys.stderr)
        raise
