#!/usr/bin/env python3
"""Validate the current-master-safe Phase 1 closure note against the live helper manifest."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BUILD_FILE_REL = Path("zigux/tests/build.zig")
SMOKE_FILE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

REQUIRED_NOTE_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=partial`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "manifest": "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "current_packet": "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "shared_sync_complete": "`PHASE1_SHARED_REMINDER_SYNC_STATE=complete`",
    "gap_packet": "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,scripts/zigux/check-phase1-bench.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
    "validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "next_step": "`PHASE1_NEXT_SAFE_STEP=refresh draft PR 364 summary so it matches the synced Phase 1 reminder packet before widening into zigux/tests/phase1_helpers.zig or bench claims`",
}

REQUIRED_BUILD_MARKERS = {
    "step_binding": 'const phase1_step = b.step(',
    "step_description": '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
    "root_source": '"phase1_host_tools_smoke.zig"',
}

REQUIRED_SMOKE_MARKERS = {
    "argv_split_decl": '@hasDecl(argv_split, "argvSplit")',
    "cmdline_decl": '@hasDecl(cmdline, "memparse")',
    "find_bit_decl": '@hasDecl(find_bit, "findFirstBit")',
    "bitmap_decl": '@hasDecl(bitmap, "setRange")',
}

REQUIRED_SCRIPTS_README_MARKERS = {
    "phase1_flow": "the restored closure note, the live owner-map and string-review guards, the narrow closure validator, and the shared tests-root smoke anchor",
    "validator_presence": "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner marker, and current-master-safe closure packet explicit from the scripts root",
    "companion_surfaces": "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet",
    "gap_list": "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "narrow_route": "`python3 scripts/zigux/validate-phase1-closure.py` and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` now replay the narrow closure-side validation route that current `master` honestly supports without claiming the older parity, bench, or Makefile wrappers have returned",
}

REQUIRED_DOCS_README_MARKERS = {
    "phase1_notes": "- `scripts/zigux/validate-phase1-closure.py` keep the closure note, the live owner map, the narrow closure validator, the shared host-tools smoke route, and the parked shared-replay-versus-direct-anchor split explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "gap_list": "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
    "closure_route": "the current docs-root Phase 1 reminder packet now keeps `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` explicit beside the live owner-map and string-review guards so the shared reminder packet stays aligned around the same current-master-safe closure route.",
}

REQUIRED_REVIEW_CHECKLIST_MARKERS = {
    "phase1_packet": "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "phase1_gaps": "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
    "phase1_validation": "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/validate-phase1-closure.py` replay the bounded live reminder checks",
}

REQUIRED_TESTS_README_MARKERS = {
    "phase1_packet": "current direct-readback Phase 1 reminder packet: `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/validate-phase1-closure.py`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "gap_list": "repo-reality warning for the broader Phase 1 closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "closure_route": "the restored closure note plus `python3 scripts/zigux/validate-phase1-closure.py` and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` now keep the current closure-side validation route explicit in the tests root instead of leaving that narrower packet implied through docs-root wording alone",
}

FORBIDDEN_DOCS_README_MARKERS = {
    "stale_missing_closure": "still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(load_text(path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_absent(text: str, label: str, marker: str) -> list[str]:
    if marker in text:
        return [f"{label}:forbidden_marker_present"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    file_map = {
        CLOSURE_NOTE_REL: root / CLOSURE_NOTE_REL,
        DOCS_README_REL: root / DOCS_README_REL,
        REVIEW_CHECKLIST_REL: root / REVIEW_CHECKLIST_REL,
        MANIFEST_REL: root / MANIFEST_REL,
        BUILD_FILE_REL: root / BUILD_FILE_REL,
        SMOKE_FILE_REL: root / SMOKE_FILE_REL,
        SCRIPTS_README_REL: root / SCRIPTS_README_REL,
        TESTS_README_REL: root / TESTS_README_REL,
    }

    for relpath, path in file_map.items():
        if not path.exists():
            failures.append(f"missing_file:{relpath.as_posix()}")
            return failures

    closure_text = load_text(file_map[CLOSURE_NOTE_REL])
    for label, marker in REQUIRED_NOTE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, f"closure_note:{label}", marker))

    build_text = load_text(file_map[BUILD_FILE_REL])
    for label, marker in REQUIRED_BUILD_MARKERS.items():
        failures.extend(require_exact_occurrence(build_text, f"build_zig:{label}", marker))

    smoke_text = load_text(file_map[SMOKE_FILE_REL])
    for label, marker in REQUIRED_SMOKE_MARKERS.items():
        failures.extend(require_exact_occurrence(smoke_text, f"phase1_host_tools_smoke:{label}", marker))

    scripts_readme_text = load_text(file_map[SCRIPTS_README_REL])
    for label, marker in REQUIRED_SCRIPTS_README_MARKERS.items():
        failures.extend(require_exact_occurrence(scripts_readme_text, f"scripts_readme:{label}", marker))

    docs_readme_text = load_text(file_map[DOCS_README_REL])
    for label, marker in REQUIRED_DOCS_README_MARKERS.items():
        failures.extend(require_exact_occurrence(docs_readme_text, f"docs_readme:{label}", marker))
    for label, marker in FORBIDDEN_DOCS_README_MARKERS.items():
        failures.extend(require_absent(docs_readme_text, f"docs_readme:{label}", marker))

    review_checklist_text = load_text(file_map[REVIEW_CHECKLIST_REL])
    for label, marker in REQUIRED_REVIEW_CHECKLIST_MARKERS.items():
        failures.extend(require_exact_occurrence(review_checklist_text, f"review_checklist:{label}", marker))

    tests_readme_text = load_text(file_map[TESTS_README_REL])
    for label, marker in REQUIRED_TESTS_README_MARKERS.items():
        failures.extend(require_exact_occurrence(tests_readme_text, f"tests_readme:{label}", marker))

    manifest = load_json(file_map[MANIFEST_REL])
    if not isinstance(manifest, dict):
        failures.append("manifest:expected_json_object")
        return failures

    if manifest.get("phase") != "Phase 1":
        failures.append("manifest:phase")
    if manifest.get("status") != "closed":
        failures.append("manifest:status")
    if manifest.get("helper_count") != 13:
        failures.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        failures.append("manifest:helpers")

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    source_root = DEFAULT_ROOT
    for relpath in (
        CLOSURE_NOTE_REL,
        DOCS_README_REL,
        REVIEW_CHECKLIST_REL,
        MANIFEST_REL,
        BUILD_FILE_REL,
        SMOKE_FILE_REL,
        SCRIPTS_README_REL,
        TESTS_README_REL,
    ):
        write_file(root, relpath, load_text(source_root / relpath))


def run_self_test() -> int:
    cases = [("success", None, None)]
    cases.extend((f"remove_note_{label}", CLOSURE_NOTE_REL, marker) for label, marker in REQUIRED_NOTE_MARKERS.items())
    cases.extend((f"remove_build_{label}", BUILD_FILE_REL, marker) for label, marker in REQUIRED_BUILD_MARKERS.items())
    cases.extend((f"remove_smoke_{label}", SMOKE_FILE_REL, marker) for label, marker in REQUIRED_SMOKE_MARKERS.items())
    cases.extend((f"remove_scripts_{label}", SCRIPTS_README_REL, marker) for label, marker in REQUIRED_SCRIPTS_README_MARKERS.items())
    cases.extend((f"remove_docs_{label}", DOCS_README_REL, marker) for label, marker in REQUIRED_DOCS_README_MARKERS.items())
    cases.extend((f"remove_review_{label}", REVIEW_CHECKLIST_REL, marker) for label, marker in REQUIRED_REVIEW_CHECKLIST_MARKERS.items())
    cases.extend((f"remove_tests_{label}", TESTS_README_REL, marker) for label, marker in REQUIRED_TESTS_README_MARKERS.items())
    cases.append(("docs_forbidden_marker", DOCS_README_REL, next(iter(FORBIDDEN_DOCS_README_MARKERS.values()))))

    for name, relpath, marker in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if name == "success":
                failures = collect_failures(root)
                if failures:
                    print("self-test:success:unexpected_failures")
                    for item in failures:
                        print(item)
                    return 1
                continue

            file_path = root / relpath
            text = file_path.read_text(encoding="utf-8")
            if name == "docs_forbidden_marker":
                file_path.write_text(text + marker + "\n", encoding="utf-8")
            else:
                file_path.write_text(text.replace(marker, "", 1), encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("phase1-closure-self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
