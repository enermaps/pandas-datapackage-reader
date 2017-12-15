import os
import pandas as pd
import pytest
import requests
import sys

from datetime import datetime, date, time
from pandas_datapackage_reader import read_datapackage


path = os.path.dirname(__file__)


def test_local_package():
    dp = read_datapackage(os.path.join(path, "test-package"))
    assert isinstance(dp, dict)
    assert "moredata" in dp.keys()
    assert "data" in dp.keys()


def test_load_single_resource():
    df = pd.read_csv(os.path.join(path, "test-package/moredata.csv"))
    moredata = read_datapackage(os.path.join(path, "test-package"), "moredata")
    assert df.equals(moredata)


def test_load_multiple_resources():
    dp = read_datapackage(os.path.join(path, "test-package"),
                          ["data", "moredata"])
    assert "data" in dp.keys()
    assert "moredata" in dp.keys()


def test_remote_package():
    url = ("https://github.com/rgieseke/pandas-datapackage-reader/"
           "raw/master/tests/test-package/datapackage.json")
    dp = read_datapackage(url)
    assert isinstance(dp, dict)
    assert "moredata" in dp.keys()
    assert isinstance(dp["moredata"], pd.DataFrame)
    assert "data" in dp.keys()


def test_not_existing_remote_package():
    with pytest.raises(requests.exceptions.HTTPError):
        dp = read_datapackage("http://www.example.com")


def test_github_url():
    url = "https://github.com/datasets/country-codes"
    dp = read_datapackage(url)
    assert isinstance(dp, pd.DataFrame)


def test_github_url_with_trailing_slash():
    url = "https://github.com/datasets/country-codes/"
    dp = read_datapackage(url)
    assert isinstance(dp, pd.DataFrame)

@pytest.mark.skipif(sys.version_info < (3, 4), reason="requires pathlib")
def test_pathlib_posixpath():
    from pathlib import Path
    path = Path(__file__).parents[0]
    dp = read_datapackage(path / "test-package")
    assert "data" in dp.keys()


def test_ignore_missing_values():
    df = read_datapackage(os.path.join(path, "test-package"), "data")
    assert df.loc["c"].value == "NA"


def test_missing_integer_values():
    df_wo_index = read_datapackage(
        os.path.join(path, "test-package"),
        "datawithoutindex"
    )
    assert pd.isnull(df_wo_index.iloc[1].intvalue)
    assert df_wo_index["intvalue"].dtype == pd.np.dtype("O")


def test_missing_integer_values_with_index():
    df = read_datapackage(os.path.join(path, "test-package"), "datawithindex")
    assert pd.isnull(df.loc[2].intvalue)
    assert df["intvalue"].dtype == pd.np.dtype("O")


def test_datetimes():
    # Default test date/time '2017-01-01 01:23:45'
    df = read_datapackage(os.path.join(path, "test-package"), "datetimes")
    assert df["date"].loc[0] == date(2017, 1, 1)
    assert df["datetime"].loc[0] == datetime(2017, 1, 1, 1, 23, 45)
    assert df["time"].loc[0] == time(1, 23, 45)
    assert df["year"].loc[0] == pd.Period("2017")
    assert df["yearmonth"].loc[0] == pd.Period("2017-01")
    assert df["yearmonth"].loc[0] == pd.Period("2017-01")
    assert df["dayfirstdate"].loc[0] == date(2017, 12, 13)
