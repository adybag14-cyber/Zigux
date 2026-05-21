#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")
FIXTURE = ROOT / FIXTURE_REL

EXPECTED_STATUS = "closed"
EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]
EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/fixdep.zig",
]
EXPECTED_FIXTURE_FIELDS = {
    "phase",
    "status",
    "target_count",
    "targets",
    "zig_test_files",
}
EXPECTED_SELF_TEST_CASE_COUNT = 38


def probe_required_file(path: Path) -> None:
    with path.open("rb") as handle:
        handle.read(0)


def require_files(root: Path) -> list[tuple[str, str]]:
    required = [
        FIXTURE_REL,
        Path("scripts/zigux/fixdep.zig"),
    ]
    issues: list[tuple[str, str]] = []
    for rel in required:
        candidate = root / rel
        rel_str = str(rel)
        if not candidate.is_file():
            if candidate.exists():
                issues.append(("required_path_not_file", rel_str))
            else:
                issues.append(("required_file_missing", rel_str))
            continue
        try:
            probe_required_file(candidate)
        except OSError:
            issues.append(("required_file_unreadable", rel_str))
    return issues


def load_fixture(path: Path) -> dict[str, object]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"required file missing: {path}") from exc
    except OSError as exc:
        raise RuntimeError(f"required file unreadable: {path}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"fixture is not valid json: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"fixture is not a JSON object: {path}")
    return payload


def collect_duplicate_entries(values: object, prefix: str) -> list[str]:
    if not isinstance(values, list):
        return []

    counts: dict[str, int] = {}
    for value in values:
        key = value if isinstance(value, str) else repr(value)
        counts[key] = counts.get(key, 0) + 1
    return [f"{prefix}:{key}:count={count}" for key, count in counts.items() if count > 1]


def collect_non_string_entries(values: object, prefix: str) -> list[str]:
    if not isinstance(values, list):
        return []
    return [f"{prefix}:{value!r}" for value in values if not isinstance(value, str)]


def validate_fixture(root: Path) -> list[str]:
    issues: list[str] = []
    payload = load_fixture(root / FIXTURE_REL)

    unexpected_fields = sorted(set(payload) - EXPECTED_FIXTURE_FIELDS)
    issues.extend(f"fixture:unexpected_field:{field}" for field in unexpected_fields)

    if payload.get("phase") != "Phase 2":
        issues.append(f"fixture:phase:{payload.get('phase')!r}")
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"fixture:status:{payload.get('status')!r}")

    targets = payload.get("targets")
    if not isinstance(targets, list):
        issues.append(f"fixture:targets_not_list:{targets!r}")
    elif targets != EXPECTED_TARGETS:
        issues.append(f"fixture:targets:{targets!r}")

    target_count = payload.get("target_count")
    if type(target_count) is not int:
        issues.append(f"fixture:target_count_not_int:{target_count!r}")
    elif target_count != len(EXPECTED_TARGETS):
        issues.append(f"fixture:target_count:{target_count!r}")

    issues.extend(collect_non_string_entries(targets, "fixture:non_string_target"))
    issues.extend(collect_duplicate_entries(targets, "fixture:duplicate_target"))

    zig_test_files = payload.get("zig_test_files")
    if not isinstance(zig_test_files, list):
        issues.append(f"fixture:zig_test_files_not_list:{zig_test_files!r}")
    elif zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append(f"fixture:zig_test_files:{zig_test_files!r}")
    issues.extend(collect_non_string_entries(zig_test_files, "fixture:non_string_zig_test_file"))
    issues.extend(collect_duplicate_entries(zig_test_files, "fixture:duplicate_zig_test_file"))
    return issues


def resolve_zig(override: str | None) -> str | None:
    if override:
        return override
    return shutil.which("zig")


def validate_zig_test_file(root: Path, rel_path: str) -> str | None:
    candidate = root / rel_path
    if not candidate.is_file():
        if candidate.exists():
            return f"zig test path is not a file: {rel_path}"
        return f"zig test path missing on branch: {rel_path}"
    try:
        probe_required_file(candidate)
    except OSError:
        return f"zig test path unreadable on branch: {rel_path}"
    return None


