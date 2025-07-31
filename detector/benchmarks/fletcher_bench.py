import argparse
import csv
import os
import time, random
from statistics import mean

from detector.fletcher import emisor_fletcher
from detector.emitter.ruido import apply_ber
from detector.emitter.transmision import send_over_tcp, JsonlClient

def parse_args():
    p = argparse.ArgumentParser("Fletcher bench (detección)")
    p.add_argument("--host", required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--trials", type=int, default=10000,
                   help="Iteraciones por combinación (longitud × BER × block)")
    p.add_argument("--lengths", default="5,11,50",
                   help="Longitudes de mensaje (bytes), separadas por coma")
    p.add_argument("--bers", default="0,0.001,0.01,0.05",
                   help="BERs separadas por coma")
    p.add_argument("--blocks", default="8,16,32",
                   help="Tamaños de bloque para Fletcher (8/16/32)")
    p.add_argument("--seed", type=int, default=123)
    p.add_argument("--out-csv", default="docs/fletcher_stats.csv")
    p.add_argument("--plots-dir", default="docs/plots")
    return p.parse_args()

def rand_bytes(n: int) -> bytes:
    # Mensajes aleatorios en ASCII imprimible
    alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789"
    return bytes(random.choice(alphabet) for _ in range(n))

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def run_combo(host, port, trials, length, ber, block_size, seed):
    random.seed(seed)
    t_start = time.perf_counter()

    # Contadores
    ok_true = 0                   # receptor aceptó
    ok_false = 0                  # receptor rechazó
    flips_trials = 0              # veces que hubo flips reales (>0 bits)
    err_and_ok = 0                # FALSO NEGATIVO: hubo flips, receptor aceptó
    err_and_rej = 0               # Detección correcta: hubo flips y receptor rechazó
    noerr_and_ok = 0              # Aceptó correctamente sin flips
    noerr_and_rej = 0             # FALSO POSITIVO: sin flips y receptor rechazó
    no_response = 0               # receptor no respondió (timeout / caída)
    times_ms = []

    overhead_bytes = 2 * (block_size // 8)
    overhead_ratio_samples = []

    with JsonlClient(host, port) as client:
        for _ in range(trials):
            msg = rand_bytes(length)
            frame = emisor_fletcher(msg, block_size)

            # overhead relativo de esta trama
            overhead_ratio_samples.append(overhead_bytes / max(1, len(msg)))

            # ruído canal
            noisy_frame, flipped_bits = apply_ber(frame, ber)
            had_flips = len(flipped_bits) > 0
            if had_flips:
                flips_trials += 1

            t0 = time.perf_counter()
            payload = {
                "alg": "fletcher",
                "block_size": block_size,
                "frame_hex": noisy_frame.hex(),
            }
            resp = send_over_tcp(host, port, "fletcher", block_size, noisy_frame)
            t1 = time.perf_counter()
            times_ms.append((t1 - t0) * 1000.0)

            if not resp:
                no_response += 1
                continue

            ok = bool(resp.get("ok", False))
            if ok:
                ok_true += 1
                if had_flips:
                    err_and_ok += 1      # falso negativo
                else:
                    noerr_and_ok += 1    # aceptación correcta sin errores
            else:
                ok_false += 1
                if had_flips:
                    err_and_rej += 1     # detección correcta
                else:
                    noerr_and_rej += 1   # falso positivo

    trials_eff = trials - no_response
    det_rate = (err_and_rej / flips_trials) if flips_trials > 0 else 0.0
    fn_rate  = (err_and_ok / flips_trials) if flips_trials > 0 else 0.0
    fp_rate  = (noerr_and_rej / (trials_eff - flips_trials)) if (trials_eff - flips_trials) > 0 else 0.0
    acc_rate = (ok_true / trials_eff) if trials_eff > 0 else 0.0

    return {
        "alg": "fletcher",
        "block_size": block_size,
        "length": length,
        "ber": ber,
        "trials": trials,
        "no_response": no_response,
        "flips_trials": flips_trials,
        "ok_true": ok_true,
        "ok_false": ok_false,
        "error_and_ok": err_and_ok,         # falso negativo
        "error_and_rejected": err_and_rej,  # detección correcta
        "noerror_and_ok": noerr_and_ok,
        "noerror_and_rejected": noerr_and_rej,  # falso positivo
        "detection_rate": det_rate,
        "false_negative_rate": fn_rate,
        "false_positive_rate": fp_rate,
        "acceptance_rate": acc_rate,
        "avg_ms": mean(times_ms) if times_ms else 0.0,
        "overhead_bytes": overhead_bytes,
        "avg_overhead_ratio": mean(overhead_ratio_samples) if overhead_ratio_samples else 0.0,
        "elapsed_s": time.perf_counter() - t_start,
    }

def write_csv(rows, path):
    ensure_dir(os.path.dirname(path) or ".")
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def plot_from_csv(csv_path: str, plots_dir: str):
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print("matplotlib no disponible; se omitió la generación de gráficos.", e)
        return

    import math
    import collections

    ensure_dir(plots_dir)

    # Cargar CSV
    import csv as _csv
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in _csv.DictReader(f):
            # Convertir tipos
            r["block_size"] = int(r["block_size"])
            r["length"] = int(r["length"])
            r["ber"] = float(r["ber"])
            r["detection_rate"] = float(r["detection_rate"])
            r["false_negative_rate"] = float(r["false_negative_rate"])
            rows.append(r)

    # Agrupar por length
    by_len = collections.defaultdict(list)
    for r in rows:
        by_len[r["length"]].append(r)

    for L, group in by_len.items():
        # Curvas: x = BER, y = detection_rate / false_negative_rate, una curva por block_size
        for metric in ("detection_rate", "false_negative_rate"):
            plt.figure()
            for bs in sorted({g["block_size"] for g in group}):
                sub = [g for g in group if g["block_size"] == bs]
                sub = sorted(sub, key=lambda x: x["ber"])
                xs = [s["ber"] for s in sub]
                ys = [s[metric] for s in sub]
                plt.plot(xs, ys, marker="o", label=f"block={bs}")
            plt.xlabel("BER")
            plt.ylabel(metric.replace("_", " "))
            plt.title(f"Fletcher – {metric} vs BER (length={L})")
            plt.legend()
            out = os.path.join(plots_dir, f"{metric}_len{L}.png")
            plt.savefig(out, dpi=160, bbox_inches="tight")
            plt.close()

def main():
    args = parse_args()
    random.seed(args.seed)

    lengths = [int(x) for x in args.lengths.split(",") if x.strip()]
    bers = [float(x) for x in args.bers.split(",") if x.strip()]
    blocks = [int(x) for x in args.blocks.split(",") if x.strip()]

    all_rows = []
    for bs in blocks:
        for L in lengths:
            for ber in bers:
                print(f"[RUN] block={bs} length={L} ber={ber} trials={args.trials}")
                res = run_combo(args.host, args.port, args.trials, L, ber, bs, seed=args.seed)
                print(f"  -> detection_rate={res['detection_rate']:.4f} "
                      f"fn_rate={res['false_negative_rate']:.6f} "
                      f"acc={res['acceptance_rate']:.4f} "
                      f"no_response={res['no_response']}")
                all_rows.append(res)

    write_csv(all_rows, args.out_csv)
    print(f"CSV guardado en: {args.out_csv}")

    ensure_dir(args.plots_dir)
    plot_from_csv(args.out_csv, args.plots_dir)
    print(f"Gráficas en: {args.plots_dir}")

if __name__ == "__main__":
    main()
