#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) >= 3 and _HERE.parent.name == "zigux" else _HERE.parent
SCRIPT_PATH = Path("scripts/zigux/check-phase11-active-review-prompt.py")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

ACTIVE_PHASE11_PROMPT = (
    "- if the change touches the active Phase 11 contributor packet, do "
    "`Documentation/zigux/phase11-shared-replay-contract.md`, "
    "`scripts/zigux/check-phase11-build-inventory.py`, "
    "`scripts/zigux/check-phase11-layout-assert-surface.py`, "
    "`scripts/zigux/check-phase11-hvc-validation-flow.py`, "
    "`scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, "
    "`scripts/zigux/check-phase11-shared-replay-contract.py`, "
    "`scripts/zigux/check-phase11-header-boundary-packet.py`, "
    "`zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, "
    "and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the "
    "pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the "
    "shared header-boundary packet aligned?"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_packet(root: Path) -> int:
    missing: list[str] = []

    review_checklist = text(root / REVIEW_CHECKLIST_PATH)
    if review_checklist.count(ACTIVE_PHASE11_PROMPT) != 1:
        missing.append(
            "review_checklist:active_phase11_prompt_count="
            f"{review_checklist.count(ACTIVE_PHASE11_PROMPT)}"
        )

    if missing:
        print("PHASE11_ACTIVE_REVIEW_PROMPT=fail")
        print("PHASE11_ACTIVE_REVIEW_PROMPT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_ACTIVE_REVIEW_PROMPT_MISSING_END")
        return 1

    print("PHASE11_ACTIVE_REVIEW_PROMPT=pass")
    print("PHASE11_ACTIVE_REVIEW_PROMPT_CHECKLIST_COUNT=1")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, result: subprocess.CompletedProcess[str], marker: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-active-review-prompt-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-active-review-prompt-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture_tree(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST_PATH, ACTIVE_PHASE11_PROMPT + "\n")
    write_text(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_active_review_prompt_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-active-review-prompt-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        review_checklist_path = tmp_root / REVIEW_CHECKLIST_PATH
        review_checklist_backup = text(review_checklist_path)
        write_text(review_checklist_path, "")
        expect_missing(
            "missing_checklist_prompt",
            run_checker(tmp_root),
            "review_checklist:active_phase11_prompt_count=0",
        )
        write_text(review_checklist_path, review_checklist_backup)

    print("PHASE11_ACTIVE_REVIEW_PROMPT_SELF_TEST=pass")
    print("PHASE11_ACTIVE_REVIEW_PROMPT_SELF_TEST_CASE_COUNT=1")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_packet(ROOT))
