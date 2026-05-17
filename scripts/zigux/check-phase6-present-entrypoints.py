#!/usr/bin/env python3
"""Guard the current Phase 6 helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

HELPER_EVIDENCE_CATALOG_PATH = Path(
    "Documentation/zigux/phase6-helper-evidence-catalog.md"
)
HELPER_EVIDENCE_MANIFEST_PATH = Path(
    "zigux/tests/phase6_helper_evidence_manifest.json"
)
CONTROL_SURFACE_GAP_SURVEY_PATH = Path(
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md"
)

REQUIRED_HELPER_PATHS = [
    Path("lib/base64.zig"),
    Path("lib/bsearch.zig"),
    Path("lib/checksum.zig"),
    Path("lib/hexdump.zig"),
]

REQUIRED_DIRECT_READBACK_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase6_build.zig",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
]

EXPECTED_CONTROL_SURFACE_GAP_SURVEY = {
    "survey_note": "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
    "roadmap_scope": [
        "lib/base64.c",
        "lib/bsearch.c",
        "lib/checksum.c",
        "lib/hexdump.c",
    ],
    "zar_runtime_command_surfaces": [
        "shell-run",
        "shell-expand",
        "tty-send",
        "tty-shell",
        "CMD",
        "EXEC",
        "APPSTATE",
        "APPRUN",
        "DISPLAYSET",
        "TRUSTSELECT",
        "RUNTIMESNAPSHOT",
        "RUNTIMESESSION",
    ],
    "zar_runtime_environment_surfaces": [
        "/runtime/tty/<name>/",
        "/dev/tty/sessions/<name>/{info,input,pending,stdout,stderr,events,transcript}",
        "/sys/tty/sessions/<name>/{info,input,pending,stdout,stderr,events,transcript}",
        "/runtime/state/runtime-state.json",
        "/runtime/workspaces/<name>.txt",
    ],
    "current_review_posture": "recorded as out-of-scope for the bounded Phase 6 leaf-helper tranche; later roadmap-backed tooling or runtime lanes may reuse the survey without widening this helper packet",
}
