#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SURVEYED_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_FILES = [
    "scripts/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-devres-scatterlist-slice.md",
    "zigux/Makefile",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_scatterlist.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
]

SCRIPTS_README_MARKER = (
    "that shared Phase 13 release packet keeps `Documentation/zigux/phase13-notifier-list-survey.md`, "
    "`Documentation/zigux/phase13-devres-scatterlist-slice.md`, the four roadmap-anchor manifests plus "
    "`zigux/tests/phase13_notifier_list_manifest.json`, the direct libfs, devres, coherent-DMA, "
    "scatterlist, Landlock ruleset, and Landlock syscalls helper replays, the `iounmap`, `iomap`, "
    "wrapper, ruleset-fops-sync, and syscall reviewability gates, `zigux/tests/phase13_notifier_list_reviewability.zig`, "
    "`zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` visible "
    "from the scripts root so the contributor packet names the same validator-first evidence bundle as the tests-root and docs-root guides."
)

REVIEW_CHECKLIST_MARKER = (
    "if the change touches the shared Phase 13 release-discipline packet, do "
    "`scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, "
    "`Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, "
    "`zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, "
    "`zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_reviewability.zig` still keep the scripts-root "
    "devres inventory sentence and its adjacent coherent-DMA, scatterlist, plus reviewability evidence explicit so reviewer guidance "
    "does not drift behind the stricter shared validator contract?"
)

MAKEFILE_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/check-phase13-devres-inventory-contract.py --self-test",
    "scripts/zigux/check-phase13-devres-inventory-contract.py",
]

MAKEFILE_EXACT_COUNT_MARKERS = {
    "scripts/zigux/check-phase13-devres-inventory-contract.py --self-test": 1,
    "scripts/zigux/check-phase13-devres-inventory-contract.py\n": 1,
}

SURVEY_MARKERS = [
    "# Phase 13 devres helper DMA/scatterlist boundary survey",
    "helper-first iomap or resource planners plus explicit DMA/scatterlist blockers pinned to the current repo state",
]

