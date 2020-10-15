import os
import re
from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=[os.getenv("ES_HOST")])


def get_index_name(prefix, ingestor_type):
    env = os.getenv("INGEST_ENV", "dev")

    # TODO: Make this less nasty -- we're ripping out special characters from ISO8601 to make it index name friendly
    utc_now = datetime.now().isoformat()
    utc_now = re.sub(r"\W+", "", utc_now.lower())

    index_name = f"{prefix}_{ingestor_type}_{utc_now}_{env}"
    return index_name


def create_new_index(index_name, mapping_template):
    body = {"mappings": mapping_template}

    es.indices.create(index_name, body)

    return index_name


def promote_index(prefix, index, index_type):
    env = os.getenv("INGEST_ENV", "dev")

    actions = {
        "actions": [
            {"remove": {"index": "*", "alias": f"{prefix}_{index_type}_{env}"}},
            {"add": {"index": index, "alias": f"{prefix}_{index_type}_{env}"}},
        ]
    }
    es.indices.update_aliases(actions)