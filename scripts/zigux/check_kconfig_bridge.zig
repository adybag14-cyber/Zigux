const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "KCONFIG_BRIDGE_DIFF=pass";
pub const self_test_pass_marker = "KCONFIG_BRIDGE_SELF_TEST=pass";

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "pub fn runConfBridge",
    "conf bridge mode surface stays aligned with conf.c long options",
    "conf bridge emits olddefconfig argv and env",
    "conf bridge emits syncconfig auto files",
    "conf bridge emits syncconfig nosilentupdate when present",
    "conf bridge omits empty syncconfig nosilentupdate",
    "conf bridge emits silent flag before mode flag",
    "conf bridge emits alldefconfig argv and env",
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
    "conf bridge emits yes2modconfig argv and env",
    "conf bridge emits defconfig mode argument before kconfig",
    "conf bridge emits savedefconfig mode argument before kconfig",
    "conf bridge escapes low control bytes in JSON strings",
    "mode argument validation rejects bridge option shaped defconfig payload",
    "mode argument validation accepts defconfig path that only starts with silent",
    "mode argument validation still accepts ordinary path text with equals",
    "bridge options parser accepts explicit allconfig override for allmodconfig",
    "bridge options parser accepts syncconfig nosilentupdate",
    "bridge options parser keeps empty syncconfig nosilentupdate unset",
    "bridge options parser accepts generic silent flag",
    "bridge options parser accepts silent alongside randconfig options",
    "bridge options parser rejects duplicate silent flag",
    "bridge options parser rejects duplicate randconfig probability",
    "bridge options parser rejects unexpected options for mode",
    "bridge options parser keeps empty randconfig tunables unset",
    "bridge options parser rejects duplicate mode specific options",
};

const markers_1 = [_][]const u8{
    "\"case_count\": 16",
    "oldaskconfig",
    "syncconfig",
    "oldconfig",
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
    "defconfig",
    "savedefconfig",
    "listnewconfig",
    "helpnewconfig",
    "olddefconfig",
    "yes2modconfig",
    "mod2yesconfig",
    "mod2noconfig",
    "oldaskconfig_expected.json",
    "syncconfig_expected.json",
    "oldconfig_expected.json",
    "allnoconfig_expected.json",
    "allyesconfig_expected.json",
    "allmodconfig_expected.json",
    "alldefconfig_expected.json",
    "randconfig_expected.json",
    "defconfig_expected.json",
    "savedefconfig_expected.json",
    "listnewconfig_expected.json",
    "helpnewconfig_expected.json",
    "olddefconfig_expected.json",
    "yes2modconfig_expected.json",
    "mod2yesconfig_expected.json",
    "mod2noconfig_expected.json",
    "conf bridge mode surface stays aligned with conf.c long options",
    "conf bridge emits olddefconfig argv and env",
    "conf bridge emits syncconfig auto files",
    "conf bridge emits syncconfig nosilentupdate when present",
    "conf bridge omits empty syncconfig nosilentupdate",
    "conf bridge emits silent flag before mode flag",
    "conf bridge emits alldefconfig argv and env",
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
    "conf bridge emits yes2modconfig argv and env",
    "conf bridge emits defconfig mode argument before kconfig",
    "conf bridge emits savedefconfig mode argument before kconfig",
    "conf bridge escapes low control bytes in JSON strings",
    "mode argument validation rejects bridge option shaped defconfig payload",
    "mode argument validation accepts defconfig path that only starts with silent",
    "mode argument validation still accepts ordinary path text with equals",
    "bridge options parser accepts explicit allconfig override for allmodconfig",
    "bridge options parser accepts syncconfig nosilentupdate",
    "bridge options parser keeps empty syncconfig nosilentupdate unset",
    "bridge options parser accepts generic silent flag",
    "bridge options parser accepts silent alongside randconfig options",
    "bridge options parser rejects duplicate silent flag",
    "bridge options parser rejects duplicate randconfig probability",
    "bridge options parser rejects unexpected options for mode",
    "bridge options parser keeps empty randconfig tunables unset",
    "bridge options parser rejects duplicate mode specific options",
};

