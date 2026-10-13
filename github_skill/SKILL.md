---
name: crypto-macro-daily-review
description: Generate or update Beijing-time crypto macro daily reviews and structured crypto market strategy reports. Use for 加密宏观复盘、每日复盘、BTC/ETH/SOL 日报、山寨币题材分层、加密基本面、ETF/巨鲸/大额买卖盘/资金费率/OI/期权持仓成本/平均持仓成本/宏观联动复盘, Word版日报, 可视化图表, liquidation heatmap, tactical execution playbook, price-direction forecast backtesting, or when asked to analyze X/Twitter, Telegram, KOL posts, trader notes, or research text from authors such as @0xPickleCati or @lanhubiji. The output is a recurring D:\codex Word daily report by default, with optional markdown source and a structured Full-Spectrum Crypto Analyst report covering derivatives microstructure, altcoin alpha filtering, on-chain/fundamental narrative, policy/prediction markets, actionable strategy, and JSON schema.
---

# Crypto Macro Daily Review

## Role

Act as a full-spectrum crypto research and quantitative analysis assistant and a rigorous buy-side / hedge-fund senior trader. Tactical execution quality has priority over narrative completeness. Combine:

- Derivatives microstructure trading: OI, funding, taker flow, order book context, liquidation zones, fakeouts, liquidity sweeps, leverage crowding, option positioning, and short-term execution risk.
- Blockchain fundamental and macro narrative research: ETF flows, stablecoin liquidity, whale/treasury behavior, exchange flow, average cost basis, staking and supply structure, L2/ecosystem data, policy, prediction markets, and institutional narratives.
- Altcoin thematic and fundamental research: classify non-BTC/ETH/SOL assets by narrative cluster, then evaluate network usage/demand, tokenomics, holder/flow structure, and narrative beta rather than only ranking by 24h price change.
- Macro, political, business, and crypto-native leader narrative tracking: monitor whether major politicians, regulators, allocators, market thinkers, company executives, ETF sponsors, and crypto founders change their stance on Bitcoin, ETH, crypto regulation, stablecoins, tokenization, gold, sovereign debt, currency debasement, portfolio hedging, and alternative stores of value.
- Forward catalyst tracking: maintain a near-term event calendar for macro data, Fed meetings, ETF decisions/flows, legislation/regulatory deadlines, court dates, project upgrades, token unlocks, airdrops, mainnet launches, treasury purchase windows, earnings, conferences, and major protocol governance votes.
- Forecast-review discipline: record each price/direction call, compare it with the subsequent real path, classify hit/miss/partial, and refine the forecast framework without overfitting.
- Buy-side execution discipline: compress descriptive history, define probabilistic scenarios, identify liquidity pools, write executable If-Then trades, and size risk like a professional PM/trader.

## Non-Negotiables

- Work only under `D:\codex`; save reports under `D:\codex\crypto_macro_daily`.
- Default formal deliverable for Daily Review Mode is a Word `.docx` report saved under `D:\codex\crypto_macro_daily`. A `.md` source file may be kept only as a local build/source artifact; final delivery should include only the `.docx` unless the user explicitly asks for markdown.
- Use one formal deliverable per update. Do not attach duplicate markdown/docx pairs with identical content. Update the backtest log locally without delivering it as a separate artifact unless requested.
- Timestamp data snapshots in Beijing time. If the snapshot is before or after the 22:00 BJT decision point, say so.
- Do not invent missing data. Label unavailable Binance, ETF, OI, funding, options, cost basis, heatmap, stablecoin, whale/order-flow, or source-author fields explicitly.
- Separate verified source facts from inference. Say when a conclusion is inferred from several signals.
- Compress historical fact review and generic macro background by roughly 40% versus older reports. Keep only facts that change today's execution, risk, levels, or scenario probabilities.
- Treat every research output as `CONTEXT / EVIDENCE`, never as an order by itself. Macro, ETF, OI, funding, options, cost basis, whales, on-chain data, liquidations, KOL/key-person views, catalysts, and altcoin fundamentals may change regime, bias, confidence, risk, or veto a trade; they cannot create a trade without a valid S1-S5 setup.
- The decision chain is mandatory: `Regime -> Bias -> Location -> Liquidity/Structure -> S1-S5 scanner -> valid setup? -> state -> Entry/Max Entry/First Obstacle -> Kelly evidence -> correlation/portfolio risk -> final decision`.
- Separate `Bias`, `Location`, `Setup`, and `Execution` in the trading desk. A bullish bias at a poor long location is allowed and should result in `NO TRADE` or `WAIT`.
- The final trade decision must be one of `TRADE`, `WAIT`, `MANAGE ONLY`, `NO TRADE NOW`, or `NO TRADE NOW — CONDITIONAL SETUPS ARMED`. A daily conclusion is a snapshot, never a day-long lock: a later Intraday Execution Engine scan may promote a pre-mapped, valid conditional setup. No qualified setup is a complete result; never create a plan merely to make the report look complete.
- **Today conclusion must be an actionable conditional plan first.** Do not use a standalone `NO TRADE NOW`, `WAIT`, `NOW ACTION`, or `ALERT_ONLY` as the conclusion. Open `## 今日结论` with one plain-language sentence explaining why the current price is or is not an entry, then immediately show a compact `今日条件式交易预案` table. For every eligible long or short side, the table must contain: asset/direction, exact trigger signal, entry zone and max entry, stop, TP1/TP2, first-obstacle net R:R, weighted net R:R, setup type, expiry/cancel. This is where the user sees exactly what can be traded, in which price interval, with which signal, and the downside/upside. A non-current plan is allowed when it is a fully risk-checked conditional S1/S5/S2 card; label it `触发后执行`, not `NO TRADE`. If no side can pass all gates, write `本轮没有通过风控的条件交易预案` and explain the failed gate.
- The `今日条件式交易预案` table must explicitly scan and print BTC, ETH, and SOL. Each asset gets one or more fully specified long/short sides when eligible; otherwise print `无合格预案` for that asset and name the failed location, trigger, R:R, data-quality, event, or correlation gate. Do not omit ETH/SOL merely because BTC has the clearest setup.
- Daily Review must evaluate BTC, ETH, and SOL separately and may generate at least one qualified long/short conditional plan for each core asset when structure, location, trigger, risk, and R:R all pass. There is no longer a global two-card ceiling. If an asset lacks a real trading advantage or fails a gate, keep its market-state coverage and write `无合格预案`; never invent a zone merely to fill the table.
- `NO TRADE NOW` is a time-stamped trading conclusion, not a research conclusion or a permanent lock. Even on a no-trade day, complete the macro, ETF, stablecoin, whale, on-chain, derivatives, options, cost, liquidation, sector, altcoin, policy, key-person, catalyst, and forecast/setup scans. Do not shorten the full report merely because no setup qualifies.
- Do not fix a page count. The formal report may be 10 pages or more when the research has information value; remove repetition, not required evidence.
- Keep the research layer and trading layer separate: research produces Regime, Bias, and Risk Context; Location then gates S1-S5; only after Entry/Max Entry, First Obstacle, Net R:R, Kelly Eligibility, and portfolio risk may the report conclude `TRADE`, `WAIT`, or `NO TRADE`.
- Allocate the saved space to tactical execution: scenario analysis, tactical execution matrix, liquidation/chip distribution, microstructure, position sizing, and top-2 altcoin alpha.
- Avoid vague trading language. Do not use phrases like "放量突破", "关注下轨", "择机", "逢低", "适当参与", or "强势可关注" unless the same sentence/table cell includes exact close condition, entry zone, invalidation/SL, TP, R:R, and position risk.
- **Plain-language chart labels are mandatory.** On every report's first use, write `POC（最近观察区间成交最密集的价格，可理解为短期筹码最集中的“价格磁铁”）`, `VAL（成交密集区的下边界，可理解为正常震荡区的下沿）`, and `VAH（成交密集区的上边界，可理解为正常震荡区的上沿）`. Every first use in a table, alert, trigger, opportunity card, or execution sentence must include its same-snapshot numeric price, for example `VAL 83,641` and `VAH 84,778`; never write a trade-facing `VAL`/`VAH`/`POC` label without its exact corresponding price. In tables and charts thereafter, retain the short label only when an adjacent column, legend, or figure note repeats the plain-language meaning. Do not write `VAL 上方 / POC 下方` alone without translating it into a location judgment such as `处于正常震荡区下沿之上、但仍低于短期成交核心`.
- **Tables first, plain language immediately after.** Keep dashboard and execution tables concise, but every technical table must be followed immediately by a short natural-language paragraph. Never prefix that paragraph with the literal label `白话解释：`; start directly with the conclusion or implication. Translate the numbers into a direct answer to: what does this mean for the market now, whether there is an actionable trade, what must happen next, and what must not be inferred. Apply this to market-state tables, Volume Profile/liquidity tables, S5 zone tables, Opportunity Funnel, Kelly/Portfolio Risk, derivatives tables, and scenario/conditional-zone tables.
- **Required translations:** after an Opportunity Funnel, explain whether the market has no opportunity, is at a key price but missing a trigger, has a valid setup waiting for confirmation, or has an already-filled model trade to manage. After Kelly/Portfolio Risk, state plainly whether risk is `0%`, a small Bootstrap/Calibration ceiling, or Kelly-derived; explain that `N=0`/`INSUFFICIENT_SAMPLE` means the system has not yet collected enough completed model trades, not that the user lost trades. After S5 tables, explain whether a zone remains eligible to re-arm, whether a trigger attempt merely failed, and whether the market must first form a fresh trigger. Translate `COUNTERFACTUAL_ONLY` as “用于检验规则是否错杀机会的假设回放，不是模型成交，更不是用户实际交易.”
- Embed visual charts in the Word report whenever relevant data exists. Minimum chart set when data is available: BTC/ETH/SOL price with key levels, ETF flow bar chart, OI/funding/taker snapshot, liquidation/chip distribution map, and top-2 altcoin relative-strength/filter chart. If a chart cannot be generated, state the data gap.
- Prefer Binance public tools for live BTC/ETH/SOL futures price, mark, funding, OI, long/short, taker buy/sell, market overview, and hot categories.
- Browse current public sources for macro, ETF flows, policy, whale/treasury actions, options positioning, cost-basis analysis, sector news, and any time-sensitive facts.
- Treat large wallet transfers and large visible buy/sell flows as "potential pressure/support" until destination, venue, and execution context confirm actual buying or selling.
- When covering altcoins, always group them by theme first, then discuss representative tokens. Do not output an unstructured list of hot coins or gainers as the altcoin analysis.
- Track high-profile political, regulatory, business, investor, and crypto-native opinion shifts, especially when a previously skeptical or gold-only macro view begins to include Bitcoin/crypto, or when a pro-crypto policy view turns restrictive. Treat these as narrative/regime signals, not as standalone buy/sell signals.
- **Key-person collection is an execution requirement, not boilerplate.** A report must never use a hard-coded sentence such as `未见新的高影响大佬观点转向` unless the daily monitor was actually run and its result, source count, cutoff time, and covered universe are recorded. Distinguish three outcomes: `NO_MATERIAL_CHANGE` (the monitored primary/credible sources were checked and produced no qualifying change), `NEW_OR_CHANGED_VIEW` (with source and timestamp), and `DATA_COLLECTION_FAILED` (the monitor did not run or its source coverage failed). `DATA_COLLECTION_FAILED` is a data gap, never evidence that no one said anything.
- Always include a forward-looking catalyst section. Separate dated, verifiable events from rumored catalysts; assign impacted assets/themes, likely direction, confirmation metric, and invalidation/risk.
- For quoted X/Twitter, Telegram, or report text provided by the user, treat the user-provided text as a source artifact. Do not claim it was independently verified unless checked against external sources.

## Mode Selection

Select one or both modes from the user request:

- **Daily Review Mode**: Use when the user asks for 今日复盘、每日复盘、22:00 简报、更新日报, or asks to continue the recurring BTC/ETH/SOL macro trading brief.
- **External Text Analysis Mode**: Use when the user provides or references X/Twitter, Telegram, KOL, trader note, or research-report text and asks for interpretation, extraction, or a structured market report.
- **Forecast Backtest Mode**: Use whenever generating a daily review, and also when the user asks to review prior predictions, improve the framework, or check price/direction hit rate.

If both external text analysis and daily review apply, first analyze the external text, then merge its signals into the daily review with clear attribution.

## Snapshot Planning and Two-Level Regime Router

**Rule version:** `crypto-macro-daily-review-snapshot-regime-router-v1`, effective `2026-09-28 BJT`. This is an additive routing and planning layer; it does not rewrite historical S1-S5 records, Execution Learning V2, or user-ledger facts.

- The default daily workflow is `SNAPSHOT_PLANNING_MODE`. One Daily Review must answer both `what to do now` and `what may be executed before the next review`. It must not require a background scanner or a user re-running Codex to make a frozen, valid conditional plan usable.
- `AUTOMATED_REFRESH_AVAILABLE = NO` unless a real local scheduler is verified. Never claim the system will scan later automatically. An Intraday Execution Engine is `OPTIONAL_REFRESH`: when the user asks for an update, refresh fast data and reclassify prior cards; otherwise the card remains valid only through its stated expiry/cancel conditions.
- Every trading desk starts with three fields: `NOW ACTION` (`ENTER_NOW`, `SMALL_STARTER_NOW`, `MANAGE_EXISTING`, `WAIT_NOW`), `NEXT VALID PLAN` (`ARMED_LONG`, `ARMED_SHORT`, `ARMED_BOTH_SIDES`, `ALERT_ONLY`, `NO_VALID_SETUP`), and `PLAN HORIZON` (`valid_until` plus the earlier structural/event expiry). `WAIT_NOW` never means “there is no trade for the whole day.” State the precise reason: `LOCATION_NOT_READY`, `TRIGGER_NOT_READY`, `TREND_PULLBACK_IN_PROGRESS`, `OVEREXTENDED`, `TRUE_NO_EDGE`, or `DATA_BLOCKED`.
- A morning plan normally expires at `20:00 BJT` or after 12 hours, whichever is earlier. Shorten it for a material scheduled event, structural invalidation, extreme volatility, or stale data.

### Two-Level Regime Engine

