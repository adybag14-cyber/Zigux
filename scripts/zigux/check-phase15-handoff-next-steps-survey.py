#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
HANDOFF_ZIG_PATH = Path("zigux/tests/phase15_handoff_next_steps.zig")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

HANDOFF_REQUIRED_MARKERS = (
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-25`",
    "The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries",
    "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.",
    "`Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet",
    "keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there, reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py`, and only treat it as routine drift-follow-through after that wording exists and starts to diverge from the directly materialized governance packet",
    "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
)

SHARED_GAP_REQUIRED_MARKERS = (
    "## Current shared-summary watchpoints",
    "`Documentation/zigux/README.md`",
    "`zigux/tests/phase15_build.zig`",
)

SEQUENCING_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
    "the directly readable `zigux/tests/phase15_build.zig` shared build companion changes enough to force a packet rewrite",
)

SCRIPTS_README_REQUIRED_MARKERS = (
    "## Phase 15",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_build.zig`",
)

TESTS_README_REQUIRED_MARKERS = (
    "## Phase 10 shared virtio closure packet",
)

DOCS_README_REQUIRED_MARKERS = (
    "Phase 14 notes",
)

MANIFEST_REQUIRED = {
    "lane_key": "P15-L12",
    "slice": "existing_governance_packet_handoff_inventory",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2) + "\n")


def _has_make_target(text: str, target: str) -> bool:
    return f"\n{target}:" in ("\n" + text)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    required_paths = (
        HANDOFF_NOTE_PATH,
        SHARED_GAP_NOTE_PATH,
        SEQUENCING_NOTE_PATH,
        DOCS_README_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        VALIDATOR_PATH,
        MANIFEST_PATH,
        HANDOFF_ZIG_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    handoff = _read(root / HANDOFF_NOTE_PATH)
    shared_gap = _read(root / SHARED_GAP_NOTE_PATH)
    sequencing = _read(root / SEQUENCING_NOTE_PATH)
    docs_readme = _read(root / DOCS_README_PATH)
    scripts_readme = _read(root / SCRIPTS_README_PATH)
    tests_readme = _read(root / TESTS_README_PATH)
    manifest = json.loads(_read(root / MANIFEST_PATH))
    makefile = _read(root / MAKEFILE_PATH)

    for marker in HANDOFF_REQUIRED_MARKERS:
        if marker not in handoff:
            failures.append(f"handoff:missing:{marker}")

    for marker in SHARED_GAP_REQUIRED_MARKERS:
        if marker not in shared_gap:
            failures.append(f"shared_gap:missing:{marker}")

    for marker in SEQUENCING_REQUIRED_MARKERS:
        if marker not in sequencing:
            failures.append(f"sequencing:missing:{marker}")

    for marker in DOCS_README_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:missing:{marker}")

    for marker in SCRIPTS_README_REQUIRED_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"scripts_readme:missing:{marker}")

    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:missing:{marker}")

    for key, value in MANIFEST_REQUIRED.items():
        if manifest.get(key) != value:
            failures.append(f"manifest:{key}:{manifest.get(key)!r}")

    required_manifest_paths = (
        "Documentation/zigux/phase15-handoff-next-steps-survey.md",
        "Documentation/zigux/phase15-shared-summary-gap.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "Documentation/zigux/README.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "scripts/zigux/validate-phase15.py",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/tests/phase15_build.zig",
    )
    paths = manifest.get("direct_packet_paths")
    if not isinstance(paths, list):
        failures.append("manifest:direct_packet_paths:not_list")
    else:
        for rel in required_manifest_paths:
            if rel not in paths:
                failures.append(f"manifest:missing_direct_path:{rel}")

    if _has_make_target(makefile, "phase15-validate"):
        failures.append("makefile:unexpected_phase15_validate")
    if _has_make_target(makefile, "phase15-test"):
        failures.append("makefile:unexpected_phase15_test")
    if _has_make_target(makefile, "phase15"):
        failures.append("makefile:unexpected_phase15")

    return failures


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

## Status

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`

The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears.

Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.

- `Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet
- keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there, reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py`, and only treat it as routine drift-follow-through after that wording exists and starts to diverge from the directly materialized governance packet
- no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`
- no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`
"""


def _sample_shared_gap() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/README.md`
- `zigux/tests/phase15_build.zig`
"""


def _sample_sequencing() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
- the directly readable `zigux/tests/phase15_build.zig` shared build companion changes enough to force a packet rewrite
"""


def _sample_docs_readme() -> str:
    return """# Zigux Documentation

Phase 14 notes
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
"""


def _sample_scripts_readme() -> str:
    return """# scripts/zigux

## Phase 15

- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_build.zig`
"""


def _sample_tests_readme() -> str:
    return """# zigux/tests

## Phase 10 shared virtio closure packet
"""


def _sample_manifest() -> dict:
    return {
        "lane_key": "P15-L12",
        "slice": "existing_governance_packet_handoff_inventory",
        "direct_packet_paths": [
            "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "Documentation/zigux/phase15-shared-summary-gap.md",
            "Documentation/zigux/phase15-governance-lane-sequencing.md",
            "Documentation/zigux/README.md",
            "scripts/zigux/README.md",
            "zigux/tests/README.md",
            "scripts/zigux/validate-phase15.py",
            "zigux/tests/phase15_handoff_next_steps.zig",
            "zigux/tests/phase15_build.zig",
        ],
    }


def _seed(root: Path) -> None:
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap())
    _write(root / SEQUENCING_NOTE_PATH, _sample_sequencing())
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / SCRIPTS_README_PATH, _sample_scripts_readme())
    _write(root / TESTS_README_PATH, _sample_tests_readme())
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write_json(root / MANIFEST_PATH, _sample_manifest())
    _write(root / HANDOFF_ZIG_PATH, 'const std = @import("std");\n')
    _write(root / BUILD_PATH, 'const std = @import("std");\n')
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_next_steps_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_handoff_marker = root / "missing_handoff_marker"
        _seed(missing_handoff_marker)
        _write(
            missing_handoff_marker / HANDOFF_NOTE_PATH,
            _sample_handoff().replace(
                HANDOFF_REQUIRED_MARKERS[4] + "\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_handoff_marker)
        expected = [f"handoff:missing:{HANDOFF_REQUIRED_MARKERS[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected handoff failures: {failures}")
        case_count += 1

        missing_manifest_path = root / "missing_manifest_path"
        _seed(missing_manifest_path)
        payload = _sample_manifest()
        payload["direct_packet_paths"].remove("zigux/tests/phase15_build.zig")
        _write_json(missing_manifest_path / MANIFEST_PATH, payload)
        failures = collect_failures(missing_manifest_path)
        expected = ["manifest:missing_direct_path:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected manifest failures: {failures}")
        case_count += 1

        unexpected_target = root / "unexpected_target"
        _seed(unexpected_target)
        _write(unexpected_target / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(unexpected_target)
        expected = ["makefile:unexpected_phase15_validate"]
        if failures != expected:
            raise AssertionError(f"unexpected makefile failures: {failures}")
        case_count += 1

        missing_scripts_marker = root / "missing_scripts_marker"
        _seed(missing_scripts_marker)
        _write(
            missing_scripts_marker / SCRIPTS_README_PATH,
            _sample_scripts_readme().replace("`zigux/tests/phase15_build.zig`\n", "", 1),
        )
        failures = collect_failures(missing_scripts_marker)
        expected = ["scripts_readme:missing:`zigux/tests/phase15_build.zig`"]
        if failures != expected:
            raise AssertionError(f"unexpected scripts README failures: {failures}")
        case_count += 1

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff-next-steps survey stays aligned."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
