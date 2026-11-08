import sqlite3

DB_FILE = "tasks.db"


def get_connection():
    """Connects to SQLite and enables foreign keys."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes the database schema using schema.sql."""
    with open("schema.sql", "r") as f:
        schema_script = f.read()

    with get_connection() as conn:
        conn.executescript(schema_script)
    print("Database initialized successfully!")


def add_category(name):
    """Inserts a new category into the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (name) VALUES (?)", (name,)
            )
            conn.commit()
            print(f"Category '{name}' added!")
        except sqlite3.IntegrityError:
            print(f"Category '{name}' already exists.")


def add_task(title, category_id=None):
    """Inserts a new task."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, category_id) VALUES (?, ?)",
            (title, category_id),
        )
        conn.commit()
        print(f"Task '{title}' created!")


def list_tasks():
    """Queries and prints all tasks along with their category names using INNER JOIN."""
    query = """
    SELECT 
        t.task_id, 
        t.title, 
        t.status, 
        COALESCE(c.name, 'No Category') AS category_name
    FROM tasks t
    LEFT JOIN categories c ON t.category_id = c.category_id;
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute(query).fetchall()

        print("\n--- YOUR TASKS ---")
        if not rows:
            print("No tasks found.")
            return

        for row in rows:
            task_id, title, status, category = row
            status_flag = "[X]" if status == "Completed" else "[ ]"
            print(
                f"{task_id}. {status_flag} {title} (Category: {category})"
            )
        print("------------------\n")


def mark_completed(task_id):
    """Updates a task status to 'Completed'."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'Completed' WHERE task_id = ?",
            (task_id,),
        )
        conn.commit()
        print(f"Task #{task_id} marked as completed!")


def delete_task(task_id):
    """Deletes a task by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        print(f"Task #{task_id} deleted!")


if __name__ == "__main__":
    # 1. Initialize tables
    init_db()

    # 2. Add default categories
    add_category("Work")
    add_category("Personal")

    # 3. Add sample tasks (Category ID 1 = Work, 2 = Personal)
    add_task("Finish SQL setup in VS Code", category_id=1)
    add_task("Buy groceries", category_id=2)

    # 4. View all tasks with joined category names
    list_tasks()

    # 5. Complete a task and view again
    mark_completed(1)
    list_tasks()