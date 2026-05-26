#!/usr/bin/env python3
"""Fail closed if the Phase 2 closure repo-reality-gap section drifts."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

SECTION_HEADING = "## Current Repo-Reality Gaps"
NEXT_HEADING = "## Closure Validation"
DOC_PATH = Path("Documentation/zigux/phase2-closure.md")

REQUIRED_MARKERS = (
    "Within the bounded Phase 2 closure packet, current `master` no longer leaves the local-first archive pair, returned archive-verification and staged-archive helper packet, installer hook, direct cross-route packet, returned closure-validator companions, primary artifact helper, fixdep checker packet, helper-local kconfig allconfig guard, or fixture-backed manifest guards in the repo-reality-gap bucket.",
    "keeps the helper-local kconfig allconfig guard explicit through `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/kconfig/conf_bridge.zig`, and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "keeps the artifact-support helper packet explicit through `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-fixdep-diff.py`, and `make -C zigux phase2-tools`",
    "keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`",
    "keeps the bounded genksyms closure evidence explicit through `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, the restored process-output fixture packet, the returned dash-prefixed long-option-arguments-as-data and dash-prefixed short-option-arguments-as-data expected-output fixtures, `zig test scripts/zigux/genksyms.zig`, and `make -C zigux phase2-genksyms`",
    "keeps same-lane follow-through tied to the toolchain, local-first archive, archive-verification, staged-archive helper, cross-route, kconfig, manifest-guard, helper-local allconfig guard, artifact-support, genksyms, make-wrapper, fixdep, and validator packet that the repo still ships directly.",
)

EXACT_ONCE_MARKERS = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-genksyms",
)

FORBIDDEN_MARKERS = (
    "still leaves the local-first archive pair",
    "still leaves the returned archive-verification and staged-archive helper packet",
    "keeps same-lane follow-through tied only to older validator-first claims",
)

SAMPLE_SECTION = """## Current Repo-Reality Gaps

Within the bounded Phase 2 closure packet, current `master` no longer leaves the local-first archive pair, returned archive-verification and staged-archive helper packet, installer hook, direct cross-route packet, returned closure-validator companions, primary artifact helper, fixdep checker packet, helper-local kconfig allconfig guard, or fixture-backed manifest guards in the repo-reality-gap bucket.

