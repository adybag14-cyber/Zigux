#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_STATUS = "closed"
EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate key {key!r}")
        payload[key] = value
    return payload


def require_files(root: Path) -> list[str]:
    required = [Path("zigux/tests/fixtures/phase2_cross_targets.json")]
    required.extend(Path(rel_path) for rel_path in EXPECTED_ZIG_TEST_FILES)
    return [str(rel) for rel in required if not (root / rel).is_file()]


def load_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_json_keys,
    )
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def load_toolchain_policy_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:
    if not policy_path.exists():
        return None
    try:
        payload = json.loads(
            policy_path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
        )
    except ValueError as exc:
        raise ValueError(f"invalid toolchain policy JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("toolchain policy must be a JSON object")
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel:
        raise ValueError("toolchain policy channel must be a non-empty string")
    return channel


def iter_repo_local_zig_candidates(
    *,
    root: Path = ROOT,
    pinned_channel: str | None = None,
) -> list[Path]:
    toolchain_root = root / ".zig-toolchain"
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    if pinned_channel is not None:
        pinned_root = toolchain_root / f"zig-x86_64-linux-{pinned_channel}"
        add_candidate(pinned_root / "zig")
        add_candidate(pinned_root / "bin" / "zig")

    if toolchain_root.exists():
        for child in sorted(toolchain_root.iterdir()):
            add_candidate(child / "zig")
            add_candidate(child / "bin" / "zig")
    return candidates


def resolve_zig_executable(
    explicit_zig: str | None = None,
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
    which=shutil.which,
) -> str | None:
    if explicit_zig is not None:
        return explicit_zig

    pinned_channel = load_toolchain_policy_channel(policy_path) if policy_path.exists() else None
    for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):
        if candidate.is_file():
            return str(candidate)
    return which("zig")


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


