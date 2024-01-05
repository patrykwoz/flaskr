import time

from celery import shared_task, Task

from celery.contrib import rdb

from flaskr.models import db, KnowledgeBase
# from flaskr.helpers.ml_functions import class_kb

from flaskr.helpers.ml_functions import resource_cache

import math
import torch
import json

tokenizer = resource_cache.tokenizer
model = resource_cache.model



@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    time.sleep(5)
    return a + b

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

@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    return {"current": total, "total": total}


def extract_relations_from_model_output(text):
    relations = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    text_replaced = text.replace("<s>", "").replace("<pad>", "").replace("</s>", "")
    for token in text_replaced.split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        relations.append({
            'head': subject.strip(),
            'type': relation.strip(),
            'tail': object_.strip()
        })
    return relations

class KB():
    def __init__(self):
        self.entities = {}
        self.relations = []
        self.sources = {}

    def are_relations_equal(self, r1, r2):
        return all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"])

    def exists_relation(self, r1):
        return any(self.are_relations_equal(r1, r2) for r2 in self.relations)
    
    def merge_relations(self, r2):
        r1 = [r for r in self.relations
              if self.are_relations_equal(r2, r)][0]

        # if different article
        article_url = list(r2["meta"].keys())[0]
        if article_url not in r1["meta"]:
            r1["meta"][article_url] = r2["meta"][article_url]

        # if existing article
        else:
            spans_to_add = [span for span in r2["meta"][article_url]["spans"]
                            if span not in r1["meta"][article_url]["spans"]]
            r1["meta"][article_url]["spans"] += spans_to_add
    
    def get_wikipedia_data(self, candidate_entity):
        try:
            entity_data = {
                "title": candidate_entity,
                "url": ' ',
                "summary": ' ',
            }
            return entity_data
        except:
            return None

    def add_entity(self, e):
        self.entities[e["title"]] = {k:v for k,v in e.items() if k != "title"}

    def add_relation(self, r, article_title, article_publish_date):
        # check on wikipedia
        candidate_entities = [r["head"], r["tail"]]

        entities = [self.get_wikipedia_data(ent) for ent in candidate_entities]

        # if one entity does not exist, stop
        if any(ent is None for ent in entities):
            return

        # manage new entities
        for e in entities:
            self.add_entity(e)

        # rename relation entities with their wikipedia titles
        r["head"] = entities[0]["title"]
        r["tail"] = entities[1]["title"]

        # add source if not in kb
        article_url = list(r["meta"].keys())[0]
        if article_url not in self.sources:
            self.sources[article_url] = {
                "article_title": article_title,
                "article_publish_date": article_publish_date
            }

        # manage new relation
        if not self.exists_relation(r):
            self.relations.append(r)
        else:
            self.merge_relations(r)
    
    def merge_with_kb(self, kb2):
        for r in kb2.relations:
            article_url = list(r["meta"].keys())[0]
            source_data = kb2.sources[article_url]
            self.add_relation(r, source_data["article_title"],
                              source_data["article_publish_date"])

    def print(self):
        print("Entities:")
        for e in self.entities.items():
            print(f"  {e}")
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")
        print("Sources:")
        for s in self.sources.items():
            print(f"  {s}")
    
    def to_json(self):
        kb_data = {
            "entities": self.entities,
            "relations": self.relations,
            "sources": self.sources
        }
        return json.dumps(kb_data, indent=4)



def from_text_to_kb(text, article_url,tokenizer, model, span_length=128, article_title=None,
                    article_publish_date=None, verbose=False):

    # tokenize whole text
    inputs = tokenizer([text], return_tensors="pt")

    # compute span boundaries
    num_tokens = len(inputs["input_ids"][0])
    if verbose:
        print(f"Input has {num_tokens} tokens")
    num_spans = math.ceil(num_tokens / span_length)
    if verbose:
        print(f"Input has {num_spans} spans")
    overlap = math.ceil((num_spans * span_length - num_tokens) / max(num_spans - 1, 1))
    spans_boundaries = []
    start = 0
    for i in range(num_spans):
        spans_boundaries.append([start + span_length * i, start + span_length * (i + 1)])
        start -= overlap
    if verbose:
        print(f"Span boundaries are {spans_boundaries}")

    # transform input with spans
    # tensor_ids = [inputs["input_ids"][0][boundary[0]:boundary[1]] for boundary in spans_boundaries]
    # Initialize an empty list to store tensor_ids
    tensor_ids = []

    # Iterate through spans_boundaries and extract slices from inputs["input_ids"]
    for boundary in spans_boundaries:
        start_idx, end_idx = boundary[0], boundary[1]
        input_ids_slice = inputs["input_ids"][0][start_idx:end_idx]
        tensor_ids.append(input_ids_slice)

    # tensor_masks = [inputs["attention_mask"][0][boundary[0]:boundary[1]] for boundary in spans_boundaries]
    # Initialize an empty list to store tensor_masks
    tensor_masks = []

    # Iterate through spans_boundaries and extract slices from inputs["attention_mask"]
    for boundary in spans_boundaries:
        start_idx, end_idx = boundary[0], boundary[1]
        attention_mask_slice = inputs["attention_mask"][0][start_idx:end_idx]
        tensor_masks.append(attention_mask_slice)


    inputs = {
        "input_ids": torch.stack(tensor_ids),
        "attention_mask": torch.stack(tensor_masks)
    }
    # generate relations
    num_return_sequences = 3
    gen_kwargs = {
        "max_length": 256,
        "length_penalty": 0,
        "num_beams": 3,
        "num_return_sequences": num_return_sequences
    }

    
    print('before generated tokens')
    try:
        generated_tokens = model.generate(**inputs,**gen_kwargs,)
    except Exception as e:
        print (f"error {e}" )
    rdb.set_trace()
    print('after generated tokens')

    # decode relations
    decoded_preds = tokenizer.batch_decode(generated_tokens,
                                           skip_special_tokens=False)
    print('after decoded pred')

    # create kb
    kb = KB()
    i = 0
    for sentence_pred in decoded_preds:
        current_span_index = i // num_return_sequences
        relations = extract_relations_from_model_output(sentence_pred)
        for relation in relations:
            relation["meta"] = {
                article_url: {
                    "spans": [spans_boundaries[current_span_index]]
                }
            }
            
            kb.add_relation(relation, article_title, article_publish_date)
        i += 1

    return kb


def from_idea_to_kb(idea):
    config = {
        "article_title": idea.name,
        "article_publish_date": idea.publish_date.isoformat()
    }
    kb = from_text_to_kb(idea.text, idea.url, **config)
    return kb

def from_ideas_to_kb(ideas, verbose=False):
    kb = KB()
    if verbose:
        print(f"{len(ideas)} ideas to visit")
    for idea in ideas:
        if verbose:
            print(f"Visiting idea: {idea.name}...")
        try:
            kb_idea = from_idea_to_kb(idea)
            kb.merge_with_kb(kb_idea)
        except ArticleException:
            if verbose:
                print(f"Couldn't process the idea: {idea.name}")
    return kb 