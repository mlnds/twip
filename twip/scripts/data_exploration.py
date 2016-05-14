#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Load, clean, and do some basic data exploration on the data

- load tweets (previously concatenated with cat_tweets) into a single DataFrame
- drop columns with mostly null values
- drop rows with mostly null values
- use DataFrame.describe to get basic stats on each column
- use pandas_profiler.ProfileReport to produce histograms, etc in HTML
"""
from __future__ import division, print_function, absolute_import

import os
from decimal import Decimal
from traceback import print_exc

import pandas as pd
import pandas_profiling


# you really want to be efficient about RAM, so user iter and itertools
# from itertools import izip
from twip.constant import DATA_PATH

# this should load 100k tweets in about a minute
print('Loading tweets (could take a minute or so)...')
df = pd.read_csv(os.path.join(DATA_PATH, 'all_tweets.csv'), encoding='utf-8', engine='python')
# in iPython Notebook print out df.columns to show that many of them contain dots
# rename the columns to be attribute-name friendly
df.columns = [label.replace('.', '_') for label in df.columns]

# in iPython Notebook, try dropping with lower thresholds, checking column and row count each time
print('The raw table shape is {}'.format(df.shape))
nonnull_rows = 330
nonnull_cols = 50
df = df.dropna(axis=1, thresh=nonnull_rows)
print('After dropping columns with fewer than {} nonnull values, the table shape is {}'.format(nonnull_rows, df.shape))
df = df.dropna(axis=0, thresh=nonnull_cols)
print('After dropping rows with fewer than {} nonnull values, the table shape is {}'.format(nonnull_cols, df.shape))


# in ipython notebook, explore and describe the DataFrame columns
print('Of the {} columns, {} are actually DataFrames'.format(len(df.columns), sum([not isinstance(df[col], pd.Series) for col in df.columns])))
# remove dataframes with only 2 columns and one is the _str of the other:
for col in df.columns:
    if isinstance(df[col], pd.DataFrame):
        print('Column {} is a {}-wide DataFrame'.format(col, len(df[col].columns)))
        if df[col].columns[1] == df[col].columns[0] + '_str':
            print('Column {} looks easy because it has sub-columns {}'.format(col, df[col].columns))
            df[col] = df[col][df[col].columns[1]]
        else:
            try:
                assert(float(df[col].iloc[:, 0].max()) == float(df[col].iloc[:, 1].max()))
                df[col] = df[col].fillna(-1, inplace=False)
                series = pd.Series([int(Decimal(x)) for x in df[col].iloc[:, 1].values]).astype('int64').copy()
                del df[col]
                df[col] = series
                print('Finished converting column {} to type {}({})'.format(col, type(df[col]), df[col].dtype))
            except:
                print_exc()

print('Of the {} columns, {} are still DataFrames after trying to convert both columns to long integers'.format(
    len(df.columns), sum([not isinstance(df[col], pd.Series) for col in df.columns])))

print('df.describe() stats:')
desc = df.describe()
for col, stats in desc.T.iterrows():
    print('')
    print('{} ({})'.format(col, df[col].dtype if isinstance(df[col], pd.Series) else type(df[col])))
    print(stats)


# this is redundant with stats above and takes way longer than it should (30 minutes?)
# print('Column, Count, Min, Mean, Max:')
# for k, c, colmin, colmean, colmax in izip(df.columns, df.count().T, df.min().T, df.mean().T, df.max().T):
#     print('{:40s}\t{}\t{}\t{}\t{}'.format(k, c, colmin, colmean, colmax))

# this takes a few minutes
print('Trying to compute a ProfileReport, including correlation between columns, skew etc')
# pandas_profiling.ProfileReport raises Tkinter exceptions before it can produce any output,
#  at least describe produces a dataframe of stats
report = pandas_profiling.describe(df)
print(report['table'])

print('')
for col, stats in report['variables'].iterrows():
    print('')
    print(col)
    # print('{} ({})'.format(col, df[col].dtype if isinstance(df[col], pd.Series) else type(df[col])))
    print(stats)

print('')
for col, stats in report['freq'].iteritems():
    print('')
    print(stats)
