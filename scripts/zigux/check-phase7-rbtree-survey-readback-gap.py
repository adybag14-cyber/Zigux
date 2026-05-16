#!/usr/bin/env python3
"""Guard the current Phase 7 rbtree survey/readback gap."""

from __future__ import annotations

import argparse
import pathlib
import tempfile


EXISTING_ANCHORS = (
    "Documentation/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_rbtree_survey.zig",
    "lib/rbtree.zig",
)

SUMMARY_MARKERS = (
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
)

DOCS_PHASE7_MARKERS = (
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
)

EXPECTED_MISSING = (
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
)


class GapCheckError(RuntimeError):
    pass


def read_text(root: pathlib.Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise GapCheckError(f"required anchor missing: {relative_path}")
    return path.read_text(encoding="utf-8")


def ensure_markers(text: str, markers: tuple[str, ...], source: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        rendered = ", ".join(missing)
        raise GapCheckError(f"{source} no longer carries expected gap markers: {rendered}")


def collect_missing(root: pathlib.Path) -> list[str]:
    return [relative_path for relative_path in EXPECTED_MISSING if not (root / relative_path).exists()]


def inspect_repo(root: pathlib.Path) -> dict[str, object]:
    for relative_path in EXISTING_ANCHORS:
        if not (root / relative_path).is_file():
            raise GapCheckError(f"required anchor missing: {relative_path}")

    docs_text = read_text(root, "Documentation/zigux/README.md")
    survey_text = read_text(root, "zigux/tests/phase7_rbtree_survey.zig")

    ensure_markers(docs_text, DOCS_PHASE7_MARKERS, "Documentation/zigux/README.md")
    ensure_markers(survey_text, SUMMARY_MARKERS, "zigux/tests/phase7_rbtree_survey.zig")

    missing = collect_missing(root)
    unexpected_present = sorted(set(EXPECTED_MISSING) - set(missing))
    if unexpected_present:
        rendered = ", ".join(unexpected_present)
        raise GapCheckError(
            "gap note is stale because some previously missing companion files now exist: "
            f"{rendered}"
        )

    return {
        "missing_count": len(missing),
        "missing_paths": missing,
    }


def build_fixture(root: pathlib.Path) -> None:
    for relative_path, content in {
        "Documentation/zigux/README.md": (
            "Phase 7 notes - `Documentation/zigux/phase7-string-helpers-slice.md` - "
            "`Documentation/zigux/phase7-cmdline-slice.md` - "
            "`Documentation/zigux/phase7-argv-split-slice.md` - "
            "`Documentation/zigux/phase7-rbtree-slice.md` - "
            "`zigux/tests/phase7_build.zig` and `make -C zigux phase7` now gate the current "
            "string-helpers, cmdline, argv-split, and rbtree helper bundle together, while "
            "`lib/string_helpers.zig` plus `zigux/tests/phase7_string_helpers.zig` are back on current master."
        ),
        "zigux/tests/README.md": "phase7 packet reminder\n",
        "zigux/tests/phase7_rbtree_survey.zig": (
            "packet paths: "
            "`Documentation/zigux/phase7-rbtree-slice.md` "
            "`Documentation/zigux/phase7-helper-lane-sequencing.md` "
            "`zigux/tests/phase7_build.zig` "
            "`zigux/tests/phase7_rbtree.zig` "
            "`zigux/tests/phase7_rbtree_manifest.json` "
            "`scripts/zigux/validate-phase7.py` "
            "`scripts/zigux/check-phase7-rbtree-parity.py` "
            "`zigux/tests/fixtures/phase7_rbtree.json` "
            "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`\n"
        ),
        "lib/rbtree.zig": "pub fn anchor() void {}\n",
    }.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    cases = 3
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        build_fixture(root)
        report = inspect_repo(root)
        if report["missing_count"] != len(EXPECTED_MISSING):
            raise SystemExit("self-test failed: unexpected missing-count report")

        stale_file = root / "zigux/tests/phase7_build.zig"
        stale_file.parent.mkdir(parents=True, exist_ok=True)
        stale_file.write_text("// landed companion\n", encoding="utf-8")
        try:
            inspect_repo(root)
        except GapCheckError:
            pass
        else:
            raise SystemExit("self-test failed: stale gap was not detected")
        stale_file.unlink()

        docs = root / "Documentation/zigux/README.md"
        docs.write_text("Phase 7 notes removed\n", encoding="utf-8")
        try:
            inspect_repo(root)
        except GapCheckError:
            pass
        else:
            raise SystemExit("self-test failed: missing docs markers were not detected")

    print("PHASE7_RBTREE_SURVEY_READBACK_GAP_SELF_TEST=pass")
    print(f"PHASE7_RBTREE_SURVEY_READBACK_GAP_SELF_TEST_CASES={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    report = inspect_repo(pathlib.Path(args.repo_root))
    print("PHASE7_RBTREE_SURVEY_READBACK_GAP=present")
    print(f"PHASE7_RBTREE_SURVEY_READBACK_GAP_MISSING_COUNT={report['missing_count']}")
    for relative_path in report["missing_paths"]:
        print(f"MISSING={relative_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
