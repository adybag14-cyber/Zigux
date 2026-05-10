#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "samples/zigux/**",
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-test",
    ],
    "Documentation/zigux/README.md": [
        "Phase 7 notes -",
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "dedicated make-wrapper self-test alignment checker",
        "the dedicated string-helper manifest packet",
        "`scripts/zigux/validate-phase7.py`",
        "`scripts/zigux/check-phase7-make-wrapper.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "`scripts/zigux/check-phase7-argv-split-packet.py`",
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "`scripts/zigux/check-phase7-build-wiring.py`",
        "`zigux/Makefile`",
        "`zigux/tests/phase7_string_helpers_survey.zig`",
        "`make -C zigux phase7-validate`",
        "`make -C zigux phase7`",
    ],
    "Documentation/zigux/review-checklist.md": [
        "shared Phase 7 leaf-helper packet",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        ".github/workflows/zigux-bootstrap.yml",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
        "without implying unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surfaces?",
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "string_escape_mem()",
        "`kstrdup_quotable()` over the bounded quotable-log escape path",
        "`kasprintf_strarray()` over the bounded sequential prefix-index ownership path",
        "`kfree_strarray()` over the bounded repeated-teardown-safe release path",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "no `samples/zigux/*string*` Phase 5 reference sample is expected here;",
        "If the string-helper family reopens, prefer one tiny helper-local parity, survey, manifest, or validation sync inside the now-landed whitespace, size-rendering, quoting, escape, string-array, and no-sample boundary packet before widening into `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, or `devm_kasprintf_strarray()`.",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "validator-only `get_option()` acceptance plus Linux-style hyphen range expansion, validation-only counting, and leading-plus numeric acceptance for `get_option()` and `get_options()`",
        "exact bare-option matching for comma-delimited flags, including leading and doubled-comma empty-option acceptance plus trailing-comma rejection",
        "caller-owned buffer discipline for `next_arg()`: `nextArg()` writes NUL sentinels into the supplied mutable buffer and returns borrowed `param`, `value`, and `rest` slices into that same storage",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "null-terminated pointer-vector access through `cArgv()`",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "This slice does not carry an open parity-fixture follow-up",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "PHASE7_LANE_KEY=P7-Y05",
        "`scripts/zigux/check-phase7-make-wrapper.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "`scripts/zigux/validate-phase7.py`",
        "`zigux/Makefile`",
        "`.github/workflows/zigux-bootstrap.yml`",
        "`make -C zigux phase7-validate` and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface",
        "this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;",
        "treat any new `samples/zigux/*string*.zig` file as review-blocking",
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "zigux/tests/phase7_build.zig",
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "lib/cmdline.zig",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "lib/argv_split.zig",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/rbtree.zig",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "zigux/tests/fixtures/phase7_rbtree.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/Makefile",
        "the shared Phase 7 build-wiring gate lives in `scripts/zigux/check-phase7-build-wiring.py` and `zigux/tests/phase7_build.zig`; treat it as the parked shared reviewability route for the no-sample `string_helpers`, `cmdline`, `argv_split`, and `rbtree` packet instead of reading that checker as an `rbtree`-only surface",
    ],
    "scripts/zigux/README.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "zigux/tests/fixtures/phase7_rbtree.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
        "make -C zigux phase7-validate",
        "`make -C zigux phase7`",
        "there is no separate shared `check-phase7-build-inventory.py`",
    ],
    "scripts/zigux/check-phase7-make-wrapper.py": [
        "--self-test",
        "PHASE7_MAKE_WRAPPER_SELF_TEST=pass",
    ],
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py": [
        "--self-test",
        "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass",
        "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    "scripts/zigux/check-phase7-rbtree-parity.py": [
        "--self-test",
        "PHASE7_RBTREE_PARITY_SELF_TEST=pass",
    ],
    "scripts/zigux/check-phase7-build-wiring.py": [
        "--self-test",
        "PHASE7_BUILD_WIRING_SELF_TEST=pass",
    ],
    "zigux/tests/README.md": [
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/README.md",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/Makefile",
        ".github/workflows/zigux-bootstrap.yml",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
        "zigux/tests/phase7_build.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "the committed `zigux/tests/phase7_string_helpers_manifest.json` string-helper manifest packet",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "zigux/tests/fixtures/phase7_rbtree.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
        "including the dedicated `zigux/tests/phase7_string_helpers_survey.zig` string-helper survey gate",
        "including the dedicated `zigux/tests/phase7_cmdline_survey.zig` cmdline survey gate",
        "the dedicated `zigux/tests/phase7_argv_split_survey.zig` argvSplit survey gate",
        "the dedicated `zigux/tests/phase7_string_helpers_sample_boundary.zig` boundary replay",
        "and the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/validate-phase7.py --self-test",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
        "phase7-test:",
        "build test --build-file zigux/tests/phase7_build.zig --summary all",
        "phase7: phase7-validate phase7-test",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-string-helpers-tests",
        "phase7-string-helpers-survey-tests",
        "\"phase7_string_helpers_survey.zig\"",
        "run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
        "phase7-string-helpers-sample-boundary-tests",
        "\"phase7_string_helpers_sample_boundary.zig\"",
        "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));",
        "phase7-cmdline-tests",
        "phase7-cmdline-survey-tests",
        "\"phase7_cmdline_survey.zig\"",
        "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));",
        "phase7-argv-split-tests",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        "phase7-rbtree-tests",
        "phase7-rbtree-survey-tests",
        "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));",
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_build.zig",
        "phase 7 string helpers survey keeps the roadmap-backed helper packet reviewable",
        "scripts/zigux/check-phase7-build-wiring.py",
        "phase 7 parseIntArray keeps base and sign parsing explicit",
        "phase 7 stringUnescape covers deterministic Linux escape fixtures",
        "phase 7 stringUnescapeInplace reuses the core escape path without extra buffers",
        "If the string-helper family reopens, prefer one tiny helper-local parity, survey, manifest, or validation sync inside the now-landed whitespace, size-rendering, quoting, escape, string-array, and no-sample boundary packet before widening into `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, or `devm_kasprintf_strarray()`.",
        "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator",
        "phase 7 kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe",
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "samples/zigux/string_helpers_sample.zig",
        "std.mem.indexOf(u8, entry.name, \"string\") != null",
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "no `samples/zigux/*string*` Phase 5 reference sample is expected here;",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        "Documentation/zigux/phase7-cmdline-slice.md",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_build.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "const docs_root = try readRepoFile(allocator, \"Documentation/zigux/README.md\");",
        "const helper_impl = try readRepoFile(allocator, \"lib/cmdline.zig\");",
        "caller-owned buffer discipline for `next_arg()`: `nextArg()` writes NUL sentinels into the supplied mutable buffer and returns borrowed `param`, `value`, and `rest` slices into that same storage",
        "phase 7 getOption preserves validator-only numeric acceptance",
        "phase 7 parseOptionStr matches only exact bare options",
        "try expectContains(cmdline_tests, \"try std.testing.expect(cmdline.parseOptionStr(\\\",debug\\\", \\\"\\\"));\");",
        "try expectContains(cmdline_tests, \"try std.testing.expect(cmdline.parseOptionStr(\\\"debug,,quiet\\\", \\\"\\\"));\");",
        "try expectContains(helper_impl, \"test \\\"nextArg keeps param, value, and rest borrowed from the caller buffer\\\"\");",
        "phase 7 nextArg matches serialized edge fixtures",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "zigux/tests/phase7_argv_split_manifest.json",
        "PHASE7_LANE_KEY=P7-Y07",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    ],
}

