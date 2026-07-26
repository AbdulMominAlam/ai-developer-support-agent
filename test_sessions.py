from sessions import (
    delete_expired_sessions,
    delete_session,
    get_session_response_id,
    save_session_response_id,
)


TEST_SESSION_ID = "session-001"


print("\n--- Test 1: Session does not exist yet ---")
response_id = get_session_response_id(TEST_SESSION_ID)
print(response_id)


print("\n--- Test 2: Save a response ID ---")
save_session_response_id(
    session_id=TEST_SESSION_ID,
    response_id="resp_test_123",
)
print("Session saved successfully.")


print("\n--- Test 3: Retrieve the saved response ID ---")
response_id = get_session_response_id(TEST_SESSION_ID)
print(response_id)


print("\n--- Test 4: Update the same session ---")
save_session_response_id(
    session_id=TEST_SESSION_ID,
    response_id="resp_test_456",
)
print("Session updated successfully.")


print("\n--- Test 5: Retrieve the updated response ID ---")
response_id = get_session_response_id(TEST_SESSION_ID)
print(response_id)


print("\n--- Test 6: Delete expired sessions ---")
deleted_count = delete_expired_sessions()
print(f"Deleted {deleted_count} expired sessions.")


print("\n--- Test 7: Delete the test session ---")
was_deleted = delete_session(TEST_SESSION_ID)
print(f"Session deleted: {was_deleted}")


print("\n--- Test 8: Confirm the session is gone ---")
response_id = get_session_response_id(TEST_SESSION_ID)
print(response_id)