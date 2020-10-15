import argparse
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

from state_fin_ingest.ingest import run, code_to_ingestor

logger = logging.getLogger(__name__)

available_states = code_to_ingestor.keys()

parser = argparse.ArgumentParser(
    description="Ingest finance data for state legislature campaigns"
)
parser.add_argument(
    "-s",
    "--states",
    nargs="+",
    help="<Required> States to ingest",
    required=True,
    choices=available_states,
)

args = parser.parse_args()

env = os.getenv("INGEST_ENV", "dev")
logger.info(f"Ingest running in mode: {env}")

for state in args.states:
    run(state)
