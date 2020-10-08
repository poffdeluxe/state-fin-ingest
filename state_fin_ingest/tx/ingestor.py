import csv
import glob

from datetime import datetime
from zipfile import ZipFile
from state_fin_ingest.ingestor import Ingestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR

TEXAS_FILE_NAME = "tx/TEC_CF_CSV.zip"

req_csvs = [
    "filers.csv",
    "spacs.csv",
]

AFTER_DATE = datetime(2018, 11, 6, 0, 0, 0)


class TexasIngestor(Ingestor):
    required_files = [f"{TEXAS_FILE_NAME}"]
    ingest_prefix = "tx"

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

                print(f"Saving: {this_dict['name']}")

                self.candidate_dict[row[1]] = this_dict

        # load candidate to committee mapping to dict
        self.spac_to_cand = dict()
        with open(f"{TEMP_DIR}/spacs.csv", "r") as f:
            reader = csv.reader(f)

            # Skip header
            next(reader)

            for row in reader:
                # It's not ideal but for not just look at SUPPORT/ASSIST and not at oppose
                if row[8] not in list(["SUPPORT", "ASSIST"]):
                    continue

                this_dict = dict()
                this_dict["candidate_id"] = row[9]
                this_dict["committee_id"] = row[1]

                candId = this_dict["candidate_id"]
                if candId in self.candidate_dict:
                    print(
                        f"Connecting {this_dict['candidate_id']} to {this_dict['committee_id']}"
                    )

                    print(f"{row[3]} to {row[11]}")
                else:
                    print(f"missing {row[1]}")

                self.spac_to_cand[row[1]] = this_dict

    def work(self):
        contrib_files = glob.glob(f"{TEMP_DIR}/contrib*.csv")

        for c_file in contrib_files:
            print(f"Now loading {c_file}")
            with open(f"{c_file}", "r") as f:
                reader = csv.reader(f)

                # Skip header
                next(reader)

                # try:
                for row in reader:
                    # Skip contribution if missing a date
                    if row[10] == "":
                        continue

                    contrib_date = datetime.strptime(row[10], "%Y%m%d")

                    # Skip contributions prior to a given date
                    if contrib_date <= AFTER_DATE:
                        continue

                    # Skip non-monetary contributions
                    if row[2] == "A2":
                        continue

                    this_dict = dict()

                    this_dict["filer"] = {
                        "filer_id": row[6],
                        "type": row[7],
                        "name": row[8],
                    }

                    this_dict["addtl_data"] = {"schedule": row[2]}

                    # Attach candidate info if direct contrib to canidate campaign
                    if row[7] == "COH":
                        # I don't care about contributions that aren't to
                        # candidate or candidate linked PAC
                        if row[6] not in self.candidate_dict:
                            continue
                        this_dict["candidate"] = self.candidate_dict[row[6]]
                    elif row[6] in self.spac_to_cand:
                        # I don't care about contributions that aren't to
                        # candidate or candidate linked PAC
                        if row[6] not in self.spac_to_cand:
                            continue

                        candidate_id = self.spac_to_cand[row[6]]["candidate_id"]

                        if candidate_id not in self.candidate_dict:
                            continue
                        this_dict["candidate"] = self.candidate_dict[candidate_id]
                        print(
                            f"CONNECTED {this_dict['candidate']['name']} to {this_dict['filer']['name']}"
                        )
                    else:
                        continue

                    this_dict["contribution_id"] = row[9]

                    this_dict["contribution_date"] = contrib_date.isoformat()

                    this_dict["amount"] = float(row[11])
                    this_dict["memo"] = row[12]

                    # Information about the contributor -- INDIVIDUAL OR ENTITY OR UNKNOWN
                    this_dict["type"] = row[15].lower()

                    if row[15] == "INDIVIDUAL":
                        this_dict["name"] = f"{row[19]} {row[17]}"
                    else:
                        this_dict["name"] = row[16]

                    this_dict["city"] = row[22]
                    this_dict["state"] = row[23]
                    this_dict["zip"] = row[26]

                    this_dict["employer"] = row[28]
                    this_dict["occupation"] = row[29]
                    this_dict["job_title"] = row[30]

                    yield this_dict

    def post(self):
        pass