const markers_2 = [_][]const u8{
    "pub fn runConfdataBridge",
    "confdata bridge parses bounded config states",
    "confdata bridge emits bounded json output",
    "confdata bridge decodes escaped quoted strings",
    "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
    "confdata bridge escapes low control bytes in json output",
    "confdata bridge accepts CRLF config lines",
    "confdata bridge preserves trailing carriage return on final unterminated value line",
    "confdata bridge ignores unterminated unset comment with trailing carriage return",
    "confdata bridge ignores suffix bytes after an embedded NUL",
    "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines",
    "confdata bridge keeps explicit n assignments as tristate values",
    "confdata bridge recognizes uppercase tristate assignments",
    "confdata bridge ignores non-CONFIG lines like upstream confdata",
    "confdata bridge ignores empty CONFIG symbol names",
    "confdata bridge ignores malformed unset comments with extra tokens",
    "confdata bridge keeps trailing escaped backslashes in quoted strings",
    "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata",
    "confdata bridge ignores malformed quoted values like upstream confdata",
    "confdata bridge emits no entries for empty CONFIG symbol names",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
    "confdata bridge emits the preserved duplicate state after later malformed quoted assignments",
    "confdata bridge keeps only the last state across unset and set transitions",
    "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
    "confdata bridge emits explicit empty assignments distinctly in json output",
    "confdata bridge escapes parsed string bytes in json output",
    "confdata bridge emits auto.conf symbol export lines",
    "confdata bridge emits autoconf header symbol export lines",
    "confdata bridge keeps explicit n out of autoconf header exports",
    "confdata bridge parses explicit output modes",
    "confdata bridge rejects unknown output modes",
    "confdata bridge emits auto.conf output through the explicit mode surface",
    "confdata bridge emits autoconf header output through the explicit mode surface",
    "confdata bridge file reader accepts config inputs beyond one mebibyte",
    "confdata bridge releases appended entry ownership on index-allocation failure",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
};

const markers_3 = [_][]const u8{
    "\"case_count\": 16",
    "sample",
    "escaped_strings",
    "escaped_control_sequences",
    "trailing_escaped_backslash",
    "sample_crlf",
    "explicit_n_tristate",
    "final_trailing_carriage_return",
    "final_unterminated_unset_comment",
    "uppercase_tristate",
    "non_config_lines",
    "empty_config_symbol_names",
    "malformed_unset_comment_tokens",
    "last_state_transitions",
    "duplicate_assignments",
    "duplicate_malformed_quoted_assignment",
    "explicit_empty_assignments",
    "sample.config",
    "escaped_strings.config",
    "escaped_control_sequences.config",
    "trailing_escaped_backslash.config",
    "sample_crlf.config",
    "explicit_n_tristate.config",
    "final_trailing_carriage_return.config",
    "final_unterminated_unset_comment.config",
    "uppercase_tristate.config",
    "non_config_lines.config",
    "empty_config_symbol_names.config",
    "malformed_unset_comment_tokens.config",
    "last_state_transitions.config",
    "duplicate_assignments.config",
    "duplicate_malformed_quoted_assignment.config",
    "explicit_empty_assignments.config",
    "sample_expected.json",
    "escaped_strings_expected.json",
    "escaped_control_sequences_expected.json",
    "trailing_escaped_backslash_expected.json",
    "sample_crlf_expected.json",
    "explicit_n_tristate_expected.json",
    "final_trailing_carriage_return_expected.json",
    "final_unterminated_unset_comment_expected.json",
    "uppercase_tristate_expected.json",
    "non_config_lines_expected.json",
    "empty_config_symbol_names_expected.json",
    "malformed_unset_comment_tokens_expected.json",
    "last_state_transitions_expected.json",
    "duplicate_assignments_expected.json",
    "duplicate_malformed_quoted_assignment_expected.json",
    "explicit_empty_assignments_expected.json",
    "confdata bridge parses bounded config states",
    "confdata bridge emits bounded json output",
    "confdata bridge decodes escaped quoted strings",
    "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
    "confdata bridge escapes low control bytes in json output",
    "confdata bridge accepts CRLF config lines",
    "confdata bridge preserves trailing carriage return on final unterminated value line",
    "confdata bridge ignores unterminated unset comment with trailing carriage return",
    "confdata bridge ignores suffix bytes after an embedded NUL",
    "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines",
    "confdata bridge keeps explicit n assignments as tristate values",
    "confdata bridge recognizes uppercase tristate assignments",
    "confdata bridge ignores non-CONFIG lines like upstream confdata",
    "confdata bridge ignores empty CONFIG symbol names",
    "confdata bridge ignores malformed unset comments with extra tokens",
    "confdata bridge keeps trailing escaped backslashes in quoted strings",
    "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata",
    "confdata bridge ignores malformed quoted values like upstream confdata",
    "confdata bridge emits no entries for empty CONFIG symbol names",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
    "confdata bridge emits the preserved duplicate state after later malformed quoted assignments",
    "confdata bridge keeps only the last state across unset and set transitions",
    "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
    "confdata bridge emits explicit empty assignments distinctly in json output",
    "confdata bridge escapes parsed string bytes in json output",
    "confdata bridge emits auto.conf symbol export lines",
    "confdata bridge emits autoconf header symbol export lines",
    "confdata bridge keeps explicit n out of autoconf header exports",
    "confdata bridge parses explicit output modes",
    "confdata bridge rejects unknown output modes",
    "confdata bridge emits auto.conf output through the explicit mode surface",
    "confdata bridge emits autoconf header output through the explicit mode surface",
    "confdata bridge file reader accepts config inputs beyond one mebibyte",
    "confdata bridge releases appended entry ownership on index-allocation failure",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
};

