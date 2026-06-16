const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "GENKSYMS_BRIDGE=pass";
pub const self_test_pass_marker = "GENKSYMS_BRIDGE_SELF_TEST=pass";

const MAKEFILE = [_][]const u8{
    "zigux/Makefile",
};

const WORKFLOW = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const GENKSYMS_ZIG = [_][]const u8{
    "scripts/zigux/genksyms.zig",
};

const VERSION_SIDE_EFFECT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
};

const AMBIGUOUS_VERSION_SIDE_EFFECT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
};

const INLINE_SHORT_ARGUMENT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
};

const REPEATED_VERSION_BEFORE_ABBREV_ARGUMENT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
};

const ABBREVIATED_WARNING_QUIET_TERMINATOR_TEST = [_][]const u8{
    "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
};

const HELP_FIXTURE = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
};

const CASES_FIXTURE = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
};

const MANIFEST_FIXTURE = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
};

const EXPECTED_PROCESS_OUTPUT_PACKET = [_][]const u8{
    "abbreviated_version_expected.json",
    "ambiguous_long_option_expected.json",
    "invalid_option_expected.json",
    "missing_long_dump_types_argument_expected.json",
    "missing_long_reference_argument_expected.json",
    "missing_reference_argument_expected.json",
    "too_many_reference_files_expected.json",
    "unsupported_long_option_expected.json",
    "unexpected_long_help_argument_expected.json",
    "abbreviated_unexpected_long_help_argument_expected.json",
};

const EXPECTED_HELPER_LOCAL_ANCHORS = [_][]const u8{
    "genksyms bridge treats pure version requests as version command",
    "genksyms bridge preserves repeated pure version invocations",
    "genksyms bridge preserves empty inline long reference argument",
    "genksyms bridge preserves empty inline abbreviated dump-types argument",
    "parseArgs reports ambiguous abbreviated long options",
    "genksyms bridge renders ambiguous long option failure like the fixture",
    "genksyms bridge renders invalid short option failure like the fixture",
    "genksyms bridge renders missing long option argument like the fixture",
    "genksyms bridge renders missing short option argument like the fixture",
    "genksyms bridge renders unexpected long option argument like the fixture",
    "genksyms bridge appends usage after getopt-style parse failures",
    "genksyms bridge leaves tool-local reference-limit failure message unchanged",
    "genksyms bridge keeps dash-prefixed long option arguments as data",
    "genksyms bridge keeps dash-prefixed short option arguments as data",
    "genksyms bridge rejects more than sixteen reference files like the C harness",
};

const REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = [_][]const u8{
    "test \"genksyms bridge preserves version side effect before invalid long option\" {",
    "test \"genksyms bridge preserves abbreviated version side effect before invalid long option\" {",
};

const REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES = [_][]const u8{
    "test \"genksyms bridge preserves version side effect before ambiguous long option\" {",
    "test \"genksyms bridge preserves abbreviated version side effect before ambiguous long option\" {",
};

const REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES = [_][]const u8{
    "test \"genksyms bridge accepts inline short option arguments\" {",
};

const HELP_USAGE = [_][]const u8{
    "Usage:\ngenksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver\n\n -d, --debug Increment the debug level (repeatable)\n -D, --dump Dump expanded symbol defs (for debugging only)\n -r, --reference file Read reference symbols from a file\n -T, --dump-types file Dump expanded types into file\n -p, --preserve Preserve reference modversions or fail\n -w, --warnings Enable warnings\n -q, --quiet Disable warnings (default)\n -h, --help Print this message\n -V, --version Print the release version\n",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig --self-test",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-genksyms",
};

