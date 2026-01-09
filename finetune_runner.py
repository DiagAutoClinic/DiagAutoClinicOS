import argparse
import json
import math
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests


@dataclass(frozen=True)
class EvalMetrics:
    precision: float
    recall: float
    f1: float
    accuracy: float
    ece: float
    brier: float
    kill_rate: float
    n: int


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            rows.append(json.loads(s))
    return rows


def _safe_json_loads(s: str) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _top1_prediction(obj: Dict[str, Any]) -> Tuple[Optional[str], float]:
    ranked = obj.get("ranked_faults", [])
    if not isinstance(ranked, list) or not ranked:
        return None, 0.0
    item = ranked[0] if isinstance(ranked[0], dict) else None
    if not item:
        return None, 0.0
    fault = item.get("fault")
    prob = item.get("probability", 0.0)
    return (fault if isinstance(fault, str) else None), float(prob) if isinstance(prob, (int, float)) else 0.0


def _ece(conf: List[float], correct: List[int], bins: int = 10) -> float:
    if not conf:
        return 0.0
    n = len(conf)
    edges = [i / bins for i in range(bins + 1)]
    ece = 0.0
    for b in range(bins):
        lo, hi = edges[b], edges[b + 1]
        idx = [i for i, c in enumerate(conf) if (c >= lo and (c < hi if b < bins - 1 else c <= hi))]
        if not idx:
            continue
        acc = sum(correct[i] for i in idx) / len(idx)
        avg_conf = sum(conf[i] for i in idx) / len(idx)
        ece += (len(idx) / n) * abs(acc - avg_conf)
    return float(ece)


def _brier(conf: List[float], correct: List[int]) -> float:
    if not conf:
        return 0.0
    s = 0.0
    for p, y in zip(conf, correct):
        s += (float(p) - float(y)) ** 2
    return float(s / len(conf))


def _metrics_from_rows(rows: List[Dict[str, Any]], pred_key: str = "assistant") -> EvalMetrics:
    y_true: List[str] = []
    y_pred: List[str] = []
    conf: List[float] = []
    correct: List[int] = []

    kills = 0
    total = 0

    for r in rows:
        gt = r.get("target", {}).get("ground_truth", {})
        true_fault = gt.get("primary_fault")
        if not isinstance(true_fault, str):
            continue

        pred_obj = None
        if pred_key == "assistant":
            pred_obj = _safe_json_loads(r.get("assistant", "")) or {}
        else:
            pred_obj = r.get(pred_key, {}) if isinstance(r.get(pred_key), dict) else {}

        pred_fault, pred_prob = _top1_prediction(pred_obj)
        if pred_fault is None:
            pred_fault = "unknown"
            pred_prob = 0.0

        y_true.append(true_fault)
        y_pred.append(pred_fault)
        conf.append(float(max(0.0, min(1.0, pred_prob))))
        correct.append(1 if pred_fault == true_fault else 0)

        dq = r.get("target", {}).get("data_quality", {}) or {}
        is_lean = False
        try:
            lam = r.get("live_data", {}).get("live_parameters", {}).get("lambda", {}).get("value")
            is_lean = isinstance(lam, (int, float)) and lam > 1.15
        except Exception:
            is_lean = False

        if pred_fault == "normal_operation" and true_fault != "normal_operation" and not dq.get("ood") and is_lean:
            kills += 1

        total += 1

    if not y_true:
        return EvalMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)

    labels = sorted(set(y_true) | set(y_pred))
    tp = {lab: 0 for lab in labels}
    fp = {lab: 0 for lab in labels}
    fn = {lab: 0 for lab in labels}
    for t, p in zip(y_true, y_pred):
        if t == p:
            tp[t] += 1
        else:
            fp[p] += 1
            fn[t] += 1

    macro_p = 0.0
    macro_r = 0.0
    macro_f1 = 0.0
    for lab in labels:
        p = tp[lab] / (tp[lab] + fp[lab]) if (tp[lab] + fp[lab]) else 0.0
        r = tp[lab] / (tp[lab] + fn[lab]) if (tp[lab] + fn[lab]) else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        macro_p += p
        macro_r += r
        macro_f1 += f1

    n_labels = len(labels) if labels else 1
    macro_p /= n_labels
    macro_r /= n_labels
    macro_f1 /= n_labels

    acc = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)
    ece = _ece(conf, correct, bins=10)
    brier = _brier(conf, correct)
    kill_rate = kills / total if total else 0.0

    return EvalMetrics(
        precision=float(macro_p),
        recall=float(macro_r),
        f1=float(macro_f1),
        accuracy=float(acc),
        ece=float(ece),
        brier=float(brier),
        kill_rate=float(kill_rate),
        n=int(len(y_true)),
    )


def _openai_headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _openai_upload_file(api_key: str, file_path: str) -> str:
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://api.openai.com/v1/files",
            headers=_openai_headers(api_key),
            files={"file": (os.path.basename(file_path), f)},
            data={"purpose": "fine-tune"},
            timeout=120,
        )
    resp.raise_for_status()
    return str(resp.json()["id"])


