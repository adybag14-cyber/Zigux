#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
README_PATH = Path("scripts/zigux/README.md")

EXPECTED_PHASE12_MARKERS = [
    "## Phase 12",
    (
        "- Phase 12 flow - the current scripts-root reminder packet stays "
        "reviewable through the validator-first support bundle and returned "
        "shared wrappers without promoting driver-local rollback, NVMe foothold, "
        "or parked libbpf evidence into the shared smoke-and-test route"
    ),
    (
        "- `scripts/zigux/check-build-only-phase12-surface.py`, "
        "`scripts/zigux/check-phase12-release-readiness-packet.py`, "
        "`scripts/zigux/check-phase12-complex-driver-lane-packet.py`, "
        "`scripts/zigux/check-phase12-cross-compile-smoke.py`, "
        "`scripts/zigux/check-phase12-libbpf-snapshot.py`, "
        "`scripts/zigux/check-phase12-libbpf-lane-marker.py`, "
        "`scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and "
        "`scripts/zigux/validate-phase12.py` keep the current Phase 12 "
        "validator-side support bundle explicit from the scripts root"
    ),
    (
        "- `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, "
        "`make -C zigux phase12-test`, and `make -C zigux phase12` are "
        "shipped current-`master` wrapper evidence again, while "
        "`zigux/tests/phase12_build.zig` keeps the shared smoke and test route "
        "bounded to the six-file `virtio_net` sextet"
    ),
    (
        "- keep the shared route split explicit here too: the six-file "
        "`virtio_net` packet is the only current shared smoke-and-test route, "
        "the rollback-lab `virtio_scsi` survey-build packet and bounded "
        "`nvme_pci` foothold stay driver-local evidence outside that route, "
        "and the parked libbpf packet stays limited to survey, snapshot, "
        "lane-marker, and heavy-consumer reminder guards"
    ),
]

EXPECTED_SUPPORT_TOOLS = [
    "scripts/zigux/check-build-only-phase12-surface.py",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "scripts/zigux/check-phase12-complex-driver-lane-packet.py",
    "scripts/zigux/check-phase12-cross-compile-smoke.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "scripts/zigux/check-phase12-libbpf-lane-marker.py",
    "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
    "scripts/zigux/validate-phase12.py",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / README_PATH).exists():
            return candidate
    return SELF_PATH.parent


def validate(root: Path) -> list[str]:
    readme = root / README_PATH
    if not readme.exists():
        return [f"missing_file:{README_PATH}"]

    text = readme.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in EXPECTED_PHASE12_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{README_PATH}:{marker}")

    for tool in EXPECTED_SUPPORT_TOOLS:
        marker = f"`{tool}`"
        if marker not in text:
            failures.append(f"missing_support_tool:{README_PATH}:{tool}")
    return failures


def write_readme(root: Path, content: str) -> None:
    path = root / README_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_readme() -> str:
    return "# scripts/zigux\n\n" + "\n".join(EXPECTED_PHASE12_MARKERS) + "\n"


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    root = Path(tempfile.mkdtemp(prefix="phase12-scripts-readme-bundle-"))
    try:
        write_readme(root, fixture_readme())
        failures = validate(root)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        for marker in EXPECTED_PHASE12_MARKERS:
            write_readme(root, fixture_readme().replace(marker, "", 1))
            expect_failure(root, f"missing_marker:{README_PATH}:{marker}")

        for tool in EXPECTED_SUPPORT_TOOLS:
            write_readme(
                root,
                fixture_readme().replace(f"`{tool}`", f"`missing/{tool}`", 1),
            )
            expect_failure(root, f"missing_support_tool:{README_PATH}:{tool}")

        shutil.rmtree(root)
        expect_failure(root, f"missing_file:{README_PATH}")

        case_count = len(EXPECTED_PHASE12_MARKERS) + len(EXPECTED_SUPPORT_TOOLS) + 1
        print("PHASE12_SCRIPTS_README_SUPPORT_BUNDLE_SELF_TEST=pass")
        print(f"PHASE12_SCRIPTS_README_SUPPORT_BUNDLE_SELF_TEST_CASES={case_count}")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the scripts-root Phase 12 support-bundle reminder so "
            "libbpf artifact guards stay visible without promoting parked "
            "driver-local packets into the shared smoke-and-test route."
        )
    )
    parser.add_argument("--root", type=Path, default=infer_repo_root())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_SCRIPTS_README_SUPPORT_BUNDLE=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_SCRIPTS_README_SUPPORT_BUNDLE=pass")
    print(f"PHASE12_SCRIPTS_README_SUPPORT_BUNDLE_MARKERS={len(EXPECTED_PHASE12_MARKERS)}")
    print(f"PHASE12_SCRIPTS_README_SUPPORT_BUNDLE_TOOLS={len(EXPECTED_SUPPORT_TOOLS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
