# FundingPips — Full Verified Ruleset

Verified 2026-07-11 from fundingpips.com/trading-objectives (via browser_navigate)
and help.fundingpips.com (via Wayback Machine snapshots 2025-11-26 to 2026-02-10).

## 1 Step model

### Step 1 (Student / Evaluation)
- Profit target: 10%
- Max daily loss: 3% (of higher of equity/balance at session start)
- Max overall loss: 6%
- Min trading days: 3
- Trading period: Unlimited
- Leverage: 1:30 (FX 1:50, Indices 1:20, Metals 1:20, Energies 1:10, Crypto 1:2)
- News trading: Allowed
- Weekend holding: Allowed
- Inactivity: 30 days (close at least 1 trade every 30 days)
- Stop loss: Not required but highly recommended
- Max risk per trade: No restriction on Step 1

### Master (Funded)
- Profit target: None
- Max daily loss: 3%
- Max overall loss: 6%
- Max risk per trade idea: 3% (<$50K) / 2% ($50K+)
  - Includes: single trade, split trades, opening new position within 5 min in same direction
  - All collectively considered one trade for the 3% limit
- News trading: RESTRICTED
  - 5 min before/after high-impact (red folder) news events on affected currencies
  - Trades opened 5 hours before the news event are EXCLUDED from the restriction
  - Restricted window includes: manual trades, pending orders, stop-loss orders, take-profit orders
  - Profits from trades in the restricted window will NOT be counted (deducted)
  - For speeches (red folder): window extends from 5 min before speech begins until 5 min after speech concludes
- Weekend holding: Allowed
- Inactivity: 30 days
- Leverage: 1:30 (same as Step 1)
- 1.2% Risk Guideline: No restrictions (not applicable on 1 Step model)

## 2 Step model (for reference)

### Step 1 (Student)
- Profit target: 8% (Option One) or 10% (Option Two) — trader's choice
- Max daily loss: 5%
- Max overall loss: 10%
- Min trading days: 3
- Trading period: Unlimited

### Step 2 (Practitioner)
- Profit target: 5%
- Max daily loss: 5%
- Max overall loss: 10%
- Min trading days: 3

### Master (Funded)
- Max daily loss: 4%
- Max overall loss: 12%
- Max risk per trade: 3% (<$50K) / 2% ($50K+)
- News trading: RESTRICTED (same 5-min window as 1 Step)
- Overnight & weekend holding: Allowed
- Leverage: 1:100

## EA / Bot policy (verbatim from "What are the Forbidden Strategies?")

> "Using a third-party Expert Advisor (EA) is allowed as long as it is a trade or risk manager. Using any other third-party Expert Advisor is not allowed. This will lead to a denial of the evaluation or reward and closure of the account."

Forbidden strategies (verbatim):
- Gap trading
- High-frequency trading (HFT)
- Server spamming
- Latency arbitrage
- Toxic trading flow
- Hedging
- Long-short arbitrage
- Reverse arbitrage
- Tick scalping
- Server execution
- Opposite account trading
- Copy trading with others or account management by a third-party vendor

## Copy trading policy

Permitted:
- Copy trades between your own FundingPips accounts (same individual)
- Trade copier from FundingPips master to external slave account
  - IMPORTANT: Always use the investor password (read-only) when setting up a master account

Prohibited:
- Copying trades between FundingPips accounts owned by different users
- Coordinated trading across master accounts not owned by the same individual

## IP rule

- IP region must remain consistent (purchase, website login, account access)
- VPS/VPN: allowed; if IP region changes, FP may request proof
- Multiple ISPs: allowed; may be asked for proof
- Multiple devices within same city: allowed

## Toxic trading flow

Includes:
- Excessive risk-taking / over-leveraging
- Gambling behavior
- Overtrading
- HFT & tick scalping
- Arbitrage (hedge, latency)
- Poor money management