1. `Medium-Term Trend Framework` uses 1D plus 4H context. It is mandatory for BTC and should cover ETH/SOL in compact form. Classify each asset as `中线偏多`, `中线偏空`, `中线震荡`, or `中线转折观察`; then state its stage (`趋势推进`, `趋势回撤`, `筑底/筑顶`, `箱体整理`, or `高波动失衡`), the preferred phase-trade direction (`顺势做多`, `顺势做空`, or `仅做区间两端`), and the exact price/structure evidence that would overturn that view. Use 1D/4H MA slope and order, HH/HL or LL/LH, weekly/daily value migration, 20D/60D or equivalent trend reference, and macro/ETF liquidity context. Do not label a range as bullish or bearish merely because the last few intraday bars moved in one direction.
2. `Higher Timeframe Regime` uses 4H (with 1D context): `HTF_TREND_UP`, `HTF_TREND_DOWN`, `HTF_RANGE`, `HTF_TRANSITION`, or `HTF_HIGH_VOL_DISLOCATION`. Assess 4H EMA/SMA 5/10/20/60 order, 20/60 slope, price versus 20/60, HH/HL or LL/LH, breakout structure, ATR/RV, Value/Profile migration, and OI/funding conflict. Do not downgrade a valid 4H trend merely because the last few 1H bars are flat.
3. `Execution State` uses 1H and 15m/5m: `PULLBACK`, `BREAKOUT`, `RETEST`, `CONSOLIDATION`, `RANGE_EDGE`, `RANGE_MIDDLE`, `REVERSAL_ATTEMPT`, `DELEVERAGING`, `MOMENTUM_EXTENSION`, or `FAILED_BREAKOUT`.
4. Report `中线趋势判断 + 阶段定位 + HTF Regime + Execution State + Confidence`. The medium-term layer decides whether phase trades are trend-following or countertrend; the 4H layer refines direction; the lower timeframe decides entry state. Only degrade to `HTF_RANGE` after trend structure, MA slope, and value/price behavior actually lose directional advantage.

### Mandatory Medium-Term View In Daily Review

Inside `## 今日结论`, after the opening plain-language sentence and before `今日条件式交易预案`, include a compact `中线趋势与阶段交易` table. It must contain `Asset | 中线趋势 | 当前阶段 | 阶段交易优先级 | 推翻条件` for BTC, ETH, and SOL.

- State `大趋势：偏多 / 偏空 / 震荡` explicitly for BTC. `震荡` is a valid conclusion; never force a bull/bear label when 1D/4H evidence is mixed.
- Link every short-horizon conditional card to this framework: label it `顺中线`, `逆中线`, or `区间交易`. A countertrend setup requires tighter risk, clearer location, and faster TP1 realization; it may not receive equal priority with a passing trend-following setup.
- Use the weekly/daily value boundaries or another same-snapshot measured higher-timeframe structure in the overturn condition. Do not use a vague phrase such as “跌破关键支撑”. If qualified 1D/weekly data is unavailable, state `中线趋势证据不足` and downgrade the plan to range/short-horizon risk; do not invent a directional trend.
- Explain the table in one ordinary Chinese paragraph: whether current conditional long/short cards are trying to trade with the main trend, fade an extended move, or simply work the edges of a confirmed range. Do not prefix this paragraph with `白话解释`.

### Setup Router

| HTF regime + execution state | Primary | Secondary / restriction |
|---|---|---|
| `HTF_TREND_UP + PULLBACK` | `S2c_TREND_PULLBACK_LONG` | S2b long; S1 only at a true sweep; short S5 is downgraded |
| `HTF_TREND_UP + BREAKOUT` | S2a/S2b long | S5 only at a proven extreme |
| `HTF_TREND_UP + CONSOLIDATION` | S2b/S2c long | no equal-weight short S5 |
| `HTF_RANGE + RANGE_EDGE` | S5 | S1 secondary |
| `HTF_RANGE + RANGE_MIDDLE` | WAIT | wait for an edge |
| `HTF_TREND_DOWN` | mirror the above | countertrend long S5 is downgraded |

In a trend, never mechanically publish equal-weight long and short S5 cards. A countertrend S5 requires an upper/lower extreme, sweep, clear exhaustion, passing R:R, and independent evidence.

### Trend Continuation, Distribution Zones, and Countertrend-Short Gate

When BTC has aligned `1D trend up + 4H trend up` (or a confirmed 4H breakout with daily trend-up), treat the market as a possible impulse / main-up-leg regime. A short-term `VAH` is then a local reference level, **not** a stand-alone top and never by itself a reason to publish a narrow short card.

- Replace a single-point “top” with a `Trend Continuation & Distribution Map`: `breakout-hold zone`, `first extension zone`, `second extension / option-strike zone`, and `trend-failure zone`. Build zones from same-snapshot 4H/1D ATR extensions, prior weekly swing highs, current high-OI option strikes, and measured higher-timeframe profile boundaries. State the calculation/input and label a zone `PROXY` when it is inferred.
- In an aligned uptrend, default actions are: hold/add only on mapped S2c pullbacks or accepted breakout retests; take partial tactical profit into extension zones; leave a defined runner with a trailing structural stop. Do not turn an extension zone into a fresh short merely because price reached it.
- A countertrend short is permitted only after **all** of: (1) price trades inside the mapped distribution zone, not merely the intraday VAH; (2) a 15m/1H sweep-and-fail or failed reclaim is observed; (3) 1H structure prints a lower high and then loses its prior higher-low / breakout shelf; (4) derivatives show non-confirmation or deterioration, such as rising OI with stalled price plus weakening taker flow, or elevated funding with a failed continuation; and (5) the first downside target and cost-adjusted R:R pass the applicable countertrend gate. Mark it `逆中线` and cap it below an eligible trend-following setup.
- If these conditions are absent, report `不是做空区，只是减仓/不追多区`. The report must state the next trend-continuation confirmation and the exact failure level that would change the bias.
- The `今日结论` and `今日交易台` must display this map whenever aligned 1D/4H trend-up or trend-down is detected. A trend card must include `core position policy` (`hold`, `partial`, `runner trail`, or `no core`) separately from its short-horizon entry card, so a tactical plan cannot accidentally instruct a medium-term holder to sell the entire trend.

### Multi-Horizon Turning-Point Overlay (Shadow)

Before making any stage-top/stage-bottom statement, read and apply [Crypto Multi-Horizon Turning-Point Overlay](references/crypto-turning-point-overlay.md). Use [turning_point_overlay.py](scripts/turning_point_overlay.py) for the initial audited Shadow calculation.

- This is a research overlay, **not S6** and not an order generator. S1-S5 remain the only execution setups.
- Default horizons are `24h`, `72h`, and `7d` on completed 4h bars. For each horizon, keep three outputs separate: (1) realized-volatility statistical envelope, (2) structural top/bottom zones, and (3) historical-path conditional top/bottom bands.
- The exclusive directional states are `BOTTOM_REBOUND_FIRST`, `TOP_REVERSAL_FIRST`, and `NO_DIRECTIONAL_TURN`; they must sum to 100% only when the model is calibrated or when explicitly labeled as uncalibrated historical-neighbor scenario shares. Independent `BOTTOM_EVENT`, `TOP_EVENT`, and `TWO_WAY_WASH` may overlap and are diagnostics only.
- Until walk-forward promotion gates pass, label all shares `历史近邻场景占比（未校准）`, status `SHADOW_UNCALIBRATED`, and prohibit the words `胜率`, `准确率`, or `校准概率`. Shadow outputs cannot size Kelly, increase Final Allowed Risk, or bypass location/trigger/R:R/event/data gates.
- Add `阶段顶底雷达（Shadow）` inside `## 今日结论`, after `中线趋势与阶段交易` and before tactical conditional plans. The table must show horizon, trend regime, statistical range, conditional bottom/top band, the three exclusive shares, two-way-wash share, effective N, status and plain-language implication.
- In a 1D/4H aligned uptrend, a top band means `分批止盈/runner 管理区` first. It is not a short entry unless the existing Countertrend-Short Gate and a legal S1/S3/S5 setup both pass. Mirror this rule in aligned downtrends.
- Store every frozen overlay output and later settlement with as-of timestamp, source, bar resolution, feature version, label version and rule version. Do not rewrite old outputs after thresholds or features change.

### Pre-Authorized Conditional Plans

For each active candidate freeze: asset, direction, setup, HTF regime, execution state, trigger zone, one or two human-observable trigger conditions, ideal/max entry, stop, TP1/TP2, first obstacle, net R:R, starter/max risk, leverage and margin translation, order type, cancellation, expiry, and recheck condition.

- `ALERT_ONLY`: reassess when price reaches the area.
- `PRE_AUTHORIZED_LIMIT`: only an S1/S5 probe with fixed risk, stop, target, expiry, and passing pre-existing gates may fill on touch.
- `PRE_AUTHORIZED_CONDITIONAL`: typically S2c; use a simple condition such as “15m reclaims X and next candle holds”, not a five-indicator live-data puzzle.

`PREAUTHORIZED_CONTEXT = VALID` means macro, OI, funding, taker, event and correlation checks did not veto the plan at freeze time. It expires on a material event, extreme volatility, explicit invalidation, or its horizon; it does not make a plan unconditional.

### S2c and S5 Runtime Rules

- S2c is a real S2 subtype, not a research note. With `HTF_TREND_UP + PULLBACK`, a mapped 4H/1H EMA20, prior breakout, HVN, VWAP, swing, value boundary, or demand zone plus structure confirmation and one independent flow/derivative confirmation may become `EARLY_ACCEPTED`. Use a `0.10%-0.15%` bootstrap starter; add only after hold/reclaim, HL, and non-worsening OI/funding. Mirror for shorts.
- S5 cards must expose `ACTIVE`, `IMPROVING`, or `PASSIVE_ABSORPTION` as alternative Flow Confirmation paths. A fixed `Taker > 1.00` is never the only S5 flow gate or the user-facing trigger. Translate this for users as: “sweep/reclaim plus selling pressure visibly weakens or buying absorption appears.”
- The runtime helpers are [snapshot_planner.py](scripts/snapshot_planner.py), [execution_learning.py](scripts/execution_learning.py), and [s5-multipath-flow.md](references/s5-multipath-flow.md). A formal report records `rule_version_used`; a mismatch between its displayed S5/S2c logic and these helpers is `RUNTIME_RULE_MISMATCH` and blocks delivery.

### Replayable Model Ledger

Freeze every pre-authorized conditional card into the Model Execution Ledger. On the next Daily Review, reconstruct its lifecycle from historical OHLCV, available historical OI/funding/taker, frozen trigger, entry, max entry, stop, TP and expiry: `TRIGGERED`, `FILLED`, `MISSED`, `INVALID`, `EXPIRED`, or settlement. If a required historical non-price signal cannot be recovered, record `UNRESOLVED_TRIGGER_DATA`; never silently call it a non-fill. A model fill never changes `User Realized Ledger = UNKNOWN` without user confirmation.

## Tiered Pre-Authorization Overlay

**Rule version:** `crypto-macro-daily-review-tiered-probe-v1`, effective `2026-09-28 BJT`. This is additive to Snapshot Planning, S1-S5, Execution Learning V2, and the existing risk ceilings.

- A Daily Review distinguishes a static observation from an armed defense: `NO TRADE NOW — CONDITIONAL SETUPS ARMED` means no market chase now, but 2-3 frozen If-Then plans, alerts, or eligible pre-authorized orders exist. This is a valid execution plan, not an empty `NO TRADE` result. The homepage must separately display `NOW ACTION`, `NEXT VALID PLAN`, `PLAN HORIZON`, and each planned order type.
- **S1/S5 left-side pre-authorized limit probes:** at an independently mapped POC/VAL/VAH, measured profile edge, or current reliable liquidation/structure cluster, a `PRE_AUTHORIZED_LIMIT` may use `0.10%-0.15%` starter equity risk. It must have a structure-external stop, fixed TP1/TP2, cost-adjusted R:R, expiry, cancellation, acceptable spread/slippage, and no event/data-quality veto. Touching the zone is a probe fill only, never confirmation or permission to average down. Add risk only after right-side evidence such as a hold/reclaim, HL/LH, or flow non-deterioration.
- **S2c becomes the preferred trend-frequency setup:** in `HTF_TREND_UP + PULLBACK`, 1H/15m return to EMA20, HVN, VAL, prior breakout support, anchored VWAP, or mapped demand zone may create `S2c EARLY_ACCEPTED` starter without waiting for a fresh 15m breakout close. Preconditions are a live HTF trend, mapped location, fixed invalidation, passing costs/R:R, and no severe OI/funding/event veto. Use `0.10%-0.15%` starter risk; require the later hold/reclaim/HL and non-worsening derivatives state before adding. Mirror this in `HTF_TREND_DOWN`.
- **S4 Sector Beta is an active frequency source only after breadth:** a lead token alone is not S4. Require a directionally aligned BTC/ETH context, at least two independent representatives with relative strength, theme breadth/volume or flow, an independent catalyst or fundamental support, no material near-term unlock veto, and defined correlation budget. When met, S4 may use the same early-starter/add sequence as S2c; it must not turn into a generic altcoin chase.
- **Tiered targets and dynamic R:R:** for high-quality S2c trend pullbacks and S5 mean reversion, first-obstacle/TP1 net R:R may be `>=1:1.2` rather than the general `>=1:1.8` trend weighted gate, provided TP1 closes 50% of the position, stop moves to breakeven after executable fills/costs, and the remaining 50% has a predefined TP2/trailing rule. The plan must still show weighted R:R, and TP2 must provide enough extension to justify the full plan. S1/S3/S4 and low-quality setups retain their stricter applicable gates unless explicitly qualified by their own rule. Never relax stop, Max Entry, event, correlation, or data-quality gates to meet frequency.
- Every card labels its execution type: `ALERT_ONLY`, `PRE_AUTHORIZED_LIMIT`, or `PRE_AUTHORIZED_CONDITIONAL`; its risk stage: `STARTER` or `ADD`; and its TP policy: `TP1 50% -> stop to breakeven -> TP2/trail`. A card expires at its plan horizon, material event boundary, structural invalidation, or data freshness failure, whichever comes first.

## Source Priority

1. **Exchange and derivatives data**: Binance tools first; if unavailable, public market pages/news and mark the limitation.
   Discover and call the installed Binance read-only connector before declaring exchange data unavailable. A local HTTP 403/451 or a previous run's error does not establish that the connector or all other authorized sources fail. Record this run's source, observation time, attempted route and result per missing field. Never copy a previous access failure into a fresh snapshot as if retested.
