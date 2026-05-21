#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_ROOT_README = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Phase 5 notes - `Documentation/zigux/phase5-sample-review-guide.md`",
    "keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.",
    "* keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "* keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    "* keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.",
    "* keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
    "* keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those two routes.",
)

ORDER_MARKERS = (
    "Phase 3 notes",
    "Phase 5 notes",
    "Phase 6 notes",
)


def collect_failures(root: Path) -> list[str]:
    text = (root / DOCS_ROOT_README).read_text(encoding="utf-8")

    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing:{marker}")

    if text.count("Phase 5 notes") != 1:
        failures.append("count:Phase 5 notes")

    positions = [text.find(marker) for marker in ORDER_MARKERS]
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        failures.append("order:Phase 3 notes -> Phase 5 notes -> Phase 6 notes")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation
Phase 3 notes - placeholder
Phase 5 notes - `Documentation/zigux/phase5-sample-review-guide.md`
keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.
* keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.
* keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.
* keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.
* keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.
* keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those two routes.
Phase 6 notes - placeholder
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_docs_root_phase5_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_ROOT_README, _sample_readme())

        if collect_failures(root):
            raise AssertionError("baseline phase5 fixture should pass")
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "Phase 5 notes - `Documentation/zigux/phase5-sample-review-guide.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:Phase 5 notes - `Documentation/zigux/phase5-sample-review-guide.md`",
            "count:Phase 5 notes",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected phase5 heading failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected packet-summary failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected review-guide failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected no-extra-sample failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected kobject attr-group failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected runtime-split failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those two routes.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those two routes."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected kobject split failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            """# Zigux Documentation
Phase 5 notes - `Documentation/zigux/phase5-sample-review-guide.md`
keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.
* keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.
* keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.
* keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.
* keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.
* keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those two routes.
Phase 3 notes - placeholder
Phase 6 notes - placeholder
""",
        )
        failures = collect_failures(root)
        expected = ["order:Phase 3 notes -> Phase 5 notes -> Phase 6 notes"]
        if failures != expected:
            raise AssertionError(f"unexpected ordering failures: {failures}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE5_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE5_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the live Zigux docs root keeps its Phase 5 notes packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic docs-root fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE5_NOTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