### Maximum Lot Exposure Limit (2-Step Master accounts only)
- $5K: None
- $10K: None
- $25K: Maximum 10 lots
- $50K: Maximum 20 lots
- $100K: Maximum 40 lots
- Note: NOT a daily limit — applies to open trades simultaneously
- First violation: warning. Second: account closure + profit deduction + 30% performance commission

## 20 lots per click rule
- Maximum order size: 20 lots per click/transaction
- Larger orders must be split into multiple transactions

## Daily loss reset
- Resets at 00:00 Platform Time (GMT+2)
- Dashboard shows reset timer

## MT5 server
- Server name: "FundingPips Corp (2)"
- May not appear in server list by default — must manually search and add
- If still not visible: clear MT5 cache and redo steps

## Account credentials
- Location: Dashboard → Accounts → click account number → Credentials (top-right, next to Share)
- Password also sent via registered email
- Master password=REDACTED_SET_LOCALLY
- Investor password=REDACTED_SET_LOCALLY

## Onboarding (Step 1 → Master)
- After passing Step 1: Master Account created with "onboarding" status
- Takes 2 working days
- Trading disabled until onboarding completes + reward cycle is set
- Steps: Manual Review (2 days) → KYC → Customer Agreement → Onboarding (2 days) → Set Reward Cycle → Trading enabled

## Scaling plan

| Level | Requirements | Rewards |
|---|---|---|
| Novice (L1) | 4 rewards + 10% profit | +20% capital, +1% DD |
| Intermediate (L2) | 8 rewards + 15% profit | +30% capital, +1% DD |
| Advanced (L3) | 12 rewards + 30% profit | +40% capital, +1% DD |
| Hot Seat (Elite) | 16 rewards + 40% profit | 2x balance, 100% split, $2M capital, monthly bonuses |

Monthly bonuses (Hot Seat): $100 for 5K, $200 for 10K, $300 for 25K, $400 for 50K, $500 for 100K

## Fail discount
- Step 1 fail: 10% off next purchase
- Step 2 fail: 15% off
- Master fail: no discount
- Valid 7 days, same model + size only
- Automated: code sent via email + dashboard

## Restricted countries
- Cannot join: UAE, Iran, Vietnam
- US/Canada: cannot use cTrader but CAN use MT5

## Platform lock
- Trading platform (MT5/cTrader/MatchTrader) CANNOT be changed after purchase

## Instruments
- Forex, Metals, Indices, Energies, Crypto — all with RAW spreads
- Indices/Oil: commission-free
- Forex/Metals/Crypto: commissions vary by model

## High-impact news affected instruments

| Currency | Affected instruments |
|---|---|
| USD | NFP, CPI, PPI, GDP, FOMC, Jobless Claims, ISM PMI, JOLTs, Consumer Confidence, Trade Balances, 10Y/30Y auctions, Home Sales, Durable Goods, Avg Hourly Earnings |
| EUR | PMI, CPI, GDP, Employment Change, Unemployment, Retail Sales, Trade Balance, ECB Rates/Statements, Deposit Facility Rate, Economic Sentiment, Business Climate, Consumer Confidence |
| GBP | PMI, CPI, GDP, Nationwide House Prices, Mortgage Approvals, Retail Sales, RPI, Housing Price Balance, BoE Rates/Statements, Trade Balances, Industrial/Manufacturing Production, Unemployment, Employment Change, Claimant Count, Consumer Confidence |
| CAD | BoC Rates/Statements, PMI, CPI, GDP, International Merchandise Trade, Wholesale Sales, Housing Starts, Trade Balance, Employment Change, Unemployment, Retail Sales |
| AUD | Cash Rate & RBA Statement, Employment/Unemployment, CPI, GDP, Retail Sales |
| NZD | Official Cash Rate & RBNZ Statement, Employment/Unemployment, CPI, GDP |
| CHF | CPI, SNB Policy Rate |
| JPY | PMI, CPI, GDP, Monetary Base |