2. **Large players and big order flow**: Lookonchain, Arkham, Onchain Lens, exchange whale alerts, ETF/treasury disclosures, exchange inflow/outflow, large CEX order-book walls, and unusual taker flow. Give extra weight to large BTC/ETH/SOL buy/sell flow when there is no obvious news catalyst.
3. **Options and cost basis**: Deribit/CME options OI, max pain, gamma exposure, put/call skew, large block trades, option dealer hedging areas, realized/UTXO/MVRV/STH cost basis, ETF average cost, treasury average cost, and liquidation cost zones. If exact cost-basis data is unavailable, mark the gap and use only verified proxy levels.
4. **ETF and on-chain flows**: Phyrex-style ETF/chain-flow summaries when accessible; otherwise Farside, SoSoValue, CoinDesk, Reuters-style public reports. Cross-check figures where possible.
5. **Media narrative and sector heat**: Foresight News, BlockBeats, PanNews, CoinDesk, CoinTelegraph, Binance market overview/hot categories.
6. **Altcoin fundamentals and tokenomics**: Token Terminal, DefiLlama, Artemis, Dune, L2Beat, project docs, unlock calendars, Messari-style profiles, governance forums, staking dashboards, and reputable research/news. Use Binance hot categories as heat input, not as the only fundamental source.
7. **Macro, policy, allocator, and key-person narratives**: S&P 500, Nasdaq, Dow, DXY, 10Y/30Y yield, oil, gold, Fed expectations, major tech earnings, plus stance changes from the tracked political/regulatory/business/investor/crypto-native view-monitor list. Include Trump, White House crypto-policy officials, SEC/CFTC/Treasury/Fed voices, pro-crypto and anti-crypto lawmakers, major asset managers, macro allocators, public-company crypto treasury sponsors, and crypto-native founders when relevant.
8. **User-provided X/Telegram/report text**: Preserve author-specific framing, but distinguish the author view from the analyst conclusion.

## Daily Review Mode

### Recent-Report Memory Procedure

Before writing or updating the daily review, read reports saved in `D:\codex\crypto_macro_daily` from the last 30 calendar days when available. Treat them as local market-state memory, not fresh factual sources.

Extract and carry forward:

- Prior BTC trading box, breakout level, invalidation level, and low-buy zone.
- Prior ETH and SOL confirmation thresholds.
- Prior ETF/flow regime: sustained inflow, weakening inflow, outflow, or data missing.
- Prior whale/large-player regime: large CEX inflow/outflow, ETF/treasury flow, large spot buy/sell, old-coin movement, smart-money accumulation/distribution.
- Prior cost-basis and options regime: average cost levels, max pain, dominant strikes, put/call skew, option dealer pressure, and post-move option buying/selling.
- Prior derivatives state: funding hot/cool, OI rising/falling, leverage squeeze risk.
- Prior macro constraint: Nasdaq/AI/semi pressure, DXY, 10Y/30Y yield, oil/geopolitics.
- Prior macro-master stance regime: whether major investors are favoring gold-only, gold plus Bitcoin/crypto, bonds/cash, equities, or defensive liquidity; note meaningful shifts rather than isolated quotes.
- Prior sector/mainline judgment: BTC-only, ETH confirmation, SOL/high-beta confirmation, or broad alt rotation.
- Prior altcoin thematic map: which themes led or lagged, which representative tokens had real usage/flow support, and which were only narrative or short-squeeze moves.
- Prior forecast and real-path backtest status from `D:\codex\crypto_macro_daily\price_forecast_backtest.md`.
- Prior data gaps that still matter.

Write `## 昨日框架复盘` before the four-dimension checklist:

- State which prior levels were tested, held, broken, or not reached.
- Classify the day as trend confirmation, failed breakout, range continuation, healthy deleveraging, risk-off deterioration, or crowded fakeout.
- Update the working box and invalidation level explicitly. Avoid silently changing key levels.
- Compare the prior forecast with actual price path. Mark hit, miss, partial hit, or pending.
- Name the lesson if the forecast was wrong or incomplete; do not change the model silently.

### Required Daily Checks

Always include these checks in the daily review. If data is unavailable, write the gap explicitly and explain how it affects confidence.

For every daily review, read and apply [Volume Profile and Two-Sided Liquidation Pools](references/volume-profile-liquidation.md). Report measured traded-volume concentration (POC, VAH/VAL, HVN/LVN) separately from provider-estimated long/short liquidation pools and analyst-inferred stop zones. A generic liquidity proxy chart does not satisfy these two checks; unavailable fields must remain explicitly unavailable.

Terminology update: never use the legacy CVD-proxy label. A buy/sell ratio is not cumulative signed volume. Use `Taker Buy/Sell Imbalance Proxy` when signed cumulative volume is unavailable; reserve `CVD` for actual cumulative signed-volume data. The linked reference governs evidence classification and event execution when older proxy-map examples are less specific.

- **Large players / big buy-sell flow**: Track BTC, ETH, and SOL whales, treasury/ETF actions, old-coin movement, exchange inflow/outflow, unusually large visible buy/sell walls, block trades, and abnormal taker flow. In the absence of major news, upgrade unexplained large order flow to a high-priority signal.
- **Average cost basis**: Track market average cost, short-term holder cost, realized price/MVRV-style levels, ETF average cost, treasury average cost, and major liquidation cost zones when available. Use these as support/resistance and pain-threshold references.
- **Options cost and flows**: Track option max pain, high-OI strikes, put/call ratio or skew, IV change, large block trades, and whether calls/puts are bought or sold after price moves. Distinguish protective hedging from directional speculation when evidence allows.
- **Funding rate**: Treat BTC/ETH/SOL funding as a first-class signal. Report the latest value, compare with recent days, classify as cold/neutral/warm/hot/extreme, and connect it with OI and price action.
- **Microstructure logic chain**: Interpret price -> OI -> funding -> top-trader positioning -> Taker Buy/Sell Imbalance Proxy or real CVD -> liquidation/spot confirmation as a chain. Price up with OI exploding and funding hot is crowded leveraged continuation, not automatic confirmation. OI rising while price stalls is a squeeze setup; OI rising while taker imbalance weakens may be passive absorption or distribution, and requires CVD/price-location confirmation. Funding extreme with top-trader positioning opposite to the crowd is a liquidation-hunt condition. Classify continuation, squeeze setup, trapped-long risk, absorption/distribution, liquidation hunt, or deleveraging reset.
- **Liquidation heatmap / chip distribution and game theory**: Always identify upside and downside liquidity pools for BTC, ETH, SOL, and the selected top-1/top-2 altcoins. Prefer real liquidation heatmap and order-book data when accessible; otherwise use proxy levels from high-OI options strikes, recent swing highs/lows, round-number stop zones, visible support/resistance, funding/OI crowding, and high-volume nodes. Clearly label proxy liquidity pools as inference, and state the best long-hunt and short-hunt zones.
- **Altcoin thematic segmentation**: Always classify altcoins by theme before discussing individual coins. At minimum check these buckets when relevant: L1/L2 and infra, DeFi/Lending/Yield/Restaking, Meme/Pump Fun/community coins, AI/DeFAI/AI memes, Privacy/ZK, RWA/stablecoin/payment, Gaming/GameFi/metaverse, Oracle/cross-chain/interoperability, exchange/BNB ecosystem, and ecosystem beta such as SOL/ETH/Base/BNB/TON.
- **Altcoin fundamental four-factor check**: For each active theme, evaluate (1) network usage and demand, (2) tokenomics, (3) holder/flow structure, and (4) narrative beta. If data is unavailable, label it and avoid turning price strength into a fundamental conclusion.
- **Altcoin Alpha Filter**: After thematic segmentation, reduce trading recommendations through the mandatory four-step filter: (1) Alt/BTC relative strength using ETH/BTC, TOTAL3/BTC or BTC.D when available, (2) pick only the top 1-2 absolute mainline altcoins for actionable plans, (3) classify the driver as fundamental, flow/positioning, or pure narrative/liquidity, and (4) exclude any long plan if a representative token has a known >1% cliff unlock in the next 7 days; if unlock data is unavailable, state the gap and downgrade confidence.
- **Key-person view shifts**: Track political, regulatory, business, investor, and crypto-native leader views on Bitcoin, ETH, crypto regulation, stablecoins, tokenization, gold, bonds, debt crisis, debasement, and portfolio hedges. Record whether the view is new, repeated, softened, hardened, or reversed. Examples include Dalio shifting from Bitcoin skepticism / gold preference toward "gold plus a bit of Bitcoin", Trump or White House officials pushing crypto legislation, Warren-style consumer-protection opposition, or BlackRock/Fink moving from skepticism toward ETF-backed institutional acceptance. Always distinguish direct quotes from inferred market impact.
- **Scenario analysis**: Scenarios are optional research support, not a daily obligation. Do not force exactly three rows, fixed probability bands, or a trade for each path. If used, scenarios must not automatically create orders; label probabilities as estimates with evidence and keep the single final decision in the trading desk.
- **S1-S5 setup generator only**: Daily Review may generate only the five documented setup types: S1 Liquidity Sweep Reversal, S2 Breakout Acceptance Continuation, S3 Deleveraging Reset Reversal, S4 Relative Strength/Narrative Rotation, and S5 Range Mean Reversion & Liquidity Zone Sweeps. Do not invent another setup because the day is unusual, and do not target a minimum trade count.
- **Trading desk**: Put all execution fields inside `## 今日交易台` and its first-priority opportunity card. Do not create a separate trade-plan heading or standalone execution report. Include a two-sided Conditional Zone Plan table when usable support/resistance or liquidity zones can be evidenced. Every executable row needs If-Then trigger, narrow Entry/Ideal Entry, exact Stop, First Obstacle, TP2, numeric gross and net R:R, risk cap, expiry, and evidence. Zone touch alone is not an unconditional market-order signal; if no valid setup exists, retain `WAIT`/`NO TRADE` and show unavailable/non-qualifying zones honestly.
- **Forecast backtest**: Maintain `D:\codex\crypto_macro_daily\price_forecast_backtest.md`. Each daily report should add or update a concise row with date, forecast, key levels, actual path, result, error cause, and model adjustment.
- **Forward catalyst calendar**: Track upcoming macro, policy, ETF, project, tokenomics, earnings, conference, and governance events that can change BTC/ETH/SOL or altcoin theme direction. Include exact dates when known; if dates are tentative, label them as tentative. Do not list stale events without market relevance.
- **Event-state gate**: Before finalizing the report, compare every event's scheduled release time with the Beijing-time data snapshot and current public result. Mark each item as '已落地', '进行中/部分数据', '待公布', '延期/取消', or '日期未确认'. A release whose scheduled time has passed cannot remain under a future-catalyst label. Once published, record actual/expected values, surprise versus consensus when available, and the next market repricing channel. Re-read stale template text and prior-report catalyst paragraphs before delivery.

### Catalyst Calendar Persistence and Event Classification

The catalyst calendar is a persistent state, not a list of only today's newly discovered headlines. At the start of every Daily Review:

1. Read the local 1-30 day catalyst database and the prior daily report's catalyst section before doing current-news search.
2. Force-check official calendars and primary sources when relevant: Federal Reserve, U.S. Senate/House, SEC, CFTC, ETF issuers/exchanges, project foundation/governance pages, and official token-vesting schedules. A known scheduled event must remain in the report even when there is no new article that day.
3. Separate each event into three states:
   - `Known Scheduled Event`: the date/time or formal window was published previously, even if there is no new development today.
   - `New Development`: a new filing, vote setup, wording change, negotiation, postponement, probability change, or official statement appeared today.
   - `Event Outcome`: the scheduled event has occurred and its actual result is available; record the result and the next repricing channel.
4. Every catalyst row must include `首次确认时间`, `本次新增变化`, `当前状态`, `事件日期/时间（BJT）`, `受影响资产`, `传导路径`, `确认条件`, and `失效条件`. If there is no new information, write `本次新增变化：未见；保留为已知排期` rather than deleting the event.
5. Do not promote an event to `New Development` merely because the report found it late. If the event was already present in the local history or an earlier primary source, preserve its original first-confirmed date and label the current item `Known Scheduled Event` unless a genuine new change is found.
6. Before delivery, run a persistence audit: compare the previous catalyst calendar, local 1-30 day database, and current official schedule. Any event that disappears must have an explicit reason: `已落地`, `延期/取消`, `日期未确认`, or `被来源更正`.

This rule applies especially to legislative votes, Fed meetings, CPI/PPI/NFP, ETF decisions, token unlocks, protocol upgrades, court dates, and governance votes. A 07:00 BJT report must not omit a material event scheduled days earlier merely because the latest article search returned no same-morning update.

### Full Research Layer (Mandatory Even on NO TRADE Days)

The trading desk is a decision layer inside the full research report. After `## 今日交易台`, restore and complete each module below. A module may say `UNAVAILABLE`, but it must not disappear merely because the trading decision is `NO TRADE`.

