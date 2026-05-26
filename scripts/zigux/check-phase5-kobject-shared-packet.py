#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase5-kobject-sample-survey.md")
GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
LANE_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_build.zig",
)

FALLBACK_PACKET_PATHS = (
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
)

MARKERS = {
    SURVEY_PATH: (
        "Authenticated contents readback in this run directly returned:",
        "`samples/zigux/kobject_example_attr_group_contract.zig`",
        "`zigux/tests/phase5_kobject_attr_group_contract.zig`",
        "`zigux/tests/phase5_kobject_attr_group_contract_survey.zig`",
        "The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor",
        "Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:",
        "`zigux/tests/phase5_kobject_example_manifest.json`",
        "`zigux/tests/phase5_kobject_example_survey.zig`",
        "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract",
    ),
    GUIDE_PATH: (
        "The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit:",
        "`samples/zigux/kobject_example_attr_group_contract.zig` keeps the bounded `foo`/`baz`/`bar` attribute-group contract",
        "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet",
        "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit",
    ),
    LANE_PATH: (
        "Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet",
        "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion",
        "`phase5-kobject-example-sample-selfcheck`",
        "while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.",
    ),
    CHECKLIST_PATH: (
        "keep `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the current direct sample-root, focused-test, bounded attr-group companion, focused attr-group replay, and attr-group survey-guard evidence in this runtime,",
        "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
        "keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet,",
    ),
    SAMPLE_ROOT_PATH: (
        "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime:",
        "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion.",
        "Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route",
    ),
    TESTS_ROOT_PATH: (
        "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again",
        "`samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract",
        "`zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
    ),
}