const CASE_FIXTURES = [_][]const u8{
    "{name:minimal",
    "args:[]",
    "expected_file:minimal_expected.json}",
    "{name:debug_reference_types",
    "args:[-d",
    "-r",
    "ref.symvers",
    "-T",
    "types.symtypes]",
    "expected_file:debug_reference_types_expected.json",
    "}",
    "{name:inline_short_option_arguments",
    "args:[-d",
    "-rfoo.symref",
    "-Ttypes.symtypes]",
    "expected_file:inline_short_option_arguments_expected.json",
    "}",
    "{name:long_options",
    "args:[--debug",
    "--dump",
    "--reference=foo.symref",
    "--dump-types",
    "types.symtypes",
    "--preserve",
    "]",
    "expected_file:long_options_expected.json",
    "}",
    "{name:abbreviated_long_options",
    "args:[--deb",
    "--warn",
    "--qui",
    "--ref=foo.symref",
    "--dump-t",
    "types.symtypes",
    "--pres",
    "]",
    "expected_file:abbreviated_long_options_expected.json",
    "}",
    "{name:quiet_overrides_warning",
    "args:[--warnings",
    "--quiet",
    "--reference",
    "bar.symref]",
    "expected_file:quiet_overrides_warning_expected.json",
    "}",
    "{name:explicit_option_terminator",
    "args:[-d",
    "leftover.c",
    "--",
    "--leftover",
    "positional]",
    "expected_file:explicit_option_terminator_expected.json",
    "}",
    "{name:positional_passthrough",
    "args:[leftover.c",
    "-d",
    "rightover.h",
    "-r",
    "foo.symref]",
    "expected_file:positional_passthrough_expected.json",
    "}",
    "{name:lone_dash_passthrough",
    "args:[-",
    "-d]",
    "expected_file:lone_dash_passthrough_expected.json",
    "}",
    "{name:dash_prefixed_long_option_arguments_as_data",
    "args:[--reference",
    "--debug",
    "--dump-types",
    "--types]",
    "expected_file:dash_prefixed_long_option_arguments_as_data_expected.json",
    "}",
    "{name:dash_prefixed_short_option_arguments_as_data",
    "args:[-r",
    "-d",
    "-T",
    "--symtypes]",
    "expected_file:dash_prefixed_short_option_arguments_as_data_expected.json",
    "}",
};

const STANDALONE_PROOF_PACKET = [_][]const u8{
    "VERSION_SIDE_EFFECT_TEST",
    "AMBIGUOUS_VERSION_SIDE_EFFECT_TEST",
    "INLINE_SHORT_ARGUMENT_TEST",
    "REPEATED_VERSION_BEFORE_ABBREV_ARGUMENT_TEST",
    "ABBREVIATED_WARNING_QUIET_TERMINATOR_TEST",
};

