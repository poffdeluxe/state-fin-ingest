import csv
import glob
import re
import logging

from datetime import datetime
from zipfile import ZipFile
from state_fin_ingest.ingestor import Ingestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR

logger = logging.getLogger(__name__)

contrib_files = [
    "mi/2019_mi_cfr_contributions_00.zip",
    "mi/2019_mi_cfr_contributions_01.zip",
    "mi/2020_mi_cfr_contributions_00.zip",
    "mi/2020_mi_cfr_contributions_01.zip",
    "mi/2020_mi_cfr_contributions_02.zip",
]

AFTER_DATE = datetime(2019, 1, 1, 0, 0, 0)

district_re = re.compile("^(\d+).*")


class ContribIngestor(Ingestor):
    required_files = contrib_files

    def pre(self):
        global contrib_files

        # Unzip our contribution files
        self.contrib_files = []
        for cf in contrib_files:
            with ZipFile(f"{INPUT_DIR}/{cf}", "r") as zip_obj:
                file_names = zip_obj.namelist()

                for file_name in file_names:
                    zip_obj.extract(file_name, path=TEMP_DIR)

                self.contrib_files = self.contrib_files + file_names

    def work(self):
        for c_file in self.contrib_files:
            with open(f"{TEMP_DIR}/{c_file}", "r", errors="replace") as f:
                reader = csv.reader(f, delimiter="\t")

                # Skip header only in _00 files
                if "_00.txt" in c_file:
                    next(reader)

                for row in reader:
                    # Skip contribution if missing a date
                    if row[21] == "":
                        continue

                    # There's a record with some really messed up formatting...
                    if row[0] == "486666" and row[2] == "9839":
                        logger.debug("Skipped bad record")
                        continue

                    # Clean up our row
                    row = [x.strip() for x in row]

                    contrib_date = datetime.strptime(row[21], "%m/%d/%Y")

                    # Skip contributions prior to a given date
                    if contrib_date <= AFTER_DATE:
                        continue

                    this_dict = dict()

                    this_dict["filer"] = {
                        "filer_id": row[8],
                        "type": row[9],
                        "name": row[6],
                    }

                    # TODO: any additional data?
                    # this_dict["addtl_data"] = {"schedule": row[2]}

                    # connect candidate
                    if row[8] in self.parent.candidate_dict:
                        this_dict["candidate"] = self.parent.candidate_dict[row[8]]
                    else:
                        # I don't care about contributions that aren't to
                        # candidate or candidate linked PAC
                        continue

                    this_dict["contribution_id"] = f"{row[0]}_{row[2]}"

                    this_dict["contribution_date"] = contrib_date.isoformat()

                    this_dict["amount"] = float(row[22])
                    this_dict["memo"] = row[24]

                    # Information about the contributor -- INDIVIDUAL OR ENTITY OR UNKNOWN
                    first_name = row[13]
                    last_or_org_name = row[14]

                    if first_name == "" and last_or_org_name != "":
                        this_dict["type"] = "entity"
                        this_dict["name"] = last_or_org_name
                    else:
                        this_dict["type"] = "individual"
                        this_dict["name"] = f"{first_name} {last_or_org_name}"

                    this_dict["city"] = row[16]
                    this_dict["state"] = row[17]
                    this_dict["zip"] = row[18]

                    this_dict["employer"] = row[20]
                    this_dict["occupation"] = row[19]
                    this_dict["job_title"] = ""

                    yield this_dict

    def post(self):
        pass
