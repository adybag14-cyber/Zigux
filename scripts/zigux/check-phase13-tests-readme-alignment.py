#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS_README = Path("zigux/tests/README.md")

PHASE13_HEADING = "Phase 13 review packet"
PHASE13_SECTION_END = "Tests-root reviewer prompt:"

REQUIRED_SHIPPED_MARKERS = (
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-release-coordination-matrix.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`Documentation/zigux/phase13-libfs-survey.md`",
    "`Documentation/zigux/phase13-devres-slice.md`",
    "`Documentation/zigux/phase13-devres-survey.md`",
    "`Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`",
    "`Documentation/zigux/phase13-devres-scatterlist-slice.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-survey.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`fs/libfs.zig`",
    "`zigux/tests/phase13_libfs.zig`",
    "`zigux/tests/phase13_libfs_reviewability.zig`",
    "`zigux/tests/phase13_libfs_manifest.json`",
    "`scripts/zigux/check-phase13-devres-dma-boundary.py`",
    "`scripts/zigux/check-phase13-devres-mmio-packet.py`",
    "`lib/devres.zig`",
    "`zigux/tests/phase13_devres_dma_coherent.zig`",
    "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`",
    "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`",
    "`lib/devres_scatterlist.zig`",
    "`zigux/tests/phase13_devres_scatterlist.zig`",
    "`zigux/tests/phase13_devres_scatterlist_build.zig`",
    "`security/landlock/ruleset.zig`",
    "`security/landlock/syscalls.zig`",
    "`zigux/tests/phase13_landlock_ruleset.zig`",
    "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "`drivers/tty/hvc/hvc_console.h`",
)

REQUIRED_GAP_MARKERS = (
    "`zigux/helpers/notifier_chain_view.zig`",
)

REQUIRED_TEXT = (
    "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with that stable handle as supporting shared reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.",
    "Current `master` instead materializes the narrower devres helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `lib/devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, so broader contributor wording should keep the direct DMA-boundary replay, the pure `dmam_alloc_coherent()` planning helper, and the scatterlist packet explicit instead of rebuilding the older missing `zigux/tests/phase13_devres.zig` replay family.",
    "Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `Documentation/zigux/phase13-landlock-syscalls-slice.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, and the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of treating Landlock as docs-only ownership metadata or as a fully returned syscall replay packet.",
    "Current `master` still does not materialize `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json`, so keep those validator-first, broader direct devres replay, missing direct Landlock syscall, and checker names framed as repo-reality gaps rather than shipped tests-root evidence.",
    "Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
    "Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
)

FORBIDDEN_SHIPPED_LINES = (
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
    "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "- `zigux/tests/phase13_landlock_syscalls.zig`",
    "- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
)

