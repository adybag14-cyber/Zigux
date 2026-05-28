#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
GAP_MATRIX_PATH = Path("zigux/tests/phase15_readiness_gap_matrix.json")
SELF_PATH = Path("scripts/zigux/check-phase15-readiness-gap-matrix.py")
READY_CHECKER_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_PHASE = "Phase 15"
EXPECTED_LANE_KEY = "P15-L01"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"
EXPECTED_LEDGER_ANCHOR = "docs(zigux): add documentation root, review checklist, and freeze map"

EXPECTED_REQUIREMENTS = (
    {
        "requirement": "freeze map",
        "status": "landed_but_status_change_still_blocked",
        "evidence": (
            "Documentation/zigux/freeze-map.md",
            "Documentation/zigux/phase15-freeze-map-governance.md",
        ),
        "remaining_gap": "no Architecture Council approval is currently recorded for a freeze-map status change",
    },
    {
        "requirement": "Architecture Council review process",
        "status": "landed_but_no_reopen_decision_recorded",
        "evidence": (
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "Documentation/zigux/phase15-architecture-council-decision-index.md",
        ),
        "remaining_gap": "no reopen decision is currently recorded for a deep-core Phase 15 status change",
    },
    {
        "requirement": "parity scorecard",
        "status": "landed_but_not_shared_route_ready",
        "evidence": (
            "Documentation/zigux/phase15-parity-scorecard.md",
            "Documentation/zigux/phase15-parity-scorecard-survey.md",
            "zigux/tests/phase15_parity_scorecard.json",
            "zigux/tests/phase15_parity_scorecard.zig",
        ),
        "remaining_gap": "the broader Phase 15 replay route is still blocked on missing `phase15*` Makefile wrappers and a dedicated workflow route",
    },
    {
        "requirement": "policy for code that remains in C indefinitely",
        "status": "landed_but_not_one_command_or_ci_ready",
        "evidence": (
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "zigux/tests/phase15_indefinite_c_policy.json",
            "zigux/tests/phase15_indefinite_c_policy.zig",
        ),
        "remaining_gap": "the indefinite-C policy is landed and replay-backed, but the broader reminder surface is still not one-command or shared-CI ready",
    },
)

EXPECTED_GAPS = (
    {
        "gap": "missing_make_routes",
        "status": "blocked",
        "path": "zigux/Makefile",
        "blocked_routes": ("phase15-validate", "phase15-test", "phase15"),
        "why_it_matters": "without dedicated wrapper routes, the broader Phase 15 replay packet is not one-command ready",
    },
    {
        "gap": "missing_workflow_route",
        "status": "blocked",
        "path": ".github/workflows/zigux-bootstrap.yml",
        "why_it_matters": "without a dedicated workflow route, the broader Phase 15 replay packet is not shared-CI ready",
    },
    {
        "gap": "no_architecture_council_status_change_approval",
        "status": "blocked",
        "paths": (
            "Documentation/zigux/freeze-map.md",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
        ),
        "why_it_matters": "the landed governance packet still does not authorize a freeze-map status change or direct deep-core Zig delivery claim",
    },
)

