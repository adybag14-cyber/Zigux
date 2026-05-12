#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SCRIPTS_README = "scripts/zigux/README.md"
RELEASE_READINESS = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE = "Documentation/zigux/phase12-release-closure-checklist.md"
VERIFY_NOTE = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
VALIDATOR = "scripts/zigux/validate-phase12.py"
CHECKER = "scripts/zigux/check-build-only-phase12-surface.py"
VIRTIO_NET_DRIVER = "drivers/net/virtio_net.zig"
VIRTIO_NET_TEST = "zigux/tests/phase12_virtio_net.zig"
VIRTIO_NET_SYNTAX = "zigux/tests/phase12_virtio_net_syntax_lab.zig"
VIRTIO_NET_MANIFEST = "zigux/tests/phase12_virtio_net_manifest.json"
VIRTIO_NET_SURVEY = "zigux/tests/phase12_virtio_net_survey.zig"

REQUIRED_FILES = (
    SCRIPTS_README,
    RELEASE_READINESS,
    RELEASE_SEQUENCING,
    RELEASE_CLOSURE,
    VERIFY_NOTE,
    VALIDATOR,
    CHECKER,
    VIRTIO_NET_DRIVER,
    VIRTIO_NET_TEST,
    VIRTIO_NET_SYNTAX,
    VIRTIO_NET_MANIFEST,
    VIRTIO_NET_SURVEY,
)

README_REQUIRED_MARKERS = (
    "`scripts/zigux/validate-phase12.py`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`drivers/net/virtio_net.zig`",
    "`zigux/tests/phase12_virtio_net.zig`",
    "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
    "`zigux/tests/phase12_virtio_net_manifest.json`",
    "`zigux/tests/phase12_virtio_net_survey.zig`",
    "starter-present `virtio_net`",
    "unwired helper",
)

README_FORBIDDEN_MARKERS = (
    "`Documentation/zigux/phase12-nvme-pci-slice.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
    "survey-only `virtio_net` boundary",
    "absent direct `phase12_virtio_net`",
)

READINESS_MARKERS = (
    "`scripts/zigux/validate-phase12.py` as an unwired helper",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "starter-present `virtio_net`",
)

SEQUENCING_MARKERS = (
    "`scripts/zigux/validate-phase12.py` exists as an unwired helper",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "starter-present `virtio_net`",
)

CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase12.py` now exists as an unwired helper",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "starter-present `virtio_net`",
    "scripts-root sync",
)

VERIFY_NOTE_MARKERS = (
    "current `master` now exposes the verify, manifest, reviewability, and survey-gate source files again",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
)


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(failures: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:missing:{marker}")


def forbid_markers(failures: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker in text:
            failures.append(f"{label}:forbidden:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    require_markers(failures, "scripts_readme", read_text(root, SCRIPTS_README), README_REQUIRED_MARKERS)
    forbid_markers(failures, "scripts_readme", read_text(root, SCRIPTS_README), README_FORBIDDEN_MARKERS)
    require_markers(failures, "release_readiness", read_text(root, RELEASE_READINESS), READINESS_MARKERS)
    require_markers(failures, "release_sequencing", read_text(root, RELEASE_SEQUENCING), SEQUENCING_MARKERS)
    require_markers(failures, "release_closure", read_text(root, RELEASE_CLOSURE), CLOSURE_MARKERS)
    require_markers(failures, "verify_note", read_text(root, VERIFY_NOTE), VERIFY_NOTE_MARKERS)
    return failures


def seed_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    placeholder = "// fixture\n"
    for rel in REQUIRED_FILES:
        content = placeholder
        if rel == SCRIPTS_README:
            content = "\n".join(
                [
                    "# scripts/zigux",
                    "",
                    *README_REQUIRED_MARKERS,
                    "",
                ]
            )
        elif rel == RELEASE_READINESS:
            content = "\n".join(["# Phase 12 Release Readiness Survey", "", *READINESS_MARKERS, ""])
        elif rel == RELEASE_SEQUENCING:
            content = "\n".join(["# Phase 12 Release Sequencing", "", *SEQUENCING_MARKERS, ""])
        elif rel == RELEASE_CLOSURE:
            content = "\n".join(["# Phase 12 Release Closure Checklist", "", *CLOSURE_MARKERS, ""])
        elif rel == VERIFY_NOTE:
            content = "\n".join(["# Phase 12 Libbpf Verify Shard Note", "", *VERIFY_NOTE_MARKERS, ""])
        elif rel in (VALIDATOR, CHECKER):
            content = "#!/usr/bin/env python3\n"
        elif rel.endswith(".json"):
            content = "{}\n"
        write_text(root / rel, content)


def expect_exact_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if failures != [expected]:
        raise SystemExit(f"expected {expected!r}, got {failures!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12_scripts_readme_alignment_"))
    try:
        seed_fixture_tree(tmp_root)
        baseline_failures = validate(tmp_root)
        if baseline_failures:
            raise SystemExit(f"baseline fixture failed: {baseline_failures!r}")

        readme_path = tmp_root / SCRIPTS_README
        original_readme = read_text(tmp_root, SCRIPTS_README)
        readme_path.write_text(
            original_readme.replace("`scripts/zigux/validate-phase12.py`\n", "", 1),
            encoding="utf-8",
        )
        expect_exact_failure(
            tmp_root,
            "scripts_readme:missing:`scripts/zigux/validate-phase12.py`",
        )

        seed_fixture_tree(tmp_root)
        readme_path.write_text(
            read_text(tmp_root, SCRIPTS_README) + "\n`Documentation/zigux/phase12-nvme-pci-slice.md`\n",
            encoding="utf-8",
        )
        expect_exact_failure(
            tmp_root,
            "scripts_readme:forbidden:`Documentation/zigux/phase12-nvme-pci-slice.md`",
        )

        seed_fixture_tree(tmp_root)
        readme_path.write_text(
            read_text(tmp_root, SCRIPTS_README).replace("`zigux/tests/phase12_virtio_net.zig`\n", "", 1),
            encoding="utf-8",
        )
        expect_exact_failure(
            tmp_root,
            "scripts_readme:missing:`zigux/tests/phase12_virtio_net.zig`",
        )

        seed_fixture_tree(tmp_root)
        readiness_path = tmp_root / RELEASE_READINESS
        readiness_path.write_text(
            read_text(tmp_root, RELEASE_READINESS).replace(
                "`scripts/zigux/validate-phase12.py` as an unwired helper\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_exact_failure(
            tmp_root,
            "release_readiness:missing:`scripts/zigux/validate-phase12.py` as an unwired helper",
        )

        seed_fixture_tree(tmp_root)
        verify_path = tmp_root / VERIFY_NOTE
        verify_path.write_text(
            read_text(tmp_root, VERIFY_NOTE).replace(
                "current `master` now exposes the verify, manifest, reviewability, and survey-gate source files again\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_exact_failure(
            tmp_root,
            "verify_note:missing:current `master` now exposes the verify, manifest, reviewability, and survey-gate source files again",
        )

        seed_fixture_tree(tmp_root)
        (tmp_root / VALIDATOR).unlink()
        expect_exact_failure(tmp_root, f"missing_file:{VALIDATOR}")

        print("PHASE12_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
        print("PHASE12_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that scripts/zigux/README.md keeps the active Phase 12 "
            "starter-present virtio_net packet, parked libbpf verify-shard note, "
            "and unwired validate-phase12 helper aligned with the shared release notes."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-test cases.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_SCRIPTS_README_ALIGNMENT=fail")
        print("PHASE12_SCRIPTS_README_ALIGNMENT_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_SCRIPTS_README_ALIGNMENT_FAILURES_END")
        return 1

    marker_count = (
        len(REQUIRED_FILES)
        + len(README_REQUIRED_MARKERS)
        + len(README_FORBIDDEN_MARKERS)
        + len(READINESS_MARKERS)
        + len(SEQUENCING_MARKERS)
        + len(CLOSURE_MARKERS)
        + len(VERIFY_NOTE_MARKERS)
    )
    print("PHASE12_SCRIPTS_README_ALIGNMENT=pass")
    print(f"PHASE12_SCRIPTS_README_ALIGNMENT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
