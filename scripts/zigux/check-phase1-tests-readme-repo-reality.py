#!/usr/bin/env python3
"""Guard the current Phase 1 tests-root repo-reality packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

TESTS_README_REL = "zigux/tests/README.md"
MAKEFILE_REL = "zigux/Makefile"

DIRECT_PACKET_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    TESTS_README_REL,
)

REQUIRED_FILES = DIRECT_PACKET_FILES + (MAKEFILE_REL,)

BROADER_COMPANION_GAPS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

REQUIRED_LINES = (
    "* current direct-readback Phase 1 reminder packet:",
    "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "* current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    "* current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
)

REQUIRED_MAKEFILE_LINES = (
    "phase1-route-summary:",
    "phase3-validate:",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-validate:",
    "phase14-validate",
)

FORBIDDEN_MAKEFILE_LINES = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_required_file:{relative_path}")

    for relative_path in BROADER_COMPANION_GAPS:
        if (root / relative_path).exists():
            failures.append(f"unexpected_broader_companion_presence:{relative_path}")

    if failures:
        return failures

    tests_readme = read_text(root, TESTS_README_REL)
    for marker in REQUIRED_LINES:
        count = count_exact_line(tests_readme, marker)
        if count != 1:
            failures.append(
                f"tests_readme_marker_count:{marker}:expected=1:actual={count}"
            )

    for relative_path in DIRECT_PACKET_FILES:
        marker = f"- `{relative_path}`"
        count = count_exact_line(tests_readme, marker)
        if count != 1:
            failures.append(
                f"tests_readme_direct_packet_entry:{relative_path}:expected=1:actual={count}"
            )

    makefile_text = read_text(root, MAKEFILE_REL)
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, marker)
        if count != 1:
            failures.append(
                f"makefile_required_line:{marker}:expected=1:actual={count}"
            )

    for marker in FORBIDDEN_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, marker)
        if count != 0:
            failures.append(f"makefile_forbidden_line:{marker}:expected=0:actual={count}")

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def build_sample_repo(root: Path) -> None:
    tests_readme_lines = [
        "# zigux/tests",
        "",
        "## Phase 1 host-tools review packet",
        "",
        REQUIRED_LINES[0],
        *[f"- `{relative_path}`" for relative_path in DIRECT_PACKET_FILES],
        REQUIRED_LINES[1],
        REQUIRED_LINES[2],
        REQUIRED_LINES[3],
        REQUIRED_LINES[4],
        REQUIRED_LINES[5],
    ]
    for relative_path in DIRECT_PACKET_FILES:
        if relative_path == TESTS_README_REL:
            write_text(root, relative_path, "\n".join(tests_readme_lines) + "\n")
        else:
            write_text(root, relative_path, f"placeholder for {relative_path}\n")
    write_text(root, MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")


def remove_exact_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def duplicate_exact_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_required:{relative_path}", ("remove_file", relative_path)))
    for relative_path in BROADER_COMPANION_GAPS:
        cases.append((f"unexpected_gap_presence:{relative_path}", ("add_file", relative_path)))
    for marker in REQUIRED_LINES:
        cases.append((f"missing_line:{marker}", ("remove_line", TESTS_README_REL, marker)))
        cases.append((f"duplicate_line:{marker}", ("duplicate_line", TESTS_README_REL, marker)))
    for relative_path in DIRECT_PACKET_FILES:
        marker = f"- `{relative_path}`"
        cases.append((f"missing_entry:{relative_path}", ("remove_line", TESTS_README_REL, marker)))
        cases.append((f"duplicate_entry:{relative_path}", ("duplicate_line", TESTS_README_REL, marker)))
    for marker in REQUIRED_MAKEFILE_LINES:
        cases.append((f"missing_makefile_line:{marker}", ("remove_line", MAKEFILE_REL, marker)))
        cases.append((f"duplicate_makefile_line:{marker}", ("duplicate_line", MAKEFILE_REL, marker)))
    for marker in FORBIDDEN_MAKEFILE_LINES:
        cases.append((f"forbidden_makefile:{marker}", ("add_line", MAKEFILE_REL, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-tests-readme-repo-reality-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove_file":
                    (root / mutation[1]).unlink()
                elif kind == "add_file":
                    write_text(root, mutation[1], "unexpected broader companion\n")
                elif kind == "remove_line":
                    remove_exact_line(root, mutation[1], mutation[2])
                elif kind == "duplicate_line":
                    duplicate_exact_line(root, mutation[1], mutation[2])
                elif kind == "add_line":
                    path = root / mutation[1]
                    text = path.read_text(encoding="utf-8")
                    path.write_text(text + mutation[2] + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_TESTS_README_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_REPO_REALITY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample repo root instead of validating",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print("PHASE1_TESTS_README_REPO_REALITY_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_TESTS_README_REPO_REALITY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_TESTS_README_REPO_REALITY=pass")
    print(f"PHASE1_TESTS_README_REPO_REALITY_DIRECT_PACKET_COUNT={len(DIRECT_PACKET_FILES)}")
    print(
        "PHASE1_TESTS_README_REPO_REALITY_BROADER_COMPANION_GAP_COUNT="
        f"{len(BROADER_COMPANION_GAPS)}"
    )
    print(
        "PHASE1_TESTS_README_REPO_REALITY_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_LINES) + len(DIRECT_PACKET_FILES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
