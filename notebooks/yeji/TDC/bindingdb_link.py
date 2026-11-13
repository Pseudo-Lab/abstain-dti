"""
Link TDC DTI rows back to the original BindingDB rows.

TDC drops three things BindingDB keeps: the inequality sign on a value
(">10000" becomes 10000), the curation source, and the assay description.
This module recovers them by matching each TDC row to BindingDB 202610 rows
with the same PubChem CID, the same target (chain sequence, or UniProt as a
fallback) and the same numeric value in the same measurement column.

Inputs (BindingDB 202610, SHA256 checked against the UCSD archive
doi:10.6075/J02V2H30, see .scratch/tdc-dta-merge/research/06-kd-assay-method.md):
  BindingDB_All.tsv          one row per measurement
  BindingDB_Assays.tsv       assay name and description per (entry, assay)
  BindingDB_rsid_eaids.tsv   measurement (reactant set id) -> assay id

The keyword rules that sort an assay text into direct / indirect come from
ticket 06. They are rough: they were not hand-checked and some rows are
mislabelled. Use the class as a description, not as a filter.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

csv.field_size_limit(sys.maxsize)

# Which BindingDB value column each TDC dataset was built from.
VALUE_COLUMN = {"davis": "Kd (nM)", "bindingdb_kd": "Kd (nM)",
                "bindingdb_ki": "Ki (nM)"}

_RULES = [
    ("ITC", r"isothermal titration|\bitc\b|calorimetr"),
    ("SPR", r"surface plasmon|\bspr\b|biacore"),
    ("BLI", r"bio-?layer interferometry|\bbli\b|octet"),
    ("MST", r"microscale thermophoresis|\bmst\b"),
    ("competition_binding", r"kinomescan|competition binding|competitive binding|"
                            r"competition assay|binding competition"),
    ("displacement_or_radioligand", r"displac|radioligand|\[3h\]|\[125i\]|radiolabel|"
                                    r"scintillation proximity|tracer"),
    ("FP_or_anisotropy", r"fluorescence polari[sz]ation|anisotropy|\bfp\b"),
    ("TR_FRET_HTRF_AlphaScreen", r"tr-fret|htrf|lanthascreen|alphascreen|alphalisa|"
                                 r"time-resolved"),
    ("fluorescence_titration", r"fluorescence titration|tryptophan fluorescence|"
                               r"fluorescence quench|intrinsic fluorescence"),
    ("NMR", r"\bnmr\b"),
    ("cheng_prusoff", r"cheng.?prusoff"),
    ("mentions_IC50", r"ic50|ic 50"),
    ("enzyme_activity", r"inhibition assay|enzyme activity|enzymatic|substrate|"
                        r"kinase activity|kinase assay"),
]
_RULES = [(n, re.compile(p)) for n, p in _RULES]
_DIRECT = {"ITC", "SPR", "BLI", "MST", "fluorescence_titration", "NMR"}
_INDIRECT = {"competition_binding", "displacement_or_radioligand", "cheng_prusoff",
             "FP_or_anisotropy", "TR_FRET_HTRF_AlphaScreen", "enzyme_activity",
             "mentions_IC50"}

# Per-row columns this module adds, in output order.
LINK_COLUMNS = ["bindingdb_match", "bindingdb_n_candidates", "bindingdb_qualifier",
                "bindingdb_curation_source", "bindingdb_pmid", "bindingdb_doi",
                "bindingdb_patent", "assay_class", "assay_keywords",
                "assay_description"]

MAX_DESCRIPTIONS = 3


def assay_class(name: str, description: str) -> tuple[str, set[str]]:
    """Sort one assay text into direct / indirect / both_keywords / unknown."""
    text = f"{name} {description}".lower()
    labels = {n for n, p in _RULES if p.search(text)}
    direct, indirect = bool(labels & _DIRECT), bool(labels & _INDIRECT)
    if direct and indirect:
        return "both_keywords", labels
    if direct:
        return "direct", labels
    if indirect:
        return "indirect", labels
    return "unknown", labels


def _num(s: str) -> float | None:
    try:
        return float(s.strip().lstrip("<>=~ ").strip())
    except ValueError:
        return None


def _vkey(x: float | None) -> float | None:
    """Value key for matching. 6 significant digits absorbs float formatting."""
    return None if x is None else float(f"{x:.6g}")


def _cid(x) -> str:
    try:
        return str(int(float(x)))
    except (TypeError, ValueError):
        return ""


def _read_assays(path: Path) -> dict[str, tuple[str, str]]:
    out = {}
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if len(row) == 4:
                out[f"{row[0]}_{row[1]}"] = (row[2].strip(), row[3].strip())
    return out


def _read_measurements(path: Path, columns: set[str]) -> dict[str, dict]:
    """BindingDB_All rows that carry a value in one of `columns`, by rsid."""
    rows: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        h = next(r)
        ix = {c: i for i, c in enumerate(h)}
        need = max(ix[c] for c in (
            *columns, "PubChem CID", "BindingDB Target Chain Sequence 1",
            "UniProt (SwissProt) Primary ID of Target Chain 1",
            "UniProt (TrEMBL) Primary ID of Target Chain 1",
            "Curation/DataSource", "PMID", "Article DOI", "Patent Number")) + 1
        for row in r:
            if len(row) < need:
                row = row + [""] * (need - len(row))
            for col in columns:
                raw = row[ix[col]].strip()
                if not raw:
                    continue
                rows[f"{row[0]}|{col}"] = {
                    "col": col, "raw": raw, "value": _num(raw),
                    "qualifier": raw[0] if raw[0] in "<>" else "",
                    "cid": row[ix["PubChem CID"]].strip(),
                    "seq": row[ix["BindingDB Target Chain Sequence 1"]].strip(),
                    "uniprot": (row[ix["UniProt (SwissProt) Primary ID of Target Chain 1"]].strip()
                                or row[ix["UniProt (TrEMBL) Primary ID of Target Chain 1"]].strip()),
                    "source": row[ix["Curation/DataSource"]].strip(),
                    "pmid": row[ix["PMID"]].strip(),
                    "doi": row[ix["Article DOI"]].strip(),
                    "patent": row[ix["Patent Number"]].strip(),
                    "rsid": row[0],
                }
    return rows


def _attach_assays(rows: dict[str, dict], rsid_path: Path,
                   assays: dict[str, tuple[str, str]]) -> None:
    by_rsid = defaultdict(list)
    for k, d in rows.items():
        by_rsid[d["rsid"]].append(k)
    with open(rsid_path, encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            rsid, eaid = line.rstrip("\n").split("\t")
            for k in by_rsid.get(rsid, ()):
                rows[k]["eaid"] = eaid
    for d in rows.values():
        name, desc = assays.get(d.get("eaid", ""), ("", ""))
        d["assay_name"], d["assay_desc"] = name, desc
        d["assay_class"], d["assay_labels"] = (
            assay_class(name, desc) if (name or desc) else ("unknown", set()))


def _join(values) -> str:
    return "; ".join(sorted({v for v in values if v}))


def link(frames: dict[str, pd.DataFrame], bindingdb_dir: Path,
         log=print) -> dict[str, pd.DataFrame]:
    """
    Annotate TDC rows with their BindingDB origin.

    frames: dataset name -> TDC frame with Drug_ID, Target_ID, Target, Y.
    Returns dataset name -> frame with LINK_COLUMNS, aligned to the input index.
    """
    bindingdb_dir = Path(bindingdb_dir)
    columns = {VALUE_COLUMN[n] for n in frames}
    log(f"  reading BindingDB_All ({', '.join(sorted(columns))})")
    rows = _read_measurements(bindingdb_dir / "BindingDB_All.tsv", columns)
    log(f"  {len(rows):,} BindingDB measurements")
    assays = _read_assays(bindingdb_dir / "BindingDB_Assays.tsv")
    _attach_assays(rows, bindingdb_dir / "BindingDB_rsid_eaids.tsv", assays)

    by_seq, by_up = defaultdict(list), defaultdict(list)
    for k, d in rows.items():
        v = _vkey(d["value"])
        if d["cid"] and d["seq"]:
            by_seq[(d["col"], d["cid"], d["seq"], v)].append(k)
        if d["cid"] and d["uniprot"]:
            by_up[(d["col"], d["cid"], d["uniprot"], v)].append(k)

    out = {}
    for name, df in frames.items():
        col = VALUE_COLUMN[name]
        recs = []
        for drug_id, target_id, seq, y in zip(df["Drug_ID"], df["Target_ID"],
                                              df["Target"], df["Y"]):
            cid, v = _cid(drug_id), _vkey(_num(str(y)))
            cands = by_seq.get((col, cid, str(seq).strip(), v), [])
            route = "sequence" if cands else ""
            # UniProt 경로는 서열을 보지 않으므로 같은 UniProt 의 변이체나 다른
            # construct 행과 이어질 수 있다. bindingdb_match 로 구분해 둔다.
            if not cands and isinstance(target_id, str):
                for up in target_id.split(","):
                    cands = cands + by_up.get((col, cid, up.strip(), v), [])
                route = "uniprot" if cands else ""
            cands = list(dict.fromkeys(cands))
            recs.append([route] + _summarise([rows[c] for c in cands]))
        ann = pd.DataFrame(recs, index=df.index, columns=LINK_COLUMNS)
        matched = int((ann["bindingdb_n_candidates"] > 0).sum())
        log(f"  {name}: {matched:,} / {len(df):,} rows linked")
        out[name] = ann
    return out


def _summarise(cands: list[dict]) -> list:
    if not cands:
        return [0, "", "", "", "", "", "no_match", "", ""]
    quals = {c["qualifier"] for c in cands}
    qualifier = quals.pop() if len(quals) == 1 else "mixed"
    classes = {c["assay_class"] for c in cands}
    klass = classes.pop() if len(classes) == 1 else "candidates_disagree"
    texts = []
    for c in cands:
        t = ": ".join(x for x in (c["assay_name"], c["assay_desc"]) if x)
        if t and t not in texts:
            texts.append(t)
    return [len(cands), qualifier,
            _join(c["source"] for c in cands), _join(c["pmid"] for c in cands),
            _join(c["doi"] for c in cands), _join(c["patent"] for c in cands),
            klass, _join(l for c in cands for l in c["assay_labels"]),
            " || ".join(texts[:MAX_DESCRIPTIONS])]
