import os
import time
import logging
import re
import shutil
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from state_fin_ingest.tx.ingestor import TexasIngestor
from state_fin_ingest.mi.ingestor import MichiganIngestor

from state_fin_ingest.dir import TEMP_DIR
from state_fin_ingest.index import MAPPING_TEMPLATE

logger = logging.getLogger(__name__)

code_to_ingestor = {"tx": TexasIngestor, "mi": MichiganIngestor}

es = Elasticsearch(hosts=[os.getenv("ES_HOST")])

NUM_BEFORE_FLUSH = 500


def create_new_index(prefix):
    # TODO: Make this less nasty -- we're ripping out special characters from ISO8601 to make it index name friendly
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
    for r in records:
        r["_id"] = r["contribution_id"]

    bulk(es, index=index, actions=records)


def run(state_code):
    logger.info(f"Running ingestion system for: {state_code}")
    ingestor = code_to_ingestor[state_code]()

    # TODO: We should probably wrap this process in a try-finally to clean up the created index if there's an exception
    prefix = ingestor.ingest_prefix
    index = create_new_index(prefix)

    logger.info(f"Index created: {index}")

    create_temp_data_dir()

    logger.debug("Created temporary data directory")

    logger.info("Running ingestor's pre-work setup")
    ingestor.pre()
    logger.info("Done")

    logger.info("Begin ingesting records....")
    start_time = time.perf_counter()

    ticker = 0
    records = []
    for record in ingestor.work():
        ticker = ticker + 1

        records.append(record)

        # TODO: The ES bulk helpers actually take care of this so I should call the streaming_bulk helper directly
        if ticker % NUM_BEFORE_FLUSH == 0:
            flush_records(index, records)
            records = []

    # Final flush
    if len(records) > 0:
        flush_records(index, records)

    end_time = time.perf_counter()

    logger.info("Done ingesting records.")
    logger.info(f"Ingested {ticker} records in {end_time - start_time:0.4f} seconds")

    ingestor.post()

    logger.debug("Deleting data in the temporary data directory")
    cleanup_temp_data_dir()

    logger.info(f"Promoting {index} to {prefix}_contribs")
    promote_index(prefix, index)

    logger.info(f"Ingestion complete for {prefix}")
