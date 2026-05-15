#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

DOCS_ROOT_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
CATALOG_PATH = "Documentation/zigux/phase6-helper-parity-catalog.md"
PERF_SURVEY_PATH = "Documentation/zigux/phase6-perf-gate-survey.md"
SEQUENCING_PATH = "Documentation/zigux/phase6-leaf-helper-lane-sequencing.md"
MANIFEST_PATH = "zigux/tests/phase6_helper_parity_manifest.json"
SHARED_CHECKER_PATH = "scripts/zigux/check-phase6-shared-surface.py"
PERF_CHECKER_PATH = "scripts/zigux/check-phase6-perf-threshold-markers.py"
ENTRYPOINT_CHECKER_PATH = "scripts/zigux/check-phase6-present-entrypoints.py"
BUILD_PATH = "zigux/tests/phase6_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
VALIDATOR_PATH = "scripts/zigux/validate-phase6.py"

REQUIRED_FILES = (
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    CATALOG_PATH,
    PERF_SURVEY_PATH,
    SEQUENCING_PATH,
    MANIFEST_PATH,
    SHARED_CHECKER_PATH,
    PERF_CHECKER_PATH,
    ENTRYPOINT_CHECKER_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    VALIDATOR_PATH,
)

REQUIRED_MARKERS = {
    DOCS_ROOT_PATH: (
        "`Documentation/zigux/phase6-helper-parity-catalog.md`",
        "`Documentation/zigux/phase6-perf-gate-survey.md`",
        "`scripts/zigux/check-phase6-shared-surface.py`",
        "`zigux/tests/phase6_helper_parity_manifest.json`",
        "`make -C zigux phase6-validate`",
        "`make -C zigux phase6`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "does the patch make Zigux more buildable, more testable, or more reviewable?",
        "is there a stated performance gate if the code is algorithmic, queueing-sensitive, or driver-facing?",
    ),
    SCRIPTS_README_PATH: (
        "`Documentation/zigux/phase6-helper-parity-catalog.md`",
        "`Documentation/zigux/phase6-perf-gate-survey.md`",
        "`scripts/zigux/check-phase6-shared-surface.py`",
        "`scripts/zigux/check-phase6-perf-threshold-markers.py`",
        "`scripts/zigux/check-phase6-base64-c-parity.py`",
        "`scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "`scripts/zigux/check-phase6-checksum-c-parity.py`",
        "`scripts/zigux/check-phase6-hexdump-packet.py`",
        "`make -C zigux phase6-validate`",
    ),
    TESTS_README_PATH: (
        "`zigux/tests/phase6_build.zig`",
        "`zigux/tests/phase6_helper_parity_manifest.json`",
        "`Documentation/zigux/phase6-helper-parity-catalog.md`",
        "`Documentation/zigux/phase6-perf-gate-survey.md`",
        "`scripts/zigux/check-phase6-shared-surface.py`",
        "`make -C zigux phase6-validate`",
    ),
    CATALOG_PATH: (
        "`PHASE6_STATUS=partially_blocked`",
        "`PHASE6_PACKET=base64-bsearch-checksum-hexdump`",
        "shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`",
        "shared checker: `scripts/zigux/check-phase6-shared-surface.py`",
        "`make -C zigux phase6-validate`",
        "inventory-only",
        "phase6-checksum-perf",
    ),
    PERF_SURVEY_PATH: (
        "`PHASE6_PERF_SURVEY_STATUS=active`",
        "`PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`",
        "phase6-base64-perf",
        "phase6-checksum-perf",
        "phase6-hexdump-perf",
        "future same-lane follow-up should stay inside exact-threshold evidence, shared-route truthfulness, or the smallest shared replay repair",
    ),
    SEQUENCING_PATH: (
        "`PHASE6_LANE_MAP_STATUS=active`",
        "shared sequencing lane key: `P6-Y10`",
        "Use `P6-Y10` only for packet-wide routing, ownership, or anti-overlap truthfulness",
        "`scripts/zigux/check-phase6-shared-surface.py`",
        "`zigux/tests/phase6_helper_parity_manifest.json`",
    ),
    BUILD_PATH: (
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    ),
    WORKFLOW_PATH: (
        "Self-test Phase 6 shared-surface checker",
        "Check Phase 6 shared surface",
        "Self-test Phase 6 perf-threshold checker",
        "Check Phase 6 perf threshold markers",
        "Run Phase 6 hexdump perf gate",
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 6",
    "tranche": "leaf-helper-parity",
    "status": "partially_blocked",
    "surveyed_commit": "a0f4d7e",
}

REQUIRED_MANIFEST_SHARED_GATES = {
    DOCS_ROOT_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    CATALOG_PATH,
    PERF_SURVEY_PATH,
    SHARED_CHECKER_PATH,
    ENTRYPOINT_CHECKER_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
}

REQUIRED_MANIFEST_EXACT_CHECKS = {
    "python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase6-shared-surface.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test",
    "python3 scripts/zigux/check-phase6-present-entrypoints.py",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf",
}

REQUIRED_PACKET_SUMMARY = {
    "base64": "parked_reviewable",
    "bsearch": "parked_reviewable",
    "checksum": "parked_reviewable",
    "hexdump": "parked_reviewable",
}

REQUIRED_PERF_POSTURE = {
    "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
    "comparison_budget_helpers": ["bsearch"],
    "timing_sanity_only_helpers": [],
}

MAKEFILE_PHONY = (
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity "
    "phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf "
    "phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6"
)

MAKEFILE_LIVE_TARGETS = (
    "phase6-bsearch-test:",
    "phase6-hexdump-test:",
    "phase6-hexdump-review:",
    "phase6-checksum-perf:",
)

MAKEFILE_INVENTORY_ONLY_TARGETS = (
    "phase6-validate",
    "phase6-perf",
    "phase6",
    "phase6-base64-perf",
)

WORKFLOW_ABSENT_MARKERS = (
    "Validate Phase 6 shared packet",
    "python3 scripts/zigux/validate-phase6.py",
    "make -C zigux phase6-validate",
)

SELF_TEST_CASE_COUNT = 4


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def require_markers(repo_root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(repo_root / rel_path)
        for marker in markers:
            if marker not in text:
                raise ValidationError(f"missing expected Phase 6 marker in {rel_path}: {marker}")


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    for key, expected in REQUIRED_MANIFEST_FIELDS.items():
        if manifest.get(key) != expected:
            raise ValidationError(
                f"unexpected {key!r} in {MANIFEST_PATH}: {manifest.get(key)!r}"
            )

    if manifest.get("packet_state_summary") != REQUIRED_PACKET_SUMMARY:
        raise ValidationError(f"unexpected packet_state_summary in {MANIFEST_PATH}")

    if manifest.get("perf_posture") != REQUIRED_PERF_POSTURE:
        raise ValidationError(f"unexpected perf_posture in {MANIFEST_PATH}")

    shared_gates = manifest.get("shared_gates")
    if not isinstance(shared_gates, list):
        raise ValidationError(f"missing shared_gates in {MANIFEST_PATH}")
    missing_shared_gates = REQUIRED_MANIFEST_SHARED_GATES.difference(shared_gates)
    if missing_shared_gates:
        raise ValidationError(
            f"missing shared_gates in {MANIFEST_PATH}: {sorted(missing_shared_gates)}"
        )

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH}")
    missing_exact_checks = REQUIRED_MANIFEST_EXACT_CHECKS.difference(exact_checks)
    if missing_exact_checks:
        raise ValidationError(
            f"missing exact_checks in {MANIFEST_PATH}: {sorted(missing_exact_checks)}"
        )


def validate_makefile(repo_root: Path) -> None:
    text = read_text(repo_root / MAKEFILE_PATH)
    if MAKEFILE_PHONY not in text:
        raise ValidationError(f"missing Phase 6 phony inventory in {MAKEFILE_PATH}")

    for marker in MAKEFILE_LIVE_TARGETS:
        if marker not in text:
            raise ValidationError(f"missing live Phase 6 target in {MAKEFILE_PATH}: {marker}")

    for target in MAKEFILE_INVENTORY_ONLY_TARGETS:
        if re.search(rf"(?m)^{re.escape(target)}:\s*$", text):
            raise ValidationError(
                f"inventory-only Phase 6 target unexpectedly has a committed body in {MAKEFILE_PATH}: {target}"
            )


def validate_workflow(repo_root: Path) -> None:
    text = read_text(repo_root / WORKFLOW_PATH)
    for marker in WORKFLOW_ABSENT_MARKERS:
        if marker in text:
            raise ValidationError(
                f"unexpected live Phase 6 validator workflow marker in {WORKFLOW_PATH}: {marker}"
            )


def run_validation(repo_root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            raise ValidationError(f"missing required file: {rel_path}")

    require_markers(repo_root)
    validate_manifest(repo_root)
    validate_makefile(repo_root)
    validate_workflow(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    shared_gates = sorted(REQUIRED_MANIFEST_SHARED_GATES)
    exact_checks = sorted(REQUIRED_MANIFEST_EXACT_CHECKS)
    manifest = {
        **REQUIRED_MANIFEST_FIELDS,
        "packet_state_summary": REQUIRED_PACKET_SUMMARY,
        "perf_posture": REQUIRED_PERF_POSTURE,
        "shared_gates": shared_gates,
        "exact_checks": exact_checks,
    }

    write(
        root / DOCS_ROOT_PATH,
        "\n".join(
            [
                "# Docs",
                "`Documentation/zigux/phase6-helper-parity-catalog.md`",
                "`Documentation/zigux/phase6-perf-gate-survey.md`",
                "`scripts/zigux/check-phase6-shared-surface.py`",
                "`zigux/tests/phase6_helper_parity_manifest.json`",
                "`make -C zigux phase6-validate`",
                "`make -C zigux phase6`",
            ]
        )
        + "\n",
    )
    write(
        root / REVIEW_CHECKLIST_PATH,
        "\n".join(
            [
                "# Checklist",
                "does the patch make Zigux more buildable, more testable, or more reviewable?",
                "is there a stated performance gate if the code is algorithmic, queueing-sensitive, or driver-facing?",
            ]
        )
        + "\n",
    )
    write(
        root / SCRIPTS_README_PATH,
        "\n".join(
            [
                "# Scripts",
                "`Documentation/zigux/phase6-helper-parity-catalog.md`",
                "`Documentation/zigux/phase6-perf-gate-survey.md`",
                "`scripts/zigux/check-phase6-shared-surface.py`",
                "`scripts/zigux/check-phase6-perf-threshold-markers.py`",
                "`scripts/zigux/check-phase6-base64-c-parity.py`",
                "`scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
                "`scripts/zigux/check-phase6-checksum-c-parity.py`",
                "`scripts/zigux/check-phase6-hexdump-packet.py`",
                "`make -C zigux phase6-validate`",
            ]
        )
        + "\n",
    )
    write(
        root / TESTS_README_PATH,
        "\n".join(
            [
                "# Tests",
                "`zigux/tests/phase6_build.zig`",
                "`zigux/tests/phase6_helper_parity_manifest.json`",
                "`Documentation/zigux/phase6-helper-parity-catalog.md`",
                "`Documentation/zigux/phase6-perf-gate-survey.md`",
                "`scripts/zigux/check-phase6-shared-surface.py`",
                "`make -C zigux phase6-validate`",
            ]
        )
        + "\n",
    )
    write(
        root / CATALOG_PATH,
        "\n".join(
            [
                "# Catalog",
                "`PHASE6_STATUS=partially_blocked`",
                "`PHASE6_PACKET=base64-bsearch-checksum-hexdump`",
                "shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`",
                "shared checker: `scripts/zigux/check-phase6-shared-surface.py`",
                "`make -C zigux phase6-validate`",
                "inventory-only",
                "phase6-checksum-perf",
            ]
        )
        + "\n",
    )
    write(
        root / PERF_SURVEY_PATH,
        "\n".join(
            [
                "# Perf",
                "`PHASE6_PERF_SURVEY_STATUS=active`",
                "`PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`",
                "phase6-base64-perf",
                "phase6-checksum-perf",
                "phase6-hexdump-perf",
                "future same-lane follow-up should stay inside exact-threshold evidence, shared-route truthfulness, or the smallest shared replay repair",
            ]
        )
        + "\n",
    )
    write(
        root / SEQUENCING_PATH,
        "\n".join(
            [
                "# Sequencing",
                "`PHASE6_LANE_MAP_STATUS=active`",
                "shared sequencing lane key: `P6-Y10`",
                "Use `P6-Y10` only for packet-wide routing, ownership, or anti-overlap truthfulness",
                "`scripts/zigux/check-phase6-shared-surface.py`",
                "`zigux/tests/phase6_helper_parity_manifest.json`",
            ]
        )
        + "\n",
    )
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write(root / SHARED_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / PERF_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / ENTRYPOINT_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(
        root / BUILD_PATH,
        "\n".join(
            [
                'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
                'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
                'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
            ]
        )
        + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                MAKEFILE_PHONY,
                "phase6-bsearch-test:",
                "\ttrue",
                "phase6-hexdump-test:",
                "\ttrue",
                "phase6-hexdump-review:",
                "\ttrue",
                "phase6-checksum-perf:",
                "\ttrue",
            ]
        )
        + "\n",
    )
    write(
        root / WORKFLOW_PATH,
        "\n".join(
            [
                "Self-test Phase 6 shared-surface checker",
                "Check Phase 6 shared surface",
                "Self-test Phase 6 perf-threshold checker",
                "Check Phase 6 perf threshold markers",
                "Run Phase 6 hexdump perf gate",
            ]
        )
        + "\n",
    )
    write(root / VALIDATOR_PATH, "# placeholder replaced by real script\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validator_target = root / VALIDATOR_PATH
        validator_target.write_text(SELF_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        run_validation(root)

        broken_catalog = root / CATALOG_PATH
        broken_catalog.write_text("# broken\n", encoding="utf-8")
        try:
            run_validation(root)
        except ValidationError:
            pass
        else:
            raise ValidationError("self-test expected marker failure did not occur")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="path to the repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator scaffolding checks",
    )
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print(f"PHASE6_VALIDATE_SELF_TEST=pass cases={SELF_TEST_CASE_COUNT}")
        else:
            run_validation(args.repo_root.resolve())
            print("PHASE6_VALIDATE=pass")
    except ValidationError as exc:
        print(f"PHASE6_VALIDATE=fail reason={exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
