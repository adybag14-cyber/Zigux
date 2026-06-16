const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "KCONFIG_BRIDGE_DIFF=pass";
pub const self_test_pass_marker = "KCONFIG_BRIDGE_SELF_TEST=pass";

const REQUIRED_CONF_HELPER_ANCHORS = [_][]const u8{
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

const REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES = [_][]const u8{
    "allmodconfig",
    "randconfig",
};

const REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES = [_][]const u8{
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

const REQUIRED_CONFDATA_HELPER_ANCHORS = [_][]const u8{
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

const SAMPLE_CONF_CASES = [_][]const u8{
    "{name:oldaskconfig",
    "mode:oldaskconfig",
    "kconfig:Kconfig",
    "config:ask/.config",
    "arch:x86_64",
    "expected:oldaskconfig_expected.json}",
    "{name:syncconfig",
    "mode:syncconfig",
    "kconfig:Kconfig",
    "config:out/.config",
    "arch:riscv64",
    "nosilentupdate:1",
    "expected:syncconfig_expected.json}",
    "{name:oldconfig",
    "mode:oldconfig",
    "kconfig:Kconfig",
    "config:refresh/.config",
    "arch:x86",
    "expected:oldconfig_expected.json}",
    "{name:allnoconfig",
    "mode:allnoconfig",
    "kconfig:Kconfig",
    "config:none/.config",
    "arch:arm64",
    "expected:allnoconfig_expected.json}",
    "{name:allyesconfig",
    "mode:allyesconfig",
    "kconfig:Kconfig",
    "config:yes/.config",
    "arch:arm64",
    "expected:allyesconfig_expected.json}",
    "{name:allmodconfig",
    "mode:allmodconfig",
    "kconfig:Kconfig",
    "config:mod/.config",
    "arch:arm",
    "allconfig:",
    "expected:allmodconfig_expected.json}",
    "{name:alldefconfig",
    "mode:alldefconfig",
    "kconfig:Kconfig",
    "config:build/.config",
    "arch:arm64",
    "allconfig:mini-all.config",
    "expected:alldefconfig_expected.json}",
    "{name:randconfig",
    "mode:randconfig",
    "kconfig:Kconfig",
    "config:rand/.config",
    "arch:x86_64",
    "allconfig:",
    "seed:0xC0FFEE",
    "probability:15:25",
    "expected:randconfig_expected.json}",
    "{name:defconfig",
    "mode:defconfig",
    "kconfig:Kconfig",
    "config:out/.config",
    "arch:arm64",
    "mode_arg:arch/arm64/configs/defconfig",
    "expected:defconfig_expected.json}",
    "{name:savedefconfig",
    "mode:savedefconfig",
    "kconfig:Kconfig",
    "config:.config",
    "arch:x86_64",
    "mode_arg:silent=debug_defconfig",
    "expected:savedefconfig_expected.json}",
    "{name:listnewconfig",
    "mode:listnewconfig",
    "kconfig:Kconfig",
    "config:out/list.config",
    "arch:x86_64",
    "silent:True",
    "expected:listnewconfig_expected.json}",
    "{name:helpnewconfig",
    "mode:helpnewconfig",
    "kconfig:Kconfig",
    "config:out/help.config",
    "arch:riscv64",
    "silent:True",
    "expected:helpnewconfig_expected.json}",
    "{name:olddefconfig",
    "mode:olddefconfig",
    "kconfig:Kconfig",
    "config:.config",
    "arch:x86_64",
    "expected:olddefconfig_expected.json}",
    "{name:yes2modconfig",
    "mode:yes2modconfig",
    "kconfig:Kconfig",
    "config:rewrite/.config",
    "arch:x86",
    "expected:yes2modconfig_expected.json}",
    "{name:mod2yesconfig",
    "mode:mod2yesconfig",
    "kconfig:Kconfig",
    "config:promote/.config",
    "arch:x86",
    "expected:mod2yesconfig_expected.json}",
    "{name:mod2noconfig",
    "mode:mod2noconfig",
    "kconfig:Kconfig",
    "config:demote/.config",
    "arch:x86",
    "expected:mod2noconfig_expected.json}",
};

const SAMPLE_CONFDATA_CASES = [_][]const u8{
    "{name:sample",
    "input:sample.config",
    "expected:sample_expected.json}",
    "{name:escaped_strings",
    "input:escaped_strings.config",
    "expected:escaped_strings_expected.json}",
    "{name:escaped_control_sequences",
    "input:escaped_control_sequences.config",
    "expected:escaped_control_sequences_expected.json}",
    "{name:trailing_escaped_backslash",
    "input:trailing_escaped_backslash.config",
    "expected:trailing_escaped_backslash_expected.json}",
    "{name:sample_crlf",
    "input:sample_crlf.config",
    "expected:sample_crlf_expected.json}",
    "{name:explicit_n_tristate",
    "input:explicit_n_tristate.config",
    "expected:explicit_n_tristate_expected.json}",
    "{name:final_trailing_carriage_return",
    "input:final_trailing_carriage_return.config",
    "expected:final_trailing_carriage_return_expected.json}",
    "{name:final_unterminated_unset_comment",
    "input:final_unterminated_unset_comment.config",
    "expected:final_unterminated_unset_comment_expected.json}",
    "{name:uppercase_tristate",
    "input:uppercase_tristate.config",
    "expected:uppercase_tristate_expected.json}",
    "{name:non_config_lines",
    "input:non_config_lines.config",
    "expected:non_config_lines_expected.json}",
    "{name:empty_config_symbol_names",
    "input:empty_config_symbol_names.config",
    "expected:empty_config_symbol_names_expected.json}",
    "{name:malformed_unset_comment_tokens",
    "input:malformed_unset_comment_tokens.config",
    "expected:malformed_unset_comment_tokens_expected.json}",
    "{name:last_state_transitions",
    "input:last_state_transitions.config",
    "expected:last_state_transitions_expected.json}",
    "{name:duplicate_assignments",
    "input:duplicate_assignments.config",
    "expected:duplicate_assignments_expected.json}",
    "{name:duplicate_malformed_quoted_assignment",
    "input:duplicate_malformed_quoted_assignment.config",
    "expected:duplicate_malformed_quoted_assignment_expected.json}",
    "{name:explicit_empty_assignments",
    "input:explicit_empty_assignments.config",
    "expected:explicit_empty_assignments_expected.json}",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_conf_helper_anchors_path = try guard.joinPath(allocator, root, "scripts/zigux/artifact_diff.zig");
    defer allocator.free(text_required_conf_helper_anchors_path);
    const text_required_conf_helper_anchors = try guard.readUtf8File(io, allocator, text_required_conf_helper_anchors_path);
    defer allocator.free(text_required_conf_helper_anchors);
    for (REQUIRED_CONF_HELPER_ANCHORS) |marker| try guard.requireMarker(text_required_conf_helper_anchors, marker);
    const text_required_conf_helper_local_allconfig_implicit_omission_modes_path = try guard.joinPath(allocator, root, "scripts/zigux/artifact_diff.zig");
    defer allocator.free(text_required_conf_helper_local_allconfig_implicit_omission_modes_path);
    const text_required_conf_helper_local_allconfig_implicit_omission_modes = try guard.readUtf8File(io, allocator, text_required_conf_helper_local_allconfig_implicit_omission_modes_path);
    defer allocator.free(text_required_conf_helper_local_allconfig_implicit_omission_modes);
    for (REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES) |marker| try guard.requireMarker(text_required_conf_helper_local_allconfig_implicit_omission_modes, marker);
    const text_required_conf_helper_local_allconfig_explicit_override_modes_path = try guard.joinPath(allocator, root, "scripts/zigux/artifact_diff.zig");
    defer allocator.free(text_required_conf_helper_local_allconfig_explicit_override_modes_path);
    const text_required_conf_helper_local_allconfig_explicit_override_modes = try guard.readUtf8File(io, allocator, text_required_conf_helper_local_allconfig_explicit_override_modes_path);
    defer allocator.free(text_required_conf_helper_local_allconfig_explicit_override_modes);
    for (REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES) |marker| try guard.requireMarker(text_required_conf_helper_local_allconfig_explicit_override_modes, marker);
    const text_required_confdata_helper_anchors_path = try guard.joinPath(allocator, root, "scripts/zigux/artifact_diff.zig");
    defer allocator.free(text_required_confdata_helper_anchors_path);
    const text_required_confdata_helper_anchors = try guard.readUtf8File(io, allocator, text_required_confdata_helper_anchors_path);
    defer allocator.free(text_required_confdata_helper_anchors);
    for (REQUIRED_CONFDATA_HELPER_ANCHORS) |marker| try guard.requireMarker(text_required_confdata_helper_anchors, marker);
    const text_sample_conf_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_sample_conf_cases_path);
    const text_sample_conf_cases = try guard.readUtf8File(io, allocator, text_sample_conf_cases_path);
    defer allocator.free(text_sample_conf_cases);
    for (SAMPLE_CONF_CASES) |marker| try guard.requireMarker(text_sample_conf_cases, marker);
    const text_sample_confdata_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_sample_confdata_cases_path);
    const text_sample_confdata_cases = try guard.readUtf8File(io, allocator, text_sample_confdata_cases_path);
    defer allocator.free(text_sample_confdata_cases);
    for (SAMPLE_CONFDATA_CASES) |marker| try guard.requireMarker(text_sample_confdata_cases, marker);
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
