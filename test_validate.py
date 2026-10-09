"""Local tests for the routing logic. Run from this folder: python3 test_validate.py

The Zapier entry point at the bottom of validate.py needs `input_data`,
so we define a dummy before importing.
"""
import builtins
import importlib.util
import pathlib

builtins.input_data = {}  # satisfies the Zapier entry point at import time

path = pathlib.Path(__file__).resolve().parent / "validate.py"
spec = importlib.util.spec_from_file_location("validate", path)
validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate)
triage = validate.triage


def case(name, data, routed_to, status):
    out = triage(data)
    ok = out["routed_to"] == routed_to and out["processing_status"] == status
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {out['routed_to']} / {out['processing_status']}")
    return ok


results = [
    case("REQ-001 billing dispute",
         {"category": "billing_dispute", "urgency": "medium", "injection_suspected": "false"},
         "STANDARD_QUEUE", "OK"),
    case("REQ-002 fraud, high urgency",
         {"category": "fraud_or_security", "urgency": "high", "injection_suspected": "false"},
         "URGENT_QUEUE", "OK"),
    case("REQ-003 general enquiry",
         {"category": "general_enquiry", "urgency": "low", "injection_suspected": "false"},
         "STANDARD_QUEUE", "OK"),
    case("REQ-004 injection flagged",
         {"category": "other", "urgency": "low", "injection_suspected": "true"},
         "SECURITY_REVIEW", "FLAGGED_INJECTION"),
    case("fraud category with low urgency still urgent",
         {"category": "fraud_or_security", "urgency": "low", "injection_suspected": "false"},
         "URGENT_QUEUE", "OK"),
    case("injection overrides high urgency",
         {"category": "fraud_or_security", "urgency": "high", "injection_suspected": "true"},
         "SECURITY_REVIEW", "FLAGGED_INJECTION"),
    case("invalid category falls back and needs review",
         {"category": "refund_please", "urgency": "low", "injection_suspected": "false"},
         "STANDARD_QUEUE", "NEEDS_REVIEW"),
    case("invalid urgency falls back and needs review",
         {"category": "complaint", "urgency": "URGENT!!", "injection_suspected": "false"},
         "STANDARD_QUEUE", "NEEDS_REVIEW"),
    case("missing fields do not crash",
         {},
         "STANDARD_QUEUE", "NEEDS_REVIEW"),
    case("case and whitespace are normalised",
         {"category": " Billing_Dispute ", "urgency": " HIGH ", "injection_suspected": "False"},
         "URGENT_QUEUE", "OK"),
]

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
