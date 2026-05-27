#!/usr/bin/env python3
"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "scripts/zigux/check-phase1-find-bit-review-packet.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/Makefile",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks",
        "`python3 scripts/zigux/check-phase1-bench.py --self-test`",
        "`zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
        "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
        "For `tools/lib/bitmap.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass. The shipped direct anchors already cover whole-word range edges, raw copy and tail-clearing behavior, zero and aligned `copyAndExtend()` handling, zero-sized destination-view no-op behavior, exact-word-boundary equality masking, out-of-range tail masking for predicates and weights, caller-window `xor` and `or` clamping including multiword tails, complement tail clamping, cross-word `scnprintf()` merging, empty-bitmap caller-buffer preservation, Linux-style alias mirrors, and allocator optional-reset coverage.",
        "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.",
        "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.",
    ),
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md": (
        "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    ),
    "Documentation/zigux/review-checklist.md": (
        "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
        "keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
        "there is no standalone `samples/zigux/*bitmap*` reference sample, direct bitmap helper reviewability remains under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `Documentation/zigux/phase4-reversible-delivery-evidence.md`, the partial separate runtime bitmap reminder packet stays explicit in `samples/zigux/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and `zigux/tests/phase9_build.zig` while `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` stay repo-reality gaps on the trusted contents path, keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned or extra Phase 5 evidence landed",
    ),
    "scripts/zigux/README.md": (
        "current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
        "`Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`",
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "`scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
        "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks",
        "`zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
    ),
    "scripts/zigux/check-phase1-bench.py": (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def run_self_test() -> None:",
    ),
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py": (
        'description="Validate the Phase 1 direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string."',
        'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")',
        'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")',
    ),
    "scripts/zigux/check-phase1-direct-owner-markers.py": (
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        'print("PHASE1_DIRECT_OWNER_MARKERS=pass")',
    ),
    "scripts/zigux/check-phase1-find-bit-bench-anchors.py": (
        'description="Validate that the live find_bit helper still carries the current bench-adjacent edge anchors, including the landed andnot, clump-forward-skip, and tail-word next-skip paths."',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")',
    ),
    "scripts/zigux/check-phase1-find-bit-review-packet.py": (
        '"""Guard the Phase 1 find_bit review packet against helper, fixture, smoke, and lane drift."""',
        'print("phase1-find-bit-review-packet:ok")',
    ),
    "scripts/zigux/check-phase1-route-summary-counts.py": (
        '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
    ),
    "scripts/zigux/check-phase1-shared-reminder-packet.py": (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    "scripts/zigux/check-phase1-string-review-packet.py": (
        "EXPECTED_STRING_SOURCE_SYMBOLS = [",
        "EXPECTED_HELPER_TEST_ANCHORS = [",
        'print("phase1-string-review-packet:ok")',
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        "PHASE1_CLOSURE_VALIDATION=pass",
        "PHASE1_CLOSURE_SELF_TEST=pass",
    ),
    "zigux/tests/README.md": (
        "current direct-readback Phase 1 reminder packet:",
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
    "zigux/tests/build.zig": (
        'root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        "const slab_module = b.createModule(.{",
        "const str_error_r_module = b.createModule(.{",
        "const vsprintf_module = b.createModule(.{",
        "const zalloc_module = b.createModule(.{",
        'root_module.addImport("slab", slab_module);',
        'root_module.addImport("str_error_r", str_error_r_module);',
        'root_module.addImport("vsprintf", vsprintf_module);',
        'root_module.addImport("zalloc", zalloc_module);',
        '.name = "phase1-host-tools-smoke",',
    ),
    "zigux/tests/phase1_helpers.zig": (
        'test "phase 1 helper ports match committed parity fixture" {',
    ),
    "zigux/tests/phase1_helpers_build.zig": (
        '.name = "phase1-helpers",',
        'root_source_file = b.path("phase1_helpers.zig"),',
    ),
    "zigux/tests/fixtures/phase1_helper_manifest.json": (
        '"lane_sequencing": {',
        '"direct_anchor_followup_helpers": [',
        '"rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master."',
    ),
    "zigux/Makefile": (
        "phase1-route-summary:",
        "phase2-toolchain:",
        "phase2-tools:",
        "phase2-kconfig:",
        "phase2-cross:",
        "phase2-genksyms:",
        "phase3-validate:",
        "phase4-validate:",
        "phase6-validate:",
        "phase8-validate:",
        "phase10-validate:",
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
        "phase14-validate:",
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'const argv_split = @import("argv_split");',
        'const slab = @import("slab");',
        'const str_error_r = @import("str_error_r");',
        'const vsprintf = @import("vsprintf");',
        'const zalloc = @import("zalloc");',
        'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
        'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
        'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
        'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
        'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
    ),
}

FORBIDDEN_FRAGMENTS = (
    "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`",
    "python3 scripts/zigux/check-phase1-parity.py --self-test",
    "python3 scripts/zigux/check-phase1-parity.py",
    "python3 scripts/zigux/validate-phase1.py --self-test",
    "python3 scripts/zigux/validate-phase1.py",
    "repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "`zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.",
    "C-string list lookup anchors through `matchString()` and `match_string()`, counted-search anchors through `strpbrk()`, `strcspn()`, `strnchr()`, `strnchrNul()` or `strnchrnul()`, and `strspn()`",
    "keep `zigux/Makefile` explicit as current repo evidence for the returned non-Phase-1 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
    "keep `zigux/Makefile` explicit as current repo evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
    "`zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_stripped_line_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str) -> list[str]:
    issues: list[str] = []
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"{label}:forbidden:{fragment}:actual={count}")
    return issues