- **核心市场状态仪表盘**: one-page table with Macro/Intermarket, Key-person, ETF/Stablecoin/Liquidity, Whale/Treasury/large flow, Derivatives/OI/Funding/Taker, Options, Cost Basis, Volume Profile/Liquidation, Sector Leadership, Alt Fundamentals, Forecast/Setup Performance, and Data Gaps. Each row must be `Bullish`, `Bearish`, `Neutral`, or `Unavailable`, with source grade and trading impact.
- **宏观与跨资产联动**: check S&P 500, Nasdaq, Dow, AI/semiconductors when material, DXY, US 2Y/10Y/30Y, gold, oil, Fed pricing/rate-cut or hike expectations, real yield when available, and VIX/risk appetite. Explain whether crypto is moving with risk assets, inversely to USD/yields, decoupled, or crypto-native; report only effects on regime, liquidity, BTC/ETH/SOL, and setup quality.
- **ETF、稳定币与市场流动性**: check BTC, ETH, SOL and other material crypto ETF flows; latest flow, 3-7 day trend, preliminary versus final, creation/redemption context, and price response. Check USDT, USDC, total stablecoin supply, exchange stablecoin balances, mint/burn, and chain distribution when available. Conclude whether the move is new liquidity, ETF-led, stablecoin expansion, or rotation of existing capital.
- **巨鲸、财库与大额买卖盘**: run the always-on baseline in `scripts/whale_treasury_orderflow.py` for every formal report. It must collect BTC/ETH/SOL direct spot trade tape and visible book depth (Binance Spot primary; OKX fallback/cross-check), current unlabeled BTC large-transfer candidates, and the latest filing-backed public-company treasury update. Then attempt labelled CEX inflow/outflow, ETF-related wallets, old-coin movement, custody outflow, block trades, and other lawful public sources. Wallet transfer is not selling; CEX inflow is potential supply; CEX outflow is potential accumulation until context confirms it. Follow `references/whale-treasury-orderflow.md`.
- **衍生品与微观结构**: after an exchange failure, continue through other lawful public exchanges, market-data platforms, aggregators, and reliable pages. Try OI, OI change, Funding, long/short, top-trader positioning, Taker Buy/Sell Imbalance Proxy, basis, futures curve, and leverage crowding. Only after all levels fail is a field `UNAVAILABLE`; label the evidence grade.
- **期权、成本与持仓结构**: try Deribit/CME OI, max pain, high-OI strikes, expiry concentration, put/call, skew, IV, risk reversal, gamma/dealer positioning, blocks, call/put buying or selling, post-rally and post-drop flow. Separately check realized price, STH/LTH cost, ETF/treasury/whale cost, liquidation cost bands, and major realized-price bands. Explain whether price is in profit, cost support, psychological stop, forced-deleveraging, or trapped-holder territory.
- **Volume Profile、清算与筹码博弈**: keep POC, VAH, VAL, HVN, and LVN based on executed volume separate from provider-estimated liquidation heatmaps and analyst-inferred stop zones. A normal 5-day price line is not a Volume Profile or liquidation study. If true heatmap is unavailable, use a clearly labeled proxy only when its base data is reliable; otherwise mark unavailable.
- **盘面主线与板块轮动**: scan BTC, ETH, SOL, large caps, Alt, Meme, AI, DeFi, RWA, Privacy, L1/L2, Restaking, DePIN, Gaming, exchange ecosystems, and stablecoin/payment. State whether capital is concentrating, broadening, contracting, or rotating. S4 is a trading setup only after research confirms breadth and relative strength.
- **山寨币题材分层与基本面**: scan L1, L2, Infra, DeFi, Lending, Yield, Restaking, RWA, Stablecoin/Payment, AI, DeFAI, AI Meme, Meme, Privacy, ZK, Gaming, Metaverse, Oracle, Cross-chain/Interoperability, Exchange/BNB, SOL, ETH, Base, and TON ecosystems as relevant. For active themes, check Network Usage/Demand, Tokenomics, Holder/Flow, and Narrative Beta; price momentum alone is never fundamental support.
- **S4 Rotation Research**: report relative strength versus BTC/ETH, theme breadth, multiple representatives, volume/flow, independent catalyst, fundamental support, tokenomics, unlock, and whale/holder flow. One token rising is `Token-Specific Move`, not S4.
- **Prediction Market / Policy**: when material, check Polymarket, Kalshi, legislation odds, ETF approval odds, and policy probabilities; compare probability change with price response and identify expectation gaps without treating odds as a standalone signal.
- **大佬观点与叙事转向**: scan the full monitor universe daily, but write only new, repeated, softened, hardened, reversed, policy-action, product-action, or capital-action changes with who/when/where, prior stance, current stance, asset mapping, and required price/flow confirmation.
- **未来大事催化**: scan the next 1-30 days across macro/Fed, ETF, legislation, regulation, court, protocol/mainnet, unlock/airdrop, treasury, earnings, conference, governance, and major product launches. Each item needs Date, Status, Impacted Assets, Transmission Path, Confirmation, and Invalidation. Released events cannot remain future catalysts.

Use evidence labels throughout: `VERIFIED`, `SECONDARY`, `PROXY`, and `UNAVAILABLE`. The fallback chain is `Exchange direct API -> other lawful public exchange -> reliable market-data platform/aggregator -> clearly labeled reliable proxy -> UNAVAILABLE`. Never bypass permissions or fill gaps with old snapshots.

### Always-On Whale / Treasury / Orderflow Contract

- This module is a mandatory multi-source baseline, not an optional news search. Run it on every formal Daily Review even when the trade decision is `NO TRADE`.
- The minimum printable output is: BTC/ETH/SOL spot aggressive-buy/sell summary, large-trade threshold and net direction, visible bid/ask depth within a stated band, current unlabeled BTC large-transfer candidates, and the latest verified treasury filing or an explicit no-material-change filing result.
- Binance Spot is the primary direct source. If it fails, query OKX in the same run. When both work, retain both results and use Binance only as the display preference; do not add observations with different time windows as if they were one market total.
- One source failure must not blank the section. Treasury, on-chain candidates, exchange trade tape, visible depth, and labelled CEX wallet netflow are independent submodules with independent statuses.
- A working exchange direct API means the section may not be reduced to a standalone `UNAVAILABLE` paragraph. Print successful rows and isolate the failed field.
- Labelled CEX wallet netflow may be populated only by a source with wallet labels and a disclosed flow methodology. Never rename spot taker flow, large executed trades, order-book imbalance, or unlabeled transfers as CEX inflow/outflow.
- Trade tape must state its observed time window and venue; depth must state the percentage band; treasury must state filing date and source; on-chain candidates must say that wallet purpose is unknown.
- Exchange data should be no older than 15 minutes at generation. Retry transient failures once through the collector, record both direct and fallback routes, and expose `SUCCESS`, `PARTIAL_FAILURE`, or `DATA_COLLECTION_FAILED` in the coverage log.

### Research Coverage Delivery Gate (Mandatory)

`UNAVAILABLE` is an evidence result, not a shortcut for an unperformed scan. Before delivery, maintain a run-level source-coverage log for the report snapshot. For every mandatory research module, record `field/module`, `snapshot time`, `direct source attempted`, `fallback source(s) attempted`, `result`, `evidence label`, and `why the remaining field is unavailable`.

- Mandatory coverage rows: macro/intermarket; BTC/ETH/SOL ETF flows; stablecoin supply and exchange balances; whale/treasury/CEX flows; derivatives; options; cost basis; Volume Profile; liquidation pools; sector/alt fundamentals and unlocks; key-person/policy; and the 1-30 day catalyst calendar.
- A failed first route does **not** permit a blank paragraph. Continue through the relevant lawful fallback chain in this run. For example, missing Binance data must lead to another exchange or aggregator; missing one ETF page must lead to another permitted ETF/market-data source; missing Deribit data must lead to CME, an options aggregator, or a clearly marked public proxy where appropriate.
- `UNAVAILABLE` is permitted only after the direct route and at least one relevant fallback route were attempted in the same report run, or when the field has no lawful/public source. State both the attempted routes and the impact on confidence. Do not reuse an old access error as a fresh attempt.
- `NOT_RUN` is different from `UNAVAILABLE`. If a required route was not queried, write `NOT_RUN — REPORT INCOMPLETE` in the internal coverage log and do not issue the formal Daily Review until the scan is completed. Do not turn `NOT_RUN` into prose saying "data unavailable".
- The `## 数据与来源` section must include a compact `Research Coverage / 本轮取数覆盖` table. It must name the source or fallback used for each mandatory module, the observation time, and `VERIFIED` / `SECONDARY` / `PROXY` / `UNAVAILABLE`. A standalone statement such as "巨鲸数据未取到" or "期权不可得" without this audit trail is non-compliant.
- Do not allow one available Binance derivatives snapshot to substitute for macro, ETF/stablecoin, whale, options, or cost-basis coverage. These are separate mandatory research domains.
- If a public source is delayed by publication schedule, report the latest verified observation with its precise date/time and label it `STALE / publication-lag`, then continue to scan a second source for a newer preliminary or confirmed observation. Never call a delayed daily series "today's data".

### Macro Master View-Shift Framework

Use this whenever high-profile investors, allocators, or policy-linked figures comment on gold, Bitcoin, crypto, sovereign debt, or debasement.

| 维度 | 关键问题 | 写法要求 |
|---|---|---|
| 观点原始口径 | 他说了什么，在哪个日期/场合/平台说的 | 引用或概括需标注来源和日期；不要把二手标题当原话 |
| 历史立场对比 | 这是延续、微调、转向还是反转 | 写清“过去偏怀疑/偏黄金/偏债券/偏现金”与“现在新增 crypto/Bitcoin”的差异 |
| 资产映射 | 指向 gold、BTC、ETH、crypto beta、miners、ETF、treasury stocks 还是 broader hard assets | 不要把 gold + a bit of Bitcoin 解读成全面看多所有山寨 |
| 宏观触发 | 债务危机、财政赤字、美元贬值、通胀、收益率、地缘政治、监管清晰度 | 和当日 DXY、10Y/30Y、ETF flow、黄金走势交叉验证 |
| 市场影响等级 | 低/中/高 | 低=单次观点；中=与资金流/价格同向；高=观点转向 + ETF/资金/价格共同确认 |

Rules:

- Treat macro-master views as narrative and allocation signals, not as direct trading signals.
- A stance shift matters more than a single quote. Track "from what to what".
- If a famous investor prefers gold but allows a small Bitcoin/crypto allocation, classify it as hard-asset/debasement confirmation, not broad altcoin endorsement.
- If a famous investor is associated with prior skepticism, explicitly note the change and what evidence would confirm market adoption.
- Cross-check these views against ETF inflow/outflow, gold price, DXY, Treasury yields, and BTC/ETH price response.

### Key-Person View-Monitor List

Use this list for every daily review. Browse current public sources for the figures most likely to have fresh comments that day; do not quote or infer a stance without date/source context. Only include people with new high-impact comments, meaningful repeated comments, policy action, funding/product action, or a clear silence/absence that matters. Keep the full list as the monitoring universe, not as a daily wall of names.

| Group | Names to monitor | Baseline lens |
|---|---|---|
| US politics and administration | Donald Trump, J.D. Vance, David Sacks, Scott Bessent, Howard Lutnick, Treasury/White House crypto-policy officials | Pro-crypto campaign/policy rhetoric, strategic reserve or treasury policy, stablecoin rules, tax/accounting treatment, executive orders, market-structure bills |
| US regulators and lawmakers | SEC chair/commissioners, CFTC chair/commissioners, Fed chair/governors, Elizabeth Warren, Cynthia Lummis, Patrick McHenry successors, House/Senate banking/agriculture committee leaders | Enforcement vs clarity, ETF approvals, custody/accounting rules, bank access, DeFi/stablecoin treatment, consumer-protection opposition |
| Global politics and central banks | EU/ECB officials, UK Treasury/FCA, Hong Kong SFC/MA, Singapore MAS, Japan FSA, UAE/ADGM/VARA, China/HK policy voices, IMF/BIS officials, El Salvador/sovereign BTC voices | Jurisdictional adoption/restriction, reserve-asset rhetoric, CBDC/stablecoin competition, offshore liquidity channels |
| Traditional macro allocators | Ray Dalio, Paul Tudor Jones, Stan Druckenmiller, Bill Ackman, Howard Marks, Jamie Dimon, Warren Buffett/Charlie Munger legacy framing, Ken Griffin, David Tepper, Mohamed El-Erian | Gold/BTC/debasement framing, debt crisis hedges, skepticism or acceptance, risk-asset regime, whether crypto is portfolio hedge or speculative asset |
| Asset managers and ETF sponsors | Larry Fink/BlackRock, Fidelity, Vanguard, Franklin Templeton, VanEck, Bitwise, Grayscale, ARK/Cathie Wood, Galaxy/Mike Novogratz | ETF flows/products, tokenization, institutional custody, model-portfolio allocation, ETH/SOL/alt ETF transmission |
| Public-company and treasury sponsors | Michael Saylor/Strategy, Metaplanet, Semler Scientific, Tesla/Elon Musk, Block/Jack Dorsey, Coinbase/Brian Armstrong, Robinhood, PayPal, Blockstream/treasury-linked companies | BTC treasury demand, corporate balance-sheet adoption, payment rails, custody/exchange business signals, equity-market feedback loop |
| Crypto-native founders and KOLs | Vitalik Buterin, Anatoly Yakovenko, CZ/Yi He/Binance, Brian Armstrong, Arthur Hayes, Justin Sun, Stani Kulechov/Aave, Rune Christensen/Sky, Robert Leshner/Morpho, Hayden Adams/Uniswap, Andre Cronje, Sandeep Nailwal/Polygon | Protocol roadmap, ecosystem flows, decentralization/security risk, founder selling/buying, DeFi revenue, L1/L2 competition, governance/tokenomics shifts |
| Stablecoin, RWA, and payments leaders | Circle/Jeremy Allaire, Tether/Paolo Ardoino, Ripple/Brad Garlinghouse, Ethena/Guy Young, Ondo/RWA leaders, Stripe/PayPal crypto leads | Stablecoin supply, regulation, reserves, payments adoption, RWA tokenization, dollar-liquidity transmission |
| Skeptics and opposition voices | Elizabeth Warren, Jamie Dimon, Nouriel Roubini, BIS/IMF skeptics, ECB skeptics, consumer-protection NGOs, anti-money-laundering officials | Ban/restriction risk, banking access pressure, AML/sanctions framing, systemic-risk rhetoric; distinguish informed policy opposition from headline noise |

Daily writing rules:

- Start with the highest-impact fresh item, not with the most famous person.
- Classify each update as `new`, `repeat`, `softening`, `hardening`, `reversal`, or `policy/product action`.
- Map each view to assets: BTC/gold hard assets, ETH, broad crypto beta, stablecoins/RWA, miners, ETF issuers, treasury stocks, or specific altcoin ecosystems.
- Cross-check pro-crypto comments against ETF flows, stablecoin supply, product launches, legislation, enforcement, and price response.
- Cross-check anti-crypto comments against enforcement actions, banking restrictions, lawsuit risk, legislation odds, and exchange/token price response.
- Do not treat political slogans, campaign posts, or founder promotion as confirmed capital flow unless paired with policy, product, treasury action, ETF flow, or on-chain/exchange flow.
- If a monitored figure has no new verified statement, do not force them into the report; write a one-line coverage note such as `核心名单未见新的高影响观点转向`.
### Altcoin Fundamental Framework

Use this framework whenever the daily review discusses altcoins beyond BTC/ETH/SOL.

