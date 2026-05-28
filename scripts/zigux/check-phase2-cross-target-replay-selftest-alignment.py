#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-target-replay.py"

REQUIRED_SOURCE_MARKERS = (
    'FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"',
    'POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'EXPECTED_ROUTE = "make -C zigux phase2-cross"',
    'ZIG_TEST_FILES = (',
    'emit_summary("all-targets", targets)',
    'print("PHASE2_CROSS_TARGET_REPLAY=pass")',
    'print("PHASE2_CROSS_TARGET_REPLAY_SELF_TEST=pass")',
)

REQUIRED_CASE_MARKERS = (
    'payload["cross_targets"][0]["validation_mode"] = "unexpected_mode"',
    'payload["cross_targets"].append(dict(payload["cross_targets"][0]))',
    'payload["cross_targets"][0]["target"] = "riscv64-linux"',
    'result, output = capture_stdout(run_all_targets, root, str(fake_zig), 60)',
    'assert "PHASE2_CROSS_TARGET_REPLAY_MODE=single-target" not in output',
    'result, output = capture_stdout(run_single_target, root, "/definitely-missing-zig", "x86_64-linux", 60)',
    'result, output = capture_stdout(run_single_target, root, str(fake_zig), "riscv64-linux", 60)',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    checker_text = read_text(resolve_path(root, CHECKER))
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_SOURCE_MARKERS:
        count = count_occurrences(checker_text, marker)
        if count == 0:
            issues.append(("MISSING_SOURCE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SOURCE_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_CASE_MARKERS:
        count = count_occurrences(checker_text, marker)
        if count == 0:
            issues.append(("MISSING_CASE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CASE_MARKER", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_TARGET_REPLAY_SELFTEST_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, CHECKER),
        "\n".join((*REQUIRED_SOURCE_MARKERS, *REQUIRED_CASE_MARKERS, "")),
    )


def run_self_test() -> int:
    expected_case_count = 1 + len(REQUIRED_SOURCE_MARKERS) + len(REQUIRED_CASE_MARKERS) + 2
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_target_replay_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_SOURCE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_SOURCE_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_CASE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_CASE_MARKER", marker) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, CHECKER)
        path.write_text(path.read_text(encoding="utf-8") + REQUIRED_SOURCE_MARKERS[0] + "\n", encoding="utf-8")
        assert (
            "DUPLICATE_SOURCE_MARKER",
            f"{REQUIRED_SOURCE_MARKERS[0]}:count=2",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, CHECKER)
        path.write_text(path.read_text(encoding="utf-8") + REQUIRED_CASE_MARKERS[0] + "\n", encoding="utf-8")
        assert (
            "DUPLICATE_CASE_MARKER",
            f"{REQUIRED_CASE_MARKERS[0]}:count=2",
        ) in collect_issues(root)
        checks += 1

    assert checks == expected_case_count
    print("PHASE2_CROSS_TARGET_REPLAY_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 cross-target replay helper self-test surface intact."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_TARGET_REPLAY_SELFTEST_ALIGNMENT=pass")
    print(
        "PHASE2_CROSS_TARGET_REPLAY_SELFTEST_ALIGNMENT_SOURCE_MARKER_COUNT="
        f"{len(REQUIRED_SOURCE_MARKERS)}"
    )
    print(
        "PHASE2_CROSS_TARGET_REPLAY_SELFTEST_ALIGNMENT_CASE_MARKER_COUNT="
        f"{len(REQUIRED_CASE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
