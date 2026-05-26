#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase15-roadmap-ledger-readiness-gap-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_roadmap_ledger_readiness_gap_manifest.json")
SELF_PATH = Path("scripts/zigux/check-phase15-roadmap-ledger-readiness-gap.py")
ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "P15-L01"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-26"

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=roadmap_ledger_readiness_gap_survey_landed",
    "PHASE15_LANE_KEY=P15-L01",
    "PHASE15_SLICE=roadmap_ledger_gap_accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current `master` already materializes all four roadmap-required governance features",
    "the bootstrap ledger is still intentionally authoritative only through item 25",
    "does not define a dedicated Phase 15 tranche-close family",
    "remaining readiness gaps are still route-level rather than governance-feature absence",
    "no dedicated `phase15-validate`, `phase15-test`, or `phase15` Makefile wrapper route is materialized",
    "no dedicated Phase 15 validate, test, or aggregate workflow route is materialized",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "no direct deep-core Zig bridge or port-readiness decision is implied",
)

BLOCKED_ROUTE_MARKERS = {
    "phase15-validate": "`make -C zigux phase15-validate` remains blocked route vocabulary rather than directly readable shipped evidence",
    "phase15-test": "`make -C zigux phase15-test` remains blocked route vocabulary rather than directly readable shipped evidence",
    "phase15": "`make -C zigux phase15` remains blocked route vocabulary rather than directly readable shipped evidence",
}

WORKFLOW_BLOCKED_MARKER = (
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route"
)
WORKFLOW_PHASE15_MARKERS = (
    "phase15-validate",
    "phase15-test",
    "phase15:",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_for(rel: str) -> str:
    if rel.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel.endswith(".json"):
        return "{}\n"
    if rel.endswith(".md"):
        return f"# Placeholder for {rel}\n"
    if rel.endswith(".zig"):
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    return "\n"


def _makefile_has_target(root: Path, target: str) -> bool:
    path = root / MAKEFILE_PATH
    if not path.exists():
        return False
    return f"\n{target}:" in ("\n" + _read_text(path))


def _workflow_has_phase15_route(root: Path) -> bool:
    path = root / WORKFLOW_PATH
    if not path.exists():
        return False
    workflow = _read_text(path)
    return any(marker in workflow for marker in WORKFLOW_PHASE15_MARKERS)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (NOTE_PATH, MANIFEST_PATH, SELF_PATH, ROADMAP_PATH, LEDGER_PATH, MAKEFILE_PATH, WORKFLOW_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    note = _read_text(root / NOTE_PATH)
    manifest = _read_json(root / MANIFEST_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest.get('lane_key', '')}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"manifest phase drifted from {EXPECTED_PHASE}: {manifest.get('phase', '')}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(
            f"manifest surveyed_commit drifted from {EXPECTED_SURVEYED_COMMIT}: {manifest.get('surveyed_commit', '')}"
        )
    if manifest["surveyed_commit"] not in note:
        failures.append("note is missing the manifest surveyed_commit marker")
    if manifest["checker_path"] != str(SELF_PATH):
        failures.append("manifest checker_path does not point at the focused roadmap-ledger checker")
    if f"`{manifest['checker_path']}`" not in note:
        failures.append("note is missing the focused roadmap-ledger checker marker")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"note is missing required marker: {marker}")

    for rel in manifest["direct_packet_paths"]:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"note is missing direct-packet marker: {marker}")
        if not (root / rel).exists():
            failures.append(f"direct_packet_path_missing:{rel}")

    phase15_validate_present = _makefile_has_target(root, "phase15-validate")
    phase15_test_present = _makefile_has_target(root, "phase15-test")
    phase15_present = _makefile_has_target(root, "phase15")
    workflow_phase15_present = _workflow_has_phase15_route(root)

    for target, marker in BLOCKED_ROUTE_MARKERS.items():
        target_present = {
            "phase15-validate": phase15_validate_present,
            "phase15-test": phase15_test_present,
            "phase15": phase15_present,
        }[target]
        if marker not in note:
            failures.append(f"note is missing blocked route marker: {marker}")
        elif target_present:
            failures.append(f"note still treats materialized Phase 15 make route as blocked: {target}")

    if WORKFLOW_BLOCKED_MARKER not in note:
        failures.append(f"note is missing blocked workflow marker: {WORKFLOW_BLOCKED_MARKER}")
    elif workflow_phase15_present:
        failures.append("note still treats a materialized Phase 15 workflow route as absent")

    repo_evidence = manifest["repo_evidence"]
    observed = {
        "roadmap_present": (root / ROADMAP_PATH).exists(),
        "ledger_present": (root / LEDGER_PATH).exists(),
        "freeze_map_present": (root / Path("Documentation/zigux/freeze-map.md")).exists(),
        "review_process_present": (root / Path("Documentation/zigux/phase15-architecture-council-review-process.md")).exists(),
        "decision_record_template_present": (
            root / Path("Documentation/zigux/phase15-architecture-council-decision-record-template.md")
        ).exists(),
        "parity_scorecard_present": (root / Path("Documentation/zigux/phase15-parity-scorecard.md")).exists(),
        "indefinite_c_policy_present": (root / Path("Documentation/zigux/phase15-indefinite-c-policy.md")).exists(),
        "readiness_survey_present": (root / Path("Documentation/zigux/phase15-readiness-gate-survey.md")).exists(),
        "readiness_checker_present": (root / Path("scripts/zigux/check-phase15-readiness-gate-packet.py")).exists(),
        "phase15_validator_present": (root / Path("scripts/zigux/validate-phase15.py")).exists(),
        "phase15_build_present": (root / Path("zigux/tests/phase15_build.zig")).exists(),
        "phase15_makefile_present": (root / MAKEFILE_PATH).exists(),
        "phase15_validate_target_present": phase15_validate_present,
        "phase15_test_target_present": phase15_test_present,
        "phase15_target_present": phase15_present,
        "phase15_workflow_route_present": workflow_phase15_present,
    }
    for key, value in observed.items():
        if repo_evidence[key] != value:
            failures.append(f"manifest {key} disagrees with repo reality")

    return failures


