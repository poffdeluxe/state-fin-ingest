import os
import logging
import shutil

from .run_ingestor import run_ingestor
from .index import get_index_name, create_new_index, promote_index
from .mapping_template import CONTRIB_MAPPING_TEMPLATE, REPORT_MAPPING_TEMPLATE

from state_fin_ingest.tx.ingestor import TexasIngestor
from state_fin_ingest.mi.ingestor import MichiganIngestor

from state_fin_ingest.dir import TEMP_DIR

logger = logging.getLogger(__name__)

code_to_ingestor = {"tx": TexasIngestor, "mi": MichiganIngestor}


def create_temp_data_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)


def cleanup_temp_data_dir():
    shutil.rmtree(TEMP_DIR)


def run_contribs(ingestor):
    if not ingestor.contrib_ingestor_class:
        return

    index_name = get_index_name(ingestor.ingest_prefix, "contribs")

    # TODO: We should probably wrap this process in a try-finally to clean up the created index if there's an exception
    create_new_index(index_name, CONTRIB_MAPPING_TEMPLATE)
    logger.info(f"Index created: {index_name}")

    run_ingestor(ingestor.contrib_ingestor, index_name)

    logger.info(f"Promoting {index_name}...")
    promote_index(ingestor.ingest_prefix, index_name, "contribs")


def run_reports(ingestor):
    if not ingestor.report_ingestor_class:
        return

    index_name = get_index_name(ingestor.ingest_prefix, "reports")

    # TODO: We should probably wrap this process in a try-finally to clean up the created index if there's an exception
    create_new_index(index_name, REPORT_MAPPING_TEMPLATE)
    logger.info(f"Index created: {index_name}")

    run_ingestor(ingestor.report_ingestor, index_name)

    logger.info(f"Promoting {index_name}...")
    promote_index(ingestor.ingest_prefix, index_name, "reports")


def run(state_code):
    logger.info(f"Running ingestion system for: {state_code}")
    ingestor = code_to_ingestor[state_code]()

    create_temp_data_dir()
    logger.debug("Created temporary data directory")

    logger.info("Running root ingestor's pre-work setup")
    ingestor.pre()
    logger.info("Done")

    # Ingest contributions
    # run_contribs(ingestor)

    # Ingest reports
    run_reports(ingestor)

    ingestor.post()

    logger.debug("Deleting data in the temporary data directory")
    cleanup_temp_data_dir()

    logger.info(f"Ingestion complete for {state_code}")
