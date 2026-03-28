# root/tests/test_runner.py
# Production test harness for the Unified Action Engine.

import time
from core.action_engine import get_action_engine
from root.tests.test_cases import SKILL_TEST_SUITE

def run_all_skill_tests():
    """
    Validates the ActionEngine against the centralized test suite.
    """
    print("="*50)
    print("  S1 ASSISTANT - UNIFIED ACTION ENGINE TEST")
    print("="*50)

    engine = get_action_engine()
    passed_tests = 0
    failed_tests = []

    for test in SKILL_TEST_SUITE:
        name = test["name"]
        intent = test["intent"]
        entity = test["entity"]
        extra_data = test.get("kwargs", {}).get("extra_data")
        expected = test["expected_result_type"]

        print(f"[TEST] Running: {name}...")
        
        try:
            # Use the new ActionEngine
            result_msg = engine.execute({"intent": intent, "entity": entity, "extra_data": extra_data})
            
            is_failure_result = not result_msg or any(word in result_msg.lower() for word in ["sorry", "fail", "error", "blocked", "unknown"])
            actual_result_type = "failure" if is_failure_result else "success"

            if actual_result_type == expected:
                print(f"  ✔ PASS: Expected '{expected}', got '{actual_result_type}'.")
                passed_tests += 1
            else:
                reason = f"Expected '{expected}' but got '{actual_result_type}'. (Result: '{result_msg}')"
                print(f"  ❌ FAIL: {reason}")
                failed_tests.append({"name": name, "reason": reason})

        except Exception as e:
            failed_tests.append({"name": name, "reason": str(e)})
        
        time.sleep(0.1)

    print("\n" + "="*50)
    print(f"Summary: {passed_tests}/{len(SKILL_TEST_SUITE)} Passed.")
    print("="*50)

    return len(failed_tests) == 0

if __name__ == "__main__":
    run_all_skill_tests()
