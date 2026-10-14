# Core Banking MCP Server — Zuma Demo

A mock Core Banking MCP server for the Saviynt Zuma Access Gateway demo. Simulates a
financial-services AI agent scenario with safe, medium, and critical-risk tools.

## Tools (10)

### Tier 1 — Safe (PBAC: ALLOW)
- `get_account_balance` — read account balance
- `list_recent_transactions` — read transaction history
- `check_customer_status` — read status & risk rating

### Tier 2 — Medium (approval workflow)
- `create_payment_request` — pending payment (needs approval)
- `flag_transaction_for_review` — flag for fraud/compliance

### Tier 3 — Critical (PBAC: DENY)
- `transfer_funds` — move money between accounts
- `update_credit_limit` — change credit limit
- `wire_transfer_external` — irreversible external wire
- `export_customer_pii` — bulk PII export
- `close_account` — permanently close account

## Local test

```bash
pip install -r requirements.txt
python core_banking_mcp.py
# then: curl http://localhost:8000/health
```

## Deploy to Koyeb (free, never sleeps)

1. Push this folder to a GitHub repo
2. Go to app.koyeb.com → Create App → GitHub → select the repo
3. Build: Buildpack (auto-detects Python)
4. Run command: `python core_banking_mcp.py`
5. Set the exposed port to `8000` (or let Koyeb inject `$PORT`)
6. Health check path: `/health`
7. Deploy → you get a public URL like `https://core-banking-mcp-<org>.koyeb.app`

MCP endpoint will be: `https://<your-koyeb-url>/mcp/`

## Attach to Zuma Gateway

- Target Type: MCP
- Base URL: `https://<your-koyeb-url>`
- MCP Endpoint: `/mcp`
- Auth: NONE (public demo server) or API key as needed

## Suggested PBAC policy

Allow: `get_account_balance`, `list_recent_transactions`, `check_customer_status`, `create_payment_request`
Deny: `transfer_funds`, `update_credit_limit`, `wire_transfer_external`, `export_customer_pii`, `close_account`
Default-deny: `flag_transaction_for_review`
