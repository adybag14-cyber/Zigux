#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
README = ROOT / "scripts" / "zigux" / "README.md"

PRESENT_FILES = [
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
]

MISSING_FILES = [
    Path("scripts/zigux/check-phase1-installer-review-surfaces.py"),
    Path("scripts/zigux/check-phase1-installer-companion-checks.py"),
    Path("scripts/zigux/validate-phase1.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
]

REQUIRED_README_MARKERS = [
    "Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable",
    "`scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
    "repeated authenticated reads on current `master` still return missing for",
]

MISSING_LINE_PREFIX = "repeated authenticated reads on current `master` still return missing for "

SELF_TEST_CASES = [
    "pass",
    "missing_readme",
    "readme_not_file",
    "missing_required_marker",
    "missing_present_file",
    "present_path_not_file",
    "unexpected_missing_file_returned",
    "unexpected_missing_path_not_file",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_with_directory(path: Path) -> None:
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def format_path_list(paths: list[Path]) -> str:
    quoted = [f"`{path.as_posix()}`" for path in paths]
    if len(quoted) == 1:
        return quoted[0]
    return ", ".join(quoted[:-1]) + f", and {quoted[-1]}"


def build_readme() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
            "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
            "- current `master` directly serves `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/check-phase1-parity.py`, so keep the remaining Phase 1 scripts-root reminder follow-through focused on the older validator-first and replay routes that still stay absent instead of modeling those three directly readable paths as repo-reality gaps",
            f"- {MISSING_LINE_PREFIX}{format_path_list(MISSING_FILES)}, so treat those older installer-backed, validator-first, parity-replay, and harness routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
            "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
            "",
        ]
    ) + "\n"


def build_sample_root(root: Path) -> None:
    write(root / README.relative_to(ROOT), build_readme())
    for rel in PRESENT_FILES:
        write(root / rel, "#!/usr/bin/env python3\n")


def find_missing_line(text: str) -> str | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(f"- {MISSING_LINE_PREFIX}"):
            return line[2:]
    return None


def validate(root: Path) -> tuple[str, object]:
    readme = root / README.relative_to(ROOT)
    if not readme.exists():
        return ("missing_readme", readme)
    if not readme.is_file():
        return ("readme_not_file", readme)

    text = readme.read_text(encoding="utf-8")
    missing_markers = [marker for marker in REQUIRED_README_MARKERS if marker not in text]
    if missing_markers:
        return ("missing_required_marker", missing_markers)

    missing_line = find_missing_line(text)
    if missing_line is None:
        return ("missing_required_marker", [MISSING_LINE_PREFIX])

    stale_present_markers = [str(rel) for rel in PRESENT_FILES if f"`{rel.as_posix()}`" in missing_line]
    if stale_present_markers:
        return ("stale_present_path_marked_missing", stale_present_markers)

    omitted_missing_markers = [str(rel) for rel in MISSING_FILES if f"`{rel.as_posix()}`" not in missing_line]
    if omitted_missing_markers:
        return ("missing_absent_path_marker", omitted_missing_markers)

    missing_present_files = [str(rel) for rel in PRESENT_FILES if not (root / rel).exists()]
    if missing_present_files:
        return ("missing_present_file", missing_present_files)

    present_paths_not_file = [str(rel) for rel in PRESENT_FILES if (root / rel).exists() and not (root / rel).is_file()]
    if present_paths_not_file:
        return ("present_path_not_file", present_paths_not_file)

    unexpected_present_missing_files = [str(rel) for rel in MISSING_FILES if (root / rel).is_file()]
    if unexpected_present_missing_files:
        return ("unexpected_missing_file_returned", unexpected_present_missing_files)

    unexpected_present_missing_paths = [str(rel) for rel in MISSING_FILES if (root / rel).exists() and not (root / rel).is_file()]
    if unexpected_present_missing_paths:
        return ("unexpected_missing_path_not_file", unexpected_present_missing_paths)

    return ("pass", None)


def assert_case(kind: str, actual: tuple[str, object]) -> None:
    if actual[0] != kind:
        raise AssertionError((kind, actual))


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_scripts_repo_reality_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert_case("pass", validate(root))
        covered.append("pass")

        missing_readme_root = root / "missing_readme"
        missing_readme_root.mkdir()
        assert_case("missing_readme", validate(missing_readme_root))
        covered.append("missing_readme")

        readme_not_file_root = root / "readme_not_file"
        build_sample_root(readme_not_file_root)
        replace_with_directory(readme_not_file_root / README.relative_to(ROOT))
        assert_case("readme_not_file", validate(readme_not_file_root))
        covered.append("readme_not_file")

        missing_marker_root = root / "missing_marker"
        build_sample_root(missing_marker_root)
        write(
            missing_marker_root / README.relative_to(ROOT),
            "# scripts/zigux\n\n## Phase 1\n\n- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it.\n",
        )
        assert_case("missing_required_marker", validate(missing_marker_root))
        covered.append("missing_required_marker")

        missing_present_root = root / "missing_present"
        build_sample_root(missing_present_root)
        (missing_present_root / PRESENT_FILES[0]).unlink()
        assert_case("missing_present_file", validate(missing_present_root))
        covered.append("missing_present_file")

        present_path_not_file_root = root / "present_path_not_file"
        build_sample_root(present_path_not_file_root)
        replace_with_directory(present_path_not_file_root / PRESENT_FILES[0])
        assert_case("present_path_not_file", validate(present_path_not_file_root))
        covered.append("present_path_not_file")

        unexpected_missing_root = root / "unexpected_missing"
        build_sample_root(unexpected_missing_root)
        write(unexpected_missing_root / MISSING_FILES[0], "# unexpected\n")
        assert_case("unexpected_missing_file_returned", validate(unexpected_missing_root))
        covered.append("unexpected_missing_file_returned")

        unexpected_missing_path_root = root / "unexpected_missing_path"
        build_sample_root(unexpected_missing_path_root)
        replace_with_directory(unexpected_missing_path_root / MISSING_FILES[0])
        assert_case("unexpected_missing_path_not_file", validate(unexpected_missing_path_root))
        covered.append("unexpected_missing_path_not_file")

    if covered != SELF_TEST_CASES:
        raise AssertionError(("case_coverage", covered))
    print("PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST_CASE_COUNT={len(covered)}")
    print("PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST_CASES=" + ",".join(covered))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 1 scripts-root repo-reality packet drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root and exit.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        build_sample_root(args.write_sample_root)
        print(f"PHASE1_SCRIPTS_REPO_REALITY_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    kind, payload = validate(args.root)
    if kind != "pass":
        print(f"PHASE1_SCRIPTS_REPO_REALITY={kind}")
        if payload is not None:
            print(payload)
        return 1

    print("PHASE1_SCRIPTS_REPO_REALITY=pass")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_PRESENT_COUNT={len(PRESENT_FILES)}")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_MISSING_COUNT={len(MISSING_FILES)}")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_REQUIRED_MARKER_COUNT={len(REQUIRED_README_MARKERS)}")
    print("PHASE1_SCRIPTS_REPO_REALITY_STALE_PRESENT_MARKER_COUNT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
