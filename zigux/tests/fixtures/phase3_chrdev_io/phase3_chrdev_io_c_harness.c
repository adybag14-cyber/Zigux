#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void write_summary(FILE *out, const struct zigux_chrdev_io_summary *summary)
{
    fprintf(out,
        "{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"chunk_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"flags\":%u}",
        summary->major,
        summary->target_minor,
        summary->selected_count,
        summary->resolved_index,
        summary->resolved_dev,
        summary->granted_mode,
        summary->io_op,
        summary->requested_bytes,
        summary->chunk_bytes,
        summary->entry_ops,
        summary->data_ops,
        summary->exit_ops,
        summary->blocked_ops,
        summary->flags);
}

int main(void)
{
    const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
    const struct zigux_chrdev_io_view read_view =
        zigux_chrdev_io_view_from_bits(words, 240, 32, 8, 6, 2,
                           ZIGUX_IDA_POLICY_FIRST_FIT, 34,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                               ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE,
                           ZIGUX_CHRDEV_IO_OP_READ, 16, 8);
    const struct zigux_chrdev_io_view partial_write_view =
        zigux_chrdev_io_view_from_bits(words, 240, 32, 8, 8, 2,
                           ZIGUX_IDA_POLICY_LAST_FIT, 37,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                               ZIGUX_CHRDEV_FOP_WRITE,
                           ZIGUX_CHRDEV_IO_OP_WRITE, 12, 32);
    const struct zigux_chrdev_io_view blocked_read_view =
        zigux_chrdev_io_view_from_bits(words, 240, 32, 8, 8, 2,
                           ZIGUX_IDA_POLICY_LAST_FIT, 37,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                               ZIGUX_CHRDEV_FOP_WRITE,
                           ZIGUX_CHRDEV_IO_OP_READ, 12, 32);
    const struct zigux_chrdev_io_view denied_view =
        zigux_chrdev_io_view_from_bits(words, 240, 32, 8, 8, 2,
                           ZIGUX_IDA_POLICY_LAST_FIT, 37,
                           ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
                           ZIGUX_CHRDEV_MODE_READ,
                           ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                               ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE,
                           ZIGUX_CHRDEV_IO_OP_WRITE, 12, 32);
    const struct zigux_chrdev_io_view miss_view =
        zigux_chrdev_io_view_from_bits(words, 240, 32, 8, 8, 2,
                           ZIGUX_IDA_POLICY_LAST_FIT, 35,
                           ZIGUX_CHRDEV_MODE_READ,
                           ZIGUX_CHRDEV_MODE_READ,
                           ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                               ZIGUX_CHRDEV_FOP_READ,
                           ZIGUX_CHRDEV_IO_OP_READ, 12, 32);
    const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
    const struct zigux_chrdev_io_view exhausted_view =
        zigux_chrdev_io_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
                           ZIGUX_IDA_POLICY_FIRST_FIT, 20,
                           ZIGUX_CHRDEV_MODE_READ,
                           ZIGUX_CHRDEV_MODE_READ,
                           ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                               ZIGUX_CHRDEV_FOP_READ,
                           ZIGUX_CHRDEV_IO_OP_READ, 12, 32);
    const struct zigux_chrdev_io_view empty_view = {
        .bits_addr = 0,
        .major = 240,
        .first_minor = 0,
        .minor_count = 0,
        .max_scan = 0,
        .request_count = 2,
        .policy = ZIGUX_IDA_POLICY_FIRST_FIT,
        .target_minor = 0,
        .requested_mode = ZIGUX_CHRDEV_MODE_READ,
        .supported_mode = ZIGUX_CHRDEV_MODE_READ,
        .available_ops = ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
                 ZIGUX_CHRDEV_FOP_READ,
        .io_op = ZIGUX_CHRDEV_IO_OP_READ,
        .requested_bytes = 8,
        .max_chunk_bytes = 8,
        .reserved = 0,
    };

    fputs("{\"constants\":{\"chrdev_io_op_read\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_OP_READ);
    fputs(",\"chrdev_io_op_write\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_OP_WRITE);
    fputs(",\"chrdev_io_flag_truncated\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_TRUNCATED);
    fputs(",\"chrdev_io_flag_found\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_FOUND);
    fputs(",\"chrdev_io_flag_exhausted\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_EXHAUSTED);
    fputs(",\"chrdev_io_flag_hit\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_HIT);
    fputs(",\"chrdev_io_flag_permitted\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_PERMITTED);
    fputs(",\"chrdev_io_flag_denied\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_DENIED);
    fputs(",\"chrdev_io_flag_routable\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_ROUTABLE);
    fputs(",\"chrdev_io_flag_blocked\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_BLOCKED);
    fputs(",\"chrdev_io_flag_dispatchable\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_FLAG_DISPATCHABLE);
    fputs(",\"chrdev_io_index_none\":", stdout);
    fprintf(stdout, "%u", ZIGUX_CHRDEV_IO_INDEX_NONE);

    fputs("},\"read_dispatch\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&read_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"write_partial\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&partial_write_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"blocked_read\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&blocked_read_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"denied\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&denied_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"miss\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&miss_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"exhausted\":{\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&exhausted_view);
        write_summary(stdout, &summary);
    }

    fputs("},\"empty\":{\"is_valid\":", stdout);
    fputs(zigux_chrdev_io_view_valid(&empty_view) ? "true" : "false", stdout);
    fputs(",\"summary\":", stdout);
    {
        const struct zigux_chrdev_io_summary summary =
            zigux_chrdev_io_summarize(&empty_view);
        write_summary(stdout, &summary);
    }

    fputs("}}\n", stdout);
    return 0;
}
