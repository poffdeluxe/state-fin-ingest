import csv
import glob
import re
import logging

from datetime import datetime
from state_fin_ingest.ingestor import Ingestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR

logger = logging.getLogger(__name__)

AFTER_DATE = datetime(2019, 1, 1, 0, 0, 0)

district_re = re.compile("^(\d+).*")


class ReportIngestor(Ingestor):
    required_files = []

    def pre(self):
        pass

    def work(self):
        # NOTE: the summary file is already extracted and available to us
        # thanks to the root ingestor

        # Load up candidates
        with open(f"{TEMP_DIR}/micfrcansummary.txt", "r") as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)

            # Skip header and rundate
            next(reader)
            next(reader)

            for row in reader:
                if row[12] == "":
                    continue

                received_date = datetime.strptime(row[12], "%m/%d/%Y")

                # If the report date is before the date we care about, skip
                if received_date < AFTER_DATE:
                    continue

                # Skip if we don't care about this candidate
                if row[0] not in self.parent.candidate_dict:
                    continue

                this_dict = dict()

                this_dict["candidate"] = self.parent.candidate_dict[row[0]]

                this_dict["filer"] = {
                    "filer_id": row[0],
                    "type": row[2],
                    "name": row[3],
                }

                this_dict["report_id"] = f"{row[0]}_{row[1]}"

                this_dict["period_start_date"] = datetime.strptime(
                    row[13], "%m/%d/%Y"
                ).isoformat()
                this_dict["period_end_date"] = datetime.strptime(
                    row[14], "%m/%d/%Y"
                ).isoformat()

                this_dict["received_date"] = received_date.isoformat()

                # Report type
                this_dict["type"] = row[11].lower()

                # TODO: Amended -- is there a better way to record this?
                # this_dict["amendment"] = True if "amended" in this_dict["type"] else False

                # Total contributions
                this_dict["contributions_amount"] = row[15]

                # Total expenditures
                this_dict["expenditures_amount"] = row[21]

                # Cash on hand
                this_dict["ending_balance_amount"] = row[28]

                yield this_dict

    def post(self):
        pass
