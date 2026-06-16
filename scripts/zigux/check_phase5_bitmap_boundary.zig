const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_BITMAP_BOUNDARY=pass";
pub const self_test_pass_marker = "PHASE5_BITMAP_BOUNDARY_SELF_TEST=pass";

const MARKERS__Documentation_zigux_phase5-sample-lane-sequencing_md = [_][]const u8{
    "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
    "keep the returned runtime bitmap reminder packet `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` framed as separate Phase 9 runtime evidence rather than extra Phase 5 sample proof",
    "there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`",
};

const MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit.",
};

const MARKERS__Documentation_zigux_phase5-sample-review-guide_md = [_][]const u8{
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "treating Phase 9 runtime samples as extra Phase 5 evidence",
};

const MARKERS__scripts_zigux_README_md = [_][]const u8{
    "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
};

const MARKERS__zigux_tests_README_md = [_][]const u8{
    "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
};

const MARKERS = [_][]const u8{
    "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
    "keep the returned runtime bitmap reminder packet `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` framed as separate Phase 9 runtime evidence rather than extra Phase 5 sample proof",
    "there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`",
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit.",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "treating Phase 9 runtime samples as extra Phase 5 evidence",
    "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
    "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-lane-sequencing/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path);
    const text_markers__documentation_zigux_phase5-sample-lane-sequencing_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md);
    for (MARKERS__Documentation_zigux_phase5-sample-lane-sequencing_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md, marker);
    const text_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README/md");
    defer allocator.free(text_markers__samples_zigux_readme_md_path);
    const text_markers__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__samples_zigux_readme_md_path);
    defer allocator.free(text_markers__samples_zigux_readme_md);
    for (MARKERS__samples_zigux_README_md) |marker| try guard.requireMarker(text_markers__samples_zigux_readme_md, marker);
    const text_markers__documentation_zigux_phase5-sample-review-guide_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-review-guide/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-review-guide_md_path);
    const text_markers__documentation_zigux_phase5-sample-review-guide_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-sample-review-guide_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-review-guide_md);
    for (MARKERS__Documentation_zigux_phase5-sample-review-guide_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-sample-review-guide_md, marker);
    const text_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_markers__scripts_zigux_readme_md_path);
    const text_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_markers__scripts_zigux_readme_md);
    for (MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_markers__scripts_zigux_readme_md, marker);
    const text_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_markers__zigux_tests_readme_md_path);
    const text_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_markers__zigux_tests_readme_md);
    for (MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_markers__zigux_tests_readme_md, marker);
    const text_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_markers_path);
    const text_markers = try guard.readUtf8File(io, allocator, text_markers_path);
    defer allocator.free(text_markers);
    for (MARKERS) |marker| try guard.requireMarker(text_markers, marker);
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