FORBIDDEN_TEXT = (
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/kobject_example_attr_group_contract.zig` as a fifth Phase 5 sample family.",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def placeholder(rel: Path) -> str:
    lines = [f"# Placeholder for {rel}"]
    lines.extend(MARKERS[rel])
    return "\n\n".join(lines) + "\n"


def seed(root: Path) -> None:
    for rel in MARKERS:
        write_text(root, rel, placeholder(rel))
    for rel in DIRECT_PACKET_PATHS + FALLBACK_PACKET_PATHS:
        path = Path(rel)
        if path in MARKERS:
            continue
        write_text(root, path, "present\n")


def strip_standalone_path(text: str, rel: str) -> str:
    standalone = f"\n\n`{rel}`"
    if standalone in text:
        return text.replace(standalone, "", 1)
    return text.replace(rel, "", 1)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    texts = {rel: read_text(root, rel) for rel in MARKERS}

    for rel, required_markers in MARKERS.items():
        text = texts[rel]
        for marker in required_markers:
            if marker not in text:
                failures.append(f"{rel}:missing_text:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in FALLBACK_PACKET_PATHS:
        guide_text = texts[GUIDE_PATH]
        lane_text = texts[LANE_PATH]
        survey_text = texts[SURVEY_PATH]
        if all(token not in guide_text and token not in lane_text and token not in survey_text for token in (f"`{rel}`", rel)):
            failures.append(f"packet:missing_fallback_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_fallback_path:{rel}")

    for forbidden in FORBIDDEN_TEXT:
        if forbidden in texts[GUIDE_PATH] or forbidden in texts[SURVEY_PATH] or forbidden in texts[SAMPLE_ROOT_PATH]:
            failures.append(f"forbidden_text:{forbidden}")

    return failures


def expect_exact(label: str, actual: list[str], expected: list[str]) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def write_sample_root(dest: Path) -> None:
    seed(dest)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 12
    with tempfile.TemporaryDirectory(prefix="phase5_kobject_shared_packet_") as tmpdir:
        root = Path(tmpdir)

        baseline = root / "baseline"
        seed(baseline)
        expect_exact("baseline", collect_failures(baseline), [])
        checks_run += 1

        missing_survey = root / "missing_survey_marker"
        seed(missing_survey)
        write_text(missing_survey, SURVEY_PATH, placeholder(SURVEY_PATH).replace(MARKERS[SURVEY_PATH][4], ""))
        expect_exact("missing survey marker", collect_failures(missing_survey), [f"{SURVEY_PATH}:missing_text:{MARKERS[SURVEY_PATH][4]}"])
        checks_run += 1

        missing_guide = root / "missing_guide_marker"
        seed(missing_guide)
        write_text(missing_guide, GUIDE_PATH, placeholder(GUIDE_PATH).replace(MARKERS[GUIDE_PATH][2], ""))
        expect_exact("missing guide marker", collect_failures(missing_guide), [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][2]}"])
        checks_run += 1

        missing_lane = root / "missing_lane_marker"
        seed(missing_lane)
        write_text(missing_lane, LANE_PATH, placeholder(LANE_PATH).replace(MARKERS[LANE_PATH][2], ""))
        expect_exact("missing lane marker", collect_failures(missing_lane), [f"{LANE_PATH}:missing_text:{MARKERS[LANE_PATH][2]}"])
        checks_run += 1

        missing_checklist = root / "missing_checklist_marker"
        seed(missing_checklist)
        write_text(missing_checklist, CHECKLIST_PATH, placeholder(CHECKLIST_PATH).replace(MARKERS[CHECKLIST_PATH][1], ""))
        expect_exact("missing checklist marker", collect_failures(missing_checklist), [f"{CHECKLIST_PATH}:missing_text:{MARKERS[CHECKLIST_PATH][1]}"])
        checks_run += 1

        missing_sample_root = root / "missing_sample_root_marker"
        seed(missing_sample_root)
        write_text(missing_sample_root, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(MARKERS[SAMPLE_ROOT_PATH][2], ""))
        expect_exact("missing sample-root marker", collect_failures(missing_sample_root), [f"{SAMPLE_ROOT_PATH}:missing_text:{MARKERS[SAMPLE_ROOT_PATH][2]}"])
        checks_run += 1

        missing_tests_root = root / "missing_tests_root_marker"
        seed(missing_tests_root)
        write_text(missing_tests_root, TESTS_ROOT_PATH, placeholder(TESTS_ROOT_PATH).replace(MARKERS[TESTS_ROOT_PATH][2], ""))
        expect_exact("missing tests-root marker", collect_failures(missing_tests_root), [f"{TESTS_ROOT_PATH}:missing_text:{MARKERS[TESTS_ROOT_PATH][2]}"])
        checks_run += 1

        missing_fallback_ref = root / "missing_fallback_ref"
        seed(missing_fallback_ref)
        write_text(missing_fallback_ref, SURVEY_PATH, strip_standalone_path(placeholder(SURVEY_PATH), "zigux/tests/phase5_kobject_example_manifest.json"))
        expect_exact("missing fallback ref", collect_failures(missing_fallback_ref), [f"{SURVEY_PATH}:missing_text:{MARKERS[SURVEY_PATH][6]}"])
        checks_run += 1

        missing_direct_repo_path = root / "missing_direct_repo_path"
        seed(missing_direct_repo_path)
        (missing_direct_repo_path / "zigux/tests/phase5_kobject_attr_group_contract_survey.zig").unlink()
        expect_exact("missing direct repo path", collect_failures(missing_direct_repo_path), ["repo:missing_direct_path:zigux/tests/phase5_kobject_attr_group_contract_survey.zig"])
        checks_run += 1

        missing_fallback_repo_path = root / "missing_fallback_repo_path"
        seed(missing_fallback_repo_path)
        (missing_fallback_repo_path / "samples/zigux/kobject_example.zig").unlink()
        expect_exact("missing fallback repo path", collect_failures(missing_fallback_repo_path), ["repo:missing_fallback_path:samples/zigux/kobject_example.zig"])
        checks_run += 1

        forbidden = root / "forbidden"
        seed(forbidden)
        write_text(forbidden, GUIDE_PATH, placeholder(GUIDE_PATH) + FORBIDDEN_TEXT[0] + "\n")
        expect_exact("forbidden text", collect_failures(forbidden), [f"forbidden_text:{FORBIDDEN_TEXT[0]}"])
        checks_run += 1

        extra_context = root / "extra_context"
        seed(extra_context)
        write_text(extra_context, SURVEY_PATH, placeholder(SURVEY_PATH) + "\nContext: keep the mixed packet honest.\n")
        expect_exact("extra context", collect_failures(extra_context), [])
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")
    print("PHASE5_KOBJECT_SHARED_PACKET_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_SHARED_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample tree for replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE5_KOBJECT_SHARED_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_KOBJECT_SHARED_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_KOBJECT_SHARED_PACKET=pass")
    print(f"PHASE5_KOBJECT_SHARED_PACKET_DIRECT_PATH_COUNT={len(DIRECT_PACKET_PATHS)}")
    print(f"PHASE5_KOBJECT_SHARED_PACKET_FALLBACK_PATH_COUNT={len(FALLBACK_PACKET_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
