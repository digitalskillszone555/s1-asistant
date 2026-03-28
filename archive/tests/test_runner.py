# skills/test_runner.py
# An enhanced test harness to validate the skills system using a centralized test suite.

import time
from skills.router import route_skill
from skills.test_cases import SKILL_TEST_SUITE

def _validate_test_suite():
    """Performs self-validation on the imported test suite."""
    print("[VALIDATION] Validating test suite...")
    names = set()
    errors = []
    for i, test in enumerate(SKILL_TEST_SUITE):
        # 1. Check for required keys
        required_keys = ["name", "intent", "entity", "expected_result_type", "description"]
        missing_keys = [key for key in required_keys if key not in test]
        if missing_keys:
            errors.append(f"Test #{i} ('{test.get('name', 'Unnamed')}') is missing keys: {missing_keys}")
        
        # 2. Check for duplicate names
        name = test.get("name")
        if name in names:
            errors.append(f"Duplicate test name found: '{name}'")
        if name:
            names.add(name)

    if errors:
        print("❌ VALIDATION FAILED:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✔ VALIDATION PASSED: Test suite is well-formed.\n")
    return True

def run_all_skill_tests():
    """
    Loads test cases from the central suite, validates them, runs them,
    and provides a final system status.
    """
    print("="*50)
    print("  S1 ASSISTANT - ENHANCED SKILLS TEST HARNESS")
    print("="*50)

    if not _validate_test_suite():
        print("Aborting tests due to validation errors.")
        return False

    passed_tests = 0
    failed_tests = []

    for test in SKILL_TEST_SUITE:
        name = test["name"]
        intent = test["intent"]
        entity = test["entity"]
        kwargs = test.get("kwargs", {})
        expected = test["expected_result_type"]

        print(f"[TEST] Running: {name}...")
        
        try:
            result_msg = route_skill(intent=intent, entity=entity, **kwargs)
            
            # Determine if the actual result was a success or failure
            is_failure_result = not result_msg or any(word in result_msg.lower() for word in ["sorry", "fail", "error", "blocked", "unknown"])
            actual_result_type = "failure" if is_failure_result else "success"

            # Check if the actual result matches the expectation
            if actual_result_type == expected:
                print(f"  ✔ PASS: Expected '{expected}', got '{actual_result_type}'. (Result: '{result_msg}')")
                passed_tests += 1
            else:
                reason = f"Expected '{expected}' but got '{actual_result_type}'. (Result: '{result_msg}')"
                print(f"  ❌ FAIL: {reason}")
                failed_tests.append({"name": name, "reason": reason})

        except Exception as e:
            reason = f"An unexpected exception occurred: {e}"
            print(f"  ❌ FAIL: {reason}")
            failed_tests.append({"name": name, "reason": reason})
        
        time.sleep(0.5) # Small delay

    # --- FINAL REPORT ---
    print("\n" + "="*50)
    print("  TEST SUMMARY")
    print("="*50)
    print(f"Total Tests: {len(SKILL_TEST_SUITE)}")
    print(f"Passed:      {passed_tests}")
    print(f"Failed:      {len(failed_tests)}")
    
    if failed_tests:
        print("\n--- FAILED TESTS ---")
        for failure in failed_tests:
            print(f"- {failure['name']}: {failure['reason']}")

    print("\n" + "="*50)
    if not failed_tests:
        print("  ✔ SKILLS SYSTEM VERIFIED")
    else:
        print("  ❌ SKILLS SYSTEM UNSTABLE")
    print("="*50)

    return len(failed_tests) == 0
