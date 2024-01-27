import time

from celery import shared_task, Task

from flaskr.models import db, KnowledgeBase
from flaskr.ml_functions import resource_cache
from flaskr.ml_functions.class_kb import from_text_to_kb

tokenizer = resource_cache.tokenizer
model = resource_cache.model

@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    time.sleep(5)
    return a + b

@shared_task()
def block() -> None:
    time.sleep(5)

@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    return {"current": total, "total": total}

@shared_task(ignore_result=False, time_limit=180)
def create_kb(kb_id: int):
    try:
        knowledge_base = db.session.query(KnowledgeBase).get(kb_id)

        if knowledge_base:
            kb = from_text_to_kb(text=knowledge_base.title, article_url='http://valid-url.com', verbose=False, model=model, tokenizer=tokenizer)
            
            knowledge_base.json_object = kb.to_json()

            db.session.commit()

            return kb_id
        else:
            raise ValueError('Could not find the knowledge_base')

    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        return str(e) 