const LONG_OPTION_SPECS = [_][]const u8{
    "helphelp",
    "versionversion",
    "debugdebug",
    "warningswarnings",
    "quietquiet",
    "dumpdump",
    "referencereference",
    "dump-typesdump-types",
    "preservepreserve",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_path);
    const text_makefile = try guard.readUtf8File(io, allocator, text_makefile_path);
    defer allocator.free(text_makefile);
    for (MAKEFILE) |marker| try guard.requireMarker(text_makefile, marker);
    const text_workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_path);
    const text_workflow = try guard.readUtf8File(io, allocator, text_workflow_path);
    defer allocator.free(text_workflow);
    for (WORKFLOW) |marker| try guard.requireMarker(text_workflow, marker);
    const text_genksyms_zig_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_zig_path);
    const text_genksyms_zig = try guard.readUtf8File(io, allocator, text_genksyms_zig_path);
    defer allocator.free(text_genksyms_zig);
    for (GENKSYMS_ZIG) |marker| try guard.requireMarker(text_genksyms_zig, marker);
    const text_version_side_effect_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_version_side_effect_test_path);
    const text_version_side_effect_test = try guard.readUtf8File(io, allocator, text_version_side_effect_test_path);
    defer allocator.free(text_version_side_effect_test);
    for (VERSION_SIDE_EFFECT_TEST) |marker| try guard.requireMarker(text_version_side_effect_test, marker);
    const text_ambiguous_version_side_effect_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_ambiguous_version_side_effect_test_path);
    const text_ambiguous_version_side_effect_test = try guard.readUtf8File(io, allocator, text_ambiguous_version_side_effect_test_path);
    defer allocator.free(text_ambiguous_version_side_effect_test);
    for (AMBIGUOUS_VERSION_SIDE_EFFECT_TEST) |marker| try guard.requireMarker(text_ambiguous_version_side_effect_test, marker);
    const text_inline_short_argument_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_inline_short_argument_test_path);
    const text_inline_short_argument_test = try guard.readUtf8File(io, allocator, text_inline_short_argument_test_path);
    defer allocator.free(text_inline_short_argument_test);
    for (INLINE_SHORT_ARGUMENT_TEST) |marker| try guard.requireMarker(text_inline_short_argument_test, marker);
    const text_repeated_version_before_abbrev_argument_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_repeated_version_before_abbrev_argument_test_path);
    const text_repeated_version_before_abbrev_argument_test = try guard.readUtf8File(io, allocator, text_repeated_version_before_abbrev_argument_test_path);
    defer allocator.free(text_repeated_version_before_abbrev_argument_test);
    for (REPEATED_VERSION_BEFORE_ABBREV_ARGUMENT_TEST) |marker| try guard.requireMarker(text_repeated_version_before_abbrev_argument_test, marker);
    const text_abbreviated_warning_quiet_terminator_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_abbreviated_warning_quiet_terminator_test_path);
    const text_abbreviated_warning_quiet_terminator_test = try guard.readUtf8File(io, allocator, text_abbreviated_warning_quiet_terminator_test_path);
    defer allocator.free(text_abbreviated_warning_quiet_terminator_test);
    for (ABBREVIATED_WARNING_QUIET_TERMINATOR_TEST) |marker| try guard.requireMarker(text_abbreviated_warning_quiet_terminator_test, marker);
    const text_help_fixture_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_help_fixture_path);
    const text_help_fixture = try guard.readUtf8File(io, allocator, text_help_fixture_path);
    defer allocator.free(text_help_fixture);
    for (HELP_FIXTURE) |marker| try guard.requireMarker(text_help_fixture, marker);
    const text_cases_fixture_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_cases_fixture_path);
    const text_cases_fixture = try guard.readUtf8File(io, allocator, text_cases_fixture_path);
    defer allocator.free(text_cases_fixture);
    for (CASES_FIXTURE) |marker| try guard.requireMarker(text_cases_fixture, marker);
    const text_manifest_fixture_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_manifest_fixture_path);
    const text_manifest_fixture = try guard.readUtf8File(io, allocator, text_manifest_fixture_path);
    defer allocator.free(text_manifest_fixture);
    for (MANIFEST_FIXTURE) |marker| try guard.requireMarker(text_manifest_fixture, marker);
    const text_expected_process_output_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_process_output_packet_path);
    const text_expected_process_output_packet = try guard.readUtf8File(io, allocator, text_expected_process_output_packet_path);
    defer allocator.free(text_expected_process_output_packet);
    for (EXPECTED_PROCESS_OUTPUT_PACKET) |marker| try guard.requireMarker(text_expected_process_output_packet, marker);
    const text_expected_helper_local_anchors_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_helper_local_anchors_path);
    const text_expected_helper_local_anchors = try guard.readUtf8File(io, allocator, text_expected_helper_local_anchors_path);
    defer allocator.free(text_expected_helper_local_anchors);
    for (EXPECTED_HELPER_LOCAL_ANCHORS) |marker| try guard.requireMarker(text_expected_helper_local_anchors, marker);
    const text_required_version_side_effect_test_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_version_side_effect_test_lines_path);
    const text_required_version_side_effect_test_lines = try guard.readUtf8File(io, allocator, text_required_version_side_effect_test_lines_path);
    defer allocator.free(text_required_version_side_effect_test_lines);
    for (REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES) |marker| try guard.requireExactLineCount(text_required_version_side_effect_test_lines, marker, 1);
    const text_required_ambiguous_version_side_effect_test_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_ambiguous_version_side_effect_test_lines_path);
    const text_required_ambiguous_version_side_effect_test_lines = try guard.readUtf8File(io, allocator, text_required_ambiguous_version_side_effect_test_lines_path);
    defer allocator.free(text_required_ambiguous_version_side_effect_test_lines);
    for (REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES) |marker| try guard.requireExactLineCount(text_required_ambiguous_version_side_effect_test_lines, marker, 1);
    const text_required_inline_short_argument_test_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_inline_short_argument_test_lines_path);
    const text_required_inline_short_argument_test_lines = try guard.readUtf8File(io, allocator, text_required_inline_short_argument_test_lines_path);
    defer allocator.free(text_required_inline_short_argument_test_lines);
    for (REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES) |marker| try guard.requireExactLineCount(text_required_inline_short_argument_test_lines, marker, 1);
    const text_help_usage_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_help_usage_path);
    const text_help_usage = try guard.readUtf8File(io, allocator, text_help_usage_path);
    defer allocator.free(text_help_usage);
    for (HELP_USAGE) |marker| try guard.requireMarker(text_help_usage, marker);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
    const text_case_fixtures_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_case_fixtures_path);
    const text_case_fixtures = try guard.readUtf8File(io, allocator, text_case_fixtures_path);
    defer allocator.free(text_case_fixtures);
    for (CASE_FIXTURES) |marker| try guard.requireMarker(text_case_fixtures, marker);
    const text_standalone_proof_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_standalone_proof_packet_path);
    const text_standalone_proof_packet = try guard.readUtf8File(io, allocator, text_standalone_proof_packet_path);
    defer allocator.free(text_standalone_proof_packet);
    for (STANDALONE_PROOF_PACKET) |marker| try guard.requireMarker(text_standalone_proof_packet, marker);
    const text_long_option_specs_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_long_option_specs_path);
    const text_long_option_specs = try guard.readUtf8File(io, allocator, text_long_option_specs_path);
    defer allocator.free(text_long_option_specs);
    for (LONG_OPTION_SPECS) |marker| try guard.requireMarker(text_long_option_specs, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
