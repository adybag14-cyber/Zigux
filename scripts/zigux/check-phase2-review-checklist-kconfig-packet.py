#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

REVIEW_MARKERS = (
    "if the change touches the shared Phase 2 kconfig bridge packet",
    "do `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, and `make -C zigux phase2-kconfig`",
    "still agree on the current bridge packet?",
)

TESTS_MARKERS = (
    "Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "Keep the current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
)

TESTS_FORBIDDEN_MARKERS = (
    "current `master` still returns missing for `scripts/zigux/check-kconfig-bridge.py`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_text = read_text(resolve_path(root, TESTS_README))
    issues.extend(collect_missing_markers(review_text, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(tests_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_forbidden_markers(tests_text, TESTS_FORBIDDEN_MARKERS, "FORBIDDEN_TESTS_MARKERS"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REVIEW_MARKERS) + len(TESTS_MARKERS) + len(TESTS_FORBIDDEN_MARKERS) + 2
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_kconfig_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REVIEW_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for rel_path in (REVIEW_CHECKLIST, TESTS_README):
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 kconfig bridge reminder aligned between the review checklist and tests root."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample tree to the given root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_KCONFIG_PACKET_FORBIDDEN_MARKER_COUNT={len(TESTS_FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
