#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
DOCS_CHECKER_PATH = Path("scripts/zigux/check-phase15-docs-readme-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_VALIDATE_CHECKERS = [
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
]


def _read_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def _workflow_has_phase15_steps(root: Path) -> bool:
    workflow = root / WORKFLOW_PATH
    if not workflow.exists():
        return False
    text = workflow.read_text(encoding="utf-8")
    return "make -C zigux phase15-validate" in text and "make -C zigux phase15-test" in text


def _makefile_has_target(root: Path, target: str) -> bool:
    makefile = root / MAKEFILE_PATH
    if not makefile.exists():
        return False
    text = makefile.read_text(encoding="utf-8")
    return f"{target}:" in text


def collect_failures(root: Path) -> list[str]:
    manifest = _read_manifest(root)
    failures: list[str] = []

    if manifest.get("surveyed_commit_mode") != "dated_master_readback":
        failures.append("manifest:surveyed_commit_mode must stay dated_master_readback")

    if manifest.get("surveyed_commit") != "current-master-readback-2026-05-17":
        failures.append("manifest:surveyed_commit must stay current-master-readback-2026-05-17")

    repo_evidence = manifest.get("repo_evidence")
    if not isinstance(repo_evidence, dict):
        failures.append("manifest:repo_evidence must be an object")
        return failures

    expected = {
        "phase15_validator_script_present": (root / VALIDATOR_PATH).exists(),
        "phase15_docs_readme_checker_present": (root / DOCS_CHECKER_PATH).exists(),
        "phase15_validate_target_present": _makefile_has_target(root, "phase15-validate"),
        "phase15_test_target_present": _makefile_has_target(root, "phase15-test"),
        "shared_ci_phase15_present": _workflow_has_phase15_steps(root),
    }
    expected["phase15_replay_green_on_current_master"] = (
        expected["phase15_validator_script_present"]
        and expected["phase15_validate_target_present"]
        and expected["phase15_test_target_present"]
        and expected["shared_ci_phase15_present"]
    )

    for key, value in expected.items():
        if repo_evidence.get(key) is not value:
            failures.append(
                f"manifest:repo_evidence[{key}] expected {str(value).lower()} but found {repo_evidence.get(key)!r}"
            )

    if manifest.get("phase15_validate_checkers") != EXPECTED_VALIDATE_CHECKERS:
        failures.append("manifest:phase15_validate_checkers no longer matches the bounded Phase 15 checker packet")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _baseline_manifest() -> str:
    return json.dumps(
        {
            "surveyed_commit_mode": "dated_master_readback",
            "surveyed_commit": "current-master-readback-2026-05-17",
            "repo_evidence": {
                "phase15_validator_script_present": False,
                "phase15_docs_readme_checker_present": True,
                "phase15_validate_target_present": False,
                "phase15_test_target_present": False,
                "shared_ci_phase15_present": False,
                "phase15_replay_green_on_current_master": False,
            },
            "phase15_validate_checkers": EXPECTED_VALIDATE_CHECKERS,
        },
        indent=2,
    ) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / MANIFEST_PATH, _baseline_manifest())
        _write(root / DOCS_CHECKER_PATH, "# present\n")
        _write(
            root / WORKFLOW_PATH,
            "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: echo no phase15 yet\n",
        )

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        wrong_validator = root / "wrong_validator"
        _write(wrong_validator / MANIFEST_PATH, _baseline_manifest().replace("false", "true", 1))
        _write(wrong_validator / DOCS_CHECKER_PATH, "# present\n")
        _write(
            wrong_validator / WORKFLOW_PATH,
            "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: echo no phase15 yet\n",
        )
        failures = collect_failures(wrong_validator)
        expected = [
            "manifest:repo_evidence[phase15_validator_script_present] expected false but found True"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected validator mismatch failure: {failures}")

        wrong_ci = root / "wrong_ci"
        _write(wrong_ci / MANIFEST_PATH, _baseline_manifest().replace('"shared_ci_phase15_present": false', '"shared_ci_phase15_present": true', 1))
        _write(wrong_ci / DOCS_CHECKER_PATH, "# present\n")
        _write(
            wrong_ci / WORKFLOW_PATH,
            "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: echo no phase15 yet\n",
        )
        failures = collect_failures(wrong_ci)
        expected = ["manifest:repo_evidence[shared_ci_phase15_present] expected false but found True"]
        if failures != expected:
            raise AssertionError(f"unexpected CI mismatch failure: {failures}")

        wrong_checkers = root / "wrong_checkers"
        wrong_manifest = json.loads(_baseline_manifest())
        wrong_manifest["phase15_validate_checkers"] = EXPECTED_VALIDATE_CHECKERS[:-1]
        _write(wrong_checkers / MANIFEST_PATH, json.dumps(wrong_manifest, indent=2) + "\n")
        _write(wrong_checkers / DOCS_CHECKER_PATH, "# present\n")
        _write(
            wrong_checkers / WORKFLOW_PATH,
            "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: echo no phase15 yet\n",
        )
        failures = collect_failures(wrong_checkers)
        expected = [
            "manifest:phase15_validate_checkers no longer matches the bounded Phase 15 checker packet"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected checker-list failure: {failures}")

    print("PHASE15_READINESS_GATE_MANIFEST_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness manifest matches current repo reality."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing scripts/zigux, zigux/tests, and workflow files",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 readiness manifest check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
