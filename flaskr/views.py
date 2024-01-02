from celery.result import AsyncResult
from flask import Blueprint, request, render_template, url_for

from . import tasks
from flaskr.models import db, KnowledgeBase

bp = Blueprint("tasks", __name__, url_prefix="/tasks")



@bp.get("/add")
def render_add():
    
    return render_template('add.html')

@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }

@bp.get("/result/json/<id>")
def task_result_json(id: str):
    result = AsyncResult(id)
    response = {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
    return jsonify(response)

@bp.post("/add")
def add() -> dict[str, object]:
    a = request.form.get("a", type=int)
    b = request.form.get("b", type=int)
    result = tasks.add.delay(a, b)
    return {"result_id": result.id}

@bp.get("/kbs/add")
def render_add_kbs():
    
    return render_template('add-kb.html')

@bp.post("/kbs/add")
def add_kb() -> dict[str, object]:

    title = request.form.get("title")

    new_kb = KnowledgeBase(title=title)
    db.session.add(new_kb)
    db.session.commit()
    kb_id = new_kb.id


    result = tasks.create_kb.delay(kb_id)

    return {"result_id": result.id}

@bp.post("/block")
def block() -> dict[str, object]:
    result = tasks.block.delay()
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    result = tasks.process.delay(total=request.form.get("total", type=int))
    return {"result_id": result.id}