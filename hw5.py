# Необходимо создать API для управления списком задач. Каждая задача должна содержать заголовок и описание.
# Для каждой задачи должна быть возможность указать статус (выполнена/не выполнена).
#
# API должен содержать следующие конечные точки:
# — GET /tasks — возвращает список всех задач.
# — GET /tasks/{id} — возвращает задачу с указанным идентификатором.
# — POST /tasks — добавляет новую задачу.
# — PUT /tasks/{id} — обновляет задачу с указанным идентификатором.
# — DELETE /tasks/{id} — удаляет задачу с указанным идентификатором.
#
# Для каждой конечной точки необходимо проводить валидацию данных запроса и ответа.
# Для этого использовать библиотеку Pydantic.

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    description: str
    is_completed: Optional[bool] = False
    is_deleted: Optional[bool] = False


tasks: list[Task] = []

tasks.append(Task(id=1, title="First task", description="First task description"))
tasks.append(Task(id=2, title="Second task", description="Second task description", is_completed=True))
tasks.append(Task(id=3, title="Third task", description="Third task description"))
tasks.append(Task(id=4, title="Deleted task", description="Deleted task description", is_deleted=True))


@app.get("/")
async def root():
    return {"message": "Welcome"}


@app.get("/tasks", response_model=list[Task])
async def show_all_tasks():
    existing_tasks = [task for task in tasks if not task.is_deleted]
    return existing_tasks


@app.get("/tasks/{id}", response_model=Task)
async def show_task(id: int):
    result = next((task for task in tasks if task.id == id), None)
    return result if result and not result.is_deleted else JSONResponse(content="Not found", status_code=404)


@app.post("/tasks")
async def create_task(new_task: Task):
    non_unique = next((task for task in tasks if task.id == new_task.id), None)
    if non_unique or new_task.id <= 0:
        return JSONResponse(content="Invalid ID", status_code=422)
    tasks.append(new_task)
    return JSONResponse(content="New task was created", status_code=200)


@app.put("/tasks/{id}")
async def update_task(id: int, updated_task: Task):
    task = next((task for task in tasks if task.id == id), None)
    if task:
        task.title = updated_task.title
        task.description = updated_task.description
        task.status = updated_task.status if updated_task.status else task.status
    return task if task else JSONResponse(content="Not found", status_code=404)


@app.delete("/tasks/{id}")
async def delete_task(id: int):
    task = next((task for task in tasks if task.id == id), None)
    if task:
        task.is_deleted = True
        msg = f'Task with ID {task.id} and title {task.title} was removed'
        return JSONResponse(content=msg, status_code=200)
    return JSONResponse(content="Not found", status_code=404)