EXACT_COUNT_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        ("samples/zigux/**", 2),
        ("Validate Phase 7 runtime helper gates", 1),
        ("make -C zigux phase7-validate", 1),
        ("Run Phase 7 runtime helper tests", 1),
        ("make -C zigux phase7-test", 1),
    ],
    "Documentation/zigux/README.md": [
        ("Phase 7 notes -", 1),
        ("Documentation/zigux/phase7-argv-split-slice.md", 1),
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 1),
        ("dedicated make-wrapper self-test alignment checker", 1),
        ("the dedicated string-helper manifest packet", 1),
        ("`scripts/zigux/check-phase7-make-wrapper.py`", 1),
        ("`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`", 1),
        ("`scripts/zigux/check-phase7-argv-split-packet.py`", 1),
        ("`scripts/zigux/check-phase7-rbtree-parity.py`", 1),
        ("`scripts/zigux/check-phase7-build-wiring.py`", 1),
        ("`zigux/tests/phase7_string_helpers_survey.zig`", 1),
        ("`make -C zigux phase7-validate`", 1),
        ("`make -C zigux phase7`", 1),
    ],
    "Documentation/zigux/review-checklist.md": [
        ("shared Phase 7 leaf-helper packet", 1),
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 1),
        ("scripts/zigux/check-phase7-make-wrapper.py", 1),
        ("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", 1),
        ("scripts/zigux/check-phase7-argv-split-packet.py", 1),
        ("scripts/zigux/check-phase7-rbtree-parity.py", 1),
        ("scripts/zigux/check-phase7-build-wiring.py", 1),
        ("zigux/tests/phase7_string_helpers_survey.zig", 1),
        ("`make -C zigux phase7-validate`", 1),
        ("`make -C zigux phase7`", 1),
        (
            "without implying unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surfaces?",
            1,
        ),
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        ("`kstrdup_quotable()` over the bounded quotable-log escape path", 1),
        ("`kasprintf_strarray()` over the bounded sequential prefix-index ownership path", 1),
        ("`kfree_strarray()` over the bounded repeated-teardown-safe release path", 1),
        ("zigux/tests/phase7_string_helpers_manifest.json", 1),
        (
            "If the string-helper family reopens, prefer one tiny helper-local parity, survey, manifest, or validation sync inside the now-landed whitespace, size-rendering, quoting, escape, string-array, and no-sample boundary packet before widening into `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, or `devm_kasprintf_strarray()`.",
            1,
        ),
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        ("validator-only `get_option()` acceptance plus Linux-style hyphen range expansion, validation-only counting, and leading-plus numeric acceptance for `get_option()` and `get_options()`", 1),
        ("exact bare-option matching for comma-delimited flags, including leading and doubled-comma empty-option acceptance plus trailing-comma rejection", 1),
        ("caller-owned buffer discipline for `next_arg()`: `nextArg()` writes NUL sentinels into the supplied mutable buffer and returns borrowed `param`, `value`, and `rest` slices into that same storage", 1),
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        ("null-terminated pointer-vector access through `cArgv()`", 1),
        ("python3 scripts/zigux/check-phase7-argv-split-packet.py", 1),
    ],
    "Documentation/zigux/phase7-rbtree-slice.md": [
        ("python3 scripts/zigux/check-phase7-rbtree-parity.py", 1),
        ("zig build test --build-file zigux/tests/phase7_build.zig", 1),
        ("This slice does not carry an open parity-fixture follow-up", 1),
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        ("PHASE7_LANE_KEY=P7-Y05", 1),
        ("`scripts/zigux/check-phase7-make-wrapper.py`", 1),
        ("`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`", 1),
        ("`scripts/zigux/validate-phase7.py`", 1),
        ("`zigux/Makefile`", 1),
        ("`.github/workflows/zigux-bootstrap.yml`", 1),
        (
            "`make -C zigux phase7-validate` and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface",
            1,
        ),
        (
            "this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`",
            1,
        ),
    ],
    "samples/zigux/README.md": [
        ("current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;", 1),
        ("Documentation/zigux/phase7-string-helpers-slice.md", 1),
        ("lib/string_helpers.zig", 1),
        ("zigux/tests/phase7_string_helpers.zig", 1),
        ("zigux/tests/phase7_string_helpers_survey.zig", 1),
        ("zigux/tests/phase7_string_helpers_sample_boundary.zig", 1),
        ("zigux/tests/phase7_string_helpers_manifest.json", 1),
        ("zigux/tests/phase7_build.zig", 1),
        ("current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;", 1),
        ("Documentation/zigux/phase7-cmdline-slice.md", 1),
        ("lib/cmdline.zig", 1),
        ("zigux/tests/phase7_cmdline.zig", 1),
        ("zigux/tests/phase7_cmdline_survey.zig", 1),
        ("current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;", 1),
        ("Documentation/zigux/phase7-argv-split-slice.md", 1),
        ("lib/argv_split.zig", 1),
        ("zigux/tests/phase7_argv_split.zig", 1),
        ("zigux/tests/phase7_argv_split_survey.zig", 1),
        ("zigux/tests/phase7_argv_split_manifest.json", 1),
        ("scripts/zigux/check-phase7-argv-split-packet.py", 1),
        ("current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;", 1),
        ("Documentation/zigux/phase7-rbtree-slice.md", 1),
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 1),
        ("lib/rbtree.zig", 1),
        ("zigux/tests/phase7_rbtree.zig", 1),
        ("zigux/tests/phase7_rbtree_survey.zig", 1),
        ("zigux/tests/phase7_rbtree_manifest.json", 1),
        ("zigux/tests/fixtures/phase7_rbtree.json", 1),
        ("zigux/tests/fixtures/phase7_rbtree_c_harness.c", 1),
        ("scripts/zigux/validate-phase7.py", 1),
        ("scripts/zigux/check-phase7-make-wrapper.py", 1),
        ("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", 1),
        ("scripts/zigux/check-phase7-rbtree-parity.py", 1),
        ("scripts/zigux/check-phase7-build-wiring.py", 1),
        ("zigux/Makefile", 1),
        (
            "the shared Phase 7 build-wiring gate lives in `scripts/zigux/check-phase7-build-wiring.py` and `zigux/tests/phase7_build.zig`; treat it as the parked shared reviewability route for the no-sample `string_helpers`, `cmdline`, `argv_split`, and `rbtree` packet instead of reading that checker as an `rbtree`-only surface",
            1,
        ),
    ],
    "scripts/zigux/README.md": [
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 1),
        ("scripts/zigux/check-phase7-make-wrapper.py", 1),
        ("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", 1),
        ("scripts/zigux/check-phase7-argv-split-packet.py", 1),
        ("scripts/zigux/check-phase7-rbtree-parity.py", 1),
        ("scripts/zigux/check-phase7-build-wiring.py", 1),
        ("zigux/tests/phase7_string_helpers_manifest.json", 1),
        ("make -C zigux phase7-validate", 1),
        ("`make -C zigux phase7`", 1),
    ],
    "zigux/Makefile": [
        ("phase7-validate:\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py --self-test\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py\n", 1),
        ("phase7-test:\n", 1),
        ("\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all\n", 1),
        ("phase7: phase7-validate phase7-test\n", 1),
    ],
    "zigux/tests/README.md": [
        ("`Documentation/zigux/README.md`", 1),
        ("`Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`", 1),
        ("`scripts/zigux/README.md`", 1),
        ("`scripts/zigux/validate-phase7.py`", 1),
        ("`scripts/zigux/check-phase7-make-wrapper.py`", 1),
        ("`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`", 1),
        ("`scripts/zigux/check-phase7-argv-split-packet.py`", 1),
        ("`scripts/zigux/check-phase7-rbtree-parity.py`", 1),
        ("`scripts/zigux/check-phase7-build-wiring.py`", 1),
        ("`zigux/Makefile`", 1),
        ("`.github/workflows/zigux-bootstrap.yml`", 1),
        ("`make -C zigux phase7-validate`", 1),
        ("`make -C zigux phase7`", 1),
        ("`zigux/tests/phase7_string_helpers_manifest.json`", 1),
        (
            "the committed `zigux/tests/phase7_string_helpers_manifest.json` string-helper manifest packet",
            1,
        ),
        ("`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`", 1),
        ("`zigux/tests/phase7_argv_split_manifest.json`", 1),
        ("`zigux/tests/phase7_rbtree_manifest.json`", 1),
        ("`zigux/tests/fixtures/phase7_rbtree.json`", 1),
        ("`zigux/tests/fixtures/phase7_rbtree_c_harness.c`", 1),
        ("including the dedicated `zigux/tests/phase7_string_helpers_survey.zig` string-helper survey gate", 1),
        ("including the dedicated `zigux/tests/phase7_cmdline_survey.zig` cmdline survey gate", 1),
        ("the dedicated `zigux/tests/phase7_argv_split_survey.zig` argvSplit survey gate", 1),
        ("the dedicated `zigux/tests/phase7_string_helpers_sample_boundary.zig` boundary replay", 1),
        ("and the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate", 1),
    ],
    "zigux/tests/phase7_build.zig": [
        ("phase7-string-helpers-survey-tests", 1),
        ("\"phase7_string_helpers_survey.zig\"", 1),
        ("run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));", 1),
        ("phase7-string-helpers-sample-boundary-tests", 1),
        ("\"phase7_string_helpers_sample_boundary.zig\"", 1),
        ("run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));", 1),
        ("phase7-cmdline-survey-tests", 1),
        ("\"phase7_cmdline_survey.zig\"", 1),
        ("run_cmdline_survey_tests.setCwd(b.path(\"../..\"));", 1),
        ("phase7-argv-split-survey-tests", 1),
        ("\"phase7_argv_split_survey.zig\"", 1),
        ("run_argv_split_survey_tests.setCwd(b.path(\"../..\"));", 1),
        ("phase7-rbtree-survey-tests", 1),
        ("run_rbtree_survey_tests.setCwd(b.path(\"../..\"));", 1),
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        ("Documentation/zigux/phase7-string-helpers-slice.md", 1),
        ("zigux/tests/phase7_string_helpers.zig", 1),
        ("zigux/tests/phase7_string_helpers_sample_boundary.zig", 1),
        ("scripts/zigux/validate-phase7.py", 1),
        ("zigux/tests/phase7_build.zig", 1),
        ("scripts/zigux/check-phase7-build-wiring.py", 1),
        ("phase 7 stringUnescapeInplace reuses the core escape path without extra buffers", 1),
        ("phase 7 kstrdupQuotable escapes special log bytes and preserves first-NUL bounds", 1),
        ("phase 7 kstrdupQuotable returns null for null inputs and keeps empty results owned", 1),
        ("phase 7 kstrdupQuotable frees the owned copy when allocation fails", 1),
        ("phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator", 1),
        ("phase 7 kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe", 1),
        (
            "If the string-helper family reopens, prefer one tiny helper-local parity, survey, manifest, or validation sync inside the now-landed whitespace, size-rendering, quoting, escape, string-array, and no-sample boundary packet before widening into `kstrdup_quotable_cmdline()`, `kstrdup_quotable_file()`, or `devm_kasprintf_strarray()`.",
            1,
        ),
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        ("This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.", 1),
        ("no `samples/zigux/*string*` Phase 5 reference sample is expected here;", 1),
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        ("Documentation/zigux/phase7-cmdline-slice.md", 1),
        ("zigux/tests/phase7_cmdline.zig", 1),
        ("zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", 1),
        ("const docs_root = try readRepoFile(allocator, \"Documentation/zigux/README.md\");", 1),
        ("const helper_impl = try readRepoFile(allocator, \"lib/cmdline.zig\");", 1),
        ("caller-owned buffer discipline for `next_arg()`: `nextArg()` writes NUL sentinels into the supplied mutable buffer and returns borrowed `param`, `value`, and `rest` slices into that same storage", 1),
        ("phase 7 getOption preserves validator-only numeric acceptance", 1),
        ("phase 7 parseOptionStr matches only exact bare options", 1),
        ("try expectContains(cmdline_tests, \"try std.testing.expect(cmdline.parseOptionStr(\\\",debug\\\", \\\"\\\"));\");", 1),
        ("try expectContains(cmdline_tests, \"try std.testing.expect(cmdline.parseOptionStr(\\\"debug,,quiet\\\", \\\"\\\"));\");", 1),
        ("try expectContains(helper_impl, \"test \\\"nextArg keeps param, value, and rest borrowed from the caller buffer\\\"\");", 1),
        ("phase 7 nextArg matches serialized edge fixtures", 1),
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        ("Documentation/zigux/phase7-argv-split-slice.md", 1),
        ("zigux/tests/phase7_argv_split_manifest.json", 1),
        ("PHASE7_LANE_KEY=P7-Y07", 1),
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        (
            "phase 7 rbtree survey manifest records the landed runtime leaf surface and committed parity fixture",
            1,
        ),
        ("zigux/tests/phase7_rbtree_manifest.json", 1),
        ("python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test", 1),
        ("PHASE7_LANE_KEY=P7-Y04", 1),
        ("phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable", 1),
        ("phase 7 rbtree detached nodes stay non-empty until callers clear them", 1),
        ("phase 7 rbtree clearNode marks detached nodes as empty", 1),
        ("try std.testing.expectEqual(@as(?*Node, null), nextPostorder(null));", 1),
    ],
}

