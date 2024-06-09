# Score processing and get groups for Next House Lab

## [Web api](https://nhl-scoreprocessingforprelim.streamlit.app/)

This project is designed to process preliminary data, group participants into equal groups, and manage and download the results using Streamlit.

## Expected data format

- Entry list

    ``` csv
    No, name, Represent
    1, Player1, TeamA
    2, Player2, TeamB
    ...
    ```

- Score sheet
  - file name: `{judgename}.csv`

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
