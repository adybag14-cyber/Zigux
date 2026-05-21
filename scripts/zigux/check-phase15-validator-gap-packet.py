#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
READINESS_NOTE_PATH = "Documentation/zigux/phase15-readiness-gate-survey.md"
SHARED_GAP_PATH = "Documentation/zigux/phase15-shared-summary-gap.md"
HANDOFF_NOTE_PATH = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
READINESS_MANIFEST_PATH = "zigux/tests/phase15_readiness_gate_manifest.json"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
VALIDATOR_PATH = "scripts/zigux/validate-phase15.py"
BUILD_PATH = "zigux/tests/phase15_build.zig"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    READINESS_NOTE_PATH,
    SHARED_GAP_PATH,
    HANDOFF_NOTE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    READINESS_MANIFEST_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` still belong to the broader validator-first and dedicated-build reminder family",
        "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
        "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route",
    ],
    REVIEW_CHECKLIST_PATH: [
        "keep `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes framed as repo-reality gaps",
    ],
    READINESS_NOTE_PATH: [
        "the missing validator, build, and workflow companions still block any claim that the broader Phase 15 replay route is fully ready",
        "`scripts/zigux/validate-phase15.py`",
        "`zigux/tests/phase15_build.zig`",
        "`make -C zigux phase15-validate` remains blocked route vocabulary",
    ],
    SHARED_GAP_PATH: [
        "## Still-missing broader validator-first companions on current master",
        "`scripts/zigux/validate-phase15.py`",
        "`zigux/tests/phase15_build.zig`",
        "broader validator-first wording around `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes",
    ],
    HANDOFF_NOTE_PATH: [
        "no broader validator-first companion `scripts/zigux/validate-phase15.py` is directly materialized on current `master`",
        "no dedicated shared Phase 15 build replay `zigux/tests/phase15_build.zig` is directly materialized on current `master`",
        "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` still belong to the broader validator-first and dedicated-build reminder family",
        "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
        "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route",
    ],
    TESTS_README_PATH: [
        "Current `master` still does not materialize `scripts/zigux/validate-phase15.py` or `zigux/tests/phase15_build.zig`, so keep those broader validator-first and build-route companions framed as repo-reality gaps",
        "Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
    ],
}

EXPECTED_MISSING_PATHS = [
    VALIDATOR_PATH,
    BUILD_PATH,
]

EXPECTED_MANIFEST_FLAGS = {
    "phase15_validator_script_present": False,
    "phase15_build_zig_present": False,
    "phase15_validate_target_present": False,
    "phase15_test_target_present": False,
    "phase15_aggregate_target_present": False,
    "shared_ci_phase15_present": False,
    "phase15_replay_green_on_current_master": False,
}

