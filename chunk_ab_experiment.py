"""A/B retrieval pilot. Python 3.10+. See README_KO.md. No LLM/CRAG calls."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def sample_data():
    # Fictional data for debugging, not a public benchmark or real school policy.
    # 가상문서 3개, 질문참고 정답근거 10개 
    texts = [
        ("library", "가상학교 도서관", [
            "이 문서는 실험용으로 만든 가상학교 도서관 안내입니다. 실제 학교의 규정이 아닙니다. 도서관은 자료 열람과 대출 서비스를 제공합니다. 입구 안내 데스크에서 이용 방법을 물어볼 수 있습니다.",
            "학생은 도서를 최대 5권까지 빌릴 수 있습니다. 교직원의 대출 한도는 10권입니다. 대출 시 본인의 학생증이나 교직원증을 제시해야 합니다. 다른 사람의 신분증으로는 대출할 수 없습니다.",
            "학생의 기본 대출 기간은 14일입니다. 예약자가 없는 도서는 한 번에 한해 7일 연장할 수 있습니다. 연장 신청은 반납일 이전에 홈페이지에서 해야 합니다. 이미 연체된 도서는 연장할 수 없습니다.",
            "도서를 연체하면 연체한 일수만큼 신규 대출이 제한됩니다. 연체에 따른 금전적 벌금은 없습니다. 반납함에 넣은 책은 다음 운영일에 처리됩니다. 분실 도서는 안내 데스크에 신고해야 합니다.",
            "평일 자료실 운영 시간은 오전 9시부터 오후 6시까지입니다. 토요일은 오후 1시에 문을 닫고 일요일은 운영하지 않습니다. 시험 기간 열람실의 연장 운영은 별도 공지합니다.",
            "스터디룸은 최소 2명부터 이용할 수 있습니다. 스터디룸은 하루 최대 2시간 예약할 수 있습니다. 예약 시작 후 15분이 지나도 입실하지 않으면 예약이 취소됩니다. 음식물 반입은 금지합니다.",
            "전자책은 학교 계정으로 로그인한 뒤 이용합니다. 전자책의 대출 조건은 종이책과 별도로 적용됩니다. 참고자료와 희귀자료는 자료실 안에서만 열람할 수 있으며 외부 대출은 불가능합니다.",
        ]),
        ("lab", "가상학교 실습실", [
            "이 문서는 실험용 가상 실습실 안내입니다. 실습실에는 컴퓨터와 간단한 전자 장비가 있습니다. 이용자는 사전에 안전교육을 이수해야 합니다. 실제 기관의 안전 지침으로 사용하면 안 됩니다.",
            "실습실은 평일 오전 10시부터 오후 8시까지 운영합니다. 주말과 공휴일에는 운영하지 않습니다. 정기 점검일에는 예약이 있어도 이용이 제한될 수 있으며 담당자가 변경 일정을 공지합니다.",
            "장비 예약은 이용일 3일 전부터 가능합니다. 예약은 학교 포털의 실습실 메뉴에서 진행합니다. 한 사람이 동시에 유지할 수 있는 예약은 2건입니다. 중복 시간대 예약은 허용하지 않습니다.",
            "노트북은 한 번에 최대 4시간 대여할 수 있습니다. 대여 시 신분증을 확인하고 장비 상태를 함께 기록합니다. 반납할 때는 충전기와 가방도 함께 제출해야 합니다. 개인 파일은 이용자가 삭제합니다.",
            "3D 프린터를 이용하려면 별도의 장비 교육을 받아야 합니다. 출력 신청 파일은 담당자가 검토합니다. 출력 재료는 실습실에서 지정한 것만 사용할 수 있습니다. 장비 이상이 생기면 즉시 담당자에게 알립니다.",
            "예약 취소는 이용 시작 2시간 전까지 해야 합니다. 사전 연락 없이 두 번 이용하지 않으면 7일간 예약이 제한됩니다. 시스템 장애로 취소하지 못했다면 담당자에게 상황을 설명합니다.",
            "실습이 끝나면 책상을 정리하고 사용한 도구를 제자리에 놓습니다. 마지막 이용자는 담당자에게 종료 사실을 알립니다. 공용 컴퓨터에 프로그램을 설치하려면 사전 승인을 받아야 합니다.",
        ]),
        ("dorm", "가상학교 기숙사", [
            "이 문서는 실험용 가상 기숙사 생활 안내입니다. 입사자는 입사 당일 행정실에서 열쇠를 받습니다. 방 상태를 확인하고 이상이 있으면 입사 점검표에 기록합니다. 안내 내용은 실제 규정이 아닙니다.",
            "기숙사 택배 보관 기간은 도착일로부터 5일입니다. 택배를 찾을 때 본인 확인이 필요합니다. 냉장이나 냉동 보관이 필요한 물품은 접수하지 않습니다. 장기 미수령 물품은 발송인에게 반송될 수 있습니다.",
            "공용 세탁실은 오전 7시부터 오후 11시까지 이용할 수 있습니다. 세탁 종료 후에는 바로 세탁물을 가져가야 합니다. 세제는 개인이 준비합니다. 고장 난 기기는 사용하지 말고 신고해야 합니다.",
            "야간 정숙 시간은 오후 11시부터 다음 날 오전 7시까지입니다. 이 시간에는 복도에서 큰 소리로 대화하지 않습니다. 악기 연주와 큰 음량의 음악 재생은 삼가야 합니다. 민원은 당직실에 접수합니다.",
            "시설 고장은 기숙사 홈페이지에서 접수합니다. 누수 등 긴급한 문제는 당직실에 바로 연락합니다. 방문 수리가 필요한 경우 담당자가 방문 시간을 안내합니다. 입사자는 임의로 시설을 분해하지 않습니다.",
            "외부 방문객은 오후 8시 이전에 퇴실해야 합니다. 방문객은 안내 데스크에서 방문 목적과 방문 호실을 기록합니다. 입사자가 방문객과 동행해야 하며 숙박은 허용되지 않습니다.",
            "퇴사할 때는 개인 물품을 모두 반출하고 방을 청소합니다. 열쇠는 행정실에 반납합니다. 공동 물품의 파손 여부를 담당자가 확인합니다. 남겨진 물품의 처리 절차는 별도 안내를 따릅니다.",
        ]),
    ]
    documents = [{"id": i, "title": title, "text": "\n\n".join(parts),
                  "source": "synthetic_demo_not_public_benchmark"} for i, title, parts in texts]
    # 문서 3개 정리 
    qa = [
        ("library", "학생은 책을 몇 권까지 빌릴 수 있나요?", "5권", "학생은 도서를 최대 5권까지 빌릴 수 있습니다."),
        ("library", "학생이 빌린 책은 기본적으로 며칠 후에 반납하나요?", "14일", "학생의 기본 대출 기간은 14일입니다."),
        ("library", "예약자가 없으면 책을 며칠 더 빌릴 수 있나요?", "7일", "예약자가 없는 도서는 한 번에 한해 7일 연장할 수 있습니다."),
        ("library", "스터디룸은 하루에 얼마나 예약할 수 있나요?", "2시간", "스터디룸은 하루 최대 2시간 예약할 수 있습니다."),
        ("lab", "실습 장비 예약은 며칠 전부터 할 수 있나요?", "3일 전", "장비 예약은 이용일 3일 전부터 가능합니다."),
        ("lab", "실습실 노트북의 최대 대여 시간은 얼마인가요?", "4시간", "노트북은 한 번에 최대 4시간 대여할 수 있습니다."),
        ("lab", "실습실 예약을 취소하려면 언제까지 해야 하나요?", "시작 2시간 전", "예약 취소는 이용 시작 2시간 전까지 해야 합니다."),
        ("dorm", "기숙사에 온 택배는 며칠 동안 보관하나요?", "5일", "기숙사 택배 보관 기간은 도착일로부터 5일입니다."),
        ("dorm", "기숙사에서 조용히 지내야 하는 야간 시간은 언제인가요?", "오후 11시~오전 7시", "야간 정숙 시간은 오후 11시부터 다음 날 오전 7시까지입니다."),
        ("dorm", "기숙사 방문객은 몇 시까지 나가야 하나요?", "오후 8시", "외부 방문객은 오후 8시 이전에 퇴실해야 합니다."),
    ]
    # 질문, 평가기준 목록
    questions = [{"id": f"q{n:02d}", "question": q, "answer": a,
                  "evidence": [{"doc_id": d, "quote": e}]} for n, (d, q, a, e) in enumerate(qa, 1)]
    # 질문 항목 이름 번호 붙이기
    return {"dataset_type": "synthetic_demo", "documents": documents, "questions": questions}


def validate_data(data):  #문서, 질문, 근거 검사 % 근거 위치 표시
    docs = data["documents"]
    questions = data["questions"]
    if not docs or not questions:
        raise ValueError("문서와 질문이 각각 한 개 이상 필요합니다.")
    for items in (docs, questions):
        ids = [x["id"] for x in items]
        if len(ids) != len(set(ids)):
            raise ValueError("문서 또는 질문 ID가 중복됩니다.")
    by_id = {d["id"]: d for d in docs}  #문서 ID 바로 찾기 
    for d in docs:
        if not d["text"].strip():
            raise ValueError("빈 문서는 사용할 수 없습니다.")
    for q in questions:
        if not q["question"].strip() or not q["evidence"]:
            raise ValueError("질문과 정답 근거가 필요합니다.")
        for e in q["evidence"]:
            source = by_id[e["doc_id"]]["text"]
            quote = e["quote"]
            if not quote:
                raise ValueError("정답 근거 인용문이 비어 있습니다.")
            start = e.get("start", source.find(quote))   #정답 근거 원문 어디에 있는지 기록
            if start < 0 or source[start:start + len(quote)] != quote:
                raise ValueError(f"{q['id']}: 근거 문장이 원문과 일치하지 않습니다.")
            if "start" not in e and source.count(quote) != 1:
                raise ValueError("중복 근거 문장은 start 문자 위치를 지정하세요.")
            e.update(start=start, end=start + len(quote))
    return by_id


def token_count(tokenizer, text):  #텍스트 길이 토큰 계산 : tokenizer 임베딩 모델 사용 토큰분할도구
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def split_documents(documents, tokenizer, size): # 기본 청크 경계 설정
    """Token-guided character boundaries; never lose original whitespace/text."""
    chunks = []
    for doc in documents:
        text = doc["text"]
        offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
        # 원문의 문자 위치 (시작, 끝) 토큰 
        boundaries = [0] #위치 청크 
        for i in range(size, len(offsets), size):
            pos = offsets[i][0]
            if pos > boundaries[-1]:
                boundaries.append(pos)
        boundaries.append(len(text))
        for local_id, (start, end) in enumerate(zip(boundaries, boundaries[1:])):
            chunks.append({"id": len(chunks), "doc_id": doc["id"], "local_id": local_id,
                           "start": start, "end": end}) #청크 별 위치 정보
    return chunks


def make_records(mode, chunks, docs, radius): #A,B에 사용할 실제 텍스트 생성/ radius 주변 청크 몇 개씩 포함할지(기본값1)
    grouped = {}
    for c in chunks:
        grouped.setdefault(c["doc_id"], []).append(c)
    records = []
    for c in chunks:
        group = grouped[c["doc_id"]]
        neighbors = group[max(0, c["local_id"] - radius):c["local_id"] + radius + 1]
        rec = dict(c, neighbor_ids=[n["id"] for n in neighbors])
        if mode == "A": # A : 주변 전체 텍스트 범위 지정
            rec["text_start"] = neighbors[0]["start"]
            rec["text_end"] = neighbors[-1]["end"]
        else: # B : 현재 기본 청크만 텍스트 범위 지정
            rec["text_start"], rec["text_end"] = c["start"], c["end"]
        rec["text"] = docs[c["doc_id"]]["text"][rec["text_start"]:rec["text_end"]]
        records.append(rec)
    return records


def prepare_context(mode, ranked_ids, records, chunks, docs, tokenizer, budget):
    """Same rank-first, source-order, base-ID deduplication and budget for A/B."""
    seen, pieces, segments = set(), [], []
    for idx in ranked_ids:
        rec = records[int(idx)]
        for cid in rec["neighbor_ids"]:
            if cid in seen:
                continue
            seen.add(cid)
            c = chunks[cid]
            if mode == "A":
                start = c["start"] - rec["text_start"]
                part = rec["text"][start:start + c["end"] - c["start"]]
            else:
                part = docs[c["doc_id"]]["text"][c["start"]:c["end"]]
            # Preserve adjacent chunks without inserting text into a gold evidence span.
            sep = "" if segments and segments[-1]["doc_id"] == c["doc_id"] and segments[-1]["end"] == c["start"] else "\n\n"
            candidate = "".join(pieces) + (sep if pieces else "") + part
            if token_count(tokenizer, candidate) > budget:
                continue  # Do not cut a chunk; later smaller chunks may still fit.
            pieces.extend(([sep] if pieces else []) + [part])
            segments.append(dict(c))
    return "".join(pieces), segments


def contains_evidence(evidence, segments):
    # Every annotated span is required; coverage can cross contiguous base chunks.
    for e in evidence:
        cursor = e["start"]
        ranges = sorted((s["start"], s["end"]) for s in segments if s["doc_id"] == e["doc_id"])
        for start, end in ranges:
            if start <= cursor:
                cursor = max(cursor, end)
        if cursor < e["end"]:
            return False
    return True


def csv_write(path, rows):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def self_test():
    # An intentionally simple tokenizer ONLY for structural tests, never benchmarks.
    class CharTokenizer:
        def __call__(self, text, **kwargs):
            return {"input_ids": list(range(len(text))), "offset_mapping": [(i, i+1) for i in range(len(text))]}
    tok = CharTokenizer()
    documents = [{"id": "d1", "text": "abcdefghij"}, {"id": "d2", "text": "klmnop"}]
    docs = {d["id"]: d for d in documents}
    chunks = split_documents(documents, tok, 3)
    a = make_records("A", chunks, docs, 1)
    b = make_records("B", chunks, docs, 1)
    for d in documents:
        assert "".join(d["text"][c["start"]:c["end"]] for c in chunks if c["doc_id"] == d["id"]) == d["text"]
    assert a[0]["text"] == "abcdef" and a[3]["text"] == "ghij"
    assert all(chunks[n]["doc_id"] == r["doc_id"] for r in a for n in r["neighbor_ids"])
    for ranking in ([0, 1, 2], [3, 0], [4, 2]):
        for budget in (0, 4, 9, 100):
            ca, sa = prepare_context("A", ranking, a, chunks, docs, tok, budget)
            cb, sb = prepare_context("B", ranking, b, chunks, docs, tok, budget)
            assert (ca, sa) == (cb, sb)
            assert len(ca) <= budget and len({s["id"] for s in sa}) == len(sa)
    e = [{"doc_id": "d1", "start": 2, "end": 5}]
    assert contains_evidence(e, chunks[:2])
    assert not contains_evidence(e, chunks[:1])
    assert not contains_evidence(e, [chunks[0], chunks[2]])
    validate_data(sample_data())
    print("PASS: 원문 보존, 문서 경계, A/B 문맥 일치, 중복 제거, 토큰 제한, 근거 범위, 예제 데이터")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, help="JSON dataset; omitted = synthetic practice data")
    p.add_argument("--out", type=Path, default=Path("ab_results"))
    p.add_argument("--chunk-tokens", type=int, default=150)
    p.add_argument("--radius", type=int, default=1)
    p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--context-tokens", type=int, default=900)
    p.add_argument("--repeats", type=int, default=5, help="Repeated rounds, plus one first-observed round")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--build-order", choices=["AB", "BA"], default="AB")
    p.add_argument("--revision", default=None, help="Optional Hugging Face model commit")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if min(args.chunk_tokens, args.top_k, args.context_tokens, args.repeats, args.batch_size, args.threads) < 1 or args.radius < 0:
        p.error("크기와 반복 수는 양수, radius는 0 이상이어야 합니다.")
    try:
        import numpy as np
        import pandas as pd
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise SystemExit("먼저 pip install -r requirements.txt 를 실행하세요.\n" + str(e))
    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = random.Random(args.seed)
    model_name = "intfloat/multilingual-e5-small"
    print("1/5 임베딩 모델 준비 중. 첫 실행은 모델 다운로드가 필요합니다.", flush=True)
    t = time.perf_counter()
    model = SentenceTransformer(model_name, device=args.device, revision=args.revision)
    model.max_seq_length = 512
    load_s = time.perf_counter() - t
    tokenizer = model.tokenizer
    if not tokenizer.is_fast:
        raise ValueError("문자 위치 추적을 위해 fast tokenizer가 필요합니다.")

    def check_length(texts):
        maximum = max(len(tokenizer(x, add_special_tokens=True)["input_ids"]) for x in texts)
        if maximum > model.max_seq_length:
            raise ValueError(f"임베딩 입력 {maximum}토큰 > {model.max_seq_length}. 자동 절단을 방지했습니다. --chunk-tokens 값을 줄이세요.")
        return maximum

    def sync():
        if args.device == "cuda":
            torch.cuda.synchronize()

    def encode(texts, progress=False):
        return model.encode(texts, batch_size=args.batch_size, normalize_embeddings=True,
                            convert_to_numpy=True, show_progress_bar=progress).astype("float32")

    data = json.loads(args.data.read_text(encoding="utf-8-sig")) if args.data else sample_data()
    docs = validate_data(data)
    check_length(["query: " + q["question"] for q in data["questions"]])
    run = args.out / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    run.mkdir(parents=True, exist_ok=False)
    save_json(run / "dataset.json", data)
    if not args.data:
        print("주의: 내장 데이터는 가상 연습용입니다. ", flush=True)
    # Warm up shared model once. This is recorded and excluded from index build time.
    t = time.perf_counter()
    encode(["query: 준비", "passage: 준비"])
    sync()
    warmup_s = time.perf_counter() - t
    artifacts, build_rows = {}, []
    for mode in args.build_order:
        print(f"2/5 {mode} 인덱스 구축 중", flush=True)
        sync()
        t0 = time.perf_counter()
        chunks = split_documents(data["documents"], tokenizer, args.chunk_tokens)
        records = make_records(mode, chunks, docs, args.radius)
        inputs = ["passage: " + r["text"] for r in records]
        max_input = check_length(inputs)
        t1 = time.perf_counter()
        vectors = encode(inputs, progress=True)
        sync()
        t2 = time.perf_counter()
        folder = run / mode
        folder.mkdir()
        save_json(folder / "corpus.json", data["documents"])
        save_json(folder / "chunks.json", chunks)
        save_json(folder / "records.json", records)
        np.save(folder / "vectors.npy", vectors, allow_pickle=False)
        t3 = time.perf_counter()
        sizes = {f.name: f.stat().st_size for f in folder.iterdir() if f.is_file()}
        # Load both representations into RAM; timed retrieval does not read disk.
        t4 = time.perf_counter()
        loaded_docs = {d["id"]: d for d in json.loads((folder / "corpus.json").read_text(encoding="utf-8"))}
        loaded_records = json.loads((folder / "records.json").read_text(encoding="utf-8"))
        loaded_chunks = json.loads((folder / "chunks.json").read_text(encoding="utf-8"))
        loaded_vectors = np.load(folder / "vectors.npy", allow_pickle=False)
        index_load_s = time.perf_counter() - t4
        artifacts[mode] = (loaded_records, loaded_chunks, loaded_docs, loaded_vectors)
        build_rows.append({"method": mode, "chunk_count": len(chunks), "vector_dimension": vectors.shape[1],
                           "max_embedding_input_tokens": max_input, "chunk_prepare_s": t1-t0,
                           "embedding_s": t2-t1, "save_s": t3-t2, "build_total_s": t3-t0,
                           "index_load_s": index_load_s, "vector_bytes": sizes["vectors.npy"],
                           "corpus_bytes": sizes["corpus.json"],
                           "text_metadata_bytes": sizes["chunks.json"] + sizes["records.json"],
                           "total_storage_bytes": sum(sizes.values())})
    if args.top_k > len(chunks):
        raise ValueError("top-k가 전체 청크 수보다 큽니다. top-k를 줄이세요.")
    csv_write(run / "storage_build.csv", sorted(build_rows, key=lambda x: x["method"]))
    print("3/5 질문별 검색과 반복 측정 중", flush=True)
    rows, examples = [], []
    for repeat in range(args.repeats + 1):
        order = list(range(len(data["questions"])))
        rng.shuffle(order)
        for position, qi in enumerate(order):
            q = data["questions"][qi]
            methods = "AB" if (repeat + position) % 2 == 0 else "BA"
            for mode in methods:
                records, chunks, source_docs, vectors = artifacts[mode]
                sync()
                t0 = time.perf_counter()
                query_vector = encode(["query: " + q["question"]])[0]
                sync()
                t1 = time.perf_counter()
                scores = vectors @ query_vector  # normalized dot product = cosine similarity
                ranking = np.argsort(-scores, kind="stable")[:args.top_k]
                t2 = time.perf_counter()
                context, segments = prepare_context(mode, ranking, records, chunks, source_docs,
                                                    tokenizer, args.context_tokens)
                t3 = time.perf_counter()
                hit = contains_evidence(q["evidence"], segments)
                rows.append({"method": mode, "question_id": q["id"], "repeat": repeat,
                             "phase": "first_observed" if repeat == 0 else "repeated",
                             "order_in_pair": methods.index(mode) + 1,
                             "question_embedding_ms": (t1-t0)*1000, "vector_search_ms": (t2-t1)*1000,
                             "context_prepare_ms": (t3-t2)*1000, "retrieval_total_ms": (t3-t0)*1000,
                             "initial_evidence_hit": int(hit), "context_tokens": token_count(tokenizer, context),
                             "retrieved_ids": json.dumps(ranking.tolist()), "context_chunk_count": len(segments)})
                if repeat == 0:
                    examples.append({"method": mode, "question_id": q["id"], "question": q["question"],
                                     "reference_answer": q.get("answer", ""), "evidence": q["evidence"],
                                     "initial_evidence_hit": hit, "retrieved_ids": ranking.tolist(),
                                     "scores": [float(scores[i]) for i in ranking],
                                     "context": context, "segments": segments})
    csv_write(run / "query_runs.csv", rows)
    save_json(run / "contexts.json", examples)
    frame = pd.DataFrame(rows)
    summaries = []
    for (mode, phase), group in frame.groupby(["method", "phase"]):
        item = {"method": mode, "phase": phase, "unique_questions": group.question_id.nunique(),
                "timed_runs": len(group), "initial_evidence_rate": group.groupby("question_id").initial_evidence_hit.mean().mean(),
                "mean_context_tokens": group.context_tokens.mean()}
        for field in ("question_embedding_ms", "vector_search_ms", "context_prepare_ms", "retrieval_total_ms"):
            item[field + "_mean"] = group[field].mean()
            item[field + "_median"] = group[field].median()
            item[field + "_p95"] = group[field].quantile(.95)
        summaries.append(item)
    csv_write(run / "summary.csv", summaries)
    packages = {}
    for name in ("sentence-transformers", "transformers", "torch", "numpy", "pandas", "tokenizers", "huggingface-hub"):
        packages[name] = importlib.metadata.version(name)
    config = model[0].auto_model.config
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "arguments": vars(args),
                "model": model_name, "resolved_model_commit": getattr(config, "_commit_hash", None),
                "model_max_seq_length": model.max_seq_length, "model_load_s": load_s,
                "model_warmup_s": warmup_s, "dataset_type": data.get("dataset_type", "user_supplied"),
                "dataset_sha256": hashlib.sha256((run / "dataset.json").read_bytes()).hexdigest(),
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "python": sys.version, "platform": platform.platform(), "processor": platform.processor(),
                "torch_threads": torch.get_num_threads(), "device": str(model.device),
                "gpu": torch.cuda.get_device_name() if args.device == "cuda" else None,
                "packages": packages, "cache_policy": "Both indexes and corpus preloaded in RAM; OS caches not cleared",
                "not_measured": ["CRAG evaluation", "supplementary retrieval", "first answer latency", "answer accuracy"],
                "build_timing_note": "Single build per method after shared warmup; use reverse order in a separate run"}
    manifest["arguments"] = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    save_json(run / "run_config.json", manifest)
    (run / "installed_versions.txt").write_text("\n".join(f"{k}=={v}" for k, v in packages.items()) + "\n", encoding="utf-8")
    print("4/5 결과 저장 완료", flush=True)
    print(pd.DataFrame(summaries)[["method", "phase", "initial_evidence_rate", "retrieval_total_ms_median"]].to_string(index=False))
    print(f"5/5 결과 폴더: {run.resolve()}")
    print("근거 포함률은 답변 정확도가 아닙니다. CRAG/LLM은 아직 연결하지 않았습니다.")


if __name__ == "__main__":
    main()
