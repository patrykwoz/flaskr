import time

from celery import shared_task
from celery import Task
from .models import KnowledgeBase

from flaskr.models import db, KnowledgeBase




@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    time.sleep(5)
    return a + b

@shared_task(ignore_result=False)
def create_kb(kb_id: int) -> int:

    knowledge_base = db.session.get(KnowledgeBase, kb_id)

    # kb = class_kb.kb_from_text(knowledge_base.title, verbose=False)
    # knowledge_base.json_object = kb.to_json()

    json_obj = {
        "text":f"{knowledge_base.title}",
    }

    db.session.commit
    
    return kb_id

@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    return {"current": total, "total": total}