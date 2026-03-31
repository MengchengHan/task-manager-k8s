from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import psycopg2
import psycopg2.extras
import os
import time

app = FastAPI(title="Task Manager")
templates = Jinja2Templates(directory="templates")

# ── Configuración DB ────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "db"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
    "dbname":   os.environ.get("DB_NAME", "tasks_db"),
    "user":     os.environ.get("DB_USER", "taskuser"),
    "password": os.environ.get("DB_PASSWORD", "taskpass"),
}

def get_conn():
    for _ in range(10):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a la base de datos")

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          SERIAL PRIMARY KEY,
            title       TEXT    NOT NULL,
            description TEXT,
            status      TEXT    NOT NULL DEFAULT 'pending',
            created_at  TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ── Modelos ─────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "pending"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# ── Vistas HTML ─────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ── API CRUD ────────────────────────────────────────────────────
@app.get("/api/tasks")
def list_tasks():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()
    cur.close(); conn.close()
    return {"tasks": [dict(t) for t in tasks]}

@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    if task.status not in ("pending", "done"):
        raise HTTPException(400, "status debe ser 'pending' o 'done'")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) RETURNING *",
        (task.title, task.description, task.status)
    )
    new = dict(cur.fetchone())
    conn.commit(); cur.close(); conn.close()
    return new

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
    existing = cur.fetchone()
    if not existing:
        cur.close(); conn.close()
        raise HTTPException(404, "Tarea no encontrada")

    new_title  = task.title       if task.title       is not None else existing["title"]
    new_desc   = task.description if task.description is not None else existing["description"]
    new_status = task.status      if task.status      is not None else existing["status"]

    if new_status not in ("pending", "done"):
        cur.close(); conn.close()
        raise HTTPException(400, "status debe ser 'pending' o 'done'")

    cur.execute(
        "UPDATE tasks SET title=%s, description=%s, status=%s WHERE id=%s RETURNING *",
        (new_title, new_desc, new_status, task_id)
    )
    updated = dict(cur.fetchone())
    conn.commit(); cur.close(); conn.close()
    return updated

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s RETURNING id", (task_id,))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        raise HTTPException(404, "Tarea no encontrada")
    return {"deleted": task_id}

@app.get("/health")
def health():
    return {"status": "ok"}
