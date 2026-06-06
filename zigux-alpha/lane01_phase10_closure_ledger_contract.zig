const std = @import("std");
const testing = std.testing;

const ledger = @embedFile("PHASE10_CLOSURE_LEDGER.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, ledger, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, ledger, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase10 closure ledger keeps active virtio lab identity" {
    try requireContains(ledger, "# Phase 10 Closure Ledger");
    try requireContains(ledger, "PHASE10_LEDGER_STATUS=active");
    try requireContains(ledger, "PHASE10_LEDGER_TRANCHE=virtio-lab-bundle");
    try requireContains(ledger, "PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle");
    try requireContains(ledger, "PHASE10_LEDGER_ROADMAP_ANCHORS=drivers/virtio/virtio.c,drivers/virtio/virtio_ring.c,drivers/virtio/virtio_input.c,drivers/virtio/virtio_mmio.c");
}

test "phase10 closure ledger keeps validation route roster explicit" {
    try requireContains(ledger, "PHASE10_LEDGER_CORE_PACKET_VALIDATE=scripts/zigux/check-phase10-core-packet.py");
    try requireContains(ledger, "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py");
    try requireContains(ledger, "PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py");
    try requireContains(ledger, "PHASE10_LEDGER_ENTRYPOINTS=make -C zigux phase10-validate,make -C zigux phase10-test,make -C zigux phase10");

    try requireOrdered("PHASE10_LEDGER_EXACT_CHECK_13=zig build test --build-file zigux/tests/phase10_build.zig --summary all", "PHASE10_LEDGER_EXACT_CHECK_15=make -C zigux phase10");
}

test "phase10 closure ledger keeps manifest-backed survey provenance" {
    try requireContains(ledger, "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json");
    try requireContains(ledger, "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived");
    try requireContains(ledger, "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01");
    try requireContains(ledger, "PHASE10_LEDGER_SURVEY_RING_LANE=");
    try requireContains(ledger, "PHASE10_LEDGER_SURVEY_INPUT_LANE=");
    try requireContains(ledger, "PHASE10_LEDGER_SURVEY_MMIO_LANE=");
}

test "phase10 closure ledger keeps parked risky transport boundary" {
    try requireContains(ledger, "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport");
    try requireContains(ledger, "PHASE10_LEDGER_FORBIDDEN_TRANSPORT_CLAIMS=");
    try requireContains(ledger, "queue_setup_reset_paths");
    try requireContains(ledger, "irq_parity");
    try requireContains(ledger, "dma_paths");
    try requireContains(ledger, "input_registration_lifecycle");
    try requireContains(ledger, "probe_remove_lifecycle");
    try requireContains(ledger, "PHASE10_LEDGER_BLOCKERS=");
    try requireContains(ledger, "phase10-virtio-input-registration-lifecycle");
    try requireContains(ledger, "phase10-mmio-lifecycle-and-irq-paths");
    try requireContains(ledger, "PHASE10_LEDGER_NEXT_STEP=leave_parked_unless");
    try requireContains(ledger, "This ledger stays intentionally narrow.");
    try requireContains(ledger, "without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity");
}
