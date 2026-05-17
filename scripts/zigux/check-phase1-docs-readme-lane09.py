#!/usr/bin/env python3
"""Guard the docs-root Phase 1 Lane 09 parity-fixture packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DOCS_README_REL = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = {
    "phase1_manifest_note": "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "phase1_fixture_note": "- `zigux/tests/fixtures/phase1_helpers.json`",
    "phase1_missing_routes_note": "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/build.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `Documentation/zigux/artifact-diff.md`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, closure-side, validator-first, bench, replay, harness, and artifact-diff routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.",
    "phase1_packet_alignment_note": "- the current docs-root Phase 1 reminder packet should stay parked on the live owner-map and string-review guards: `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py` are the shipped direct checks, while `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helpers.json`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around them.",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


LINE_LABELS = {
    "phase1_missing_routes_note",
    "phase1_packet_alignment_note",
}


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == line)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    readme_path = root / DOCS_README_REL
    if not readme_path.exists():
        return [f"missing_file:{DOCS_README_REL.as_posix()}"]

    readme_text = load_text(root, DOCS_README_REL)
    missing: list[str] = []
    for label, line in REQUIRED_MARKERS.items():
        if label in LINE_LABELS:
            missing.extend(require_exact_line(readme_text, f"docs_readme:{label}", line))
        else:
            missing.extend(require_exact_occurrence(readme_text, f"docs_readme:{label}", line))
    return missing


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_readme_text() -> str:
    return (
        "# Zigux Documentation This directory is the product documentation root for Zigux.\n"
        "Phase 1 notes\n"
        f"{REQUIRED_MARKERS['phase1_manifest_note']}\n"
        f"{REQUIRED_MARKERS['phase1_fixture_note']}\n"
        f"{REQUIRED_MARKERS['phase1_missing_routes_note']}\n"
        f"{REQUIRED_MARKERS['phase1_packet_alignment_note']}\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(root, DOCS_README_REL, sample_readme_text())


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str]] = [("success", None, "none")]
    for label, line in REQUIRED_MARKERS.items():
        cases.append((f"missing_{label}", line, "remove"))
        cases.append((f"duplicate_{label}", line, "duplicate"))

    for name, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-docs-readme-lane09-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if needle:
                target = root / DOCS_README_REL
                text = target.read_text(encoding="utf-8")
                if operation == "remove":
                    target.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    target.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")

            missing = collect_failures(root)
            if name == "success":
                if missing:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in missing:
                        print(item)
                    return 1
                continue

            if not missing:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_failures(repo_root(args.root))
    if missing:
        for item in missing:
            print(item)
        return 1

    print("phase1-docs-readme-lane09:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
