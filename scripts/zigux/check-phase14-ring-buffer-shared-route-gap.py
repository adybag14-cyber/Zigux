#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=ring_buffer_shared_route_gap

Validate the current Phase 14 shared-smoke ring-buffer route handoff.

This checker is intentionally narrow. It records the current productization gap:
the Phase 14 validator and shared manifest already know about the ring-buffer
compile-route checker, while the shared-smoke route checker still needs a small
follow-up to fail-close on the same evidence.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=ring_buffer_shared_route_gap"
NOTE_PATH = Path("Documentation/zigux/phase14-ring-buffer-shared-route-gap.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")
SHARED_ROUTE_CHECKER_PATH = Path("scripts/zigux/check-phase14-shared-smoke-route.py")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

NOTE_MARKERS = [
    "PHASE14_GAP=ring-buffer-shared-route-checker-undercount",
    "PHASE14_REPAIR_TARGET=scripts/zigux/check-phase14-shared-smoke-route.py",
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH",
    "survey_summary.phase14_validate_runs_ring_buffer_compile_route_checker == true",
    "survey_summary.shared_manifest_records_ring_buffer_compile_route_checker == true",
]

VALIDATOR_MARKERS = [
    'RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (\n    "scripts/zigux/check-phase14-ring-buffer-compile-route.py"\n)',
    "run_guardrail_checker(\n                args.root,\n                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,",
]

SHARED_ROUTE_CURRENT_GAP_MARKERS = [
    'SKBUFF_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-skbuff-compile-route.py"',
    'RCU_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"',
    "phase14_validate_runs_skbuff_compile_route_checker",
    "phase14_validate_runs_rcu_compile_route_checker",
]

SHARED_ROUTE_EXPECTED_MISSING_MARKERS = [
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH",
    "phase14_validate_runs_ring_buffer_compile_route_checker",
    "shared_manifest_records_ring_buffer_compile_route_checker",
]

REQUIRED_MANIFEST_VALUES = {
    ("p14_l05_anti_regression_readback", "observed_checker_gap"): "scripts/zigux/validate-phase14.py already runs the ring-buffer compile-route checker and this manifest already records the ring-buffer summary booleans, but scripts/zigux/check-phase14-shared-smoke-route.py currently fail-closes only the validator-side skbuff and RCU compile-route calls.",
    ("p14_l05_anti_regression_readback", "next_checker_only_repair"): "Teach scripts/zigux/check-phase14-shared-smoke-route.py to require RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH, its run_guardrail_checker call, and the existing phase14_validate_runs_ring_buffer_compile_route_checker plus shared_manifest_records_ring_buffer_compile_route_checker manifest booleans.",
    ("survey_summary", "phase14_validate_runs_ring_buffer_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_ring_buffer_compile_route_checker"): True,
}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"gap_already_closed:{rel.as_posix()}:{marker}")


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_manifest_values(errors: list[str], manifest: object) -> None:
    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            errors.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(
                "manifest_value_mismatch:"
                f"{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in [NOTE_PATH, VALIDATOR_PATH, SHARED_ROUTE_CHECKER_PATH, MANIFEST_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    note = read_text(root, NOTE_PATH)
    validator = read_text(root, VALIDATOR_PATH)
    shared_route_checker = read_text(root, SHARED_ROUTE_CHECKER_PATH)
    require_markers(errors, NOTE_PATH, note, NOTE_MARKERS)
    require_markers(errors, VALIDATOR_PATH, validator, VALIDATOR_MARKERS)
    require_markers(
        errors,
        SHARED_ROUTE_CHECKER_PATH,
        shared_route_checker,
        SHARED_ROUTE_CURRENT_GAP_MARKERS,
    )
    require_absent(
        errors,
        SHARED_ROUTE_CHECKER_PATH,
        shared_route_checker,
        SHARED_ROUTE_EXPECTED_MISSING_MARKERS,
    )

    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors
    require_manifest_values(errors, manifest)
    return errors


def fixture_note() -> str:
    return "\n".join(
        [
            "# Phase 14 Ring-Buffer Shared Route Gap",
            "- `PHASE14_GAP=ring-buffer-shared-route-checker-undercount`",
            "- `PHASE14_REPAIR_TARGET=scripts/zigux/check-phase14-shared-smoke-route.py`",
            "- `RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH`",
            "- `survey_summary.phase14_validate_runs_ring_buffer_compile_route_checker == true`",
            "- `survey_summary.shared_manifest_records_ring_buffer_compile_route_checker == true`",
            "",
        ]
    )


def fixture_validator() -> str:
    return """RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (
    "scripts/zigux/check-phase14-ring-buffer-compile-route.py"
)

def main(args):
    run_guardrail_checker(
                args.root,
                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
                self_test=False,
            )
"""


def fixture_shared_route_checker() -> str:
    return """SKBUFF_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-skbuff-compile-route.py"
RCU_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"
phase14_validate_runs_skbuff_compile_route_checker
phase14_validate_runs_rcu_compile_route_checker
"""


def fixture_manifest() -> str:
    payload = {
        "p14_l05_anti_regression_readback": {
            "observed_checker_gap": REQUIRED_MANIFEST_VALUES[
                ("p14_l05_anti_regression_readback", "observed_checker_gap")
            ],
            "next_checker_only_repair": REQUIRED_MANIFEST_VALUES[
                ("p14_l05_anti_regression_readback", "next_checker_only_repair")
            ],
        },
        "survey_summary": {
            "phase14_validate_runs_ring_buffer_compile_route_checker": True,
            "shared_manifest_records_ring_buffer_compile_route_checker": True,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, NOTE_PATH, fixture_note())
    write_text(root, VALIDATOR_PATH, fixture_validator())
    write_text(root, SHARED_ROUTE_CHECKER_PATH, fixture_shared_route_checker())
    write_text(root, MANIFEST_PATH, fixture_manifest())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-ring-buffer-shared-route-gap-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        write_text(base, NOTE_PATH, fixture_note().replace(NOTE_MARKERS[0], "", 1))
        if not any(NOTE_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=fail")
            print("expected note marker drift to fail")
            return 1

        write_fixture_tree(base)
        write_text(base, VALIDATOR_PATH, fixture_validator().replace(VALIDATOR_MARKERS[1], "", 1))
        if not any("RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH" in error for error in check(base)):
            print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=fail")
            print("expected validator marker drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_ring_buffer_compile_route_checker"] = False
        write_text(base, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        if not any(
            "manifest_value_mismatch:survey_summary.phase14_validate_runs_ring_buffer_compile_route_checker"
            in error
            for error in check(base)
        ):
            print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=fail")
            print("expected manifest ring-buffer run drift to fail")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            SHARED_ROUTE_CHECKER_PATH,
            fixture_shared_route_checker() + "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH\n",
        )
        if not any("gap_already_closed" in error for error in check(base)):
            print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=fail")
            print("expected closure marker to fail this temporary gap sentinel")
            return 1

        print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST=pass")
        print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP=fail")
        print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_ISSUES_END")
        return 1

    print("PHASE14_RING_BUFFER_SHARED_ROUTE_GAP=pass")
    print(f"PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE14_RING_BUFFER_SHARED_ROUTE_GAP_MANIFEST_ASSERTION_COUNT={len(REQUIRED_MANIFEST_VALUES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
