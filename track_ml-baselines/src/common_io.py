"""설정과 쿼리 파일을 읽는 공통 코드. 1~4 단계 스크립트가 모두 씁니다."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACK = HERE.parent
DEFAULT_CONFIG = TRACK / "config" / "default.yaml"


def load_config(path: str | Path | None = None) -> dict:
    path = Path(path) if path else DEFAULT_CONFIG
    if not path.is_file():
        sys.exit(f"설정 파일이 없습니다: {path}")
    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml 이 필요합니다. `mamba install -c conda-forge pyyaml`")
    with path.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg["_config_path"] = str(path)
    return cfg


def resolve(cfg: dict, key: str) -> Path:
    """설정의 상대 경로는 트랙 폴더 기준입니다."""
    p = Path(cfg["paths"][key])
    return p if p.is_absolute() else (TRACK / p).resolve()


def load_queries(cfg: dict) -> list[dict]:
    """queries.jsonl 을 그대로 읽습니다. 열은 네 개입니다."""
    path = resolve(cfg, "queries")
    if not path.is_file():
        sys.exit(
            f"쿼리 파일이 없습니다: {path}\n"
            "먼저 track_curation/benchmark/05_make_queries.py 를 돌리십시오."
        )
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        sys.exit(f"쿼리 파일이 비어 있습니다: {path}")
    return rows


def load_meta(cfg: dict) -> dict[str, dict[str, str]]:
    """queries_meta.tsv 를 query_id 로 색인해 돌려줍니다.

    `queries.jsonl` 은 열이 네 개뿐이라 발행일이 없습니다. temporal split 만 이 파일을 씁니다.
    """
    import csv

    path = resolve(cfg, "queries_meta")
    if not path.is_file():
        sys.exit(
            f"메타데이터가 없습니다: {path}\n"
            "temporal split 은 date_publication 이 필요합니다. "
            "05_make_queries.py 를 다시 돌리십시오."
        )
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["query_id"]: r for r in csv.DictReader(fh, delimiter="\t")}


def pub_year(meta_row: dict | None) -> int | None:
    """`date_publication` 에서 연도만. BindingDB 는 M/D/YYYY 로 적습니다.

    읽히지 않으면 None 이고, temporal split 에서 그 쌍은 **제외합니다** (2026-11-26 결정).
    날짜 없는 행을 train 에 몰아 넣으면 "오래된 것" 이라는 잘못된 신호가 됩니다.
    """
    if not meta_row:
        return None
    s = (meta_row.get("date_publication") or "").strip()
    if not s:
        return None
    tail = s.split("/")[-1].split("-")[0]
    if len(tail) == 4 and tail.isdigit() and 1970 <= int(tail) <= 2027:
        return int(tail)
    return None


def load_assignment(cfg: dict) -> dict[str, dict[str, list[str]]]:
    """큐레이션 트랙의 분할 배정표를 읽습니다.

    반환값은 `{split_name: {"train": [query_id, ...], "cal": [...], "test": [...]}}` 입니다.
    `drop` 으로 적힌 쌍은 어느 목록에도 들어가지 않습니다.

    **이 트랙은 분할을 만들지 않습니다.** 배정표는
    `track_curation/benchmark/08_make_splits.py` 가 만들고 git 으로 넘어옵니다. 조건 A 와
    조건 B·C·D 가 같은 평가 평면에 서려면 분할이 한 곳에서 나와야 합니다. 2026-11-27 전까지
    이 트랙이 자기 분할을 따로 만들었는데, 그러면 리간드 묶기 키 하나만 달라도 (SMILES 원문
    vs InChIKey) cold 분할의 내용이 달라집니다.
    """
    import csv

    path = resolve(cfg, "splits_assignment")
    if not path.is_file():
        sys.exit(
            f"분할 배정표가 없습니다: {path}\n"
            "track_curation/benchmark/08_make_splits.py 를 돌려 만드십시오. "
            "이 파일은 git 에 들어 있습니다."
        )

    out: dict[str, dict[str, list[str]]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        names = [c for c in (rd.fieldnames or []) if c != "query_id"]
        if not names:
            sys.exit(f"{path.name} 에 분할 열이 없습니다. 읽은 열: {rd.fieldnames}")
        for name in names:
            out[name] = {"train": [], "cal": [], "test": []}
        for row in rd:
            qid = row["query_id"]
            for name in names:
                part = (row.get(name) or "").strip()
                if part in ("train", "cal", "test"):
                    out[name][part].append(qid)
                elif part != "drop":
                    sys.exit(
                        f"{path.name} 의 {name} 열에 모르는 값이 있습니다: {part!r} "
                        f"(query_id {qid}). 허용되는 값은 train, cal, test, drop 입니다."
                    )
    return out


def ligand_key(row: dict) -> str:
    """cold-drug 묶기용 키.

    데모에서는 SMILES 원문을 그대로 씁니다. 같은 분자를 다르게 쓴 SMILES 는 다른 키가
    되므로, 본실행에서는 queries_meta.tsv 의 InChIKey 로 바꾸십시오 (티켓: 유사도 분할).
    """
    return row["smiles"]


def target_key(row: dict) -> str:
    """cold-target 묶기용 키. 서열이 길어 해시로 줄입니다."""
    return hashlib.blake2b(row["sequence"].encode(), digest_size=12).hexdigest()
