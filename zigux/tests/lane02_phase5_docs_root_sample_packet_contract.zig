const std = @import("std");
const testing = std.testing;

fn readText(path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn expectMissing(text: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, needle) == null);
}

test "phase 5 docs root keeps the four-anchor sample packet visible" {
    const docs_root = try readText("Documentation/zigux/README.md");
    defer testing.allocator.free(docs_root);

    try expectContains(docs_root, "Phase 5 notes");
    try expectContains(docs_root, "Documentation/zigux/phase5-sample-review-guide.md");
    try expectContains(docs_root, "Documentation/zigux/phase5-sample-lane-sequencing.md");
    try expectContains(docs_root, "samples/zigux/README.md");
    try expectContains(docs_root, "scripts/zigux/check-phase5-review-guide-surface.py");
    try expectContains(docs_root, "zigux/tests/phase5_build.zig");

    try expectContains(docs_root, "samples/kfifo/bytestream-example.c");
    try expectContains(docs_root, "samples/kobject/kobject-example.c");
    try expectContains(docs_root, "samples/kprobes/kretprobe_example.c");
    try expectContains(docs_root, "samples/trace_events/trace-events-sample.c");
}

test "phase 5 review surfaces preserve non-runtime sample boundaries" {
    const checklist = try readText("Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(checklist);
    const guide = try readText("Documentation/zigux/phase5-sample-review-guide.md");
    defer testing.allocator.free(guide);
    const sequencing = try readText("Documentation/zigux/phase5-sample-lane-sequencing.md");
    defer testing.allocator.free(sequencing);

    try expectContains(checklist, "if the change touches the shared Phase 5 sample packet");
    try expectContains(checklist, "scripts/zigux/check-phase5-review-guide-surface.py");
    try expectContains(checklist, "samples/zigux/trace_events_callback_focus_contract.zig");
    try expectContains(checklist, "samples/zigux/trace_events_payload_preview_contract.zig");

    try expectContains(guide, "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.");
    try expectContains(guide, "samples/zigux/bytestream_fifo_transfer_contract.zig");
    try expectContains(guide, "samples/zigux/kobject_example_attr_group_contract.zig");
    try expectContains(guide, "samples/zigux/kretprobe_example_probe_spec.zig");
    try expectContains(guide, "samples/zigux/trace_events_string_formatting_sample.zig");
    try expectContains(guide, "no standalone");
    try expectContains(guide, "`samples/zigux/*string*`");
    try expectContains(guide, "`*bitmap*`");
    try expectContains(guide, "`*printf*`");

    try expectContains(sequencing, "stay inside the four approved non-runtime Linux sample anchors");
    try expectContains(sequencing, "keep later runtime-facing sample families in the separate Phase 9 lane");
    try expectContains(sequencing, "not extra Phase 5 sample proof");
}

test "sample root and checker keep direct, companion, and forbidden buckets explicit" {
    const sample_root = try readText("samples/zigux/README.md");
    defer testing.allocator.free(sample_root);
    const scripts_root = try readText("scripts/zigux/README.md");
    defer testing.allocator.free(scripts_root);
    const tests_root = try readText("zigux/tests/README.md");
    defer testing.allocator.free(tests_root);
    const checker = try readText("scripts/zigux/check-phase5-review-guide-surface.py");
    defer testing.allocator.free(checker);

    try expectContains(sample_root, "samples/zigux/bytestream_fifo.zig");
    try expectContains(sample_root, "samples/zigux/kobject_example_attr_group_contract.zig");
    try expectContains(sample_root, "samples/zigux/kretprobe_example_instance_budget_contract.zig");
    try expectContains(sample_root, "samples/zigux/trace_events_callback_focus_contract.zig");
    try expectContains(sample_root, "samples/zigux/runtime_*.zig");
    try expectContains(sample_root, "no standalone Phase 5 sample-root files");

    try expectContains(scripts_root, "python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test");
    try expectContains(scripts_root, "zigux/tests/phase5_build.zig");
    try expectContains(tests_root, "phase5_trace_events_sample_manifest.json");
    try expectContains(tests_root, "standalone helper-family sample claims");

    try expectContains(checker, "DIRECT_PACKET_PATHS");
    try expectContains(checker, "PUBLIC_TREE_COMPANION_PATHS");
    try expectContains(checker, "FORBIDDEN_GUIDE_TEXT");
    try expectContains(checker, "samples/zigux/trace_events_payload_preview_contract.zig");
}

test "shared phase 5 build file keeps the sample rerun handles discoverable" {
    const build_root = try readText("zigux/tests/phase5_build.zig");
    defer testing.allocator.free(build_root);

    try expectContains(build_root, "phase5-bytestream-fifo-sample-selfcheck");
    try expectContains(build_root, "phase5-bytestream-fifo-transfer-contract");
    try expectContains(build_root, "phase5-kobject-example-sample-selfcheck");
    try expectContains(build_root, "phase5-kobject-attr-group-contract");
    try expectContains(build_root, "phase5-kretprobe-example-instance-budget-contract");
    try expectContains(build_root, "phase5-kretprobe-example-probe-spec");
    try expectContains(build_root, "phase5-trace-events-string-formatting-companion");
    try expectContains(build_root, "phase5-trace-events-callback-focus-contract");
    try expectContains(build_root, "phase5-trace-events-payload-preview-contract");
    try expectMissing(build_root, "phase5-runtime-bitmap");
}
