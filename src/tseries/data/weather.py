import requests
import polars as pl


# %% GET DAILY TIME SERIES TEMPERATURE SINCE 2010


def get_daily():
    POST_DATA = {"stns": "260", "vars": "TG", "start": "19800101", "end": "19901231", "fmt": "json"}

    url = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"
    r = requests.post(url, data=POST_DATA)
    data = r.json()

    SCHEMA = pl.Schema({"date": pl.Utf8, "TG": pl.Int64})
    df = pl.from_dicts(data, schema=SCHEMA)
    df = df.with_columns(pl.col("date").str.strptime(pl.Datetime(time_unit="ms", time_zone="UTC")).dt.date())
    return df


# %% GET HOURLY DATA


def get_hourly():
    POST_DATA = {"stns": "260", "vars": "TEMP", "start": "2025010101", "end": "2025123124", "fmt": "json"}

    url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"
    r = requests.post(url, data=POST_DATA)
    data = r.json()

    SCHEMA = pl.Schema(
        {
            "date": pl.Utf8,
            "T": pl.Int64,
            "hour": pl.Int64,
        }
    )
    df = pl.from_dicts(data, schema=SCHEMA)
    df = (
        df.with_columns(
            pl.col("date").str.strptime(pl.Datetime(time_unit="ms", time_zone="UTC")).dt.replace_time_zone(None)
        ).with_columns((pl.col("date").cast(pl.Datetime) + pl.duration(hours=pl.col("hour"))).alias("datetime"))
    ).select(["datetime", "T"])
    return df


# %%

df = get_daily()

# %%

import matplotlib.pyplot as plt

"""
>>> plt.gcf().dpi

"""
some_dpi = 100
dim_x = 1920
dim_y = 1080

# remove the frame of the Figure
fig, ax = plt.subplots(figsize=(dim_x / some_dpi, dim_y / some_dpi), dpi=some_dpi, frameon=True)
ax.scatter(x=df["date"], y=df["TG"])
ax.set_xlabel("x-as")
ax.set_ylabel("y-as")
# make the Axes transparent
ax.patch.set_alpha(0.0)
fig.tight_layout()
plt.show()
