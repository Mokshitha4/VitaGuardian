from typing import Dict, Any
from collections import Counter
from langchain.tools import StructuredTool
import pandas as pd
import pathlib
import us

import glob,os

def get_full_state_name(abbr: str) -> str:
    return us.states.lookup(abbr).name.upper()  # e.g. "CA" → "CALIFORNIA"


# FEMA & NOAA data paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of the current script
FEMA_CSV = os.path.join(BASE_DIR, "Datasets\\DisasterDeclarationsSummaries.csv")
NOAA_DIR = "Datasets/"  # Your folder with NOAA .csv files

# Load NOAA data (merged)
noaa_files = glob.glob(os.path.join(NOAA_DIR, "StormEvents_details-ftp_v1.0_d*.csv"))

noaa_dfs = [pd.read_csv(f, usecols=["STATE", "CZ_NAME", "EVENT_TYPE", "DEATHS_DIRECT"], low_memory=False) for f in noaa_files]
noaa_df = pd.concat(noaa_dfs, ignore_index=True)

# FEMA corrected load
fema_df = pd.read_csv(FEMA_CSV, low_memory=False, parse_dates=["declarationDate"])
fema_df["declarationDate"] = pd.to_datetime(fema_df["declarationDate"], errors="coerce")

def fema_search(state: str, county_name: str) -> Dict[str, Any]:
    cutoff = (pd.Timestamp.now(tz=None) - pd.DateOffset(years=15)).tz_localize(None)
    mask = (
        (fema_df["state"].str.upper() == state.upper()) &
        (fema_df["designatedArea"].str.contains(county_name, case=False, na=False)) &
        (fema_df["declarationDate"].dt.tz_localize(None) >= cutoff)
    )
    sub = fema_df[mask]
    counter = Counter(sub["incidentType"])
    return {
        "source": "FEMA Disaster Declarations",
        "top_incidents": counter.most_common(5),
        "total_events": sum(counter.values())
    }

# NOAA tool function
def noaa_search(state: str, county_name: str) -> Dict[str, Any]:
    state_full = get_full_state_name(state)
    mask = (
        (noaa_df["STATE"].str.upper() == state_full.upper()) &
        (noaa_df["CZ_NAME"].str.contains(county_name, case=False, na=False))
    )
    sub = noaa_df[mask]
    freq = Counter(sub["EVENT_TYPE"])
    fatal = Counter({etype: int(sub[sub["EVENT_TYPE"] == etype]["DEATHS_DIRECT"].gt(0).sum()) for etype in freq})
    return {
        "source": "NOAA Storm Events",
        "top_events": freq.most_common(5),
        "fatal_event_counts": {k: v for k, v in fatal.items() if v > 0},
        "total_events": sum(freq.values())
    }

# Wrap as LangChain tools
fema_tool = StructuredTool.from_function(
    name="fema_hazard_lookup",
    description="Get FEMA top hazards for a given state and county FIPS (past 15 years).",
    func=fema_search
)

noaa_tool = StructuredTool.from_function(
    name="noaa_hazard_lookup",
    description="Get NOAA storm event hazards and fatalities by state and county name (last 10 years).",
    func=noaa_search
)

# Example usage:
# print(fema_search("VA",'Montgomery'))
# print(noaa_search("VA",'Montgomery'))