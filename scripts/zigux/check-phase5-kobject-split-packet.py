#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SURVEY_PATH = Path("Documentation/zigux/phase5-kobject-sample-survey.md")
GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")
SCRIPTS_ROOT_PATH = Path("scripts/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")

DIRECT_KOBJECT_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_build.zig",
)

SHARED_REMINDER_OWNER_PATHS = (
    "samples/zigux/kobject_example.zig",
)

PUBLIC_TREE_COMPANION_PATHS = (
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
)

MARKERS = {
    SURVEY_PATH: (
        "The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when this run's authenticated contents route flaked on that one path, so that owner path stays shared-reminder-backed rather than direct authenticated proof in this runtime.",
        "Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:",
        "The strongest current packet for this lane is:",
        "- the direct sample-owned replay, bounded attr-group companion, focused attr-group replay, attr-group survey guard, and shared build-route companion are current direct evidence again",
        "- the dedicated manifest and survey replay remain current public-tree-backed companions in this runtime when the authenticated contents route flakes on them",
        "- connector-local `404` results on the companion paths are a readback limitation here, not proof that the packet vanished from `master`",
    ),
    GUIDE_PATH: (
        "The same-lane survey note and shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when the current authenticated reread flakes on that one path.",
        "The current public-tree-backed companions are:",
        "* `zigux/tests/phase5_kobject_example_manifest.json`",
        "* `zigux/tests/phase5_kobject_example_survey.zig`",
    ),
    CHECKLIST_PATH: (
        "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` explicit as the current direct reminder or replay surfaces in this runtime, keep `samples/zigux/kobject_example.zig` framed as the current shared-reminder-backed owner path, keep `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
    ),
    SAMPLE_ROOT_PATH: (
        "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again.",
    ),
    SCRIPTS_ROOT_PATH: (
        "keep the current kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the direct reminder or replay surfaces in this runtime, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again",
    ),
    TESTS_ROOT_PATH: (
        "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
    ),
}


def read_text(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def write_text(root: Path, path: Path, text: str) -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def strip_standalone_path(text: str, rel: str) -> str:
    standalone = f"\n`{rel}`"
    if standalone in text:
        return text.replace(standalone, "", 1)
    return text


def seed(root: Path) -> None:
    for path, markers in MARKERS.items():
        write_text(root, path, "# seeded\n\n" + "\n\n".join(markers) + "\n")
    survey_lines = [f"`{rel}`" for rel in DIRECT_KOBJECT_PATHS + PUBLIC_TREE_COMPANION_PATHS + SHARED_REMINDER_OWNER_PATHS]
    write_text(root, SURVEY_PATH, read_text(root, SURVEY_PATH) + "\n" + "\n".join(survey_lines) + "\n")
    guide_lines = [f"`{rel}`" for rel in PUBLIC_TREE_COMPANION_PATHS + SHARED_REMINDER_OWNER_PATHS]
    write_text(root, GUIDE_PATH, read_text(root, GUIDE_PATH) + "\n" + "\n".join(guide_lines) + "\n")
    for rel in DIRECT_KOBJECT_PATHS + SHARED_REMINDER_OWNER_PATHS + PUBLIC_TREE_COMPANION_PATHS:
        rel_path = Path(rel)
        if rel_path in MARKERS:
            continue
        write_text(root, rel_path, "present\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    texts = {path: read_text(root, path) for path in MARKERS}
    for path, markers in MARKERS.items():
        text = texts[path]
        for marker in markers:
            if marker not in text:
                failures.append(f"{path}:missing_text:{marker}")

    survey = texts[SURVEY_PATH]
    guide = texts[GUIDE_PATH]
    for rel in DIRECT_KOBJECT_PATHS:
        if f"`{rel}`" not in survey and rel not in survey:
            failures.append(f"survey:missing_direct_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in SHARED_REMINDER_OWNER_PATHS:
        if f"`{rel}`" not in guide and rel not in guide:
            failures.append(f"guide:missing_owner_path:{rel}")
        if f"`{rel}`" not in survey and rel not in survey:
            failures.append(f"survey:missing_owner_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_owner_path:{rel}")

    for rel in PUBLIC_TREE_COMPANION_PATHS:
        if f"`{rel}`" not in guide and rel not in guide:
            failures.append(f"guide:missing_public_companion:{rel}")
        if f"`{rel}`" not in survey and rel not in survey:
            failures.append(f"survey:missing_public_companion:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_public_companion:{rel}")

    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_kobject_split_packet_") as tmpdir:
        root = Path(tmpdir)

        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_survey_split_marker"
        seed(mutated)
        broken = read_text(mutated, SURVEY_PATH).replace(MARKERS[SURVEY_PATH][0], "")
        write_text(mutated, SURVEY_PATH, broken)
        expect_exact(
            "missing survey split marker",
            collect_failures(mutated),
            [f"{SURVEY_PATH}:missing_text:{MARKERS[SURVEY_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_owner_path_from_guide"
        seed(mutated)
        broken = read_text(mutated, GUIDE_PATH).replace(MARKERS[GUIDE_PATH][0], "")
        write_text(mutated, GUIDE_PATH, broken)
        expect_exact(
            "missing owner path from guide",
            collect_failures(mutated),
            [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_public_companion_from_survey"
        seed(mutated)
        broken = strip_standalone_path(read_text(mutated, SURVEY_PATH), "zigux/tests/phase5_kobject_example_manifest.json")
        write_text(mutated, SURVEY_PATH, broken)
        expect_exact(
            "missing public companion from survey",
            collect_failures(mutated),
            ["survey:missing_public_companion:zigux/tests/phase5_kobject_example_manifest.json"],
        )
        checks_run += 1

        mutated = root / "missing_direct_path_from_survey"
        seed(mutated)
        broken = strip_standalone_path(read_text(mutated, SURVEY_PATH), "zigux/tests/phase5_kobject_example.zig")
        write_text(mutated, SURVEY_PATH, broken)
        expect_exact(
            "missing direct path from survey",
            collect_failures(mutated),
            ["survey:missing_direct_path:zigux/tests/phase5_kobject_example.zig"],
        )
        checks_run += 1

        mutated = root / "missing_owner_repo_path"
        seed(mutated)
        (mutated / "samples/zigux/kobject_example.zig").unlink()
        expect_exact(
            "missing owner repo path",
            collect_failures(mutated),
            ["repo:missing_owner_path:samples/zigux/kobject_example.zig"],
        )
        checks_run += 1

        mutated = root / "missing_public_companion_repo_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_kobject_example_survey.zig").unlink()
        expect_exact(
            "missing public companion repo path",
            collect_failures(mutated),
            ["repo:missing_public_companion:zigux/tests/phase5_kobject_example_survey.zig"],
        )
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")
    print("PHASE5_KOBJECT_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_SPLIT_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_KOBJECT_SPLIT_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_KOBJECT_SPLIT_PACKET=pass")
    print(f"PHASE5_KOBJECT_SPLIT_PACKET_DIRECT_COUNT={len(DIRECT_KOBJECT_PATHS)}")
    print(f"PHASE5_KOBJECT_SPLIT_PACKET_OWNER_COUNT={len(SHARED_REMINDER_OWNER_PATHS)}")
    print(f"PHASE5_KOBJECT_SPLIT_PACKET_COMPANION_COUNT={len(PUBLIC_TREE_COMPANION_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
