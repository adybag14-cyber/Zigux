#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=compile_shard_matrix_evidence"
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-survey.md")
SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
EVIDENCE_NOTE_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-evidence.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")
THIS_PATH = Path("scripts/zigux/check-phase14-compile-shard-matrix-evidence.py")
MISSING_BUILD_PATH = Path("zigux/tests/phase14_build.zig")

REQUIRED_FILES = [
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    MANIFEST_PATH,
    SURVEY_PATH,
    SMOKE_NOTE_PATH,
    EVIDENCE_NOTE_PATH,
    VALIDATOR_PATH,
    THIS_PATH,
]

REQUIRED_MANIFEST_VALUES = {
    ("smoke_commands",): ["make -C zigux phase14-validate"],
    ("smoke_shard_commands",): ["zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"],
    ("survey_summary", "phase14_make_target_present"): True,
    ("survey_summary", "phase14_make_smoke_target_present"): False,
    ("survey_summary", "workflow_runs_phase14_validate"): True,
    ("survey_summary", "workflow_runs_phase14_build"): False,
    ("survey_summary", "workflow_runs_phase14_smoke_shard"): False,
}

REQUIRED_SURVEY_MARKERS = [
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "- shared gate: `make -C zigux phase14-validate`",
    "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
]

REQUIRED_SMOKE_NOTE_MARKERS = [
    "* `zigux/tests/phase14_build.zig`",
    "executable packet members still unrecovered through this lane's exact contents path:",
    "the same manifest now records the focused raw build-file smoke shard",
]

REQUIRED_EVIDENCE_NOTE_MARKERS = [
    "Readback date: `2026-05-27`",
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    "Direct current-master contents readback for `zigux/tests/phase14_build.zig` still returns `404 Not Found`.",
    "- zero direct contents-path proof for the focused build-file body itself",
]

REQUIRED_MAKEFILE_MARKERS = [
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase14-smoke:",
    "phase14-test:",
    "\nphase14:",
]

REQUIRED_WORKFLOW_MARKERS = [
    "- name: Run current Phase 14 validate route",
    "run: make -C zigux phase14-validate",
]

FORBIDDEN_WORKFLOW_MARKERS = [
    "run: make -C zigux phase14-smoke",
    "run: make -C zigux phase14-test",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


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
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    if (root / MISSING_BUILD_PATH).exists():
        errors.append(f"expected_missing_file_present:{MISSING_BUILD_PATH.as_posix()}")

    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    survey = read_text(root, SURVEY_PATH)
    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    evidence_note = read_text(root, EVIDENCE_NOTE_PATH)

    require_markers(errors, MAKEFILE_PATH, makefile, REQUIRED_MAKEFILE_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile, FORBIDDEN_MAKEFILE_MARKERS)
    require_markers(errors, WORKFLOW_PATH, workflow, REQUIRED_WORKFLOW_MARKERS)
    require_absent(errors, WORKFLOW_PATH, workflow, FORBIDDEN_WORKFLOW_MARKERS)
    require_markers(errors, SURVEY_PATH, survey, REQUIRED_SURVEY_MARKERS)
    require_markers(errors, SMOKE_NOTE_PATH, smoke_note, REQUIRED_SMOKE_NOTE_MARKERS)
    require_markers(errors, EVIDENCE_NOTE_PATH, evidence_note, REQUIRED_EVIDENCE_NOTE_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    require_manifest_values(errors, manifest)
    return errors


def fixture_makefile() -> str:
    return """PYTHON ?= python3

.PHONY: phase14-validate

phase14-validate:
\tcd .. && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test
\tcd .. && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py
\tcd .. && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
\tcd .. && $(PYTHON) scripts/zigux/validate-phase14.py
\tcd .. && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
\tcd .. && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
"""


def fixture_workflow() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Run current Phase 14 validate route
        run: make -C zigux phase14-validate
"""


def fixture_manifest() -> str:
    payload = {
        "smoke_commands": ["make -C zigux phase14-validate"],
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "survey_summary": {
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "workflow_runs_phase14_validate": True,
            "workflow_runs_phase14_build": False,
            "workflow_runs_phase14_smoke_shard": False,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def fixture_survey() -> str:
    return """# Phase 14 Compile Shard Matrix Survey

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- shared gate: `make -C zigux phase14-validate`
- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`
"""


def fixture_smoke_note() -> str:
    return """# Phase 14 End-to-End Smoke Survey

- executable packet members still unrecovered through this lane's exact contents path:
  * `zigux/tests/phase14_build.zig`
- the same manifest now records the focused raw build-file smoke shard
"""


def fixture_validator() -> str:
    return """#!/usr/bin/env python3
print(\"PHASE14_VALIDATION=pass\")
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, WORKFLOW_PATH, fixture_workflow())
    write_text(root, MANIFEST_PATH, fixture_manifest())
    write_text(root, SURVEY_PATH, fixture_survey())
    write_text(root, SMOKE_NOTE_PATH, fixture_smoke_note())
    write_text(root, EVIDENCE_NOTE_PATH, fixture_note())
    write_text(root, VALIDATOR_PATH, fixture_validator())
    write_text(root, THIS_PATH, Path(__file__).read_text(encoding="utf-8"))


def fixture_note() -> str:
    return Path(__file__).resolve().parents[2].joinpath(
        "Documentation/zigux/phase14-compile-shard-matrix-evidence.md"
    ).read_text(encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-compile-shard-evidence-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            SURVEY_PATH,
            fixture_survey().replace(
                "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`\n",
                "",
                1,
            ),
        )
        if not any("PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected survey marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace("* `zigux/tests/phase14_build.zig`\n", "", 1),
        )
        if not any("zigux/tests/phase14_build.zig" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected smoke-note missing-build marker failure")
            return 1

        write_fixture_tree(base)
        (base / MISSING_BUILD_PATH).parent.mkdir(parents=True, exist_ok=True)
        (base / MISSING_BUILD_PATH).write_text("// unexpected recovery\n", encoding="utf-8")
        if not any("expected_missing_file_present" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected unexpected-build-file presence failure")
            return 1

        write_fixture_tree(base)
        payload = json.loads(fixture_manifest())
        payload["survey_summary"]["phase14_make_smoke_target_present"] = True
        write_text(base, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        if not any("phase14_make_smoke_target_present" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected manifest drift failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            EVIDENCE_NOTE_PATH,
            fixture_note().replace(
                "Direct current-master contents readback for `zigux/tests/phase14_build.zig` still returns `404 Not Found`.\n",
                "",
                1,
            ),
        )
        if not any("404 Not Found" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected evidence-note marker failure")
            return 1

        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=pass")
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check exact current Phase 14 compile-shard matrix evidence.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_fixture_tree(args.write_sample_root)
        print(f"PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE=fail")
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_ISSUES_END")
        return 1

    print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE=pass")
    print("PHASE14_COMPILE_SHARD_TOTAL=6")
    print("PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1")
    print("PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5")
    print("PHASE14_SHARED_SMOKE_GATE_COUNT=1")
    print("PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