The current closure-side packet keeps the returned archive-verification and staged repo-local archive helper packet explicit through `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, `scripts/zigux/check-lane05-stage-helper-selftest.py`, `scripts/zigux/install-zig.py`, `third_party/README.md`, and `make -C zigux phase2-toolchain`, keeps the helper-local kconfig allconfig guard explicit through `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/kconfig/conf_bridge.zig`, and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, keeps the artifact-support helper packet explicit through `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-fixdep-diff.py`, and `make -C zigux phase2-tools`, keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`, keeps the bounded genksyms closure evidence explicit through `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, the restored process-output fixture packet, the returned dash-prefixed long-option-arguments-as-data and dash-prefixed short-option-arguments-as-data expected-output fixtures, `zig test scripts/zigux/genksyms.zig`, and `make -C zigux phase2-genksyms`, and keeps same-lane follow-through tied to the toolchain, local-first archive, archive-verification, staged-archive helper, cross-route, kconfig, manifest-guard, helper-local allconfig guard, artifact-support, genksyms, make-wrapper, fixdep, and validator packet that the repo still ships directly.
"""


@dataclass
class CheckResult:
    marker_count: int
    exact_count_marker_count: int
    forbidden_marker_count: int


def extract_section(text: str) -> str:
    start = text.find(SECTION_HEADING)
    if start < 0:
        raise ValueError(f"missing section heading: {SECTION_HEADING}")
    end = text.find(NEXT_HEADING, start)
    if end < 0:
        raise ValueError(f"missing next heading after {SECTION_HEADING}: {NEXT_HEADING}")
    return text[start:end].strip()


def check_section(section: str) -> CheckResult:
    errors: list[str] = []
    missing = [marker for marker in REQUIRED_MARKERS if marker not in section]
    if missing:
        errors.extend(f"missing required marker: {marker}" for marker in missing)

    duplicate_exact = [marker for marker in EXACT_ONCE_MARKERS if section.count(marker) != 1]
    if duplicate_exact:
        errors.extend(
            f"expected exactly one occurrence of marker: {marker}" for marker in duplicate_exact
        )

    present_forbidden = [marker for marker in FORBIDDEN_MARKERS if marker in section]
    if present_forbidden:
        errors.extend(f"found forbidden stale marker: {marker}" for marker in present_forbidden)

    if errors:
        raise ValueError("\n".join(errors))

    return CheckResult(
        marker_count=len(REQUIRED_MARKERS),
        exact_count_marker_count=len(EXACT_ONCE_MARKERS),
        forbidden_marker_count=len(FORBIDDEN_MARKERS),
    )


def read_doc(root: Path) -> str:
    return (root / DOC_PATH).read_text(encoding="utf-8")


def write_sample_root(root: Path) -> None:
    doc = root / DOC_PATH
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(
        "# Phase 2 Closure\n\n"
        + SAMPLE_SECTION
        + "\n\n"
        + "## Closure Validation\n\n"
        + "- placeholder\n",
        encoding="utf-8",
    )


def run_check(root: Path) -> CheckResult:
    section = extract_section(read_doc(root))
    return check_section(section)


def expect_failure(root: Path, needle: str) -> None:
    try:
        run_check(root)
    except ValueError as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected error containing {needle!r}, got: {exc}") from exc
        return
    raise AssertionError(f"expected failure containing {needle!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2-closure-repo-gaps-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        result = run_check(root)
        assert result.marker_count == len(REQUIRED_MARKERS)
        assert result.exact_count_marker_count == len(EXACT_ONCE_MARKERS)
        assert result.forbidden_marker_count == len(FORBIDDEN_MARKERS)
        case_count += 1

        text = read_doc(root)

        missing_heading_root = root / "missing_heading"
        write_sample_root(missing_heading_root)
        (missing_heading_root / DOC_PATH).write_text(
            read_doc(missing_heading_root).replace(SECTION_HEADING, "## Wrong Heading", 1),
            encoding="utf-8",
        )
        expect_failure(missing_heading_root, "missing section heading")
        case_count += 1

        missing_sentence_root = root / "missing_sentence"
        write_sample_root(missing_sentence_root)
        (missing_sentence_root / DOC_PATH).write_text(
            read_doc(missing_sentence_root).replace(REQUIRED_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        expect_failure(missing_sentence_root, "missing required marker")
        case_count += 1

        duplicate_route_root = root / "duplicate_route"
        write_sample_root(duplicate_route_root)
        duplicate_text = read_doc(duplicate_route_root).replace(
            "make -C zigux phase2-toolchain",
            "make -C zigux phase2-toolchain and again make -C zigux phase2-toolchain",
            1,
        )
        (duplicate_route_root / DOC_PATH).writeText if False else None
        (duplicate_route_root / DOC_PATH).write_text(duplicate_text, encoding="utf-8")
        expect_failure(duplicate_route_root, "expected exactly one occurrence")
        case_count += 1

        missing_kconfig_root = root / "missing_kconfig"
        write_sample_root(missing_kconfig_root)
        (missing_kconfig_root / DOC_PATH).write_text(
            read_doc(missing_kconfig_root).replace(REQUIRED_MARKERS[1], "", 1),
            encoding="utf-8",
        )
        expect_failure(missing_kconfig_root, "check-phase2-kconfig-allconfig-helper-packet")
        case_count += 1

        missing_artifact_root = root / "missing_artifact"
        write_sample_root(missing_artifact_root)
        (missing_artifact_root / DOC_PATH).write_text(
            read_doc(missing_artifact_root).replace(REQUIRED_MARKERS[2], "", 1),
            encoding="utf-8",
        )
        expect_failure(missing_artifact_root, "check-phase2-artifact-tools-manifest.py")
        case_count += 1

        missing_fixdep_root = root / "missing_fixdep"
        write_sample_root(missing_fixdep_root)
        (missing_fixdep_root / DOC_PATH).write_text(
            read_doc(missing_fixdep_root).replace(REQUIRED_MARKERS[3], "", 1),
            encoding="utf-8",
        )
        expect_failure(missing_fixdep_root, "check-phase2-fixdep-gate.py")
        case_count += 1

        missing_genksyms_root = root / "missing_genksyms"
        write_sample_root(missing_genksyms_root)
        (missing_genksyms_root / DOC_PATH).write_text(
            read_doc(missing_genksyms_root).replace(REQUIRED_MARKERS[4], "", 1),
            encoding="utf-8",
        )
        expect_failure(
            missing_genksyms_root, "genksyms_version_before_invalid_long_option_test.zig"
        )
        case_count += 1

        missing_followthrough_root = root / "missing_followthrough"
        write_sample_root(missing_followthrough_root)
        (missing_followthrough_root / DOC_PATH).write_text(
            read_doc(missing_followthrough_root).replace(REQUIRED_MARKERS[5], "", 1),
            encoding="utf-8",
        )
        expect_failure(missing_followthrough_root, "same-lane follow-through")
        case_count += 1

        forbidden_root = root / "forbidden"
        write_sample_root(forbidden_root)
        (forbidden_root / DOC_PATH).write_text(
            read_doc(forbidden_root).replace(
                REQUIRED_MARKERS[5],
                REQUIRED_MARKERS[5] + " still leaves the local-first archive pair",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(forbidden_root, "found forbidden stale marker")
        case_count += 1

        missing_next_heading_root = root / "missing_next_heading"
        write_sample_root(missing_next_heading_root)
        (missing_next_heading_root / DOC_PATH).write_text(
            read_doc(missing_next_heading_root).replace(NEXT_HEADING, "## Different Next", 1),
            encoding="utf-8",
        )
        expect_failure(missing_next_heading_root, "missing next heading")
        case_count += 1

        regenerated_root = root / "regenerated"
        write_sample_root(regenerated_root)
        rerun = run_check(regenerated_root)
        assert rerun.marker_count == len(REQUIRED_MARKERS)
        case_count += 1

        unchanged_root = root / "unchanged"
        write_sample_root(unchanged_root)
        (unchanged_root / DOC_PATH).write_text(text.replace("# Phase 2 Closure", "# Phase 2 Closure"), encoding="utf-8")
        assert run_check(unchanged_root).marker_count == len(REQUIRED_MARKERS)
        case_count += 1

    print("PHASE2_CLOSURE_REPO_REALITY_GAPS_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_REPO_REALITY_GAPS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail closed if the Phase 2 closure repo-reality-gap section drifts."
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a tiny passing sample root for focused local validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    result = run_check(args.root)
    print("PHASE2_CLOSURE_REPO_REALITY_GAPS=pass")
    print(f"PHASE2_CLOSURE_REPO_REALITY_GAPS_MARKER_COUNT={result.marker_count}")
    print(
        "PHASE2_CLOSURE_REPO_REALITY_GAPS_EXACT_COUNT_MARKER_COUNT="
        f"{result.exact_count_marker_count}"
    )
    print(
        "PHASE2_CLOSURE_REPO_REALITY_GAPS_FORBIDDEN_MARKER_COUNT="
        f"{result.forbidden_marker_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
