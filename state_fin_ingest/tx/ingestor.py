import csv
import glob

from datetime import datetime
from zipfile import ZipFile
from state_fin_ingest.ingestor import RootIngestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR

from .contrib_ingestor import ContribIngestor
from .report_ingestor import ReportIngestor

TEXAS_FILE_NAME = "tx/TEC_CF_CSV.zip"

req_csvs = ["filers.csv", "spacs.csv", "cover.csv"]

AFTER_DATE = datetime(2018, 11, 6, 0, 0, 0)


class TexasIngestor(RootIngestor):
    required_files = [f"{TEXAS_FILE_NAME}"]
    ingest_prefix = "tx"

    contrib_ingestor_class = ContribIngestor
    report_ingestor_class = ReportIngestor

    def pre(self):
        with ZipFile(f"{INPUT_DIR}/{TEXAS_FILE_NAME}", "r") as zip_obj:
            file_names = zip_obj.namelist()

            for file_name in file_names:
                if file_name in req_csvs or file_name.startswith("contrib"):
                    zip_obj.extract(file_name, path=TEMP_DIR)

        # load filer data to dict
        self.candidate_dict = dict()

        with open(f"{TEMP_DIR}/filers.csv", "r") as f:
            reader = csv.reader(f)

            # Skip header
            next(reader)

            for row in reader:
                # Only care about candidates when building the dict
                if row[2] != "COH":
                    continue

                # Only care about state rep and state senate
                if row[49] not in ["STATEREP", "STATESEN"]:
                    continue

                if not row[50]:
                    continue

                this_dict = dict()
                this_dict["candidate_id"] = row[1]
                this_dict["name"] = row[3]
                this_dict[
                    "party"
                ] = "unknown"  # State of Texas makes it hard to figure out party

                this_dict["house"] = "lower" if row[49] == "STATEREP" else "upper"
                this_dict["district"] = int(row[50])

                # this_dict["status"] = row[46]

                self.candidate_dict[row[1]] = this_dict

        # load candidate to committee mapping to dict
        self.spac_to_cand = dict()
        with open(f"{TEMP_DIR}/spacs.csv", "r") as f:
            reader = csv.reader(f)

            # Skip header
            next(reader)

            for row in reader:
                # It's not ideal but for now just look at SUPPORT/ASSIST and not at oppose
                if row[8] not in list(["SUPPORT", "ASSIST"]):
                    continue

                this_dict = dict()
                this_dict["candidate_id"] = row[9]
                this_dict["committee_id"] = row[1]

                candId = this_dict["candidate_id"]

                self.spac_to_cand[row[1]] = this_dict

    def post(self):
        pass
