#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC teardown packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileExpectation:
    relative_path: str
    required_fragments: tuple[str, ...]


@dataclass(frozen=True)
class InventoryMarkerExpectation:
    path: str
    marker: str


REQUIRED_PACKET_FILES = (
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-slice.md",
    "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
)

FILE_EXPECTATIONS = (
    FileExpectation(
        "Documentation/zigux/phase11-hvc-console-survey.md",
        (
            "hvc_cleanup() tty-port release handoff summary",
            "hvc_hangup() disconnect summary",
            "hvc_remove() handoff summary",
            "zigux/tests/phase11_hvc_cleanup.zig",
            "drivers/tty/hvc/hvc_console_verify.zig",
        ),
    ),
    FileExpectation(
        "Documentation/zigux/phase11-hvc-console-slice.md",
        (
            "hvc_cleanup() tty-port release handoff summary",
            "cleanup-time tty-port ownership",
            "targetless notifier no-unregister edge",
        ),
    ),
    FileExpectation(
        "Documentation/zigux/phase11-hvc-console-teardown-note.md",
        (
            "hvc_cleanup() tty-port release handoff",
            "cleanup-time tty-port ownership",
            "hvc_hangup() disconnect",
            "hvc_remove() slot-release and handoff ordering",
            "direct verify, replay, and cleanup companion surfaces",
        ),
    ),
    FileExpectation(
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        (
            "hvc_cleanup() tty-port release handoff",
            "cleanup-time tty-port ownership",
            "hvc_hangup() disconnect summary",
            "hvc_remove() handoff summary",
            "direct replay and cleanup surfaces explicit",
            "modem-control split",
            "poll-retry split",
            "shared build inventory",
        ),
    ),
    FileExpectation(
        "drivers/tty/hvc/hvc_console_sysrq.zig",
        (
            "pub fn summarizeSysrqHandoff",
            "keeps_live_sysrq_execution_out_of_scope",
        ),
    ),
    FileExpectation(
        "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        (
            "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks",
            "phase11 hvc console keeps tiocmset masks live when tiocmget falls back",
        ),
    ),
    FileExpectation(
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        (
            "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep",
            "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes",
            "phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state",
            "phase11 hvc console keeps sysrq handoff unavailable after teardown",
        ),
    ),
)

INVENTORY_REQUIRED_BUILD_TESTS = (
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
)

INVENTORY_REQUIRED_MODULE_PATHS = {
    "hvc_console_module": "../../drivers/tty/hvc/hvc_console.zig",
    "hvc_console_verify_module": "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_console_module": "phase11_hvc_console.zig",
    "phase11_hvc_cleanup_module": "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey_module": "phase11_hvc_console_survey.zig",
}

INVENTORY_REQUIRED_MARKERS = (
    InventoryMarkerExpectation(
        "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        "try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    ),
    InventoryMarkerExpectation(
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        "try std.testing.expect(dispatch.invokes_sysrq_handler);",
    ),
)


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {relative_path}") from exc


def require_fragments(root: Path) -> None:
    for expectation in FILE_EXPECTATIONS:
        text = read_text(root, expectation.relative_path)
        for fragment in expectation.required_fragments:
            if fragment not in text:
                raise ValidationError(
                    f"{expectation.relative_path} is missing required fragment: {fragment!r}"
                )


