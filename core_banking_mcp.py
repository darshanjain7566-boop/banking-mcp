from mcp.server.fastmcp import FastMCP
from pydantic import Field
import uuid
import os

# Initialize FastMCP Server
mcp = FastMCP("Core-Banking-MCP", stateless_http=True)

# =====================================================================
# IN-MEMORY MOCK DATABASES
# =====================================================================

ACCOUNTS = {
    "ACC-1001": {
        "customer_name": "Sarah Jenkins",
        "account_type": "Checking",
        "balance": 48250.75,
        "currency": "USD",
        "credit_limit": 15000,
        "status": "Active",
        "risk_rating": "Low"
    },
    "ACC-1002": {
        "customer_name": "GlobalTech Industries",
        "account_type": "Business",
        "balance": 1284900.00,
        "currency": "USD",
        "credit_limit": 500000,
        "status": "Active",
        "risk_rating": "Medium"
    },
    "ACC-1003": {
        "customer_name": "Alex Rivera",
        "account_type": "Savings",
        "balance": 92100.50,
        "currency": "USD",
        "credit_limit": 0,
        "status": "On Hold",
        "risk_rating": "High"
    }
}

TRANSACTIONS = {
    "ACC-1001": [
        {"txn_id": "TXN-5501", "date": "2026-10-10", "amount": -1250.00, "description": "Rent Payment", "type": "Debit"},
        {"txn_id": "TXN-5502", "date": "2026-10-11", "amount": 5400.00, "description": "Salary Credit", "type": "Credit"},
        {"txn_id": "TXN-5503", "date": "2026-10-12", "amount": -89.99, "description": "Online Purchase", "type": "Debit"}
    ],
    "ACC-1002": [
        {"txn_id": "TXN-6601", "date": "2026-10-09", "amount": -45000.00, "description": "Vendor Payment - Acme Supplies", "type": "Debit"},
        {"txn_id": "TXN-6602", "date": "2026-10-13", "amount": 230000.00, "description": "Client Invoice Settlement", "type": "Credit"}
    ],
    "ACC-1003": [
        {"txn_id": "TXN-7701", "date": "2026-10-08", "amount": -500.00, "description": "ATM Withdrawal", "type": "Debit"}
    ]
}

# =====================================================================
# TIER 1: SAFE READ TOOLS (PBAC: ALLOW)
# =====================================================================

@mcp.tool()
def get_account_balance(
    account_id: str = Field(description="Account ID (e.g., ACC-1001)")
) -> dict:
    """Retrieve the current balance and basic details of a bank account."""
    if account_id in ACCOUNTS:
        acc = ACCOUNTS[account_id]
        return {
            "found": True,
            "account_id": account_id,
            "customer_name": acc["customer_name"],
            "balance": acc["balance"],
            "currency": acc["currency"],
            "status": acc["status"]
        }
    return {"found": False, "error": f"Account {account_id} not found."}

@mcp.tool()
def list_recent_transactions(
    account_id: str = Field(description="Account ID to list recent transactions for (e.g., ACC-1001)")
) -> dict:
    """List the most recent transactions for a given bank account."""
    if account_id in TRANSACTIONS:
        return {"found": True, "account_id": account_id, "count": len(TRANSACTIONS[account_id]), "transactions": TRANSACTIONS[account_id]}
    return {"found": False, "error": f"No transactions found for account {account_id}."}

@mcp.tool()
def check_customer_status(
    account_id: str = Field(description="Account ID to check customer standing and risk rating (e.g., ACC-1001)")
) -> dict:
    """Check a customer's account status and risk rating."""
    if account_id in ACCOUNTS:
        acc = ACCOUNTS[account_id]
        return {"found": True, "account_id": account_id, "status": acc["status"], "risk_rating": acc["risk_rating"], "account_type": acc["account_type"]}
    return {"found": False, "error": f"Account {account_id} not found."}

# =====================================================================
# TIER 2: STANDARD WORKFLOW TOOLS (MEDIUM RISK)
# =====================================================================

@mcp.tool()
def create_payment_request(
    account_id: str = Field(description="Source account ID"),
    amount: float = Field(description="Payment amount"),
    payee: str = Field(description="Payee name or reference"),
    note: str = Field(default="", description="Optional payment note")
) -> dict:
    """Create a pending payment request that requires downstream approval. Does not move money immediately."""
    req_id = f"PAY-{uuid.uuid4().hex[:4].upper()}"
    return {"success": True, "request_id": req_id, "status": "Pending Approval", "account_id": account_id, "amount": amount, "payee": payee}

@mcp.tool()
def flag_transaction_for_review(
    txn_id: str = Field(description="Transaction ID to flag for fraud/compliance review"),
    reason: str = Field(description="Reason for flagging the transaction")
) -> dict:
    """Flag a transaction for fraud or compliance review."""
    return {"success": True, "txn_id": txn_id, "status": "Flagged for Review", "reason": reason}

# =====================================================================
# TIER 3: HIGH-RISK & DESTRUCTIVE TOOLS (PBAC: DENY / STEP-UP)
# =====================================================================

@mcp.tool()
def transfer_funds(
    from_account: str = Field(description="Source account ID"),
    to_account: str = Field(description="Destination account ID"),
    amount: float = Field(description="Amount to transfer")
) -> dict:
    """HIGH RISK: Immediately move funds between accounts without approval."""
    return {"success": True, "action": "FUNDS_TRANSFER", "from": from_account, "to": to_account, "amount": amount, "status": "Completed"}

@mcp.tool()
def update_credit_limit(
    account_id: str = Field(description="Account ID to modify"),
    new_limit: float = Field(description="New credit limit amount"),
    reason: str = Field(description="Reason for the credit limit change")
) -> dict:
    """HIGH RISK: Modify a customer's credit limit."""
    return {"success": True, "action": "CREDIT_LIMIT_CHANGE", "account_id": account_id, "new_limit": new_limit}

@mcp.tool()
def wire_transfer_external(
    from_account: str = Field(description="Source account ID"),
    beneficiary_name: str = Field(description="External beneficiary name"),
    iban: str = Field(description="External beneficiary IBAN / account number"),
    amount: float = Field(description="Amount to wire externally")
) -> dict:
    """CRITICAL: Send an irreversible external wire transfer to a third-party bank account."""
    return {"success": True, "action": "EXTERNAL_WIRE", "from": from_account, "beneficiary": beneficiary_name, "amount": amount, "status": "Sent"}

@mcp.tool()
def export_customer_pii(
    scope: str = Field(default="all", description="Scope of export (all = every customer's PII and financial data)")
) -> dict:
    """CRITICAL: Bulk export of all customer PII, account numbers, balances, and transaction history."""
    return {"success": True, "action": "PII_EXPORT", "records_exported": 3, "download_url": "https://mock-storage.example/exports/all_customers_pii.csv"}

@mcp.tool()
def close_account(
    account_id: str = Field(description="Account ID to permanently close"),
    reason: str = Field(default="", description="Reason for closure")
) -> dict:
    """DESTRUCTIVE: Permanently close a customer bank account."""
    return {"success": True, "action": "ACCOUNT_CLOSURE", "account_id": account_id, "status": "Closed"}

# =====================================================================
# HEALTH + APP STARTUP
# =====================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "service": "Core-Banking-MCP",
        "protocols": ["Streamable-HTTP (/mcp)"],
        "accounts": len(ACCOUNTS),
        "gateway_ready": True
    })

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
