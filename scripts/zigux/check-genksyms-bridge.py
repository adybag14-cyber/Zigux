#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


def derive_repo_root(script_path: Path) -> Path:
    return script_path.parents[2] if len(script_path.parents) >= 3 else script_path.parent


SELF_PATH = Path(__file__).resolve()
ROOT = derive_repo_root(SELF_PATH)

GENKSYMS_TOOL_REL = "scripts/zigux/genksyms.zig"
GENKSYMS_CHECKER_REL = "scripts/zigux/check-genksyms-bridge.py"
FIXTURE_ROOT_REL = "zigux/tests/fixtures/genksyms_bridge"
GENKSYMS_CASES_REL = f"{FIXTURE_ROOT_REL}/cases.json"
GENKSYMS_HARNESS_REL = f"{FIXTURE_ROOT_REL}/genksyms_bridge_c_harness.c"

EXPECTED_CASES = [
    {
        "name": "minimal",
        "argv": [],
        "mode": "stdout_json",
        "expected": "minimal_expected.json",
    },
    {
        "name": "debug_reference_types",
        "argv": [
            "-d",
            "-d",
            "-D",
            "-w",
            "-p",
            "-r",
            "foo.symref",
            "-r",
            "bar.symref",
            "-T",
            "out.symtypes",
        ],
        "mode": "stdout_json",
        "expected": "debug_reference_types_expected.json",
    },
    {
        "name": "long_options",
        "argv": [
            "--debug",
            "--warnings",
            "--quiet",
            "--reference=foo.symref",
            "--dump-types",
            "types.symtypes",
            "--preserve",
        ],
        "mode": "stdout_json",
        "expected": "long_options_expected.json",
    },
    {
        "name": "abbreviated_long_options",
        "argv": [
            "--deb",
            "--warn",
            "--qui",
            "--ref=foo.symref",
            "--dump-t",
            "types.symtypes",
            "--pres",
        ],
        "mode": "stdout_json",
        "expected": "abbreviated_long_options_expected.json",
    },
    {
        "name": "ambiguous_long_option",
        "argv": ["--d"],
        "mode": "process_json",
        "expected": "ambiguous_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "missing_long_reference_argument",
        "argv": ["--reference"],
        "mode": "process_json",
        "expected": "missing_long_reference_argument_expected.json",
    },
    {
        "name": "empty_inline_long_reference_argument",
        "argv": ["--reference="],
        "mode": "process_json",
        "expected": "missing_long_reference_argument_expected.json",
    },
    {
        "name": "long_version_before_missing_long_reference_argument",
        "argv": ["--version", "--reference"],
        "mode": "process_json",
        "expected": "version_before_missing_long_reference_argument_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_missing_long_reference_argument",
        "argv": ["--ver", "--reference"],
        "mode": "process_json",
        "expected": "version_before_missing_long_reference_argument_expected.json",
    },
    {
        "name": "missing_long_dump_types_argument",
        "argv": ["--dump-types"],
        "mode": "process_json",
        "expected": "missing_long_dump_types_argument_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_missing_long_dump_types_argument",
        "argv": ["--ver", "--dump-types"],
        "mode": "process_json",
        "expected": "version_before_missing_long_dump_types_argument_expected.json",
    },
    {
        "name": "empty_inline_abbreviated_long_dump_types_argument",
        "argv": ["--dump-t="],
        "mode": "process_json",
        "expected": "missing_long_dump_types_argument_expected.json",
    },
    {
        "name": "missing_short_dump_types_argument",
        "argv": ["-T"],
        "mode": "process_json",
        "expected": "missing_short_dump_types_argument_expected.json",
    },
    {
        "name": "unexpected_long_option_argument",
        "argv": ["--help=extra"],
        "mode": "process_json",
        "expected": "unexpected_long_option_argument_expected.json",
    },
    {
        "name": "long_version_before_unexpected_long_option_argument",
        "argv": ["--version", "--help=extra"],
        "mode": "process_json",
        "expected": "version_before_unexpected_long_option_argument_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_unexpected_long_option_argument",
        "argv": ["--ver", "--help=extra"],
        "mode": "process_json",
        "expected": "version_before_unexpected_long_option_argument_expected.json",
    },
    {
        "name": "version_before_invalid_short_option",
        "argv": ["-Vx"],
        "mode": "process_json",
        "expected": "version_before_invalid_short_option_expected.json",
    },
    {
        "name": "long_version_before_invalid_short_option",
        "argv": ["--version", "-x"],
        "mode": "process_json",
        "expected": "version_before_invalid_short_option_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_invalid_short_option",
        "argv": ["--ver", "-x"],
        "mode": "process_json",
        "expected": "version_before_invalid_short_option_expected.json",
    },
    {
        "name": "long_version_before_invalid_long_option",
        "argv": ["--version", "--unknown"],
        "mode": "process_json",
        "expected": "version_before_invalid_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "abbreviated_long_version_before_invalid_long_option",
        "argv": ["--ver", "--unknown"],
        "mode": "process_json",
        "expected": "version_before_invalid_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "version_before_missing_short_option_argument",
        "argv": ["-Vr"],
        "mode": "process_json",
        "expected": "version_before_missing_short_option_argument_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_missing_short_option_argument",
        "argv": ["--ver", "-r"],
        "mode": "process_json",
        "expected": "version_before_missing_short_option_argument_expected.json",
    },
    {
        "name": "version_before_short_help",
        "argv": ["-Vh"],
        "mode": "process_json",
        "expected": "version_before_short_help_expected.json",
    },
    {
        "name": "long_version_before_short_help",
        "argv": ["--version", "-h"],
        "mode": "process_json",
        "expected": "version_before_short_help_expected.json",
    },
    {
        "name": "version_before_long_help",
        "argv": ["-V", "--help"],
        "mode": "process_json",
        "expected": "version_before_long_help_expected.json",
    },
    {
        "name": "long_version_before_long_help",
        "argv": ["--version", "--help"],
        "mode": "process_json",
        "expected": "version_before_long_help_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_long_help",
        "argv": ["--ver", "--help"],
        "mode": "process_json",
        "expected": "version_before_long_help_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_short_help",
        "argv": ["--ver", "-h"],
        "mode": "process_json",
        "expected": "version_before_short_help_expected.json",
    },
    {
        "name": "repeated_version",
        "argv": ["-VV"],
        "mode": "process_json",
        "expected": "repeated_version_expected.json",
    },
    {
        "name": "repeated_long_version",
        "argv": ["--version", "--ver"],
        "mode": "process_json",
        "expected": "repeated_version_expected.json",
    },
    {
        "name": "unsupported_long_option",
        "argv": ["--unknown"],
        "mode": "process_json",
        "expected": "unsupported_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "too_many_reference_files",
        "argv": [
            "-r",
            "01.symref",
            "-r",
            "02.symref",
            "-r",
            "03.symref",
            "-r",
            "04.symref",
            "-r",
            "05.symref",
            "-r",
            "06.symref",
            "-r",
            "07.symref",
            "-r",
            "08.symref",
            "-r",
            "09.symref",
            "-r",
            "10.symref",
            "-r",
            "11.symref",
            "-r",
            "12.symref",
            "-r",
            "13.symref",
            "-r",
            "14.symref",
            "-r",
            "15.symref",
            "-r",
            "16.symref",
            "-r",
            "17.symref",
        ],
        "mode": "process_json",
        "expected": "too_many_reference_files_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "quiet_overrides_warning",
        "argv": ["-w", "-q"],
        "mode": "stdout_json",
        "expected": "quiet_overrides_warning_expected.json",
    },
    {
        "name": "long_version_before_missing_short_dump_types_argument",
        "argv": ["--version", "-T"],
        "mode": "process_json",
        "expected": "version_before_missing_short_dump_types_argument_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_missing_short_dump_types_argument",
        "argv": ["--ver", "-T"],
        "mode": "process_json",
        "expected": "version_before_missing_short_dump_types_argument_expected.json",
    },
    {
        "name": "explicit_option_terminator",
        "argv": ["-d", "leftover.c", "--", "--leftover", "positional"],
        "mode": "stdout_json",
        "expected": "explicit_option_terminator_expected.json",
    },
    {
        "name": "positional_passthrough",
        "argv": ["leftover.c", "-d", "rightover.h", "-r", "foo.symref"],
        "mode": "stdout_json",
        "expected": "positional_passthrough_expected.json",
    },
    {
        "name": "lone_dash_passthrough",
        "argv": ["-", "-d"],
        "mode": "stdout_json",
        "expected": "lone_dash_passthrough_expected.json",
    },
]

