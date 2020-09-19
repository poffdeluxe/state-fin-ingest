from dotenv import load_dotenv

load_dotenv()

from state_fin_ingest.ingest import run

run("tx")