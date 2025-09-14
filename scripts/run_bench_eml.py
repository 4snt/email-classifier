#!/usr/bin/env python3
import argparse
import os
import time
import random
import requests
from pathlib import Path

def send_one(path: str, url: str, profile_id: str | None, timeout: int):
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f, "message/rfc822")}
        params = {}
        if profile_id:
            params["profile_id"] = profile_id
        return requests.post(url, files=files, params=params, timeout=timeout)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="pasta com .eml")
    ap.add_argument("--url", default="http://127.0.0.1:8000/classify")
    ap.add_argument("--profile-id", default=None, help="profile_id padrão (opcional)")
    ap.add_argument("--rpm", type=float, default=5.0, help="requests por minuto (default 5)")
    ap.add_argument("--retry", type=int, default=3, help="tentativas por item (em caso de 429/erro)")
    ap.add_argument("--timeout", type=int, default=60, help="timeout por request (s)")
    ap.add_argument("--shuffle", action="store_true", help="embaralhar a ordem dos arquivos")
    args = ap.parse_args()

    files = [str(Path(args.dir) / f) for f in os.listdir(args.dir) if f.lower().endswith(".eml")]
    if args.shuffle:
        random.shuffle(files)
    files.sort()  # se não embaralhar, ordena pelo nome

    min_interval = 60.0 / max(args.rpm, 0.1)  # espaçamento mínimo entre envios
    jitter_frac = 0.10  # 10% do intervalo para evitar burst exato
    last_sent = 0.0

    ok = 0
    fail = 0
    status_counts: dict[int, int] = {}

    for i, fp in enumerate(files, 1):
        # respeita o intervalo mínimo entre requisições
        now = time.monotonic()
        wait = min_interval - (now - last_sent)
        if wait > 0:
            time.sleep(wait + random.uniform(0, jitter_frac * min_interval))

        attempts = 0
        while attempts < args.retry:
            attempts += 1
            try:
                r = send_one(fp, args.url, args.profile_id, args.timeout)
            except requests.RequestException as e:
                print(f"[{i}/{len(files)}] {os.path.basename(fp)} -> ERROR {e}")
                if attempts >= args.retry:
                    fail += 1
                else:
                    time.sleep(2.0)
                continue

            status_counts[r.status_code] = status_counts.get(r.status_code, 0) + 1

            if r.status_code == 429:
                # respeita Retry-After (segundos) quando presente
                ra = r.headers.get("Retry-After")
                try:
                    wait_429 = float(ra) if ra is not None else 60.0
                except ValueError:
                    wait_429 = 60.0
                print(f"[{i}/{len(files)}] {os.path.basename(fp)} -> 429, aguardando {wait_429:.1f}s e tentando novamente ({attempts}/{args.retry})")
                time.sleep(wait_429 + random.uniform(0, 1.0))
                continue

            # sucesso/erro “de verdade”
            try:
                payload = r.json()
            except Exception:
                payload = r.text[:200]

            print(f"[{i}/{len(files)}] {os.path.basename(fp)} -> {r.status_code} {payload}")
            if r.ok:
                ok += 1
            else:
                fail += 1
            break 

        last_sent = time.monotonic()

    total = ok + fail
    print("\n=== SUMÁRIO ===")
    print(f"Total: {total} | OK: {ok} | FAIL: {fail}")
    for sc in sorted(status_counts):
        print(f"  {sc}: {status_counts[sc]}")

if __name__ == "__main__":
    main()
