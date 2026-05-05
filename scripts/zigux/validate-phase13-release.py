#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
]

MAKE_REQUIRED_LINES = [
    "phase13-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
    "phase13: phase13-validate phase13-test",
]

MAKE_FORBIDDEN_LINES = [
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-release-replay-exact-counts.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _collect_missing_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    makefile = _read(root / "zigux/Makefile")

    issues.extend(_collect_missing_markers(makefile, MAKE_REQUIRED_LINES, "makefile"))
    for forbidden in MAKE_FORBIDDEN_LINES:
        if forbidden in makefile:
            issues.append(f"makefile:forbidden_route:{forbidden}")
    return issues


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "phase13-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
            "",
            "phase13-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase13_build.zig",
            "",
            "phase13: phase13-validate phase13-test",
            "",
        )
    )


def _seed_fixture_tree(root: Path) -> None:
    _write(root / "zigux/Makefile", _baseline_makefile())
    for rel in REQUIRED_FILES[1:]:
        _write(root / rel, "// stub\n" if rel.endswith(".zig") else "{}\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase13-release-validator-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_release_validator_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        baseline_makefile = _read(makefile_path)
        makefile_path.write_text(
            baseline_makefile + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["makefile:forbidden_route:scripts/zigux/check-phase13-devres-packet.py"],
            "forbidden_makefile_route_guard_failed",
        )
        makefile_path.write_text(baseline_makefile, encoding="utf-8")
        case_count += 1

        _write(root / "zigux/Makefile", "phase13-test:\n\t@true\n")
        _assert_only(
            validate(root),
            [
                "makefile:phase13-validate:",
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
                "makefile:phase13: phase13-validate phase13-test",
            ],
            "missing_makefile_marker_guard_failed",
        )
        _write(root / "zigux/Makefile", baseline_makefile)
        case_count += 1

        (root / "zigux/tests/phase13_landlock_syscalls_manifest.json").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_landlock_syscalls_manifest.json"],
            "missing_required_file_guard_failed",
        )
        _write(root / "zigux/tests/phase13_landlock_syscalls_manifest.json", "{}\n")
        case_count += 1

    print("PHASE13_RELEASE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current shipped Phase 13 release packet surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE13_RELEASE_VALIDATION=fail")
        print("PHASE13_RELEASE_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE13_RELEASE_VALIDATION_ISSUES_END")
        return 1

    print("PHASE13_RELEASE_VALIDATION=pass")
    print(
        "PHASE13_RELEASE_VALIDATION_MARKER_COUNT="
        f"{len(REQUIRED_FILES) + len(MAKE_REQUIRED_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
