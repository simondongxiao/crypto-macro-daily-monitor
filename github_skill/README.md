# GitHub Cloud Version

This bundle is the cloud-compatible deployment of the local `crypto-macro-daily-review` Skill. It keeps the local Skill unchanged and adapts its Word builder and live-data fetcher to repository-relative paths.

## Schedule

`.github/workflows/daily_review_cloud.yml` runs at `23:00 UTC`, which is `07:00 Asia/Shanghai` the following day. It can also be started manually from the Actions tab.

## Required secret

Create the repository secret `FEISHU_WEBHOOK_URL`. The workflow does not store the webhook in source code.

## Outputs

- `reports/crypto_macro_daily_*.docx`
- `config/active_conditions.json`

The generated conditions are consumed by `price_monitor.yml`, which continues to poll prices every ten minutes and sends one alert per side when a zone is entered.

## Cloud limitations

The report labels data gaps explicitly. Public endpoints may be rate-limited or unavailable from GitHub runners; a failed source must not be replaced with invented values. The generated report is a cloud-compatible version of the local builder, not a claim that every premium options, liquidation-heatmap, or wallet-label source is available without credentials.