def require_manifest(root: Path) -> None:
    manifest_text = read_text(root, "zigux/tests/phase11_hvc_console_manifest.json")
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            "zigux/tests/phase11_hvc_console_manifest.json is not valid JSON"
        ) from exc

    anchor = manifest.get("anchor")
    if anchor != "drivers/tty/hvc/hvc_console.c":
        raise ValidationError(
            "phase11_hvc_console_manifest.json must stay anchored to drivers/tty/hvc/hvc_console.c"
        )

    destinations = set(manifest.get("roadmap_destinations", ()))
    missing_destinations = {
        "drivers/tty/hvc/hvc_console.zig",
        "drivers/tty/hvc/hvc_console_sysrq.zig",
        "zigux/tests/phase11_hvc_console_survey.zig",
    } - destinations
    if missing_destinations:
        missing_list = ", ".join(sorted(missing_destinations))
        raise ValidationError(
            f"phase11_hvc_console_manifest.json is missing roadmap destinations: {missing_list}"
        )

    survey_summary = manifest.get("survey_summary", {})
    required_true_flags = (
        "hvc_console_zig_present",
        "hvc_console_sysrq_present",
        "hvc_console_test_present",
        "hvc_console_survey_gate_present",
        "hvc_console_survey_note_present",
        "hvc_console_modem_control_split_present",
        "hvc_console_poll_retry_split_present",
    )
    for flag in required_true_flags:
        if survey_summary.get(flag) is not True:
            raise ValidationError(
                f"phase11_hvc_console_manifest.json must keep survey_summary[{flag!r}] true"
            )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise ValidationError("phase11_hvc_console_manifest.json must keep gaps as a JSON array")

    gap_ids = {entry.get("id") for entry in gaps if isinstance(entry, dict)}
    required_gap_ids = {
        "phase11-hvc-console-survey-gate",
        "phase11-hvc-console-survey-note",
        "phase11-hvc-console-driver-starter",
        "phase11-hvc-console-close-teardown",
        "phase11-hvc-console-notifier-add-handoff",
        "phase11-hvc-console-khvcd-sleep-handoff",
        "phase11-hvc-console-hangup-disconnect",
        "phase11-hvc-console-remove-handoff",
        "phase11-hvc-console-header-parity",
        "phase11-hvc-console-winsize-layout-assert",
        "phase11-hvc-console-hv-ops-layout-assert",
        "phase11-hvc-console-hv-ops-signature-assert",
        "phase11-hvc-console-validation-matrix",
        "phase11-hvc-console-tty-and-teardown-parity",
    }
    missing_gap_ids = sorted(required_gap_ids - gap_ids)
    if missing_gap_ids:
        raise ValidationError(
            "phase11_hvc_console_manifest.json is missing teardown-facing gaps: "
            + ", ".join(missing_gap_ids)
        )

    cleanup_gap = None
    for entry in gaps:
        if not isinstance(entry, dict):
            continue
        why_now = entry.get("why_now")
        if isinstance(why_now, str) and "hvc_cleanup tty-port release handoff" in why_now:
            cleanup_gap = entry
            break
    if cleanup_gap is None:
        raise ValidationError(
            "phase11_hvc_console_manifest.json must keep one teardown-facing gap that names the "
            "hvc_cleanup tty-port release handoff"
        )

    cleanup_status = cleanup_gap.get("status")
    if cleanup_status != "starter_landed":
        raise ValidationError(
            "the manifest gap naming the hvc_cleanup tty-port release handoff must remain starter_landed"
        )


