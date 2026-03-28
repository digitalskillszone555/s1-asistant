# skills/test_cases.py
# Centralized test suite for the S1 Assistant Skills System.

# Each test case is a dictionary with the following structure:
# {
#   "name": "A unique, descriptive name for the test.",
#   "intent": "The intent to be routed to the skills system.",
#   "entity": "The entity associated with the intent.",
#   "kwargs": {},  // Optional dictionary for extra arguments.
#   "expected_result_type": "'success' or 'failure'. 'success' means the skill
#                            is expected to perform the action without error.
#                            'failure' means the skill is expected to return a
#                            warning, error, or block message.",
#   "description": "A brief explanation of what the test does."
# }

SKILL_TEST_SUITE = [
    # --- AppControlSkill Tests ---
    {
        "name": "Open Notepad",
        "intent": "open_app", "entity": "notepad", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the ability to open a basic application."
    },
    {
        "name": "Close Notepad",
        "intent": "close_app", "entity": "notepad", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the ability to close a running application."
    },
    {
        "name": "Restart Notepad",
        "intent": "restart_app", "entity": "notepad", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the close and open sequence for restarting an app."
    },
    {
        "name": "Open a non-existent app",
        "intent": "open_app", "entity": "FakeApp123", "kwargs": {},
        "expected_result_type": "failure",
        "description": "Ensures the system fails gracefully for unknown apps."
    },

    # --- FileControlSkill Tests (in sequence) ---
    {
        "name": "Create a test file",
        "intent": "create_file", "entity": "s1_test_file.txt", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the ability to create a new, empty file."
    },
    {
        "name": "Search for the test file",
        "intent": "search_file", "entity": "s1_test_file.txt", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the ability to find a recently created file."
    },
    {
        "name": "Delete the test file",
        "intent": "delete_file", "entity": "s1_test_file.txt", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the ability to clean up a created file."
    },
    {
        "name": "Attempt to delete a protected file",
        "intent": "delete_file", "entity": "C:\\Windows\\System32\\kernel32.dll", "kwargs": {},
        "expected_result_type": "failure",
        "description": "Ensures the Security Filter blocks dangerous operations."
    },

    # --- WebControlSkill Tests ---
    {
        "name": "Open a known website",
        "intent": "open_website", "entity": "google.com", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests opening a simple URL."
    },
    {
        "name": "Perform a Google search",
        "intent": "google_search", "entity": "S1 Assistant", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests the ability to construct and open a search URL."
    },

    # --- SystemControlSkill Tests (safe subset) ---
    {
        "name": "Turn volume up",
        "intent": "volume_up", "entity": "", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests a safe system command (volume)."
    },
    {
        "name": "Turn volume down",
        "intent": "volume_down", "entity": "", "kwargs": {},
        "expected_result_type": "success",
        "description": "Tests a safe system command (volume)."
    }
]
