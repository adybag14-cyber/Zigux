#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=attached_toolchain_guidance_evidence

Fail-closed checker for the bounded Phase 14 attached-toolchain and
environment-guidance reminder packet.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ATTACHED_NOTE_PATH = Path("Documentation/zigux/phase14-attached-toolchain-guidance-gap.md")
SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

ATTACHED_NOTE_MARKERS = [
    "# Phase 14 Attached Toolchain Guidance Gap",
    "- lane: `P14-L10`",
    "shared attached-toolchain and environment-guidance reminder packet",
    "Fresh builder-environment validation on 2026-05-25 also confirms that the attached Zig bundle used by this lane still behaves like a usable bounded-check fallback rather than a stale archival assumption:",
    "unpacking `agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` into the scheduled runtime succeeded without extra environment overrides",
    "`zig version` returned `0.17.0-dev.87+9b177a7d2`",
    "`zig env` reported the expected `x86_64-linux` target plus the normal bundled library and global cache paths",
    "manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain optional packet-local escape hatches rather than the primary current rerun path",
]

SMOKE_NOTE_MARKERS = [
    "`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
    "keep the attached-toolchain boundary explicit",
    "The current readable route layer still stops at `make -C zigux phase14-validate`",
    "Keep `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase14`, and the attached-toolchain `ZIG=/absolute/path/to/attached-zig/zig ...` variants only as historical packet vocabulary",
]

SCRIPTS_README_MARKERS = [
    "keep the attached-toolchain vocabulary explicit from the scripts root too:",
    "ZIG_PINNED_TARGET :=",
    "ZIG_PINNED_CHANNEL :=",
    "ZIG_PINNED_EXTRACT_ROOT :=",
    "ZIG_PINNED_EXECUTABLE :=",
    "ZIG_LOCAL_TOOLCHAIN :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain packet-local escape vocabulary rather than current default rerun guidance",
]

MAKEFILE_MARKERS = [
    "ZIG_PINNED_TARGET :=",
    "ZIG_PINNED_CHANNEL :=",
    "ZIG_PINNED_EXTRACT_ROOT :=",
    "ZIG_PINNED_EXECUTABLE :=",
    "ZIG_LOCAL_TOOLCHAIN :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    ".PHONY:",
    "phase14-validate",
]

REQUIRED_MANIFEST_VALUES = {
    ("productization", "validation_gate"): "make -C zigux phase14-validate",
    ("survey_summary", "phase14_make_target_present"): True,
    ("survey_summary", "phase14_make_smoke_target_present"): False,
    ("survey_summary", "phase14_make_uses_pinned_toolchain_fallback"): True,
    ("survey_summary", "phase14_make_uses_local_toolchain_probe"): True,
    ("survey_summary", "phase14_make_falls_back_to_path_zig"): True,
}

