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
]

MISSING_FILES = [
    Path("scripts/zigux/check-phase1-installer-review-surfaces.py"),
    Path("scripts/zigux/check-phase1-installer-companion-checks.py"),
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
]

REQUIRED_README_MARKERS = [
    "Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable",
    "`scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
    "`scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`scripts/zigux/check-phase1-installer-companion-checks.py`",
    "`scripts/zigux/validate-phase1.py`",
    "`scripts/zigux/check-phase1-parity.py`",
    "`zigux/tests/phase1_helpers.zig`",
    "`zigux/tests/phase1_bench.zig`",
    "`zigux/tests/fixtures/phase1_bench_expectations.json`",
    "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
]

SELF_TEST_CASES = [
    "pass",
    "missing_readme",
    "missing_required_marker",
    "missing_phase1_missing_bucket",
    "present_file_listed_missing",
    "missing_expected_missing_entry",
    "missing_present_file",
    "unexpected_missing_file_returned",
]

PHASE1_MISSING_BUCKET_PREFIX = (
    "- repeated authenticated reads on current `master` still return missing for "
)
PHASE1_MISSING_BUCKET_DELIMITER = ", so treat those "


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_readme(*, include_stale_install_marker: bool) -> str:
    missing_entries = [
        "`scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "`scripts/zigux/check-phase1-installer-companion-checks.py`",
        "`scripts/zigux/validate-phase1.py`",
        "`scripts/zigux/check-phase1-parity.py`",
        "`zigux/tests/phase1_helpers.zig`",
        "`zigux/tests/phase1_bench.zig`",
        "`zigux/tests/fixtures/phase1_bench_expectations.json`",
        "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ]
    if include_stale_install_marker:
        missing_entries.insert(0, "`scripts/zigux/install-zig.py`")
    missing_list = ", ".join(missing_entries[:-1]) + f", and {missing_entries[-1]}"
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
            "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
            "- repeated authenticated reads on current `master` still return missing for "
            + missing_list
            + ", so treat those older installer-backed, validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
            "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
            "",
        ]
    ) + "\n"


def build_sample_root(root: Path, *, include_stale_install_marker: bool = False) -> None:
    write(root / README.relative_to(ROOT), build_readme(include_stale_install_marker=include_stale_install_marker))
    for rel in PRESENT_FILES:
        write(root / rel, "#!/usr/bin/env python3\n")


def extract_phase1_missing_bucket(text: str) -> list[str] | None:
    for line in text.splitlines():
        if not line.startswith(PHASE1_MISSING_BUCKET_PREFIX):
            continue
        if PHASE1_MISSING_BUCKET_DELIMITER not in line:
            continue
        body, _ = line.removeprefix(PHASE1_MISSING_BUCKET_PREFIX).split(
            PHASE1_MISSING_BUCKET_DELIMITER, 1
        )
        parts = body.split("`")
        return [parts[index] for index in range(1, len(parts), 2)]
    return None


def validate(root: Path) -> tuple[str, object]:
    readme = root / README.relative_to(ROOT)
    if not readme.exists():
        return ("missing_readme", readme)
    text = readme.read_text(encoding="utf-8")

    missing_markers = [marker for marker in REQUIRED_README_MARKERS if marker not in text]
    if missing_markers:
        return ("missing_required_marker", missing_markers)

    phase1_missing_bucket = extract_phase1_missing_bucket(text)
    if phase1_missing_bucket is None:
        return ("missing_phase1_missing_bucket", None)

    present_files_listed_missing = [
        str(rel) for rel in PRESENT_FILES if str(rel) in phase1_missing_bucket
    ]
    if present_files_listed_missing:
        return ("present_file_listed_missing", present_files_listed_missing)

    missing_expected_missing_entries = [
        str(rel) for rel in MISSING_FILES if str(rel) not in phase1_missing_bucket
    ]
    if missing_expected_missing_entries:
        return ("missing_expected_missing_entry", missing_expected_missing_entries)

    missing_present_files = [str(rel) for rel in PRESENT_FILES if not (root / rel).exists()]
    if missing_present_files:
        return ("missing_present_file", missing_present_files)

    unexpected_present_missing_files = [str(rel) for rel in MISSING_FILES if (root / rel).exists()]
    if unexpected_present_missing_files:
        return ("unexpected_missing_file_returned", unexpected_present_missing_files)

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

        missing_marker_root = root / "missing_marker"
        build_sample_root(missing_marker_root)
        write(
            missing_marker_root / README.relative_to(ROOT),
            "# scripts/zigux\n\n## Phase 1\n\n- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it.\n",
        )
        assert_case("missing_required_marker", validate(missing_marker_root))
        covered.append("missing_required_marker")

        missing_bucket_root = root / "missing_bucket"
        build_sample_root(missing_bucket_root)
        write(
            missing_bucket_root / README.relative_to(ROOT),
            build_readme(include_stale_install_marker=False).replace(
                PHASE1_MISSING_BUCKET_PREFIX,
                "- older reminder text with no live missing bucket for ",
                1,
            ),
        )
        assert_case("missing_phase1_missing_bucket", validate(missing_bucket_root))
        covered.append("missing_phase1_missing_bucket")

        stale_root = root / "stale_install"
        build_sample_root(stale_root, include_stale_install_marker=True)
        assert_case("present_file_listed_missing", validate(stale_root))
        covered.append("present_file_listed_missing")

        dropped_missing_root = root / "dropped_missing"
        build_sample_root(dropped_missing_root)
        write(
            dropped_missing_root / README.relative_to(ROOT),
            build_readme(include_stale_install_marker=False).replace(
                "phase1_helpers_c_harness.c", "phase1_helpers_harness.c", 1
            )
            + "- marker keepalive `zigux/tests/fixtures/phase1_helpers_c_harness.c`\n",
        )
        assert_case("missing_expected_missing_entry", validate(dropped_missing_root))
        covered.append("missing_expected_missing_entry")

        missing_present_root = root / "missing_present"
        build_sample_root(missing_present_root)
        (missing_present_root / PRESENT_FILES[0]).unlink()
        assert_case("missing_present_file", validate(missing_present_root))
        covered.append("missing_present_file")

        unexpected_missing_root = root / "unexpected_missing"
        build_sample_root(unexpected_missing_root)
        write(unexpected_missing_root / MISSING_FILES[0], "# unexpected\n")
        assert_case("unexpected_missing_file_returned", validate(unexpected_missing_root))
        covered.append("unexpected_missing_file_returned")

    if covered != SELF_TEST_CASES:
        raise AssertionError(("case_coverage", covered))
    print("PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_REPO_REALITY_SELF_TEST_CASE_COUNT={len(covered)}")
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
    print("PHASE1_SCRIPTS_REPO_REALITY_MISSING_BUCKET_MODE=structural")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