FORBIDDEN_TEXT = (
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands",
    "Current `master` still does not materialize `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json`, so keep those validator-first, broader devres, missing direct Landlock syscall, and checker names framed as repo-reality gaps rather than shipped tests-root evidence.",
    "Current `master` still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note framed as an adjacent repo-reality gap rather than as shipped tests-root evidence.",
    "Current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, or `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep those validator-first and checker names framed as repo-reality gaps rather than shipped tests-root evidence.",
    "Current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    "Current `master` also materializes the devres helper packet through `lib/devres.zig`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json`, so broader contributor wording should keep that direct boundary-evidence replay explicit beside the shared devres packet instead of treating it as a missing companion.",
    "Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, and the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of treating Landlock as docs-only ownership metadata.",
    "Keep `make -C zigux phase13-validate` explicit as the stable contributor-facing reminder handle for this shared packet even while the returned `zigux/Makefile` still lacks that shared build route, and keep blocked convenience route `make -C zigux phase13` framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
)

GAP_MARKER_SENTENCE = (
    "Keep `zigux/helpers/notifier_chain_view.zig` framed as an adjacent repo-reality gap rather than a shipped shared surface."
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, rel_path: Path) -> Path:
    return root / rel_path


def extract_phase13_shipped_section(text: str) -> str:
    heading_index = text.find(PHASE13_HEADING)
    if heading_index == -1:
        raise SystemExit(f"missing heading: {PHASE13_HEADING}")
    end_index = text.find(PHASE13_SECTION_END, heading_index)
    if end_index == -1:
        raise SystemExit(f"missing section terminator: {PHASE13_SECTION_END}")
    return text[heading_index:end_index]


def collect_missing_markers(text: str) -> list[str]:
    return [marker for marker in REQUIRED_SHIPPED_MARKERS if marker not in text]


def collect_missing_gap_markers(text: str) -> list[str]:
    return [marker for marker in REQUIRED_GAP_MARKERS if marker not in text]


def collect_missing_text(text: str) -> list[str]:
    return [fragment for fragment in REQUIRED_TEXT if fragment not in text]


def collect_forbidden_shipped_markers(text: str) -> list[str]:
    shipped_section = extract_phase13_shipped_section(text)
    return [line for line in FORBIDDEN_SHIPPED_LINES if line in shipped_section]


def collect_forbidden_text(text: str) -> list[str]:
    return [fragment for fragment in FORBIDDEN_TEXT if fragment in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    issues: list[tuple[str, str]] = []
    for marker in collect_missing_markers(tests_readme_text):
        issues.append(("MISSING_MARKER", marker))
    for marker in collect_missing_gap_markers(tests_readme_text):
        issues.append(("MISSING_GAP_MARKER", marker))
    for fragment in collect_missing_text(tests_readme_text):
        issues.append(("MISSING_TEXT", fragment))
    for marker in collect_forbidden_shipped_markers(tests_readme_text):
        issues.append(("FORBIDDEN_SHIPPED_MARKER", marker))
    for fragment in collect_forbidden_text(tests_readme_text):
        issues.append(("FORBIDDEN_TEXT", fragment))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE13_TESTS_README_ALIGNMENT=fail")
    print("PHASE13_TESTS_README_ALIGNMENT_ISSUES_START")
    for code, value in issues:
        print(f"{code}:{value}")
    print("PHASE13_TESTS_README_ALIGNMENT_ISSUES_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    section_lines = [
        "# zigux/tests",
        "",
        "## Phase 13 review packet",
        "",
        REQUIRED_TEXT[0],
        "",
        "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:",
    ]
    section_lines.extend(f"- {marker}" for marker in REQUIRED_SHIPPED_MARKERS)
    section_lines.append("")
    section_lines.extend(REQUIRED_TEXT[1:])
    section_lines.append("")
    section_lines.append(GAP_MARKER_SENTENCE)
    section_lines.append("")
    section_lines.append(PHASE13_SECTION_END)
    write_text(resolve_path(root, TESTS_README), "\n".join(section_lines) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 8
    with tempfile.TemporaryDirectory(prefix="zigux_p13_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = resolve_path(root, TESTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), "`zigux/helpers/notifier_chain_view.zig`"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (("MISSING_GAP_MARKER", "`zigux/helpers/notifier_chain_view.zig`")) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), REQUIRED_TEXT[1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (("MISSING_TEXT", REQUIRED_TEXT[1])) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), REQUIRED_TEXT[-1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (("MISSING_TEXT", REQUIRED_TEXT[-1])) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), REQUIRED_TEXT[0]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (("MISSING_TEXT", REQUIRED_TEXT[0])) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:\n",
                "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:\n- `zigux/helpers/notifier_chain_view.zig`\n",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (("FORBIDDEN_SHIPPED_MARKER", "- `zigux/helpers/notifier_chain_view.zig`")) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(
            path.read_text(encoding="utf-8") + "\n" + FORBIDDEN_TEXT[-1] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (("FORBIDDEN_TEXT", FORBIDDEN_TEXT[-1])) in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TESTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing tests readme did not abort")

    assert checks_run == expected_case_count
    print("PHASE13_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE13_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 13 tests-root reminder packet aligned with shared-helper repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE13_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE13_TESTS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_SHIPPED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())