REVIEWABILITY_MARKERS = [
    'test "phase13 devres manifest records the current helper boundary and explicit dma/scatterlist blockers"',
    "try std.testing.expect(!descriptor.touches_live_dma);",
    "try std.testing.expect(!descriptor.touches_live_scatterlist);",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def _require_exact_count(
    missing: list[str], label: str, text: str, marker: str, expected_count: int
) -> None:
    actual_count = text.count(marker)
    if actual_count != expected_count:
        missing.append(f"{label}:exact_count:{marker}:{actual_count}!={expected_count}")


def _check_repo(root: Path) -> list[str]:
    missing: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(f"missing_file:{rel}")

    if missing:
        return missing

    scripts_readme_text = _read(root / "scripts/zigux/README.md")
    review_checklist_text = _read(root / "Documentation/zigux/review-checklist.md")
    survey_text = _read(root / "Documentation/zigux/phase13-devres-survey.md")
    makefile_text = _read(root / "zigux/Makefile")
    reviewability_text = _read(root / "zigux/tests/phase13_devres_reviewability.zig")
    manifest = json.loads(_read(root / "zigux/tests/phase13_devres_manifest.json"))

    _require_exact_count(
        missing, "scripts_readme", scripts_readme_text, SCRIPTS_README_MARKER, 1
    )
    _require_exact_count(
        missing,
        "review_checklist",
        review_checklist_text,
        REVIEW_CHECKLIST_MARKER,
        1,
    )
    _require_markers(missing, "makefile", makefile_text, MAKEFILE_MARKERS)
    for marker, expected_count in MAKEFILE_EXACT_COUNT_MARKERS.items():
        _require_exact_count(missing, "makefile", makefile_text, marker, expected_count)
    _require_markers(missing, "survey", survey_text, SURVEY_MARKERS)
    _require_markers(missing, "reviewability", reviewability_text, REVIEWABILITY_MARKERS)

    if manifest.get("phase") != "Phase 13":
        missing.append("manifest:phase")
    if manifest.get("lane_key") != "P13-L10":
        missing.append("manifest:lane_key")
    if manifest.get("anchor") != "lib/devres.c":
        missing.append("manifest:anchor")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or SURVEYED_COMMIT_RE.fullmatch(surveyed_commit) is None:
        missing.append("manifest:surveyed_commit")
    elif f"- `PHASE13_SURVEYED_COMMIT={surveyed_commit}`" not in survey_text:
        missing.append("survey:surveyed_commit")

    return missing


def _run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests").mkdir(parents=True, exist_ok=True)

        surveyed_commit = "aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb"
        case_count = 0

        (root / "scripts/zigux/README.md").write_text(
            SCRIPTS_README_MARKER + "\n", encoding="utf-8"
        )
        (root / "Documentation/zigux/review-checklist.md").write_text(
            REVIEW_CHECKLIST_MARKER + "\n", encoding="utf-8"
        )
        (root / "Documentation/zigux/phase13-devres-survey.md").write_text(
            f"- `PHASE13_SURVEYED_COMMIT={surveyed_commit}`\n"
            + "\n".join(SURVEY_MARKERS)
            + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-devres-scatterlist-slice.md").write_text(
            "# Phase 13 devres scatterlist helper slice\n",
            encoding="utf-8",
        )
        (root / "zigux/Makefile").write_text(
            "phase13-validate:\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py --self-test\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_devres_reviewability.zig").write_text(
            "\n".join(REVIEWABILITY_MARKERS) + "\n", encoding="utf-8"
        )
        (root / "zigux/tests/phase13_devres_dma_coherent.zig").write_text(
            'test "phase13 devres coherent dma placeholder" {}\n',
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_devres_scatterlist.zig").write_text(
            'test "phase13 devres scatterlist placeholder" {}\n',
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_devres_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 13",
                    "lane_key": "P13-L10",
                    "anchor": "lib/devres.c",
                    "surveyed_commit": surveyed_commit,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        missing = _check_repo(root)
        if missing:
            print("PHASE13_DEVRES_INVENTORY_CONTRACT_SELF_TEST=fail")
            for item in missing:
                print(item)
            return 1
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(
            _read(makefile_path)
            + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py\n",
            encoding="utf-8",
        )
        missing = _check_repo(root)
        expected_missing = (
            "makefile:exact_count:scripts/zigux/check-phase13-devres-inventory-contract.py\n:2!=1"
        )
        if expected_missing not in missing:
            print("PHASE13_DEVRES_INVENTORY_CONTRACT_SELF_TEST=fail")
            print("missing duplicate makefile route exact-count failure")
            for item in missing:
                print(item)
            return 1
        case_count += 1
        makefile_path.write_text(
            "phase13-validate:\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py --self-test\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py\n",
            encoding="utf-8",
        )

        scripts_path = root / "scripts/zigux/README.md"
        scripts_path.write_text(
            _read(scripts_path) + SCRIPTS_README_MARKER + "\n", encoding="utf-8"
        )
        missing = _check_repo(root)
        expected_missing = f"scripts_readme:exact_count:{SCRIPTS_README_MARKER}:2!=1"
        if expected_missing not in missing:
            print("PHASE13_DEVRES_INVENTORY_CONTRACT_SELF_TEST=fail")
            print("missing duplicate scripts-root inventory exact-count failure")
            for item in missing:
                print(item)
            return 1
        case_count += 1
        scripts_path.write_text(SCRIPTS_README_MARKER + "\n", encoding="utf-8")

        checklist_path = root / "Documentation/zigux/review-checklist.md"
        checklist_path.write_text("", encoding="utf-8")
        missing = _check_repo(root)
        expected_missing = (
            "review_checklist:exact_count:" + REVIEW_CHECKLIST_MARKER + ":0!=1"
        )
        if expected_missing not in missing:
            print("PHASE13_DEVRES_INVENTORY_CONTRACT_SELF_TEST=fail")
            print("missing review checklist inventory sentence failure")
            for item in missing:
                print(item)
            return 1
        case_count += 1

    print("PHASE13_DEVRES_INVENTORY_CONTRACT_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_INVENTORY_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        return _run_self_test()

    missing = _check_repo(Path(args.root).resolve())
    if missing:
        print("PHASE13_DEVRES_INVENTORY_CONTRACT=fail")
        print("PHASE13_DEVRES_INVENTORY_CONTRACT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_DEVRES_INVENTORY_CONTRACT_MISSING_END")
        return 1

    print("PHASE13_DEVRES_INVENTORY_CONTRACT=pass")
    print(f"PHASE13_DEVRES_INVENTORY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_DEVRES_INVENTORY_MARKER_COUNT="
        f"{1 + 1 + len(MAKEFILE_MARKERS) + len(MAKEFILE_EXACT_COUNT_MARKERS) + len(SURVEY_MARKERS) + len(REVIEWABILITY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
