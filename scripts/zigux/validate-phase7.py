#!/usr/bin/env python3
"""Validate the bounded Phase 7 leaf-library evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_FILE_PATH = Path(__file__).resolve()
ROOT = _FILE_PATH.parents[2] if len(_FILE_PATH.parents) > 2 else _FILE_PATH.parent

CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")
CHECKER_PATH = Path("scripts/zigux/check-phase7-shared-surface.py")
BUILD_WIRING_CHECKER_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")
MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
CMDLINE_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-cmdline-packet.py")
ARGV_SPLIT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")
STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py")
RBTREE_PARITY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-rbtree-parity.py")

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
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
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
EXPECTED_ROADMAP_ANCHORS = [
    "lib/string_helpers.c",
    "lib/cmdline.c",
    "lib/argv_split.c",
    "lib/rbtree.c",
]
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase7-build-wiring.py",
    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase7-cmdline-packet.py",
    "python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]
EXPECTED_GAPS: list[str] = []
EXPECTED_HELPER_MARKERS = {
    Path("lib/string_helpers.zig"): [
        "pub const STRING_UNITS_10",
        "pub const KasprintfStrarrayResult",
        "pub fn kstrdupQuotable",
        "pub fn kstrdupQuotableCmdline",
        "pub const ParseIntArrayError",
        "pub fn parseIntArray",
    ],
    Path("lib/cmdline.zig"): ["pub fn parseOptionStr", "pub fn getOption"],
    Path("lib/argv_split.zig"): ["pub const ArgvSplitResult", "pub fn argvSplit"],
    Path("lib/rbtree.zig"): [
        "pub const Node = struct",
        "pub const RootCached = struct",
        "pub fn add(",
        "pub fn rb_find_add_cached(",
    ],
}
EXPECTED_BUILD_WIRING_EVIDENCE = [
    {
        "path": "zigux/tests/phase7_build.zig",
        "expected_markers": [
            "../../lib/string_helpers.zig",
            "../../lib/cmdline.zig",
            "../../lib/argv_split.zig",
            "../../lib/rbtree.zig",
            "phase7-string-helpers-test",
            "phase7-string-helpers-survey",
            "phase7-string-helpers-sample-boundary",
            "phase7-string-helpers-format-boundary",
            "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
            "phase7-cmdline-test",
            "phase7-cmdline-survey",
            "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)",
            "phase7-argv-split-test",
            "phase7-argv-split-survey",
            "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)",
            "phase7-rbtree-test",
            "phase7-rbtree-survey",
            "const test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");",
            "test_step.dependOn(&run_string_helpers_tests.step)",
            "test_step.dependOn(&run_string_helpers_survey_tests.step)",
            "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
            "test_step.dependOn(&run_cmdline_tests.step)",
            "test_step.dependOn(&run_cmdline_survey_tests.step)",
            "test_step.dependOn(&run_argv_split_tests.step)",
            "test_step.dependOn(&run_argv_split_survey_tests.step)",
            "test_step.dependOn(&run_rbtree_tests.step)",
            "test_step.dependOn(&run_rbtree_survey_tests.step)",
        ],
    },
    {
        "path": "zigux/Makefile",
        "expected_markers": [
            "phase7-validate:",
            "$(PYTHON) scripts/zigux/validate-phase7.py --self-test",
            "$(PYTHON) scripts/zigux/validate-phase7.py",
        ],
    },
]
REQUIRED_FILES = [
    CATALOG_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
    CHECKER_PATH,
    BUILD_WIRING_CHECKER_PATH,
    MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH,
    CMDLINE_PACKET_CHECKER_PATH,
    ARGV_SPLIT_PACKET_CHECKER_PATH,
    STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH,
    RBTREE_PARITY_PACKET_CHECKER_PATH,
    Path("lib/string_helpers.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
    Path("lib/rbtree.zig"),
]
REQUIRED_MAKEFILE_LINES = [
    "phase7-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
]
SELF_TEST_CASE_COUNT = 30


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def count_exact_lines(text: str, marker: str) -> int:
    normalized_marker = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized_marker)


def run_checker(root: Path, checker_path: Path, root_flag: str = "--repo-root") -> None:
    result = subprocess.run(
        [sys.executable, str(root / checker_path), root_flag, str(root)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker_path.as_posix()} failed: {detail}")


def run_checker_self_test(root: Path, checker_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / checker_path), "--self-test"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker_path.as_posix()} self-test failed: {detail}")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    manifest = read_json(root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase7 packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase7 phase drift")
    if manifest.get("lane_scope") != EXPECTED_SCOPE:
        raise ValidationError("phase7 scope drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_COMPANIONS:
        raise ValidationError("phase7 companion drift")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase7 roadmap anchor drift")
    if manifest.get("current_replay_inventory") != EXPECTED_REPLAYS:
        raise ValidationError("phase7 replay inventory drift")
    if manifest.get("current_repo_reality_gaps") != EXPECTED_GAPS:
        raise ValidationError("phase7 repo-reality gaps drift")
    if manifest.get("current_build_wiring_evidence") != EXPECTED_BUILD_WIRING_EVIDENCE:
        raise ValidationError("phase7 build-wiring evidence drift")

    for rel_path, markers in EXPECTED_HELPER_MARKERS.items():
        helper_text = read_text(root / rel_path)
        for marker in markers:
            if marker not in helper_text:
                raise ValidationError(f"phase7 helper marker missing in {rel_path.as_posix()}: {marker}")

    build_text = read_text(root / BUILD_PATH)
    for marker in EXPECTED_BUILD_WIRING_EVIDENCE[0]["expected_markers"]:
        if marker not in build_text:
            raise ValidationError(f"phase7 build marker missing: {marker}")

    makefile = read_text(root / MAKEFILE_PATH)
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            raise ValidationError(f"phase7 make route missing: {marker}")
        if count != 1:
            raise ValidationError(f"phase7 make route count drift: {marker} ({count} != 1)")

    run_checker(root, CHECKER_PATH)
    run_checker_self_test(root, BUILD_WIRING_CHECKER_PATH)
    run_checker(root, BUILD_WIRING_CHECKER_PATH)
    run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")
    run_checker_self_test(root, CMDLINE_PACKET_CHECKER_PATH)
    run_checker(root, CMDLINE_PACKET_CHECKER_PATH)
    run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)
    run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)
    run_checker_self_test(root, RBTREE_PARITY_PACKET_CHECKER_PATH)
    run_checker(root, RBTREE_PARITY_PACKET_CHECKER_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / CATALOG_PATH,
        "\n".join(
            [
                "- packet: `phase7-leaf-library-evidence`",
                "- phase: `Phase 7`",
                "- lane scope: shared leaf-library evidence rows and validation foothold only",
                "",
                "## Current direct-readback companions",
                "- `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
                "- `Documentation/zigux/README.md`",
                "- `Documentation/zigux/review-checklist.md`",
                "- `scripts/zigux/check-phase7-shared-surface.py`",
                "- `scripts/zigux/check-phase7-build-wiring.py`",
                "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
                "- `scripts/zigux/check-phase7-cmdline-packet.py`",
                "- `scripts/zigux/check-phase7-argv-split-packet.py`",
                "- `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`",
                "- `scripts/zigux/check-phase7-rbtree-parity.py`",
                "- `scripts/zigux/validate-phase7.py`",
                "- `scripts/zigux/README.md`",
                "- `zigux/tests/README.md`",
                "- `zigux/tests/phase7_leaf_library_evidence_manifest.json`",
                "- `zigux/tests/phase7_build.zig`",
                "- `zigux/Makefile`",
                "- `lib/string_helpers.zig`",
                "- `lib/cmdline.zig`",
                "- `lib/argv_split.zig`",
                "- `lib/rbtree.zig`",
                "",
                "## Current replay inventory",
                "- `python3 scripts/zigux/check-phase7-shared-surface.py`",
                "- `python3 scripts/zigux/check-phase7-shared-surface.py --self-test`",
                "- `python3 scripts/zigux/check-phase7-build-wiring.py`",
                "- `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`",
                "- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
                "- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`",
                "- `python3 scripts/zigux/check-phase7-cmdline-packet.py`",
                "- `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`",
                "- `python3 scripts/zigux/check-phase7-argv-split-packet.py`",
                "- `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "- `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`",
                "- `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test`",
                "- `python3 scripts/zigux/check-phase7-rbtree-parity.py`",
                "- `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`",
                "- `python3 scripts/zigux/validate-phase7.py`",
                "- `python3 scripts/zigux/validate-phase7.py --self-test`",
                "- `make -C zigux phase7-validate`",
                "",
                "## Current build-wiring evidence",
                "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.",
                "- `zigux/tests/phase7_build.zig` still exposes the dedicated helper, survey, sample-boundary, and format-boundary routes through `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-string-helpers-format-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey`.",
                "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.",
                "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
                "",
                "## Current repo-reality gaps",
                "- none currently",
                "",
                "## Review posture",
                "- keep the current Phase 7 packet bounded to returned leaf-library helper evidence, the shared docs-root, scripts-root, and tests-root reminder packet, the dedicated build-wiring guard, the dedicated `cmdline` packet guard, the dedicated `argv_split` packet guard, the dedicated `string_helpers` format-boundary packet guard, the dedicated `rbtree` parity guard, the make-wrapper self-test alignment guard, and one Makefile-backed validation foothold",
                "- do not widen this packet into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes",
            ]
        ) + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "phase7-validate:\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n",
    )
    write(
        root / WORKFLOW_PATH,
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 7 make-wrapper selftest alignment checker",
                "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
                "      - name: Self-test current Phase 7 cmdline packet checker",
                "        run: python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test",
                "      - name: Check current Phase 7 make-wrapper selftest alignment packet",
                "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
            ]
        )
        + "\n",
    )
    write(root / BUILD_PATH, "\n".join(EXPECTED_BUILD_WIRING_EVIDENCE[0]["expected_markers"]) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": EXPECTED_SCOPE,
                "current_direct_readback_companions": EXPECTED_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_direct_helper_evidence": [
                    {
                        "key": "string_helpers",
                        "zig_helper": "lib/string_helpers.zig",
                        "expected_markers": [
                            "pub const STRING_UNITS_10",
                            "pub const KasprintfStrarrayResult",
                            "pub fn kstrdupQuotable",
                            "pub fn kstrdupQuotableCmdline",
                        ],
                    },
                    {
                        "key": "string_helpers_parse_int_array",
                        "zig_helper": "lib/string_helpers.zig",
                        "expected_markers": [
                            "pub const ParseIntArrayError",
                            "pub fn parseIntArray",
                        ],
                    },
                    {
                        "key": "cmdline",
                        "zig_helper": "lib/cmdline.zig",
                        "expected_markers": EXPECTED_HELPER_MARKERS[Path("lib/cmdline.zig")],
                    },
                    {
                        "key": "argv_split",
                        "zig_helper": "lib/argv_split.zig",
                        "expected_markers": EXPECTED_HELPER_MARKERS[Path("lib/argv_split.zig")],
                    },
                    {
                        "key": "rbtree",
                        "zig_helper": "lib/rbtree.zig",
                        "expected_markers": EXPECTED_HELPER_MARKERS[Path("lib/rbtree.zig")],
                    },
                ],
                "current_build_wiring_evidence": EXPECTED_BUILD_WIRING_EVIDENCE,
                "current_replay_inventory": EXPECTED_REPLAYS,
                "current_repo_reality_gaps": EXPECTED_GAPS,
            },
            indent=2,
        ) + "\n",
    )
    for rel_path, content in [
        (
            Path("lib/string_helpers.zig"),
            "pub const STRING_UNITS_10 = 0;\n"
            "pub const KasprintfStrarrayResult = struct {};\n"
            "pub fn kstrdupQuotable() void {}\n"
            "pub fn kstrdupQuotableCmdline() void {}\n"
            "pub const ParseIntArrayError = error{};\n"
            "pub fn parseIntArray() void {}\n",
        ),
        (Path("lib/cmdline.zig"), "pub fn parseOptionStr() void {}\npub fn getOption() void {}\n"),
        (Path("lib/argv_split.zig"), "pub const ArgvSplitResult = struct {};\npub fn argvSplit() void {}\n"),
        (
            Path("lib/rbtree.zig"),
            "pub const Node = struct {};\n"
            "pub const RootCached = struct {};\n"
            "pub fn add() void {}\n"
            "pub fn rb_find_add_cached() void {}\n",
        ),
    ]:
        write(root / rel_path, content)
    write(
        root / Path("scripts/zigux/validate-phase7.py"),
        "\n".join(
            [
                "from pathlib import Path",
                'MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")',
                'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")',
                'run_checker_self_test(root, Path("scripts/zigux/check-phase7-cmdline-packet.py"))',
                "print('PHASE7_VALIDATE=pass')",
            ]
        )
        + "\n",
    )
    write(
        root / CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n"
        "import argparse\n"
        "from pathlib import Path\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        "    parser.add_argument('--repo-root', type=Path, default=Path('.'))\n"
        "    parser.parse_args()\n"
        "    print('PHASE7_SHARED_SURFACE=pass')\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
    )
    write(
        root / CMDLINE_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n"
        "import argparse\n"
        "from pathlib import Path\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        "    parser.add_argument('--repo-root', type=Path, default=Path('.'))\n"
        "    parser.add_argument('--self-test', action='store_true')\n"
        "    args = parser.parse_args()\n"
        "    if args.self_test:\n"
        "        print('PHASE7_CMDLINE_PACKET_SELF_TEST=pass')\n"
        "        return 0\n"
        "    print('PHASE7_CMDLINE_PACKET=pass')\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
    )
    for checker_path, success_marker, root_flag in [
        (ARGV_SPLIT_PACKET_CHECKER_PATH, "PHASE7_ARGV_SPLIT_PACKET=pass", "--repo-root"),
        (STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass", "--repo-root"),
    ]:
        write(
            root / checker_path,
            "#!/usr/bin/env python3\n"
            "from __future__ import annotations\n"
            "import argparse\n"
            "from pathlib import Path\n\n"
            "def main() -> int:\n"
            "    parser = argparse.ArgumentParser()\n"
            f"    parser.add_argument('{root_flag}', type=Path, default=Path('.'))\n"
            "    parser.parse_args()\n"
            f"    print('{success_marker}')\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n",
        )
    write(
        root / RBTREE_PARITY_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n"
        "import argparse\n"
        "from pathlib import Path\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        "    parser.add_argument('--repo-root', type=Path, default=Path('.'))\n"
        "    parser.add_argument('--self-test', action='store_true')\n"
        "    args = parser.parse_args()\n"
        "    if args.self_test:\n"
        "        print('PHASE7_RBTREE_PARITY_SELF_TEST=pass')\n"
        "        return 0\n"
        "    print('PHASE7_RBTREE_PARITY=pass')\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
    )
    write(
        root / BUILD_WIRING_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n"
        "import argparse\n"
        "from pathlib import Path\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        "    parser.add_argument('--repo-root', type=Path, default=Path('.'))\n"
        "    parser.add_argument('--self-test', action='store_true')\n"
        "    args = parser.parse_args()\n"
        "    if args.self_test:\n"
        "        print('PHASE7_BUILD_WIRING_SELF_TEST=pass')\n"
        "        print('PHASE7_BUILD_WIRING_SELF_TEST_CASE_COUNT=1')\n"
        "        return 0\n"
        "    print('PHASE7_BUILD_WIRING=pass')\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
    )
    write(
        root / MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n"
        "import argparse\n"
        "from pathlib import Path\n\n"
        "WORKFLOW_PATH = Path('.github/workflows/zigux-bootstrap.yml')\n"
        "VALIDATOR_PATH = Path('scripts/zigux/validate-phase7.py')\n"
        "PARKED_PATH = Path('scripts/zigux/check-phase7-make-wrapper.py')\n"
        "REQUIRED_WORKFLOW_LINES = (\n"
        "    'run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test',\n"
        "    'run: python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test',\n"
        "    'run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py',\n"
        ")\n"
        "REQUIRED_VALIDATOR_MARKERS = (\n"
        "    'MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path(\"scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py\")',\n"
        "    'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, \"--root\")',\n"
        "    'run_checker_self_test(root, Path(\"scripts/zigux/check-phase7-cmdline-packet.py\"))',\n"
        ")\n\n"
        "def count_exact_lines(text: str, marker: str) -> int:\n"
        "    normalized = marker.strip()\n"
        "    return sum(1 for line in text.splitlines() if line.strip() == normalized)\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        "    parser.add_argument('--root', type=Path, default=Path('.'))\n"
        "    args = parser.parse_args()\n"
        "    root = args.root\n"
        "    if (root / PARKED_PATH).exists():\n"
        "        raise SystemExit('parked make-wrapper path unexpectedly returned')\n"
        "    workflow_text = (root / WORKFLOW_PATH).read_text(encoding='utf-8')\n"
        "    validator_text = (root / VALIDATOR_PATH).read_text(encoding='utf-8')\n"
        "    for marker in REQUIRED_WORKFLOW_LINES:\n"
        "        if count_exact_lines(workflow_text, marker) != 1:\n"
        "            raise SystemExit(f'workflow marker drift: {marker}')\n"
        "    for marker in REQUIRED_VALIDATOR_MARKERS:\n"
        "        if validator_text.count(marker) != 1:\n"
        "            raise SystemExit(f'validator marker drift: {marker}')\n"
        "    print('PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass')\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
    )


def expect_failure(root: Path, rel_path: Path, marker: str, delete_only: bool = False) -> None:
    path = root / rel_path
    if delete_only:
        path.unlink()
    else:
        original = read_text(path)
        updated = original.replace(marker, "", 1)
        if updated == original:
            raise AssertionError(f"marker not found: {marker}")
        write(path, updated)
    try:
        validate(root)
    except (ValidationError, json.JSONDecodeError):
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        for rel_path, marker, delete_only in [
            (MANIFEST_PATH, '"scripts/zigux/check-phase7-cmdline-packet.py"', False),
            (MANIFEST_PATH, '"python3 scripts/zigux/check-phase7-cmdline-packet.py"', False),
            (MANIFEST_PATH, '"python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test"', False),
            (CATALOG_PATH, "- `scripts/zigux/check-phase7-cmdline-packet.py`", False),
            (CATALOG_PATH, "- `python3 scripts/zigux/check-phase7-cmdline-packet.py`", False),
            (MANIFEST_PATH, '"lib/rbtree.zig"', False),
            (MANIFEST_PATH, '"zigux/tests/phase7_build.zig"', False),
            (MANIFEST_PATH, '"scripts/zigux/check-phase7-rbtree-parity.py"', False),
            (MANIFEST_PATH, '"python3 scripts/zigux/check-phase7-rbtree-parity.py"', False),
            (BUILD_PATH, "../../lib/rbtree.zig", False),
            (BUILD_PATH, "phase7-string-helpers-format-boundary", False),
            (BUILD_PATH, "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)", False),
            (BUILD_PATH, "phase7-rbtree-test", False),
            (MAKEFILE_PATH, "phase7-validate:", False),
            (MAKEFILE_PATH, "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n", False),
            (Path("lib/rbtree.zig"), "pub fn rb_find_add_cached()", False),
            (Path("lib/string_helpers.zig"), "pub fn parseIntArray()", False),
            (MANIFEST_PATH, '"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py"', False),
            (MANIFEST_PATH, '"python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py"', False),
            (WORKFLOW_PATH, "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test\n", False),
            (WORKFLOW_PATH, "        run: python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test\n", False),
            (WORKFLOW_PATH, "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py\n", False),
            (Path("scripts/zigux/validate-phase7.py"), 'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")\n', False),
            (Path("scripts/zigux/validate-phase7.py"), 'run_checker_self_test(root, Path("scripts/zigux/check-phase7-cmdline-packet.py"))\n', False),
            (BUILD_WIRING_CHECKER_PATH, "    parser.add_argument('--self-test', action='store_true')\n", False),
            (CHECKER_PATH, "", True),
            (BUILD_WIRING_CHECKER_PATH, "", True),
            (MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "", True),
            (CMDLINE_PACKET_CHECKER_PATH, "", True),
            (ARGV_SPLIT_PACKET_CHECKER_PATH, "", True),
            (STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, "", True),
            (RBTREE_PARITY_PACKET_CHECKER_PATH, "", True),
        ]:
            case_root = Path(tempfile.mkdtemp(prefix="zigux_phase7_validate_case_"))
            try:
                scaffold_repo(case_root)
                expect_failure(case_root, rel_path, marker, delete_only)
                cases_run += 1
            finally:
                for child in sorted(case_root.rglob("*"), reverse=True):
                    if child.is_file():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                case_root.rmdir()
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE7_VALIDATE_SELF_TEST=pass")
    print(f"PHASE7_VALIDATE_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_VALIDATE=fail: {exc}")
        return 1
    print("PHASE7_VALIDATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
