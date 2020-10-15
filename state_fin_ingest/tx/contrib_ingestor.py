import csv
import glob

from datetime import datetime
from zipfile import ZipFile
from state_fin_ingest.ingestor import Ingestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR


AFTER_DATE = datetime(2018, 11, 6, 0, 0, 0)


class ContribIngestor(Ingestor):
    def pre(self):
        pass

    def work(self):
        contrib_files = glob.glob(f"{TEMP_DIR}/contrib*.csv")

        for c_file in contrib_files:
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
                        if row[6] not in self.parent.candidate_dict:
                            continue
                        this_dict["candidate"] = self.parent.candidate_dict[row[6]]
                    elif row[6] in self.parent.spac_to_cand:
                        # I don't care about contributions that aren't to
                        # candidate or candidate linked PAC
                        if row[6] not in self.parent.spac_to_cand:
                            continue

                        candidate_id = self.parent.spac_to_cand[row[6]]["candidate_id"]

                        if candidate_id not in self.parent.candidate_dict:
                            continue
                        this_dict["candidate"] = self.parent.candidate_dict[
                            candidate_id
                        ]
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