PHASE7_VALIDATE_TARGET = "phase7-validate"
REQUIRED_PHASE7_VALIDATE_BLOCK_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
)

FORBIDDEN_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "run: make -C zigux phase7",
        "run: python3 scripts/zigux/validate-phase7.py --self-test",
        "run: python3 scripts/zigux/validate-phase7.py",
        "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        "run: zig build test --build-file zigux/tests/phase7_build.zig",
    ],
    "zigux/Makefile": [
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig\n",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig\n",
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase7.py": "# fixture\n",
    "samples/zigux/README.md": "\n".join(
        marker
        for marker in REQUIRED_MARKERS["samples/zigux/README.md"]
        if marker != "scripts/zigux/check-phase7-build-wiring.py"
    )
    + "\n",
    "zigux/tests/phase7_string_helpers.zig": "// fixture\n",
    "zigux/tests/phase7_string_helpers_survey.zig": "\n".join(
        REQUIRED_MARKERS["zigux/tests/phase7_string_helpers_survey.zig"]
    )
    + "\n",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": "\n".join(
        REQUIRED_MARKERS["zigux/tests/phase7_string_helpers_sample_boundary.zig"]
    )
    + "\n",
    "zigux/tests/phase7_string_helpers_manifest.json": "{}\n",
    "zigux/tests/phase7_cmdline.zig": "// fixture\n",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig": "// fixture\n",
    "zigux/tests/phase7_argv_split.zig": "// fixture\n",
    "zigux/tests/phase7_argv_split_survey.zig": "\n".join(
        REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"]
    )
    + "\n",
    "zigux/tests/phase7_argv_split_manifest.json": "{}\n",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "// fixture\n",
    "zigux/tests/phase7_rbtree.zig": "// fixture\n",
    "zigux/tests/phase7_rbtree_manifest.json": "{}\n",
    "zigux/tests/fixtures/phase7_rbtree.json": "{}\n",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c": "/* fixture */\n",
    "lib/string_helpers.zig": "// fixture\n",
    "lib/cmdline.zig": "// fixture\n",
    "lib/argv_split.zig": "// fixture\n",
    "lib/rbtree.zig": "// fixture\n",
    "scripts/zigux/check-phase7-build-wiring.py": "\n".join(
        REQUIRED_MARKERS["scripts/zigux/check-phase7-build-wiring.py"]
    )
    + "\n",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py": "\n".join(
        REQUIRED_MARKERS["scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"]
    )
    + "\n",
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected_count in marker_counts:
            actual_count = text.count(marker)
            if actual_count != expected_count:
                missing.append(f"{rel}: {marker}:expected={expected_count}:actual={actual_count}")
    return missing


