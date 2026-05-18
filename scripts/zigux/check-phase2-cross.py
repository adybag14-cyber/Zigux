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


def require_files(root: Path) -> list[str]:
    required = [
        FIXTURE_REL,
        Path("scripts/zigux/fixdep.zig"),
    ]
    return [str(rel) for rel in required if not (root / rel).is_file()]


def load_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def collect_duplicate_entries(values: object, prefix: str) -> list[str]:
    if not isinstance(values, list):
        return []

    counts: dict[str, int] = {}
    for value in values:
        key = value if isinstance(value, str) else repr(value)
        counts[key] = counts.get(key, 0) + 1
    return [f"{prefix}:{key}:count={count}" for key, count in counts.items() if count > 1]


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
    if targets != EXPECTED_TARGETS:
        issues.append(f"fixture:targets:{targets!r}")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(f"fixture:target_count:{payload.get('target_count')!r}")
    issues.extend(collect_duplicate_entries(targets, "fixture:duplicate_target"))

    zig_test_files = payload.get("zig_test_files")
    if zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append(f"fixture:zig_test_files:{zig_test_files!r}")
    issues.extend(collect_duplicate_entries(zig_test_files, "fixture:duplicate_zig_test_file"))
    return issues


def resolve_zig(override: str | None) -> str | None:
    if override:
        return override
    return shutil.which("zig")


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
        try:
            validate_fixture(root)
        except json.JSONDecodeError:
            case_count += 1
        else:
            raise AssertionError("invalid JSON did not raise JSONDecodeError")

        build_self_test_root(root)
        write_fixture(root, ["not", "an", "object"])
        try:
            validate_fixture(root)
        except ValueError as exc:
            assert str(exc) == "fixture must be a JSON object"
            case_count += 1
        else:
            raise AssertionError("non-object fixture did not raise ValueError")

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

        build_self_test_root(root)
        (root / FIXTURE_REL).unlink()
        missing = require_files(root)
        assert str(FIXTURE_REL) in missing
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/fixdep.zig").unlink()
        missing = require_files(root)
        assert "scripts/zigux/fixdep.zig" in missing
        case_count += 1

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

    missing = require_files(args.root)
    if missing:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_MISSING_FILES_START")
        for rel_path in missing:
            print(rel_path)
        print("PHASE2_CROSS_MISSING_FILES_END")
        return 1

    try:
        issues = validate_fixture(args.root)
    except json.JSONDecodeError as exc:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_NOTE=invalid fixture JSON: {exc.msg}")
        return 1
    except ValueError as exc:
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

    if args.target:
        zig = resolve_zig(args.zig)
        if zig is None:
            print("PHASE2_CROSS=fail")
            print("PHASE2_CROSS_NOTE=zig not found on PATH")
            return 1
        return run_cross_compile(args.root, args.target, zig)

    return summarize_packet(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
