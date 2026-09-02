#!/usr/bin/env python3
"""session-nudge 机械核心：向指定 ZCode 会话注入一条消息让它继续干活。

流程：查会话与原模型 → 构造凭据候选链 → 逐候选探针（zcode -p "1"，无 resume）
→ swap 全局 CLI 配置（文件锁串行，try/finally 必还原）→ 真注入（--resume --json）
→ 还原配置 → 打印结果 JSON。

用法：
  python -X utf8 nudge_session.py --session sess_xxx --message "继续：…" [--force] [--dry-run]
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOME = Path.home()
CLI_CONFIG = HOME / ".zcode" / "cli" / "config.json"
V2_CONFIG = HOME / ".zcode" / "v2" / "config.json"
DB = HOME / ".zcode" / "cli" / "db" / "db.sqlite"
LOCK = Path(tempfile.gettempdir()) / "session-nudge.lock"
STALE_MS = 60 * 60 * 1000  # 会话停止 60 分钟才允许注入（--force 覆盖）

# 回退凭据：tokenrhythm 原账号（2026-09-01 实测可用）
DEFAULT_PROVIDER_ID = "d20bde8b-1b7a-4a93-aec7-56fd37f46282"
DEFAULT_MODEL = "deepseek-v4-flash-0731"


def die(msg):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(1)


def query_session(sid):
    con = sqlite3.connect(str(DB))
    cur = con.cursor()
    row = cur.execute(
        "SELECT id, title, directory, time_updated FROM session WHERE id=?", (sid,)
    ).fetchone()
    if not row:
        die(f"会话不存在：{sid}")
    usage = cur.execute(
        "SELECT provider_id, model_id, variant FROM model_usage "
        "WHERE session_id=? ORDER BY started_at DESC LIMIT 1",
        (sid,),
    ).fetchone()
    con.close()
    return {"id": row[0], "title": row[1], "directory": row[2],
            "time_updated": row[3], "last_model": usage}


def build_candidates(last_model, session_model_id):
    """候选 = [(provider别名, kind, baseURL, apiKey, model_id)]，实测失败逐级降级。"""
    v2 = json.loads(V2_CONFIG.read_text(encoding="utf-8"))
    provs = v2.get("provider", {})
    cands = []
    if last_model:
        pid, mid = last_model[0], last_model[1]
        p = provs.get(pid)
        if p and p.get("options", {}).get("apiKey"):
            cands.append((pid[:8], p.get("kind"), p["options"]["baseURL"],
                          p["options"]["apiKey"], mid))
    if session_model_id:
        p = provs.get(DEFAULT_PROVIDER_ID, {})
        if p.get("options", {}).get("apiKey"):
            cands.append(("nudge-default", p.get("kind"), p["options"]["baseURL"],
                          p["options"]["apiKey"], session_model_id))
    p = provs.get(DEFAULT_PROVIDER_ID, {})
    if p.get("options", {}).get("apiKey"):
        cands.append(("nudge-default", p.get("kind"), p["options"]["baseURL"],
                      p["options"]["apiKey"], DEFAULT_MODEL))
    # 注意：禁止加入 deepseek 官方等计费 API（用户 2026-09-02 明令：未经许可不得自动选用）
    return cands


def swap_config(candidate, original_bytes):
    cfg = json.loads(original_bytes.decode("utf-8"))
    alias, kind, base, key, model = candidate
    cfg["provider"] = {alias: {"kind": kind or "openai-compatible", "name": alias,
                               "options": {"apiKey": key, "baseURL": base},
                               "models": {model: {"name": model}}}}
    cfg["model"] = {"main": f"{alias}/{model}"}
    CLI_CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def run_zcode(args, timeout):
    return subprocess.run(["zcode", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--message", required=True)
    ap.add_argument("--force", action="store_true", help="跳过死会话判据")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    info = query_session(a.session)
    age = int(time.time() * 1000) - info["time_updated"]
    if age < STALE_MS and not a.force:
        die(f"会话可能仍活跃（最后活动 {age//60000} 分钟前），拒绝注入；确认已死加 --force")

    cands = build_candidates(info["last_model"], info["last_model"][1] if info["last_model"] else None)
    if not cands:
        die("无可用凭据候选（v2 配置缺 apiKey）")

    original = CLI_CONFIG.read_bytes()
    if a.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "session": info,
                          "candidates": [(*c[:2], c[4]) for c in cands]}, ensure_ascii=False, indent=1))
        return

    lock_fd = None
    if LOCK.exists() and (time.time() - LOCK.stat().st_mtime) > 600:
        LOCK.unlink()  # 陈旧锁（进程被杀未释放）自动接管
    try:
        lock_fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL)
        chosen, probe_report = None, []
        for cand in cands:
            swap_config(cand, original)
            try:
                r = run_zcode(["-p", "1"], 120)
                ok = r.returncode == 0
            except subprocess.TimeoutExpired:
                ok = False
            probe_report.append({"alias": cand[0], "model": cand[4], "probe_ok": ok})
            if ok:
                chosen = cand
                break
        if not chosen:
            die(f"所有凭据候选探针失败：{probe_report}")
        swap_config(chosen, original)
        r = run_zcode(["-p", a.message, "--resume", a.session, "--json"], a.timeout)
        out = r.stdout.strip()
        try:
            result = json.loads(out)
        except Exception:
            result = {"raw": out[-2000:], "stderr": r.stderr[-1000:]}
        result["nudge"] = {"model": f"{chosen[0]}/{chosen[4]}", "probe": probe_report,
                           "session_title": info["title"]}
        print(json.dumps(result, ensure_ascii=False, indent=1))
    finally:
        CLI_CONFIG.write_bytes(original)
        if lock_fd is not None:
            os.close(lock_fd)
        if LOCK.exists():
            os.unlink(LOCK)


if __name__ == "__main__":
    main()