const markers_4 = [_][]const u8{
    "\"conf_cases\"",
    "\"confdata_cases\"",
    "oldaskconfig",
    "oldaskconfig_expected.json",
    "syncconfig",
    "syncconfig_expected.json",
    "1",
    "oldconfig",
    "oldconfig_expected.json",
    "allnoconfig",
    "allnoconfig_expected.json",
    "allyesconfig",
    "allyesconfig_expected.json",
    "allmodconfig",
    "allmodconfig_expected.json",
    "alldefconfig",
    "alldefconfig_expected.json",
    "mini-all.config",
    "randconfig",
    "randconfig_expected.json",
    "0xC0FFEE",
    "15:25",
    "defconfig",
    "defconfig_expected.json",
    "arch/arm64/configs/defconfig",
    "savedefconfig",
    "savedefconfig_expected.json",
    "silent=debug_defconfig",
    "listnewconfig",
    "listnewconfig_expected.json",
    "helpnewconfig",
    "helpnewconfig_expected.json",
    "olddefconfig",
    "olddefconfig_expected.json",
    "yes2modconfig",
    "yes2modconfig_expected.json",
    "mod2yesconfig",
    "mod2yesconfig_expected.json",
    "mod2noconfig",
    "mod2noconfig_expected.json",
    "sample",
    "sample.config",
    "sample_expected.json",
    "escaped_strings",
    "escaped_strings.config",
    "escaped_strings_expected.json",
    "escaped_control_sequences",
    "escaped_control_sequences.config",
    "escaped_control_sequences_expected.json",
    "trailing_escaped_backslash",
    "trailing_escaped_backslash.config",
    "trailing_escaped_backslash_expected.json",
    "sample_crlf",
    "sample_crlf.config",
    "sample_crlf_expected.json",
    "explicit_n_tristate",
    "explicit_n_tristate.config",
    "explicit_n_tristate_expected.json",
    "final_trailing_carriage_return",
    "final_trailing_carriage_return.config",
    "final_trailing_carriage_return_expected.json",
    "final_unterminated_unset_comment",
    "final_unterminated_unset_comment.config",
    "final_unterminated_unset_comment_expected.json",
    "uppercase_tristate",
    "uppercase_tristate.config",
    "uppercase_tristate_expected.json",
    "non_config_lines",
    "non_config_lines.config",
    "non_config_lines_expected.json",
    "empty_config_symbol_names",
    "empty_config_symbol_names.config",
    "empty_config_symbol_names_expected.json",
    "malformed_unset_comment_tokens",
    "malformed_unset_comment_tokens.config",
    "malformed_unset_comment_tokens_expected.json",
    "last_state_transitions",
    "last_state_transitions.config",
    "last_state_transitions_expected.json",
    "duplicate_assignments",
    "duplicate_assignments.config",
    "duplicate_assignments_expected.json",
    "duplicate_malformed_quoted_assignment",
    "duplicate_malformed_quoted_assignment.config",
    "duplicate_malformed_quoted_assignment_expected.json",
    "explicit_empty_assignments",
    "explicit_empty_assignments.config",
    "explicit_empty_assignments_expected.json",
};

const markers_5 = [_][]const u8{
    "run: zig run check_kconfig_bridge.zig --self-test",
    "run: zig run check_kconfig_bridge.zig",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/kconfig/conf_bridge.zig", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json", .markers = &markers_1 },
    .{ .rel = "scripts/zigux/kconfig/confdata_bridge.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json", .markers = &markers_3 },
    .{ .rel = "zigux/tests/fixtures/kconfig_bridge/cases.json", .markers = &markers_4 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_5 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