REQUIRED_NOTE_MARKERS = (
    "`zigux/tests/phase15_readiness_gap_matrix.json`",
    "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
    "broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready",
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
    if rel.endswith(".zig"):
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    return f"# Placeholder for {rel}\n"


def _require_path(root: Path, rel: Path, failures: list[str]) -> None:
    if not (root / rel).exists():
        failures.append(f"missing_required_path:{rel.as_posix()}")


def _validate_requirements(matrix: dict, failures: list[str]) -> None:
    rows = matrix.get("roadmap_required_features", [])
    if len(rows) != len(EXPECTED_REQUIREMENTS):
        failures.append("roadmap_required_features:length")
        return

    for index, expected in enumerate(EXPECTED_REQUIREMENTS):
        row = rows[index]
        if row.get("requirement") != expected["requirement"]:
            failures.append(f"roadmap_required_features:{index}:requirement")
        if row.get("status") != expected["status"]:
            failures.append(f"roadmap_required_features:{index}:status")
        if tuple(row.get("evidence", [])) != expected["evidence"]:
            failures.append(f"roadmap_required_features:{index}:evidence")
        if row.get("remaining_gap") != expected["remaining_gap"]:
            failures.append(f"roadmap_required_features:{index}:remaining_gap")


def _validate_ledger(matrix: dict, failures: list[str]) -> None:
    rows = matrix.get("ledger_anchors", [])
    if len(rows) != 1:
        failures.append("ledger_anchors:length")
        return

    row = rows[0]
    if row.get("anchor") != EXPECTED_LEDGER_ANCHOR:
        failures.append("ledger_anchors:anchor")
    if row.get("status") != "landed_and_materially_exceeded":
        failures.append("ledger_anchors:status")
    if tuple(row.get("evidence", [])) != (
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase15-readiness-gate-survey.md",
    ):
        failures.append("ledger_anchors:evidence")
    if row.get("remaining_gap") != "none at the original docs-root anchor itself; the remaining readiness gaps now live in missing wrapper and workflow routes":
        failures.append("ledger_anchors:remaining_gap")


def _validate_gaps(matrix: dict, failures: list[str]) -> None:
    rows = matrix.get("remaining_readiness_gaps", [])
    if len(rows) != len(EXPECTED_GAPS):
        failures.append("remaining_readiness_gaps:length")
        return

    for index, expected in enumerate(EXPECTED_GAPS):
        row = rows[index]
        if row.get("gap") != expected["gap"]:
            failures.append(f"remaining_readiness_gaps:{index}:gap")
        if row.get("status") != expected["status"]:
            failures.append(f"remaining_readiness_gaps:{index}:status")
        if row.get("why_it_matters") != expected["why_it_matters"]:
            failures.append(f"remaining_readiness_gaps:{index}:why_it_matters")

        if "path" in expected and row.get("path") != expected["path"]:
            failures.append(f"remaining_readiness_gaps:{index}:path")
        if "blocked_routes" in expected and tuple(row.get("blocked_routes", [])) != expected["blocked_routes"]:
            failures.append(f"remaining_readiness_gaps:{index}:blocked_routes")
        if "paths" in expected and tuple(row.get("paths", [])) != expected["paths"]:
            failures.append(f"remaining_readiness_gaps:{index}:paths")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (
        READINESS_NOTE_PATH,
        MANIFEST_PATH,
        GAP_MATRIX_PATH,
        SELF_PATH,
        READY_CHECKER_PATH,
        VALIDATOR_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ):
        _require_path(root, rel, failures)
    if failures:
        return failures

    note = _read_text(root / READINESS_NOTE_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    matrix = _read_json(root / GAP_MATRIX_PATH)

    if matrix.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{matrix.get('lane_key')!r}")
    if matrix.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{matrix.get('phase')!r}")
    if matrix.get("surveyed_commit_mode") != "dated_master_readback":
        failures.append(f"surveyed_commit_mode:{matrix.get('surveyed_commit_mode')!r}")
    if matrix.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{matrix.get('surveyed_commit')!r}")
    if matrix.get("scope") != "tranche readiness gate survey remaining readiness gaps vs roadmap and ledger":
        failures.append(f"scope:{matrix.get('scope')!r}")

    if manifest.get("roadmap_ledger_gap_matrix") != str(GAP_MATRIX_PATH):
        failures.append("manifest:roadmap_ledger_gap_matrix")
    if manifest.get("surveyed_commit") != matrix.get("surveyed_commit"):
        failures.append("manifest:surveyed_commit_mismatch")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"note:missing:{marker}")
    if EXPECTED_SURVEYED_COMMIT not in note:
        failures.append("note:surveyed_commit")

    _validate_requirements(matrix, failures)
    _validate_ledger(matrix, failures)
    _validate_gaps(matrix, failures)

    return failures


def _sample_note() -> str:
    return f"""# Phase 15 Readiness Gate Survey

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`

This note says the governance packet is materially landed and reviewable, the dedicated validator now exists as a directly readable maintenance gate, the dedicated shared-build companion is now directly readable current-master evidence, the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit, and broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready.

- `zigux/tests/phase15_readiness_gap_matrix.json`
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": "P15-L04",
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "readiness_packet_checker": str(READY_CHECKER_PATH),
        "roadmap_ledger_gap_matrix": str(GAP_MATRIX_PATH),
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_gap_matrix() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "scope": "tranche readiness gate survey remaining readiness gaps vs roadmap and ledger",
        "roadmap_required_features": [
            {
                "requirement": entry["requirement"],
                "status": entry["status"],
                "evidence": list(entry["evidence"]),
                "remaining_gap": entry["remaining_gap"],
            }
            for entry in EXPECTED_REQUIREMENTS
        ],
        "ledger_anchors": [
            {
                "anchor": EXPECTED_LEDGER_ANCHOR,
                "status": "landed_and_materially_exceeded",
                "evidence": [
                    "Documentation/zigux/freeze-map.md",
                    "Documentation/zigux/review-checklist.md",
                    "Documentation/zigux/phase15-readiness-gate-survey.md",
                ],
                "remaining_gap": "none at the original docs-root anchor itself; the remaining readiness gaps now live in missing wrapper and workflow routes",
            }
        ],
        "remaining_readiness_gaps": [
            {
                "gap": entry["gap"],
                "status": entry["status"],
                **({"path": entry["path"]} if "path" in entry else {}),
                **({"paths": list(entry["paths"])} if "paths" in entry else {}),
                **({"blocked_routes": list(entry["blocked_routes"])} if "blocked_routes" in entry else {}),
                "why_it_matters": entry["why_it_matters"],
            }
            for entry in EXPECTED_GAPS
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / GAP_MATRIX_PATH, _sample_gap_matrix())
    for rel in (
        SELF_PATH,
        READY_CHECKER_PATH,
        VALIDATOR_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ):
        _write(root / rel, _placeholder_for(rel.as_posix()))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_readiness_gap_matrix_") as tmpdir:
        base = Path(tmpdir)

        baseline = base / "baseline"
        write_sample_root(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_requirement = base / "missing_requirement"
        write_sample_root(missing_requirement)
        payload = json.loads(_sample_gap_matrix())
        payload["roadmap_required_features"][0].pop("remaining_gap")
        _write(missing_requirement / GAP_MATRIX_PATH, json.dumps(payload, indent=2) + "\n")
        failures = collect_failures(missing_requirement)
        expected = ["roadmap_required_features:0:remaining_gap"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-requirement failure: {failures}")
        case_count += 1

        wrong_ledger = base / "wrong_ledger"
        write_sample_root(wrong_ledger)
        payload = json.loads(_sample_gap_matrix())
        payload["ledger_anchors"][0]["anchor"] = "wrong anchor"
        _write(wrong_ledger / GAP_MATRIX_PATH, json.dumps(payload, indent=2) + "\n")
        failures = collect_failures(wrong_ledger)
        expected = ["ledger_anchors:anchor"]
        if failures != expected:
            raise AssertionError(f"unexpected wrong-ledger failure: {failures}")
        case_count += 1

        wrong_gap = base / "wrong_gap"
        write_sample_root(wrong_gap)
        payload = json.loads(_sample_gap_matrix())
        payload["remaining_readiness_gaps"][1]["path"] = "wrong.yml"
        _write(wrong_gap / GAP_MATRIX_PATH, json.dumps(payload, indent=2) + "\n")
        failures = collect_failures(wrong_gap)
        expected = ["remaining_readiness_gaps:1:path"]
        if failures != expected:
            raise AssertionError(f"unexpected wrong-gap failure: {failures}")
        case_count += 1

        note_missing = base / "note_missing"
        write_sample_root(note_missing)
        _write(note_missing / READINESS_NOTE_PATH, "# note without gap matrix marker\n")
        failures = collect_failures(note_missing)
        expected = [
            "note:missing:`zigux/tests/phase15_readiness_gap_matrix.json`",
            "note:missing:the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
            "note:missing:broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready",
            "note:surveyed_commit",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected note-missing failure: {failures}")
        case_count += 1

    print("PHASE15_READINESS_GAP_MATRIX_SELF_TEST=pass")
    print(f"PHASE15_READINESS_GAP_MATRIX_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness gap matrix stays aligned with the current readiness packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic fixture coverage")
    parser.add_argument("--write-sample-root", type=Path, help="write a minimal passing sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_READINESS_GAP_MATRIX_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_READINESS_GAP_MATRIX=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