def run_toolchain_preflight(
    root: Path,
    zig_executable: str,
    *,
    runner=subprocess.run,
) -> str | None:
    try:
        completed = runner(
            [sys.executable, str(root / "scripts" / "zigux" / "check-zig-toolchain.py"), "--zig", zig_executable],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return f"toolchain preflight failed: {exc}"
    except OSError as exc:
        return f"toolchain preflight failed: {exc}"

    if completed.returncode == 0:
        return None

    detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
    return f"toolchain preflight failed: {detail}"


def run_cross_compile(
    root: Path,
    target: str,
    zig_executable: str | None = None,
    *,
    toolchain_runner=subprocess.run,
    zig_runner=subprocess.run,
) -> int:
    try:
        zig = resolve_zig_executable(zig_executable, root=root)
    except ValueError as exc:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_NOTE={exc}")
        return 1

    if zig is None:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=zig not found on PATH or in repo-local .zig-toolchain")
        return 1

    toolchain_note = run_toolchain_preflight(root, zig, runner=toolchain_runner)
    if toolchain_note is not None:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_TARGET={target}")
        print(f"PHASE2_CROSS_NOTE={toolchain_note}")
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
        completed = zig_runner(
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
    for rel_path in EXPECTED_ZIG_TEST_FILES:
        write_text(root / rel_path, 'test "stub" {}\n')


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
                    "phase": "Phase 3",
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
        (root / "zigux/tests/fixtures/phase2_cross_targets.json").writeText if False else None
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
                    "status": EXPECTED_STATUS,
                    "target_count": len(EXPECTED_TARGETS),
                    "targets": EXPECTED_TARGETS,
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES[:-1],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert (
            "fixture:zig_test_files:"
            f"{EXPECTED_ZIG_TEST_FILES[:-1]!r}"
        ) in issues
        case_count += 1

        for rel_path in EXPECTED_ZIG_TEST_FILES:
            build_self_test_root(root)
            (root / rel_path).unlink()
            missing = require_files(root)
            assert rel_path in missing
            case_count += 1

        build_self_test_root(root)
        assert load_toolchain_policy_channel(root / "scripts/zigux/zig-toolchain-policy.json") is None
        case_count += 1

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/zig-toolchain-policy.json",
            json.dumps({"channel": "0.17.0-dev.87+9b177a7d2"}) + "\n",
        )
        pinned_root = root / ".zig-toolchain/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2"
        writeText if False else None
        write_text(pinned_root / "zig", "#!/bin/sh\n")
        resolved = resolve_zig_executable(root=root, policy_path=root / "scripts/zigux/zig-toolchain-policy.json", which=lambda _: "/usr/bin/zig")
        assert resolved == str(pinned_root / "zig")
        case_count += 1

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/zig-toolchain-policy.json",
            json.dumps({"channel": "0.17.0-dev.87+9b177a7d2"}) + "\n",
        )
        pinned_root = root / ".zig-toolchain/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2"
        if pinned_root.exists():
            shutil.rmtree(pinned_root)
        fallback_root = root / ".zig-toolchain/fallback/bin"
        write_text(fallback_root / "zig", "#!/bin/sh\n")
        resolved = resolve_zig_executable(root=root, policy_path=root / "scripts/zigux/zig-toolchain-policy.json", which=lambda _: "/usr/bin/zig")
        assert resolved == str(fallback_root / "zig")
        case_count += 1

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/zig-toolchain-policy.json",
            json.dumps({"channel": 7}) + "\n",
        )
        try:
            resolve_zig_executable(root=root, policy_path=root / "scripts/zigux/zig-toolchain-policy.json", which=lambda _: None)
        except ValueError as exc:
            assert "toolchain policy channel must be a non-empty string" in str(exc)
        else:
            raise AssertionError("expected invalid toolchain policy to fail")
        case_count += 1

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/zig-toolchain-policy.json",
            '{"channel":"0.17.0-dev.87+9b177a7d2","channel":"0.18.0"}\n',
        )
        try:
            resolve_zig_executable(
                root=root,
                policy_path=root / "scripts/zigux/zig-toolchain-policy.json",
                which=lambda _: None,
            )
        except ValueError as exc:
            assert "invalid toolchain policy JSON: duplicate key 'channel'" in str(exc)
        else:
            raise AssertionError("expected duplicate toolchain policy key to fail")
        case_count += 1

        build_self_test_root(root)
        assert resolve_zig_executable("/custom/zig", root=root, which=lambda _: None) == "/custom/zig"
        case_count += 1

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/fixtures/phase2_cross_targets.json",
            '{"phase":"Phase 2","phase":"Phase 3","status":"closed","target_count":3,"targets":["x86_64-linux-musl","aarch64-linux-musl","riscv64-linux-musl"],"zig_test_files":["scripts/zigux/fixdep.zig","scripts/zigux/genksyms.zig","scripts/zigux/kconfig/conf_bridge.zig","scripts/zigux/kconfig/confdata_bridge.zig"]}\n',
        )
        try:
            validate_fixture(root)
        except ValueError as exc:
            assert "duplicate key 'phase'" in str(exc)
        else:
            raise AssertionError("expected duplicate fixture key to fail")
        case_count += 1

        preflight_ok = run_toolchain_preflight(
            root,
            "/custom/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, stdout="ok\n", stderr=""),
        )
        assert preflight_ok is None
        case_count += 1

        preflight_stdout_failure = run_toolchain_preflight(
            root,
            "/custom/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                1,
                stdout="ZIG_TOOLCHAIN_NOTE=expected pinned Zig channel 0.17.0-dev.87+9b177a7d2\n",
                stderr="",
            ),
        )
        assert preflight_stdout_failure == (
            "toolchain preflight failed: ZIG_TOOLCHAIN_NOTE=expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"
        )
        case_count += 1

        preflight_stderr_failure = run_toolchain_preflight(
            root,
            "/custom/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                1,
                stdout="",
                stderr="permission denied\n",
            ),
        )
        assert preflight_stderr_failure == "toolchain preflight failed: permission denied"
        case_count += 1

        preflight_exec_failure = run_toolchain_preflight(
            root,
            "/custom/zig",
            runner=lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError("missing checker")),
        )
        assert preflight_exec_failure == "toolchain preflight failed: missing checker"
        case_count += 1

        build_self_test_root(root)
        success_output = io.StringIO()
        zig_invocations: list[list[str]] = []

        def success_zig_runner(command, cwd, check=False):
            zig_invocations.append(command)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with contextlib.redirect_stdout(success_output):
            success_rc = run_cross_compile(
                root,
                EXPECTED_TARGETS[0],
                zig_executable="/custom/zig",
                toolchain_runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                    args[0], 0, stdout="ZIG_TOOLCHAIN_STATUS=present\n", stderr=""
                ),
                zig_runner=success_zig_runner,
            )
        assert success_rc == 0
        assert "PHASE2_CROSS=pass" in success_output.getvalue()
        assert len(zig_invocations) == len(EXPECTED_ZIG_TEST_FILES)
        case_count += 1

        build_self_test_root(root)
        preflight_failure_output = io.StringIO()
        with contextlib.redirect_stdout(preflight_failure_output):
            preflight_failure_rc = run_cross_compile(
                root,
                EXPECTED_TARGETS[0],
                zig_executable="/custom/zig",
                toolchain_runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                    args[0],
                    1,
                    stdout="ZIG_TOOLCHAIN_NOTE=expected pinned Zig channel 0.17.0-dev.87+9b177a7d2\n",
                    stderr="",
                ),
                zig_runner=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("zig runner should not execute")),
            )
        assert preflight_failure_rc == 1
        assert "PHASE2_CROSS=fail" in preflight_failure_output.getvalue()
        assert (
            "PHASE2_CROSS_NOTE=toolchain preflight failed: ZIG_TOOLCHAIN_NOTE=expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"
            in preflight_failure_output.getvalue()
        )
        case_count += 1

    assert case_count == 22
    print("PHASE2_CROSS_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 cross-target matrix packet and optionally replay one cross compile target."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument("--target", help="Run cross-target Zig test replays for one configured target.")
    parser.add_argument("--zig", help="Explicit zig executable path.")
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
        return run_cross_compile(ROOT, args.target, args.zig)

    payload = load_fixture(FIXTURE)
    targets = payload["targets"]
    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGETS={','.join(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
