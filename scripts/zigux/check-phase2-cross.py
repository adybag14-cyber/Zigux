#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")

EXPECTED_PHASE = "Phase 2"
EXPECTED_LANE = 21
EXPECTED_STATUS = "starter"
EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]
EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]
DEFAULT_ZIG_TIMEOUT_SECONDS = 300


def fixture_path(root: Path) -> Path:
    return root / FIXTURE_REL


def require_files(root: Path) -> list[str]:
    required = [
        FIXTURE_REL,
        Path("scripts/zigux/kconfig/conf_bridge.zig"),
        Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    ]
    return [str(rel) for rel in required if not (root / rel).is_file()]


def load_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def collect_list_issues(payload: object, issue_prefix: str) -> tuple[list[str], list[str] | None]:
    if not isinstance(payload, list):
        return [f"{issue_prefix}:not_list:{payload!r}"], None

    if not all(isinstance(item, str) for item in payload):
        return [f"{issue_prefix}:non_string:{payload!r}"], None

    if any(not item for item in payload):
        return [f"{issue_prefix}:empty_string:{payload!r}"], None

    if len(set(payload)) != len(payload):
        return [f"{issue_prefix}:duplicate_entries:{payload!r}"], None

    return [], payload


def build_matrix_entries(targets: list[str], zig_test_files: list[str]) -> list[str]:
    return [f"{target}:{rel_path}" for target in targets for rel_path in zig_test_files]


def emit_matrix_summary(targets: list[str], zig_test_files: list[str]) -> None:
    matrix_entries = build_matrix_entries(targets, zig_test_files)
    print(f"PHASE2_CROSS_MATRIX_ENTRY_COUNT={len(matrix_entries)}")
    print("PHASE2_CROSS_MATRIX_ENTRIES=" + ",".join(matrix_entries))


def validate_fixture(root: Path) -> list[str]:
    issues: list[str] = []
    payload = load_fixture(fixture_path(root))

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(f"fixture:phase:{payload.get('phase')!r}")

    lane = payload.get("lane")
    if not is_strict_int(lane) or lane != EXPECTED_LANE:
        issues.append(f"fixture:lane:{lane!r}")

    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"fixture:status:{payload.get('status')!r}")

    target_issues, targets = collect_list_issues(payload.get("targets"), "fixture:targets")
    issues.extend(target_issues)
    if targets is not None and targets != EXPECTED_TARGETS:
        issues.append(f"fixture:targets:{targets!r}")

    target_count = payload.get("target_count")
    if not is_strict_int(target_count) or target_count != len(EXPECTED_TARGETS):
        issues.append(f"fixture:target_count:{target_count!r}")
    if targets is not None and (not is_strict_int(target_count) or target_count != len(targets)):
        issues.append(f"fixture:target_count_mismatch:{target_count!r}!={len(targets)!r}")

    zig_file_issues, zig_test_files = collect_list_issues(
        payload.get("zig_test_files"),
        "fixture:zig_test_files",
    )
    issues.extend(zig_file_issues)
    if zig_test_files is not None and zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append(f"fixture:zig_test_files:{zig_test_files!r}")

    return issues


def resolve_zig(override: str | None) -> str | None:
    if override:
        override_path = Path(override)
        if override_path.is_file():
            return override
        return shutil.which(override)
    return shutil.which("zig")


def load_configured_lists(root: Path) -> tuple[list[str], list[str]] | tuple[None, None]:
    payload = load_fixture(fixture_path(root))
    targets = payload.get("targets")
    if not isinstance(targets, list) or not all(isinstance(item, str) for item in targets):
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=fixture targets is invalid")
        return None, None

    zig_test_files = payload.get("zig_test_files")
    if not isinstance(zig_test_files, list) or not all(isinstance(item, str) for item in zig_test_files):
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=fixture zig_test_files is invalid")
        return None, None

    return targets, zig_test_files


