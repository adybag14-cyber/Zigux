#!/usr/bin/env python3
"""Fail-close the focused Phase 3 ABI replay route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("include/linux/zigux.h"),
    Path("include/zigux/abi.h"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/abi.zig"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    ABI_MANIFEST_PATH,
    Path("scripts/zigux/validate-phase3.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
)
REQUIRED_MANIFEST_ENTRIES = (
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
)

# The export/UAPI lane explicitly keeps these dedicated replay files out of the
# current shared ABI packet until they land with the rest of that packet.
OPTIONAL_EXPORT_UAPI_REPLAY_FILES = (
    Path("zigux/tests/phase3_export_uapi.zig"),
    Path("zigux/tests/phase3_export_uapi_layout.zig"),
)

MAKEFILE_PATH = Path("zigux/Makefile")
RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")
CHECK_LIB_PATH = Path("scripts/zigux/phase3_check_lib.py")
MAKE_MARKERS = (
    "phase3-abi:",
    "$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
)
RUNNER_MARKERS = (
    "from phase3_check_lib import run_phase3_slice_entry",
    "return run_phase3_slice_entry(entry, root=root)",
)
CHECK_LIB_MARKERS = (
    'if slug == "abi":',
    '(sys.executable, "scripts/zigux/check-phase3-abi.py"),',
    '("zig", "build", "phase3-test", "--build-file", "zigux/tests/build.zig"),',
    '("zig", "build", "phase3-dump", "--build-file", "zigux/tests/build.zig"),',
    "def run_phase3_slice_entry(",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_manifest_entries(repo_root: Path) -> list[str]:
    manifest_path = repo_root / ABI_MANIFEST_PATH
    if not manifest_path.is_file():
        return []

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid phase3 ABI manifest JSON: {exc.msg}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return ["invalid phase3 ABI manifest files list"]

    issues: list[str] = []
    file_entries: set[str] = set()
    for entry in files:
        if not isinstance(entry, str):
            issues.append(f"invalid phase3 ABI manifest file entry: {entry!r}")
            continue
        file_entries.add(entry)

    for rel_path in REQUIRED_MANIFEST_ENTRIES:
        if rel_path.as_posix() not in file_entries:
            issues.append(f"missing phase3 ABI manifest entry: {rel_path.as_posix()}")

    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    makefile_path = repo_root / MAKEFILE_PATH
    if not makefile_path.is_file():
        issues.append(f"missing repo file: {MAKEFILE_PATH.as_posix()}")
    else:
        makefile_text = _read(makefile_path)
        for marker in MAKE_MARKERS:
            if marker not in makefile_text:
                issues.append(f"missing make marker: {marker}")

    runner_path = repo_root / RUNNER_PATH
    if runner_path.is_file():
        runner_text = _read(runner_path)
        for marker in RUNNER_MARKERS:
            if marker not in runner_text:
                issues.append(f"missing runner marker: {marker}")

    check_lib_path = repo_root / CHECK_LIB_PATH
    if check_lib_path.is_file():
        check_lib_text = _read(check_lib_path)
        for marker in CHECK_LIB_MARKERS:
            if marker not in check_lib_text:
                issues.append(f"missing shared helper marker: {marker}")

    issues.extend(validate_manifest_entries(repo_root))
    return issues


def _write(path: Path, text: str = "# stub\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_payload(files: list[Path] | tuple[Path, ...]) -> str:
    payload = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files),
        "files": [path.as_posix() for path in files],
    }
    return json.dumps(payload, indent=2) + "\n"


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path)
    _write(root / ABI_MANIFEST_PATH, _manifest_payload(REQUIRED_MANIFEST_ENTRIES))
    _write(root / MAKEFILE_PATH, "\n".join(MAKE_MARKERS) + "\n")
    _write(root / RUNNER_PATH, "\n".join(RUNNER_MARKERS) + "\n")
    _write(root / CHECK_LIB_PATH, "\n".join(CHECK_LIB_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_gate_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        for rel_path in OPTIONAL_EXPORT_UAPI_REPLAY_FILES:
            _write(root / rel_path)
            (root / rel_path).unlink()
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected ABI gate to keep export/UAPI-only replay files optional")
            print("\n".join(issues))
            return 1
        case_count += 1

        for manifest_entry_rel in REQUIRED_MANIFEST_ENTRIES:
            _write(
                root / ABI_MANIFEST_PATH,
                _manifest_payload(
                    [
                        rel_path
                        for rel_path in REQUIRED_MANIFEST_ENTRIES
                        if rel_path != manifest_entry_rel
                    ]
                ),
            )
            issues = validate_repo(root)
            expected_manifest_entry_missing = (
                f"missing phase3 ABI manifest entry: {manifest_entry_rel.as_posix()}"
            )
            if expected_manifest_entry_missing not in issues:
                print("PHASE3_ABI_SELF_TEST=fail")
                print("expected missing phase3 ABI manifest entry was not reported")
                return 1
            case_count += 1
            _write(root / ABI_MANIFEST_PATH, _manifest_payload(REQUIRED_MANIFEST_ENTRIES))

        missing_rel = REQUIRED_FILES[0]
        (root / missing_rel).unlink()
        issues = validate_repo(root)
        expected_missing = f"missing repo file: {missing_rel.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1
        case_count += 1

        _write(root / missing_rel)
        _write(root / MAKEFILE_PATH, "phase3-abi:\n")
        issues = validate_repo(root)
        expected_make_marker = "missing make marker: $(ZIG) build phase3-test --build-file zigux/tests/build.zig"
        if expected_make_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing make marker was not reported")
            return 1
        case_count += 1

        _write(root / MAKEFILE_PATH, "\n".join(MAKE_MARKERS) + "\n")
        _write(root / RUNNER_PATH, "from phase3_check_lib import run_phase3_slice_entry\n")
        issues = validate_repo(root)
        expected_runner_marker = "missing runner marker: return run_phase3_slice_entry(entry, root=root)"
        if expected_runner_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing runner marker was not reported")
            return 1
        case_count += 1

        _write(root / RUNNER_PATH, "\n".join(RUNNER_MARKERS) + "\n")
        _write(root / CHECK_LIB_PATH, "def run_phase3_slice_entry(entry, root=root):\n    return 0\n")
        issues = validate_repo(root)
        expected_helper_marker = 'missing shared helper marker: if slug == "abi":'
        if expected_helper_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing shared helper marker was not reported")
            return 1
        case_count += 1

    print("PHASE3_ABI_SELF_TEST=pass")
    print(f"PHASE3_ABI_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 ABI replay route against the live shared ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
