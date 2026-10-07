"""Validation and routing logic for the Inbound Request Triage Zap.

This is the body of the "Code by Zapier (Run Python)" step (step 3).

Design principle: the LLM only reads and labels messy text. Everything that
decides what happens next lives here, as plain deterministic code.

In Zapier, `input_data` is injected by the platform and the result must be
assigned to a variable called `output`. To make this file testable locally,
the logic is wrapped in `triage()`, and the Zapier-specific lines are at the
bottom. When pasting into Zapier, paste everything and keep the last two lines.
"""

ALLOWED_CATEGORIES = {
    "billing_dispute",
    "fraud_or_security",
    "account_access",
    "policy_or_claims_query",
    "complaint",
    "general_enquiry",
    "other",
}
ALLOWED_URGENCY = {"low", "medium", "high"}


def triage(data):
    category = str(data.get("category", "")).strip().lower()
    urgency = str(data.get("urgency", "")).strip().lower()
    injection = str(data.get("injection_suspected", "")).strip().lower() == "true"
    reference = str(data.get("extracted_reference", "")).strip()
    summary = str(data.get("summary", "")).strip()

    status = "OK"

    # 1. Validate: never trust the model's output blindly.
    #    Anything outside the allowlist falls back to a safe default
    #    and is marked for a human to look at.
    if category not in ALLOWED_CATEGORIES:
        category = "other"
        status = "NEEDS_REVIEW"
    if urgency not in ALLOWED_URGENCY:
        urgency = "medium"
        status = "NEEDS_REVIEW"

    # 2. Route: plain rules, no AI involved.
    #    The injection flag is checked first, so it overrides everything else,
    #    including whatever urgency the model returned.
    if injection:
        routed_to = "SECURITY_REVIEW"
        status = "FLAGGED_INJECTION"
    elif urgency == "high" or category == "fraud_or_security":
        routed_to = "URGENT_QUEUE"
    else:
        routed_to = "STANDARD_QUEUE"

    return {
        "category": category,
        "urgency": urgency,
        "summary": summary,
        "extracted_reference": reference,
        "routed_to": routed_to,
        "processing_status": status,
    }


# --- Zapier entry point (keep this line when pasting into the Code step) ---
output = triage(input_data)
