from flask import Flask, request, render_template
from celery import Celery

from flaskr.models import db, KnowledgeBase


app = Flask(__name__)
celery = Celery(app.name, broker='redis://localhost:6379/0')

@app.route('/', methods=["GET"])
def main():
    return f"Hello!"

@app.route('/task/app', methods=["POST", "GET"])
def start_ml_task():
    if request.method == "POST":
        a = request.form.get("a", type=int)
        b = request.form.get("b", type=int)
        task = celery.send_task('celery_worker.add', kwargs={'a': a, 'b':b})
        return f"Task ID: {task.id}"

    return render_template('add-test.html')

@app.route("/kbs/add")
def render_add_kb():
    
    return render_template('add-kb.html')

@app.route("/kbs/add")
def add_kb() -> dict[str, object]:

    title = request.form.get("title")

    new_kb = KnowledgeBase(title=title)
    db.session.add(new_kb)
    db.session.commit()
    kb_id = new_kb.id


    result = celery.send_task('celery_worker.create_kb', kwargs={kb_id})

    return {"result_id": result.id}