def collect_forbidden_markers(root: Path) -> list[str]:
    forbidden: list[str] = []
    for rel, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                forbidden.append(f"{rel}: {marker}")
    return forbidden


def extract_make_target_block(text: str, target: str) -> str:
    block_lines: list[str] = []
    collecting = False
    for line in text.splitlines():
        if not collecting:
            if line == f"{target}:":
                collecting = True
                block_lines.append(line)
            continue
        if line and not line.startswith("\t"):
            break
        block_lines.append(line)
    return "\n".join(block_lines)


def collect_phase7_validate_block_markers(root: Path) -> list[str]:
    missing: list[str] = []
    makefile_text = (root / "zigux/Makefile").read_text(encoding="utf-8")
    block = extract_make_target_block(makefile_text, PHASE7_VALIDATE_TARGET)
    if not block:
        missing.append(f"zigux/Makefile: missing {PHASE7_VALIDATE_TARGET} target block")
        return missing
    for marker in REQUIRED_PHASE7_VALIDATE_BLOCK_LINES:
        actual_count = sum(1 for line in block.splitlines() if line.strip() == marker)
        if actual_count != 1:
            missing.append(
                f"zigux/Makefile {PHASE7_VALIDATE_TARGET} block: {marker}:expected=1:actual={actual_count}"
            )
    return missing


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []
    missing_markers = collect_missing_markers(root)
    missing_markers.extend(collect_phase7_validate_block_markers(root))
    forbidden_markers = collect_forbidden_markers(root)
    return [], missing_markers, forbidden_markers


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    fixture_text.update(FIXTURE_OVERRIDES)
    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = fixture_text.get(rel, "")
        for marker, expected_count in marker_counts:
            while text.count(marker) < expected_count:
                text += marker + "\n"
        fixture_text[rel] = text
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert forbidden_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(tmp_root)
    assert missing_files == [], case
    assert forbidden_markers == [], case
    assert expected in missing_markers, case


