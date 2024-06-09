# Score processing and get groups for Next House Lab

## [Web api](https://nhl-scoreprocessingforprelim.streamlit.app/)

This project is designed to process preliminary data, group participants into equal groups, and manage and download the results using Streamlit.

## Usage

1. Upload entrylist and score sheets
2. download data of top 36 in local
3. Group them into 8 groups (multiple trial is enabled)
   - `Random 8 groups`: grouping ramdomly
   - `Even 8 groups (two top half and bottom half each)`: picking two from top half and the other from bottom half of top 36
4. refer logs of grouping
   - all of trials can be downloaded

## Expected data format

- Entry list

    ``` csv
    No, name, Represent
    1, Player1, TeamA
    2, Player2, TeamB
    ...
    ```

- Score sheet
  - file name should be `{judgename}.csv` as `{judgename}` will become its column name.

## Output files

### top 36

- `top4.csv`
- `top5to36.csv`
- data are in rising order on No.

### Groups

- `group_{1,2,...}.csv`

## Files

- `app.py`: The main Streamlit application script. It handles file uploads, data processing, and displays the results interactively.
- `main.py`: Contains the core functions for data processing, file output, and managing groupings.
- `makegroup.py`: Contains the functions for splitting data into groups, both randomly and evenly.

## Requirements

Make sure you have the following packages installed:

- `streamlit`
- `pandas`
- `numpy`

You can install the required packages using pip:

```bash
pip install streamlit pandas numpy