def run_cross_compile(root: Path, target: str, zig: str) -> int:
    payload = load_fixture(root / FIXTURE_REL)
    targets = payload.get("targets")
    if not isinstance(targets, list) or target not in targets:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_TARGET={target}")
        print("PHASE2_CROSS_NOTE=target not listed in fixture")
        return 1

    zig_test_files = payload.get("zig_test_files")
    if not isinstance(zig_test_files, list) or not all(isinstance(item, str) for item in zig_test_files):
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=fixture zig_test_files is invalid")
        return 1

    for rel_path in zig_test_files:
        path_issue = validate_zig_test_file(root, rel_path)
        if path_issue is not None:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_TARGET={target}")
            print(f"PHASE2_CROSS_FAILED_FILE={rel_path}")
            print(f"PHASE2_CROSS_NOTE={path_issue}")
            return 1

        completed = subprocess.run(
            [zig, "test", rel_path, "-target", target, "--test-no-exec"],
            cwd=root,
            check=False,
        )
        if completed.returncode != 0:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_TARGET={target}")
            print(f"PHASE2_CROSS_FAILED_FILE={rel_path}")
            return completed.returncode

    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET={target}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")
    return 0


def summarize_packet(root: Path) -> int:
    payload = load_fixture(root / FIXTURE_REL)
    targets = payload["targets"]
    zig_test_files = payload["zig_test_files"]
    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGETS={','.join(targets)}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")
    return 0


def run_checker(root: Path, *, target: str | None, zig: str | None) -> int:
    missing = require_files(root)
    if missing:
        return emit_required_file_issues(missing)

    try:
        issues = validate_fixture(root)
    except RuntimeError as exc:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_NOTE={exc}")
        return 1

    if issues:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CROSS_ISSUES_END")
        return 1

    if target:
        resolved_zig = resolve_zig(zig)
        if resolved_zig is None:
            print("PHASE2_CROSS=fail")
            print("PHASE2_CROSS_NOTE=zig not found on PATH")
            return 1
        try:
            return run_cross_compile(root, target, resolved_zig)
        except RuntimeError as exc:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_NOTE={exc}")
            return 1

    try:
        return summarize_packet(root)
    except RuntimeError as exc:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_NOTE={exc}")
        return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        path.rmdir()
    path.write_text(content, encoding="utf-8")


def write_fixture(root: Path, payload: object) -> None:
    write_text(
        root / FIXTURE_REL,
        json.dumps(payload, indent=2) + "\n",
    )


def build_self_test_root(root: Path) -> None:
    write_fixture(
        root,
        {
            "phase": "Phase 2",
            "status": EXPECTED_STATUS,
            "target_count": len(EXPECTED_TARGETS),
            "targets": EXPECTED_TARGETS,
            "zig_test_files": EXPECTED_ZIG_TEST_FILES,
        },
    )
    write_text(root / "scripts/zigux/fixdep.zig", 'test "stub" {}\n')


def emit_required_file_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_CROSS=fail")

    missing = [value for code, value in issues if code == "required_file_missing"]
    non_file = [value for code, value in issues if code == "required_path_not_file"]
    unreadable = [value for code, value in issues if code == "required_file_unreadable"]

    if missing:
        print("PHASE2_CROSS_MISSING_FILES_START")
        for rel_path in missing:
            print(rel_path)
        print("PHASE2_CROSS_MISSING_FILES_END")
    if non_file:
        print("PHASE2_CROSS_NON_FILE_PATHS_START")
        for rel_path in non_file:
            print(rel_path)
        print("PHASE2_CROSS_NON_FILE_PATHS_END")
    if unreadable:
        print("PHASE2_CROSS_UNREADABLE_FILES_START")
        for rel_path in unreadable:
            print(rel_path)
        print("PHASE2_CROSS_UNREADABLE_FILES_END")
    return 1


def capture_cross_compile(root: Path, target: str, zig: str) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        result = run_cross_compile(root, target, zig)
    return result, stdout.getvalue()


def capture_packet_summary(root: Path) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        result = summarize_packet(root)
    return result, stdout.getvalue()


def capture_run_checker(root: Path, *, target: str | None = None, zig: str | None = None) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        result = run_checker(root, target=target, zig=zig)
    return result, stdout.getvalue()


def assert_runtime_error_contains(callback, expected_fragment: str) -> None:
    try:
        callback()
    except RuntimeError as exc:
        assert expected_fragment in str(exc), str(exc)
        return
    raise AssertionError(f"expected RuntimeError containing: {expected_fragment}")


def assert_run_checker_note_contains(
    root: Path,
    *,
    target: str | None = None,
    zig: str | None = None,
    expected_fragment: str,
) -> None:
    result, output = capture_run_checker(root, target=target, zig=zig)
    assert result == 1
    assert "PHASE2_CROSS=fail" in output
    assert f"PHASE2_CROSS_NOTE={expected_fragment}" in output, output


