#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap workflow viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")
DOCS_SANITY_MARKER = "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`"

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/check-phase7-shared-control-gap.py"),
    Path("scripts/zigux/check-phase10-bootstrap-route.py"),
    Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    Path("scripts/zigux/check-phase11-build-inventory.py"),
    Path("scripts/zigux/check-phase11-matrix-gap-survey.py"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    Path("scripts/zigux/check-phase12-release-readiness-packet.py"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/phase12-release-readiness-survey.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/Makefile"),
    Path("zigux/tests/phase12_build.zig"),
    Path("zigux/tests/phase8_libbpf_segments_only_build.zig"),
    NOTE_REL,
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 reminder checks only`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    "- `PHASE1_WORKFLOW_REQUIRED_FILES=.github/workflows/zigux-bootstrap.yml,scripts/zigux/check-zig-toolchain.py,scripts/zigux/check-phase2-kconfig-selftest-alignment.py,scripts/zigux/check-phase2-kbuild-routes.py,scripts/zigux/check-phase2-tests-readme-alignment.py,scripts/zigux/check-phase2-cross-selftest-alignment.py,scripts/zigux/check-phase2-toolchain-pinning.py,scripts/zigux/check-phase2-toolchain-pin-scope.py,scripts/zigux/check-phase2-required-make-routes.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/check-phase1-workflow-viability.py,scripts/zigux/check-phase4-repo-reality-warning.py,scripts/zigux/check-phase4-reversible-delivery-pins.py,scripts/zigux/check-phase4-tests-readme-packet.py,scripts/zigux/check-phase7-shared-control-gap.py,scripts/zigux/check-phase10-bootstrap-route.py,scripts/zigux/check-phase11-hvc-cleanup-current-head.py,scripts/zigux/check-phase11-build-inventory.py,scripts/zigux/check-phase11-matrix-gap-survey.py,scripts/zigux/check-build-only-phase12-surface.py,scripts/zigux/check-phase12-release-readiness-packet.py,Documentation/zigux/README.md,Documentation/zigux/phase12-release-readiness-survey.md,zigux/tests/README.md,zigux/Makefile,zigux/tests/phase12_build.zig,zigux/tests/phase8_libbpf_segments_only_build.zig,Documentation/zigux/phase1-workflow-viability.md`",
    "- `PHASE1_WORKFLOW_NEIGHBOR_TOOLCHAIN_STEPS=Self-test current Zig toolchain checker,Check current Zig toolchain policy packet,Check current pinned Zig archive packet`",
    "- `PHASE1_WORKFLOW_NEIGHBOR_PHASE2_STEPS=Self-test current Phase 2 kconfig bridge checker,Check current Phase 2 kconfig bridge packet,Self-test current Phase 2 kbuild routes checker,Check current Phase 2 kbuild packet,Self-test current Phase 2 tests README checker,Check current Phase 2 tests README packet,Self-test current Phase 2 cross selftest alignment checker,Check current Phase 2 cross alignment packet,Self-test current Phase 2 toolchain pinning checker,Check current Phase 2 toolchain pinning packet,Self-test current Phase 2 toolchain pin-scope checker,Check current Phase 2 toolchain pin-scope packet,Self-test current Phase 2 required make-routes checker,Check current Phase 2 required make routes`",
    "- `PHASE1_WORKFLOW_SELFTEST_STEPS=Self-test current Phase 1 direct-owner checker,Self-test current Phase 1 string review checker,Self-test current Phase 1 bench checker,Self-test current Phase 1 shared reminder checker,Self-test current Phase 1 workflow viability checker`",
    "- `PHASE1_WORKFLOW_LIVE_STEPS=Check current Phase 1 direct-owner markers,Check current Phase 1 string review packet,Check current Phase 1 shared reminder packet,Check current Phase 1 workflow viability`",
    "- `PHASE1_WORKFLOW_POST_PHASE1_STEPS=Self-test current Phase 4 repo-reality warning checker,Check current Phase 4 repo-reality warning packet,Self-test current Phase 4 reversible-delivery pin checker,Check current Phase 4 reversible-delivery pin packet,Self-test current Phase 4 tests README checker,Check current Phase 4 tests README packet,Self-test current Phase 7 shared-control gap checker,Check current Phase 7 shared-control gap packet,Self-test current Phase 10 bootstrap route checker,Check current Phase 10 bootstrap route,Validate Phase 10 checker-backed review packet,Run Phase 10 helper tests,Self-test current Phase 11 HVC cleanup current-head checker,Check current Phase 11 HVC cleanup current-head packet,Self-test current Phase 11 build inventory checker,Check current Phase 11 build inventory packet,Self-test current Phase 11 matrix-gap survey checker,Check current Phase 11 matrix-gap survey packet,Self-test current Phase 12 build-only surface checker,Check current Phase 12 build-only surface,Self-test current Phase 12 release-readiness packet checker,Validate Phase 12 degraded-workflow bundle,Check current Phase 12 release-readiness packet,Run focused Phase 12 smoke shard,Run Phase 12 complex driver tests,Validate Phase 8 tooling gates,Run focused Phase 8 libbpf segment survey tests,Check current docs-root sanity markers`",
    "- `PHASE1_WORKFLOW_COMMAND_PACKET=python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test; python3 scripts/zigux/check-phase1-direct-owner-markers.py; python3 scripts/zigux/check-phase1-string-review-packet.py --self-test; python3 scripts/zigux/check-phase1-string-review-packet.py; python3 scripts/zigux/check-phase1-bench.py --self-test; python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test; python3 scripts/zigux/check-phase1-shared-reminder-packet.py; python3 scripts/zigux/check-phase1-workflow-viability.py --self-test; python3 scripts/zigux/check-phase1-workflow-viability.py`",
    "- current `master` workflow viability stays bounded to the shipped Phase 1 reminder packet, so treat `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` as broader closure-side or make-route packet members until fresh rereads recover them on current `master`.",
    "- keep the bench checker self-test-only in the bootstrap workflow until `zigux/tests/fixtures/phase1_bench_expectations.json` returns on current `master`; a live `python3 scripts/zigux/check-phase1-bench.py` workflow step is still a workflow-viability regression in this narrower packet.",
    "- keep the shipped `scripts/zigux/check-phase1-shared-reminder-packet.py` pair explicit beside the direct-owner, string-review, bench, and workflow-viability checks so this lane does not silently regress the already-landed Phase 1 reminder packet while the workflow shape keeps moving.",
    "- replay this packet on top of the current bootstrap workflow instead of reviving older neighbor names or dropping the newer ones; the active non-Phase-1 packet now keeps the Zig toolchain policy pair plus the pinned archive probe, the current full Phase 2 checker packet, the current Phase 11 HVC cleanup/build-inventory/matrix-gap packet, the current Phase 12 build-only plus release-readiness packet, and the focused Phase 8 tail explicit around the narrower Phase 1 reminder slice.",
    "- if this lane reopens, harden the same current workflow packet first instead of reconstructing the broader missing closure-side Phase 1 validator family from historical route names alone.",
)

WORKFLOW_STEPS = (
    ("Self-test current Zig toolchain checker", "python3 scripts/zigux/check-zig-toolchain.py --self-test"),
    ("Check current Zig toolchain policy packet", "python3 scripts/zigux/check-zig-toolchain.py --policy-only"),
    ("Check current pinned Zig archive packet", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"),
    ("Self-test current Phase 2 kconfig bridge checker", "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"),
    ("Check current Phase 2 kconfig bridge packet", "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    ("Self-test current Phase 2 kbuild routes checker", "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test"),
    ("Check current Phase 2 kbuild packet", "python3 scripts/zigux/check-phase2-kbuild-routes.py"),
    ("Self-test current Phase 2 tests README checker", "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test"),
    ("Check current Phase 2 tests README packet", "python3 scripts/zigux/check-phase2-tests-readme-alignment.py"),
    ("Self-test current Phase 2 cross selftest alignment checker", "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test"),
    ("Check current Phase 2 cross alignment packet", "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    ("Self-test current Phase 2 toolchain pinning checker", "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test"),
    ("Check current Phase 2 toolchain pinning packet", "python3 scripts/zigux/check-phase2-toolchain-pinning.py"),
    ("Self-test current Phase 2 toolchain pin-scope checker", "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test"),
    ("Check current Phase 2 toolchain pin-scope packet", "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    ("Self-test current Phase 2 required make-routes checker", "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test"),
    ("Check current Phase 2 required make routes", "python3 scripts/zigux/check-phase2-required-make-routes.py"),
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 workflow viability checker", "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test"),
    ("Check current Phase 1 workflow viability", "python3 scripts/zigux/check-phase1-workflow-viability.py"),
    ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
    ("Check current Phase 4 repo-reality warning packet", "python3 scripts/zigux/check-phase4-repo-reality-warning.py"),
    ("Self-test current Phase 4 reversible-delivery pin checker", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test"),
    ("Check current Phase 4 reversible-delivery pin packet", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    ("Self-test current Phase 4 tests README checker", "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test"),
    ("Check current Phase 4 tests README packet", "python3 scripts/zigux/check-phase4-tests-readme-packet.py"),
    ("Self-test current Phase 7 shared-control gap checker", "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test"),
    ("Check current Phase 7 shared-control gap packet", "python3 scripts/zigux/check-phase7-shared-control-gap.py"),
    ("Self-test current Phase 10 bootstrap route checker", "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test"),
    ("Check current Phase 10 bootstrap route", "python3 scripts/zigux/check-phase10-bootstrap-route.py"),
    ("Validate Phase 10 checker-backed review packet", "make -C zigux phase10-validate"),
    ("Run Phase 10 helper tests", "make -C zigux phase10-test"),
    ("Self-test current Phase 11 HVC cleanup current-head checker", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"),
    ("Check current Phase 11 HVC cleanup current-head packet", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    ("Self-test current Phase 11 build inventory checker", "python3 scripts/zigux/check-phase11-build-inventory.py --self-test"),
    ("Check current Phase 11 build inventory packet", "python3 scripts/zigux/check-phase11-build-inventory.py"),
    ("Self-test current Phase 11 matrix-gap survey checker", "python3 scripts/zigux/check-phase11-matrix-gap-survey.py --self-test"),
    ("Check current Phase 11 matrix-gap survey packet", "python3 scripts/zigux/check-phase11-matrix-gap-survey.py"),
    ("Self-test current Phase 12 build-only surface checker", "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test"),
    ("Check current Phase 12 build-only surface", "python3 scripts/zigux/check-build-only-phase12-surface.py"),
    ("Self-test current Phase 12 release-readiness packet checker", "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test"),
    ("Validate Phase 12 degraded-workflow bundle", "make -C zigux phase12-validate"),
    ("Check current Phase 12 release-readiness packet", "python3 scripts/zigux/check-phase12-release-readiness-packet.py"),
    ("Run focused Phase 12 smoke shard", "make -C zigux phase12-smoke"),
    ("Run Phase 12 complex driver tests", "zig build test --build-file zigux/tests/phase12_build.zig --summary all"),
    ("Validate Phase 8 tooling gates", "make -C zigux phase8-validate"),
    ("Run focused Phase 8 libbpf segment survey tests", "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all"),
)

FORBIDDEN_SNIPPETS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "scripts/zigux/check-kconfig-bridge.py --self-test",
)

FORBIDDEN_LINES = (
    "        run: python3 scripts/zigux/check-phase1-bench.py",
    "        run: make -C zigux phase1",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def collect_failures(root: Path) -> list[str]:
    failures = []
    for rel in REQUIRED_FILE_RELS:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    workflow_text = read_text(root / WORKFLOW_REL)
    note_text = read_text(root / NOTE_REL)

    for line in REQUIRED_NOTE_LINES:
        count = count_exact_line(note_text, line)
        if count != 1:
            failures.append(f"note:expected=1:actual={count}:{line}")

    for name, run in WORKFLOW_STEPS:
        name_line = f"      - name: {name}"
        run_line = f"        run: {run}"
        count_name = count_exact_line(workflow_text, name_line)
        count_run = count_exact_line(workflow_text, run_line)
        if count_name != 1:
            failures.append(f"workflow:name:expected=1:actual={count_name}:{name}")
        if count_run != 1:
            failures.append(f"workflow:run:expected=1:actual={count_run}:{run}")

    if count_exact_line(workflow_text, "      - name: Check current docs-root sanity markers") != 1:
        failures.append("workflow:docs-sanity-name")
    if DOCS_SANITY_MARKER not in workflow_text:
        failures.append("workflow:docs-sanity-marker")

    positions = []
    for name, _ in WORKFLOW_STEPS:
        pos = workflow_text.find(f"- name: {name}")
        if pos == -1:
            failures.append(f"workflow:missing-order-step:{name}")
            return failures
        positions.append(pos)
    if positions != sorted(positions):
        failures.append("workflow:out-of-order")

    for needle in FORBIDDEN_SNIPPETS:
        if needle in workflow_text:
            failures.append(f"workflow:forbidden:{needle}")
    for line in FORBIDDEN_LINES:
        if count_exact_line(workflow_text, line):
            failures.append(f"workflow:forbidden-line:{line}")
    return failures


def write_file(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_workflow() -> str:
    lines = ["name: zigux-bootstrap", "", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:"]
    for name, run in WORKFLOW_STEPS:
        lines.append(f"      - name: {name}")
        lines.append(f"        run: {run}")
        lines.append("")
    lines.extend([
        "      - name: Check current docs-root sanity markers",
        "        run: |",
        "          python3 - <<'PY2'",
        f"          print('{DOCS_SANITY_MARKER}')",
        "          PY2",
        "",
    ])
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, sample_workflow())
    write_file(root, NOTE_REL, "# Phase 1 Workflow Viability\n\n" + "\n".join(REQUIRED_NOTE_LINES) + "\n")
    for rel in REQUIRED_FILE_RELS[1:-1]:
        write_file(root, rel, "# placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-") as tmp:
        root = Path(tmp)
        build_sample_repo(root)
        if collect_failures(root):
            print("self-test:base")
            return 1
        case_count += 1

        build_sample_repo(root)
        (root / "scripts/zigux/check-phase11-build-inventory.py").unlink()
        if "missing_file:scripts/zigux/check-phase11-build-inventory.py" not in collect_failures(root):
            print("self-test:missing-phase11-file")
            return 1
        case_count += 1

        build_sample_repo(root)
        path = root / WORKFLOW_REL
        text = read_text(path).replace("      - name: Check current pinned Zig archive packet\n", "", 1)
        path.write_text(text, encoding="utf-8")
        if not any(item.startswith("workflow:name:expected=1:actual=0:Check current pinned Zig archive packet") for item in collect_failures(root)):
            print("self-test:missing-archive-step")
            return 1
        case_count += 1

        build_sample_repo(root)
        path = root / WORKFLOW_REL
        text = read_text(path).replace("      - name: Self-test current Phase 2 required make-routes checker\n", "", 1)
        path.write_text(text, encoding="utf-8")
        if not any(item.startswith("workflow:name:expected=1:actual=0:Self-test current Phase 2 required make-routes checker") for item in collect_failures(root)):
            print("self-test:missing-required-make-routes-step")
            return 1
        case_count += 1

        build_sample_repo(root)
        (root / "scripts/zigux/check-phase2-toolchain-pin-scope.py").unlink()
        if "missing_file:scripts/zigux/check-phase2-toolchain-pin-scope.py" not in collect_failures(root):
            print("self-test:missing-phase2-pin-scope-file")
            return 1
        case_count += 1

        build_sample_repo(root)
        path = root / WORKFLOW_REL
        text = read_text(path).replace("      - name: Check current Phase 1 shared reminder packet\n", "", 1)
        path.write_text(text, encoding="utf-8")
        if not any(item.startswith("workflow:name:expected=1:actual=0:Check current Phase 1 shared reminder packet") for item in collect_failures(root)):
            print("self-test:missing-phase1-step")
            return 1
        case_count += 1

        build_sample_repo(root)
        path = root / WORKFLOW_REL
        path.write_text(read_text(path).replace(DOCS_SANITY_MARKER, "missing", 1), encoding="utf-8")
        if "workflow:docs-sanity-marker" not in collect_failures(root):
            print("self-test:missing-docs-sanity")
            return 1
        case_count += 1

        build_sample_repo(root)
        path = root / WORKFLOW_REL
        path.write_text(read_text(path) + "      - name: Old route\n        run: python3 scripts/zigux/validate-phase1.py\n", encoding="utf-8")
        if "workflow:forbidden:scripts/zigux/validate-phase1.py" not in collect_failures(root):
            print("self-test:forbidden-phase1")
            return 1
        case_count += 1

        build_sample_repo(root)
        path = root / WORKFLOW_REL
        path.write_text(read_text(path) + "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n", encoding="utf-8")
        if "workflow:forbidden-line:        run: python3 scripts/zigux/check-phase1-bench.py" not in collect_failures(root):
            print("self-test:forbidden-live-bench")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT.resolve()
    failures = collect_failures(root)
    if failures:
        for item in failures:
            print(item)
        return 1
    print("phase1-workflow-viability:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
