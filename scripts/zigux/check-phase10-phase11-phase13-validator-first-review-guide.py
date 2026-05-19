#!/usr/bin/env python3
"""Guard the Phase 10/11/13 validator-first review guide against repo-drift."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


GUIDE_PATH = Path(
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"
)

REQUIRED_MARKERS = (
    "# Phase 10, 11, and 13 Validator-First Review Guide",
    "Keep `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` aligned with this note when they describe the same contributor-facing packets.",
    "- `make -C zigux phase10-validate`",
    "- `make -C zigux phase10-test`",
    "- `make -C zigux phase10`",
    "- `python3 scripts/zigux/check-phase11-build-inventory.py`",
    "- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "- `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "- `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "- `zigux/Makefile` is present on current `master`, but it still exposes no dedicated `make -C zigux phase11`, `make -C zigux phase11-validate`, or `make -C zigux phase11-contract` routes.",
    "- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "- `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
    "- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`.",
    "- `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` remain repo-reality gaps rather than shipped current-`master` evidence.",
)

FORBIDDEN_MARKERS = (
    "- `make -C zigux phase11-validate`",
    "- `make -C zigux phase11`",
    "- `python3 scripts/zigux/check-phase11-shared-replay-contract.py`",
    "- `python3 scripts/zigux/check-phase13-libfs-packet.py --self-test`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
    "- `zigux/tests/phase13_build.zig`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
)


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: Path, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    text = read_text(root, GUIDE_PATH)
    issues: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing_marker:{marker}")

    phase11_section = text.split("## Phase 11: Simple-driver packet", 1)[1].split(
        "## Phase 13: Shared-helper release packet", 1
    )[0]
    phase13_section = text.split("## Phase 13: Shared-helper release packet", 1)[1]

    for marker in FORBIDDEN_MARKERS[:4]:
        if marker in phase11_section:
            issues.append(f"forbidden_phase11_marker:{marker}")

    for marker in FORBIDDEN_MARKERS[4:]:
        if marker in phase13_section:
            issues.append(f"forbidden_phase13_marker:{marker}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE=fail")
    print("PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    content = "\n".join(REQUIRED_MARKERS[:2]) + "\n\n## Phase 10: Virtio lab packet\n"
    content += "\n".join(REQUIRED_MARKERS[2:5]) + "\n\n## Phase 11: Simple-driver packet\n"
    content += "\n".join(REQUIRED_MARKERS[5:11]) + "\n\n## Phase 13: Shared-helper release packet\n"
    content += "\n".join(REQUIRED_MARKERS[11:]) + "\n"
    write_text(root, GUIDE_PATH, content)


def expect_issue(issues: list[str], expected: str) -> None:
    assert expected in issues, f"missing expected issue: {expected}"


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase10-11-13-validator-guide-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        guide_path = tempdir / GUIDE_PATH
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(REQUIRED_MARKERS[5] + "\n", "", 1),
            encoding="utf-8",
        )
        expect_issue(collect_issues(tempdir), f"missing_marker:{REQUIRED_MARKERS[5]}")
        checks_run += 1

        populate_repo(tempdir)
        guide_path = tempdir / GUIDE_PATH
        phase13_heading = "\n## Phase 13: Shared-helper release packet\n"
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                phase13_heading,
                "\n- `make -C zigux phase11`\n" + phase13_heading,
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(collect_issues(tempdir), "forbidden_phase11_marker:- `make -C zigux phase11`")
        checks_run += 1

        populate_repo(tempdir)
        guide_path = tempdir / GUIDE_PATH
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(REQUIRED_MARKERS[13] + "\n", "", 1),
            encoding="utf-8",
        )
        expect_issue(collect_issues(tempdir), f"missing_marker:{REQUIRED_MARKERS[13]}")
        checks_run += 1

        populate_repo(tempdir)
        guide_path = tempdir / GUIDE_PATH
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8") + "\n- `make -C zigux phase13`\n",
            encoding="utf-8",
        )
        expect_issue(collect_issues(tempdir), "forbidden_phase13_marker:- `make -C zigux phase13`")
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE_SELF_TEST=pass")
    print(f"PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 10/11/13 validator-first review guide aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE=pass")
    print(f"PHASE10_PHASE11_PHASE13_VALIDATOR_FIRST_GUIDE_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
