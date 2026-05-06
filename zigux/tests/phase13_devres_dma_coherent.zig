const std = @import("std");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

test "phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership" {
    const manifest = @embedFile("phase13_devres_manifest.json");

    try requireContains(manifest, "\"preexisting_phase13_devres_test_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_reviewability_present\": true");
    try requireContains(manifest, "\"preexisting_phase13_devres_survey_present\": true");
    try requireContains(manifest, "\"id\": \"phase13-devres-coherent-dma-replay\"");
    try requireContains(manifest, "\"status\": \"starter_landed\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dma-backed-helpers\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
}

test "phase13 devres coherent-dma boundary note keeps dma-backed helpers and scatter-gather ownership out of scope" {
    const survey = @embedFile("../../Documentation/zigux/phase13-devres-survey.md");
    try requireContains(survey, "live DMA-backed helpers");
    try requireContains(survey, "live scatter-gather ownership");
    try requireContains(survey, "dma_unmap_*");
    try requireContains(survey, "sg_table lifecycle");
}