def _sample_note() -> str:
    return """# Phase 15 Roadmap/Ledger Readiness Gap Survey

## Status

- `PHASE15_STATUS=roadmap_ledger_readiness_gap_survey_landed`
- `PHASE15_LANE_KEY=P15-L01`
- `PHASE15_SLICE=roadmap_ledger_gap_accounting`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-26`

- current `master` already materializes all four roadmap-required governance features
- the bootstrap ledger is still intentionally authoritative only through item 25
- does not define a dedicated Phase 15 tranche-close family
- remaining readiness gaps are still route-level rather than governance-feature absence

- `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/validate-phase15.py`
- `scripts/zigux/check-phase15-roadmap-ledger-readiness-gap.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_roadmap_ledger_readiness_gap_manifest.json`

- no dedicated `phase15-validate`, `phase15-test`, or `phase15` Makefile wrapper route is materialized
- no dedicated Phase 15 validate, test, or aggregate workflow route is materialized

- `make -C zigux phase15-validate` remains blocked route vocabulary rather than directly readable shipped evidence
- `make -C zigux phase15-test` remains blocked route vocabulary rather than directly readable shipped evidence
- `make -C zigux phase15` remains blocked route vocabulary rather than directly readable shipped evidence

`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route.

- no Architecture Council approval is currently recorded for a freeze-map status change
- no direct deep-core Zig bridge or port-readiness decision is implied
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "checker_path": str(SELF_PATH),
        "direct_packet_paths": [
            "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
            "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
            "Documentation/zigux/freeze-map.md",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "Documentation/zigux/phase15-parity-scorecard.md",
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "Documentation/zigux/phase15-readiness-gate-survey.md",
            "scripts/zigux/check-phase15-readiness-gate-packet.py",
            "scripts/zigux/validate-phase15.py",
            "scripts/zigux/check-phase15-roadmap-ledger-readiness-gap.py",
            "zigux/tests/phase15_build.zig",
            "zigux/tests/phase15_roadmap_ledger_readiness_gap_manifest.json"
        ],
        "repo_evidence": {
            "roadmap_present": true,
            "ledger_present": true,
            "freeze_map_present": true,
            "review_process_present": true,
            "decision_record_template_present": true,
            "parity_scorecard_present": true,
            "indefinite_c_policy_present": true,
            "readiness_survey_present": true,
            "readiness_checker_present": true,
            "phase15_validator_present": true,
            "phase15_build_present": true,
            "phase15_makefile_present": true,
            "phase15_validate_target_present": false,
            "phase15_test_target_present": false,
            "phase15_target_present": false,
            "phase15_workflow_route_present": false
        }
    }
    return json.dumps(payload, indent=2) + "\n"


def _seed_repo(root: Path) -> None:
    _write(root / NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")
    _write(root / WORKFLOW_PATH, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/validate-phase15.py\n")
    for rel in (
        ROADMAP_PATH,
        LEDGER_PATH,
        Path("Documentation/zigux/freeze-map.md"),
        Path("Documentation/zigux/phase15-architecture-council-review-process.md"),
        Path("Documentation/zigux/phase15-architecture-council-decision-record-template.md"),
        Path("Documentation/zigux/phase15-parity-scorecard.md"),
        Path("Documentation/zigux/phase15-indefinite-c-policy.md"),
        Path("Documentation/zigux/phase15-readiness-gate-survey.md"),
        Path("scripts/zigux/check-phase15-readiness-gate-packet.py"),
        Path("scripts/zigux/validate-phase15.py"),
        SELF_PATH,
        Path("zigux/tests/phase15_build.zig"),
    ):
        _write(root / rel, _placeholder_for(str(rel)))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_roadmap_ledger_gap_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        lane_drift = root / "lane_drift"
        _seed_repo(lane_drift)
        manifest = json.loads(_sample_manifest())
        manifest["lane_key"] = "P15-L99"
        _write(lane_drift / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(lane_drift)
        expected = ["manifest lane key drifted from P15-L01: P15-L99"]
        if failures != expected:
            raise AssertionError(f"unexpected lane-drift failure: {failures}")

        route_recovered = root / "route_recovered"
        _seed_repo(route_recovered)
        _write(route_recovered / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(route_recovered)
        expected = [
            "note still treats materialized Phase 15 make route as blocked: phase15-validate",
            "manifest phase15_validate_target_present disagrees with repo reality",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected route-recovered failure: {failures}")

        missing_path = root / "missing_path"
        _seed_repo(missing_path)
        (missing_path / Path("Documentation/zigux/phase15-parity-scorecard.md")).unlink()
        failures = collect_failures(missing_path)
        expected = [
            "direct_packet_path_missing:Documentation/zigux/phase15-parity-scorecard.md",
            "manifest parity_scorecard_present disagrees with repo reality",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")

    print("PHASE15_ROADMAP_LEDGER_READINESS_GAP_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 roadmap/ledger readiness-gap survey still matches repo reality."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 roadmap/ledger readiness-gap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
