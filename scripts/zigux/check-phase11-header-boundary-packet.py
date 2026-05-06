#!/usr/bin/env python3
"""Check the bounded Phase 11 shared header-boundary packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


EXPECTED_LANE_KEY = "P11-L18"

REQUIRED_GAP_IDS = {
    "phase11-build-gate",
    "phase11-uapi-header-parity-survey-gate",
    "phase11-uapi-header-parity-note",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
}

REQUIRED_NOTE_MARKERS = [
    "PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored",
    f"lane: `{EXPECTED_LANE_KEY}`",
    "phase11-dw-wdt-watchdog-header-boundary",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
    "phase11-uapi-header-parity-surface",
    "notifier_hangup_irq",
]

REQUIRED_SURVEY_MARKERS = [
    "phase11 shared header parity survey manifest records the maintained packet cleanly",
    "phase11 shared header parity survey keeps a bounded watchdog_info layout proof",
    "phase11 shared header parity survey keeps a bounded winsize layout proof",
    "phase11 shared header parity survey keeps the note pinned to the manifest provenance",
    "phase11 shared header parity survey keeps shared replay markers explicit without a missing inventory fixture",
    "phase11 shared header parity survey keeps the exported hvc header declarations explicit",
    "phase11 shared header parity survey keeps the shared build hook explicit",
    "layout_assert.assertSize(WatchdogInfo, 40);",
    "layout_assert.assertSize(WinSize, 8);",
]

REQUIRED_BUILD_MARKERS = [
    "phase11_uapi_header_parity_survey.zig",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-hvc-console-survey-tests",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
    'phase11_uapi_header_parity_survey_module.addImport("layout_assert", layout_assert_module);',
]

REQUIRED_CONTRACT_MARKERS = [
    "PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "there is no broader multi-checker Phase 11 validator stack on `master`",
]

REQUIRED_HVC_CONSOLE_MARKERS = [
    "pub fn hvc_instantiate",
    "pub fn hvc_alloc",
    "pub fn hvc_remove",
    "pub fn hvc_poll",
    "pub fn hvc_kick",
    "pub fn __hvc_resize",
    "pub fn notifier_add_irq",
    "pub fn notifier_del_irq",
]

REQUIRED_HVC_HEADER_MARKERS = [
    "extern int hvc_instantiate(uint32_t vtermno, int index,",
    "extern struct hvc_struct * hvc_alloc(uint32_t vtermno, int data,",
    "extern void hvc_remove(struct hvc_struct *hp);",
    "int hvc_poll(struct hvc_struct *hp);",
    "void hvc_kick(void);",
    "extern void __hvc_resize(struct hvc_struct *hp, struct winsize ws);",
    "extern int notifier_add_irq(struct hvc_struct *hp, int data);",
    "extern void notifier_del_irq(struct hvc_struct *hp, int data);",
    "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);",
]

FIXTURE_SURVEYED_COMMIT = "fixture-phase11-shared-header-packet"


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{label} missing markers: {', '.join(missing)}")


def check_repo(root: Path) -> None:
    manifest = json.loads(read_text(root, "zigux/tests/phase11_uapi_header_parity_manifest.json"))
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        raise SystemExit("manifest lane_key mismatch")
    if manifest.get("phase") != "Phase 11":
        raise SystemExit("manifest phase mismatch")

    gap_ids = {gap["id"] for gap in manifest.get("gaps", [])}
    if gap_ids != REQUIRED_GAP_IDS:
        raise SystemExit(f"manifest gap ids mismatch: {sorted(gap_ids)}")

    note = read_text(root, "Documentation/zigux/phase11-uapi-header-parity-survey.md")
    survey = read_text(root, "zigux/tests/phase11_uapi_header_parity_survey.zig")
    build = read_text(root, "zigux/tests/phase11_build.zig")
    contract = read_text(root, "Documentation/zigux/phase11-shared-replay-contract.md")
    hvc_console = read_text(root, "drivers/tty/hvc/hvc_console.zig")
    hvc_header = read_text(root, "drivers/tty/hvc/hvc_console.h")

    require_markers(note, REQUIRED_NOTE_MARKERS + [manifest["surveyed_commit"]], "note")
    require_markers(survey, REQUIRED_SURVEY_MARKERS, "survey")
    require_markers(build, REQUIRED_BUILD_MARKERS, "build")
    require_markers(contract, REQUIRED_CONTRACT_MARKERS, "contract")
    require_markers(hvc_console, REQUIRED_HVC_CONSOLE_MARKERS, "hvc_console")
    require_markers(hvc_header, REQUIRED_HVC_HEADER_MARKERS, "hvc_header")


def build_fixture_repo(root: Path) -> None:
    manifest = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": "Phase 11",
        "surveyed_commit": FIXTURE_SURVEYED_COMMIT,
        "gaps": [{"id": gap_id} for gap_id in sorted(REQUIRED_GAP_IDS)],
    }
    write_text(
        root,
        "zigux/tests/phase11_uapi_header_parity_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-uapi-header-parity-survey.md",
        "\n".join(REQUIRED_NOTE_MARKERS + [FIXTURE_SURVEYED_COMMIT]) + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "\n".join(REQUIRED_SURVEY_MARKERS) + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_build.zig",
        "\n".join(REQUIRED_BUILD_MARKERS) + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-shared-replay-contract.md",
        "\n".join(REQUIRED_CONTRACT_MARKERS) + "\n",
    )
    write_text(
        root,
        "drivers/tty/hvc/hvc_console.zig",
        "\n".join(REQUIRED_HVC_CONSOLE_MARKERS) + "\n",
    )
    write_text(
        root,
        "drivers/tty/hvc/hvc_console.h",
        "\n".join(REQUIRED_HVC_HEADER_MARKERS) + "\n",
    )


def expect_failure(root: Path, rel: str, stale_marker: str, replacement: str, expected_fragment: str) -> None:
    path = root / rel
    original = path.read_text(encoding="utf-8")
    if stale_marker not in original:
        raise SystemExit(f"fixture is missing stale marker for {rel}: {stale_marker}")
    path.write_text(original.replace(stale_marker, replacement, 1), encoding="utf-8")
    try:
        check_repo(root)
    except SystemExit as exc:
        if expected_fragment not in str(exc):
            raise SystemExit(f"unexpected failure for {rel}: {exc}") from exc
    else:
        raise SystemExit(f"expected failure for {rel}")
    finally:
        path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11-header-packet-") as tmp:
        root = Path(tmp)
        build_fixture_repo(root)
        check_repo(root)
        expect_failure(
            root,
            "Documentation/zigux/phase11-uapi-header-parity-survey.md",
            "phase11-uapi-header-parity-surface",
            "phase11-uapi-header-packet-absent",
            "note missing markers",
        )
        expect_failure(
            root,
            "Documentation/zigux/phase11-shared-replay-contract.md",
            "zigux/tests/phase11_uapi_header_parity_survey.zig",
            "zigux/tests/phase11_header_packet_absent.zig",
            "contract missing markers",
        )
        expect_failure(
            root,
            "drivers/tty/hvc/hvc_console.h",
            "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);",
            "extern void notifier_hangup_irq(struct hvc_struct *hp, unsigned long data);",
            "hvc_header missing markers",
        )
    print("phase11-header-boundary-packet: self-test passed")
    print("phase11-header-boundary-packet: self-test cases=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.repo_root).resolve()
    check_repo(root)
    print("phase11-header-boundary-packet: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
