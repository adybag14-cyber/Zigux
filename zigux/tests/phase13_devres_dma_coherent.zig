const std = @import("std");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) != null) {
        return error.UnexpectedMarker;
    }
}

test "phase13 devres coherent-dma shard stays visible beside the current mmio survey packet" {
    const manifest = @embedFile("phase13_devres_manifest.json");

    try requireContains(manifest, "\"lane_key\": \"P13-L01\"");
    try requireContains(manifest, "\"surveyed_commit\": \"master-readback-2026-05-14\"");
    try requireContains(manifest, "\"preexisting_phase13_build_present\": false");
    try requireContains(manifest, "\"preexisting_phase13_make_target_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_test_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_reviewability_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_survey_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_dma_coherent_present\": true");
    try requireContains(manifest, "\"id\": \"phase13-devres-test-gate\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-reviewability-gate\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-mmio-mappings\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-region-reservation\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-release-region-mutation\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-device-tree-walk\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-arch-memtype-state\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dma-mappings\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"starter_landed\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_mmio_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_device_tree_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_arch_memtype_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_dma_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_scatterlist_state\"");
    try requireContains(manifest, "stable shared Phase 13 replay handle");
    try requireContains(manifest, "actual region acquisition side effects");
    try requireContains(manifest, "real `release_mem_region()`");
    try requireContains(manifest, "helper-only DMA/scatterlist boundary");
    try requireContains(manifest, "DMA mapping helpers");
    try requireContains(manifest, "`sg_table` lifecycle control");
    try requireContains(manifest, "devm_arch_phys_wc_add()");
}

test "phase13 devres coherent-dma helper surface exposes no dma or scatterlist ownership markers" {
    const helper = @embedFile("../../lib/devres.zig");

    try requireAbsent(helper, "dmam_alloc_");
    try requireAbsent(helper, "dmam_free_");
    try requireAbsent(helper, "dma_alloc_");
    try requireAbsent(helper, "dma_map_");
    try requireAbsent(helper, "dma_unmap_");
    try requireAbsent(helper, "dma_sync_");
    try requireAbsent(helper, "dma_mmap_");
    try requireAbsent(helper, "dma_map_sgtable(");
    try requireAbsent(helper, "struct scatterlist");
    try requireAbsent(helper, "scatterlist");
    try requireAbsent(helper, "sg_table");
    try requireAbsent(helper, "sg_");
}

test "phase13 devres coherent-dma survey keeps the adjacent dma shard visible without claiming it as the core mmio gap map" {
    const survey = @embedFile("../../Documentation/zigux/phase13-devres-survey.md");

    try requireContains(survey, "zigux/tests/phase13_devres_dma_coherent.zig");
    try requireContains(survey, "adjacent coherent-DMA evidence shard");
    try requireContains(survey, "phase13-devres-live-dma-mappings");
    try requireContains(survey, "helper-only DMA/scatterlist boundary");
    try requireContains(survey, "no DMA mapping helpers");
    try requireContains(survey, "live DMA-backed helpers or DMA mapping ownership");
    try requireContains(survey, "no `sg_table` lifecycle control");
    try requireContains(survey, "live MMIO mappings");
    try requireContains(survey, "live device-tree walking");
    try requireContains(survey, "live arch memtype state transitions");
    try requireContains(survey, "helper-first MMIO safety foothold");
}
