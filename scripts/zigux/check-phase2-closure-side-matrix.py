#!/usr/bin/env python3
"""Fail closed on the closure-side Phase 2 closure-matrix packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_MATRIX_CHECKER = "scripts/zigux/check-phase2-closure-matrix.py"
SHARED_VALIDATOR_REL = Path("scripts/zigux/validate-phase2.py")
VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
CHECKERS_SURFACE = "checkers"
CLOSURE_MATRIX_CHECKER_LINE = f'    "{CLOSURE_MATRIX_CHECKER}",'
SHARED_VALIDATOR_MARKERS = (
    f'CLOSURE_MATRIX_CHECKER = "{CLOSURE_MATRIX_CHECKER}"',
    "    CLOSURE_MATRIX_CHECKER,",
)

VALIDATOR_MARKERS = (
    f'payload["present_surfaces"]["{CHECKERS_SURFACE}"].remove("{CLOSURE_MATRIX_CHECKER}")',
    (
        f'assert ("MISSING_MANIFEST_SURFACE", '
        f'"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}") in collect_issues(root)'
    ),
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    shared_validator_path = resolve(root, SHARED_VALIDATOR_REL)
    validator_path = resolve(root, VALIDATOR_REL)
    manifest_path = resolve(root, MANIFEST_REL)
    checker_path = resolve(root, Path(CLOSURE_MATRIX_CHECKER))

    if not shared_validator_path.exists():
        issues.append(("MISSING_REQUIRED_FILE", SHARED_VALIDATOR_REL.as_posix()))
    if not validator_path.exists():
        issues.append(("MISSING_REQUIRED_FILE", VALIDATOR_REL.as_posix()))
    if not manifest_path.exists():
        issues.append(("MISSING_REQUIRED_FILE", MANIFEST_REL.as_posix()))
    if not checker_path.exists():
        issues.append(("MISSING_REQUIRED_FILE", CLOSURE_MATRIX_CHECKER))
    if issues:
        return issues

    shared_validator_text = read_text(shared_validator_path)
    validator_text = read_text(validator_path)
    manifest = read_json(manifest_path)

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    checkers = surfaces.get(CHECKERS_SURFACE)
    if not isinstance(checkers, list) or not all(isinstance(item, str) for item in checkers):
        issues.append(("INVALID_MANIFEST_SHAPE", CHECKERS_SURFACE))
        return issues

    for marker in SHARED_VALIDATOR_MARKERS:
        marker_count = shared_validator_text.count(marker)
        if marker_count == 0:
            issues.append(("MISSING_SHARED_VALIDATOR_MARKER", marker))
        elif marker_count != 1:
            issues.append(("DUPLICATE_SHARED_VALIDATOR_MARKER", f"{marker}:count={marker_count}"))

    validator_marker_count = validator_text.count(CLOSURE_MATRIX_CHECKER_LINE)
    if validator_marker_count < 2:
        issues.append(("MISSING_VALIDATOR_MARKER", CLOSURE_MATRIX_CHECKER_LINE))
    elif validator_marker_count != 2:
        issues.append(
            (
                "DUPLICATE_VALIDATOR_MARKER",
                f"{CLOSURE_MATRIX_CHECKER_LINE}:count={validator_marker_count}",
            )
        )

    for marker in VALIDATOR_MARKERS:
        marker_count = validator_text.count(marker)
        if marker_count == 0:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
        elif marker_count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count={marker_count}"))

    checker_count = sum(1 for item in checkers if item == CLOSURE_MATRIX_CHECKER)
    if checker_count == 0:
        issues.append(("MISSING_MANIFEST_SURFACE", f"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}"))
    elif checker_count != 1:
        issues.append(
            (
                "DUPLICATE_MANIFEST_SURFACE",
                f"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}:count={checker_count}",
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_SIDE_MATRIX=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    shared_validator = f"""#!/usr/bin/env python3
from __future__ import annotations

CLOSURE_MATRIX_CHECKER = \"{CLOSURE_MATRIX_CHECKER}\"
REQUIRED_PATHS = (
    \"scripts/zigux/check-zig-toolchain.py\",
    CLOSURE_MATRIX_CHECKER,
)
"""
    validator = f"""#!/usr/bin/env python3
from __future__ import annotations

EXPECTED_MANIFEST_CHECKERS = (
    \"scripts/zigux/check-zig-toolchain.py\",
    \"{CLOSURE_MATRIX_CHECKER}\",
)

def collect_issues(root):
    return []