def remove_first_marker(text: str, marker: str) -> str:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if marker in line:
            removed = lines[:index] + lines[index + 1 :]
            updated = "".join(removed)
            assert updated != text
            return updated
    updated = text.replace(marker, "", 1)
    assert updated != text
    return updated


def duplicate_first_marker(text: str, marker: str) -> str:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if marker in line:
            duplicated = lines[: index + 1] + [line] + lines[index + 1 :]
            updated = "".join(duplicated)
            assert updated != text
            return updated
    updated = text.replace(marker, f"{marker}\n{marker}", 1)
    assert updated != text
    return updated


def relocate_makefile_marker_outside_target(text: str, target: str, marker: str) -> str:
    lines = text.splitlines()
    updated_lines: list[str] = []
    in_target = False
    moved = False
    for line in lines:
        if not in_target and line == f"{target}:":
            in_target = True
            updated_lines.append(line)
            continue
        if in_target and line and not line.startswith("\t"):
            in_target = False
        if in_target and line.strip() == marker:
            moved = True
            continue
        updated_lines.append(line)
    assert moved
    updated_lines.extend(["phase7-relocated:", f"\t{marker}"])
    return "\n".join(updated_lines) + "\n"


def mutate_file(path: Path, transform: callable) -> None:
    original = path.read_text(encoding="utf-8")
    path.write_text(transform(original), encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        missing_file_case_count = 0
        for rel in REQUIRED_FILES:
            (tmp_root / rel).unlink()
            expect_missing_file(f"missing_file:{rel}", tmp_root, rel)
            write_fixture_root(tmp_root)
            missing_file_case_count += 1

        missing_marker_case_count = 0
        for rel, markers in REQUIRED_MARKERS.items():
            path = tmp_root / rel
            fixture_text = path.read_text(encoding="utf-8")
            for marker in markers:
                if fixture_text.count(marker) != 1:
                    continue
                mutate_file(path, lambda text, marker=marker: remove_first_marker(text, marker))
                expect_missing_marker(f"missing_marker:{rel}:{marker}", tmp_root, f"{rel}: {marker}")
                write_fixture_root(tmp_root)
                missing_marker_case_count += 1

        exact_count_case_count = 0
        for rel, marker_counts in EXACT_COUNT_MARKERS.items():
            path = tmp_root / rel
            for marker, expected_count in marker_counts:
                mutate_file(path, lambda text, marker=marker: duplicate_first_marker(text, marker))
                expect_missing_marker(
                    f"duplicate_marker:{rel}:{marker}",
                    tmp_root,
                    f"{rel}: {marker}:expected={expected_count}:actual={expected_count + 1}",
                )
                write_fixture_root(tmp_root)
                exact_count_case_count += 1

        target_block_case_count = 0
        for marker in REQUIRED_PHASE7_VALIDATE_BLOCK_LINES:
            path = tmp_root / "zigux/Makefile"
            mutate_file(
                path,
                lambda text, marker=marker: relocate_makefile_marker_outside_target(
                    text, PHASE7_VALIDATE_TARGET, marker
                ),
            )
            expect_missing_marker(
                f"phase7_validate_block:{marker}",
                tmp_root,
                f"zigux/Makefile {PHASE7_VALIDATE_TARGET} block: {marker}:expected=1:actual=0",
            )
            write_fixture_root(tmp_root)
            target_block_case_count += 1

        forbidden_marker_case_count = 0
        for rel, markers in FORBIDDEN_MARKERS.items():
            path = tmp_root / rel
            for marker in markers:
                mutate_file(path, lambda text, marker=marker: text + marker + "\n")
                missing_files, missing_markers, forbidden_markers = validate(tmp_root)
                assert missing_files == [], f"forbidden_marker:{rel}:{marker}"
                assert missing_markers == [], f"forbidden_marker:{rel}:{marker}"
                assert f"{rel}: {marker}" in forbidden_markers, f"forbidden_marker:{rel}:{marker}"
                write_fixture_root(tmp_root)
                forbidden_marker_case_count += 1

    case_count = (
        missing_file_case_count
        + missing_marker_case_count
        + exact_count_case_count
        + target_block_case_count
        + forbidden_marker_case_count
    )
    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 7 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, forbidden_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_VALIDATION=fail")
        print("MISSING_PHASE7_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_VALIDATION=fail")
        print("MISSING_PHASE7_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_MARKERS_END")
        return 1

    if forbidden_markers:
        print("PHASE7_VALIDATION=fail")
        print("FORBIDDEN_PHASE7_MARKERS_START")
        for item in forbidden_markers:
            print(item)
        print("FORBIDDEN_PHASE7_MARKERS_END")
        return 1

    print("PHASE7_VALIDATION=pass")
    print(f"PHASE7_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
