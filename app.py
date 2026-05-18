import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="International Flights Dashboard",
    layout="wide"
)

st.title("International Flights Dashboard")

st.markdown(
    """
    **Designed and built by Bertrand Brelier**  
    Quatalyzer Inc. | [www.quatalyzer.com](https://www.quatalyzer.com)
    """
)


@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path, low_memory=False)

df = load_data("T_T100I_SEGMENT_ALL_CARRIER.csv")

# Carrier display name
df["CARRIER_DISPLAY"] = (
    df["UNIQUE_CARRIER_NAME"].fillna("Unknown Carrier")
    + " ("
    + df["UNIQUE_CARRIER"].fillna("NA")
    + ")"
)

st.sidebar.header("Filters")

year = st.sidebar.selectbox(
    "Year",
    sorted(df["YEAR"].dropna().unique(), reverse=True)
)

month = st.sidebar.selectbox(
    "Month",
    sorted(df[df["YEAR"] == year]["MONTH"].dropna().unique())
)

carrier_options = sorted(df["CARRIER_DISPLAY"].dropna().unique())

default_carrier = "Spirit Air Lines (NK)"
default_index = (
    carrier_options.index(default_carrier)
    if default_carrier in carrier_options
    else 0
)

carrier_display = st.sidebar.selectbox(
    "Carrier",
    carrier_options,
    index=default_index
)

selected_carrier_code = (
    carrier_display.split("(")[-1]
    .replace(")", "")
)

caribbean_airports = [
    "CUN", "MBJ", "PUJ", "SDQ", "STI", "KIN", "NAS",
    "AUA", "CUR", "POP", "LRM", "CZM", "PVR", "SJD",
    "SJO"
]

destination_options = sorted(df["DEST"].dropna().unique())

destination_filter = st.sidebar.multiselect(
    "Destination airports",
    destination_options,
    default=[a for a in caribbean_airports if a in destination_options]
)

data = df[
    (df["YEAR"] == year) &
    (df["MONTH"] == month) &
    (df["UNIQUE_CARRIER"] == selected_carrier_code)
].copy()

if destination_filter:
    data = data[data["DEST"].isin(destination_filter)]

data["LOAD_FACTOR"] = (
    data["PASSENGERS"] / data["SEATS"]
)

st.subheader(
    f"Summary for {carrier_display} - {int(year)}-{int(month):02d}"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Passengers",
    f"{data['PASSENGERS'].sum():,.0f}"
)

col2.metric(
    "Seats",
    f"{data['SEATS'].sum():,.0f}"
)

col3.metric(
    "Avg Load Factor",
    f"{data['LOAD_FACTOR'].mean():.1%}"
    if len(data)
    else "N/A"
)

col4.metric(
    "Routes",
    f"{data[['ORIGIN', 'DEST']].drop_duplicates().shape[0]:,.0f}"
)

route_summary = (
    data.groupby(["ORIGIN", "DEST"], as_index=False)
    .agg(
        PASSENGERS=("PASSENGERS", "sum"),
        SEATS=("SEATS", "sum"),
        DISTANCE=("DISTANCE", "mean"),
        DEPARTURES=("DEPARTURES_PERFORMED", "sum")
    )
)

route_summary["LOAD_FACTOR"] = (
    route_summary["PASSENGERS"] /
    route_summary["SEATS"]
)

route_summary = route_summary.sort_values(
    "PASSENGERS",
    ascending=False
)

st.subheader("Route Summary")

st.dataframe(
    route_summary,
    use_container_width=True
)

top_routes = route_summary.head(20).copy()

top_routes["ROUTE"] = (
    top_routes["ORIGIN"] +
    " → " +
    top_routes["DEST"]
)

st.subheader("Top 20 Routes by Passengers")

st.bar_chart(
    top_routes.set_index("ROUTE")["PASSENGERS"]
)

st.subheader("Top 20 Routes by Seats")

st.bar_chart(
    top_routes.set_index("ROUTE")["SEATS"]
)

st.subheader("Average Load Factor by Route")

load_factor_routes = (
    top_routes.set_index("ROUTE")["LOAD_FACTOR"]
)

st.bar_chart(load_factor_routes)

st.subheader("Raw Filtered Data")

st.dataframe(
    data,
    use_container_width=True
)
