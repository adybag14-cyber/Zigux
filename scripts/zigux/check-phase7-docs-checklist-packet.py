#!/usr/bin/env python3
"""Fail-closed guard for the shared Phase 7 docs/checklist reminder packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

DOCS_README = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
CATALOG = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MANIFEST = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE = Path("zigux/Makefile")
VALIDATOR = Path("scripts/zigux/validate-phase7.py")
SHARED_SURFACE = Path("scripts/zigux/check-phase7-shared-surface.py")
BUILD_WIRING = Path("scripts/zigux/check-phase7-build-wiring.py")
SELFTEST_ALIGNMENT = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
ARGV_SPLIT_PACKET = Path("scripts/zigux/check-phase7-argv-split-packet.py")
STRING_HELPERS_PACKET = Path("scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py")
BUILD_FILE = Path("zigux/tests/phase7_build.zig")
STRING_HELPERS = Path("lib/string_helpers.zig")
CMDLINE = Path("lib/cmdline.zig")
ARGV_SPLIT = Path("lib/argv_split.zig")
RBTREE = Path("lib/rbtree.zig")

EXPECTED_PACKET = "phase7-leaf-library-evidence"
EXPECTED_PHASE = "Phase 7"
EXPECTED_SCOPE = "shared leaf-library evidence rows and validation foothold only"
EXPECTED_COMPANIONS = [
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase7-shared-surface.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
]
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase7-build-wiring.py",
    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]

REQUIRED_FILES = [
    DOCS_README,
    REVIEW_CHECKLIST,
    CATALOG,
    SCRIPTS_README,
    TESTS_README,
    MANIFEST,
    MAKEFILE,
    VALIDATOR,
    SHARED_SURFACE,
    BUILD_WIRING,
    SELFTEST_ALIGNMENT,
    ARGV_SPLIT_PACKET,
    STRING_HELPERS_PACKET,
    BUILD_FILE,
    STRING_HELPERS,
    CMDLINE,
    ARGV_SPLIT,
    RBTREE,
]

REQUIRED_MARKERS = {
    DOCS_README: [
        "Phase 7 notes -",
        "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
        "scripts/zigux/check-phase7-shared-surface.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_leaf_library_evidence_manifest.json",
        "zigux/tests/phase7_build.zig",
        "zigux/Makefile",
        "lib/string_helpers.zig",
        "lib/cmdline.zig",
        "lib/argv_split.zig",
        "lib/rbtree.zig",
        "make -C zigux phase7-validate",
    ],
    REVIEW_CHECKLIST: [
        "if the change touches the shared Phase 7 leaf-library packet",
        "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
        "scripts/zigux/check-phase7-shared-surface.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_leaf_library_evidence_manifest.json",
        "zigux/tests/phase7_build.zig",
        "zigux/Makefile",
        "lib/string_helpers.zig",
        "lib/cmdline.zig",
        "lib/argv_split.zig",
        "lib/rbtree.zig",
        "make -C zigux phase7-validate",
    ],
    CATALOG: [
        "- packet: `phase7-leaf-library-evidence`",
        "- phase: `Phase 7`",
        "- lane scope: shared leaf-library evidence rows and validation foothold only",
        "## Current direct-readback companions",
        "## Current replay inventory",
        "## Current build-wiring evidence",
        "## Review posture",
        "scripts/zigux/check-phase7-shared-surface.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_leaf_library_evidence_manifest.json",
        "zigux/tests/phase7_build.zig",
        "zigux/Makefile",
        "lib/string_helpers.zig",
        "lib/cmdline.zig",
        "lib/argv_split.zig",
        "lib/rbtree.zig",
        "make -C zigux phase7-validate",
    ],
    SCRIPTS_README: [
        "## Phase 7",
        "Phase 7 flow - the current scripts-root leaf-library packet stays reviewable",
        "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
        "scripts/zigux/check-phase7-shared-surface.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_leaf_library_evidence_manifest.json",
        "zigux/tests/phase7_build.zig",
        "zigux/Makefile",
        "lib/string_helpers.zig",
        "lib/cmdline.zig",
        "lib/argv_split.zig",
        "lib/rbtree.zig",
        "make -C zigux phase7-validate",
    ],
    TESTS_README: [
        "## Phase 7 leaf-library packet",
        "current direct-readback Phase 7 leaf-library packet:",
        "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
        "scripts/zigux/check-phase7-shared-surface.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_leaf_library_evidence_manifest.json",
        "zigux/tests/phase7_build.zig",
        "zigux/Makefile",
        "lib/string_helpers.zig",
        "lib/cmdline.zig",
        "lib/argv_split.zig",
        "lib/rbtree.zig",
        "make -C zigux phase7-validate",
    ],
}

MAKEFILE_LINES = [
    "phase7-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
]


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, rel_path: Path) -> str:
    path = root / rel_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {rel_path.as_posix()}") from exc


def read_manifest(root: Path) -> dict[str, object]:
    return json.loads(read_text(root, MANIFEST))


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for candidate in text.splitlines() if candidate == line)


def require_markers(root: Path, rel_path: Path, markers: list[str]) -> int:
    text = read_text(root, rel_path)
    count = 0
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"missing marker in {rel_path.as_posix()}: {marker}")
        count += 1
    return count


def validate(root: Path) -> dict[str, int]:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    manifest = read_manifest(root)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase7 packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase7 phase drift")
    if manifest.get("lane_scope") != EXPECTED_SCOPE:
        raise ValidationError("phase7 scope drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_COMPANIONS:
        raise ValidationError("phase7 companion drift")
    if manifest.get("current_replay_inventory") != EXPECTED_REPLAYS:
        raise ValidationError("phase7 replay inventory drift")
    if manifest.get("current_repo_reality_gaps") != []:
        raise ValidationError("phase7 repo-reality gaps drift")

    marker_count = 0
    for rel_path, markers in REQUIRED_MARKERS.items():
        marker_count += require_markers(root, rel_path, markers)

    makefile = read_text(root, MAKEFILE)
    for line in MAKEFILE_LINES:
        count = count_exact_line(makefile, line)
        if count != 1:
            raise ValidationError(f"phase7 make route drift for line: {line}")

    return {
        "required_file_count": len(REQUIRED_FILES),
        "companion_count": len(EXPECTED_COMPANIONS),
        "replay_count": len(EXPECTED_REPLAYS),
        "marker_count": marker_count + len(MAKEFILE_LINES),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_manifest() -> str:
    return json.dumps(
        {
            "packet": EXPECTED_PACKET,
            "phase": EXPECTED_PHASE,
            "lane_scope": EXPECTED_SCOPE,
            "current_direct_readback_companions": EXPECTED_COMPANIONS,
            "roadmap_anchors": [
                "lib/string_helpers.c",
                "lib/cmdline.c",
                "lib/argv_split.c",
                "lib/rbtree.c",
            ],
            "current_direct_helper_evidence": [],
            "current_build_wiring_evidence": [],
            "current_replay_inventory": EXPECTED_REPLAYS,
            "current_repo_reality_gaps": [],
        },
        indent=2,
    ) + "\n"


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    write_text(
        root / DOCS_README,
        "\n".join(
            [
                "# Zigux Documentation",
                "",
                "Phase 7 notes - "
                + " - ".join(
                    [
                        "`Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
                        "`Documentation/zigux/review-checklist.md`",
                        "`scripts/zigux/README.md`",
                        "`zigux/tests/README.md`",
                        "`scripts/zigux/check-phase7-shared-surface.py`",
                        "`scripts/zigux/check-phase7-build-wiring.py`",
                        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
                        "`scripts/zigux/check-phase7-argv-split-packet.py`",
                        "`scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`",
                        "`scripts/zigux/validate-phase7.py`",
                        "`zigux/tests/phase7_leaf_library_evidence_manifest.json`",
                        "`zigux/tests/phase7_build.zig`",
                        "`zigux/Makefile`",
                        "`lib/string_helpers.zig`",
                        "`lib/cmdline.zig`",
                        "`lib/argv_split.zig`",
                        "`lib/rbtree.zig`",
                    ]
                ),
                "* `make -C zigux phase7-validate` replays the bounded current Phase 7 reminder packet.",
            ]
        )
        + "\n",
    )
    write_text(
        root / REVIEW_CHECKLIST,
        "\n".join(
            [
                "# Zigux Review Checklist",
                "",
                "* if the change touches the shared Phase 7 leaf-library packet, do "
                + ", ".join(f"`{item}`" for item in EXPECTED_COMPANIONS)
                + " still agree on the current bounded Phase 7 packet, and keep `make -C zigux phase7-validate` explicit as the current bounded replay surface?",
            ]
        )
        + "\n",
    )
    write_text(
        root / CATALOG,
        "\n".join(
            [
                "- packet: `phase7-leaf-library-evidence`",
                "- phase: `Phase 7`",
                "- lane scope: shared leaf-library evidence rows and validation foothold only",
                "",
                "## Current direct-readback companions",
                *[f"- `{item}`" for item in EXPECTED_COMPANIONS],
                "",
                "## Current replay inventory",
                *[f"- `{item}`" for item in EXPECTED_REPLAYS],
                "",
                "## Current build-wiring evidence",
                "- `zigux/tests/phase7_build.zig` keeps the dedicated helper and survey routes explicit.",
                "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit.",
                "",
                "## Review posture",
                "- keep the current Phase 7 packet bounded to returned leaf-library helper evidence, the shared docs-root, scripts-root, and tests-root reminder packet, the dedicated build-wiring guard, the dedicated `argv_split` packet guard, the dedicated `string_helpers` format-boundary packet guard, the make-wrapper self-test alignment guard, and one Makefile-backed validation foothold",
            ]
        )
        + "\n",
    )
    write_text(
        root / SCRIPTS_README,
        "\n".join(
            [
                "# scripts/zigux",
                "",
                "## Phase 7",
                "",
                "- Phase 7 flow - the current scripts-root leaf-library packet stays reviewable through the returned leaf-library evidence catalog, the shared docs-root and tests-root reminder packet, the shipped shared-surface, build-wiring, make-wrapper self-test alignment, dedicated `argv_split` and `string_helpers` format-boundary guards, the validator entrypoint, the shared machine-readable manifest, the shared build graph, the narrow `phase7-validate` wrapper foothold, and the four roadmap-backed helper anchors instead of reopening helper semantics or reconstructing a broader missing-wrapper story",
                "- "
                + ", ".join(f"`{item}`" for item in EXPECTED_COMPANIONS)
                + " remain the reminder-surface companions for that packet",
                "- `make -C zigux phase7-validate` remains the shipped bounded replay surface",
            ]
        )
        + "\n",
    )
    write_text(
        root / TESTS_README,
        "\n".join(
            [
                "# zigux/tests",
                "",
                "## Phase 7 leaf-library packet",
                "",
                "* current direct-readback Phase 7 leaf-library packet:",
                *[f"* `{item}`" for item in EXPECTED_COMPANIONS],
                "* Keep the validator-first reminder packet explicit too: "
                + ", ".join(f"`{item}`" for item in EXPECTED_REPLAYS),
            ]
        )
        + "\n",
    )
    write_text(root / MANIFEST, sample_manifest())
    write_text(
        root / MAKEFILE,
        "\n".join(
            [
                "ZIGUX_ROOT := .",
                "PYTHON ?= python3",
                "",
                "phase7-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
            ]
        )
        + "\n",
    )
    write_text(root / VALIDATOR, "#!/usr/bin/env python3\n")
    write_text(root / SHARED_SURFACE, "#!/usr/bin/env python3\n")
    write_text(root / BUILD_WIRING, "#!/usr/bin/env python3\n")
    write_text(root / SELFTEST_ALIGNMENT, "#!/usr/bin/env python3\n")
    write_text(root / ARGV_SPLIT_PACKET, "#!/usr/bin/env python3\n")
    write_text(root / STRING_HELPERS_PACKET, "#!/usr/bin/env python3\n")
    write_text(root / BUILD_FILE, "// phase7 build placeholder\n")
    write_text(root / STRING_HELPERS, "pub const STRING_UNITS_10 = [_]u8{};\n")
    write_text(root / CMDLINE, "pub fn parseOptionStr() void {}\npub fn getOption() void {}\n")
    write_text(root / ARGV_SPLIT, "pub const ArgvSplitResult = struct {};\npub fn argvSplit() void {}\n")
    write_text(root / RBTREE, "pub const Node = struct {};\npub const RootCached = struct {};\npub fn add() void {}\npub fn rb_find_add_cached() void {}\n")


def run_self_test() -> None:
    cases = 5
    with tempfile.TemporaryDirectory(prefix="phase7-docs-checker-") as tmp:
        base = Path(tmp)
        sample = base / "sample"
        write_sample_root(sample)
        validate(sample)

        missing_marker = base / "missing_marker"
        write_sample_root(missing_marker)
        docs_path = missing_marker / DOCS_README
        docs_path.write_text(docs_path.read_text(encoding="utf-8").replace("make -C zigux phase7-validate", "make -C zigux phase7-test", 1), encoding="utf-8")
        try:
            validate(missing_marker)
            raise AssertionError("expected docs marker failure")
        except ValidationError:
            pass

        manifest_drift = base / "manifest_drift"
        write_sample_root(manifest_drift)
        manifest = json.loads((manifest_drift / MANIFEST).read_text(encoding="utf-8"))
        manifest["current_replay_inventory"] = manifest["current_replay_inventory"][:-1]
        write_text(manifest_drift / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        try:
            validate(manifest_drift)
            raise AssertionError("expected manifest drift failure")
        except ValidationError:
            pass

        missing_file = base / "missing_file"
        write_sample_root(missing_file)
        (missing_file / SHARED_SURFACE).unlink()
        try:
            validate(missing_file)
            raise AssertionError("expected missing file failure")
        except ValidationError:
            pass

        makefile_drift = base / "makefile_drift"
        write_sample_root(makefile_drift)
        makefile_path = makefile_drift / MAKEFILE
        makefile_path.write_text(makefile_path.read_text(encoding="utf-8").replace("phase7-validate:", "phase7-test:"), encoding="utf-8")
        try:
            validate(makefile_drift)
            raise AssertionError("expected makefile drift failure")
        except ValidationError:
            pass

    print("PHASE7_DOCS_CHECKLIST_PACKET_SELF_TEST=pass")
    print(f"PHASE7_DOCS_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--root", type=Path, help="Alias for --repo-root")
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    root = args.root if args.root is not None else args.repo_root
    stats = validate(root)
    print("PHASE7_DOCS_CHECKLIST_PACKET=pass")
    print(f"PHASE7_DOCS_CHECKLIST_PACKET_REQUIRED_FILE_COUNT={stats['required_file_count']}")
    print(f"PHASE7_DOCS_CHECKLIST_PACKET_COMPANION_COUNT={stats['companion_count']}")
    print(f"PHASE7_DOCS_CHECKLIST_PACKET_REPLAY_COUNT={stats['replay_count']}")
    print(f"PHASE7_DOCS_CHECKLIST_PACKET_MARKER_COUNT={stats['marker_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
