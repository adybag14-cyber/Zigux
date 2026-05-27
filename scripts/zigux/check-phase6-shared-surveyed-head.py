#!/usr/bin/env python3
"""Guard surveyed-head alignment across the shared Phase 6 helper packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
ENTRYPOINTS_CHECKER_PATH = Path("scripts/zigux/check-phase6-present-entrypoints.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase6.py")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_EVIDENCE_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
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
SELF_TEST_CASE_COUNT = 12


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return payload


def extract_catalog_surveyed_head(content: str) -> str:
    match = re.search(r"- surveyed head: `([^`]+)`", content)
    if match is None:
        raise ValidationError("phase6 helper-evidence catalog is missing its surveyed-head marker")
    return match.group(1)


def extract_python_surveyed_head(content: str, label: str) -> str:
    match = re.search(r'EXPECTED_SURVEYED_HEAD = "([^"]+)"', content)
    if match is None:
        raise ValidationError(f"{label} is missing EXPECTED_SURVEYED_HEAD")
    return match.group(1)


def require_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise ValidationError(f"{label} drifted: expected {expected!r}, got {actual!r}")


def require_list(label: str, actual: object, expected: list[str]) -> None:
    if actual != expected:
        raise ValidationError(f"{label} drifted")


def validate_repo(root: Path) -> str:
    catalog_text = read_text(root / CATALOG_PATH)
    evidence_manifest = read_json(root / EVIDENCE_MANIFEST_PATH)
    parity_manifest = read_json(root / PARITY_MANIFEST_PATH)
    entrypoints_checker = read_text(root / ENTRYPOINTS_CHECKER_PATH)
    validator = read_text(root / VALIDATOR_PATH)

    surveyed_head = extract_catalog_surveyed_head(catalog_text)
    require_equal("catalog surveyed head marker", surveyed_head, evidence_manifest.get("surveyed_head"))
    require_equal("catalog surveyed head marker", surveyed_head, parity_manifest.get("surveyed_head"))
    require_equal(
        "catalog surveyed head marker",
        surveyed_head,
        extract_python_surveyed_head(entrypoints_checker, ENTRYPOINTS_CHECKER_PATH.as_posix()),
    )
    require_equal(
        "catalog surveyed head marker",
        surveyed_head,
        extract_python_surveyed_head(validator, VALIDATOR_PATH.as_posix()),
    )

    require_equal("phase6 helper evidence packet", evidence_manifest.get("packet"), EXPECTED_PACKET)
    require_equal("phase6 helper parity packet", parity_manifest.get("packet"), EXPECTED_PARITY_PACKET)
    require_equal("phase6 helper evidence phase", evidence_manifest.get("phase"), EXPECTED_PHASE)
    require_equal("phase6 helper parity phase", parity_manifest.get("phase"), EXPECTED_PHASE)
    require_equal(
        "phase6 helper evidence lane scope",
        evidence_manifest.get("lane_scope"),
        EXPECTED_EVIDENCE_LANE_SCOPE,
    )
    require_equal(
        "phase6 helper parity lane scope",
        parity_manifest.get("lane_scope"),
        EXPECTED_PARITY_LANE_SCOPE,
    )
    require_list(
        "phase6 helper evidence companions",
        evidence_manifest.get("current_direct_readback_companions"),
        EXPECTED_DIRECT_COMPANIONS,
    )
    require_list(
        "phase6 helper evidence roadmap anchors",
        evidence_manifest.get("roadmap_anchors"),
        EXPECTED_ROADMAP_ANCHORS,
    )
    require_list(
        "phase6 helper parity shared direct evidence",
        parity_manifest.get("shared_direct_evidence"),
        EXPECTED_SHARED_DIRECT_EVIDENCE,
    )
    require_list(
        "phase6 helper parity roadmap anchors",
        parity_manifest.get("roadmap_anchors"),
        EXPECTED_ROADMAP_ANCHORS,
    )
    return surveyed_head


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path, *, surveyed_head: str = "current-master-readback-2026-05-27") -> None:
    catalog = f"""# Phase 6 Helper Evidence Catalog

- surveyed head: `{surveyed_head}`
"""
    evidence_manifest = {
        "packet": EXPECTED_PACKET,
        "phase": EXPECTED_PHASE,
        "surveyed_head": surveyed_head,
        "lane_scope": EXPECTED_EVIDENCE_LANE_SCOPE,
        "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS,
        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
    }
    parity_manifest = {
        "packet": EXPECTED_PARITY_PACKET,
        "phase": EXPECTED_PHASE,
        "surveyed_head": surveyed_head,
        "lane_scope": EXPECTED_PARITY_LANE_SCOPE,
        "shared_direct_evidence": EXPECTED_SHARED_DIRECT_EVIDENCE,
        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
    }
    python_body = f'EXPECTED_SURVEYED_HEAD = "{surveyed_head}"\n'

    write_text(root / CATALOG_PATH, catalog)
    write_text(root / EVIDENCE_MANIFEST_PATH, json.dumps(evidence_manifest, indent=2) + "\n")
    write_text(root / PARITY_MANIFEST_PATH, json.dumps(parity_manifest, indent=2) + "\n")
    write_text(root / ENTRYPOINTS_CHECKER_PATH, python_body)
    write_text(root / VALIDATOR_PATH, python_body)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase6-shared-surveyed-head-") as tempdir:
        root = Path(tempdir)

        build_sample_root(root)
        require_equal("aligned sample", validate_repo(root), "current-master-readback-2026-05-27")

        build_sample_root(root)
        write_text(root / PARITY_MANIFEST_PATH, json.dumps({
            "packet": EXPECTED_PARITY_PACKET,
            "phase": EXPECTED_PHASE,
            "surveyed_head": "current-master-readback-2026-05-22",
            "lane_scope": EXPECTED_PARITY_LANE_SCOPE,
            "shared_direct_evidence": EXPECTED_SHARED_DIRECT_EVIDENCE,
            "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
        }, indent=2) + "\n")
        try:
            validate_repo(root)
        except ValidationError as exc:
            if "catalog surveyed head marker" not in str(exc):
                raise
        else:
            raise AssertionError("expected parity surveyed-head mismatch to fail")

        build_sample_root(root)
        write_text(root / EVIDENCE_MANIFEST_PATH, json.dumps({
            "packet": EXPECTED_PACKET,
            "phase": EXPECTED_PHASE,
            "surveyed_head": "current-master-readback-2026-05-27",
            "lane_scope": EXPECTED_EVIDENCE_LANE_SCOPE,
            "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS[:-1],
            "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
        }, indent=2) + "\n")
        try:
            validate_repo(root)
        except ValidationError as exc:
            if "phase6 helper evidence companions" not in str(exc):
                raise
        else:
            raise AssertionError("expected companion drift to fail")

    print("PHASE6_SHARED_SURVEYED_HEAD_SELF_TEST=pass")
    print(f"PHASE6_SHARED_SURVEYED_HEAD_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    surveyed_head = validate_repo(args.repo_root.resolve())
    print("PHASE6_SHARED_SURVEYED_HEAD=pass")
    print(f"PHASE6_SHARED_SURVEYED_HEAD_MARKER={surveyed_head}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"PHASE6_SHARED_SURVEYED_HEAD=fail: {exc}")
        raise SystemExit(1)