def assert_run_checker_output_contains(
    root: Path,
    *,
    target: str | None = None,
    zig: str | None = None,
    expected_fragment: str,
) -> None:
    result, output = capture_run_checker(root, target=target, zig=zig)
    assert result == 1
    assert "PHASE2_CROSS=fail" in output
    assert expected_fragment in output, output


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_cross_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert require_files(root) == []
        assert validate_fixture(root) == []
        result, output = capture_packet_summary(root)
        assert result == 0
        assert "PHASE2_CROSS=pass" in output
        assert f"PHASE2_CROSS_TARGET_COUNT={len(EXPECTED_TARGETS)}" in output
        assert f"PHASE2_CROSS_TARGETS={','.join(EXPECTED_TARGETS)}" in output
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": 2,
                "targets": EXPECTED_TARGETS[:-1],
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:") for issue in issues)
        assert "fixture:target_count:2" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": "3",
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:target_count_not_int:'3'" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": True,
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:target_count_not_int:True" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": "open",
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:status:'open'" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase X",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:phase:'Phase X'" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": ["scripts/zigux/other.zig"],
            },
        )
        issues = validate_fixture(root)
        assert "fixture:zig_test_files:['scripts/zigux/other.zig']" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": "x86_64-linux-musl",
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:targets_not_list:'x86_64-linux-musl'" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": [EXPECTED_TARGETS[0], 7, EXPECTED_TARGETS[2]],
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:non_string_target:7" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS + [EXPECTED_TARGETS[0]],
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
        )
        issues = validate_fixture(root)
        assert f"fixture:duplicate_target:{EXPECTED_TARGETS[0]}:count=2" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": "scripts/zigux/fixdep.zig",
            },
        )
        issues = validate_fixture(root)
        assert "fixture:zig_test_files_not_list:'scripts/zigux/fixdep.zig'" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": [123],
            },
        )
        issues = validate_fixture(root)
        assert "fixture:non_string_zig_test_file:123" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES + [EXPECTED_ZIG_TEST_FILES[0]],
            },
        )
        issues = validate_fixture(root)
        assert f"fixture:duplicate_zig_test_file:{EXPECTED_ZIG_TEST_FILES[0]}:count=2" in issues
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                "unexpected": True,
            },
        )
        issues = validate_fixture(root)
        assert "fixture:unexpected_field:unexpected" in issues
        case_count += 1

        build_self_test_root(root)
        (root / FIXTURE_REL).write_text("{\n", encoding="utf-8")
        assert_runtime_error_contains(lambda: validate_fixture(root), "fixture is not valid json:")
        case_count += 1
        assert_run_checker_note_contains(
            root,
            expected_fragment="fixture is not valid json:",
        )
        case_count += 1

        build_self_test_root(root)
        write_fixture(root, ["not", "an", "object"])
        assert_runtime_error_contains(lambda: validate_fixture(root), "fixture is not a JSON object:")
        case_count += 1
        assert_run_checker_note_contains(
            root,
            expected_fragment="fixture is not a JSON object:",
        )
        case_count += 1

        build_self_test_root(root)
        (root / FIXTURE_REL).unlink()
        assert_runtime_error_contains(lambda: validate_fixture(root), "required file missing:")
        case_count += 1
        assert_run_checker_output_contains(
            root,
            expected_fragment="PHASE2_CROSS_MISSING_FILES_START",
        )
        case_count += 1

        build_self_test_root(root)
        (root / FIXTURE_REL).unlink()
        (root / FIXTURE_REL).mkdir(parents=True)
        assert_runtime_error_contains(lambda: validate_fixture(root), "required file unreadable:")
        assert_run_checker_output_contains(
            root,
            expected_fragment="PHASE2_CROSS_NON_FILE_PATHS_START",
        )
        (root / FIXTURE_REL).rmdir()
        case_count += 1
        case_count += 1

        build_self_test_root(root)
        result, output = capture_cross_compile(root, "powerpc-linux-musl", "/bin/true")
        assert result == 1
        assert "PHASE2_CROSS_NOTE=target not listed in fixture" in output
        case_count += 1

        build_self_test_root(root)
        write_fixture(
            root,
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": [123],
            },
        )
        result, output = capture_cross_compile(root, EXPECTED_TARGETS[0], "/bin/true")
        assert result == 1
        assert "PHASE2_CROSS_NOTE=fixture zig_test_files is invalid" in output
        case_count += 1
        assert_run_checker_output_contains(
            root,
            target=EXPECTED_TARGETS[0],
            zig="/bin/true",
            expected_fragment="PHASE2_CROSS_ISSUES_START",
        )
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/fixdep.zig").unlink()
        result, output = capture_cross_compile(root, EXPECTED_TARGETS[0], "/bin/true")
        assert result == 1
        assert "PHASE2_CROSS_FAILED_FILE=scripts/zigux/fixdep.zig" in output
        assert "PHASE2_CROSS_NOTE=zig test path missing on branch: scripts/zigux/fixdep.zig" in output
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/fixdep.zig").unlink()
        (root / "scripts/zigux/fixdep.zig").mkdir(parents=True)
        result, output = capture_cross_compile(root, EXPECTED_TARGETS[0], "/bin/true")
        assert result == 1
        assert "PHASE2_CROSS_FAILED_FILE=scripts/zigux/fixdep.zig" in output
        assert "PHASE2_CROSS_NOTE=zig test path is not a file: scripts/zigux/fixdep.zig" in output
        (root / "scripts/zigux/fixdep.zig").rmdir()
        case_count += 1

        original_probe_required_file = globals()["probe_required_file"]
        try:
            build_self_test_root(root)

            def fail_fixture_probe(path: Path) -> None:
                if path == root / FIXTURE_REL:
                    raise OSError("simulated unreadable fixture")
                original_probe_required_file(path)

            globals()["probe_required_file"] = fail_fixture_probe
            missing = require_files(root)
            assert ("required_file_unreadable", str(FIXTURE_REL)) in missing
            case_count += 1
            assert_run_checker_output_contains(
                root,
                expected_fragment="PHASE2_CROSS_UNREADABLE_FILES_START",
            )
            case_count += 1

            build_self_test_root(root)

            def fail_fixdep_probe(path: Path) -> None:
                if path == root / "scripts/zigux/fixdep.zig":
                    raise OSError("simulated unreadable zig test file")
                original_probe_required_file(path)

            globals()["probe_required_file"] = fail_fixdep_probe
            missing = require_files(root)
            assert ("required_file_unreadable", "scripts/zigux/fixdep.zig") in missing
            case_count += 1
            assert_run_checker_output_contains(
                root,
                expected_fragment="scripts/zigux/fixdep.zig",
            )
            case_count += 1
            result, output = capture_cross_compile(root, EXPECTED_TARGETS[0], "/bin/true")
            assert result == 1
            assert "PHASE2_CROSS_FAILED_FILE=scripts/zigux/fixdep.zig" in output
            assert "PHASE2_CROSS_NOTE=zig test path unreadable on branch: scripts/zigux/fixdep.zig" in output
            case_count += 1
        finally:
            globals()["probe_required_file"] = original_probe_required_file

        build_self_test_root(root)
        (root / FIXTURE_REL).unlink()
        missing = require_files(root)
        assert ("required_file_missing", str(FIXTURE_REL)) in missing
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/fixdep.zig").unlink()
        missing = require_files(root)
        assert ("required_file_missing", "scripts/zigux/fixdep.zig") in missing
        case_count += 1
        assert_run_checker_output_contains(
            root,
            expected_fragment="scripts/zigux/fixdep.zig",
        )
        case_count += 1

        build_self_test_root(root)
        (root / FIXTURE_REL).unlink()
        (root / FIXTURE_REL).mkdir(parents=True)
        issues = require_files(root)
        assert ("required_path_not_file", str(FIXTURE_REL)) in issues
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/fixdep.zig").unlink()
        (root / "scripts/zigux/fixdep.zig").mkdir(parents=True)
        issues = require_files(root)
        assert ("required_path_not_file", "scripts/zigux/fixdep.zig") in issues
        case_count += 1

        build_self_test_root(root)
        assert_run_checker_note_contains(
            root,
            target=EXPECTED_TARGETS[0],
            zig=None,
            expected_fragment="zig not found on PATH",
        )
        case_count += 1

    assert case_count == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 cross-target matrix packet and optionally replay one cross compile target."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument("--target", help="Run cross-target Zig test replays for one configured target.")
    parser.add_argument("--zig", help="Path to the Zig executable for target-mode replays.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_checker(args.root, target=args.target, zig=args.zig)


if __name__ == "__main__":
    raise SystemExit(main())
