from datetime import datetime, timedelta, timezone

from database import get_connection


# A session is considered inactive after 24 hours
SESSION_EXPIRY_HOURS = 24


def get_session_response_id(session_id: str):
    """
    Get the latest OpenAI response ID stored for a session.

    Returns:
        response_id if the session exists and is still active
        None if the session does not exist or has expired
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            # Find the session using its session ID
            cursor.execute(
                """
                SELECT response_id, updated_at
                FROM sessions
                WHERE session_id = %s;
                """,
                (session_id,),
            )

            session = cursor.fetchone()

    # No session was found
    if session is None:
        return None

    response_id = session[0]
    updated_at = session[1]

    # PostgreSQL may return a datetime without timezone information.
    # We compare it using UTC.
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)

    expiry_time = updated_at + timedelta(hours=SESSION_EXPIRY_HOURS)

    # If the session has not been used for 24 hours, consider it expired
    if current_time > expiry_time:
        delete_session(session_id)
        return None

    return response_id


def save_session_response_id(
    session_id: str,
    response_id: str,
) -> None:
    """
    Create a new session or update an existing session.

    The latest OpenAI response ID is stored for the session.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    response_id,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )

                ON CONFLICT (session_id)
                DO UPDATE SET
                    response_id = EXCLUDED.response_id,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (
                    session_id,
                    response_id,
                ),
            )

        connection.commit()


def delete_session(session_id: str) -> bool:
    """
    Delete one session from PostgreSQL.

    Returns True if a session was deleted.
    Returns False if the session did not exist.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM sessions
                WHERE session_id = %s;
                """,
                (session_id,),
            )

            deleted_count = cursor.rowcount

        connection.commit()

    return deleted_count > 0


def delete_expired_sessions() -> int:
    """
    Delete all sessions that have been inactive for more than 24 hours.

    Returns the number of deleted sessions.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM sessions
                WHERE updated_at <
                    CURRENT_TIMESTAMP - INTERVAL '24 hours';
                """
            )

            deleted_count = cursor.rowcount

        connection.commit()

    return deleted_count