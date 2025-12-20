import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "diagautoclinic_users.db"
SUPERUSER_USERNAME = "superuser"

def unlock_superuser():
    """
    Unlocks the superuser account by updating its status and resetting lock-related fields.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Check if the user exists
            cursor.execute("SELECT status FROM users WHERE username = ?", (SUPERUSER_USERNAME,))
            result = cursor.fetchone()

            if not result:
                logging.error(f"Superuser '{SUPERUSER_USERNAME}' not found in the database.")
                return

            current_status = result[0]
            logging.info(f"Current status of '{SUPERUSER_USERNAME}': {current_status}")

            if current_status == "active":
                logging.info(f"Superuser '{SUPERUSER_USERNAME}' is already active. No changes needed.")
                return

            # Unlock the account
            cursor.execute("""
                UPDATE users
                SET
                    status = 'active',
                    login_attempts = 0,
                    locked_until = NULL
                WHERE
                    username = ?
            """, (SUPERUSER_USERNAME,))

            conn.commit()

            # Verify the update
            cursor.execute("SELECT status FROM users WHERE username = ?", (SUPERUSER_USERNAME,))
            new_status = cursor.fetchone()[0]

            if new_status == 'active':
                logging.info(f"Successfully unlocked the superuser account '{SUPERUSER_USERNAME}'.")
            else:
                logging.error(f"Failed to unlock the superuser account. Status is still '{new_status}'.")

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    unlock_superuser()