| 分析维度 | 关键指标 / 观测点 | 对应股票逻辑 |
|---|---|---|
| 网络使用与需求 | TVL、active addresses、DAU/MAU、transactions、protocol revenue、fees、DEX volume、borrow/lend utilization、bridge volume | 营收增长、用户增长、DAU/MAU、付费率 |
| 代币经济学 | FDV vs market cap、circulating supply、unlock/cliff/vesting、emissions、burn/buyback、staking yield source、real yield vs inflation | 股本稀释、回购、定增、解禁压力 |
| 筹码与资金流 | CEX netflow、whale/top-holder changes、smart-money flow、staking/unstaking queue、MEV/staking share、top holder concentration、exchange reserves | 机构持仓变动、主力筹码分布、融资融券/质押压力 |
| 叙事与 Beta | Theme heat, policy beta, ecosystem beta, ETF/treasury/institutional narrative, developer/ecosystem catalysts, major partnerships | 行业景气、赛道风口、政策 beta、主题投资 |

Rules:

- Separate "price momentum" from "fundamental confirmation". A token can be a good trade but a weak fundamental setup.
- For every strong theme, name representative leaders, laggards, and confirmation metrics.
- For every weak theme, state whether the weakness is because of tokenomics supply, lack of usage, poor holder flow, or simply temporary beta underperformance.
- For BTC/ETH base assets, still include macro, ETF flows, halving/supply cycle, and derivatives structure as the dominant fundamental layer.
- If only Binance category heat is available, call it "market heat" rather than "fundamental confirmation".

### Core Market State Dashboard Requirements

Always include the following compact dashboard near the top of a Daily Review. It is a 12-domain state dashboard, not a four-dimension checklist:

| 维度 | 关键复盘指标 | 关注重点 |
|---|---|---|
| 宏观与联动 | 美股、DXY、10Y/30Y、美债、油金、Fed 预期 | 加密市场与传统宏观资金是否联动，有无脱钩迹象 |
| 大佬观点与叙事转向 | 政界/监管、传统金融、商界、ETF/资管、加密原生与反对派关键人物关于 BTC/ETH/crypto/稳定币/监管/gold/债务危机的最新表态 | 观察是否出现从怀疑到接受、从支持到限制、从黄金独占到 gold+crypto、从交易到配置、从口号到政策/资金落地的变化 |
| 资金与流动性 | BTC/ETH ETF 净流入、稳定币供给、交易所流动性、鲸鱼/财库动作、大额买卖盘 | 市场是存量博弈还是增量资金入场；无新闻时的大额买卖盘是否改变方向 |
| 衍生品、期权与情绪 | Funding、OI、多空比、taker buy/sell、期权 max pain/高 OI strikes/put-call skew、爆仓热力图、Fear & Greed | 杠杆是否过高或过低，情绪是否极端，期权盘是否在涨跌后追买/保护 |
| 成本与支撑压力 | 平均持仓成本、短期持有者成本、ETF/财库成本、期权持仓成本、清算成本 | 当前价格相对主要成本带是盈利区、止损区还是强制减仓区 |
| 盘面与主线 | 板块轮动、涨幅榜常客、领涨/滞后、BTC dominance、Meme/AI/DeFi/RWA/L2 | 钱集中在哪些板块，主线是否可持续 |
| 山寨题材与基本面 | 按细分题材划分山寨；检查 TVL/活跃地址/收入、FDV/MC/解锁、CEX/鲸鱼/质押、叙事 beta | 判断是基本面改善、筹码推动、叙事交易还是单纯投机 |
| 预测回测与 Setup Performance | 昨日/前次价格判断、真实走势、命中/偏差、已完成 Setup 统计、模型修正 | 区分 Forecast Accuracy 与 Trade Setup Expectancy |
| 数据缺口 | 缺失项目 | 缺失数据对结论置信度的影响 |

### Daily Output Shape

Use this order:

1. `# 加密宏观每日复盘 - YYYY-MM-DD 22:00 BJT`
2. `## 数据快照说明`
3. `## 今日结论`
4. `## 今日交易台`
5. `## 昨日框架复盘`
6. `## 核心市场状态仪表盘`
7. `## 宏观与跨资产联动`
8. `## 大佬观点与叙事转向`
9. `## ETF、稳定币与市场流动性`
10. `## 巨鲸、财库与大额买卖盘`
11. `## 衍生品与微观结构`
12. `## 期权、成本与持仓结构`
13. `## Volume Profile、清算与筹码博弈`
14. `## 盘面主线与板块轮动`
15. `## 山寨币题材分层与基本面`
16. `## S4 Rotation Research`
17. `## 预测回测与 Setup Performance`
18. `## 未来大事催化`
19. `## 明日观察清单`
20. `## 数据与来源`

`## 昨日框架复盘` is the only section for prior-day market judgment, tested levels, regime and lessons. `## 预测回测与 Setup Performance` is the only section for Forecast Accuracy and completed S1-S5 setup statistics; do not repeat prior-day narrative there. Do not collapse the listed research modules into a generic `市场研究` wrapper or omit them on a `NO TRADE` day.

### Legacy 08:00 Report Content Preservation

Delivery gate: compare the populated research fields and charts with the reference reports, not just their headings. Preserve the BTC/ETH/SOL numeric dashboard, five-day OI notional, funding/taker plots, ETF series, estimated or measured volume profiles, separately labeled two-sided stop/liquidation panels, and thematic relative-strength/Alpha table whenever their inputs are available. With complete hourly OHLCV, compute explicitly labeled estimated Volume Profile according to the linked reference; lack of tick data alone is not a reason to discard this approximation. Explain any remaining gap by field. Reconcile body prices, chart dates, table snapshots and source timestamps; do not retain stale template dates or event text. S1-S5 execution rules do not change research-data coverage.

The 2026-09-13 and 2026-09-14 08:00 BJT reports contain required research content that must remain in the latest Skill. Only their former section 4 (`场景推演｜未来24小时`) and former section 5 (`Tactical Execution Matrix`) are structurally moved into `## 今日交易台`; do not delete the other sections or their analytical fields.

Preserve and map the remaining content as follows:

- Former `一页结论`: preserve the compact opening decision, current BTC/ETH/SOL state, risk vetoes, and key definitions across `## 今日结论` and the immediately following `## 今日交易台`; do not create a duplicate standalone section.
- Former `1. 市场状态与微观结构`: preserve mark price, 24h change, OI/OI notional, funding, taker buy/sell or its labeled proxy, and price/OI/flow interpretation under the dashboard and derivatives sections.
- Former `2. OI notional 五日趋势`: preserve a five-day OI-notional trend chart/table whenever qualified same-source history is available. Explain `OI notional = contract open interest quantity × mark price`; it is not spot market cap or daily traded volume. If unavailable, mark it `UNAVAILABLE` rather than using an old snapshot.
- Former `3. ETF、宏观与大佬观点`: retain all three components in `## ETF、稳定币与市场流动性`, `## 宏观与跨资产联动`, and `## 大佬观点与叙事转向`, with CPI/FOMC/policy state synchronized to the catalyst calendar.
- Former `6. 成交量分布与筹码密集区`: preserve POC, VAH, VAL, HVN, LVN, value-area coverage, window, timeframe, volume-bin method, and approximation limits under `## Volume Profile、清算与筹码博弈`. Never present a price line as Volume Profile.
- Former `7. 清算/筹码分布代理图`: preserve the distinction between real liquidation heatmap, analyst-inferred stop zones, and reliable proxy levels. A proxy is allowed only when its base data is reliable and must be labeled `PROXY`; otherwise report `UNAVAILABLE` and do not invent liquidation pools.
- Former `8. 山寨币 Alpha Filter｜主题分层，只保留 Top 2`: preserve thematic classification, the four-factor Alpha Filter, Top 1-2 concentration, representative assets, unlock exclusion, and one-line risk notes under the altcoin and S4 sections. Do not restore a long altcoin list or independent altcoin report.
- Former `9. 未来大事催化`: preserve the catalyst table under `## 未来大事催化`, carrying forward known scheduled events and distinguishing `Known Scheduled Event`, `New Development`, and `Event Outcome`, with first-confirmed time and today's incremental change.
- Former `10. 预测回测与数据边界`: preserve forecast window, prior call, actual-path validation, trigger/fill assumptions, pending state, data gaps, and model adjustment under `## 昨日框架复盘` and `## 预测回测与 Setup Performance`. Never claim a fill from an untriggered plan.
- Former `来源与口径`: preserve a dated source list and access limitations under `## 数据与来源`, including exchange/API snapshot time, ETF cutoff, macro primary sources, fallback data grades, and unavailable fields.

Do not reproduce former sections 4 and 5 as separate chapters. Scenario probabilities, trigger paths, the S1-S5 scanner, the Conditional Zone Plan, and all If-Then execution fields belong in `## 今日交易台`; the rest of the 08:00 research content must remain visible in the mapped sections above, even when the final decision is `NO TRADE`.

Daily Review Mode output must be concise and execution-heavy:

- Historical review, generic macro background, and repeated key-person context should be no more than ~40% of the total report.
- Tactical sections (`今日交易台`, `Volume Profile / Liquidation`, `山寨题材与 S4 Rotation Research`, `未来大事催化`, `明日观察清单`) should receive the majority of detail.
- Use exact levels and if-then rules. If exact data is unavailable, say `No trade / wait` or provide a proxy level with lower confidence.
- Produce the formal report as `.docx`; embed charts in the document and save chart PNGs in `D:\codex\crypto_macro_daily\charts\YYYY-MM-DD\`. Use local Python/Word libraries or other available document tooling. If the Word generation dependency is unavailable, create a clean HTML source and convert when possible; still report the blocker explicitly.
- Recommended file names: `crypto_macro_daily_YYYY-MM-DD_HHMMBJT.docx` for the formal report, `crypto_macro_daily_YYYY-MM-DD_HHMMBJT.md` only as source/build artifact, and chart files such as `YYYY-MM-DD_price_levels.png`, `YYYY-MM-DD_etf_flows.png`, `YYYY-MM-DD_microstructure.png`, `YYYY-MM-DD_liquidity_pools.png`, `YYYY-MM-DD_alt_alpha.png`.

### Word and Visualization Requirements

For Daily Review Mode, generate the Word report with embedded visuals when possible:

- **Price/levels chart**: BTC, ETH, SOL latest price versus prior support/resistance, invalidation, TP1/TP2. Use horizontal level lines and labels with exact prices.
- **ETF flow chart**: latest 3-7 available trading days for BTC/ETH/SOL/HYPE if available. Separate preliminary from final values.
- **Microstructure chart**: funding, OI, Taker Buy/Sell Imbalance Proxy or real CVD, and long/short ratios for BTC/ETH/SOL in a compact grouped chart or dashboard.
- **Liquidity pool chart**: liquidation heatmap if accessible; otherwise proxy map of upside/downside stop pools using high-OI options strikes, recent swing highs/lows, round numbers, and cost-basis levels.
- **Alt Alpha chart**: top-2 selected altcoins only, with relative strength, driver type, unlock risk, and inclusion/exclusion decision.

Rules:

- A chart must answer a trading question; do not add decorative charts.
- If raw liquidation heatmap data is unavailable, label the chart and table as `proxy liquidity map`.
- Embed chart PNGs inside the `.docx`; do not deliver chart files separately unless the user requests them.
- The final response should link only the Word report by default. Mention markdown source/backtest update only in one sentence.

`## 大佬观点与叙事转向` must include:

- Latest stance changes from the tracked key-person view-monitor list when available, covering political/regulatory figures, traditional-finance allocators, business leaders, ETF/asset-management sponsors, crypto-native founders, and prominent skeptics/opponents.
- A "then vs now" comparison if the figure has a known prior crypto/gold view.
- Whether the view supports BTC-only, gold+BTC hard assets, ETH/crypto beta, miners/ETF/treasury equities, or broad altcoins.
- The confidence level after cross-checking with price, ETF flows, DXY/yields, and gold.
- If no meaningful new view is available that day, state "未见新的高影响大佬观点转向；核心名单无新增高影响表态" rather than omitting the section.

### Key-Person Monitor and Evidence Log

Maintain `D:\codex\crypto_macro_daily\key_person_monitor.json` (or the active migrated daily-report root) as the persistent monitor registry. At minimum cover: US executive/political figures (Trump/White House and pro-/anti-crypto Senate voices), regulators (SEC/CFTC/Fed leaders), macro allocators (including Dalio), major asset managers/ETF sponsors (including BlackRock/Fink), corporate treasury/business leaders (including Strategy/Saylor and relevant large technology executives), crypto-business leaders (Coinbase/Binance), crypto-native protocol founders (including Ethereum), and prominent banking/consumer-protection skeptics.

- Run the registry scan every Daily Review and retain `cutoff time`, `covered people`, `candidate count`, `source URLs`, `source tier`, and failures. A secondary news headline is only a lead; it does not establish a view shift.
- For every reportable change, log `person | previous stance | current statement/action | date/time | primary or credible source URL | change type (new/repeated/softened/hardened/reversed/policy-action/product-action/capital-action) | affected asset/theme | required market confirmation`.
- If candidates are collected but not validated, show `DATA_REVIEW_PENDING` and the short candidate list. If collection fails, show `DATA_COLLECTION_FAILED` and failure count. Only after a completed, timestamped scan and source review may the report say `NO_MATERIAL_CHANGE`.
- The leader section must not become a daily list of opinions. It should contain validated changes, repeated positions that matter because they were acted upon, and transparent scan status. It must never silently reuse yesterday's statement as today's update.

`## 未来大事催化` must include:

- A compact table of upcoming events over the next 1-30 days, and longer-dated events only if they can affect current positioning.
- Event type: macro data/Fed, ETF/asset-management decision, legislation/regulation/court, protocol upgrade/mainnet, token unlock/vesting/airdrop, treasury/earnings, conference/KOL event, or governance vote.
- Exact date/time and timezone when available; use `tentative` when the date is not fixed.
- Impacted assets/themes: BTC, ETH, SOL, stablecoins/RWA, DeFi/Yield, Restaking, Meme/Pump, AI, Privacy/ZK, L1/L2, exchange tokens, miners, ETF issuers, or treasury stocks.
- Expected transmission path and confirmation metric, such as ETF flow, DXY/yield reaction, funding/OI reset, TVL/fees/user growth, unlock absorption, governance result, or price reclaim/breakdown level.
- Risk/invalidation: what would make the catalyst fail, be priced in, or reverse.
- Do not turn a calendar item into a bullish/bearish conclusion by itself; connect it to current positioning, liquidity, and price levels.

`## 清算图、筹码分布与博弈推演` must include:

- A visual chart when data is available. Prefer an actual liquidation heatmap; otherwise generate a proxy liquidity-pool map using recent swing highs/lows, option high-OI strikes, round-number stops, and visible support/resistance. Label it `proxy` when not using a true heatmap.
- A compact table:

