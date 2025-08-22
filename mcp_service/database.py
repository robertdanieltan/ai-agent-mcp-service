import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from .models import Project, ProjectCreate, Task, TaskCreate, TaskUpdate, TaskStatus, TaskSummary


class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'task_management'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def create_project(self, project: ProjectCreate) -> Project:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                INSERT INTO projects (name, description)
                VALUES (%s, %s)
                RETURNING id, name, description, created_at, updated_at
                """,
                (project.name, project.description)
            )
            result = cursor.fetchone()
            conn.commit()
            return Project(**dict(result))

    def get_all_projects(self) -> List[Project]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at FROM projects ORDER BY created_at DESC"
            )
            results = cursor.fetchall()
            return [Project(**dict(row)) for row in results]

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at FROM projects WHERE id = %s",
                (project_id,)
            )
            result = cursor.fetchone()
            return Project(**dict(result)) if result else None

    def create_task(self, task: TaskCreate) -> Task:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                INSERT INTO tasks (title, description, status, priority, project_id, assigned_to)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, title, description, status, priority, project_id, assigned_to, created_at, updated_at
                """,
                (task.title, task.description, task.status, task.priority, task.project_id, task.assigned_to)
            )
            result = cursor.fetchone()
            conn.commit()
            return Task(**dict(result))

    def update_task_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                UPDATE tasks SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, title, description, status, priority, project_id, assigned_to, created_at, updated_at
                """,
                (status, task_id)
            )
            result = cursor.fetchone()
            conn.commit()
            return Task(**dict(result)) if result else None

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, title, description, status, priority, project_id, assigned_to, created_at, updated_at
                FROM tasks WHERE status = %s ORDER BY created_at DESC
                """,
                (status,)
            )
            results = cursor.fetchall()
            return [Task(**dict(row)) for row in results]

    def get_project_tasks(self, project_id: int) -> List[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, title, description, status, priority, project_id, assigned_to, created_at, updated_at
                FROM tasks WHERE project_id = %s ORDER BY created_at DESC
                """,
                (project_id,)
            )
            results = cursor.fetchall()
            return [Task(**dict(row)) for row in results]

    def get_task_summary(self) -> TaskSummary:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
                FROM tasks
                """
            )
            result = cursor.fetchone()
            return TaskSummary(**dict(result))

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, title, description, status, priority, project_id, assigned_to, created_at, updated_at
                FROM tasks WHERE id = %s
                """,
                (task_id,)
            )
            result = cursor.fetchone()
            return Task(**dict(result)) if result else None