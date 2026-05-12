#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_STATUS = "closed"
EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/fixdep.zig",
]


def require_files(root: Path) -> list[str]:
    required = [
        Path("zigux/tests/fixtures/phase2_cross_targets.json"),
        Path("scripts/zigux/fixdep.zig"),
    ]
    return [str(rel) for rel in required if not (root / rel).is_file()]


def load_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def validate_fixture(root: Path) -> list[str]:
    issues: list[str] = []
    payload = load_fixture(root / "zigux/tests/fixtures/phase2_cross_targets.json")

    if payload.get("phase") != "Phase 2":
        issues.append(f"fixture:phase:{payload.get('phase')!r}")

    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"fixture:status:{payload.get('status')!r}")

    targets = payload.get("targets")
    if targets != EXPECTED_TARGETS:
        issues.append(f"fixture:targets:{targets!r}")

    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(f"fixture:target_count:{payload.get('target_count')!r}")

    zig_test_files = payload.get("zig_test_files")
    if zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append(f"fixture:zig_test_files:{zig_test_files!r}")
    return issues


def run_cross_compile(root: Path, target: str) -> int:
    zig = shutil.which("zig")
    if zig is None:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=zig not found on PATH")
        return 1

    payload = load_fixture(root / "zigux/tests/fixtures/phase2_cross_targets.json")
    targets = payload.get("targets")
    if not isinstance(targets, list) or target not in targets:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_TARGET={target}")
        print("PHASE2_CROSS_NOTE=target not listed in fixture")
        return 1

    zig_test_files = payload.get("zig_test_files")
    if not isinstance(zig_test_files, list) or not all(
        isinstance(item, str) for item in zig_test_files
    ):
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=fixture zig_test_files is invalid")
        return 1

    for rel_path in zig_test_files:
        completed = subprocess.run(
            [zig, "test", rel_path, "-target", target],
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "zigux/tests/fixtures/phase2_cross_targets.json",
        json.dumps(
            {
                "phase": "Phase 2",
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / "scripts/zigux/fixdep.zig", 'test "stub" {}\n')


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_cross_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert require_files(root) == []
        assert validate_fixture(root) == []
        case_count += 1

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/phase2_cross_targets.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "status": EXPECTED_STATUS,
                    "target_count": 2,
                    "targets": EXPECTED_TARGETS[:-1],
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:") for issue in issues)
        assert "fixture:target_count:2" in issues
        case_count += 1

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/phase2_cross_targets.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "status": "open",
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert "fixture:status:'open'" in issues
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
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument("--target", help="Run cross-target Zig test replays for one configured target.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = require_files(ROOT)
    if missing:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_MISSING_FILES_START")
        for rel_path in missing:
            print(rel_path)
        print("PHASE2_CROSS_MISSING_FILES_END")
        return 1

    try:
        issues = validate_fixture(ROOT)
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
        return run_cross_compile(ROOT, args.target)

    payload = load_fixture(FIXTURE)
    targets = payload["targets"]
    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGETS={','.join(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
