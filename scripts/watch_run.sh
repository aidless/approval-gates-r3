#!/bin/bash
# watch_run.sh — 守共享 GPU 显存窗口，抢跑 qwen3:8b harness（断点续跑，直到全部完成）。
# 关键：窗口开时先 ollama stop 再重新加载（强制全 GPU + 小 context），避免残留在 CPU offload。
cd /root/autodl-tmp/jmf_harness
OUT=results_qwen3_8b_v3
NEED=7000          # qwen3:8b-c4k (num_ctx locked 4096) = 5.6GB; 100% GPU needs ~7G
LOG=watch.log
echo "$(date '+%F %T') watcher-v2 started, need=${NEED}MiB, target=$OUT/summary.json" >> $LOG

while [ ! -f "$OUT/summary.json" ]; do
  FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  FREE=${FREE:-0}
  if [ "$FREE" -ge "$NEED" ]; then
    echo "$(date '+%F %T') WINDOW free=${FREE}MiB -> stop+reload+run" >> $LOG
    # 1) 停掉旧的（可能 CPU-offload 的）实例，释放显存
    ollama stop qwen3:8b-c4k >/dev/null 2>&1
    sleep 3
    # 2) 重新加载：小 context + 全 GPU
    curl -sS --max-time 180 http://127.0.0.1:11434/api/chat \
      -d '{"model":"qwen3:8b-c4k","messages":[{"role":"user","content":"OK"}],"stream":false,"think":false,"keep_alive":"30m","options":{"temperature":0,"num_predict":4,"num_ctx":4096,"num_gpu":99}}' \
      -o /dev/null 2>>$LOG
    # 3) 跑 harness（断点续跑 + 显存门控）
    python3 harness.py >> run_q3_8b.log 2>&1
    echo "$(date '+%F %T') harness run ended; done=$(ls $OUT/per_seed/*.json 2>/dev/null | wc -l)/9" >> $LOG
  else
    sleep 15
  fi
done
echo "$(date '+%F %T') ALL DONE: $OUT/summary.json exists" >> $LOG