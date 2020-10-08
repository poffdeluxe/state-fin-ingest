# Texas Ingestor

Finance data for the Texas State legislature is available from the [Texas Ethics Commission](https://www.ethics.state.tx.us/search/cf/)

The ZIP file is available here: https://www.ethics.state.tx.us/data/search/cf/TEC_CF_CSV.zip
and a breakdown of the fields is here: https://www.ethics.state.tx.us/data/search/cf/CFS-ReadMe.txt

Place the `TEC_CF_CSV.zip` into the `input/tx/` directory (create the `/tx` subdirectory if necessary)

## Methodology
We build a list of candidates and PACs from the filers.csv. Unfortunately, there isn't a field for party so party is currently missing from Texas records.
We also connect candidates to SPACs by reading the spacs.csv file and looking to see if they support or assist a particular candidate.

After that, we iterate over the contribution files and connect contributions to candidates where possible.