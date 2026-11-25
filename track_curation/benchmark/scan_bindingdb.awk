# scan_bindingdb.awk - single streaming pass over BindingDB_All.tsv.
#
# Driven by 01_bindingdb_columns.py. Counts only, no decisions.
#
# The file is 640 columns wide (40 common + 50 target-chain blocks of 12) and
# about 2.9 M rows, so pandas cannot hold a wide chunk of it as strings. awk
# streams it one row at a time instead.
#
# "non-empty" means the field holds at least one non-whitespace character.
# BindingDB pads numeric fields with leading spaces (" 43000"), so a bare
# != "" test would overcount.
#
# Required -v arguments: OUT_FILL OUT_SUMMARY OUT_QUAL OUT_QUAL_EX OUT_CHAIN
#                        OUT_EXTRACT
# Optional: MAX_EX (examples kept per qualifier pattern, default 5)

function trim(s) {
    gsub(/^[ \t\r]+/, "", s)
    gsub(/[ \t\r]+$/, "", s)
    return s
}

# Leading non-numeric run of a value: ">1000" -> ">", ">=5" -> ">=", "12" -> "".
function qual_pattern(s) {
    sub(/[0-9.].*$/, "", s)
    return s
}

BEGIN {
    FS = "\t"
    OFS = "\t"
    if (MAX_EX == 0) MAX_EX = 5

    # Column positions, from the 202610 header. Verified by 01_bindingdb_columns.py
    # before this script runs; it aborts on any mismatch.
    C_KI = 9
    C_KD = 11
    C_NCHAIN = 40
    CHAIN_BASE = 41     # BindingDB Target Chain Sequence 1
    CHAIN_STRIDE = 12
    N_CHAIN_MAX = 50
}

NR == 1 {
    ncol = NF
    for (i = 1; i <= NF; i++) name[i] = $i

    # Provisional look-at-it extract for ticket 03. Ticket 05 picks the real set.
    n_ex = split(EXTRACT_COLS, ex_col, ",")
    line = ""
    for (j = 1; j <= n_ex; j++) line = line (j > 1 ? OFS : "") name[ex_col[j]]
    print line > OUT_EXTRACT
    next
}

{
    total++
    if (NF != ncol) { ragged++; next }

    kd = trim($C_KD)
    ki = trim($C_KI)
    kd_ne = (kd != "")
    ki_ne = (ki != "")

    if (kd_ne) kd_rows++
    if (ki_ne) ki_rows++
    if (kd_ne && ki_ne) both_rows++
    either = (kd_ne || ki_ne)
    if (either) either_rows++

    for (i = 1; i <= ncol; i++) {
        if ($i ~ /[^ \t\r]/) {
            fill_all[i]++
            if (either) fill_kdki[i]++
        }
    }

    if (kd_ne) {
        p = qual_pattern(kd)
        qcount["Kd (nM)" SUBSEP p]++
        if (qex_n["Kd (nM)" SUBSEP p]++ < MAX_EX)
            print "Kd (nM)", p, kd > OUT_QUAL_EX
    }
    if (ki_ne) {
        p = qual_pattern(ki)
        qcount["Ki (nM)" SUBSEP p]++
        if (qex_n["Ki (nM)" SUBSEP p]++ < MAX_EX)
            print "Ki (nM)", p, ki > OUT_QUAL_EX
    }

    nch = trim($C_NCHAIN)
    nchain_hist[nch == "" ? "(empty)" : nch]++
    if (either) nchain_hist_kdki[nch == "" ? "(empty)" : nch]++

    for (c = 1; c <= N_CHAIN_MAX; c++) {
        col = CHAIN_BASE + (c - 1) * CHAIN_STRIDE
        if ($col ~ /[^ \t\r]/) {
            chain_seq[c]++
            if (either) chain_seq_kdki[c]++
        }
    }

    if (either) {
        line = ""
        for (j = 1; j <= n_ex; j++) line = line (j > 1 ? OFS : "") trim($ex_col[j])
        print line > OUT_EXTRACT
    }
}

END {
    print "col_index", "col_name", "nonempty_all", "nonempty_kdki" > OUT_FILL
    for (i = 1; i <= ncol; i++)
        print i, name[i], fill_all[i] + 0, fill_kdki[i] + 0 > OUT_FILL

    print "key", "value" > OUT_SUMMARY
    print "total_data_rows", total + 0 > OUT_SUMMARY
    print "ragged_rows_skipped", ragged + 0 > OUT_SUMMARY
    print "n_columns", ncol > OUT_SUMMARY
    print "kd_nonempty_rows", kd_rows + 0 > OUT_SUMMARY
    print "ki_nonempty_rows", ki_rows + 0 > OUT_SUMMARY
    print "kd_and_ki_rows", both_rows + 0 > OUT_SUMMARY
    print "kd_or_ki_rows", either_rows + 0 > OUT_SUMMARY
    for (k in nchain_hist)
        print "nchain_all[" k "]", nchain_hist[k] > OUT_SUMMARY
    for (k in nchain_hist_kdki)
        print "nchain_kdki[" k "]", nchain_hist_kdki[k] > OUT_SUMMARY

    print "field", "pattern", "count" > OUT_QUAL
    for (k in qcount) {
        split(k, parts, SUBSEP)
        print parts[1], (parts[2] == "" ? "(none)" : parts[2]), qcount[k] > OUT_QUAL
    }

    print "chain_index", "seq_nonempty_all", "seq_nonempty_kdki" > OUT_CHAIN
    for (c = 1; c <= N_CHAIN_MAX; c++)
        print c, chain_seq[c] + 0, chain_seq_kdki[c] + 0 > OUT_CHAIN
}
