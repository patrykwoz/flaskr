from celery import Celery
import time
import os

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from models import db, KnowledgeBase

from class_kb import from_text_to_kb

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///flaskr')

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

celery_app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'devnotcompletelyrandomsecretkey'),
    SQLALCHEMY_DATABASE_URI=DATABASE_URL,
    CELERY=dict(
        broker_url=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
        result_backend=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
        task_ignore_result=True,
    ),
)

db.init_app(celery_app)




@celery_app.task
def add(a: int, b: int) -> int:
    time.sleep(5)
    return a + b

@celery_app.task
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