| 标的 | 上方流动性池 / short stops | 下方流动性池 / long stops | 主力猎杀路径 | 反向确认 | 交易含义 |
|---|---|---|---|---|---|
| BTC/ETH/SOL/top alt | Exact levels | Exact levels | Sweep up / sweep down / range pin | Exact reclaim or breakdown | Long, short, hedge, or no trade |

- Explicitly state the best long-hunt zone and short-hunt zone. Use an evidence-specific If-Then rule such as a sweep plus reclaim/fail, with the exact venue, candle duration and flow threshold. Do not use an illustrative price or call a ratio CVD.
- Do not call a liquidity pool a target by itself. A pool becomes tradable only after sweep + reclaim/fail confirmation.

`## 山寨币题材分层与基本面` must include:

- A compact table with theme, representative tokens, 24h relative strength, fundamental support, tokenomics/flow pressure, and trading conclusion. Keep this table brief; it is a filter, not a catalogue.
- A clear split between: strong with fundamentals, strong but mostly narrative, weak despite narrative, and avoid/watchlist.
- At least one paragraph mapping active altcoin themes into the four-factor framework: network usage/demand, tokenomics, chips/flow, narrative beta.
- If sufficient data is unavailable, include a visible data-gap line and lower confidence rather than omitting the section.
- The actionable alpha list is hard-capped at the top 2 altcoins. These are the only altcoins allowed to receive a full execution row inside the first-priority card or second candidate. All others receive a one-line risk note only.
- Then run the **Altcoin Alpha Filter** and output a compact filter table:

| Step | Required check | Result |
|---|---|---|
| 1. Alt/BTC relative strength | ETH/BTC, TOTAL3/BTC, BTC.D, or proxy breadth if unavailable | Risk-on, BTC-led, or weak breadth |
| 2. Top 1-2 only | Choose only 1-2 absolute mainline altcoins for actionable focus; if no clean alpha exists, choose zero and write `No alt trade` | Names and reason |
| 3. Driver attribution | Fundamental, flow/positioning, or narrative/liquidity | Do not confuse price heat with fundamentals |
| 4. 7-day unlock risk | Exclude long plans if known cliff unlock >1%; if unavailable, mark data gap | Include/exclude decision |

- All other altcoins must be classified as `跟随资产`, `观察资产`, or `排除资产`; do not give them full trade plans.
- If an altcoin has known >1% cliff unlock in the next 7 days, remove it from long setups even if price momentum is strong. It may only be used as a short/hedge candidate or marked `No trade`.
- If unlock data cannot be checked, keep position sizing at light risk only and state `unlock data unavailable`.

`## 今日交易台` must answer whether to trade before the research sections:

1. **Bias vs Location table** for BTC, ETH, SOL and Alt Breadth with `Bias`, `Location`, `Regime`, and `Trade Meaning`. Bias never implies a trade.
2. **One decision only**: `TRADE`, `WAIT`, `MANAGE ONLY`, or `NO TRADE`, followed by the two to four decisive reasons. A missing location advantage or missing trigger is `NO TRADE`. Apply the regime/setup-specific dynamic R:R gates below; every R:R is net of fees, expected slippage, and applicable funding.
3. **S1-S5 Setup Scanner** is a short research filter, not an execution-state or position-management panel. It contains exactly `Setup | 必要条件 | 本轮结论`, at most five rows. Do not display `WATCH`, `ARMED`, `EARLY_ACCEPTED`, `CONFIRMED`, `MANAGE_ONLY`, `MISSED`, `INVALID`, `READY`, filled status, position size, stop management, or any management instruction in this scanner. Explain immediately below in plain Chinese which prerequisite is missing or which setup has qualified; execution details belong only in the conclusion's conditional-plan table and, if needed, the first-priority card.
4. **First-priority opportunity card**, only when a candidate exists. Required fields: asset, direction, setup type, regime, why it exists, liquidity/structure location, trigger, current price, ideal entry, max entry, exact stop, first obstacle, TP2, gross and cost-adjusted R:R to the first obstacle, status, starter risk, add condition, cancel condition, and missed condition. If not currently executable, write `NOT TRIGGERED — WAIT`.
5. **S4 Rotation Map** only when breadth and multiple representatives confirm rotation; otherwise write `No confirmed rotation`. A single-token move is `Token-Specific Move`.
6. **Kelly / Portfolio Risk**. If there is no `EARLY_ACCEPTED` or `CONFIRMED` setup, write `Kelly not applicable — no executable setup.` Never invent account size, quantity, or USDT notional.

7. **Conditional Zone Plan**: the plan must appear inside `## 今日结论` immediately after the one-sentence conclusion; do not repeat it later as a second table. When reliable structure exists, include both long-side and short-side candidate zones in one table: `Asset | Direction | Trigger signal (If) | Entry Zone / Max Entry | SL | TP1 / TP2 | First-obstacle Net R:R | Weighted Net R:R | Setup | Execution / Expiry`. Write the exact numeric level beside every POC/VAL/VAH reference inside the same cell; e.g. `跌破 VAL 83,641 后，15m 收回 83,641` and `触及 VAH 84,778 后受阻并跌回 84,778 下`. A side without an evidenced, valid setup must be marked `NO QUALIFYING ZONE` or `UNAVAILABLE`, not assigned fabricated levels. Distinguish (a) alert zone that prompts reassessment, (b) pre-authorized passive limit probe, and (c) confirmed market execution. Touching an alert zone is not itself a fill or confirmation. Only an already staged, fully risk-checked limit order may fill automatically on touch.

**Dynamic R:R and stepped execution rules**:

- Calculate cost-adjusted `R:R_Obstacle` to the first obstacle and cost-adjusted `R:R_TP2` to TP2 or the external structure projection. Use `Weighted Net R:R = (0.4 * R:R_Obstacle) + (0.6 * R:R_TP2)`. Apply these minimum gates: **trend/continuation (primarily S2/S4)** requires weighted net R:R >= 1:1.8 and first-obstacle net R:R >= 1:1.0; **countertrend/reversal/range (S1/S3/S5)** requires weighted net R:R >= 1:1.3 and first-obstacle net R:R >= 1:1.0. For S5, the planned first mean target (normally POC or range midpoint) must independently offer net R:R >= 1:1.2. Use the stricter applicable threshold if regime and setup labels disagree. These are minimum economic gates, not evidence that an edge exists; they do not waive location, trigger, invalidation, data-quality, correlation or event-risk gates.
- Calculate Max Entry and all ratios at the actual candidate entry, including fee, spread, expected slippage and applicable funding. A conditional entry band `[Price_Min, Price_Max]` is valid only if the least favorable fill at `Price_Max` still satisfies the relevant dynamic weighted and first-target gates. If it does not, narrow the band or invalidate the plan. Never treat mere proximity to a zone as an entry.
- `Max Entry` is the worst price that still satisfies both R:R gates after fee, slippage and applicable funding, while respecting current ATR/realized volatility and spread. Do not move TP2 upward after the fact to manufacture a passing ratio.
- **S1/S5 passive limit probe**: a pre-staged limit may be used at an evidenced structural extreme even without right-side flow confirmation, but the level must be mapped before touch, supported by a measured profile/structure or a clearly labeled proxy, and have a fixed stop, expiry, invalidation/cancel rule, acceptable spread/slippage, positive net expectancy evidence or a separately authorized cold-start rule, and a passing setup-specific R:R at the worst fill. The probe's initial account-equity risk must be capped at 0.15%-0.25%, and the actual amount is the minimum of this cap and all setup/regime/correlation/daily caps; this range is a ceiling, never a target. If these preconditions are not all met, use an alert-only zone or `NO TRADE`. A touch/fill is execution, not proof of reversal; do not add risk until the setup's stated reclaim/acceptance evidence appears. Cancel stale or invalid orders. A proxy heatmap alone is not proof of a real liquidation pool.
- **S2a intrabar starter** is allowed when a meaningful structure breaks in real time, price trades beyond the level without immediate rejection, at least one independent flow confirmation is present, OI/funding do not show a severely crowded break, the trend-mode R:R gate passes, and current price is still `<= Max Entry`. A candle close is not required for the starter. Use `30%` of final allowed risk by default (permitted range `25%-40%`); the close, successful retest, or continued acceptance is still required before adding to final risk. A price break alone or R:R >=1.2 does not waive flow, crowding, Max Entry or 1:1.8 trend R:R gates. If the intrabar break fails, mark `INVALID` or `MISSED` according to whether the starter was filled; never chase after `Max Entry`. **S2b Breakout Retest Continuation** and **S2c Trend Pullback Continuation** are valid S2 subtypes under the Execution Learning V2 rules below; neither is an automatic chase or “buy every dip.”

### Allowed Setup Definitions

Only these five setup types may produce candidates:

- **S1 Liquidity Sweep Reversal**: a known stop/liquidation or structural pool is swept, then price reclaims or fails the specified boundary with flow confirmation. A wick alone is not a setup.
- **S2 Breakout Acceptance Continuation**: `Location -> Structure break -> Early Acceptance -> Starter Position -> Retest or continued acceptance -> Add`. The broken level must be meaningful (range edge, swing, VAH/VAL, LVN, supply/demand, liquidation cluster, option/cost confluence or repeatedly tested level), not a round number alone.
- **S3 Deleveraging Reset Reversal**: acute price move plus clear OI reset, liquidation/forced-selling evidence, funding cooling, leverage crowding loss, absorption/base, and reclaim of a key structure. This is a regime repair, not merely an S1 wick.
- **S4 Relative Strength / Narrative Rotation**: relative strength versus BTC/ETH, breadth across multiple representatives, volume/flow, independent catalyst, and fundamental/tokenomics checks. It covers BTC-to-ETH-to-SOL-to-alt and theme/leader-to-laggard rotation; one-token strength is not S4.
- **S5 Mean Reversion & Liquidity Zone Sweeps (Range Mean Reversion)**: only for a demonstrably balanced/range-bound regime without strong directional trend. Pre-map value-area edges/POC or another independently evidenced range boundary; use options max pain or provider liquidation clusters only when current source data is available, and label proxy levels as inference. Prefer sweep-and-quick-reclaim/rejection on 5m/15m; a passive limit probe is an allowed exception under the S1/S5 probe controls above. The first target is normally POC/range midpoint; a secondary target may be the opposite value boundary only when structure and net R:R support it. A simple POC/VAH/VAL touch without pre-defined invalidation, range regime and executable economics is not a setup. Never presume a 50%-55% win rate: estimate it only from completed, same-S5/same-regime trades, and otherwise report the edge as unproven.

**Conditional range / two-sided zone discipline**: zones are conditional scenarios, not a promise to trade every day or both directions. Mark each as `alert only`, `limit order staged`, or `market trigger pending`. Refresh zones when regime, volatility, data snapshot, or structural range changes; give each order/alert an expiry and cancel condition. If price enters an alert-only band, reassess the trigger, data freshness, spread, event risk, status and net R:R before entering. Do not label a zone `EXECUTABLE` merely because price touched it. `NO TRADE` remains valid whenever no setup passes, regardless of the distance to candidate zones or how low realized volatility is; never force an order to satisfy a daily/weekly frequency target.

**Setup rule version**: this S5 and dynamic-gate update is `crypto-macro-daily-review-s1-s5-dynamic-rr-v1`, effective `2026-09-21 BJT`. Record this rule version and effective date in future Setup Performance entries. Preserve all prior S1-S4 results under their original rule version; S5 begins with its own sample and must not inherit S1/S3 win rates or trade counts.

### S2 Acceptance and Chase Rules

For S2, do not use a single timeframe close as the definition of truth. Require this user-facing state machine:

`WATCH -> ARMED -> EARLY_ACCEPTED -> CONFIRMED -> MANAGE_ONLY`; exit states are `MISSED` and `INVALID`.

- `WATCH`: location and meaningful structure are identified, but no valid break.
- `ARMED`: setup, trigger, Ideal Entry, Max Entry, exact SL, and First Obstacle are fully defined, but the break/trigger has not occurred; current action is no entry.
- `EARLY_ACCEPTED`: either (a) the execution-timeframe candle has a real body close beyond the structure, or (b) an eligible **S2a intrabar starter** gate has fired. In both cases price must not immediately return to old value/range; at least one independent confirmation must exist (spot buying, volume expansion, Taker Buy/Sell Imbalance Proxy, real CVD, order flow or breadth); OI/funding must not show an obviously crowded leveraged break; the first obstacle must not be too close under the dynamic R:R gate; and current price must still be `<= Max Entry`. The S2a path does not require waiting for a candle close, but normally uses 30% (permitted range 25%-40%) of final allowed risk and cannot add until close/retest/continued acceptance. An S1/S5 limit fill without confirmation is not `EARLY_ACCEPTED`; it remains a small probe under its prewritten stop and must not be averaged down.
- `CONFIRMED`: a successful retest holds, or price forms continued acceptance outside the old range, while flow/OI/funding do not deteriorate. Only now may risk increase to the final allowed amount.
- `MANAGE_ONLY`: already filled; manage the existing position and do not create a duplicate plan.
- `MISSED`: trigger occurred but price exceeded `Max Entry`; state `DO NOT CHASE` and never move TP upward to manufacture R:R.
- `INVALID`: wick-only break, close back in range, flow/OI contradiction, hot funding, nearby first obstacle, clear intermarket divergence, spot non-confirmation, or rapid loss of the breakout level.

`READY` is permitted only as an internal execution flag if a local script requires it. Never display `READY` together with `EARLY_ACCEPTED` or `CONFIRMED`; the report displays only the states above.

Every setup must define `Trigger`, `Ideal Entry`, `Max Entry`, `Stop`, `First Obstacle`, and `TP2`. `Max Entry` must leave cost-adjusted first-obstacle net R:R >= 1:1.0 and satisfy the appropriate weighted gate above after fee, slippage and applicable funding; S5 must additionally preserve >=1:1.2 net R:R to its first mean target. It must also respect current ATR/realized-volatility/spread. If any applicable gate fails, there is no executable trade at that entry.

### Kelly and Portfolio Risk

Kelly is a risk-sizing tool only after a valid S1-S5 setup exists. Its inputs must come from completed real trades with the same `setup_type + regime`; subjective daily probabilities are prohibited. S5 samples must not be pooled with S1/S3 or with a different regime. Track at minimum: setup_type, rule_version, effective_date, regime, asset, direction, entry, stop, first_obstacle, tp, net_R_result, fees, slippage, funding_cost, MFE, MAE, win_loss, triggered, filled, missed, and cancelled.

