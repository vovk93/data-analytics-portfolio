"""This script shows the step-by-step cleaning and validation performed on the extracted data. It contains
original debugging/testing notes for transparency."""
import numpy as np
import pandas as pd

MAX_WIND = 180
MAX_INSOLATION = 16
MAX_TEMP = 50

df_raw = pd.read_csv('all_weather_data.csv')

# Let's leave the original alone, and work with a copy
df = df_raw.copy()

# Let's rename the generic columns, based on the columns from the pdf
column_names = ['Station', 'Month', 'Year', 'Day', 'pressure_07h', 'pressure_14h',
                'pressure_21h', 'avg_pressure', 'max_temp', 'min_temp', 'temp_amp',
                'min_5cm', 'temp_07h', 'temp_14h', 'temp_21h', 'avg_temp', 'humidity_07h', 'humidity_14h',
                'humidity_21h', 'avg_humidity', 'water_vapor_pressure_07h', 'water_vapor_pressure_14h',
                'water_vapor_pressure_21h',
                'avg_water_vapor_pressure', 'wind_direction_07h', 'wind_speed_07h', 'wind_direction_14h',
                'wind_speed_14h',
                'wind_direction_21h', 'wind_speed_21h', 'avg_wind_speed', 'insolation', 'cloudiness_07h',
                'cloudiness_14h', 'cloudiness_21h', 'avg_cloudiness', 'precipitation', 'total_snow_cover',
                'new_snow_cover']

# Columns which should be numeric by nature
numeric_columns = ['pressure_07h', 'pressure_14h',
                   'pressure_21h', 'avg_pressure', 'max_temp', 'min_temp', 'temp_amp',
                   'min_5cm', 'temp_07h', 'temp_14h', 'temp_21h', 'avg_temp', 'humidity_07h', 'humidity_14h',
                   'humidity_21h', 'avg_humidity', 'water_vapor_pressure_07h', 'water_vapor_pressure_14h',
                   'water_vapor_pressure_21h',
                   'avg_water_vapor_pressure', 'wind_speed_07h', 'wind_speed_14h', 'wind_speed_21h', 'avg_wind_speed',
                   'insolation', 'cloudiness_07h',
                   'cloudiness_14h', 'cloudiness_21h', 'avg_cloudiness', 'precipitation', 'total_snow_cover',
                   'new_snow_cover']

# Replacing the commas with dots, to be able to create floats later on. Naming the columns correctly
df.replace(',', '.', regex=True, inplace=True)
df.drop(columns='Data37', inplace=True)
df.columns = column_names


# Now, we need to see which columns have characters as values, and should be cleaned of them
def num_col_check():
    for col in numeric_columns:
        s = df[col]
        numeric = pd.to_numeric(s, errors='coerce')
        non_numeric_mask = numeric.isna() & s.notna()
        non_numeric_values = s[non_numeric_mask].unique()
        if len(non_numeric_values) > 0:
            print(f"The symbols appearing in the column '{col}' are: {non_numeric_values}")
            print(f"Number of non-numeric values for '{col}': {non_numeric_mask.sum()}")
            print(f"Number of originally NaN values for '{col}': {df[col].isna().sum()}")


def str_col_check():
    cols_to_check = ['Station', 'wind_direction_07h', 'wind_direction_14h', 'wind_direction_21h']
    for col in cols_to_check:
        print(f"Unique values in column '{col}' are: {df[col].unique()}")


def col_outliers():
    for col in numeric_columns:
        max_val = df[col].max()
        print(f"{col}: max = {max_val}")
        min_val = df[col].min()
        print(f"{col}: min = {min_val}\n")


# Columns and methods to handle missing/wrong data
columns_to_clean = ['min_5cm', 'wind_speed_07h', 'wind_speed_14h', 'wind_speed_21h', 'avg_wind_speed',
                    'insolation', 'precipitation', 'total_snow_cover', 'new_snow_cover']
columns_to_coerce = ['min_5cm', 'wind_speed_07h', 'wind_speed_14h', 'wind_speed_21h', 'avg_wind_speed',
                     'insolation']
columns_to_impute = ['precipitation', 'total_snow_cover', 'new_snow_cover']

wind_columns = ['wind_direction_07h', 'wind_direction_14h', 'wind_direction_21h']

