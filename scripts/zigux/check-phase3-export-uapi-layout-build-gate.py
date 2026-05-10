#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

BUILD_REL = "zigux/tests/phase3_export_uapi_layout_build.zig"
TEST_REL = "zigux/tests/phase3_export_uapi_layout.zig"
BUILD_STEP_NAME = "phase3-export-uapi-layout-test"
BUILD_STEP = f'b.step("{BUILD_STEP_NAME}"'


def _normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()
        if line.startswith("`") and line.endswith("`") and len(line) >= 2:
            line = line[1:-1]
        lines.append(line)
    return lines


def _exact_line_count(text: str, marker: str) -> int:
    return Counter(_normalized_lines(text)).get(marker, 0)


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    build_path = root / BUILD_REL
    test_path = root / TEST_REL

    try:
        build_text = build_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_build_file:{BUILD_REL}")
    else:
        if BUILD_STEP not in build_text:
            issues.append(f"missing_build_step:{BUILD_REL}:{BUILD_STEP_NAME}")
        marker_count = _exact_line_count(
            build_text,
            f'const test_step = b.step("{BUILD_STEP_NAME}", "Run Phase 3 export shim and uapi layout tests");',
        )
        if marker_count == 0:
            issues.append(f"missing_step_decl:{BUILD_REL}:{BUILD_STEP_NAME}")
        elif marker_count != 1:
            issues.append(f"duplicate_step_decl:{BUILD_REL}:{BUILD_STEP_NAME}:{marker_count}")

    if not test_path.exists():
        issues.append(f"missing_layout_test:{TEST_REL}")

    return issues


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def run_build_smoke(root: Path, zig: str) -> list[str]:
    build_path = root / BUILD_REL
    completed = subprocess.run(
        [zig, "build", BUILD_STEP_NAME, "--build-file", str(build_path)],
        cwd=str(root),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0:
        return []

    stderr = completed.stderr.strip().replace("\n", " | ")
    stdout = completed.stdout.strip().replace("\n", " | ")
    detail = stderr or stdout or f"rc={completed.returncode}"
    return [f"build_smoke_failed:{BUILD_STEP_NAME}:{detail}"]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _fake_zig(path: Path, argv_log: Path, exit_code: int) -> None:
    _write(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "",
                "import pathlib",
                "import sys",
                "",
                f'pathlib.Path(r"{argv_log}").write_text("\\n".join(sys.argv[1:]), encoding="utf-8")',
                f"raise SystemExit({exit_code})",
                "",
            ]
        ),
    )
    path.chmod(0o755)


def _baseline_root(root: Path) -> None:
    _write(
        root / BUILD_REL,
        "\n".join(
            [
                "const std = @import(\"std\");",
                "",
                "pub fn build(b: *std.Build) void {",
                '    const test_step = b.step("phase3-export-uapi-layout-test", "Run Phase 3 export shim and uapi layout tests");',
                "    _ = test_step;",
                '    _ = b.step("phase3-export-uapi-layout-test", "Run Phase 3 export shim and uapi layout tests");',
                "}",
                "",
            ]
        ).replace(
            '_ = b.step("phase3-export-uapi-layout-test", "Run Phase 3 export shim and uapi layout tests");',
            '    const run_step = b.step("phase3-export-uapi-layout-test", "Run Phase 3 export shim and uapi layout tests");',
            1,
        ),
    )
    _write(root / TEST_REL, "const std = @import(\"std\");\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase3_export_uapi_layout_build_gate_") as tmp:
        root = Path(tmp)
        _baseline_root(root)
        assert validate(root) == []
        case_count += 1

        _write(root / BUILD_REL, "const std = @import(\"std\");\n")
        issues = validate(root)
        assert f"missing_build_step:{BUILD_REL}:{BUILD_STEP_NAME}" in issues
        assert f"missing_step_decl:{BUILD_REL}:{BUILD_STEP_NAME}" in issues
        case_count += 1

        _baseline_root(root)
        (root / TEST_REL).unlink()
        issues = validate(root)
        assert f"missing_layout_test:{TEST_REL}" in issues
        case_count += 1

        _baseline_root(root)
        argv_log = root / "zig.argv"
        fake_zig = root / "fake-zig"
        _fake_zig(fake_zig, argv_log, 0)
        assert run_build_smoke(root, str(fake_zig)) == []
        assert argv_log.read_text(encoding="utf-8").splitlines() == [
            "build",
            BUILD_STEP_NAME,
            "--build-file",
            str(root / BUILD_REL),
        ]
        case_count += 1

        _baseline_root(root)
        failing_log = root / "zig.fail.argv"
        failing_zig = root / "fake-zig-fail"
        _fake_zig(failing_zig, failing_log, 7)
        issues = run_build_smoke(root, str(failing_zig))
        assert issues == [f"build_smoke_failed:{BUILD_STEP_NAME}:rc=7"]
        case_count += 1

    print("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_GATE_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_LAYOUT_BUILD_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 export/UAPI layout build gate."
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Path to the Zigux repository root.",
    )
    parser.add_argument(
        "--check-build-smoke",
        action="store_true",
        help="Run the focused export/UAPI layout build step with zig after static checks pass.",
    )
    parser.add_argument("--zig", help="Explicit zig executable path for --check-build-smoke.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage without needing a repository checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.repo_root).resolve()
    issues = validate(root)
    if not issues and args.check_build_smoke:
        issues.extend(run_build_smoke(root, find_zig(args.zig)))

    if issues:
        print("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_GATE=fail")
        print("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_GATE_ISSUES_END")
        return 1

    print("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_GATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
