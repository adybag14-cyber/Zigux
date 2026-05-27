#!/usr/bin/env python3
"""Validate the current Phase 6 shared helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HELPER_EVIDENCE_CATALOG = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_PARITY_CATALOG = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")
PHASE6_BUILD = Path("zigux/tests/phase6_build.zig")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
SHARED_SURFACE_CHECKER = Path("scripts/zigux/check-phase6-shared-surface.py")
PRESENT_ENTRYPOINTS_CHECKER = Path("scripts/zigux/check-phase6-present-entrypoints.py")
BASE64_CORPUS_CHECKER = Path("scripts/zigux/check-phase6-base64-corpus-determinism.py")
BASE64_C_PARITY_CHECKER = Path("scripts/zigux/check-phase6-base64-c-parity.py")
BSEARCH_CORPUS_CHECKER = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
BSEARCH_C_PARITY_CHECKER = Path("scripts/zigux/check-phase6-bsearch-c-parity.py")
BASE64_BSEARCH_PERF_MARKERS_CHECKER = Path(
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py"
)
CHECKSUM_CORPUS_CHECKER = Path("scripts/zigux/check-phase6-checksum-corpus-evidence.py")
CHECKSUM_C_PARITY_CHECKER = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
CHECKSUM_HEXDUMP_PERF_MARKERS_CHECKER = Path(
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"
)
HEXDUMP_PACKET_CHECKER = Path("scripts/zigux/check-phase6-hexdump-packet.py")
HEXDUMP_ROUTE_CHECKER = Path("scripts/zigux/check-phase6-hexdump-route.py")
PERF_THRESHOLD_CHECKER = Path("scripts/zigux/check-phase6-perf-threshold-markers.py")

CHECKER_INVOCATIONS = [
    (SHARED_SURFACE_CHECKER, "--repo-root"),
    (PRESENT_ENTRYPOINTS_CHECKER, "--repo-root"),
    (BASE64_CORPUS_CHECKER, "--repo-root"),
    (BASE64_C_PARITY_CHECKER, None),
    (BSEARCH_CORPUS_CHECKER, "--repo-root"),
    (BSEARCH_C_PARITY_CHECKER, None),
    (BASE64_BSEARCH_PERF_MARKERS_CHECKER, "--repo-root"),
    (CHECKSUM_CORPUS_CHECKER, "--repo-root"),
    (CHECKSUM_C_PARITY_CHECKER, None),
    (CHECKSUM_HEXDUMP_PERF_MARKERS_CHECKER, "--repo-root"),
    (HEXDUMP_PACKET_CHECKER, "--repo-root"),
    (HEXDUMP_ROUTE_CHECKER, "--root"),
    (PERF_THRESHOLD_CHECKER, "--repo-root"),
]

REQUIRED_FILES = [
    HELPER_EVIDENCE_CATALOG,
    HELPER_PARITY_CATALOG,
    HELPER_EVIDENCE_MANIFEST,
    HELPER_PARITY_MANIFEST,
    PHASE6_BUILD,
    MAKEFILE,
    WORKFLOW,
    *[checker for checker, _ in CHECKER_INVOCATIONS],
]

EXPECTED_HELPER_EVIDENCE_PACKET = "phase6-helper-evidence"
EXPECTED_HELPER_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_EVIDENCE_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_CURRENT_DIRECT_READBACK_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_SHARED_DIRECT_EVIDENCE = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_SHARED_PERF_WRAPPER = "make -C zigux phase6-perf"
EXPECTED_SHARED_PERF_WRAPPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_SHARED_PUBLIC_COMPANIONS = []
EXPECTED_BASE64_DIRECT_GAPS: list[str] = []
EXPECTED_EVIDENCE_CURRENT_GAPS = EXPECTED_BASE64_DIRECT_GAPS
EXPECTED_PARITY_FOLLOW_THROUGH_GAPS = []
EXPECTED_SHARED_REPLAY_INVENTORY = [
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
    "python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-validate:",
    "$(PYTHON) scripts/zigux/validate-phase6.py",
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf-matrix-test:",
    "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_BUILD_SNIPPETS = [
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_perf_root_module = b.createModule(.{',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    "const checksum_perf_matrix_test_step = b.step(",
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "- name: Run current Phase 6 shared perf route",
    "run: make -C zigux phase6-perf",
]

REQUIRED_CATALOG_SNIPPETS = [
    "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
    "## Roadmap perf-gap readback",
    "## Current shared replay inventory",
    "- `python3 scripts/zigux/check-phase6-base64-c-parity.py`",
    "- `make -C zigux phase6-bsearch-perf`",
    "- `python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`",
    "- `make -C zigux phase6-checksum-perf-matrix-test`",
    "- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`",
    "- `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the Phase 6 base64 packet no longer carries a known direct-readback generator gap.",
]

REQUIRED_PARITY_CATALOG_SNIPPETS = [
    "- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "- helper-evidence row: `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts/zigux/check-phase6-base64-corpus-determinism.py`, `scripts/zigux/check-phase6-base64-c-parity.py`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
    "- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, direct C parity runner, direct C parity harness, direct C parity vectors companion, direct C parity casegen companion, direct C parity checker, and slice note. A targeted authenticated current-master reread on 2026-05-27 directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the base64 row no longer carries a known generator-side direct-readback gap.",
    "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note, so the checksum row now ships the same external parity review hook as the other portability-sensitive Phase 6 helpers without reopening hexdump work",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, `scripts/zigux/validate-phase6.py`, `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`, `scripts/zigux/check-phase6-perf-threshold-markers.py`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.",
    "broader reminder surfaces can keep the shared survey plus the base64-bsearch, checksum-hexdump, and perf-threshold guard surfaces inside the directly readable shared packet instead of treating any of those guards as fallback-only evidence.",
]

REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig and zigux/tests/phase6_base64_c_casegen.zig, so the base64 helper row no longer carries a known generator-side direct-readback gap.",
]

REQUIRED_PARITY_PERF_NOTE_SNIPPETS = [
    "zigux/tests/phase6_bsearch_perf.zig",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
]

EXPECTED_BSEARCH_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "scripts/zigux/check-phase6-bsearch-c-parity.py",
]

EXPECTED_CHECKSUM_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]

EXPECTED_HEXDUMP_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]

SELF_TEST_CASE_COUNT = 29


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def require_text_snippets(name: str, content: object, snippets: list[str]) -> None:
    if not isinstance(content, str):
        raise ValidationError(f"{name} missing")
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"{name} drifted: {snippet}")


def extract_shared_perf_wrapper_keys(helper_parity_manifest: dict[str, object]) -> list[str]:
    helpers = helper_parity_manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helper parity helpers missing")

    keys: list[str] = []
    for helper in helpers:
        if not isinstance(helper, dict):
            continue
        current_perf_evidence = helper.get("current_perf_evidence")
        if not isinstance(current_perf_evidence, dict):
            continue
        routes = current_perf_evidence.get("linux_style_rerun_routes")
        if isinstance(routes, list) and EXPECTED_SHARED_PERF_WRAPPER in routes:
            key = helper.get("key")
            if isinstance(key, str):
                keys.append(key)
    return keys


def run_checker(root: Path, checker: Path, flag: str | None) -> None:
    cmd = [sys.executable, str(root / checker)]
    if flag is not None:
        cmd.extend([flag, str(root)])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker.as_posix()} failed: {detail}")


def require_helper_checker_surfaces(
    manifest: dict[str, object], manifest_name: str, helper_key: str, expected_surfaces: list[str]
) -> None:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"{manifest_name} helpers missing")

    for helper in helpers:
        if not isinstance(helper, dict) or helper.get("key") != helper_key:
            continue
        checker_surfaces = helper.get("checker_surfaces")
        if checker_surfaces != expected_surfaces:
            raise ValidationError(
                f"{manifest_name} {helper_key} checker surfaces drift"
            )
        return

    raise ValidationError(f"{manifest_name} {helper_key} helper missing")


def require_helper_field(
    manifest: dict[str, object],
    manifest_name: str,
    helper_key: str,
    field_name: str,
    expected_value: object,
) -> None:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"{manifest_name} helpers missing")

    for helper in helpers:
        if not isinstance(helper, dict) or helper.get("key") != helper_key:
            continue
        if helper.get(field_name) != expected_value:
            raise ValidationError(
                f"{manifest_name} {helper_key} {field_name} drift"
            )
        return

    raise ValidationError(f"{manifest_name} {helper_key} helper missing")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    helper_evidence_manifest = read_json(root / HELPER_EVIDENCE_MANIFEST)
    helper_parity_manifest = read_json(root / HELPER_PARITY_MANIFEST)
    if helper_evidence_manifest.get("packet") != EXPECTED_HELPER_EVIDENCE_PACKET:
        raise ValidationError("phase6 helper evidence packet drift")
    if helper_parity_manifest.get("packet") != EXPECTED_HELPER_PARITY_PACKET:
        raise ValidationError("phase6 helper parity packet drift")
    if helper_evidence_manifest.get("phase") != EXPECTED_PHASE or helper_parity_manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 phase drift")
    if helper_evidence_manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("phase6 helper evidence surveyed_head drift")
    if helper_parity_manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("phase6 helper parity surveyed_head drift")
    if helper_evidence_manifest.get("lane_scope") != EXPECTED_EVIDENCE_LANE_SCOPE:
        raise ValidationError("phase6 helper evidence lane_scope drift")
    if helper_parity_manifest.get("lane_scope") != EXPECTED_PARITY_LANE_SCOPE:
        raise ValidationError("phase6 helper parity lane_scope drift")
    if helper_evidence_manifest.get("current_direct_readback_companions") != EXPECTED_CURRENT_DIRECT_READBACK_COMPANIONS:
        raise ValidationError("phase6 helper evidence direct-readback companion drift")
    if helper_evidence_manifest.get("public_tree_backed_shared_companions") != EXPECTED_SHARED_PUBLIC_COMPANIONS:
        raise ValidationError("phase6 helper evidence public companion drift")
    if helper_evidence_manifest.get("current_repo_reality_gaps") != EXPECTED_EVIDENCE_CURRENT_GAPS:
        raise ValidationError("phase6 helper evidence repo-reality gap drift")
    if helper_parity_manifest.get("shared_direct_evidence") != EXPECTED_SHARED_DIRECT_EVIDENCE:
        raise ValidationError("phase6 helper parity shared direct evidence drift")
    if helper_evidence_manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 roadmap anchors drift")
    if helper_evidence_manifest.get("current_shared_replay_inventory") != EXPECTED_SHARED_REPLAY_INVENTORY:
        raise ValidationError("phase6 shared replay inventory drift")
    if extract_shared_perf_wrapper_keys(helper_parity_manifest) != EXPECTED_SHARED_PERF_WRAPPER_KEYS:
        raise ValidationError("phase6 shared perf wrapper route drift")
    if helper_parity_manifest.get("public_tree_backed_shared_companions") != EXPECTED_SHARED_PUBLIC_COMPANIONS:
        raise ValidationError("phase6 helper parity public companion drift")
    if helper_parity_manifest.get("shared_follow_through_gaps") != EXPECTED_PARITY_FOLLOW_THROUGH_GAPS:
        raise ValidationError("phase6 helper parity follow-through gap drift")
    require_helper_field(
        helper_evidence_manifest,
        "phase6 helper evidence manifest",
        "base64",
        "still_missing_direct_companions",
        EXPECTED_BASE64_DIRECT_GAPS,
    )
    require_helper_checker_surfaces(
        helper_evidence_manifest,
        "phase6 helper evidence manifest",
        "bsearch",
        EXPECTED_BSEARCH_CHECKER_SURFACES,
    )
    require_helper_checker_surfaces(
        helper_evidence_manifest,
        "phase6 helper evidence manifest",
        "checksum",
        EXPECTED_CHECKSUM_CHECKER_SURFACES,
    )
    require_helper_checker_surfaces(
        helper_evidence_manifest,
        "phase6 helper evidence manifest",
        "hexdump",
        EXPECTED_HEXDUMP_CHECKER_SURFACES,
    )
    require_helper_field(
        helper_parity_manifest,
        "phase6 helper parity manifest",
        "base64",
        "still_missing_direct_companions",
        EXPECTED_BASE64_DIRECT_GAPS,
    )
    require_helper_checker_surfaces(
        helper_parity_manifest,
        "phase6 helper parity manifest",
        "bsearch",
        EXPECTED_BSEARCH_CHECKER_SURFACES,
    )
    require_helper_checker_surfaces(
        helper_parity_manifest,
        "phase6 helper parity manifest",
        "checksum",
        EXPECTED_CHECKSUM_CHECKER_SURFACES,
    )
    require_helper_checker_surfaces(
        helper_parity_manifest,
        "phase6 helper parity manifest",
        "hexdump",
        EXPECTED_HEXDUMP_CHECKER_SURFACES,
    )

    require_snippets(root / MAKEFILE, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(root / PHASE6_BUILD, REQUIRED_BUILD_SNIPPETS)
    require_snippets(root / WORKFLOW, REQUIRED_WORKFLOW_SNIPPETS)
    require_snippets(root / HELPER_EVIDENCE_CATALOG, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(root / HELPER_PARITY_CATALOG, REQUIRED_PARITY_CATALOG_SNIPPETS)
    require_text_snippets(
        "phase6 helper parity coverage note",
        helper_parity_manifest.get("coverage_verification_note"),
        REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS,
    )
    require_text_snippets(
        "phase6 helper parity perf note",
        helper_parity_manifest.get("perf_evidence_readback_note"),
        REQUIRED_PARITY_PERF_NOTE_SNIPPETS,
    )

    for checker, flag in CHECKER_INVOCATIONS:
        run_checker(root, checker, flag)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_checker_stub(expected_flag: str | None) -> str:
    if expected_flag is None:
        return "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "",
                "if len(sys.argv) != 1:",
                "    raise SystemExit(f'unexpected argv length: {len(sys.argv)}')",
                "",
            ]
        )
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "from pathlib import Path",
            "import sys",
            f"EXPECTED_FLAG = {expected_flag!r}",
            "",
            "if len(sys.argv) != 3:",
            "    raise SystemExit(f'unexpected argv length: {len(sys.argv)}')",
            "if sys.argv[1] != EXPECTED_FLAG:",
            "    raise SystemExit(f'unexpected flag: {sys.argv[1]}')",
            "if not Path(sys.argv[2]).is_dir():",
            "    raise SystemExit(f'unexpected repo root: {sys.argv[2]}')",
            "",
        ]
    )


def scaffold_repo(root: Path) -> None:
    write(root / HELPER_EVIDENCE_CATALOG, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_PARITY_CATALOG, "\n".join(REQUIRED_PARITY_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_EVIDENCE_MANIFEST, json.dumps({
        "packet": EXPECTED_HELPER_EVIDENCE_PACKET,
        "phase": EXPECTED_PHASE,
        "surveyed_head": EXPECTED_SURVEYED_HEAD,
        "lane_scope": EXPECTED_EVIDENCE_LANE_SCOPE,
        "current_direct_readback_companions": EXPECTED_CURRENT_DIRECT_READBACK_COMPANIONS,
        "public_tree_backed_shared_companions": EXPECTED_SHARED_PUBLIC_COMPANIONS,
        "current_repo_reality_gaps": EXPECTED_EVIDENCE_CURRENT_GAPS,
        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
        "current_shared_replay_inventory": EXPECTED_SHARED_REPLAY_INVENTORY,
        "helpers": [
            {
                "key": "base64",
                "still_missing_direct_companions": EXPECTED_BASE64_DIRECT_GAPS,
            },
            {
                "key": "bsearch",
                "checker_surfaces": EXPECTED_BSEARCH_CHECKER_SURFACES,
            },
            {
                "key": "checksum",
                "checker_surfaces": EXPECTED_CHECKSUM_CHECKER_SURFACES,
            },
            {
                "key": "hexdump",
                "checker_surfaces": EXPECTED_HEXDUMP_CHECKER_SURFACES,
            },
        ],
    }, indent=2) + "\n")
    write(root / HELPER_PARITY_MANIFEST, json.dumps({
        "packet": EXPECTED_HELPER_PARITY_PACKET,
        "phase": EXPECTED_PHASE,
        "surveyed_head": EXPECTED_SURVEYED_HEAD,
        "lane_scope": EXPECTED_PARITY_LANE_SCOPE,
        "shared_direct_evidence": EXPECTED_SHARED_DIRECT_EVIDENCE,
        "public_tree_backed_shared_companions": EXPECTED_SHARED_PUBLIC_COMPANIONS,
        "coverage_verification_note": " ".join(REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS),
        "perf_evidence_readback_note": " ".join(REQUIRED_PARITY_PERF_NOTE_SNIPPETS),
        "shared_follow_through_gaps": EXPECTED_PARITY_FOLLOW_THROUGH_GAPS,
        "helpers": [
            {
                "key": "base64",
                "still_missing_direct_companions": EXPECTED_BASE64_DIRECT_GAPS,
                "current_perf_evidence": {"linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER]},
            },
            {"key": "bsearch", "checker_surfaces": EXPECTED_BSEARCH_CHECKER_SURFACES, "current_perf_evidence": {"linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER]}},
            {"key": "checksum", "checker_surfaces": EXPECTED_CHECKSUM_CHECKER_SURFACES, "current_perf_evidence": {"linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER]}},
            {"key": "hexdump", "checker_surfaces": EXPECTED_HEXDUMP_CHECKER_SURFACES, "current_perf_evidence": {"linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER]}},
        ],
    }, indent=2) + "\n")
    write(root / PHASE6_BUILD, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / WORKFLOW, "\n".join(REQUIRED_WORKFLOW_SNIPPETS) + "\n")
    for checker, expected_flag in CHECKER_INVOCATIONS:
        write(root / checker, make_checker_stub(expected_flag))


def expect_failure(fn) -> None:
    try:
        fn()
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        def reset() -> None:
            scaffold_repo(root)

        def expect_mutation(mutator) -> None:
            nonlocal cases_run
            reset()
            mutator()
            expect_failure(lambda: validate(root))
            cases_run += 1

        cases_run = 0
        expect_mutation(
            lambda: write(
                root / MAKEFILE,
                read_text(root / MAKEFILE).replace("phase6-bsearch-perf:\n", "", 1),
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_CATALOG,
                read_text(root / HELPER_EVIDENCE_CATALOG).replace(
                    "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`\n",
                    "",
                    1,
                ),
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "current_direct_readback_companions": [
                            item
                            for item in read_json(root / HELPER_EVIDENCE_MANIFEST)[
                                "current_direct_readback_companions"
                            ]
                            if item != "scripts/zigux/check-phase6-perf-threshold-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "public_tree_backed_shared_companions": [
                            "Documentation/zigux/phase6-perf-gate-survey.md"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "base64"
                            else {
                                **helper,
                                "still_missing_direct_companions": [
                                    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig"
                                ],
                            }
                            for helper in read_json(root / HELPER_EVIDENCE_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "surveyed_head": "current-master-readback-2026-05-21",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "lane_scope": "shared helper-evidence rows only",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "bsearch"
                            else {
                                **helper,
                                "checker_surfaces": [
                                    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"
                                ],
                            }
                            for helper in read_json(root / HELPER_EVIDENCE_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "checksum"
                            else {
                                **helper,
                                "checker_surfaces": [
                                    "scripts/zigux/check-phase6-checksum-corpus-evidence.py"
                                ],
                            }
                            for helper in read_json(root / HELPER_EVIDENCE_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_EVIDENCE_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "hexdump"
                            else {
                                **helper,
                                "checker_surfaces": [
                                    "scripts/zigux/check-phase6-hexdump-packet.py"
                                ],
                            }
                            for helper in read_json(root / HELPER_EVIDENCE_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "surveyed_head": "current-master-readback-2026-05-21",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "lane_scope": "shared helper-parity rows only",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "shared_direct_evidence": [
                            item
                            for item in read_json(root / HELPER_PARITY_MANIFEST)[
                                "shared_direct_evidence"
                            ]
                            if item != "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "public_tree_backed_shared_companions": [
                            "Documentation/zigux/phase6-perf-gate-survey.md"
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "shared_follow_through_gaps": ["Documentation/zigux/phase6-helper-parity-catalog.md"],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "bsearch"
                            else {
                                **helper,
                                "checker_surfaces": ["scripts/zigux/check-phase6-bsearch-corpus-evidence.py"],
                            }
                            for helper in read_json(root / HELPER_PARITY_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "checksum"
                            else {
                                **helper,
                                "checker_surfaces": ["scripts/zigux/check-phase6-checksum-corpus-evidence.py"],
                            }
                            for helper in read_json(root / HELPER_PARITY_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "hexdump"
                            else {
                                **helper,
                                "checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"],
                            }
                            for helper in read_json(root / HELPER_PARITY_MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_CATALOG,
                read_text(root / HELPER_PARITY_CATALOG).replace(
                    "scripts/zigux/check-phase6-perf-threshold-markers.py",
                    "scripts/zigux/check-phase6-perf-threshold-route.py",
                    1,
                ),
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "coverage_verification_note": "coverage note drift",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        **read_json(root / HELPER_PARITY_MANIFEST),
                        "perf_evidence_readback_note": "perf evidence note drift",
                    },
                    indent=2,
                )
                + "\n",
            )
        )

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_VALIDATE_SELF_TEST=pass")
    print(f"PHASE6_VALIDATE_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.self_test:
            run_self_test()
            return 0
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_VALIDATE=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE6_VALIDATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())