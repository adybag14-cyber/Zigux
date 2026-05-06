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

test "phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership" {
    const manifest = @embedFile("phase13_devres_manifest.json");

    try requireContains(manifest, "\"preexisting_phase13_devres_test_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_reviewability_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_survey_present\": true");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dma-backed-helpers\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
}

test "phase13 devres coherent-dma boundary helper surface exposes no dma or scatterlist ownership markers" {
    const helper = @embedFile("../../lib/devres.zig");

    try requireAbsent(helper, "dmam_alloc_");
    try requireAbsent(helper, "dma_map_");
    try requireAbsent(helper, "dma_unmap_");
    try requireAbsent(helper, "dma_map_sgtable(");
    try requireAbsent(helper, "struct scatterlist");
    try requireAbsent(helper, "sg_table");
    try requireAbsent(helper, "sg_");
}

test "phase13 devres coherent-dma boundary note keeps dma-backed helpers and scatter-gather ownership out of scope" {
    const survey = @embedFile("../../Documentation/zigux/phase13-devres-survey.md");
    try requireContains(survey, "helper-source readback on current `master` shows");
    try requireContains(survey, "live DMA-backed helpers");
    try requireContains(survey, "live scatter-gather ownership");
    try requireContains(survey, "dmam_alloc_*");
    try requireContains(survey, "dma_unmap_*");
    try requireContains(survey, "sg_table lifecycle");
}
