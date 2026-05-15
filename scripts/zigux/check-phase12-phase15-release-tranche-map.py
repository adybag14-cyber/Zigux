#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

TRANCHE_MAP_REL = "Documentation/zigux/phase12-phase15-release-tranche-map.md"
READINESS_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
LANE_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"

TRANCHE_MARKERS = (
    "# Phase 12-15 Release Tranche Map",
    "`RELEASE_PACKET_PHASE_COUNT=4`",
    "`RELEASE_PACKET_ACTIVE_PHASES=phase12,phase13,phase14,phase15`",
    "`RELEASE_PACKET_RELEASE_CLOSED_PHASE_COUNT=0`",
    "Treat `Phase 12` as the active release packet that still owns smoke-first replay truthfulness.",
    "Treat `Phase 15` as parked governance maintenance until an Architecture Council status-change approval actually lands.",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "do not treat review-process, parity-scorecard-survey, parity-scorecard, or indefinite-C maintenance as shared-summary backlog or release-unblock evidence",
    "wait for a named reopen trigger or a real blocker-posture change; otherwise keep summary work limited to truthfulness repairs",
)

READINESS_MARKERS = (
    "`PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-14`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
)

LANE_MARKERS = (
    "`PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-14`",
    "`parity-scorecard-survey`: owns `Documentation/zigux/phase15-parity-scorecard-survey.md`",
    "`parity-scorecard`: owns `Documentation/zigux/phase15-parity-scorecard.md`, `zigux/tests/phase15_parity_scorecard.json`, and `zigux/tests/phase15_parity_scorecard.zig`",
    "`readiness-gate`: owns `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_readiness_gate.zig`, and `scripts/zigux/validate-phase15.py`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _extract_marker_value(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :]
    return None


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    paths = [TRANCHE_MAP_REL, READINESS_REL, LANE_REL]
    for rel in paths:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    tranche_text = _read(root / TRANCHE_MAP_REL)
    readiness_text = _read(root / READINESS_REL)
    lane_text = _read(root / LANE_REL)

    for marker in TRANCHE_MARKERS:
        if marker not in tranche_text:
            issues.append(f"tranche_map:missing:{marker}")
    for marker in READINESS_MARKERS:
        if marker not in readiness_text:
            issues.append(f"readiness:missing:{marker}")
    for marker in LANE_MARKERS:
        if marker not in lane_text:
            issues.append(f"lane:missing:{marker}")

    tranche_provenance = _extract_marker_value(tranche_text, "- `RELEASE_PACKET_PROVENANCE=")
    if tranche_provenance is not None and tranche_provenance.endswith("`"):
        tranche_provenance = tranche_provenance[:-1]
    readiness_head = _extract_marker_value(readiness_text, "- `PHASE15_SURVEYED_HEAD=")
    if readiness_head is not None and readiness_head.endswith("`"):
        readiness_head = readiness_head[:-1]
    lane_head = _extract_marker_value(lane_text, "- `PHASE15_SURVEYED_HEAD=")
    if lane_head is not None and lane_head.endswith("`"):
        lane_head = lane_head[:-1]

    if tranche_provenance is None:
        issues.append("tranche_map:missing:RELEASE_PACKET_PROVENANCE")
    if readiness_head is None:
        issues.append("readiness:missing:PHASE15_SURVEYED_HEAD")
    if lane_head is None:
        issues.append("lane:missing:PHASE15_SURVEYED_HEAD")

    if tranche_provenance and readiness_head and tranche_provenance != readiness_head:
        issues.append("alignment:tranche_map_vs_readiness_head")
    if readiness_head and lane_head and readiness_head != lane_head:
        issues.append("alignment:readiness_vs_lane_head")

    return issues


def _seed_fixture_tree(root: Path) -> None:
    _write(
        root / TRANCHE_MAP_REL,
        "\n".join(
            [
                "# Phase 12-15 Release Tranche Map",
                "",
                "- `RELEASE_PACKET_PROVENANCE=current-master-readback-2026-05-14`",
                "- `RELEASE_PACKET_PHASE_COUNT=4`",
                "- `RELEASE_PACKET_ACTIVE_PHASES=phase12,phase13,phase14,phase15`",
                "- `RELEASE_PACKET_RELEASE_CLOSED_PHASE_COUNT=0`",
                "",
                "Treat `Phase 12` as the active release packet that still owns smoke-first replay truthfulness.",
                "Treat `Phase 15` as parked governance maintenance until an Architecture Council status-change approval actually lands.",
                "`Documentation/zigux/phase12-release-sequencing.md`",
                "`Documentation/zigux/phase12-release-closure-checklist.md`",
                "`Documentation/zigux/phase12-release-readiness-survey.md`",
                "`Documentation/zigux/phase12-release-coordination-matrix.md`",
                "`Documentation/zigux/phase15-readiness-gate-survey.md`",
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "`Documentation/zigux/phase15-freeze-map-governance.md`",
                "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "`Documentation/zigux/phase15-parity-scorecard.md`",
                "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
                "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
                "do not treat review-process, parity-scorecard-survey, parity-scorecard, or indefinite-C maintenance as shared-summary backlog or release-unblock evidence",
                "wait for a named reopen trigger or a real blocker-posture change; otherwise keep summary work limited to truthfulness repairs",
                "",
            ]
        ),
    )
    _write(
        root / READINESS_REL,
        "\n".join(
            [
                "# Phase 15 Readiness Gate Survey",
                "",
                "- `PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-14`",
                "- no Architecture Council approval is currently recorded for a freeze-map status change",
                "- `Documentation/zigux/phase15-architecture-council-review-process.md`",
                "- `Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "- `Documentation/zigux/phase15-parity-scorecard.md`",
                "- `Documentation/zigux/phase15-governance-lane-sequencing.md`",
                "",
            ]
        ),
    )
    _write(
        root / LANE_REL,
        "\n".join(
            [
                "# Phase 15 Governance Lane Sequencing",
                "",
                "- `PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-14`",
                "- `parity-scorecard-survey`: owns `Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "- `parity-scorecard`: owns `Documentation/zigux/phase15-parity-scorecard.md`, `zigux/tests/phase15_parity_scorecard.json`, and `zigux/tests/phase15_parity_scorecard.zig`",
                "- `readiness-gate`: owns `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_readiness_gate.zig`, and `scripts/zigux/validate-phase15.py`",
                "- no Architecture Council approval is currently recorded for a freeze-map status change",
                "",
            ]
        ),
    )


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(
            f"phase12-phase15-release-tranche-map-self-test:{label}:got={actual!r}:want={expected!r}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_release_tranche_map_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        tranche_path = root / TRANCHE_MAP_REL
        _write(
            tranche_path,
            _read(tranche_path).replace("`Documentation/zigux/phase15-parity-scorecard.md`\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["tranche_map:missing:`Documentation/zigux/phase15-parity-scorecard.md`"],
            "missing_phase15_scorecard_note",
        )
        _seed_fixture_tree(root)
        case_count += 1

        _write(
            tranche_path,
            _read(tranche_path).replace(
                "- `RELEASE_PACKET_PROVENANCE=current-master-readback-2026-05-14`\n",
                "- `RELEASE_PACKET_PROVENANCE=current-master-readback-2026-05-13`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["alignment:tranche_map_vs_readiness_head"],
            "stale_release_packet_provenance",
        )
        _seed_fixture_tree(root)
        case_count += 1

        lane_path = root / LANE_REL
        _write(
            lane_path,
            _read(lane_path).replace(
                "- `PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-14`\n",
                "- `PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-13`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "lane:missing:`PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-14`",
                "alignment:readiness_vs_lane_head",
            ],
            "lane_head_drift",
        )
        case_count += 1

    print("PHASE12_PHASE15_RELEASE_TRANCHE_MAP_SELF_TEST=pass")
    print(f"PHASE12_PHASE15_RELEASE_TRANCHE_MAP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the late-phase PMO release tranche map aligned with the live Phase 15 governance packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE12_PHASE15_RELEASE_TRANCHE_MAP=fail")
        print("PHASE12_PHASE15_RELEASE_TRANCHE_MAP_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE12_PHASE15_RELEASE_TRANCHE_MAP_ISSUES_END")
        return 1

    print("PHASE12_PHASE15_RELEASE_TRANCHE_MAP=pass")
    print(f"PHASE12_PHASE15_RELEASE_TRANCHE_MAP_REQUIRED_MARKER_COUNT={len(TRANCHE_MARKERS) + len(READINESS_MARKERS) + len(LANE_MARKERS) + 2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
