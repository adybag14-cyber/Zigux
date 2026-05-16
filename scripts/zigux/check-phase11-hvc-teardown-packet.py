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


REQUIRED_PACKET_FILES = (
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
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
        ),
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
        "phase11-hvc-console-close-teardown",
        "phase11-hvc-console-notifier-add-handoff",
        "phase11-hvc-console-hangup-disconnect",
        "phase11-hvc-console-remove-handoff",
        "phase11-hvc-console-validation-matrix",
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
        ],
    }
    write_text(
        root,
        "zigux/tests/phase11_hvc_console_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
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
