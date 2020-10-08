# Michigan Ingestor

Finance data for the Michigan legislature is available from the [Michigan Secretary of State](https://www.michigan.gov/sos/0,4670,7-127-1633_8723_8751---,00.html)

The contribution ZIP files are available here: https://miboecfr.nictusa.com/cfr/dumpall/cfrdetail/
and a breakdown of the fields is here: https://miboecfr.nictusa.com/cfr/dumpall/cfrdetail/ReadMe_CONTRIBUTIONS.html

Candidate Summary ZIP file is available here: https://miboecfr.nictusa.com/cfr/dumpall/micfrcansummary.txt.zip

## Methodology
We build a list of candidate committees from the report data (only looking at candidates with reports from Jan 1 2019) and then interate over the contribution files from 2019 and 2020.

There is some weirdness in the tab-delimited files:
1. The header only appears in the files ending in _00.txt
2. In one of the files, there's a record that somehow has an extra field partially duplicated causing the record to have an unexpected amount of columns. We manually skip this record