def replay_target(
    root: Path,
    target: str,
    zig: str,
    zig_test_files: list[str],
    timeout_seconds: int = DEFAULT_ZIG_TIMEOUT_SECONDS,
) -> int:
    for rel_path in zig_test_files:
        try:
            completed = subprocess.run(
                [zig, "test", rel_path, "-target", target, "--test-no-exec"],
                cwd=root,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_TARGET={target}")
            print(f"PHASE2_CROSS_FAILED_FILE={rel_path}")
            print(f"PHASE2_CROSS_NOTE=zig timed out: {exc}")
            return 1
        except OSError as exc:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_TARGET={target}")
            print(f"PHASE2_CROSS_FAILED_FILE={rel_path}")
            print(f"PHASE2_CROSS_NOTE=failed to execute zig: {exc}")
            return 1
        if completed.returncode != 0:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_TARGET={target}")
            print(f"PHASE2_CROSS_FAILED_FILE={rel_path}")
            return completed.returncode
    return 0


def run_cross_compile(
    root: Path,
    target: str,
    zig: str,
    timeout_seconds: int = DEFAULT_ZIG_TIMEOUT_SECONDS,
) -> int:
    targets, zig_test_files = load_configured_lists(root)
    if targets is None or zig_test_files is None:
        return 1

    if target not in targets:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_TARGET={target}")
        print("PHASE2_CROSS_NOTE=target not listed in fixture")
        return 1

    result = replay_target(root, target, zig, zig_test_files, timeout_seconds=timeout_seconds)
    if result != 0:
        return result

    print("PHASE2_CROSS=pass")
    print("PHASE2_CROSS_REPLAY_MODE=single-target")
    print(f"PHASE2_CROSS_TARGET={target}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")
    emit_matrix_summary([target], zig_test_files)
    return 0


def run_all_targets(
    root: Path,
    zig: str,
    timeout_seconds: int = DEFAULT_ZIG_TIMEOUT_SECONDS,
) -> int:
    targets, zig_test_files = load_configured_lists(root)
    if targets is None or zig_test_files is None:
        return 1

    for target in targets:
        result = replay_target(root, target, zig=zig, zig_test_files=zig_test_files, timeout_seconds=timeout_seconds)
        if result != 0:
            print("PHASE2_CROSS_REPLAY_MODE=all-targets")
            return result

    print("PHASE2_CROSS=pass")
    print("PHASE2_CROSS_REPLAY_MODE=all-targets")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGETS={','.join(targets)}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")
    emit_matrix_summary(targets, zig_test_files)
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        fixture_path(root),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "lane": EXPECTED_LANE,
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / "scripts/zigux/kconfig/conf_bridge.zig", 'test "stub" {}\n')
    write_text(root / "scripts/zigux/kconfig/confdata_bridge.zig", 'test "stub" {}\n')


