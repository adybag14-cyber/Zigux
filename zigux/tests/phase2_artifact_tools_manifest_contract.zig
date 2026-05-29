const std = @import("std");

const manifest_text =
    \\\{
    \\\  "phase": "Phase 2",
    \\\  "status": "active",
    \\\  "scope": "artifact-diff support for fixture-backed scripts/zigux validation",
    \\\  "tooling": {
    \\\    "primary": [
    \\\      "scripts/zigux/artifact_diff.py"
    \\\    ],
    \\\    "consumers": [
    \\\      "scripts/zigux/check-kconfig-bridge.py",
    \\\      "scripts/zigux/check-fixdep-diff.py"
    \\\    ],
    \\\    "checkers": [
    \\\      "scripts/zigux/check-phase2-artifact-tools-manifest.py"
    \\\    ],
    \\\    "supported_modes": [
    \\\      "text",
    \\\      "json",
    \\\      "bytes"
    \\\    ]
    \\\  },
    \\\  "notes": [
    \\\    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    \\\    "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    \\\    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    \\\    "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`."
    \\\  ]
    \\\}
;

const manifest_checker_markers = [_][]const u8{
    "MANIFEST = Path(\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\")",
    "PRIMARY_TOOL = Path(\"scripts/zigux/artifact_diff.py\")",
    "\"scripts/zigux/check-kconfig-bridge.py\"",
    "\"scripts/zigux/check-fixdep-diff.py\"",
    "\"checkers\": [\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"]",
    "\"supported_modes\": [\"text\", \"json\", \"bytes\"]",
    "PRIMARY_TOOL_MARKERS = (",
    "EXPECTED_CONSUMER_MARKERS = {",
    "PHASE2_ARTIFACT_TOOLS_MANIFEST=pass",
    "PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_NOTE_COUNT=",
    "PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_TOOL_PATH_COUNT=",
};

const artifact_diff_markers = [_][]const u8{
    "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
    "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
    "\"legacy_sha256_alias\"",
    "def normalize_mode(mode: str) -> str:",
    "return LEGACY_MODE_ALIASES.get(mode, mode)",
};

const validator_route_markers = [_][]const u8{
    "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
    "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\"",
    "\"scripts/zigux/artifact_diff.py\"",
    "\"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py\"",
};

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
    }
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var offset: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[offset..], needle) orelse return error.MarkerOutOfOrder;
        offset += found + needle.len;
    }
}

test "artifact tools manifest keeps the current Phase 2 packet explicit" {
    const required_top_level = [_][]const u8{
        "\"phase\": \"Phase 2\"",
        "\"status\": \"active\"",
        "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"",
    };
    const required_paths = [_][]const u8{
        "\"scripts/zigux/artifact_diff.py\"",
        "\"scripts/zigux/check-kconfig-bridge.py\"",
        "\"scripts/zigux/check-fixdep-diff.py\"",
        "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
    };
    const required_modes = [_][]const u8{
        "\"text\"",
        "\"json\"",
        "\"bytes\"",
    };

    try expectContainsAll(manifest_text, &required_top_level);
    try expectContainsAll(manifest_text, &required_paths);
    try expectContainsAll(manifest_text, &required_modes);
    try expectOrdered(manifest_text, &required_paths);
    try expectOrdered(manifest_text, &required_modes);
}

test "artifact tools notes preserve bounded follow-up and sha256 alias guidance" {
    const required_notes = [_][]const u8{
        "deterministic comparison output for fixture-backed scripts-root checks",
        "fails closed beside the broader Phase 2 tool packet",
        "bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py`",
        "legacy `sha256` compatibility alias explicit",
    };

    try expectContainsAll(manifest_text, &required_notes);
    try expectOrdered(manifest_text, &required_notes);
}

test "manifest checker guards primary tool, consumers, modes, and pass sentinels" {
    const checker_surface =
        \\\MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
        \\\PRIMARY_TOOL = Path("scripts/zigux/artifact_diff.py")
        \\\"scripts/zigux/check-kconfig-bridge.py"
        \\\"scripts/zigux/check-fixdep-diff.py"
        \\\"checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"]
        \\\"supported_modes": ["text", "json", "bytes"]
        \\\PRIMARY_TOOL_MARKERS = (
        \\\EXPECTED_CONSUMER_MARKERS = {
        \\\PHASE2_ARTIFACT_TOOLS_MANIFEST=pass
        \\\PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_NOTE_COUNT=
        \\\PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_TOOL_PATH_COUNT=
    ;

    try expectContainsAll(checker_surface, &manifest_checker_markers);
}

test "artifact diff keeps bytes mode and legacy sha256 alias explicit" {
    const artifact_diff_surface =
        \\\MODE_CHOICES = ("text", "json", "bytes")
        \\\LEGACY_MODE_ALIASES = {"sha256": "bytes"}
        \\\"legacy_sha256_alias"
        \\\def normalize_mode(mode: str) -> str:
        \\\    return LEGACY_MODE_ALIASES.get(mode, mode)
    ;

    try expectContainsAll(artifact_diff_surface, &artifact_diff_markers);
}

test "Phase 2 validator keeps artifact tools in required paths and action routes" {
    const validator_surface =
        \\\"scripts/zigux/check-phase2-artifact-tools-manifest.py"
        \\\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json"
        \\\"scripts/zigux/artifact_diff.py"
        \\\"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test"
        \\\"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py"
        \\\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py"
    ;

    try expectContainsAll(validator_surface, &validator_route_markers);
}
