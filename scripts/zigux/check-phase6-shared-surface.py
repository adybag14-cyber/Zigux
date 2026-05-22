#!/usr/bin/env python3
"""Guard the current Phase 6 shared manifest-backed reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
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
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_PARITY_DIRECT_EVIDENCE = [
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
]
EXPECTED_PUBLIC_TREE_COMPANIONS = []
EXPECTED_EVIDENCE_CURRENT_GAPS = [
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
]
REQUIRED_DOCS_README_SNIPPETS = [
    "Phase 6 notes - `Documentation/zigux/phase6-helper-evidence-catalog.md` - `Documentation/zigux/phase6-helper-parity-catalog.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `zigux/tests/phase6_build.zig` - `zigux/tests/phase6_helper_evidence_manifest.json` - `zigux/tests/phase6_helper_parity_manifest.json` - `scripts/zigux/check-phase6-shared-surface.py` - `scripts/zigux/check-phase6-present-entrypoints.py` - `zigux/Makefile` keep the bounded Phase 6 docs-root packet explicit through the shared helper-evidence and helper-parity catalogs, the current scripts-root and tests-root reminders, the shared build foothold, the shared machine-readable manifests, the present-entrypoint guard, and the returned Makefile wrapper surface instead of leaving the active leaf-helper tranche implicit from neighboring reminder surfaces alone.",
    "authenticated current-master rereads now directly recover both `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so keep both note surfaces inside the current docs-root evidence packet beside the shared manifests instead of framing the broader perf-note surface as public-tree-backed companion evidence.",
    "`python3 scripts/zigux/check-phase6-shared-surface.py --self-test`, `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test`, `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-perf` replay the bounded current Phase 6 reminder packet without widening it into missing parity companions or helper-local implementation follow-through.",
]
REQUIRED_SCRIPTS_README_SNIPPETS = [
    "- repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase6-perf-gate-survey.md`, but authenticated current-master rereads now directly recover `Documentation/zigux/phase6-helper-parity-catalog.md`, so keep the helper-parity catalog inside the current directly readable shared packet and treat the broader perf reminder path as current public-tree-backed companion evidence rather than as direct scripts-root proof",
    "- the shared replay inventory now treats `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-base64-perf`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-bsearch-perf`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-checksum-perf` as committed rerun routes beside the existing hexdump reminders, so keep those wrappers out of the older inventory-only bucket",
]
REQUIRED_EVIDENCE_CATALOG_SNIPPETS = [
    "Authenticated current-master rereads now directly recover `Documentation/zigux/phase6-perf-gate-survey.md`, and that broader perf note is now aligned again on the currently readable base64, bsearch, checksum, and hexdump measurement packet.",
    "Treat the remaining paths above as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again. The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`, `scripts/zigux/check-phase6-hexdump-packet.py`, and `scripts/zigux/check-phase6-hexdump-route.py`.",
]
REQUIRED_PARITY_CATALOG_SNIPPETS = [
    "- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "- exact missing direct companions from authenticated 2026-05-20 readback: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note, so the checksum row now ships the same external parity review hook as the other portability-sensitive Phase 6 helpers without reopening hexdump work",
    "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, perf-matrix preflight, fixture surface, checker, slice note, and perf-refresh rationale note",
    "Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.",
    "Authenticated follow-up readback on 2026-05-21 directly recovered `Documentation/zigux/phase6-perf-gate-survey.md` again, so broader reminder surfaces can keep that survey inside the directly readable shared packet instead of treating it as fallback-only evidence.",
]
REQUIRED_VALIDATOR_SNIPPETS = [
    'HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")',
    'HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")',
    'run_checker(root, SHARED_SURFACE_CHECKER, "--repo-root")',
    'run_checker(root, PRESENT_ENTRYPOINTS_CHECKER, "--repo-root")',
]
REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS = [
    "Authenticated GitHub contents readback on 2026-05-20 reconfirmed direct access to Documentation/zigux/phase6-helper-evidence-catalog.md, Documentation/zigux/phase6-helper-parity-catalog.md, Documentation/zigux/phase6-hexdump-slice.md, Documentation/zigux/phase6-hexdump-perf-refresh.md, scripts/zigux/check-phase6-shared-surface.py, scripts/zigux/validate-phase6.py, and zigux/tests/phase6_build.zig.",
    "A follow-up authenticated current-master readback on 2026-05-21 also directly recovered Documentation/zigux/phase6-perf-gate-survey.md, zigux/tests/phase6_helper_parity_manifest.json, and zigux/tests/phase6_helper_evidence_manifest.json.",
    "The remaining direct-readback gaps still returning 404 were zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig, zigux/tests/phase6_base64_c_parity.zig, zigux/tests/phase6_base64_c_casegen.zig, zigux/tests/fixtures/phase6_base64_c_harness.c, and scripts/zigux/check-phase6-base64-c-parity.py.",
]
REQUIRED_PARITY_PERF_NOTE_SNIPPETS = [
    "Verified the current Phase 6 perf packet on 2026-05-20 from direct current-master readback of zigux/tests/phase6_base64_perf.zig, zigux/tests/fixtures/phase6_base64_vectors.zig, zigux/tests/phase6_bsearch.zig, zigux/tests/phase6_bsearch_perf.zig, zigux/tests/phase6_bsearch_lower_bound_c_abi.zig, zigux/tests/phase6_bsearch_c_abi_budget.zig, zigux/tests/fixtures/phase6_bsearch_vectors.zig, zigux/tests/phase6_checksum_perf.zig, zigux/tests/fixtures/phase6_checksum_vectors.zig, zigux/tests/phase6_hexdump_perf.zig, zigux/tests/phase6_hexdump_perf_matrix.zig, zigux/tests/fixtures/phase6_hexdump_vectors.zig, Documentation/zigux/phase6-hexdump-slice.md, Documentation/zigux/phase6-hexdump-perf-refresh.md, zigux/tests/phase6_build.zig, and zigux/Makefile.",
]
EXPECTED_PARITY_FOLLOW_THROUGH_GAPS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
]
SELF_TEST_CASE_COUNT = 27


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


def require_text_snippets(name: str, content: object, snippets: list[str]) -> None:
    if not isinstance(content, str):
        raise ValidationError(f"{name} missing")
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"{name} drifted: {snippet}")


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
    if evidence.get("current_repo_reality_gaps") != EXPECTED_EVIDENCE_CURRENT_GAPS:
        raise ValidationError("phase6 helper-evidence repo-reality gaps mismatch")
    if parity.get("shared_direct_evidence") != EXPECTED_PARITY_DIRECT_EVIDENCE:
        raise ValidationError("phase6 helper-parity direct evidence mismatch")
    if parity.get("public_tree_backed_shared_companions") != EXPECTED_PUBLIC_TREE_COMPANIONS:
        raise ValidationError("phase6 helper-parity public companion mismatch")
    if parity.get("shared_follow_through_gaps") != EXPECTED_PARITY_FOLLOW_THROUGH_GAPS:
        raise ValidationError("phase6 helper-parity follow-through gaps drift")

    require_snippets(repo_root / DOCS_README_PATH, REQUIRED_DOCS_README_SNIPPETS)
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_CATALOG_PATH, REQUIRED_EVIDENCE_CATALOG_SNIPPETS)
    require_snippets(repo_root / HELPER_PARITY_CATALOG_PATH, REQUIRED_PARITY_CATALOG_SNIPPETS)
    require_snippets(repo_root / VALIDATOR_PATH, REQUIRED_VALIDATOR_SNIPPETS)
    require_text_snippets(
        "phase6 helper-parity coverage_verification_note",
        parity.get("coverage_verification_note"),
        REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS,
    )
    require_text_snippets(
        "phase6 helper-parity perf_evidence_readback_note",
        parity.get("perf_evidence_readback_note"),
        REQUIRED_PARITY_PERF_NOTE_SNIPPETS,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / DOCS_README_PATH, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n")
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
                "current_repo_reality_gaps": EXPECTED_EVIDENCE_CURRENT_GAPS,
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
                "coverage_verification_note": " ".join(REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS),
                "perf_evidence_readback_note": " ".join(REQUIRED_PARITY_PERF_NOTE_SNIPPETS),
                "shared_follow_through_gaps": EXPECTED_PARITY_FOLLOW_THROUGH_GAPS,
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

        expect_failure(root, root / DOCS_README_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_DOCS_README_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / DOCS_README_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_DOCS_README_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / DOCS_README_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_DOCS_README_SNIPPETS[2] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / SCRIPTS_README_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_SCRIPTS_README_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / SCRIPTS_README_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_SCRIPTS_README_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_EVIDENCE_CATALOG_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_EVIDENCE_CATALOG_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[1] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[2] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[3] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[4] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_CATALOG_PATH, lambda path: write(path, read_text(path).replace(REQUIRED_PARITY_CATALOG_SNIPPETS[5] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"packet": "phase6-helper-parity"})))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"phase": "Phase 5"})))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("Documentation/zigux/phase6-helper-parity-catalog.md")))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("Documentation/zigux/phase6-perf-gate-survey.md")))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_direct_readback_companions"].remove("scripts/zigux/check-phase6-base64-bsearch-perf-markers.py")))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"public_tree_backed_shared_companions": ["Documentation/zigux/phase6-perf-gate-survey.md"]})))
        cases_run += 1
        expect_failure(root, root / HELPER_EVIDENCE_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["current_repo_reality_gaps"].remove("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data["shared_direct_evidence"].remove("scripts/zigux/check-phase6-shared-surface.py")))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"packet": "phase6-helper-evidence"})))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"public_tree_backed_shared_companions": ["Documentation/zigux/phase6-perf-gate-survey.md"]})))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"shared_follow_through_gaps": ["Documentation/zigux/phase6-helper-parity-catalog.md"]})))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"coverage_verification_note": "coverage drift"})))
        cases_run += 1
        expect_failure(root, root / HELPER_PARITY_MANIFEST_PATH, lambda path: rewrite_json(path, lambda data: data.update({"perf_evidence_readback_note": "perf drift"})))
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
