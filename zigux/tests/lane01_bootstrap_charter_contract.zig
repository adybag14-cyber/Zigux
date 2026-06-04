const std = @import("std");

const Surface = struct {
    path: []const u8,
    terms: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSurface(surface: Surface, limit: usize) !void {
    const text = try readRepoFile(surface.path, limit);
    defer std.testing.allocator.free(text);

    for (surface.terms) |term| {
        try expectContains(text, term);
    }
}

test "zigux-alpha README keeps the bootstrap workspace charter narrow" {
    try expectSurface(.{
        .path = "zigux-alpha/README.md",
        .terms = &.{
            "`zigux-alpha` is the Zigux bootstrap workspace.",
            "It does not exist to become a permanent parallel subsystem tree.",
            "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
            "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche",
            "Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
            "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.",
            "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
            "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
            "[ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
            "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
            "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
        },
    }, 64 * 1024);
}

test "roadmap keeps bootstrap status and product-placement boundaries explicit" {
    try expectSurface(.{
        .path = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        .terms = &.{
            "## Bootstrap Status Note",
            "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
            "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
            "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
            "No mirror-tree sprawl.",
            "`zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.",
            "Keep the Zigux support root small.",
            "`zigux/kernel/`",
            "`zigux/helpers/`",
            "`zigux/bindings/`",
            "`zigux/uapi/`",
            "`zigux/tests/`",
            "`zigux/unsafe/`",
        },
    }, 192 * 1024);
}

test "bootstrap ledger stays truthful about the early train and later handoffs" {
    try expectSurface(.{
        .path = "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
        .terms = &.{
            "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
            "## Scope Note",
            "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
            "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
            "## Release-Planning Continuation",
            "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.",
            "For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:",
            "Documentation/zigux/phase5-closure.md",
            "Documentation/zigux/phase5-sample-lane-sequencing.md",
            "Documentation/zigux/phase5-sample-review-guide.md",
        },
    }, 128 * 1024);
}

test "Phase 10 closure ledger remains a parked handoff, not a transport claim" {
    try expectSurface(.{
        .path = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        .terms = &.{
            "PHASE10_LEDGER_STATUS=active",
            "PHASE10_LEDGER_TRANCHE=virtio-lab-bundle",
            "PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle",
            "PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
            "PHASE10_LEDGER_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,queue_reset_execution,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle,freeze_restore_lifecycle",
            "PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_shared_phase10_surfaces_drift_again_around_the_manifest_backed_packet_and_reopen_P10-L06_only_if_a_fresh_shared_reminder_reread_proves_new_drift",
            "This ledger stays intentionally narrow.",
            "without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity.",
            "blocked_on_risky_transport",
            "make -C zigux phase10-validate",
            "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
        },
    }, 256 * 1024);
}
