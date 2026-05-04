#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[2]

REQUIRED_FILES = {
    "companion": "Documentation/zigux/phase3-tests-root-review-companion.md",
    "roadmap_gap": "Documentation/zigux/phase3-roadmap-gap-survey.md",
    "rbtree_survey": "Documentation/zigux/phase3-rbtree-interop-survey.md",
    "manifest": "zigux/tests/fixtures/phase3_abi_manifest.json",
}

COMPANION_MARKERS = [
    "PHASE3_TESTS_ROOT_PACKET=shared-abi-rbtree-lift-review-companion",
    "PHASE3_TESTS_ROOT_GUIDE=zigux/tests/README.md",
    "PHASE3_TESTS_ROOT_SURVEYS=Documentation/zigux/phase3-roadmap-gap-survey.md,Documentation/zigux/phase3-rbtree-interop-survey.md",
    "PHASE3_TESTS_ROOT_VALIDATOR=python3 scripts/zigux/check-phase3-tests-root-companion.py",
    "PHASE3_TESTS_ROOT_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/phase3_rbtree_shared_contract.zig,zigux/tests/fixtures/phase3_abi_manifest.json",
    "PHASE3_TESTS_ROOT_SHARED_STATUS=landed-shared-zigux_rbtree_root_view-lift-explicit",
    "PHASE3_TESTS_ROOT_NEXT_STEP=keep-this-companion-aligned-with-validate-phase3-and-the-shared-abi-manifest-without-reopening-shared-abi-growth",
]

ROADMAP_GAP_MARKERS = [
    "PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-and-shared-abi-root-view-lift-landed",
    "PHASE3_NEXT_BOUNDED_STEP=align-shared-phase3-survey-and-validator-wording-before-more-chrdev-growth",
]

RBTREE_SURVEY_MARKERS = [
    "PHASE3_RBTREE_PHASE3_BOUNDARY_STATUS=dedicated-boundary-and-shared-abi-root-view-lift-landed",
    "PHASE3_RBTREE_NEXT_BOUNDED_STEP=align-remaining-phase3-rbtree-survey-wording-with-landed-shared-rbtree-lift",
    "PHASE3_RBTREE_SHARED_CONTRACT_CHECK=scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
]

MANIFEST_MARKERS = [
    '"Documentation/zigux/phase3-tests-root-review-companion.md"',
    '"scripts/zigux/check-phase3-tests-root-companion.py"',
]


def resolve_root() -> Path:
    args = sys.argv[1:]
    if "--root" in args:
        index = args.index("--root")
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    env_root = os.environ.get("ZIGUX_PHASE3_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            issues.append(f"missing:{label}:{rel_path}")
    if issues:
        return issues

    companion = read_text(root, REQUIRED_FILES["companion"])
    roadmap_gap = read_text(root, REQUIRED_FILES["roadmap_gap"])
    rbtree_survey = read_text(root, REQUIRED_FILES["rbtree_survey"])
    manifest = read_text(root, REQUIRED_FILES["manifest"])

    for marker in COMPANION_MARKERS:
        if marker not in companion:
            issues.append(f"companion:{marker}")
    for marker in ROADMAP_GAP_MARKERS:
        if marker not in roadmap_gap:
            issues.append(f"roadmap_gap:{marker}")
    for marker in RBTREE_SURVEY_MARKERS:
        if marker not in rbtree_survey:
            issues.append(f"rbtree_survey:{marker}")
    for marker in MANIFEST_MARKERS:
        if marker not in manifest:
            issues.append(f"manifest:{marker}")

    return issues


def write_file(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clone_fixture_root(destination_root: Path) -> None:
    write_file(
        destination_root,
        "scripts/zigux/check-phase3-tests-root-companion.py",
        SCRIPT_PATH.read_text(encoding="utf-8"),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["companion"],
        "\n".join(COMPANION_MARKERS) + "\n",
    )
    write_file(
        destination_root,
        REQUIRED_FILES["roadmap_gap"],
        "\n".join(ROADMAP_GAP_MARKERS) + "\n",
    )
    write_file(
        destination_root,
        REQUIRED_FILES["rbtree_survey"],
        "\n".join(RBTREE_SURVEY_MARKERS) + "\n",
    )
    write_file(
        destination_root,
        REQUIRED_FILES["manifest"],
        '\n'.join(
            [
                "{",
                '  "files": [',
                '    "Documentation/zigux/phase3-tests-root-review-companion.md",',
                '    "scripts/zigux/check-phase3-tests-root-companion.py"',
                "  ]",
                "}",
                "",
            ]
        ),
    )


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase3-tests-root-companion.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase3-tests-root-companion-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase3-tests-root-companion-self-test:{label}:expected:{needle}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_tests_root_companion_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase3-tests-root-companion-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        companion_path = tmp_root / REQUIRED_FILES["companion"]
        original_companion = companion_path.read_text(encoding="utf-8")
        companion_path.write_text(
            original_companion.replace(
                "PHASE3_TESTS_ROOT_SHARED_STATUS=landed-shared-zigux_rbtree_root_view-lift-explicit\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "companion_shared_status",
            tmp_root,
            "companion:PHASE3_TESTS_ROOT_SHARED_STATUS=landed-shared-zigux_rbtree_root_view-lift-explicit",
        )
        companion_path.write_text(original_companion, encoding="utf-8")

        roadmap_gap_path = tmp_root / REQUIRED_FILES["roadmap_gap"]
        original_roadmap_gap = roadmap_gap_path.read_text(encoding="utf-8")
        roadmap_gap_path.write_text(
            original_roadmap_gap.replace(
                "PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-and-shared-abi-root-view-lift-landed\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "roadmap_gap_rbtree_status",
            tmp_root,
            "roadmap_gap:PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-and-shared-abi-root-view-lift-landed",
        )
        roadmap_gap_path.write_text(original_roadmap_gap, encoding="utf-8")

        manifest_path = tmp_root / REQUIRED_FILES["manifest"]
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace(
                '    "scripts/zigux/check-phase3-tests-root-companion.py"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "manifest_checker_entry",
            tmp_root,
            'manifest:"scripts/zigux/check-phase3-tests-root-companion.py"',
        )

    print("PHASE3_TESTS_ROOT_COMPANION_SELF_TEST=pass")
    print("PHASE3_TESTS_ROOT_COMPANION_SELF_TEST_CASE_COUNT=3")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print("PHASE3_TESTS_ROOT_COMPANION=fail")
    print("PHASE3_TESTS_ROOT_COMPANION_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE3_TESTS_ROOT_COMPANION_MISSING_END")
    raise SystemExit(1)

print("PHASE3_TESTS_ROOT_COMPANION=pass")
print(f"PHASE3_TESTS_ROOT_COMPANION_ROOT={ROOT}")