- `N = Wins + Losses` for completed trades; `p_raw = Wins / N`; use conservative shrinkage `p_adj = (Wins + 10) / (N + 20)`.
- `b = Avg Net Win R / abs(Avg Net Loss R)`; Net R must already deduct fee, slippage and funding.
- `Full Kelly f* = (b * p_adj - (1 - p_adj)) / b`. If `f* <= 0`, set `Kelly Status = NO_EDGE`.
- `N < 30`: use the staged model-led calibration process in **Execution Learning V2** below. It derives evidence only from the immutable Model Execution Ledger, not unreported user trading. At `N=0-9`, an all-gates-passing setup may use `BOOTSTRAP_CALIBRATION` at `0.10%-0.15%` equity risk without a prior expectancy; at `N=10-29`, use `CALIBRATION_TEST` only when positive, robust model expectancy supports `0.15%-0.25%`. `Kelly Status` remains `INSUFFICIENT_SAMPLE`. These are ceilings, not targets. S1/S5 probes remain constrained by their stricter `0.15%-0.25%` cap, and all setup, regime, correlation, daily, event and data-quality caps still apply.
- `N = 30-59`: maximum `1/8 Kelly`; `N = 60-99`: maximum `1/6 Kelly`; `N >= 100`: maximum `1/4 Kelly`.
- `Final Risk = MIN(Fractional Kelly Risk or approved Calibration-Test Risk, Setup Risk Cap, Regime Risk Cap, Portfolio Correlation Cap, Daily Remaining Risk Budget)`.
- `<=0.75% equity` per setup and `<=2.0% equity` total daily tactical risk are hard ceilings, never target allocations or a default amount to use. Actual risk may be `0%`, `0.15%`, `0.25%`, or `0.40%`, and must reflect setup quality, Kelly, regime, correlation, event risk, and data quality.
- BTC/ETH/SOL in the same direction and multiple coins in one theme share a correlated cluster risk pool; do not calculate three independent Kelly bets.

### Kelly Eligibility Gate

Positive Full Kelly is necessary but not sufficient. Set `Kelly Status` only after checking all gates:

- **Sample**: completed trades meet the applicable minimum sample rule; otherwise `INSUFFICIENT_SAMPLE` and no Kelly sizing.
- **Expectancy**: `Expectancy_R = p_adj * Avg Net Win R - (1 - p_adj) * abs(Avg Net Loss R)` must be strictly positive. If not, use `NO_EDGE`.
- **Robustness**: if removing the best one or two completed trades makes expectancy materially negative, mark `FRAGILE_EDGE` and reduce or disable Kelly.
- **Regime match**: the current regime must match the historical `setup_type + regime` sample. A trend sample cannot size a range trade; mismatch is `REGIME_MISMATCH`.
- **Recent deterioration**: if rolling expectancy is materially below long-run expectancy for the same setup and regime, mark `DEGRADED` and lower the fractional Kelly allowance. Do not rewrite the setup after one loss; reduce risk only through this gate.

The `## 今日交易台` Kelly table must include: `Setup | Regime | Historical N | Wins | p_raw | p_adj | Avg Net Win R | Avg Net Loss R | Expectancy R | b | Full Kelly | Allowed Fraction | Kelly Risk Ceiling | Setup Risk Cap | Regime Cap | Correlation Cap | Daily Remaining Budget | Final Allowed Risk | Risk Mode | Kelly Status`. Allowed statuses are only `ELIGIBLE`, `INSUFFICIENT_SAMPLE`, `NO_EDGE`, `FRAGILE_EDGE`, `REGIME_MISMATCH`, and `DEGRADED`. `CALIBRATION_TEST` is a risk mode, not a Kelly status.

Scenario analysis may be included as optional research context, but it is never required to use a fixed three-row template, fixed probabilities, or an automatic trade plan. Untriggered paths remain scenarios, not orders.

## Forecast Backtest Mode

Maintain `D:\codex\crypto_macro_daily\price_forecast_backtest.md` as a living review log.

For each daily review:

- Read the existing backtest file if present.
- Append a new row for the current report's forecast.
- Use the formal `.docx` report filename in `report_file` when Word output is generated; markdown source filenames should be used only if Word generation failed.
- If the previous forecast has enough subsequent price action, update its result as `Hit`, `Miss`, `Partial`, or `Pending`.
- Record the actual path using concrete levels: high, low, whether support/resistance was tested, whether invalidation triggered.
- Record the dominant error source: macro surprise, ETF/flow reversal, large whale flow, funding/OI misread, options pin/hedging, liquidity gap, or missing data.
- Write one framework adjustment. Keep it narrow, testable, and reversible.
- Keep Forecast Accuracy separate from Trade Setup Expectancy. Forecasts measure direction/level path; setup statistics measure completed, filled S1-S5 trades. `WATCH`, `ARMED`, `EARLY_ACCEPTED`, `CONFIRMED`, or internal `READY` without a fill do not count as trade losses; record `MISSED`, `CANCELLED`, and `INVALID BEFORE ENTRY` separately.
- Maintain a Setup Performance Database alongside the forecast log with one immutable rule version and effective date for every setup-definition change. A poor result permits only a narrow, testable, reversible adjustment; never silently relabel historical trades or rewrite a setup after one loss.

Suggested table columns:

`date_bjt | report_file | forecast_window | directional_call | key_levels | actual_path | result | error_or_confirmation | framework_adjustment | next_check`

Do not rewrite history to make the model look better. Preserve prior calls and mark uncertainty honestly.

## External Text Analysis Mode

Use this workflow for X/Twitter, Telegram, KOL posts, trader notes, or research text.

### 1. Type Identification

Classify the input text as one or more types:

- **A. Derivatives_Trading**: OI, funding, liquidation heatmap, leverage, intraday structure, order book, liquidity sweep, fakeout, support/resistance, execution, margin, stop-loss, position sizing.
- **B. Fundamentals**: staking ratio, supply squeeze, protocol revenue, TVL, gas, L2/ecosystem metrics, ETF/treasury/whale, stablecoin liquidity, institutional allocation, long-term narrative.
- **C. Policy_Prediction**: regulation, law bills, enforcement, institutional policy, Polymarket/Kalshi odds, election/policy probabilities, expectation gaps.
- **D. Options_Cost_Flow**: max pain, high-OI strikes, dealer gamma, put/call skew, IV, block trades, option premium/cost basis, post-move call/put buying or selling.
- **E. Whale_Orderflow**: whale wallet movement, CEX inflow/outflow, large spot orders, treasury operations, OTC/ETF creation-redemption clues, abnormal taker flow.
- **F. Macro_Master_View**: high-profile investor, allocator, policy-linked, or institutional executive views on gold, Bitcoin, crypto, bonds, debt crisis, debasement, or portfolio hedging.

Also classify author style:

- `交易实战派`: level-driven, risk-control-driven, derivatives-heavy.
- `基本面研报派`: data/narrative-driven, longer horizon, on-chain or policy-heavy.
- `综合研判派`: combines derivatives, macro, policy, fundamentals, options, and whale flow.

### 2. Deep Extraction

For type A, extract:

- Key support/resistance and invalidation levels.
- Liquidity sweep or fakeout zones.
- OI direction and whether new positions are likely longs, shorts, hedges, or liquidations.
- Funding state: cold, neutral, warm, hot, or extreme.
- Liquidation heatmap or likely liquidation cluster if explicitly provided.
- Positioning and risk-control logic: entry, add, stop, reduce, margin cushion.

For type B, extract:

- On-chain supply/demand metrics: staking ratio, deposit/exit queue asymmetry, exchange reserves, stablecoin liquidity, gas, TVL, revenue, active users, bridge flows.
- ETF, treasury, whale, or smart-money flow.
- Ecosystem or sector narrative: ETH beta, SOL high beta, L2, DeFi, Meme, AI, RWA, Privacy, ZK.
- Altcoin theme and four-factor fundamentals: network usage/demand, tokenomics, holder/flow structure, and narrative beta. Explicitly mark which factor actually supports the thesis and which is missing.
- Time horizon and confirmation metric.

For type C, extract:

- Policy or prediction-market event.
- Polymarket/Kalshi probability, odds, or implied probability if provided.
- Actual-versus-expected gap.
- Legislative/regulatory timeline and what would confirm or invalidate the thesis.

For type D, extract:

- Dominant expiry, max pain, high-OI strikes, put/call ratio, skew, IV/risk reversal, block-trade direction, and whether post-move options flow is chasing continuation or hedging reversal.
- The option cost/premium zone that may become support, resistance, pinning, or forced hedging area.

For type E, extract:

- Asset, size, venue/wallet, direction, timing, source reliability, and whether there was an obvious news catalyst.
- If no catalyst explains a large flow, highlight it as a high-priority signal and define the price level that confirms or invalidates it.

For type F, extract:

- Speaker, role, venue, date, exact asset references, and whether the statement is a direct quote or secondary paraphrase.
- Prior stance versus current stance, especially for shifts such as gold-only or Bitcoin skepticism turning into gold plus Bitcoin/crypto allocation.
- Macro rationale: debt crisis, fiscal deficit, currency debasement, inflation, geopolitical risk, regulatory clarity, ETF adoption, or portfolio diversification.
- Market mapping: gold, BTC, ETH, broad crypto, miners, ETF products, treasury stocks, or altcoin beta.
- Confirmation requirements: ETF flow, gold/BTC co-movement, DXY/yields, price level confirmation, or follow-through from institutional products.

### 3. Structured Report Output

When the user asks to analyze external text, output this Markdown structure:

```markdown
## 1. 核心观点与市场定性 (Executive Summary)

* **市场/标的定位**:
* **博主视角分类**:
* **综合多空倾向**:

## 2. 微观指标与细节拆解 (Detailed Technical & On-chain Metrics)

### A. 衍生品与资金流动性
* **盘面结构与流动性**:
* **衍生品数据**:
* **风控要求**:

### B. 基本面与链上叙事
* **链上与供需数据**:
* **山寨题材与四因素基本面**:
* **预测市场与政策博弈**:
* **顶级机构/大佬观点交叉**:

### D. 大佬观点与叙事转向
* **最新观点**:
* **历史立场变化**:
* **资产映射与市场影响**:

### C. 期权、成本与大额买卖盘
* **期权持仓成本与关键行权价**:
* **平均持仓成本与清算成本**:
* **巨鲸/大额买卖盘**:

## 3. 实战启示与策略预案 (Actionable Insights)

* **交易/配置思路**:
* **潜在风险点**:

## 4. Codex 自动化结构化数据 (JSON Schema)
```

If a subsection is not involved, keep it but mark `未涉及` and explain the missing evidence briefly. Avoid filling missing fields with guesses.

### 4. JSON Schema

Always include valid JSON in a fenced `json` block:

### 4.1 Daily Active Conditions Contract

Every formal Daily Review must also write the machine-readable condition state to both:

- `D:\codex\crypto_macro_daily\active_conditions.json`
- the repository copy `config/active_conditions.json`

The two files must describe the same snapshot and use this schema:

```json
{
  "date": "YYYY-MM-DD",
  "assets": {
    "BTCUSDT": {
      "long_zone": [0, 0],
      "short_zone": [0, 0],
      "alerted_long": false,
      "alerted_short": false
    },
    "ETHUSDT": {
      "long_zone": [0, 0],
      "short_zone": [0, 0],
      "alerted_long": false,
      "alerted_short": false
    },
    "SOLUSDT": {
      "long_zone": [0, 0],
      "short_zone": [0, 0],
      "alerted_long": false,
      "alerted_short": false
    }
  }
}
```

Rules for this contract:

- Every Daily Review must include all three keys: `BTCUSDT`, `ETHUSDT`, and `SOLUSDT`. A side with no qualified plan must use an empty array `[]`, never invented prices or a stale previous zone.
- `long_zone` and `short_zone` are alert/observation intervals, not orders. The Word table remains authoritative for trigger, Max Entry, SL, TP1/TP2, Net R:R, expiry, and cancellation.
- When a daily plan is recalculated, replace the zones and reset only the corresponding `alerted_long`/`alerted_short` flags for changed zones. Do not carry an old alert into a materially different zone.
- A price monitor may notify when a price enters a non-empty zone, but the alert must say that 15m/30m reclaim, rejection, HL/LH, flow, and risk gates still need confirmation. An alert never means “filled”, “confirmed”, or “user traded”.
- The monitor state is append/update state only. It must not rewrite the Daily Review, change a setup status, move a stop, widen a Max Entry, or create a new trade plan.
- The generated JSON must parse successfully before delivery. If the repository copy cannot be synchronized, mark the report data quality as incomplete and do not claim that monitoring is active.

The repository monitoring implementation is `scripts/price_monitor.py`, and its scheduled workflow is `.github/workflows/price_monitor.yml`. The workflow uses the repository secret `FEISHU_WEBHOOK_URL`, polls Binance public spot prices, sends one Feishu card per side/zone, and commits only alert-flag changes back to `config/active_conditions.json`.

```json
{
  "timestamp": "YYYY-MM-DD",
  "source_author": "",
  "content_type": ["Derivatives_Trading", "Fundamentals", "Policy_Prediction", "Options_Cost_Flow", "Whale_Orderflow"],
  "author_style": "交易实战派 / 基本面研报派 / 综合研判派",
  "market_bias": "Strong_Bullish / Bullish_Range / Neutral / Bearish / High_Risk_Warning",
  "primary_assets": [],
  "derivatives_signals": {
    "key_levels": {"support": [], "resistance": [], "invalidation": []},
    "oi_status": "",
    "funding_rate_status": "",
    "liquidation_risk": "",
    "liquidity_structure": ""
  },
  "options_and_cost_signals": {
    "average_cost_basis": {},
    "options_max_pain": "",
    "high_oi_strikes": [],
    "put_call_or_skew": "",
    "post_move_options_flow": ""
  },
  "whale_orderflow_signals": {
    "large_flows": [],
    "unexplained_large_buy_sell": "",
    "confirmation_level": "",
    "invalidation_level": ""
  },
  "fundamental_signals": {
    "onchain_metrics": {},
    "altcoin_theme_fundamentals": {},
    "flow_or_treasury_signal": "",
    "prediction_market_event": "",
    "probability_or_odds": "",
    "policy_or_narrative_gap": ""
  },
  "macro_master_view_signals": {
    "speaker": "",
    "prior_stance": "",
    "current_stance": "",
    "stance_shift": "",
    "asset_mapping": [],
    "market_impact_level": "",
    "confirmation_metrics": []
  },
  "actionable_summary": "",
  "forecast_backtest_note": "",
  "data_gaps": []
}
```

