import csv
import glob

from datetime import datetime
from zipfile import ZipFile
from state_fin_ingest.ingestor import Ingestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR

# TODO: move this to a constant or better yet an ENV variable
AFTER_DATE = datetime(2018, 11, 6, 0, 0, 0)


class ReportIngestor(Ingestor):
    def pre(self):
        pass

    def work(self):
        with open(f"{TEMP_DIR}/cover.csv", "r") as f:
            reader = csv.reader(f)

            # Skip header
            next(reader)

            # try:
            for row in reader:
                # Skip contribution if missing a date
                if row[3] == "" or row[19] == "":
                    continue

                received_date = datetime.strptime(row[3], "%Y%m%d")

                # Skip reports prior to a given date
                if received_date <= AFTER_DATE:
                    continue

                this_dict = dict()

                # Attach candidate info if report is to candidate campaign
                if row[6] == "COH":
                    # I don't care about contributions that aren't to
                    # candidate or candidate linked PAC
                    if row[5] not in self.parent.candidate_dict:
                        continue
                    this_dict["candidate"] = self.parent.candidate_dict[row[5]]
                elif row[5] in self.parent.spac_to_cand:
                    # I don't care about contributions that aren't to
                    # candidate or candidate linked PAC
                    candidate_id = self.parent.spac_to_cand[row[5]]["candidate_id"]

                    if candidate_id not in self.parent.candidate_dict:
                        continue
                    this_dict["candidate"] = self.parent.candidate_dict[candidate_id]
                else:
                    continue

                this_dict["filer"] = {
                    "filer_id": row[5],
                    "type": row[6],
                    "name": row[7],
                }

                this_dict["report_id"] = row[2]

                this_dict["period_start_date"] = datetime.strptime(
                    row[21], "%Y%m%d"
                ).isoformat()
                this_dict["period_end_date"] = datetime.strptime(
                    row[22], "%Y%m%d"
                ).isoformat()

                this_dict["received_date"] = received_date.isoformat()

                # Report type
                this_dict["type"] = row[8].lower()

                # Total contributions
                this_dict["contributions_amount"] = row[24]

                # Total expenditures
                this_dict["expenditures_amount"] = row[26]

                # Cash on hand
                this_dict["ending_balance_amount"] = row[28]

                yield this_dict

    def post(self):
        pass
