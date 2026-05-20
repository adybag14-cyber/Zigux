#!/usr/bin/env python3
"""Guard the current Phase 6 shared manifest-backed reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HELPER_EVIDENCE_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase6.py")

EXPECTED_EVIDENCE_PACKET = "phase6-helper-evidence"
EXPECTED_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_EVIDENCE_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
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
]
EXPECTED_PARITY_DIRECT_EVIDENCE = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]
EXPECTED_PUBLIC_TREE_COMPANIONS = [
    "Documentation/zigux/phase6-perf-gate-survey.md",
]
REQUIRED_EVIDENCE_CATALOG_SNIPPETS = [
    "Current public raw readback still helps recover `Documentation/zigux/phase6-perf-gate-survey.md`, so keep that broader perf note as public-tree-backed companion evidence rather than as direct authenticated shared-packet proof in this runtime.",
    "The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/phase6-helper-parity-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, and `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`.",
]
REQUIRED_PARITY_CATALOG_SNIPPETS = [
    "- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "- exact missing direct companions from authenticated 2026-05-20 readback: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- exact missing direct companions from authenticated 2026-05-20 readback: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- exact missing direct companions from authenticated 2026-05-20 readback: `Documentation/zigux/phase6-hexdump-slice.md` and `Documentation/zigux/phase6-hexdump-perf-refresh.md`",
    "Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile`.",
]
REQUIRED_VALIDATOR_SNIPPETS = [
    'HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")',
    'HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")',
    'run_checker(root, SHARED_SURFACE_CHECKER, "--repo-root")',
    'run_checker(root, PRESENT_ENTRYPOINTS_CHECKER, "--repo-root")',
]
SELF_TEST_CASE_COUNT = 11


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
            raise ValidationError(
                f"missing expected Phase 6 shared-surface marker in {path.as_posix()}: {snippet}"
            )


def validate(repo_root: Path) -> None:
    evidence = read_json(repo_root / HELPER_EVIDENCE_MANIFEST_PATH)
    parity = read_json(repo_root / HELPER_PARITY_MANIFEST_PATH)

    if evidence.get("packet") != EXPECTED_EVIDENCE_PACKET:
        raise ValidationError("phase6 helper-evidence packet drift")
    if parity.get("packet") != EXPECTED_PARITY_PACKET:
        raise ValidationError("phase6 helper-parity packet drift")
    if evidence.get("phase") != EXPECTED_PHASE or parity.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 phase drift")
    if evidence.get("current_direct_readback_companions") != EXPECTED_EVIDENCE_DIRECT_COMPANIONS:
        raise ValidationError("phase6 helper-evidence direct companion mismatch")
    if evidence.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_COMPANIONS:
        raise ValidationError("phase6 helper-evidence public companion mismatch")
    if parity.get("shared_direct_evidence") != EXPECTED_PARITY_DIRECT_EVIDENCE:
        raise ValidationError("phase6 helper-parity direct evidence mismatch")
    if parity.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_COMPANIONS:
        raise ValidationError("phase6 helper-parity public companion mismatch")

    require_snippets(repo_root / HELPER_EVIDENCE_CATALOG_PATH, REQUIRED_EVIDENCE_CATALOG_SNIPPETS)
    require_snippets(repo_root / HELPER_PARITY_CATALOG_PATH, REQUIRED_PARITY_CATALOG_SNIPPETS)
    require_snippets(repo_root / VALIDATOR_PATH, REQUIRED_VALIDATOR_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / HELPER_EVIDENCE_CATALOG_PATH, "\n".join(REQUIRED_EVIDENCE_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_PARITY_CATALOG_PATH, "\n".join(REQUIRED_PARITY_CATALOG_SNIPPETS) + "\n")
    write(
        root / HELPER_EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_EVIDENCE_PACKET,
                "phase": EXPECTED_PHASE,
                "current_direct_readback_companions": EXPECTED_EVIDENCE_DIRECT_COMPANIONS,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / HELPER_PARITY_MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PARITY_PACKET,
                "phase": EXPECTED_PHASE,
                "shared_direct_evidence": EXPECTED_PARITY_DIRECT_EVIDENCE,
                "public_tree_backed_shared_companions": EXPECTED_PUBLIC_TREE_COMPANIONS,
            },
            indent=2,
        )
        + "\n",
    )
    write(root / VALIDATOR_PATH, "\n".join(REQUIRED_VALIDATOR_SNIPPETS) + "\n")


def expect_failure(root: Path, path: Path, mutate) -> None:
    original = read_text(path)
    mutate(path)
    try:
        validate(root)
    except ValidationError:
        return
    finally:
        write(path, original)
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        def rewrite_json(path: Path, fn) -> None:
            data = json.loads(read_text(path))
            fn(data)
            write(path, json.dumps(data, indent=2) + "\n")

        expect_failure(root, root / HELPER_EVIDENCE_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_EVIDENCE_CATALOG_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_EVIDENCE_CATALOG_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[3] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("Documentation/zigux/phase6-helper-parity-catalog.md")))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("scripts/zigux/check-phase6-base64-bsearch-perf-markers.py")))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"public_tree_backed_shared_companions": []})))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["shared_direct_evidence"].remove("scripts/zigux/check-phase6-shared-surface.py")))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"packet": "phase6-helper-evidence"})))
        cases_run += 1
        expect_failure(root, root / VALIDATOR_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_VALIDATOR_SNIPPETS[2] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / VALIDATOR_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_VALIDATOR_SNIPPETS[3] + "\n", "", 1)))
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_SHARED_SURFACE_SELF_TEST=pass")
    print(f"PHASE6_SHARED_SURFACE_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_SHARED_SURFACE=fail: {exc}")
        return 1

    print("PHASE6_SHARED_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
