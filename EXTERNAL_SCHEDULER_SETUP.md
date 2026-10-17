# Crypto 日报外部定时触发

本仓库的日报工作流同时支持三种入口：

- GitHub 原生 `schedule`：北京时间 05:03，作为兜底。
- GitHub `workflow_dispatch`：人工测试入口。
- GitHub `repository_dispatch`：外部定时器正式入口，事件类型为 `crypto_daily_external_trigger`。

外部定时器只负责发出触发请求，日报生成、去重、Word/HTML 发布和飞书推送仍由 `daily_review_cloud.yml` 完成。`cloud_run.py` 会按 Asia/Shanghai 业务日期去重，重复触发不会重复覆盖日报。

## 一次性准备 GitHub Token

在 GitHub 创建 Fine-grained personal access token：

1. Repository access 只选择 `simondongxiao/crypto-macro-daily-monitor`。
2. Repository permissions 只开启 `Contents: Read and write`。
3. Token 只保存到外部定时服务的请求 Header，不要写入仓库、YAML、日志或飞书消息。

## cron-job.org 配置

cron-job.org 支持自定义时区、POST 请求、自定义 Header 和 JSON body。

- URL：`https://api.github.com/repos/simondongxiao/crypto-macro-daily-monitor/dispatches`
- Request method：`POST`
- Timezone：`Asia/Shanghai`
- Schedule：每天 `07:00`
- Header：
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <你的 Fine-grained Token>`
  - `Content-Type: application/json`
- Body：

```json
{
  "event_type": "crypto_daily_external_trigger",
  "client_payload": {
    "source": "cron-job.org",
    "scheduled_for": "07:00 Asia/Shanghai"
  }
}
```

保存后先使用 cron-job.org 的立即执行功能测试一次。GitHub 应出现一个事件为 `repository_dispatch` 的 `Crypto Daily Review (Cloud)` Run；该 Run 完成后才算外部触发链路验收通过。

## 手动测试命令

不要把 Token 写入 PowerShell 历史记录。临时在当前进程中设置后执行：

```powershell
$env:GITHUB_TOKEN = '<你的 Fine-grained Token>'
$body = @{ event_type = 'crypto_daily_external_trigger'; client_payload = @{ source = 'manual-test' } } | ConvertTo-Json -Compress
Invoke-RestMethod `
  -Method Post `
  -Uri 'https://api.github.com/repos/simondongxiao/crypto-macro-daily-monitor/dispatches' `
  -Headers @{ Authorization = "Bearer $env:GITHUB_TOKEN"; Accept = 'application/vnd.github+json' } `
  -ContentType 'application/json' `
  -Body $body
```

成功时 GitHub API 返回 HTTP 204。之后在 Actions 页面检查：

1. 事件类型为 `repository_dispatch`；
2. `Fetch data and build Word review` 成功；
3. Pages 部署成功；
4. `Notify Feishu` 成功；
5. 同一业务日期再次触发时显示去重或跳过，不新增重复日报。

如果外部服务本身延迟，GitHub 原生 05:03 cron 仍可作为第二入口；两个入口共享同一业务日期去重和 Feishu 去重状态。外部服务触发后，GitHub 的事件创建和 Runner 启动仍可能有短暂排队，但不会再依赖 GitHub 的 Scheduled 事件队列。

## 价格监控外部触发

价格监控工作流也支持 `repository_dispatch`，事件类型为 `crypto_price_monitor_external_trigger`。如果 GitHub 原生 5 分钟 schedule 出现漏跑，可在 cron-job.org 建立每 5 分钟一次的 POST 任务：

- URL：`https://api.github.com/repos/simondongxiao/crypto-macro-daily-monitor/dispatches`
- Header：`Accept: application/vnd.github+json`、`Authorization: Bearer <Fine-grained Token>`、`Content-Type: application/json`
- Body：

```json
{
  "event_type": "crypto_price_monitor_external_trigger",
  "client_payload": {"source": "cron-job.org"}
}
```

这不是放宽触发条件：价格监控仍只有在真实价格进入有效区间、报价未过期、独立来源偏差合格时才会发送飞书。外部任务需要用户登录 cron-job.org 后启用，未启用前不能视为已接通。
