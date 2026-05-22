#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TESTS_README_PATH = Path("zigux/tests/README.md")
CROSS_TARGETS_PATH = Path("zigux/tests/fixtures/phase2_cross_targets.json")

TESTS_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
    "keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
)

FORBIDDEN_TESTS_MARKERS = (
    "still-missing validator-first, installer, and direct cross-route paths",
)

EXPECTED_FIXTURE = {
    "phase": "Phase 2",
    "status": "active",
    "route": "make -C zigux phase2-cross",
    "archive_target_scope": ["x86_64-linux"],
    "cross_targets": [
        {
            "target": "x86_64-linux",
            "review_status": "pinned bootstrap archive",
            "validation_mode": "archive_required",
            "route": "make -C zigux phase2-cross",
        },
        {
            "target": "aarch64-linux",
            "review_status": "route contract only",
            "validation_mode": "route_contract_only",
            "route": "make -C zigux phase2-cross",
        },
    ],
}

CURRENT_LIKE_TESTS_README = """# zigux/tests

## Phase 2 review packet

Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:

- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-cross`.

Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/install-zig.py --self-test` and `python3 scripts/zigux/check-phase2-cross.py --self-test`.

current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {path}: {exc.msg}") from exc


def collect_tests_readme_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in TESTS_MARKERS:
        if marker not in text:
            issues.append(("MISSING_TESTS_MARKERS", marker))
    for marker in FORBIDDEN_TESTS_MARKERS:
        if marker in text:
            issues.append(("FORBIDDEN_TESTS_MARKERS", marker))
    return issues


def collect_cross_target_issues(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if payload != EXPECTED_FIXTURE:
        if not isinstance(payload, dict):
            issues.append(("INVALID_CROSS_TARGETS_PAYLOAD", "expected object"))
            return issues
        for key in ("phase", "status", "route"):
            if payload.get(key) != EXPECTED_FIXTURE[key]:
                issues.append(("MISMATCH_CROSS_TARGETS_FIELD", key))
        if payload.get("archive_target_scope") != EXPECTED_FIXTURE["archive_target_scope"]:
            issues.append(("MISMATCH_CROSS_TARGETS_FIELD", "archive_target_scope"))
        if payload.get("cross_targets") != EXPECTED_FIXTURE["cross_targets"]:
            issues.append(("MISMATCH_CROSS_TARGETS_FIELD", "cross_targets"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_tests_readme_issues(read_text(root / TESTS_README_PATH)))
    issues.extend(collect_cross_target_issues(read_json(root / CROSS_TARGETS_PATH)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, marker in issues:
        grouped.setdefault(code, []).append(marker)
    print("PHASE2_TESTS_README_CROSS_PACKET=fail")
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
    write_text(root / TESTS_README_PATH, CURRENT_LIKE_TESTS_README)
    write_text(root / CROSS_TARGETS_PATH, json.dumps(EXPECTED_FIXTURE, indent=2) + "\n")


def replace_marker(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(TESTS_MARKERS) + len(FORBIDDEN_TESTS_MARKERS) + 4
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_cross_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in TESTS_MARKERS:
            build_sample_root(root)
            path = root / TESTS_README_PATH
            path.write_text(replace_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for marker in FORBIDDEN_TESTS_MARKERS:
            build_sample_root(root)
            path = root / TESTS_README_PATH
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_MARKERS", marker) in issues
            checks_run += 1

        build_sample_root(root)
        payload = EXPECTED_FIXTURE | {"route": "make -C zigux phase2-tools"}
        write_text(root / CROSS_TARGETS_PATH, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISMATCH_CROSS_TARGETS_FIELD", "route") in issues
        checks_run += 1

        build_sample_root(root)
        payload = EXPECTED_FIXTURE | {"archive_target_scope": ["aarch64-linux"]}
        write_text(root / CROSS_TARGETS_PATH, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISMATCH_CROSS_TARGETS_FIELD", "archive_target_scope") in issues
        checks_run += 1

        build_sample_root(root)
        write_text(root / CROSS_TARGETS_PATH, "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid json did not abort")

        build_sample_root(root)
        (root / TESTS_README_PATH).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing README did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_TESTS_README_CROSS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_CROSS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the tests-root Phase 2 direct cross-route packet aligned to current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like passing sample root for replay validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_README_CROSS_PACKET=pass")
    print(f"PHASE2_TESTS_README_CROSS_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(
        "PHASE2_TESTS_README_CROSS_PACKET_TARGET_COUNT="
        f"{len(EXPECTED_FIXTURE['cross_targets'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