def run_self_test():
    payload = {{
        \"present_surfaces\": {{
            \"{CHECKERS_SURFACE}\": [
                \"scripts/zigux/check-zig-toolchain.py\",
                \"{CLOSURE_MATRIX_CHECKER}\",
            ]
        }}
    }}
    payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")
    assert (\"MISSING_MANIFEST_SURFACE\", \"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}\") in collect_issues(root)
    return payload
"""
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": [],
        "present_surfaces": {
            CHECKERS_SURFACE: [
                "scripts/zigux/check-zig-toolchain.py",
                CLOSURE_MATRIX_CHECKER,
            ]
        },
    }

    write_text(resolve(root, SHARED_VALIDATOR_REL), shared_validator)
    write_text(resolve(root, VALIDATOR_REL), validator)
    write_text(resolve(root, Path(CLOSURE_MATRIX_CHECKER)), "present\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_side_matrix_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        shared_validator_path = resolve(root, SHARED_VALIDATOR_REL)
        shared_validator_path.write_text(
            read_text(shared_validator_path).replace(SHARED_VALIDATOR_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_SHARED_VALIDATOR_MARKER", SHARED_VALIDATOR_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        shared_validator_path = resolve(root, SHARED_VALIDATOR_REL)
        shared_validator_path.write_text(
            read_text(shared_validator_path).replace(
                SHARED_VALIDATOR_MARKERS[1],
                SHARED_VALIDATOR_MARKERS[1] + "\n" + SHARED_VALIDATOR_MARKERS[1],
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_SHARED_VALIDATOR_MARKER",
            f"{SHARED_VALIDATOR_MARKERS[1]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            read_text(validator_path).replace(CLOSURE_MATRIX_CHECKER_LINE + "\n", "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MARKER", CLOSURE_MATRIX_CHECKER_LINE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            read_text(validator_path).replace(
                CLOSURE_MATRIX_CHECKER_LINE,
                CLOSURE_MATRIX_CHECKER_LINE + "\n" + CLOSURE_MATRIX_CHECKER_LINE,
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_VALIDATOR_MARKER",
            f"{CLOSURE_MATRIX_CHECKER_LINE}:count=3",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            read_text(validator_path).replace(
                f'payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")',
                "# drifted",
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_VALIDATOR_MARKER",
            f'payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")',
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            read_text(validator_path).replace(
                f'payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")',
                (
                    f'payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")\n'
                    f'    payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")'
                ),
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_VALIDATOR_MARKER",
            (
                f'payload[\"present_surfaces\"][\"{CHECKERS_SURFACE}\"].remove(\"{CLOSURE_MATRIX_CHECKER}\")'
                ":count=2"
            ),
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            read_text(validator_path).replace(
                f'assert (\"MISSING_MANIFEST_SURFACE\", \"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}\") in collect_issues(root)',
                (
                    f'assert (\"MISSING_MANIFEST_SURFACE\", \"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}\") in collect_issues(root)\n'
                    f'    assert (\"MISSING_MANIFEST_SURFACE\", \"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}\") in collect_issues(root)'
                ),
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_VALIDATOR_MARKER",
            (
                f'assert (\"MISSING_MANIFEST_SURFACE\", \"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}\") '
                "in collect_issues(root):count=2"
            ),
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = read_json(manifest_path)
        assert isinstance(payload, dict)
        payload["present_surfaces"][CHECKERS_SURFACE].remove(CLOSURE_MATRIX_CHECKER)
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert (
            "MISSING_MANIFEST_SURFACE",
            f"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = read_json(manifest_path)
        assert isinstance(payload, dict)
        payload["present_surfaces"][CHECKERS_SURFACE].append(CLOSURE_MATRIX_CHECKER)
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert (
            "DUPLICATE_MANIFEST_SURFACE",
            f"{CHECKERS_SURFACE}:{CLOSURE_MATRIX_CHECKER}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = read_json(manifest_path)
        assert isinstance(payload, dict)
        payload["present_surfaces"] = []
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_MANIFEST_SHAPE", "present_surfaces") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = read_json(manifest_path)
        assert isinstance(payload, dict)
        payload["present_surfaces"][CHECKERS_SURFACE] = {"unexpected": "shape"}
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_MANIFEST_SHAPE", CHECKERS_SURFACE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve(root, SHARED_VALIDATOR_REL).unlink()
        assert ("MISSING_REQUIRED_FILE", SHARED_VALIDATOR_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve(root, VALIDATOR_REL).unlink()
        assert ("MISSING_REQUIRED_FILE", VALIDATOR_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve(root, MANIFEST_REL).unlink()
        assert ("MISSING_REQUIRED_FILE", MANIFEST_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve(root, Path(CLOSURE_MATRIX_CHECKER)).unlink()
        assert ("MISSING_REQUIRED_FILE", CLOSURE_MATRIX_CHECKER) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_SIDE_MATRIX_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_SIDE_MATRIX_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the closure-side validator, shared validator, and Phase 2 tool manifest for closure-matrix coverage."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_SIDE_MATRIX=pass")
    print(f"PHASE2_CLOSURE_SIDE_MATRIX_CHECKER={CLOSURE_MATRIX_CHECKER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
