#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC survey packet."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_hvc_console_manifest.json",
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "survey_note": "Documentation/zigux/phase11-hvc-console-survey.md",
    "slice_note": "Documentation/zigux/phase11-hvc-console-slice.md",
    "teardown_note": "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "validation_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "modem_control_split": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "poll_retry_split": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
    "makefile": "zigux/Makefile",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

SURVEY_GATE_MARKERS = [
    'test "phase11 hvc_console survey manifest records the landed starter and remaining tty gap cleanly"',
    'test "phase11 hvc console survey keeps the shared replay separate but exposes an explicit survey step"',
    "hvc_cleanup tty-port release handoff",
    "phase11_hvc_console_modem_control_split.zig",
    "phase11_hvc_console_poll_retry_split.zig",
]

SURVEY_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`",
    "* archival landing checkpoint:",
    "drivers/tty/hvc/hvc_console.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "make -C zigux phase11-hvc-survey",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "`hvc_cleanup()` tty-port release handoff summary",
    "`tiocmget` and `tiocmset` fallback coverage when `hv_ops` modem-control callbacks are absent",
    "sysrq handoff stays unavailable after teardown",
]

SLICE_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SLICE_STATUS=starter_packet_archived`",
    "lane: `P11-L16`",
    "drivers/tty/hvc/hvc_console.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "These archival packet surfaces keep the bounded starter's teardown and failure-mode story reviewable without claiming a missing compile-local verify helper or cleanup replay.",
]

SLICE_NOTE_FORBIDDEN_MARKERS = [
    "drivers/tty/hvc/hvc_console_verify.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
]

TEARDOWN_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`",
    "drivers/tty/hvc/hvc_console.zig",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "make -C zigux phase11-hvc-survey",
    "`hvc_cleanup()` tty-port release handoff",
    "wait-until-sent intent",
    "keep-IRQ-until-hangup teardown boundaries",
]

VALIDATION_MATRIX_MARKERS = [
    "`PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`",
    "- archival landing checkpoint:",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey` archival route fail-closed",
    "targetless notifier no-unregister edge",
    "cleanup tty-port release handoff",
    "notifier callback boundary",
    "`hvc_hangup()` disconnect boundary",
    "notifier_hangup boundary",
    "Current `master` still does not materialize direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, or `zigux/tests/phase11_hvc_cleanup.zig` companions, so keep those paths framed as repo-reality gaps rather than as shipped archival replay evidence.",
    "the shared Phase 11 reminder packet should treat missing direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions as repo-reality gaps instead of reading the archival HVC packet as a direct verify-and-replay pair",
]

MODEM_CONTROL_SPLIT_MARKERS = [
    'test "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks"',
    'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back"',
]

POLL_RETRY_SPLIT_MARKERS = [
    'test "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep"',
    'test "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries"',
    'test "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console"',
    'test "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes"',
    'test "phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state"',
    'test "phase11 hvc console keeps sysrq handoff unavailable after teardown"',
]

SYSRQ_HELPER_MARKERS = [
    "pub const SysrqHandoffRequest",
    "pub const SysrqHandoffSnapshot",
    "pub fn summarizeSysrqHandoff",
]

MAKEFILE_MARKERS = [
    "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
    "phase11-test:",
    "phase11-hvc-survey:",
    "phase11: phase11-contract phase11-test phase11-hvc-survey",
]

WORKFLOW_MARKERS = [
    "- name: Run Phase 11 shared replay contract checker",
    "run: make -C zigux phase11-contract",
    "- name: Run dedicated Phase 11 hvc survey replay",
    "run: make -C zigux phase11-hvc-survey",
]

SELF_TEST_CASE_COUNT = 10


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {relative_path}: {marker}")