WORKFLOW_FORBIDDEN_MARKERS = (
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _makefile_has_target(root: Path, target: str) -> bool:
    path = root / MAKEFILE_PATH
    if not path.exists():
        return False
    return f"\n{target}:" in ("\n" + _read_text(path))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    drift: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(f"missing_file:{rel}")
    if missing:
        return missing, drift

    for rel, markers in REQUIRED_MARKERS.items():
        text = _read_text(root / rel)
        for marker in markers:
            if marker not in text:
                drift.append(f"missing_marker:{rel}:{marker}")

    if (root / VALIDATOR_PATH).exists():
        drift.append(f"unexpected_materialized_path:{VALIDATOR_PATH}")
    if (root / BUILD_PATH).exists():
        drift.append(f"unexpected_materialized_path:{BUILD_PATH}")

    manifest = json.loads(_read_text(root / READINESS_MANIFEST_PATH))
    if manifest.get("still_missing_broader_paths") != EXPECTED_MISSING_PATHS:
        drift.append("manifest_missing_path_list_drift")

    repo_evidence = manifest.get("repo_evidence", {})
    for key, expected in EXPECTED_MANIFEST_FLAGS.items():
        if repo_evidence.get(key) != expected:
            drift.append(f"manifest_flag_drift:{key}:expected={expected}:actual={repo_evidence.get(key)!r}")

    if _makefile_has_target(root, "phase15-validate"):
        drift.append("unexpected_make_target:phase15-validate")
    if _makefile_has_target(root, "phase15-test"):
        drift.append("unexpected_make_target:phase15-test")
    if _makefile_has_target(root, "phase15"):
        drift.append("unexpected_make_target:phase15")

    workflow_text = _read_text(root / WORKFLOW_PATH)
    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        if marker in workflow_text:
            drift.append(f"unexpected_workflow_marker:{marker}")

    return missing, drift


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_manifest() -> str:
    payload = {
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": "current-master-readback-2026-05-20",
        "readiness_packet_checker": "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "direct_packet_paths": [],
        "still_missing_broader_paths": EXPECTED_MISSING_PATHS,
        "repo_evidence": EXPECTED_MANIFEST_FLAGS,
        "phase15_validate_checkers": [
            "scripts/zigux/check-phase15-docs-readme-alignment.py",
            "scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "scripts/zigux/check-phase15-tests-readme-alignment.py",
            "scripts/zigux/check-phase15-review-process-handoff.py",
            "scripts/zigux/check-phase15-shared-summary-gap.py",
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        title = rel.split("/")[-1]
        markers = REQUIRED_MARKERS.get(rel, [])
        if rel == READINESS_MANIFEST_PATH:
            _write(root / rel, _fixture_manifest())
        elif rel == MAKEFILE_PATH:
            _write(root / rel, "phase2-toolchain:\n\t@true\nphase12-smoke:\n\t@true\n")
        elif rel == WORKFLOW_PATH:
            _write(root / rel, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase12-release-readiness-packet.py\n")
        else:
            body = "\n".join(f"- {marker}" for marker in markers) or "fixture"
            _write(root / rel, f"# {title}\n\n{body}\n")


def expect_failure(root: Path, expected: str) -> None:
    missing, drift = validate(root)
    failures = missing + drift
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase15-validator-gap-"))
    try:
        write_fixture_root(base)
        missing, drift = validate(base)
        if missing or drift:
            raise SystemExit(f"fixture tree should pass but failed: {(missing + drift)!r}")

        for rel in REQUIRED_FILES:
            write_fixture_root(base)
            (base / rel).unlink()
            expect_failure(base, f"missing_file:{rel}")

        write_fixture_root(base)
        _write(base / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
        expect_failure(base, f"unexpected_materialized_path:{VALIDATOR_PATH}")

        write_fixture_root(base)
        _write(base / BUILD_PATH, "const std = @import(\"std\");\n")
        expect_failure(base, f"unexpected_materialized_path:{BUILD_PATH}")

        write_fixture_root(base)
        _write(base / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        expect_failure(base, "unexpected_make_target:phase15-validate")

        write_fixture_root(base)
        _write(base / WORKFLOW_PATH, "jobs:\n  bootstrap:\n    steps:\n      - run: make -C zigux phase15-validate\n")
        expect_failure(base, "unexpected_workflow_marker:make -C zigux phase15-validate")

        write_fixture_root(base)
        path = base / READINESS_NOTE_PATH
        text = _read_text(path).replace("`scripts/zigux/validate-phase15.py`", "", 1)
        _write(path, text)
        expect_failure(base, f"missing_marker:{READINESS_NOTE_PATH}:`scripts/zigux/validate-phase15.py`")

        print("PHASE15_VALIDATOR_GAP_PACKET_SELF_TEST=pass")
        print("PHASE15_VALIDATOR_GAP_PACKET_SELF_TEST_CASE_COUNT=15")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 15 missing-validator readiness blocker packet across shared reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample tree")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_fixture_root(args.write_sample_root)
        print(f"PHASE15_VALIDATOR_GAP_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    missing, drift = validate(args.root)
    if missing:
        print("PHASE15_VALIDATOR_GAP_PACKET=fail")
        print("PHASE15_VALIDATOR_GAP_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE15_VALIDATOR_GAP_PACKET_MISSING_END")
        return 1
    if drift:
        print("PHASE15_VALIDATOR_GAP_PACKET=fail")
        print("PHASE15_VALIDATOR_GAP_PACKET_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE15_VALIDATOR_GAP_PACKET_DRIFT_END")
        return 1

    print("PHASE15_VALIDATOR_GAP_PACKET=pass")
    print(f"PHASE15_VALIDATOR_GAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE15_VALIDATOR_GAP_PACKET_MARKER_COUNT=" f"{sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print("PHASE15_VALIDATOR_GAP_PACKET_MANIFEST_FLAG_COUNT=" f"{len(EXPECTED_MANIFEST_FLAGS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
