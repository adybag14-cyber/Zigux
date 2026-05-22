#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NOTE_PATH = Path("Documentation/zigux/phase5-kobject-current-readback-note.md")

DIRECT_PATHS = (
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_build.zig",
    "samples/zigux/kobject_example_attr_group_contract.zig",
)

PUBLIC_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
)

FOLLOW_THROUGH_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
)

REQUIRED_MARKERS = (
    "Authenticated contents readback in this run directly returned:",
    "Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.",
    "The same run still confirmed these current `master` packet members through public GitHub file readback:",
    "the direct sample-root file, focused tests-root replay, shared build route, and attr-group companion are readable through the authenticated contents route used here",
    "the dedicated survey note, manifest-backed contract, and survey replay remain visible on public current `master` even though this run's authenticated contents route returned `404` for those three packet members",
    "same-lane reminder work should treat those authenticated-contents `404` results as current connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo",
    "Those surviving shared-surface follow-through targets are:",
    "The same slot also confirmed that `zigux/tests/README.md` already keeps the narrower kobject split closer to the live readback packet, so the next same-lane repair can stay outside the tests-root reminder unless a fresh reread reopens that surface too.",
    "If a fresh reread still leaves one shared reminder surface overstating the survey note, manifest, or survey replay as direct authenticated proof, or still leaves `zigux/tests/phase5_build.zig` mislabeled as companion-only evidence, reopen the lane for that one-file truthfulness repair only.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder_note() -> str:
    lines = [
        "# Phase 5 Kobject Current Readback Note",
        "",
        "Authenticated contents readback in this run directly returned:",
        "",
    ]
    lines.extend(f"- `{path}`" for path in DIRECT_PATHS[:3])
    lines.extend(
        (
            "",
            "Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.",
            "",
            "The same run still confirmed these current `master` packet members through public GitHub file readback:",
            "",
        )
    )
    lines.extend(f"- `{path}`" for path in PUBLIC_PATHS)
    lines.extend(
        (
            "",
            "That means the strongest honest current packet for this run is:",
            "",
            "- the direct sample-root file, focused tests-root replay, shared build route, and attr-group companion are readable through the authenticated contents route used here",
            "- the dedicated survey note, manifest-backed contract, and survey replay remain visible on public current `master` even though this run's authenticated contents route returned `404` for those three packet members",
            "- same-lane reminder work should treat those authenticated-contents `404` results as current connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo",
            "",
            "Those surviving shared-surface follow-through targets are:",
            "",
        )
    )
    lines.extend(f"- `{path}`" for path in FOLLOW_THROUGH_PATHS[:-2])
    lines.extend(
        (
            "",
            "The same slot also confirmed that `zigux/tests/README.md` already keeps the narrower kobject split closer to the live readback packet, so the next same-lane repair can stay outside the tests-root reminder unless a fresh reread reopens that surface too.",
            "",
            "Compare this note against `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py` the next time the lane reopens.",
            "",
            "If a fresh reread still leaves one shared reminder surface overstating the survey note, manifest, or survey replay as direct authenticated proof, or still leaves `zigux/tests/phase5_build.zig` mislabeled as companion-only evidence, reopen the lane for that one-file truthfulness repair only.",
            "",
        )
    )
    return "\n".join(lines)


def seed(root: Path) -> None:
    write_text(root / NOTE_PATH, placeholder_note())
    for path in DIRECT_PATHS + PUBLIC_PATHS + FOLLOW_THROUGH_PATHS:
        if path == str(NOTE_PATH):
            continue
        write_text(root / path, "present\n")


def collect_failures(root: Path) -> list[str]:
    note = read_text(root / NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in note:
            failures.append(f"note:missing_text:{marker}")

    for path in DIRECT_PATHS:
        if f"`{path}`" not in note:
            failures.append(f"note:missing_direct_path:{path}")
        if not (root / path).exists():
            failures.append(f"repo:missing_direct_path:{path}")

    for path in PUBLIC_PATHS:
        if f"`{path}`" not in note:
            failures.append(f"note:missing_public_path:{path}")
        if not (root / path).exists():
            failures.append(f"repo:missing_public_path:{path}")

    for path in FOLLOW_THROUGH_PATHS:
        if f"`{path}`" not in note:
            failures.append(f"note:missing_follow_through_path:{path}")
        if not (root / path).exists():
            failures.append(f"repo:missing_follow_through_path:{path}")

    return failures


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 5
    with tempfile.TemporaryDirectory(prefix="phase5_kobject_readback_note_") as tmpdir:
        root = Path(tmpdir)
        seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_marker_root = root / "missing_marker"
        seed(missing_marker_root)
        write_text(
            missing_marker_root / NOTE_PATH,
            placeholder_note().replace(REQUIRED_MARKERS[4] + "\n", "", 1),
        )
        failures = collect_failures(missing_marker_root)
        expected = [f"note:missing_text:{REQUIRED_MARKERS[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")
        checks_run += 1

        missing_direct_path_root = root / "missing_direct_path"
        seed(missing_direct_path_root)
        (missing_direct_path_root / DIRECT_PATHS[3]).unlink()
        failures = collect_failures(missing_direct_path_root)
        expected = [f"repo:missing_direct_path:{DIRECT_PATHS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct-path failure: {failures}")
        checks_run += 1

        missing_follow_through_repo_path_root = root / "missing_follow_through_repo_path"
        seed(missing_follow_through_repo_path_root)
        (missing_follow_through_repo_path_root / FOLLOW_THROUGH_PATHS[-1]).unlink()
        failures = collect_failures(missing_follow_through_repo_path_root)
        expected = [f"repo:missing_follow_through_path:{FOLLOW_THROUGH_PATHS[-1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-follow-through-repo-path failure: {failures}")
        checks_run += 1

        missing_note_root = root / "missing_note"
        seed(missing_note_root)
        (missing_note_root / NOTE_PATH).unlink()
        try:
            collect_failures(missing_note_root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-note abort: {exc}") from exc
        else:
            raise AssertionError("missing note did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_KOBJECT_CURRENT_READBACK_NOTE_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 kobject current-readback note keeps its direct-versus-public packet split explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_KOBJECT_CURRENT_READBACK_NOTE=pass")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_DIRECT_PATH_COUNT={len(DIRECT_PATHS)}")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_PUBLIC_PATH_COUNT={len(PUBLIC_PATHS)}")
    print(f"PHASE5_KOBJECT_CURRENT_READBACK_NOTE_FOLLOW_THROUGH_COUNT={len(FOLLOW_THROUGH_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