wind_speed_columns = ['wind_speed_07h', 'wind_speed_14h', 'wind_speed_21h', 'avg_wind_speed']

# Wrongly assigned values for 'total_snow_cover', if it has 3 or 4 digits, should be split
c1 = "total_snow_cover"
c2 = "new_snow_cover"

mask = (
        df[c1].notna()
        & df[c2].isna()
        & df[c1].str.len().isin([3, 4])
)

df.loc[mask, c2] = df.loc[mask, c1].str[2:]
df.loc[mask, c1] = df.loc[mask, c1].str[:2]

# Of the characters not being a number or '-', '.', we have 'ESE' appearing for three columns.
# I am suspecting that the whole row has been moved with some additional number that should not have been there

# Row index with additional wrongly inserted number: 942
# We should correct this as follows:

row_idx = 942

# get column names
cols = list(df.columns)

# find where the shift starts
shift_pos = cols.index('pressure_07h')

# get the row as a plain Python list
row = list(df.loc[row_idx])

# shift values one place to the left starting at pressure_07h
for i in range(shift_pos, len(row) - 1):
    row[i] = row[i + 1]

# last column has no real value
row[-1] = pd.NA

# put the corrected row back
df.loc[row_idx] = row

# Number of originally NaN values for 'total_snow_cover': 1 - the column before it has a huge number,
# should be divided up. For 'new_snow_cover' it is 2, that should be checked too
total_snow_nan_index = df.index[df['total_snow_cover'].isna()].to_list()
new_snow_nan_index = df.index[df['new_snow_cover'].isna()].to_list()
# By inspecting the original pdf, the issue becomes clear. Precipitation in this row is rounded to two decimals,
# instead of one. This is why the next two columns have become wrongly joined with the precipitation number.
val = df.loc[total_snow_nan_index[0], 'precipitation']

df.loc[total_snow_nan_index, 'precipitation'] = val[:4]  # "4.21"
df.loc[total_snow_nan_index, 'total_snow_cover'] = val[4:6]  # "00"
df.loc[total_snow_nan_index, 'new_snow_cover'] = val[6:8]  # "06"

# The new_snow_cover has one more NaN value, which is from the same row index 942 previously moved one field to the
# left, so that is why the last column became NaN. I will leave it as NaN, as the whole column will be imputed anyway.

# Non-numeric columns should also be inspected, such as wind direction. Do they have symbols which aren't standard,
# such as '-'? Any other?
# str_col_check()
# No other non-standard symbols detected other than '-', which represents a NaN, and all wind directions are present.

# Let's check the formatted columns we have so far, and do they have the right spread, and validate them. These are
# columns 'Station', 'Month', 'Year', 'Day' print(df_clean['Station'].value_counts())

# # Rows per year
# print(df_clean.groupby('Year').size())
#
# # Rows per month (across all years)
# print(df_clean.groupby('Month').size())
#
# # Rows per day of month (1-31)
# print(df_clean.groupby('Day').size())

# print(df_clean['Station'].unique())
# print(df_clean['Year'].unique())
# print(df_clean['Month'].unique())
# print(df_clean['Day'].unique())


# Let's remove the symbols from numeric columns, and coerce them
# num_col_check()
for col in columns_to_coerce:
    df[col] = pd.to_numeric(df[col], errors='coerce')
# And then impute missing values from the respective columns
for col in columns_to_impute:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
# Then, the numeric columns with no symbols should also be transformed
for col in numeric_columns:
    if col not in columns_to_coerce:
        if col not in columns_to_impute:
            df[col] = pd.to_numeric(df[col])
# Lastly, change '-' symbols in string columns to NaN
for col in wind_columns:
    df[col] = df[col].replace('-', np.nan)

# Next up, look at outliers. Should consult with literature to check what are normal and expected values
# col_outliers()

for col in wind_speed_columns:
    df.loc[df[col] > MAX_WIND, col] = np.nan

df.loc[df['min_5cm'] > MAX_TEMP, 'min_5cm'] = np.nan
df.loc[df['insolation'] > MAX_INSOLATION, 'insolation'] = np.nan

# col_outliers()

df.to_csv("cleaned_dataset.csv", index=False)
