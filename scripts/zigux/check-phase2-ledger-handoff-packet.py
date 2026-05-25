#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
BOOTSTRAP_LEDGER = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

PHASE2_CLOSURE_MARKERS = (
    "## Next Step",
    "The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
    "`PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again; if the shared backlog reopens first, start with one smallest truthfulness repair in Documentation/zigux/README.md, zigux/tests/README.md, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes`",
)

ARTIFACT_DIFF_MARKERS = (
    "## Current Phase 2 use",
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
)

SCRIPTS_README_MARKERS = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence",
)

TESTS_README_MARKERS = (
    "Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Does the bounded Phase 2 reminder keep the current direct-readback toolchain self-check, repo-local archive workflow, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, helper-local kconfig allconfig guard, kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

BOOTSTRAP_LEDGER_MARKERS = (
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/artifact-diff.md`",
    "- `scripts/zigux/README.md`",
    "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_CLOSURE)),
            PHASE2_CLOSURE_MARKERS,
            "MISSING_PHASE2_CLOSURE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, ARTIFACT_DIFF_NOTE)),
            ARTIFACT_DIFF_MARKERS,
            "MISSING_ARTIFACT_DIFF_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, SCRIPTS_README)),
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, BOOTSTRAP_LEDGER)),
            BOOTSTRAP_LEDGER_MARKERS,
            "MISSING_BOOTSTRAP_LEDGER_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_LEDGER_HANDOFF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, ARTIFACT_DIFF_NOTE), "\n".join(ARTIFACT_DIFF_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_LEDGER), "\n".join(BOOTSTRAP_LEDGER_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    marker_total = (
        len(PHASE2_CLOSURE_MARKERS)
        + len(ARTIFACT_DIFF_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(BOOTSTRAP_LEDGER_MARKERS)
    )
    expected_case_count = 1 + marker_total + 5
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_ledger_handoff_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for rel_path, markers, code in (
            (PHASE2_CLOSURE, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKERS"),
            (ARTIFACT_DIFF_NOTE, ARTIFACT_DIFF_MARKERS, "MISSING_ARTIFACT_DIFF_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (BOOTSTRAP_LEDGER, BOOTSTRAP_LEDGER_MARKERS, "MISSING_BOOTSTRAP_LEDGER_MARKERS"),
        ):
            for marker in markers:
                build_self_test_root(root)
                path = resolve_path(root, rel_path)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        for rel_path in (
            PHASE2_CLOSURE,
            ARTIFACT_DIFF_NOTE,
            SCRIPTS_README,
            TESTS_README,
            BOOTSTRAP_LEDGER,
        ):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_LEDGER_HANDOFF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_LEDGER_HANDOFF_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the live Phase 2 shared reminder packet aligned with the broadened ledger handoff."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for focused packet replays",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print(f"PHASE2_LEDGER_HANDOFF_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_LEDGER_HANDOFF_PACKET=pass")
    print(
        "PHASE2_LEDGER_HANDOFF_PACKET_MARKER_COUNT="
        f"{len(PHASE2_CLOSURE_MARKERS) + len(ARTIFACT_DIFF_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(BOOTSTRAP_LEDGER_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