def collect_missing_markers(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            issues.extend(collect_stripped_line_markers(text, relative_path, markers))
        else:
            issues.extend(collect_exact_markers(text, relative_path, markers))
        issues.extend(collect_forbidden_fragments(text, relative_path))
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == "scripts/zigux/check-phase1-shared-reminder-packet.py":
            write_text(root, relative_path, __file__ + "\n")
            continue
        markers = MARKERS.get(relative_path, ())
        write_text(root, relative_path, "\n".join(markers) + ("\n" if markers else ""))
    write_text(
        root,
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "\n".join(MARKERS["scripts/zigux/check-phase1-shared-reminder-packet.py"]) + "\n",
    )


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-shared-reminder-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_missing_markers(root)
        if issues:
            print("self-test:success:unexpected_failures")
            for item in issues:
                print(item)
            return 1

    def make_missing_file_case(relative_path: str):
        return (
            f"missing_file_{relative_path.replace('/', '_').replace('.', '_')}",
            lambda root, relative_path=relative_path: (root / relative_path).unlink(),
        )

    def make_marker_case(relative_path: str, marker: str, mutation: str):
        mutator = mutate_remove_marker if mutation == "remove" else mutate_duplicate_marker
        return (
            f"{mutation}_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(marker))}",
            lambda root, relative_path=relative_path, marker=marker, mutator=mutator: mutator(
                root, relative_path, marker
            ),
        )

    def make_forbidden_fragment_case(relative_path: str, fragment: str):
        return (
            f"forbidden_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(fragment))}",
            lambda root, relative_path=relative_path, fragment=fragment: mutate_append_fragment(
                root, relative_path, fragment
            ),
        )

    cases: list[tuple[str, object]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append(make_missing_file_case(relative_path))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append(make_marker_case(relative_path, marker, "remove"))
            cases.append(make_marker_case(relative_path, marker, "duplicate"))
    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append(make_forbidden_fragment_case("Documentation/zigux/README.md", fragment))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-reminder-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_missing_markers(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for item in issues:
                        print(item)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REMINDER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        "--root",
        dest="repo_root",
        help="override the repository root used for checks",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the guard against synthetic positive and negative cases",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.repo_root)
    issues = collect_missing_markers(root)
    if issues:
        for item in issues:
            print(item)
        return 1

    print("PHASE1_SHARED_REMINDER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())