def make_fake_zig(
    path: Path,
    log_path: Path,
    fail_target: str | None = None,
    sleep_seconds: int | None = None,
) -> None:
    fail_clause = ""
    if fail_target is not None:
        fail_clause = f'case "$*" in *"{fail_target}"*) exit 7 ;; esac\n'
    sleep_clause = ""
    if sleep_seconds is not None:
        sleep_clause = f"sleep {sleep_seconds}\n"
    script = (
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> "{log_path}"\n'
        f"{sleep_clause}"
        f"{fail_clause}"
        "exit 0\n"
    )
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run_main(args: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(args)
    return code, stdout.getvalue()


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_cross_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert require_files(root) == []
        assert validate_fixture(root) == []
        baseline_code, baseline_output = run_main(["--root", str(root)])
        assert baseline_code == 0
        assert "PHASE2_CROSS_MATRIX_ENTRY_COUNT=6" in baseline_output
        assert (
            "PHASE2_CROSS_MATRIX_ENTRIES="
            "x86_64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "x86_64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig,"
            "aarch64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "aarch64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig,"
            "riscv64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "riscv64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig"
        ) in baseline_output
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
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
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
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
        assert f"fixture:target_count_mismatch:{len(EXPECTED_TARGETS)!r}!={len(EXPECTED_TARGETS[:-1])!r}" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": str(len(EXPECTED_TARGETS)),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert f"fixture:target_count:{str(len(EXPECTED_TARGETS))!r}" in issues
        assert f"fixture:target_count_mismatch:{str(len(EXPECTED_TARGETS))!r}!={len(EXPECTED_TARGETS)!r}" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": float(len(EXPECTED_TARGETS)),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert f"fixture:target_count:{float(len(EXPECTED_TARGETS))!r}" in issues
        assert f"fixture:target_count_mismatch:{float(len(EXPECTED_TARGETS))!r}!={len(EXPECTED_TARGETS)!r}" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
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
        assert "fixture:phase:'Phase 3'" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": 20,
                    "status": EXPECTED_STATUS,
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
        assert "fixture:lane:20" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": float(EXPECTED_LANE),
                    "status": EXPECTED_STATUS,
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
        assert f"fixture:lane:{float(EXPECTED_LANE)!r}" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": "x86_64-linux-musl",
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:not_list:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": [EXPECTED_TARGETS[0], 7, EXPECTED_TARGETS[2]],
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:non_string:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": [EXPECTED_TARGETS[0], "", EXPECTED_TARGETS[2]],
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:empty_string:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": "closed",
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
        assert "fixture:status:'closed'" in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": [EXPECTED_TARGETS[0], EXPECTED_TARGETS[0], EXPECTED_TARGETS[2]],
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:duplicate_entries:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": "scripts/zigux/kconfig/conf_bridge.zig",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:zig_test_files:not_list:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": [EXPECTED_ZIG_TEST_FILES[0], 7],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:zig_test_files:non_string:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": [
                        EXPECTED_ZIG_TEST_FILES[0],
                        "scripts/zigux/kconfig/other_bridge.zig",
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert (
            "fixture:zig_test_files:['scripts/zigux/kconfig/conf_bridge.zig', 'scripts/zigux/kconfig/other_bridge.zig']"
        ) in issues
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).writeText(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": [
                        EXPECTED_ZIG_TEST_FILES[0],
                        EXPECTED_ZIG_TEST_FILES[0],
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:zig_test_files:duplicate_entries:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (fixture_path(root)).write_text(
            json.dumps(
                {
                    "phase": EXPECTED_PHASE,
                    "lane": EXPECTED_LANE,
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": [EXPECTED_ZIG_TEST_FILES[0], ""],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:zig_test_files:empty_string:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/kconfig/conf_bridge.zig").unlink()
        missing = require_files(root)
        assert "scripts/zigux/kconfig/conf_bridge.zig" in missing
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/kconfig/confdata_bridge.zig").unlink()
        missing = require_files(root)
        assert "scripts/zigux/kconfig/confdata_bridge.zig" in missing
        case_count += 1

        build_self_test_root(root)
        success_log = root / "success-zig.log"
        success_zig = root / "fake-zig-success.sh"
        make_fake_zig(success_zig, success_log)
        all_targets_code, all_targets_output = run_main(
            ["--root", str(root), "--all-targets", "--zig", str(success_zig)]
        )
        assert all_targets_code == 0
        success_lines = success_log.read_text(encoding="utf-8").splitlines()
        assert len(success_lines) == len(EXPECTED_TARGETS) * len(EXPECTED_ZIG_TEST_FILES)
        assert any("-target x86_64-linux-musl --test-no-exec" in line for line in success_lines)
        assert any("-target aarch64-linux-musl --test-no-exec" in line for line in success_lines)
        assert any("-target riscv64-linux-musl --test-no-exec" in line for line in success_lines)
        assert "PHASE2_CROSS_MATRIX_ENTRY_COUNT=6" in all_targets_output
        assert (
            "PHASE2_CROSS_MATRIX_ENTRIES="
            "x86_64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "x86_64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig,"
            "aarch64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "aarch64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig,"
            "riscv64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "riscv64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig"
        ) in all_targets_output
        case_count += 1

        build_self_test_root(root)
        fail_log = root / "fail-zig.log"
        fail_zig = root / "fake-zig-fail.sh"
        make_fake_zig(fail_zig, fail_log, fail_target="riscv64-linux-musl")
        assert run_all_targets(root, str(fail_zig)) == 7
        fail_lines = fail_log.read_text(encoding="utf-8").splitlines()
        assert any("-target riscv64-linux-musl --test-no-exec" in line for line in fail_lines)
        case_count += 1

        build_self_test_root(root)
        single_log = root / "single-zig.log"
        single_zig = root / "fake-zig-single.sh"
        make_fake_zig(single_zig, single_log)
        single_code, single_output = run_main(
            ["--root", str(root), "--target", EXPECTED_TARGETS[1], "--zig", str(single_zig)]
        )
        assert single_code == 0
        single_lines = single_log.read_text(encoding="utf-8").splitlines()
        assert len(single_lines) == len(EXPECTED_ZIG_TEST_FILES)
        assert all(f"-target {EXPECTED_TARGETS[1]} --test-no-exec" in line for line in single_lines)
        assert "PHASE2_CROSS_MATRIX_ENTRY_COUNT=2" in single_output
        assert (
            "PHASE2_CROSS_MATRIX_ENTRIES="
            "aarch64-linux-musl:scripts/zigux/kconfig/conf_bridge.zig,"
            "aarch64-linux-musl:scripts/zigux/kconfig/confdata_bridge.zig"
        ) in single_output
        case_count += 1

        build_self_test_root(root)
        single_fail_log = root / "single-fail-zig.log"
        single_fail_zig = root / "fake-zig-single-fail.sh"
        make_fake_zig(single_fail_zig, single_fail_log, fail_target=EXPECTED_TARGETS[1])
        single_fail_code, single_fail_output = run_main(
            ["--root", str(root), "--target", EXPECTED_TARGETS[1], "--zig", str(single_fail_zig)]
        )
        assert single_fail_code == 7
        assert f"PHASE2_CROSS_TARGET={EXPECTED_TARGETS[1]}" in single_fail_output
        assert f"PHASE2_CROSS_FAILED_FILE={EXPECTED_ZIG_TEST_FILES[0]}" in single_fail_output
        case_count += 1

        build_self_test_root(root)
        timeout_log = root / "timeout-zig.log"
        timeout_zig = root / "fake-zig-timeout.sh"
        make_fake_zig(timeout_zig, timeout_log, sleep_seconds=2)
        timeout_code, timeout_output = run_main(
            [
                "--root",
                str(root),
                "--target",
                EXPECTED_TARGETS[0],
                "--zig",
                str(timeout_zig),
                "--timeout-seconds",
                "1",
            ]
        )
        assert timeout_code == 1
        assert "PHASE2_CROSS_NOTE=zig timed out:" in timeout_output
        assert f"PHASE2_CROSS_TARGET={EXPECTED_TARGETS[0]}" in timeout_output
        assert f"PHASE2_CROSS_FAILED_FILE={EXPECTED_ZIG_TEST_FILES[0]}" in timeout_output
        case_count += 1

        build_self_test_root(root)
        missing_target_code, missing_target_output = run_main(
            ["--root", str(root), "--target", "powerpc64-linux-musl", "--zig", "/bin/true"]
        )
        assert missing_target_code == 1
        assert "PHASE2_CROSS_NOTE=target not listed in fixture" in missing_target_output
        case_count += 1

        build_self_test_root(root)
        both_flags_code, both_flags_output = run_main(
            [
                "--root",
                str(root),
                "--target",
                EXPECTED_TARGETS[0],
                "--all-targets",
                "--zig",
                "/bin/true",
            ]
        )
        assert both_flags_code == 1
        assert "PHASE2_CROSS_NOTE=choose either --target or --all-targets" in both_flags_output
        case_count += 1

        build_self_test_root(root)
        missing_zig_code, missing_zig_output = run_main(
            ["--root", str(root), "--target", EXPECTED_TARGETS[0], "--zig", str(root / "missing-zig")]
        )
        assert missing_zig_code == 1
        assert "PHASE2_CROSS_NOTE=zig not found on PATH" in missing_zig_output
        case_count += 1

        build_self_test_root(root)
        missing_zig_path = root / "missing-zig"
        missing_zig_code, missing_zig_output = run_main(
            ["--root", str(root), "--all-targets", "--zig", str(missing_zig_path)]
        )
        assert missing_zig_code == 1
        assert "PHASE2_CROSS_NOTE=zig not found on PATH" in missing_zig_output
        case_count += 1

        build_self_test_root(root)
        invalid_exec = root / "not-executable-zig"
        invalid_exec.write_text("not executable\n", encoding="utf-8")
        invalid_exec_code, invalid_exec_output = run_main(
            ["--root", str(root), "--target", EXPECTED_TARGETS[0], "--zig", str(invalid_exec)]
        )
        assert invalid_exec_code == 1
        assert "PHASE2_CROSS_NOTE=failed to execute zig:" in invalid_exec_output
        assert f"PHASE2_CROSS_TARGET={EXPECTED_TARGETS[0]}" in invalid_exec_output
        assert f"PHASE2_CROSS_FAILED_FILE={EXPECTED_ZIG_TEST_FILES[0]}" in invalid_exec_output
        case_count += 1

        build_self_test_root(root)
        broken_fixture = fixture_path(root)
        broken_fixture.write_text("{not-json}\n", encoding="utf-8")
        invalid_json_code, invalid_json_output = run_main(["--root", str(root)])
        assert invalid_json_code == 1
        assert "PHASE2_CROSS_NOTE=invalid fixture JSON:" in invalid_json_output
        case_count += 1

        build_self_test_root(root)
        non_object_fixture = fixture_path(root)
        non_object_fixture.write_text('["not-an-object"]\n', encoding="utf-8")
        non_object_code, non_object_output = run_main(["--root", str(root)])
        assert non_object_code == 1
        assert "PHASE2_CROSS_NOTE=fixture must be a JSON object" in non_object_output
        case_count += 1

    print("PHASE2_CROSS_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current-master-safe Phase 2 cross-target starter packet and optionally replay one target or the full starter matrix."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--target", help="Run the configured Zig test files for one target.")
    parser.add_argument("--all-targets", action="store_true", help="Run the configured Zig test files for every listed target.")
    parser.add_argument("--zig", help="Path to the Zig executable for target-mode replays.")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_ZIG_TIMEOUT_SECONDS,
        help="Per-target timeout for Zig target-mode replays.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    missing = require_files(root)
    if missing:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_MISSING_FILES_START")
        for rel_path in missing:
            print(rel_path)
        print("PHASE2_CROSS_MISSING_FILES_END")
        return 1

    try:
        issues = validate_fixture(root)
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

    if args.target and args.all_targets:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=choose either --target or --all-targets")
        return 1

    if args.target or args.all_targets:
        zig = resolve_zig(args.zig)
        if zig is None:
            print("PHASE2_CROSS=fail")
            print("PHASE2_CROSS_NOTE=zig not found on PATH")
            return 1

        if args.target:
            return run_cross_compile(root, args.target, zig, timeout_seconds=args.timeout_seconds)
        return run_all_targets(root, zig, timeout_seconds=args.timeout_seconds)

    payload = load_fixture(fixture_path(root))
    targets = payload["targets"]
    zig_test_files = payload["zig_test_files"]
    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGETS={','.join(targets)}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")
    emit_matrix_summary(targets, zig_test_files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())