// SPDX-License-Identifier: GPL-2.0
#include <getopt.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void write_json_escaped(FILE *out, const char *text)
{
	for (; *text; ++text) {
		switch (*text) {
		case '\\':
			fputs("\\\\", out);
			break;
		case '"':
			fputs("\\\"", out);
			break;
		case '\n':
			fputs("\\n", out);
			break;
		case '\r':
			fputs("\\r", out);
			break;
		case '\t':
			fputs("\\t", out);
			break;
		default:
			fputc(*text, out);
			break;
		}
	}
}

int main(int argc, char **argv)
{
	int debug_level = 0;
	bool warnings = false;
	bool dump_defs = false;
	bool preserve = false;
	char *dump_types_file = NULL;
	char *reference_files[16] = {0};
	size_t reference_count = 0;

	static struct option long_opts[] = {
		{"debug", 0, 0, 'd'},
		{"warnings", 0, 0, 'w'},
		{"quiet", 0, 0, 'q'},
		{"dump", 0, 0, 'D'},
		{"reference", 1, 0, 'r'},
		{"dump-types", 1, 0, 'T'},
		{"preserve", 0, 0, 'p'},
		{"version", 0, 0, 'V'},
		{"help", 0, 0, 'h'},
		{0, 0, 0, 0},
	};

	while (1) {
		int o = getopt_long(argc, argv, "dwqVDr:T:ph", long_opts, NULL);
		if (o == -1)
			break;

		switch (o) {
		case 'd':
			debug_level++;
			break;
		case 'w':
			warnings = true;
			break;
		case 'q':
			warnings = false;
			break;
		case 'D':
			dump_defs = true;
			break;
		case 'r':
			if (reference_count >= 16) {
				fprintf(stderr, "too many reference files\n");
				return 1;
			}
			reference_files[reference_count++] = optarg;
			break;
		case 'T':
			dump_types_file = optarg;
			break;
		case 'p':
			preserve = true;
			break;
		case 'V':
			fputs("genksyms version 2.5.60\n", stderr);
			break;
		case 'h':
			fputs(
				"Usage:\n"
				"genksyms [-adDTwqhVR] > /path/to/.tmp_obj.ver\n"
				"\n"
				"  -d, --debug           Increment the debug level (repeatable)\n"
				"  -D, --dump            Dump expanded symbol defs (for debugging only)\n"
				"  -r, --reference file  Read reference symbols from a file\n"
				"  -T, --dump-types file Dump expanded types into file\n"
				"  -p, --preserve        Preserve reference modversions or fail\n"
				"  -w, --warnings        Enable warnings\n"
				"  -q, --quiet           Disable warnings (default)\n"
				"  -h, --help            Print this message\n"
				"  -V, --version         Print the release version\n",
				stdout
			);
			return 0;
		default:
			return 1;
		}
	}

	fputs("{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\"", stdout);
	for (int i = 1; i < argc; ++i) {
		fputs(",\"", stdout);
		write_json_escaped(stdout, argv[i]);
		fputc('"', stdout);
	}
	fputs("],\"options\":{\"debug_level\":", stdout);
	fprintf(stdout, "%d", debug_level);
	fputs(",\"warnings\":", stdout);
	fputs(warnings ? "true" : "false", stdout);
	fputs(",\"dump_defs\":", stdout);
	fputs(dump_defs ? "true" : "false", stdout);
	fputs(",\"preserve\":", stdout);
	fputs(preserve ? "true" : "false", stdout);
	fputs(",\"reference_files\":[", stdout);
	for (size_t i = 0; i < reference_count; ++i) {
		if (i)
			fputc(',', stdout);
		fputc('"', stdout);
		write_json_escaped(stdout, reference_files[i]);
		fputc('"', stdout);
	}
	fputs("],\"dump_types_file\":", stdout);
	if (dump_types_file) {
		fputc('"', stdout);
		write_json_escaped(stdout, dump_types_file);
		fputc('"', stdout);
	} else {
		fputs("null", stdout);
	}
	fputs("}}\n", stdout);
	return 0;
}