def _openai_create_finetune_job(api_key: str, model: str, training_file_id: str, validation_file_id: Optional[str]) -> str:
    payload: Dict[str, Any] = {"model": model, "training_file": training_file_id}
    if validation_file_id:
        payload["validation_file"] = validation_file_id
    resp = requests.post(
        "https://api.openai.com/v1/fine_tuning/jobs",
        headers={**_openai_headers(api_key), "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=120,
    )
    resp.raise_for_status()
    return str(resp.json()["id"])


def _openai_get_job(api_key: str, job_id: str) -> Dict[str, Any]:
    resp = requests.get(
        f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}",
        headers=_openai_headers(api_key),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _openai_chat_completion(api_key: str, model: str, user_prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": 0.0,
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={**_openai_headers(api_key), "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return str(data["choices"][0]["message"]["content"])


def cmd_openai(args: argparse.Namespace) -> int:
    api_key = str(args.api_key or os.getenv("OPENAI_API_KEY", ""))
    if not api_key:
        raise SystemExit("Missing --api-key or OPENAI_API_KEY")

    train_file = str(args.train_file)
    val_file = str(args.val_file) if args.val_file else None
    base_model = str(args.model)

    print("Uploading training file...")
    train_id = _openai_upload_file(api_key, train_file)
    val_id = None
    if val_file:
        print("Uploading validation file...")
        val_id = _openai_upload_file(api_key, val_file)

    print("Creating fine-tuning job...")
    job_id = _openai_create_finetune_job(api_key, base_model, train_id, val_id)
    print(f"Job id: {job_id}")

    if not args.monitor:
        return 0

    last_status = None
    while True:
        job = _openai_get_job(api_key, job_id)
        status = job.get("status")
        fine_tuned_model = job.get("fine_tuned_model")
        if status != last_status:
            print(f"Status: {status}")
            last_status = status
        if status in {"succeeded", "failed", "cancelled"}:
            print(json.dumps(job, indent=2))
            if fine_tuned_model:
                print(f"Fine-tuned model: {fine_tuned_model}")
            return 0 if status == "succeeded" else 2
        time.sleep(float(args.poll_seconds))


def cmd_evaluate(args: argparse.Namespace) -> int:
    rows = _read_jsonl(str(args.test_file))
    model_type = str(args.model_type).lower()

    if model_type == "raw":
        metrics = _metrics_from_rows(rows, pred_key="assistant")
        print(json.dumps(metrics.__dict__, indent=2))
        return 0

    if model_type == "openai":
        api_key = str(args.api_key or os.getenv("OPENAI_API_KEY", ""))
        if not api_key:
            raise SystemExit("Missing --api-key or OPENAI_API_KEY")
        model_id = str(args.model_id)
        out_rows: List[Dict[str, Any]] = []
        for i, r in enumerate(rows):
            user = r.get("user")
            if not isinstance(user, str):
                continue
            content = _openai_chat_completion(api_key, model_id, user)
            parsed = _safe_json_loads(content) or {"raw": content}
            rr = dict(r)
            rr["model_output"] = parsed
            out_rows.append(rr)
            if args.max_examples and len(out_rows) >= int(args.max_examples):
                break
            if (i + 1) % 25 == 0:
                print(f"Evaluated {i + 1}/{len(rows)}")

        metrics = _metrics_from_rows(out_rows, pred_key="model_output")
        print(json.dumps(metrics.__dict__, indent=2))

        if args.output_predictions:
            os.makedirs(os.path.dirname(os.path.abspath(str(args.output_predictions))), exist_ok=True)
            with open(str(args.output_predictions), "w", encoding="utf-8") as f:
                for rr in out_rows:
                    f.write(json.dumps(rr, ensure_ascii=False) + "\n")
        return 0

    raise SystemExit(f"Unsupported model_type: {model_type}")


def cmd_compare(args: argparse.Namespace) -> int:
    rows = _read_jsonl(str(args.test_file))
    api_key = str(args.api_key or os.getenv("OPENAI_API_KEY", ""))
    if not api_key:
        raise SystemExit("Missing --api-key or OPENAI_API_KEY")
    model_ids = [m.strip() for m in str(args.model_ids).split(",") if m.strip()]
    if not model_ids:
        raise SystemExit("Provide --model-ids as comma-separated list")

    results: Dict[str, Any] = {"models": {}, "n": len(rows)}
    for model_id in model_ids:
        out_rows: List[Dict[str, Any]] = []
        for r in rows[: int(args.max_examples or len(rows))]:
            user = r.get("user")
            if not isinstance(user, str):
                continue
            content = _openai_chat_completion(api_key, model_id, user)
            parsed = _safe_json_loads(content) or {"raw": content}
            rr = dict(r)
            rr["model_output"] = parsed
            out_rows.append(rr)
        metrics = _metrics_from_rows(out_rows, pred_key="model_output")
        results["models"][model_id] = metrics.__dict__
        print(f"{model_id}: F1={metrics.f1:.3f} Acc={metrics.accuracy:.3f} ECE={metrics.ece:.3f} Kill={metrics.kill_rate:.3f} (n={metrics.n})")

    if args.output_report:
        os.makedirs(os.path.dirname(os.path.abspath(str(args.output_report))), exist_ok=True)
        with open(str(args.output_report), "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    return 0


def cmd_lora(args: argparse.Namespace) -> int:
    try:
        import torch  # type: ignore
        from datasets import load_dataset  # type: ignore
        from peft import LoraConfig, get_peft_model  # type: ignore
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments  # type: ignore
    except Exception as e:
        raise SystemExit(
            "Local LoRA dependencies missing. Install: pip install torch transformers datasets peft accelerate"
        ) from e

    train_path = str(args.train_file)
    val_path = str(args.val_file) if args.val_file else None
    base_model = str(args.base_model)
    out_dir = str(args.output_dir)

    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16 if torch.cuda.is_available() else None)
    lora_cfg = LoraConfig(
        r=int(args.r),
        lora_alpha=int(args.alpha),
        lora_dropout=float(args.dropout),
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_cfg)

    def format_row(row: Dict[str, Any]) -> Dict[str, Any]:
        user = row.get("user", "")
        assistant = row.get("assistant", "")
        text = f"{user}\n{assistant}"
        toks = tokenizer(
            text,
            truncation=True,
            max_length=int(args.max_length),
            padding="max_length",
        )
        toks["labels"] = list(toks["input_ids"])
        return toks

    ds = load_dataset("json", data_files={"train": train_path, "validation": val_path} if val_path else {"train": train_path})
    ds = ds.map(format_row, remove_columns=ds["train"].column_names)

    train_args = TrainingArguments(
        output_dir=out_dir,
        per_device_train_batch_size=int(args.batch_size),
        per_device_eval_batch_size=int(args.batch_size),
        learning_rate=float(args.learning_rate),
        num_train_epochs=float(args.epochs),
        evaluation_strategy="steps" if val_path else "no",
        save_strategy="steps",
        save_steps=int(args.save_steps),
        eval_steps=int(args.eval_steps),
        logging_steps=int(args.logging_steps),
        warmup_ratio=float(args.warmup_ratio),
        fp16=torch.cuda.is_available(),
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=ds["train"],
        eval_dataset=ds.get("validation"),
    )
    trainer.train()
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f"Saved LoRA adapter to: {os.path.abspath(out_dir)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_openai = sub.add_parser("openai")
    p_openai.add_argument("--api-key", type=str, default=None)
    p_openai.add_argument("--train-file", type=str, required=True)
    p_openai.add_argument("--val-file", type=str, default=None)
    p_openai.add_argument("--model", type=str, required=True)
    p_openai.add_argument("--monitor", action="store_true")
    p_openai.add_argument("--poll-seconds", type=float, default=15.0)
    p_openai.set_defaults(func=cmd_openai)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--test-file", type=str, required=True)
    p_eval.add_argument("--model-type", type=str, choices=["raw", "openai"], required=True)
    p_eval.add_argument("--model-id", type=str, default="")
    p_eval.add_argument("--api-key", type=str, default=None)
    p_eval.add_argument("--max-examples", type=int, default=0)
    p_eval.add_argument("--output-predictions", type=str, default="")
    p_eval.set_defaults(func=cmd_evaluate)

    p_cmp = sub.add_parser("compare")
    p_cmp.add_argument("--test-file", type=str, required=True)
    p_cmp.add_argument("--model-ids", type=str, required=True)
    p_cmp.add_argument("--api-key", type=str, default=None)
    p_cmp.add_argument("--max-examples", type=int, default=200)
    p_cmp.add_argument("--output-report", type=str, default="")
    p_cmp.set_defaults(func=cmd_compare)

    p_lora = sub.add_parser("lora")
    p_lora.add_argument("--train-file", type=str, required=True)
    p_lora.add_argument("--val-file", type=str, default=None)
    p_lora.add_argument("--base-model", type=str, required=True)
    p_lora.add_argument("--output-dir", type=str, required=True)
    p_lora.add_argument("--max-length", type=int, default=1024)
    p_lora.add_argument("--batch-size", type=int, default=1)
    p_lora.add_argument("--epochs", type=float, default=1.0)
    p_lora.add_argument("--learning-rate", type=float, default=2e-4)
    p_lora.add_argument("--warmup-ratio", type=float, default=0.03)
    p_lora.add_argument("--save-steps", type=int, default=200)
    p_lora.add_argument("--eval-steps", type=int, default=200)
    p_lora.add_argument("--logging-steps", type=int, default=25)
    p_lora.add_argument("--r", type=int, default=16)
    p_lora.add_argument("--alpha", type=int, default=32)
    p_lora.add_argument("--dropout", type=float, default=0.05)
    p_lora.set_defaults(func=cmd_lora)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

