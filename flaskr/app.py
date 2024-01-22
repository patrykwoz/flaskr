from flask import Flask, request, render_template
from celery import Celery


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