def expect_forbidden_markers_absent(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            raise CheckError(f"forbidden marker present in {relative_path}: {marker}")


def is_hex_commit(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdef" for ch in value)
    )


def load_manifest(root: Path) -> dict[str, object]:
    manifest_text = read_text(root, REQUIRED_FILES["manifest"])
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {REQUIRED_FILES['manifest']}: {exc}") from exc
    surveyed_commit = manifest.get("surveyed_commit")
    if not is_hex_commit(surveyed_commit):
        raise CheckError(
            f"invalid surveyed_commit in {REQUIRED_FILES['manifest']}: {surveyed_commit!r}"
        )
    return manifest


def expect_git_commit_exists(root: Path, surveyed_commit: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", f"{surveyed_commit}^{{commit}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CheckError(
            f"missing git commit for surveyed_commit in {REQUIRED_FILES['manifest']}: {surveyed_commit}"
        )


def run_check(root: Path) -> None:
    manifest = load_manifest(root)
    expect_git_commit_exists(root, manifest["surveyed_commit"])

    survey_note = read_text(root, REQUIRED_FILES["survey_note"])
    validation_matrix = read_text(root, REQUIRED_FILES["validation_matrix"])
    if manifest["surveyed_commit"] not in survey_note:
        raise CheckError(
            f"missing surveyed_commit provenance in {REQUIRED_FILES['survey_note']}: {manifest['surveyed_commit']}"
        )
    if manifest["surveyed_commit"] not in validation_matrix:
        raise CheckError(
            f"missing surveyed_commit provenance in {REQUIRED_FILES['validation_matrix']}: {manifest['surveyed_commit']}"
        )

    expect_markers(REQUIRED_FILES["survey_gate"], read_text(root, REQUIRED_FILES["survey_gate"]), SURVEY_GATE_MARKERS)
    expect_markers(REQUIRED_FILES["survey_note"], survey_note, SURVEY_NOTE_MARKERS)

    slice_note = read_text(root, REQUIRED_FILES["slice_note"])
    expect_markers(REQUIRED_FILES["slice_note"], slice_note, SLICE_NOTE_MARKERS)
    expect_forbidden_markers_absent(REQUIRED_FILES["slice_note"], slice_note, SLICE_NOTE_FORBIDDEN_MARKERS)

    expect_markers(REQUIRED_FILES["teardown_note"], read_text(root, REQUIRED_FILES["teardown_note"]), TEARDOWN_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["validation_matrix"], validation_matrix, VALIDATION_MATRIX_MARKERS)
    expect_markers(REQUIRED_FILES["modem_control_split"], read_text(root, REQUIRED_FILES["modem_control_split"]), MODEM_CONTROL_SPLIT_MARKERS)
    expect_markers(REQUIRED_FILES["poll_retry_split"], read_text(root, REQUIRED_FILES["poll_retry_split"]), POLL_RETRY_SPLIT_MARKERS)
    expect_markers(REQUIRED_FILES["sysrq_helper"], read_text(root, REQUIRED_FILES["sysrq_helper"]), SYSRQ_HELPER_MARKERS)
    expect_markers(REQUIRED_FILES["makefile"], read_text(root, REQUIRED_FILES["makefile"]), MAKEFILE_MARKERS)
    expect_markers(REQUIRED_FILES["workflow"], read_text(root, REQUIRED_FILES["workflow"]), WORKFLOW_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_manifest_text(surveyed_commit: str) -> str:
    manifest = {
        "lane_key": "P11-L16",
        "phase": "Phase 11",
        "surveyed_commit": surveyed_commit,
        "anchor": "drivers/tty/hvc/hvc_console.c",
    }
    return json.dumps(manifest, indent=2) + "\n"


def build_fixture(root: Path, surveyed_commit: str) -> None:
    write(root / REQUIRED_FILES["manifest"], build_manifest_text(surveyed_commit))
    write(root / REQUIRED_FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS + [surveyed_commit]) + "\n")
    write(root / REQUIRED_FILES["slice_note"], "\n".join(SLICE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["teardown_note"], "\n".join(TEARDOWN_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validation_matrix"], "\n".join(VALIDATION_MATRIX_MARKERS + [surveyed_commit]) + "\n")
    write(root / REQUIRED_FILES["modem_control_split"], "\n".join(MODEM_CONTROL_SPLIT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["poll_retry_split"], "\n".join(POLL_RETRY_SPLIT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["sysrq_helper"], "\n".join(SYSRQ_HELPER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["makefile"], "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["workflow"], "\n".join(WORKFLOW_MARKERS) + "\n")


def init_fixture_repo(root: Path) -> str:
    subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Zigux Builder"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "zigux-builder@example.com"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "commit", "-m", "fixture"], check=True, capture_output=True, text=True)
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def reset_fixture(root: Path) -> str:
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    build_fixture(root, "0" * 40)
    commit = init_fixture_repo(root)
    build_fixture(root, commit)
    return commit


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_packet_"))
    try:
        commit = reset_fixture(tmpdir)
        run_check(tmpdir)

        cases = [
            (REQUIRED_FILES["validation_matrix"], "zigux/tests/phase11_hvc_cleanup.zig"),
            (REQUIRED_FILES["validation_matrix"], "direct verify-and-replay pair"),
            (REQUIRED_FILES["slice_note"], "drivers/tty/hvc/hvc_console_sysrq.zig"),
            (REQUIRED_FILES["teardown_note"], "wait-until-sent intent"),
            (REQUIRED_FILES["poll_retry_split"], 'test "phase11 hvc console keeps sysrq handoff unavailable after teardown"'),
            (REQUIRED_FILES["modem_control_split"], 'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back"'),
            (REQUIRED_FILES["makefile"], "phase11-hvc-survey:"),
            (REQUIRED_FILES["workflow"], "run: make -C zigux phase11-hvc-survey"),
        ]
        for idx, (relative_path, marker) in enumerate(cases, start=1):
            reset_fixture(tmpdir)
            path = tmpdir / relative_path
            text = path.read_text(encoding="utf-8")
            if marker + "\n" in text:
                text = text.replace(marker + "\n", "", 1)
            else:
                text = text.replace(marker, "", 1)
            path.write_text(text, encoding="utf-8")
            expect_failure(tmpdir, marker)

        reset_fixture(tmpdir)
        path = tmpdir / REQUIRED_FILES["slice_note"]
        path.write_text(path.read_text(encoding="utf-8") + "zigux/tests/phase11_hvc_cleanup.zig\n", encoding="utf-8")
        expect_failure(tmpdir, "zigux/tests/phase11_hvc_cleanup.zig")

        reset_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["manifest"]).write_text(build_manifest_text("z" * 40), encoding="utf-8")
        expect_failure(tmpdir, "invalid surveyed_commit")

        reset_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["manifest"]).unlink()
        expect_failure(tmpdir, REQUIRED_FILES["manifest"])

        print("PHASE11_HVC_SURVEY_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
        print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_COMMIT={commit}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_HVC_SURVEY_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_SURVEY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