REQUIRED_MANIFEST_SURFACES = [
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_manifest_values(errors: list[str], manifest: object) -> None:
    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            errors.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(
                "manifest_value_mismatch:"
                f"{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )


def require_manifest_surfaces(errors: list[str], manifest: object) -> None:
    try:
        surfaces = lookup_path(manifest, ("shared_smoke_surfaces",))
    except KeyError:
        errors.append("missing_manifest_key:shared_smoke_surfaces")
        return
    if not isinstance(surfaces, list):
        errors.append("manifest_value_mismatch:shared_smoke_surfaces:not_a_list")
        return
    for surface in REQUIRED_MANIFEST_SURFACES:
        if surface not in surfaces:
            errors.append(f"missing_manifest_surface:{surface}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    required_files = [
        ATTACHED_NOTE_PATH,
        SMOKE_NOTE_PATH,
        SCRIPTS_README_PATH,
        MAKEFILE_PATH,
        MANIFEST_PATH,
    ]
    for rel in required_files:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, ATTACHED_NOTE_PATH, read_text(root, ATTACHED_NOTE_PATH), ATTACHED_NOTE_MARKERS)
    require_markers(errors, SMOKE_NOTE_PATH, read_text(root, SMOKE_NOTE_PATH), SMOKE_NOTE_MARKERS)
    require_markers(errors, SCRIPTS_README_PATH, read_text(root, SCRIPTS_README_PATH), SCRIPTS_README_MARKERS)
    require_markers(errors, MAKEFILE_PATH, read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS)

    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors
    require_manifest_values(errors, manifest)
    require_manifest_surfaces(errors, manifest)
    return errors


def fixture_attached_note() -> str:
    return """# Phase 14 Attached Toolchain Guidance Gap

## Scope
- lane: `P14-L10`
- packet: shared attached-toolchain and environment-guidance reminder packet for the bounded Phase 14 smoke route

Fresh builder-environment validation on 2026-05-25 also confirms that the attached Zig bundle used by this lane still behaves like a usable bounded-check fallback rather than a stale archival assumption:
- unpacking `agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` into the scheduled runtime succeeded without extra environment overrides
- `zig version` returned `0.17.0-dev.87+9b177a7d2`
- `zig env` reported the expected `x86_64-linux` target plus the normal bundled library and global cache paths

That local replay does not change current repo evidence.
manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain optional packet-local escape hatches rather than the primary current rerun path
"""


def fixture_smoke_note() -> str:
    return """# Phase 14 End-to-End Smoke Survey

## Status
  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`

The shared smoke packet must keep the attached-toolchain boundary explicit.
The current readable route layer still stops at `make -C zigux phase14-validate`.
Keep `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase14`, and the attached-toolchain `ZIG=/absolute/path/to/attached-zig/zig ...` variants only as historical packet vocabulary.
"""


def fixture_scripts_readme() -> str:
    return """# scripts/zigux

## Phase 14

- keep the attached-toolchain vocabulary explicit from the scripts root too: readable `zigux/Makefile` now exposes `ZIG_PINNED_TARGET :=`, `ZIG_PINNED_CHANNEL :=`, `ZIG_PINNED_EXTRACT_ROOT :=`, `ZIG_PINNED_EXECUTABLE :=`, `ZIG_LOCAL_TOOLCHAIN :=`, `ZIG_PINNED_TOOLCHAIN :=`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, so the staged pinned bundle stays first, the local `.zig-toolchain/*/zig` probe stays second, and the `zig` on `PATH` fallback stays last while manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain packet-local escape vocabulary rather than current default rerun guidance
"""


def fixture_makefile() -> str:
    return """PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..
ZIG_PINNED_CHANNEL := 0.17.0-dev.87+9b177a7d2
ZIG_PINNED_TARGET := x86_64-linux
ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)
ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))
ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)

.PHONY: phase14-validate
phase14-validate:
	@true
"""


def fixture_manifest() -> str:
    payload = {
        "productization": {
            "validation_gate": "make -C zigux phase14-validate",
        },
        "shared_smoke_surfaces": REQUIRED_MANIFEST_SURFACES,
        "survey_summary": {
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "phase14_make_uses_pinned_toolchain_fallback": True,
            "phase14_make_uses_local_toolchain_probe": True,
            "phase14_make_falls_back_to_path_zig": True,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, ATTACHED_NOTE_PATH, fixture_attached_note())
    write_text(root, SMOKE_NOTE_PATH, fixture_smoke_note())
    write_text(root, SCRIPTS_README_PATH, fixture_scripts_readme())
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, MANIFEST_PATH, fixture_manifest())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-attached-toolchain-guidance-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            ATTACHED_NOTE_PATH,
            fixture_attached_note().replace(
                "`zig version` returned `0.17.0-dev.87+9b177a7d2`\n",
                "",
                1,
            ),
        )
        if not any("`zig version` returned `0.17.0-dev.87+9b177a7d2`" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            print("expected attached note version marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
                "`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=missing`",
                1,
            ),
        )
        if not any("`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            print("expected smoke-note guidance marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            SCRIPTS_README_PATH,
            fixture_scripts_readme().replace(
                "manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain packet-local escape vocabulary rather than current default rerun guidance",
                "manual overrides exist",
                1,
            ),
        )
        if not any("manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain packet-local escape vocabulary rather than current default rerun guidance" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            print("expected scripts README override marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace("ZIG_LOCAL_TOOLCHAIN :=", "ZIG_LOCAL_MISSING :=", 1),
        )
        if not any("ZIG_LOCAL_TOOLCHAIN :=" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            print("expected Makefile local toolchain marker failure")
            return 1

        write_fixture_tree(base)
        payload = json.loads(fixture_manifest())
        payload["survey_summary"]["phase14_make_uses_local_toolchain_probe"] = False
        write_text(base, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        if not any("manifest_value_mismatch:survey_summary.phase14_make_uses_local_toolchain_probe" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            print("expected manifest toolchain-probe failure")
            return 1

        write_fixture_tree(base)
        payload = json.loads(fixture_manifest())
        payload["shared_smoke_surfaces"].remove("scripts/zigux/README.md")
        write_text(base, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        if not any("missing_manifest_surface:scripts/zigux/README.md" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=fail")
            print("expected manifest surface coverage failure")
            return 1

        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST=pass")
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_fixture_tree(args.write_sample_root)
        print(f"PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    errors = check(args.root)
    if errors:
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE=fail")
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_ISSUES_END")
        return 1

    print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE=pass")
    print(
        "PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_REQUIRED_MARKER_COUNT="
        f"{len(ATTACHED_NOTE_MARKERS) + len(SMOKE_NOTE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    print(
        "PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_EVIDENCE_MANIFEST_ASSERTION_COUNT="
        f"{len(REQUIRED_MANIFEST_VALUES) + len(REQUIRED_MANIFEST_SURFACES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
