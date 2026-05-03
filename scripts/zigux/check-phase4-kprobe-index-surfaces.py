#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_build.zig",
]

DOCS_ROOT_MARKERS = [
    "direct `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`",
    "phase4-kprobe-example-survey-tests",
    "still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "make -C zigux phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "c_anchor_only_until_kprobe_example_starter_lands",
]

BUILD_MARKERS = [
    "phase4_kprobe_example_survey.zig",
    "phase4-kprobe-example-survey-tests",
    "\"phase4-kprobe-example-survey\"",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "validate-phase4.py",
    "check-phase4-gate-evidence.py",
    "make -C zigux phase4-test-fsmount-survey",
    "make -C zigux phase4-perf-baseline-survey",
]

SCRIPTS_README_FORBIDDEN_MARKERS = [
    "phase4-kprobe-example-survey",
    "phase4_kprobe_example_manifest.json",
    "phase4_kprobe_example_survey.zig",
]


def collect_present_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker in text]


def collect_missing(root: Path) -> list[str]:
    missing = [
        f"missing_file:{path}" for path in REQUIRED_FILES if not (root / path).exists()
    ]
    if missing:
        return missing

    docs_root = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    phase4_build = (root / "zigux/tests/phase4_build.zig").read_text(encoding="utf-8")

    missing.extend(collect_present_markers(docs_root, DOCS_ROOT_MARKERS, "docs_root"))
    missing.extend(
        collect_present_markers(tests_readme, TESTS_README_MARKERS, "tests_readme")
    )
    missing.extend(collect_present_markers(phase4_build, BUILD_MARKERS, "phase4_build"))
    missing.extend(
        collect_present_markers(
            scripts_readme,
            SCRIPTS_README_REQUIRED_MARKERS,
            "scripts_readme_required",
        )
    )
    missing.extend(
        collect_forbidden_markers(
            scripts_readme,
            SCRIPTS_README_FORBIDDEN_MARKERS,
            "scripts_readme_expected_gap",
        )
    )
    return missing


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase4-kprobe-index-surfaces-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="phase4_kprobe_index_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        for relative_path in REQUIRED_FILES:
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative_path == "Documentation/zigux/README.md":
                target.write_text("\n".join(DOCS_ROOT_MARKERS) + "\n", encoding="utf-8")
            elif relative_path == "scripts/zigux/README.md":
                target.write_text(
                    "\n".join(SCRIPTS_README_REQUIRED_MARKERS) + "\n",
                    encoding="utf-8",
                )
            elif relative_path == "zigux/tests/README.md":
                target.write_text(
                    "\n".join(TESTS_README_MARKERS) + "\n",
                    encoding="utf-8",
                )
            elif relative_path == "zigux/tests/phase4_build.zig":
                target.write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
            else:
                target.write_text("placeholder\n", encoding="utf-8")

        missing = collect_missing(root)
        if missing:
            raise SystemExit(
                "phase4-kprobe-index-surfaces-self-test:unexpected_failures:"
                + ",".join(missing)
            )

        (root / "Documentation/zigux/README.md").write_text("", encoding="utf-8")
        expect_contains(
            "docs_root_detection",
            collect_missing(root),
            "docs_root:phase4-kprobe-example-survey-tests",
        )

        (root / "Documentation/zigux/README.md").write_text(
            "\n".join(DOCS_ROOT_MARKERS) + "\n", encoding="utf-8"
        )
        (root / "zigux/tests/README.md").write_text("", encoding="utf-8")
        expect_contains(
            "tests_readme_detection",
            collect_missing(root),
            "tests_readme:make -C zigux phase4-kprobe-example-survey",
        )

        (root / "zigux/tests/README.md").write_text(
            "\n".join(TESTS_README_MARKERS) + "\n", encoding="utf-8"
        )
        (root / "zigux/tests/phase4_build.zig").write_text("", encoding="utf-8")
        expect_contains(
            "phase4_build_detection",
            collect_missing(root),
            "phase4_build:phase4-kprobe-example-survey-tests",
        )

        (root / "zigux/tests/phase4_build.zig").write_text(
            "\n".join(BUILD_MARKERS) + "\n", encoding="utf-8"
        )
        (root / "scripts/zigux/README.md").write_text(
            "\n".join(SCRIPTS_README_REQUIRED_MARKERS + ["phase4-kprobe-example-survey"])
            + "\n",
            encoding="utf-8",
        )
        expect_contains(
            "scripts_gap_detection",
            collect_missing(root),
            "scripts_readme_expected_gap:phase4-kprobe-example-survey",
        )

    print("PHASE4_KPROBE_INDEX_SURFACES_SELF_TEST=pass")
    print("PHASE4_KPROBE_INDEX_SURFACES_SELF_TEST_CASE_COUNT=4")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


missing = collect_missing(ROOT)
if missing:
    print("PHASE4_KPROBE_INDEX_SURFACES=fail")
    print("PHASE4_KPROBE_INDEX_SURFACES_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE4_KPROBE_INDEX_SURFACES_MISSING_END")
    raise SystemExit(1)

print("PHASE4_KPROBE_INDEX_SURFACES=pass")
print(f"PHASE4_KPROBE_INDEX_SURFACES_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE4_KPROBE_INDEX_SURFACES_DOC_MARKER_COUNT={len(DOCS_ROOT_MARKERS)}")
print(f"PHASE4_KPROBE_INDEX_SURFACES_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
print(
    "PHASE4_KPROBE_INDEX_SURFACES_FORBIDDEN_SCRIPTS_MARKER_COUNT="
    f"{len(SCRIPTS_README_FORBIDDEN_MARKERS)}"
)
