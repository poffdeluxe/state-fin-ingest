import os
import re
import shutil
from datetime import datetime

from elasticsearch import Elasticsearch

from state_fin_ingest.tx.ingestor import TexasIngestor
from state_fin_ingest.dir import TEMP_DIR
from state_fin_ingest.index import MAPPING_TEMPLATE

code_to_ingestor = {"tx": TexasIngestor}

es = Elasticsearch(hosts=[os.getenv("ES_HOST")])

NUM_BEFORE_FLUSH = 500


def create_new_index(prefix):
    utc_now = datetime.now().isoformat()
    utc_now = re.sub(r"\W+", "", utc_now.lower())

    index_name = f"{prefix}_contribs_{utc_now}"

    body = {"mappings": MAPPING_TEMPLATE}

    es.indices.create(index_name, body)

    return index_name


def promote_index(prefix, index):
    actions = {
        "actions": [
            {"remove": {"index": "*", "alias": f"{prefix}_contribs"}},
            {"add": {"index": index, "alias": f"{prefix}_contribs"}},
        ]
    }
    es.indices.update_aliases(actions)


def create_temp_data_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)


def cleanup_temp_data_dir():
    shutil.rmtree(TEMP_DIR)


def flush_records(index, records):
    for rec in records:
        rec_id = rec["contributionId"]
        es.index(index, rec, id=rec_id)

    print("Flushed")


def run(state_code):
    print(f"Running ingestion system for: {state_code}")
    ingestor = code_to_ingestor[state_code]()

    prefix = ingestor.ingest_prefix
    index = create_new_index(prefix)

    print(f"Index created: {index}")

    create_temp_data_dir()

    print("Created temporary data directory")

    print("Running ingestor's pre-work setup")
    ingestor.pre()
    print("Done")

    print("Beginning ingestion work....")

    ticker = 0
    records = []
    for record in ingestor.work():
        ticker = ticker + 1

        records.append(record)

        if ticker % NUM_BEFORE_FLUSH == 0:
            flush_records(index, records)
            records = []

    print("Done ingesting")

    print("Beginning ingestor's post-work teardown")
    ingestor.post()

    print("Deleting data in the temporary data directory")
    cleanup_temp_data_dir()

    print(f"Promoting {index} to {prefix}_contribs")
    promote_index(prefix, index)

    print("INGESTION COMPLETE")