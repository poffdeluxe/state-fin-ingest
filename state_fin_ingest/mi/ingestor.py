import csv
import glob
import re
import logging

from datetime import datetime
from zipfile import ZipFile
from state_fin_ingest.ingestor import RootIngestor
from state_fin_ingest.dir import INPUT_DIR, TEMP_DIR

from .contrib_ingestor import ContribIngestor
from .report_ingestor import ReportIngestor

logger = logging.getLogger(__name__)

summary_files = [
    "mi/micfrcansummary.txt.zip",
    # "mi/micfrpacsummary.txt.zip", # We don't need PAC info at this detail
]

AFTER_DATE = datetime(2019, 1, 1, 0, 0, 0)

district_re = re.compile("^(\d+).*")


class MichiganIngestor(RootIngestor):
    required_files = summary_files
    ingest_prefix = "mi"

    contrib_ingestor_class = ContribIngestor
    report_ingestor_class = ReportIngestor

    def pre(self):
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
                this_dict["district"] = int(district_re.findall(row[9])[0])

                self.candidate_dict[row[0]] = this_dict


    def post(self):
        pass