def require_inventory(root: Path) -> None:
    inventory_text = read_text(root, "zigux/tests/fixtures/phase11_build_inventory.json")
    try:
        inventory = json.loads(inventory_text)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            "zigux/tests/fixtures/phase11_build_inventory.json is not valid JSON"
        ) from exc

    build_test_names = set(inventory.get("build_test_names", ()))
    missing_build_tests = sorted(set(INVENTORY_REQUIRED_BUILD_TESTS) - build_test_names)
    if missing_build_tests:
        raise ValidationError(
            "phase11_build_inventory.json is missing build_test_names: "
            + ", ".join(missing_build_tests)
        )

    module_paths = {
        entry.get("module"): entry.get("path")
        for entry in inventory.get("module_root_source_files", ())
        if isinstance(entry, dict)
    }
    for module, path in INVENTORY_REQUIRED_MODULE_PATHS.items():
        if module_paths.get(module) != path:
            raise ValidationError(
                f"phase11_build_inventory.json must map module {module!r} to {path!r}"
            )

    dedicated_replays = set(inventory.get("dedicated_survey_replays", ()))
    if "zigux/tests/phase11_hvc_console_survey.zig" not in dedicated_replays:
        raise ValidationError(
            "phase11_build_inventory.json must keep zigux/tests/phase11_hvc_console_survey.zig "
            "inside dedicated_survey_replays"
        )

    shared_adjunct_replays = set(inventory.get("shared_adjunct_replays", ()))
    required_adjuncts = {
        "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
        "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    }
    missing_adjuncts = sorted(required_adjuncts - shared_adjunct_replays)
    if missing_adjuncts:
        raise ValidationError(
            "phase11_build_inventory.json is missing shared_adjunct_replays: "
            + ", ".join(missing_adjuncts)
        )

    shared_markers = {
        (entry.get("path"), entry.get("marker"))
        for entry in inventory.get("shared_replay_markers", ())
        if isinstance(entry, dict)
    }
    for expectation in INVENTORY_REQUIRED_MARKERS:
        key = (expectation.path, expectation.marker)
        if key not in shared_markers:
            raise ValidationError(
                "phase11_build_inventory.json is missing shared_replay_marker for "
                f"{expectation.path!r}"
            )


def require_packet_files(root: Path) -> None:
    missing = [path for path in REQUIRED_PACKET_FILES if not (root / path).is_file()]
    if missing:
        raise ValidationError(
            "missing required Phase 11 HVC teardown packet files: " + ", ".join(missing)
        )


def validate(root: Path) -> None:
    require_packet_files(root)
    require_fragments(root)
    require_manifest(root)
    require_inventory(root)


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> None:
    for relative_path in REQUIRED_PACKET_FILES:
        write_text(root, relative_path, "placeholder\n")

    write_text(
        root,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        "\n".join(
            (
                "# survey",
                "hvc_cleanup() tty-port release handoff summary",
                "hvc_hangup() disconnect summary",
                "hvc_remove() handoff summary",
                "zigux/tests/phase11_hvc_cleanup.zig",
                "drivers/tty/hvc/hvc_console_verify.zig",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-hvc-console-slice.md",
        "\n".join(
            (
                "# slice",
                "hvc_cleanup() tty-port release handoff summary",
                "cleanup-time tty-port ownership",
                "targetless notifier no-unregister edge",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-hvc-console-teardown-note.md",
        "\n".join(
            (
                "# teardown",
                "hvc_cleanup() tty-port release handoff",
                "cleanup-time tty-port ownership",
                "hvc_hangup() disconnect",
                "hvc_remove() slot-release and handoff ordering",
                "direct verify, replay, and cleanup companion surfaces",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        "\n".join(
            (
                "# matrix",
                "hvc_cleanup() tty-port release handoff",
                "cleanup-time tty-port ownership",
                "hvc_hangup() disconnect summary",
                "hvc_remove() handoff summary",
                "direct replay and cleanup surfaces explicit",
                "modem-control split",
                "poll-retry split",
                "shared build inventory",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "drivers/tty/hvc/hvc_console_sysrq.zig",
        "\n".join(
            (
                "pub fn summarizeSysrqHandoff() void {}",
                "const keeps_live_sysrq_execution_out_of_scope = true;",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        "\n".join(
            (
                "test \"phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks\" {}",
                "test \"phase11 hvc console keeps tiocmset masks live when tiocmget falls back\" {}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        "\n".join(
            (
                "test \"phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep\" {}",
                "test \"phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes\" {}",
                "test \"phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state\" {}",
                "test \"phase11 hvc console keeps sysrq handoff unavailable after teardown\" {}",
            )
        )
        + "\n",
    )

    manifest = {
        "anchor": "drivers/tty/hvc/hvc_console.c",
        "roadmap_destinations": [
            "drivers/tty/hvc/hvc_console.zig",
            "drivers/tty/hvc/hvc_console_sysrq.zig",
            "zigux/tests/phase11_hvc_console_survey.zig",
        ],
        "survey_summary": {
            "hvc_console_zig_present": True,
            "hvc_console_sysrq_present": True,
            "hvc_console_test_present": True,
            "hvc_console_survey_gate_present": True,
            "hvc_console_survey_note_present": True,
            "hvc_console_modem_control_split_present": True,
            "hvc_console_poll_retry_split_present": True,
        },
        "gaps": [
            {
                "id": "phase11-hvc-console-close-teardown",
                "status": "starter_landed",
                "why_now": "Record close teardown ordering.",
            },
            {
                "id": "phase11-hvc-console-notifier-add-handoff",
                "status": "starter_landed",
                "why_now": "Record notifier add handoff.",
            },
            {
                "id": "phase11-hvc-console-hangup-disconnect",
                "status": "starter_landed",
                "why_now": "Record hangup disconnect ordering.",
            },
            {
                "id": "phase11-hvc-console-remove-handoff",
                "status": "starter_landed",
                "why_now": "Record remove handoff ordering.",
            },
            {
                "id": "phase11-hvc-console-validation-matrix",
                "status": "starter_landed",
                "why_now": "Record validation matrix coverage.",
            },
            {
                "id": "phase11-hvc-console-cleanup-handoff",
                "status": "starter_landed",
                "why_now": (
                    "Keep the hvc_cleanup tty-port release handoff, cleanup-time tty-port "
                    "ownership, and direct cleanup companion surface explicit."
                ),
            },
            {
                "id": "phase11-hvc-console-survey-gate",
                "status": "starter_landed",
                "why_now": "Keep the final-close teardown handoff visible through one bounded survey gate.",
            },
            {
                "id": "phase11-hvc-console-survey-note",
                "status": "starter_landed",
                "why_now": "Keep the final-close teardown summary aligned with the parked starter.",
            },
            {
                "id": "phase11-hvc-console-driver-starter",
                "status": "starter_landed",
                "why_now": "Keep the driver starter honest about teardown and cleanup summaries.",
            },
            {
                "id": "phase11-hvc-console-khvcd-sleep-handoff",
                "status": "starter_landed",
                "why_now": "Keep pre-sleep kick check and guard-tick timed sleep explicit.",
            },
            {
                "id": "phase11-hvc-console-header-parity",
                "status": "starter_landed",
                "why_now": "Keep hv_ops and notifier-IRQ helper surface reviewable.",
            },
            {
                "id": "phase11-hvc-console-winsize-layout-assert",
                "status": "starter_landed",
                "why_now": "Keep struct winsize offsets explicit.",
            },
            {
                "id": "phase11-hvc-console-hv-ops-layout-assert",
                "status": "starter_landed",
                "why_now": "Keep struct hv_ops callback-table order explicit.",
            },
            {
                "id": "phase11-hvc-console-hv-ops-signature-assert",
                "status": "starter_landed",
                "why_now": "Keep hv_ops callback signatures explicit.",
            },
            {
                "id": "phase11-hvc-console-tty-and-teardown-parity",
                "status": "starter_landed",
                "why_now": "Keep final-close teardown, remove ordering, and cleanup ownership explicit.",
            },
        ],
    }
    write_text(
        root,
        "zigux/tests/phase11_hvc_console_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )

    inventory = {
        "build_test_names": list(INVENTORY_REQUIRED_BUILD_TESTS),
        "shared_test_depend_steps": [
            "run_phase11_hvc_console_tests",
            "run_hvc_console_verify_tests",
            "run_phase11_hvc_cleanup_tests",
        ],
        "module_root_source_files": [
            {"module": module, "path": path}
            for module, path in INVENTORY_REQUIRED_MODULE_PATHS.items()
        ],
        "test_root_modules": [
            {"test": "phase11-hvc-console-tests", "root_module": "phase11_hvc_console_module"},
            {"test": "phase11-hvc-console-verify-tests", "root_module": "hvc_console_verify_module"},
            {"test": "phase11-hvc-cleanup-tests", "root_module": "phase11_hvc_cleanup_module"},
            {"test": "phase11-hvc-console-survey-tests", "root_module": "phase11_hvc_console_survey_module"},
        ],
        "forbidden_markers": [
            "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
        ],
        "dedicated_survey_replays": [
            "zigux/tests/phase11_hvc_console_survey.zig",
        ],
        "shared_split_replays": [],
        "shared_adjunct_replays": [
            "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
            "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
        ],
        "shared_replay_markers": [
            {"path": expectation.path, "marker": expectation.marker}
            for expectation in INVENTORY_REQUIRED_MARKERS
        ],
    }
    write_text(
        root,
        "zigux/tests/fixtures/phase11_build_inventory.json",
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
    )


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-teardown-packet-"))
    total_cases = 0
    try:
        make_fixture(temp_dir)
        validate(temp_dir)
        total_cases += 1

        broken_manifest = temp_dir / "zigux/tests/phase11_hvc_console_manifest.json"
        data = json.loads(broken_manifest.read_text(encoding="utf-8"))
        data["gaps"] = [
            entry
            for entry in data["gaps"]
            if entry["id"] != "phase11-hvc-console-cleanup-handoff"
        ]
        broken_manifest.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected cleanup handoff validation to fail")

        make_fixture(temp_dir)
        teardown_note = temp_dir / "Documentation/zigux/phase11-hvc-console-teardown-note.md"
        teardown_note.write_text("# teardown\ncleanup-time tty-port ownership\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected teardown note fragment validation to fail")

        make_fixture(temp_dir)
        inventory = temp_dir / "zigux/tests/fixtures/phase11_build_inventory.json"
        data = json.loads(inventory.read_text(encoding="utf-8"))
        data["shared_replay_markers"] = [
            entry
            for entry in data["shared_replay_markers"]
            if entry["path"] != "zigux/tests/phase11_hvc_console_poll_retry_split.zig"
        ]
        inventory.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected inventory marker validation to fail")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"PHASE11_HVC_TEARDOWN_PACKET_SELF_TEST=pass cases={total_cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 11 HVC teardown packet for review-surface drift."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in fixture cases instead of validating a repository checkout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        validate(Path(args.repo_root).resolve())
    except ValidationError as exc:
        print(f"PHASE11_HVC_TEARDOWN_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_TEARDOWN_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
