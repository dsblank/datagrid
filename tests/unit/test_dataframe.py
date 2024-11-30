import numpy as np
import pandas as pd
from pandas._testing import (
    makeCustomDataframe,
    makeDataFrame,
    makeMixedDataFrame,
    makePeriodFrame,
    makeTimeDataFrame,
)

import datagrid


def makeMissingDataframe():
    df = makeDataFrame()
    data = df.values
    data = np.where(data > 1, np.nan, data)
    return pd.DataFrame(data, index=df.index, columns=df.columns)

def test_makeCustomDataframe():
    df = makeCustomDataframe(100, 25)
    dg = datagrid.read_dataframe(df)
    assert len(dg) == 100
    assert len(dg[0]) == 25
    dg.save()

def test_makeDataFrame():
    df = makeDataFrame()
    dg = datagrid.read_dataframe(df)
    assert len(dg) == 30
    assert len(dg[0]) == 4
    dg.save()

def test_makeMissingDataframe():
    df = makeMissingDataframe()
    dg = datagrid.read_dataframe(df)
    assert len(dg) == 30
    assert len(dg[0]) == 4
    dg.save()

def test_makeMixedDataFrame():
    df = makeMixedDataFrame()
    dg = datagrid.read_dataframe(df)
    assert len(dg) == 5
    assert len(dg[0]) == 4
    dg.save()

def test_makePeriodFrame():
    df = makePeriodFrame()
    dg = datagrid.read_dataframe(df)
    assert len(dg) == 30
    assert len(dg[0]) == 4
    dg.save()

def test_makeTimeDataFrame():
    df = makeTimeDataFrame()
    dg = datagrid.read_dataframe(df)
    assert len(dg) == 30
    assert len(dg[0]) == 4
    dg.save()
