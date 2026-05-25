#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NOTE_PATH = Path("Documentation/zigux/phase5-kobject-current-readback-note.md")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_build.zig",
)

PUBLIC_PACKET_PATHS = (
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
)

REQUIRED_MARKERS = (
    "Authenticated contents readback in this run directly returned:",
    "Fresh public current-`master` GitHub file readback still kept these owner-plus-companion packet members visible:",
    "same-lane reminder work should treat those authenticated-contents `404` results as connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo",
    "`zigux/tests/phase5_build.zig` remains part of the same packet on the direct authenticated contents route",
    "`samples/zigux/kobject_example.zig` remains tied to the roadmap anchor `samples/kobject/kobject-example.c` even when the current authenticated contents route flakes on that owner path",
    "non-goals stay unchanged: no sysfs file creation parity, no `kernel_kobj` integration, no uevents, and no loadable module registration claim",
    "`Documentation/zigux/phase5-kobject-sample-survey.md` and `Documentation/zigux/phase5-sample-lane-sequencing.md` already keep the dedicated survey note, bounded attr-group companion trio, focused replay, shared build route, and public-tree-backed owner-plus-companion split explicit.",
    "If the lane reopens now, start with `samples/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and repair only one bounded surface if it stops matching the direct survey-note plus public-tree-backed owner-and-companion split above.",
)

FORBIDDEN_MARKERS = (
    "`Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are direct authenticated reminder or packet evidence again",
    "same-lane reminder work should treat those authenticated-contents `404` results as proof that the broader kobject packet vanished from the repo",
)


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, path: Path, text: str) -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def note_placeholder() -> str:
    lines = [
        "# Phase 5 Kobject Current Readback Note",
        "",
        "## Current bounded packet on 2026-05-25",
        "",
        REQUIRED_MARKERS[0],
        "",
    ]
    lines.extend(f"- `{path}`" for path in DIRECT_PACKET_PATHS)
    lines.extend(
        [
            "",
            REQUIRED_MARKERS[1],
            "",
        ]
    )
    lines.extend(f"- `{path}`" for path in PUBLIC_PACKET_PATHS)
    lines.extend(["", *REQUIRED_MARKERS[2:]])
    return "\n".join(lines) + "\n"


def seed(root: Path) -> None:
    write_text(root, NOTE_PATH, note_placeholder())
    for rel in DIRECT_PACKET_PATHS + PUBLIC_PACKET_PATHS:
        write_text(root, Path(rel), "present\n")


def collect_failures(root: Path) -> list[str]:
    note = read_text(root, NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in note:
            failures.append(f"missing_text:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in note and rel not in note:
            failures.append(f"missing_direct_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"missing_repo_path:{rel}")

    for rel in PUBLIC_PACKET_PATHS:
        if f"`{rel}`" not in note and rel not in note:
            failures.append(f"missing_public_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"missing_repo_path:{rel}")

    for marker in FORBIDDEN_MARKERS:
        if marker in note:
            failures.append(f"forbidden_text:{marker}")

    return failures


def expect_exact(label: str, actual: list[str], expected: list[str]) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 8

    with tempfile.TemporaryDirectory(prefix="phase5_kobject_readback_note_") as tmpdir:
        root = Path(tmpdir)
        seed(root)

        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_flaky_404_marker"
        seed(mutated)
        write_text(mutated, NOTE_PATH, note_placeholder().replace(REQUIRED_MARKERS[2], ""))
        expect_exact(
            "missing flaky 404 marker",
            collect_failures(mutated),
            [f"missing_text:{REQUIRED_MARKERS[2]}"],
        )
        checks_run += 1

        mutated = root / "missing_direct_path"
        seed(mutated)
        write_text(
            mutated,
            NOTE_PATH,
            note_placeholder().replace(f"- `{DIRECT_PACKET_PATHS[1]}`\n", "", 1),
        )
        expect_exact(
            "missing direct path",
            collect_failures(mutated),
            [f"missing_direct_path:{DIRECT_PACKET_PATHS[1]}"],
        )
        checks_run += 1

        mutated = root / "missing_public_path"
        seed(mutated)
        write_text(
            mutated,
            NOTE_PATH,
            note_placeholder().replace(f"- `{PUBLIC_PACKET_PATHS[1]}`\n", "", 1),
        )
        expect_exact(
            "missing public path",
            collect_failures(mutated),
            [f"missing_public_path:{PUBLIC_PACKET_PATHS[1]}"],
        )
        checks_run += 1

        mutated = root / "missing_repo_path"
        seed(mutated)
        (mutated / DIRECT_PACKET_PATHS[2]).unlink()
        expect_exact(
            "missing repo path",
            collect_failures(mutated),
            [f"missing_repo_path:{DIRECT_PACKET_PATHS[2]}"],
        )
        checks_run += 1

        mutated = root / "forbidden_direct_claim"
        seed(mutated)
        write_text(mutated, NOTE_PATH, note_placeholder() + FORBIDDEN_MARKERS[0] + "\n")
        expect_exact(
            "forbidden direct claim",
            collect_failures(mutated),
            [f"forbidden_text:{FORBIDDEN_MARKERS[0]}"],
        )
        checks_run += 1

        mutated = root / "forbidden_vanished_claim"
        seed(mutated)
        write_text(mutated, NOTE_PATH, note_placeholder() + FORBIDDEN_MARKERS[1] + "\n")
        expect_exact(
            "forbidden vanished claim",
            collect_failures(mutated),
            [f"forbidden_text:{FORBIDDEN_MARKERS[1]}"],
        )
        checks_run += 1

        mutated = root / "missing_next_step_marker"
        seed(mutated)
        write_text(mutated, NOTE_PATH, note_placeholder().replace(REQUIRED_MARKERS[7], ""))
        expect_exact(
            "missing next-step marker",
            collect_failures(mutated),
            [f"missing_text:{REQUIRED_MARKERS[7]}"],
        )
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")

    print("PHASE5_KOBJECT_READBACK_NOTE_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_READBACK_NOTE_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT.parent.parent, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_KOBJECT_READBACK_NOTE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_KOBJECT_READBACK_NOTE=pass")
    print(f"PHASE5_KOBJECT_READBACK_NOTE_DIRECT_PATH_COUNT={len(DIRECT_PACKET_PATHS)}")
    print(f"PHASE5_KOBJECT_READBACK_NOTE_PUBLIC_PATH_COUNT={len(PUBLIC_PACKET_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
