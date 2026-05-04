#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "zigux/tests/runtime_loader_gap_manifest.json"

EXPECTED_REVIEW_ONLY_LOADER_PLAN_SURFACES = [
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
]

EXPECTED_METADATA_ONLY_REGISTRATION_SURFACES = [
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
    "zigux/kernel/runtime_loader.zig",
]

EXPECTED_FORBIDDEN_LIVE_CALL_ORDER = [
    "module_init()",
    "module_exit()",
    "register_kretprobe()",
    "unregister_kretprobe()",
]


def fail(reason: str) -> int:
    print("PHASE9_LOADER_LIFECYCLE_BOUNDARY=fail")
    print(reason)
    return 1


def require_equal(actual: object, expected: object, label: str) -> str | None:
    if actual != expected:
        return f"{label}:expected={expected!r}:actual={actual!r}"
    return None


def main() -> int:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fail(f"missing_manifest:{MANIFEST_PATH.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        return fail(f"manifest_json_decode_failed:{exc}")

    summary = manifest.get("lifecycle_boundary_summary")
    if not isinstance(summary, dict):
        return fail("missing_or_invalid:lifecycle_boundary_summary")

    errors: list[str] = []

    for label, expected in (
        ("staged_init_exit_symbols_are_review_only", True),
        ("kretprobe_registration_labels_are_metadata_only", True),
        ("live_initcall_or_registration_path_present", False),
        ("shared_request_boundary_surface", "zigux/kernel/runtime_loader.zig"),
        (
            "shared_request_boundary_guard",
            "RuntimeLoadRequest.keepsPreExecutionLifecycleBoundaryExplicit",
        ),
    ):
        mismatch = require_equal(summary.get(label), expected, label)
        if mismatch is not None:
            errors.append(mismatch)

    review_only_mismatch = require_equal(
        summary.get("review_only_loader_plan_surfaces"),
        EXPECTED_REVIEW_ONLY_LOADER_PLAN_SURFACES,
        "review_only_loader_plan_surfaces",
    )
    if review_only_mismatch is not None:
        errors.append(review_only_mismatch)

    metadata_only_mismatch = require_equal(
        summary.get("metadata_only_registration_surfaces"),
        EXPECTED_METADATA_ONLY_REGISTRATION_SURFACES,
        "metadata_only_registration_surfaces",
    )
    if metadata_only_mismatch is not None:
        errors.append(metadata_only_mismatch)

    forbidden_calls_mismatch = require_equal(
        summary.get("forbidden_live_calls"),
        EXPECTED_FORBIDDEN_LIVE_CALL_ORDER,
        "forbidden_live_calls",
    )
    if forbidden_calls_mismatch is not None:
        errors.append(forbidden_calls_mismatch)

    if errors:
        return fail("\n".join(errors))

    print("PHASE9_LOADER_LIFECYCLE_BOUNDARY=pass")
    print(
        "PHASE9_LOADER_LIFECYCLE_REVIEW_ONLY_COUNT="
        f"{len(EXPECTED_REVIEW_ONLY_LOADER_PLAN_SURFACES)}"
    )
    print(
        "PHASE9_LOADER_LIFECYCLE_METADATA_ONLY_COUNT="
        f"{len(EXPECTED_METADATA_ONLY_REGISTRATION_SURFACES)}"
    )
    print(
        "PHASE9_LOADER_LIFECYCLE_FORBIDDEN_CALL_COUNT="
        f"{len(EXPECTED_FORBIDDEN_LIVE_CALL_ORDER)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
