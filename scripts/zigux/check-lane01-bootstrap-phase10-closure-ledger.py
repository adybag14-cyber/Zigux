#!/usr/bin/env python3
"""Guard the current Phase 10 closure ledger packet in zigux-alpha/."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

LEDGER_REL = Path("zigux-alpha/PHASE10_CLOSURE_LEDGER.md")

REQUIRED_LINES = [
    "# Phase 10 Closure Ledger",
    "This focused ledger records the current closure-evidence bundle for the active Phase 10 virtio tranche.",
    "- `PHASE10_LEDGER_STATUS=active`",
    "- `PHASE10_LEDGER_TRANCHE=virtio-lab-bundle`",
    "- `PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle`",
    "- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`",
    "- `PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py`",
    "- `PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`",
    "- `PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`",
    "- `PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_shared_phase10_surfaces_drift_again_around_the_manifest_backed_packet_and_reopen_P10-L06_only_if_a_fresh_shared_reminder_reread_proves_new_drift`",
    "- `PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths`",
    "This ledger stays intentionally narrow.",
    "The current exact replay packet is the manifest-backed shared closure route: `check-phase10-bootstrap-route.py`, `check-phase10-shared-freeze-boundary.py`, `check-phase10-ring-packet.py`, `check-phase10-input-packet.py`, `check-phase10-mmio-packet.py`, `check-phase10-harness-coverage.py`, `check-phase10-tests-readme-core-surfaces.py`, `validate-phase10.py`, `validate-phase10-closure.py`, `make -C zigux phase10-validate`, `zig build test --build-file zigux/tests/phase10_build.zig --summary all`, `make -C zigux phase10-test`, and `make -C zigux phase10`.",
]

REQUIRED_EXACT_CHECK_LINES = [
    "- `PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-bootstrap-route.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/check-phase10-shared-freeze-boundary.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/check-phase10-ring-packet.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-input-packet.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/check-phase10-mmio-packet.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_6=python3 scripts/zigux/check-phase10-harness-coverage.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_7=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/validate-phase10.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/validate-phase10-closure.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_10=make -C zigux phase10-validate`",
    "- `PHASE10_LEDGER_EXACT_CHECK_11=zig build test --build-file zigux/tests/phase10_build.zig --summary all`",
    "- `PHASE10_LEDGER_EXACT_CHECK_12=make -C zigux phase10-test`",
    "- `PHASE10_LEDGER_EXACT_CHECK_13=make -C zigux phase10`",
]

REQUIRED_PARAGRAPHS = [
    "It records the roadmap-backed closure packet and the current parked-next-step posture without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity. The roadmap-facing scoreboard is mirrored here from the shared closure manifest so the closure packet can be compared directly against the Phase 10 roadmap requirements without hopping between survey notes.",
    "That shared scoreboard still reads `starter_landed` for virtqueue wrappers, MMIO wrappers, and lab-only validation, while risky dual implementations remain `blocked_on_risky_transport` until a smaller transport-facing helper lane is ready.",
    "The narrower current-head repo-reality gap inside this ledger is the still-missing `scripts/zigux/check-phase10-core-packet.py` marker, so keep the core packet governed through the returned closure manifest, the returned `zigux/tests/phase10_virtio_core.zig` replay, the direct core survey note, and the shared tests-root core-surface guard rather than promoting a missing dedicated core checker back into current-head evidence.",
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    if not (root / LEDGER_REL).is_file():
        return [str(LEDGER_REL)]
    return []


def collect_issues(root: Path) -> list[str]:
    text = read_text(root, LEDGER_REL)
    issues: list[str] = []

    for line in REQUIRED_LINES:
        if line not in text:
            issues.append(f"missing_line:{line}")

    for line in REQUIRED_EXACT_CHECK_LINES:
        if line not in text:
            issues.append(f"missing_exact_check:{line}")

    for paragraph in REQUIRED_PARAGRAPHS:
        if paragraph not in text:
            issues.append(f"missing_paragraph:{paragraph}")

    if text.count("PHASE10_LEDGER_EXACT_CHECK_") != len(REQUIRED_EXACT_CHECK_LINES):
        issues.append("unexpected_exact_check_count")

    next_step_idx = text.find("PHASE10_LEDGER_NEXT_STEP=")
    blockers_idx = text.find("PHASE10_LEDGER_BLOCKERS=")
    narrow_idx = text.find("This ledger stays intentionally narrow.")
    if next_step_idx == -1 or blockers_idx == -1 or narrow_idx == -1 or not (next_step_idx < blockers_idx < narrow_idx):
        issues.append("reordered_next_step_blockers_closure_note")

    return issues


def make_fixture_text() -> str:
    return "\n".join(
        [
            REQUIRED_LINES[0],
            "",
            REQUIRED_LINES[1],
            "",
            *REQUIRED_LINES[2:11],
            *REQUIRED_EXACT_CHECK_LINES,
            "",
            REQUIRED_LINES[11],
            "",
            *REQUIRED_PARAGRAPHS,
            REQUIRED_LINES[12],
        ]
    ) + "\n"


def make_fixture_root(root: Path) -> None:
    write_text(root, LEDGER_REL, make_fixture_text())


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane01_phase10_ledger_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)

        assert collect_missing_files(root) == []
        assert collect_issues(root) == []
        case_count += 1

        (root / LEDGER_REL).unlink()
        assert str(LEDGER_REL) in collect_missing_files(root)
        case_count += 1
        make_fixture_root(root)

        ledger_path = root / LEDGER_REL
        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_LINES[2] + "\n", "", 1), encoding="utf-8")
        assert any(issue.startswith("missing_line:") for issue in collect_issues(root))
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_EXACT_CHECK_LINES[-1] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue.startswith("missing_exact_check:") for issue in issues)
        assert "unexpected_exact_check_count" in issues
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_PARAGRAPHS[1], "drifted paragraph", 1), encoding="utf-8")
        assert any(issue.startswith("missing_paragraph:") for issue in collect_issues(root))
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        reordered = text.replace(
            REQUIRED_LINES[9] + "\n" + REQUIRED_LINES[10],
            REQUIRED_LINES[10] + "\n" + REQUIRED_LINES[9],
            1,
        )
        ledger_path.write_text(reordered, encoding="utf-8")
        assert "reordered_next_step_blockers_closure_note" in collect_issues(root)
        case_count += 1

    print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_SELF_TEST_CASES={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Lane 01 Phase 10 closure ledger packet.")
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER=fail")
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_MISSING_FILES_START")
        for item in missing_files:
            print(item)
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_MISSING_FILES_END")
        return 1

    issues = collect_issues(root)
    if issues:
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER=fail")
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_ISSUES_START")
        for item in issues:
            print(item)
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER=pass")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_EXACT_CHECK_COUNT={len(REQUIRED_EXACT_CHECK_LINES)}")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_PARAGRAPH_COUNT={len(REQUIRED_PARAGRAPHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
