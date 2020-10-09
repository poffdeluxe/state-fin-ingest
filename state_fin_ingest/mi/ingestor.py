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

summary_files = [
    "mi/micfrcansummary.txt.zip",
    # "mi/micfrpacsummary.txt.zip", # We don't need PAC info at this detail
]

AFTER_DATE = datetime(2019, 1, 1, 0, 0, 0)

district_re = re.compile("^(\d+).*")


class MichiganIngestor(Ingestor):
    required_files = contrib_files + summary_files
    ingest_prefix = "mi"

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

        for sf in summary_files:
            with ZipFile(f"{INPUT_DIR}/{sf}", "r") as zip_obj:
                file_names = zip_obj.namelist()

                for file_name in file_names:
                    zip_obj.extract(file_name, path=TEMP_DIR)

        # load filer data to dict
        self.candidate_dict = dict()

        # Load up candidates
        with open(f"{TEMP_DIR}/micfrcansummary.txt", "r") as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)

            # Skip header and rundate
            next(reader)
            next(reader)

            for row in reader:
                if row[13] == "":
                    continue
                report_date = datetime.strptime(row[13], "%m/%d/%Y")

                # If the report date is before the date we care about, skip
                if report_date < AFTER_DATE:
                    continue

                # Skip if we've already saved this candidate
                if row[0] in self.candidate_dict:
                    continue

                # Only care about state rep and state senate
                if row[8] not in [
                    "Representative in State Legislature",
                    "State Senator",
                ]:
                    continue

                this_dict = dict()
                this_dict["candidate_id"] = row[0]
                this_dict[
                    "name"
                ] = f"{row[6]}, {row[4]}{(' ' + row[5] + '.') if row[5] else ''}"
                this_dict["party"] = row[7].lower()

                this_dict["house"] = (
                    "lower"
                    if row[8] == "Representative in State Legislature"
                    else "upper"
                )
                this_dict["district"] = district_re.findall(row[9])[0]

                self.candidate_dict[row[0]] = this_dict

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
                    if row[8] in self.candidate_dict:
                        this_dict["candidate"] = self.candidate_dict[row[8]]
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
