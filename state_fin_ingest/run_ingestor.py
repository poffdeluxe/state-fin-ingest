import time
import logging

from .index import es
from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)

NUM_BEFORE_FLUSH = 500


def flush_records(index, records):
    for r in records:
        # TODO: this could be much better
        r["_id"] = r["contribution_id"] if "contribution_id" in r else r["report_id"]

    bulk(es, index=index, actions=records)


def run_ingestor(ingestor, index_name):
    logger.info(f"Running ingestor's pre-work setup")
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
            flush_records(index_name, records)
            records = []

    # Final flush
    if len(records) > 0:
        flush_records(index_name, records)

    end_time = time.perf_counter()

    logger.info("Done ingesting records.")
    logger.info(f"Ingested {ticker} records in {end_time - start_time:0.4f} seconds")

    ingestor.post()