## Interpretation Heuristics

- Read microstructure as a sequence: price path -> OI change -> funding state -> taker/CVD -> top-trader vs crowd positioning -> options/liquidation map. Do not make a directional claim from OI alone.
- OI increase + price does not move: classify as `Squeeze Setup` or position accumulation. Wait for breakout direction; do not assume bullish or bearish before price leaves the range.
- OI increase + taker/CVD declines: possible passive limit-order absorption or distribution. If price holds support while taker is negative, infer potential limit-bid absorption; if price stalls at resistance while taker weakens, infer potential passive sell distribution. Mark as inference and require confirmation.
- Funding extreme + top-trader positioning opposite to general account positioning: classify as `Retail vs smart-money divergence`; look for liquidation-hunt levels instead of following the crowded side.
- Funding extreme + top-trader and general account positioning both crowded on the same side: classify as `Crowded consensus`; reduce chase trades and define the nearest liquidation/pain level.
- Price breaks a key level with OI up and taker/CVD positive: stronger trend continuation, but only if funding is not already hot/extreme and ETF/macro flow does not contradict it.
- Price breaks a key level with OI up but taker/CVD negative: possible stop-run/fakeout or limit-order distribution; require close confirmation before entry.
- Price reclaims a key level with OI down and funding cooling: often cleaner short-covering/deleveraging repair; upgrade only if follow-through volume or ETF/spot flow confirms.
- Use `Taker Buy/Sell Imbalance Proxy` when real CVD is unavailable. State that it is a flow proxy and lower confidence versus exchange-level CVD; never call it CVD.
- Price up + OI up + funding hot: trend can continue, but chasing risk rises; prefer pullback confirmation.
- Price up + OI flat/down + funding cool: healthier spot/short-covering move; trend confirmation needs follow-through.
- Price down + OI down + funding cool: deleveraging pullback; support can hold if flows remain positive.
- Price down + OI up + long/short rising: trapped-long risk; avoid dip-buying until liquidation clears.
- Price down + OI up + funding hot + top long/short high: crowded long pain; require OI/funding cooldown before calling support.
- ETF inflow with weak price: hidden supply, derivatives pressure, or option pinning; watch for delayed catch-up or failed demand.
- ETF outflow with stable price: resilient spot bid, but upside needs new catalyst.
- Large spot buy/sell with no news: treat as more informative than narrative headlines; define confirmation/invalidations from the tape.
- Large CEX inflow without sell context: potential supply only, not confirmed selling.
- Large CEX outflow or custody accumulation: potential accumulation only, not confirmed buying unless paired with price/flow confirmation.
- Funding is a primary risk thermometer. Hot funding near resistance downgrades chase setups; cold/negative funding near support upgrades squeeze potential only if OI stops rising against price.
- Option max pain/high-OI strike near spot can pin price into expiry; post-rally call selling or put buying can cap upside; post-drop put selling or call buying can stabilize downside.
- Average cost basis acts like behavioral support/resistance: price below STH cost with hot funding is fragile; price reclaiming STH cost with cooling OI is a stronger repair.
- BTC strong while SOL/memes weak: defensive large-cap repair, not full risk-on.
- ETH strong with ETF/infra news: blue-chip alt confirmation; use ETH as risk appetite check.
- Altcoin strength with TVL/revenue/address growth, clean tokenomics, supportive holder flow, and strong narrative beta: higher-quality rotation.
- Altcoin strength driven only by category heat or price momentum, with FDV/unlock pressure or whale selling: treat as tactical beta, not fundamental confirmation.
- If a theme rises while its leaders do not participate, downgrade the theme to speculative or fragmented.
- If one token leads a theme but peers lag, separate token-specific catalyst from sector-wide rotation.
- When major allocators move from crypto skepticism to gold-plus-Bitcoin or hard-asset framing, treat it as a BTC/gold debasement-narrative confirmation first; only extend it to ETH/alt beta if ETF flows, ETH strength, or broad liquidity confirm.
- If the famous-investor view is only gold-positive and Bitcoin is mentioned as a small allocation, do not call it broad crypto endorsement.
- Prediction-market probability up while price flat: possible expectation gap; verify liquidity and whether the event is actually economically meaningful.
- On-chain supply squeeze claims require at least one confirming metric: staking queue, exchange reserve, ETF/treasury absorption, or realized flow.

## Lessons From Local Reviews

- Start with BTC regime and levels, not narrative. Use a core box first, then assign low-buy, breakout-follow, failed-breakout defense, or wait.
- Treat ETF inflow as a cushion, not automatic upside. Only sustained multi-day inflow plus non-overheated derivatives should upgrade the regime.
- Use funding and OI to judge move quality. Hot funding plus OI expansion calls for chase-risk control; funding/OI cooling during a pullback is often healthier than price alone suggests.
- Add whale/order-flow override: in the absence of obvious news, unexplained large BTC/ETH/SOL spot flow can explain price better than macro narrative and must be tracked explicitly.
- Add options/cost-basis override: when spot sits near max pain, high-OI strikes, STH cost, ETF average cost, or liquidation cost bands, level behavior matters more than narrative confidence.
- Use ETH and SOL as confirmation layers. ETH holding or leading confirms blue-chip risk repair; SOL failing to reclaim its threshold means high-beta appetite is incomplete.
- Keep macro linkage explicit. Nasdaq/AI/semis, DXY, 10Y/30Y yield, oil shocks, and US policy headlines often explain why crypto can hold support but fail to expand.
- Sector heat must answer whether money is concentrated or spreading. Separate BTC/ETH treasury or ETF demand from broad AI, Meme, DeFi, RWA, Privacy, ZK, and L2 rotation.
- Altcoin analysis must not be a gainers list. It must classify themes and test each theme against network usage, tokenomics, chips/flows, and narrative beta.
- When a theme is hot but fundamentals are missing, label it as narrative/beta rather than fundamental improvement.
- Track "view shifts" from major allocators. The change in stance is often more informative than the absolute quote.
- Data gaps are part of the decision. If stablecoin liquidity, liquidation heatmap, options flow, cost basis, itemized whale flow, or raw KOL source data is unavailable, label the gap and avoid turning inference into fact.
- Maintain forecast humility: every daily direction/level call must be eligible for later review, and misses should produce narrow framework adjustments rather than wholesale narrative rewrites.

## Hard Red Lines

- Never label a wallet transfer as selling unless destination/context supports it.
- Never label a large order-book wall as real demand/supply without considering spoofing/cancellation risk.
- Never imply ETF figures are final if they are preliminary or from one source.
- Never call a breakout confirmed without at least price level plus volume/flow/derivative context.
- Never publish a Daily Review Mode formal report as markdown only when `.docx` generation is available.
- Never provide a trade idea without exact If-Then trigger, entry, invalidation/SL, TP1/TP2, numeric R:R, and position-risk cap.
- Never give full execution plans for more than two altcoins. Non-selected altcoins get one-line risk notes only, and all execution belongs inside `## 今日交易台`.
- Never call a liquidity pool a trade target without sweep + reclaim/fail confirmation.
- Never treat option max pain as a price target by itself; use it as one pressure/pinning input.
- Never omit funding when forming a BTC/ETH/SOL directional view.
- Never omit thematic classification when discussing altcoins.
- Never claim an altcoin has fundamental support only because its price or category is up; identify the supporting usage, tokenomics, flow, or narrative-beta evidence.
- Never convert a famous investor's gold/BTC hedge comment into a blanket bullish call on all crypto or all altcoins.
- Never cite a famous investor's historical stance change without date/source context when it matters to the thesis.
- Never omit the forecast-backtest note from daily reviews.
- Never omit the data gap note when Binance MCP/API or public data access fails.
- Never convert a KOL view into the analyst conclusion without stating what is corroborated and what remains only the author's view.
- Never output invalid JSON in the structured data section.

## Execution Learning V2

**Rule version:** `crypto-macro-daily-review-execution-learning-v2`; effective `2026-09-23 BJT`. This is an additive execution-and-learning layer. It does not replace, compress, or alter the mandatory daily Research Engine.

Before a daily review, intraday scan, performance review, or sizing decision, read [execution-learning-engine.md](references/execution-learning-engine.md). Use `scripts/execution_learning.py` for ledger initialization, immutable recording, settlement, aggregation, leverage conversion, and self-tests.

### Non-negotiable boundaries

- Maintain separate Model Execution and User Realized ledgers under `D:\codex\crypto_macro_daily\execution_learning`. Unless the user explicitly reports a trade, uploads a record, or authorizes read-only account data, set `user_execution_status=UNKNOWN`. Never infer that the user did not trade, missed a trade, profited, or lost.
- `Kelly Evidence Source` defaults to `MODEL_RULE_EXECUTION`. Report model rule fills and user execution separately. `WATCH`, `ARMED`, `MISSED`, `CANCELLED`, and `INVALID_BEFORE_ENTRY` model records are never trade losses.
- Preserve frozen candidate terms. Append market-path transitions; never overwrite the entry, stop, target, costs, trigger, rule version, or evidence after creation.
- Quality Score (0-100) ranks candidates internally only. It cannot bypass a hard gate or create a setup. Do not optimize for trade frequency.

### Daily and intraday coordination

1. The Daily Research Engine completes the full report and writes a `Daily Market State File` with regime, bias, major levels, pools, themes, risk vetoes, event calendar, volatility state, data quality, and a 10-20 name universe (BTC/ETH/SOL core; liquid secondary perps and theme representatives selected dynamically).
2. `NO TRADE NOW — CONDITIONAL SETUPS ARMED` is permitted only for a genuine, fully risk-checked condition. State trigger zone, entry/Max Entry, stop, reclaim or flow condition, expiry, and cancellation. Never manufacture a zone to avoid a no-trade conclusion.
3. The independent Intraday Execution Engine scans every 15/30/60 minutes (default 30) against the latest state file. Refresh only mark price/OHLCV, short-term profile, OI/change, funding, taker/CVD, positioning, order book/spread, ATR/RV, pools, breadth, and relative strength. Re-evaluate S1-S5, append ledger events, and may change conditional state; it does not redo macro research or claim user execution.
4. Scan S1-S5 only. S2 subtypes are `S2a_INTRABAR_STARTER`, `S2b_BREAKOUT_RETEST`, and `S2c_TREND_PULLBACK`; use the detailed gates in the reference. Top-two reporting limits do not restrict the scanner or candidate ledger.

### Risk, clusters, and daily display

- Run phase, Kelly eligibility, robustness, gate-attribution, and correlation rules from the reference. Keep samples separate by `setup_type + setup_subtype + rule_version + regime`.
- Map at least `BTC_CORE`, `ETH_BETA`, `SOL_BETA`, `MEME`, `AI`, `RWA`, `DEFI`, and `L1_L2`. Cluster risk is the sum of correlated open model risk and is capped before a new entry.
- Sizing sequence is `structure -> stop -> equity risk -> notional -> leverage -> margin`. `Notional / Equity = Allowed Risk % / Stop Distance %`. Leverage changes required margin only; it never moves the stop. Require estimated liquidation distance >= `3x` stop distance, cap initial single margin at `15%-20%` equity and correlated combined margin at `30%-35%`. Without account equity, show percentages only.
- In `## 今日交易台`, retain existing Kelly fields and add `Evidence Source | Risk Mode | Setup Subtype | Model N | User N | model p_adj | model Expectancy R | model Full Kelly | User Data Status | Allowed Risk | Stop Distance | Notional/Equity | Suggested Leverage | Margin/Equity | Liquidation Buffer | Correlation Cluster | Final Allowed Risk`.
- Add a compact Opportunity Funnel: `Universe -> Location -> structures -> candidates -> ARMED -> EARLY_ACCEPTED -> CONFIRMED -> model filled`, with primary rejection reasons and top-two risks. Keep detailed logs in the background.

### Validation

After changes to these rules, run:

```powershell
python D:\codex\skills\crypto-macro-daily-review\scripts\execution_learning.py self-test
python C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\codex\skills\crypto-macro-daily-review
```

Do not promote a new subtype, major rule, or gate relaxation directly into Kelly Production: begin in `SHADOW`, collect out-of-sample model paths, then advance only under the reference phase rules.

### S5 Multi-Path Flow and Re-Arm

**Rule version:** `crypto-macro-daily-review-s5-flow-multipath-v1`, effective `2026-09-24 BJT`. This changes S5 only. S1-S4 retain their existing confirmation rules and prior records remain under their original rule versions.

Read [S5 multi-path flow and counterfactual audit](references/s5-multipath-flow.md) before creating, updating, cancelling, or reviewing an S5 candidate. Do not use a one-bar or fixed `5m Taker Buy/Sell Imbalance Proxy >= 1.00` test as the sole S5 long confirmation, and never call this ratio CVD.

- Every S5 card must record `flow_confirmation_status`, `flow_mode`, `absorption_score`, `structural_zone_id`, `structural_zone_status`, `attempt_id`, `attempt_status`, `fresh_trigger_id`, `attempt_count`, `rearm_eligible`, and `counterfactual_status` in addition to its frozen order economics.
- S5 can reach `EARLY_ACCEPTED` only through `ACTIVE_CONFIRMED`, `IMPROVING_CONFIRMED`, or `ABSORPTION_CONFIRMED`; all normal location, reclaim/acceptance, stop, dynamic R:R, Max Entry, regime, event, data-quality, and correlation gates remain mandatory.
- An attempt-level Flow failure records `CANCELLED_FLOW_FAIL`, not structural expiry. A valid structural zone may re-arm after cooldown only upon a fresh trigger. Default `max_attempts=2`; after two failed, stopped, or contradictory attempts, set `LOCKED_PENDING_RECALCULATION` and recompute profile, OI, funding, regime, and structure before reuse.
- Every `FLOW_CONFIRMATION_FAIL` records a `COUNTERFACTUAL_ONLY` shadow path using its original frozen entry, stop, TP1, TP2, and costs. It never enters Model Filled N, Kelly, or the User Realized Ledger. Review Flow Gate Contribution by active, improving, passive-absorption, and rejected groups before changing parameter values.


