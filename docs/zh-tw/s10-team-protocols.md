# s10: Team Protocols (團隊協議)

`s01 > s02 > s03 > s04 > s05 > s06 | s07 > s08 > s09 > [ s10 ] s11 > s12`

> *"隊友之間要有統一的溝通規矩"* -- 一個 request-response 模式驅動所有協商。
>
> **Harness 層**: 協議 -- 模型之間的結構化握手。

## 問題

s09 中隊友能幹活能通訊, 但缺少結構化協調:

**關機**: 直接殺執行緒會留下寫了一半的檔案和過期的 config.json。需要握手 -- 領導請求, 隊友批准 (收尾退出) 或拒絕 (繼續幹)。

**計畫審批**: 領導說 "重構認證模組", 隊友立刻開幹。高風險變更應該先過審。

兩者結構一樣: 一方發帶唯一 ID 的請求, 另一方引用同一 ID 回應。

## 解決方案

```
Shutdown Protocol            Plan Approval Protocol
==================           ======================

Lead             Teammate    Teammate           Lead
  |                 |           |                 |
  |--shutdown_req-->|           |--plan_req------>|
  | {req_id:"abc"}  |           | {req_id:"xyz"}  |
  |                 |           |                 |
  |<--shutdown_resp-|           |<--plan_resp-----|
  | {req_id:"abc",  |           | {req_id:"xyz",  |
  |  approve:true}  |           |  approve:true}  |

Shared FSM:
  [pending] --approve--> [approved]
  [pending] --reject---> [rejected]

Trackers:
  shutdown_requests = {req_id: {target, status}}
  plan_requests     = {req_id: {from, plan, status}}
```

## 工作原理

1. 領導產生 request_id, 透過收件匣發起關機請求。

```python
shutdown_requests = {}

def handle_shutdown_request(teammate: str) -> str:
    req_id = str(uuid.uuid4())[:8]
    shutdown_requests[req_id] = {"target": teammate, "status": "pending"}
    BUS.send("lead", teammate, "Please shut down gracefully.",
             "shutdown_request", {"request_id": req_id})
    return f"Shutdown request {req_id} sent (status: pending)"
```

2. 隊友收到請求後, 用 approve/reject 回應。

```python
if tool_name == "shutdown_response":
    req_id = args["request_id"]
    approve = args["approve"]
    shutdown_requests[req_id]["status"] = "approved" if approve else "rejected"
    BUS.send(sender, "lead", args.get("reason", ""),
             "shutdown_response",
             {"request_id": req_id, "approve": approve})
```

3. 計畫審批遵循完全相同的模式。隊友提交計畫 (產生 request_id), 領導審查 (引用同一個 request_id)。

```python
plan_requests = {}

def handle_plan_review(request_id, approve, feedback=""):
    req = plan_requests[request_id]
    req["status"] = "approved" if approve else "rejected"
    BUS.send("lead", req["from"], feedback,
             "plan_approval_response",
             {"request_id": request_id, "approve": approve})
```

一個 FSM, 兩種用途。同樣的 `pending -> approved | rejected` 狀態機可以套用到任何請求-回應協議上。

## 相對 s09 的變更

| 組件           | 之前 (s09)       | 之後 (s10)                           |
|----------------|------------------|--------------------------------------|
| Tools          | 9                | 12 (+shutdown_req/resp +plan)        |
| 關機           | 僅自然退出       | 請求-回應握手                        |
| 計畫門控       | 無               | 提交/審查與審批                      |
| 關聯           | 無               | 每個請求一個 request_id              |
| FSM            | 無               | pending -> approved/rejected         |

## 試一試

```sh
cd learn-claude-code
python agents/s10_team_protocols.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Spawn alice as a coder. Then request her shutdown.`
2. `List teammates to see alice's status after shutdown approval`
3. `Spawn bob with a risky refactoring task. Review and reject his plan.`
4. `Spawn charlie, have him submit a plan, then approve it.`
5. 輸入 `/team` 監控狀態
