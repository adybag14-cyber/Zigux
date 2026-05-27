#!/usr/bin/env python3
"""Fail-close the current shared Phase 3 adjacent-packet sync surface."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")
SELFTEST_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_PACKET_FILES = (
    "scripts/zigux/check-phase3-low-level-wrappers.py",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
    "zigux/tests/phase3_list_hlist_dump.zig",
    "zigux/tests/phase3_list_hlist_dump_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
    "scripts/zigux/check-phase3-list-hlist.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-low-level-wrappers.py --self-test",
    "python3 scripts/zigux/check-phase3-low-level-wrappers.py",
    "python3 scripts/zigux/check-phase3-list-hlist.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
)

REQUIRED_SOURCE_MARKERS = {
    RUNNER_PATH: (
        'Path("scripts/zigux/check-phase3-low-level-wrappers.py")',
        'Path("scripts/zigux/check-phase3-list-hlist.py")',
        '"validated zigux/tests/phase3_low_level_wrappers.zig"',
        '"validated zigux/tests/phase3_list_hlist_dump.zig"',
    ),
    SELFTEST_PATH: (
        'Path("scripts/zigux/check-phase3-low-level-wrappers.py")',
        'Path("scripts/zigux/check-phase3-list-hlist.py")',
        '"PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass"',
        '"PHASE3_LIST_HLIST_SELF_TEST=pass"',
    ),
}

SELF_TEST_CASES = (
    ("packet_file", REQUIRED_PACKET_FILES[0]),
    ("packet_file", REQUIRED_PACKET_FILES[-1]),
    ("replay_route", REQUIRED_REPLAY_ROUTES[0]),
    ("replay_route", REQUIRED_REPLAY_ROUTES[-1]),
    ("marker", (RUNNER_PATH.as_posix(), REQUIRED_SOURCE_MARKERS[RUNNER_PATH][0])),
    ("marker", (SELFTEST_PATH.as_posix(), REQUIRED_SOURCE_MARKERS[SELFTEST_PATH][-1])),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _load_manifest(path: Path) -> object:
    return json.loads(_read(path))


def _literal_tuple_from_assignment(text: str, name: str) -> tuple[str, ...] | None:
    module = ast.parse(text)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                value = ast.literal_eval(node.value)
                if isinstance(value, tuple) and all(isinstance(entry, str) for entry in value):
                    return value
                return None
    return None


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    validator_path = repo_root / VALIDATOR_PATH
    runner_path = repo_root / RUNNER_PATH
    selftest_path = repo_root / SELFTEST_PATH
    manifest_path = repo_root / MANIFEST_PATH

    for path in (validator_path, runner_path, selftest_path, manifest_path):
        if not path.is_file():
            issues.append(f"missing repo file: {path.relative_to(repo_root).as_posix()}")
    if issues:
        return issues

    validator_text = _read(validator_path)
    runner_text = _read(runner_path)
    selftest_text = _read(selftest_path)
    manifest = _load_manifest(manifest_path)

    packet_files = _literal_tuple_from_assignment(
        validator_text, "REQUIRED_MANIFEST_PACKET_FILES"
    )
    if packet_files is None:
        issues.append(
            "validate-phase3.py missing parseable REQUIRED_MANIFEST_PACKET_FILES tuple"
        )
    else:
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(
                    "validate-phase3.py missing adjacent packet_files coverage: "
                    + entry
                )

    replay_routes = _literal_tuple_from_assignment(
        validator_text, "REQUIRED_MANIFEST_REPLAY_ROUTES"
    )
    if replay_routes is None:
        issues.append(
            "validate-phase3.py missing parseable REQUIRED_MANIFEST_REPLAY_ROUTES tuple"
        )
    else:
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(
                    "validate-phase3.py missing adjacent replay-route coverage: "
                    + entry
                )

    if not isinstance(manifest, dict):
        issues.append("phase3_abi_manifest.json did not decode to an object")
        return issues

    manifest_packet_files = manifest.get("packet_files")
    if not isinstance(manifest_packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for entry in REQUIRED_PACKET_FILES:
            if entry not in manifest_packet_files:
                issues.append(
                    "phase3_abi_manifest.json missing adjacent packet_files entry: "
                    + entry
                )

    manifest_replay_routes = manifest.get("replay_routes")
    if not isinstance(manifest_replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in manifest_replay_routes:
                issues.append(
                    "phase3_abi_manifest.json missing adjacent replay route: " + entry
                )

    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        text = runner_text if rel_path == RUNNER_PATH else selftest_text
        for marker in markers:
            if marker not in text:
                issues.append(
                    f"missing {rel_path.as_posix()} adjacent marker: {marker}"
                )

    return issues


def _synthetic_validator_text() -> str:
    packet_files = "\n".join(f'    "{entry}",' for entry in REQUIRED_PACKET_FILES)
    replay_routes = "\n".join(f'    "{entry}",' for entry in REQUIRED_REPLAY_ROUTES)
    return (
        "REQUIRED_MANIFEST_PACKET_FILES = (\n"
        f"{packet_files}\n"
        ")\n\n"
        "REQUIRED_MANIFEST_REPLAY_ROUTES = (\n"
        f"{replay_routes}\n"
        ")\n"
    )


def _synthetic_marker_text(markers: tuple[str, ...]) -> str:
    return "\n".join(markers) + "\n"


def _populate_repo(root: Path) -> None:
    _write(root / VALIDATOR_PATH, _synthetic_validator_text())
    _write(root / RUNNER_PATH, _synthetic_marker_text(REQUIRED_SOURCE_MARKERS[RUNNER_PATH]))
    _write(
        root / SELFTEST_PATH,
        _synthetic_marker_text(REQUIRED_SOURCE_MARKERS[SELFTEST_PATH]),
    )
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet_files": list(REQUIRED_PACKET_FILES),
                "replay_routes": list(REQUIRED_REPLAY_ROUTES),
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_adjacent_sync_") as tmp_dir:
        repo_root = Path(tmp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_ADJACENT_PACKET_SYNC_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for case_kind, payload in SELF_TEST_CASES:
            _populate_repo(repo_root)
            if case_kind == "packet_file":
                manifest_path = repo_root / MANIFEST_PATH
                manifest = _load_manifest(manifest_path)
                manifest["packet_files"].remove(payload)
                _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
                expected = (
                    "phase3_abi_manifest.json missing adjacent packet_files entry: "
                    + payload
                )
            elif case_kind == "replay_route":
                validator_path = repo_root / VALIDATOR_PATH
                validator_text = _read(validator_path)
                _write(validator_path, validator_text.replace(f'    "{payload}",\n', "", 1))
                expected = (
                    "validate-phase3.py missing adjacent replay-route coverage: "
                    + payload
                )
            else:
                rel_path, marker = payload
                target_path = repo_root / rel_path
                target_text = _read(target_path)
                _write(target_path, target_text.replace(marker + "\n", "", 1))
                expected = f"missing {rel_path} adjacent marker: {marker}"

            issues = validate_repo(repo_root)
            if expected not in issues:
                print("PHASE3_ADJACENT_PACKET_SYNC_SELF_TEST=fail")
                print(f"expected issue was not reported: {expected}")
                return 1

    print("PHASE3_ADJACENT_PACKET_SYNC_SELF_TEST=pass")
    print(f"PHASE3_ADJACENT_PACKET_SYNC_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the shared Phase 3 validator stays aligned with adjacent packet growth."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/ and zigux/tests/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ADJACENT_PACKET_SYNC=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / VALIDATOR_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    print(f"validated {args.repo_root / RUNNER_PATH}")
    print(f"validated {args.repo_root / SELFTEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