EXPECTED_OUTPUTS = {
    "minimal_expected.json": {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": ["scripts/genksyms/genksyms"],
        "options": {
            "debug_level": 0,
            "warnings": False,
            "dump_defs": False,
            "preserve": False,
            "reference_files": [],
            "dump_types_file": None,
        },
    },
    {
        "path":"zigux/tests/fixtures/genksyms_bridge/cases.json",
        "mode":"100644",
        "type":"blob",
        "content":"[
  {
    \"name\": \"minimal\",
    \"argv\": [],
    \"mode\": \"stdout_json\",
    \"expected\": \"minimal_expected.json\"
  },
  {
    \"name\": \"debug_reference_types\",
    \"argv\": [
      \"-d\",
      \"-d\",
      \"-D\",
      \"-w\",
      \"-p\",
      \"-r\",
      \"foo.symref\",
      \"-r\",
      \"bar.symref\",
      \"-T\",
      \"out.symtypes\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"debug_reference_types_expected.json\"
  },
  {
    \"name\": \"long_options\",
    \"argv\": [
      \"--debug\",
      \"--warnings\",
      \"--quiet\",
      \"--reference=foo.symref\",
      \"--dump-types\",
      \"types.symtypes\",
      \"--preserve\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"long_options_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_options\",
    \"argv\": [
      \"--deb\",
      \"--warn\",
      \"--qui\",
      \"--ref=foo.symref\",
      \"--dump-t\",
      \"types.symtypes\",
      \"--pres\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"abbreviated_long_options_expected.json\"
  },
  {
    \"name\": \"ambiguous_long_option\",
    \"argv\": [
      \"--d\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"ambiguous_long_option_expected.json\",
    \"normalize_stderr\": true
  },
  {
    \"name\": \"missing_long_reference_argument\",
    \"argv\": [
      \"--reference\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"missing_long_reference_argument_expected.json\"
  },
  {
    \"name\": \"empty_inline_long_reference_argument\",
    \"argv\": [
      \"--reference=\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"missing_long_reference_argument_expected.json\"
  },
  {
    \"name\": \"long_version_before_missing_long_reference_argument\",
    \"argv\": [
      \"--version\",
      \"--reference\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_long_reference_argument_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_missing_long_reference_argument\",
    \"argv\": [
      \"--ver\",
      \"--reference\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_long_reference_argument_expected.json\"
  },
  {
    \"name\": \"missing_long_dump_types_argument\",
    \"argv\": [
      \"--dump-types\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"missing_long_dump_types_argument_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_missing_long_dump_types_argument\",
    \"argv\": [
      \"--ver\",
      \"--dump-types\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_long_dump_types_argument_expected.json\"
  },
  {
    \"name\": \"empty_inline_abbreviated_long_dump_types_argument\",
    \"argv\": [
      \"--dump-t=\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"missing_long_dump_types_argument_expected.json\"
  },
  {
    \"name\": \"missing_short_dump_types_argument\",
    \"argv\": [
      \"-T\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"missing_short_dump_types_argument_expected.json\"
  },
  {
    \"name\": \"unexpected_long_option_argument\",
    \"argv\": [
      \"--help=extra\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"unexpected_long_option_argument_expected.json\"
  },
  {
    \"name\": \"long_version_before_unexpected_long_option_argument\",
    \"argv\": [
      \"--version\",
      \"--help=extra\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_unexpected_long_option_argument_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_unexpected_long_option_argument\",
    \"argv\": [
      \"--ver\",
      \"--help=extra\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_unexpected_long_option_argument_expected.json\"
  },
  {
    \"name\": \"version_before_invalid_short_option\",
    \"argv\": [
      \"-Vx\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_invalid_short_option_expected.json\"
  },
  {
    \"name\": \"long_version_before_invalid_short_option\",
    \"argv\": [
      \"--version\",
      \"-x\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_invalid_short_option_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_invalid_short_option\",
    \"argv\": [
      \"--ver\",
      \"-x\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_invalid_short_option_expected.json\"
  },
  {
    \"name\": \"long_version_before_invalid_long_option\",
    \"argv\": [
      \"--version\",
      \"--unknown\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_invalid_long_option_expected.json\",
    \"normalize_stderr\": true
  },
  {
    \"name\": \"abbreviated_long_version_before_invalid_long_option\",
    \"argv\": [
      \"--ver\",
      \"--unknown\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_invalid_long_option_expected.json\",
    \"normalize_stderr\": true
  },
  {
    \"name\": \"version_before_missing_short_option_argument\",
    \"argv\": [
      \"-Vr\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_short_option_argument_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_missing_short_option_argument\",
    \"argv\": [
      \"--ver\",
      \"-r\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_short_option_argument_expected.json\"
  },
  {
    \"name\": \"version_before_short_help\",
    \"argv\": [
      \"-Vh\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_short_help_expected.json\"
  },
  {
    \"name\": \"long_version_before_short_help\",
    \"argv\": [
      \"--version\",
      \"-h\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_short_help_expected.json\"
  },
  {
    \"name\": \"version_before_long_help\",
    \"argv\": [
      \"-V\",
      \"--help\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_long_help_expected.json\"
  },
  {
    \"name\": \"long_version_before_long_help\",
    \"argv\": [
      \"--version\",
      \"--help\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_long_help_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_long_help\",
    \"argv\": [
      \"--ver\",
      \"--help\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_long_help_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_short_help\",
    \"argv\": [
      \"--ver\",
      \"-h\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_short_help_expected.json\"
  },
  {
    \"name\": \"repeated_version\",
    \"argv\": [
      \"-VV\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"repeated_version_expected.json\"
  },
  {
    \"name\": \"repeated_long_version\",
    \"argv\": [
      \"--version\",
      \"--ver\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"repeated_version_expected.json\"
  },
  {
    \"name\": \"unsupported_long_option\",
    \"argv\": [
      \"--unknown\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"unsupported_long_option_expected.json\",
    \"normalize_stderr\": true
  },
  {
    \"name\": \"too_many_reference_files\",
    \"argv\": [
      \"-r\",
      \"01.symref\",
      \"-r\",
      \"02.symref\",
      \"-r\",
      \"03.symref\",
      \"-r\",
      \"04.symref\",
      \"-r\",
      \"05.symref\",
      \"-r\",
      \"06.symref\",
      \"-r\",
      \"07.symref\",
      \"-r\",
      \"08.symref\",
      \"-r\",
      \"09.symref\",
      \"-r\",
      \"10.symref\",
      \"-r\",
      \"11.symref\",
      \"-r\",
      \"12.symref\",
      \"-r\",
      \"13.symref\",
      \"-r\",
      \"14.symref\",
      \"-r\",
      \"15.symref\",
      \"-r\",
      \"16.symref\",
      \"-r\",
      \"17.symref\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"too_many_reference_files_expected.json\",
    \"normalize_stderr\": true
  },
  {
    \"name\": \"quiet_overrides_warning\",
    \"argv\": [
      \"-w\",
      \"-q\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"quiet_overrides_warning_expected.json\"
  },
  {
    \"name\": \"long_version_before_missing_short_dump_types_argument\",
    \"argv\": [
      \"--version\",
      \"-T\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_short_dump_types_argument_expected.json\"
  },
  {
    \"name\": \"abbreviated_long_version_before_missing_short_dump_types_argument\",
    \"argv\": [
      \"--ver\",
      \"-T\"
    ],
    \"mode\": \"process_json\",
    \"expected\": \"version_before_missing_short_dump_types_argument_expected.json\"
  },
  {
    \"name\": \"explicit_option_terminator\",
    \"argv\": [
      \"-d\",
      \"leftover.c\",
      \"--\",
      \"--leftover\",
      \"positional\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"explicit_option_terminator_expected.json\"
  },
  {
    \"name\": \"positional_passthrough\",
    \"argv\": [
      \"leftover.c\",
      \"-d\",
      \"rightover.h\",
      \"-r\",
      \"foo.symref\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"positional_passthrough_expected.json\"
  },
  {
    \"name\": \"lone_dash_passthrough\",
    \"argv\": [
      \"-\",
      \"-d\"
    ],
    \"mode\": \"stdout_json\",
    \"expected\": \"lone_dash_passthrough_expected.json\"
  }
]
"