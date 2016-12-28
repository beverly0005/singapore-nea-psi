#!/usr/bin/env python3
import calendar
import collections
import datetime
import os

import bs4
import pandas as pd
import requests


NEA_URL = (r'http://www.haze.gov.sg/haze-updates/historical-psi-readings/'
           r'year/{year}/month/{month}/day/{day}')


def _get_nea_dict(url, dt_ymd):
    """
    Return (NEA PSI/PM2.5 data: OrderedDict, headers: list) for url.

    May raise requests.exceptions.RequestException.

    OrderedDict keys -- hour_text, '1am', '2am', '3pm' as reported by NEA
    headers -- ordered list of data columns

    url -- NEA_URL with year, month, day substituted
    dt_ymd -- datetime object with year, month, day
    """
    result = collections.OrderedDict()

    url = url.format(year=dt_ymd.year, month=dt_ymd.month, day=dt_ymd.day)
    req = requests.get(url)
    table = bs4.BeautifulSoup(req.text, 'lxml').find('table')
    rows = table.findAll('tr')

    # The PSI readings are
    # Time at 0
    # North at 1
    # South at 2
    # East at 3
    # West at 4
    # Central at 5
    # Overall at 6
    # The pattern is repeated for PM2.5 Concentration values

    headers = [
              'PSI-North',
              'PSI-South',
              'PSI-East',
              'PSI-West',
              'PSI-Central',
              'PSI-Overall'
              ]

    # prior to 2014-04-01, there were PM2.5 readings
    # on 2014-04-01, PM2.5 readings were subsumed into PSI
    pm_subsume_date = datetime.datetime(2014, 4, 1)

    if dt_ymd < pm_subsume_date:
        headers += [
                   'PM2.5-North',
                   'PM2.5-South',
                   'PM2.5-East',
                   'PM2.5-West',
                   'PM2.5-Central',
                   'PM2.5-Overall',
                   ]

    # Rows 0 and 1 are headers, skip
    for i in range(2, len(rows)):
        items = rows[i].findAll('td')
        hour = items[0].text
        result[hour] = collections.OrderedDict()

        for index, header in enumerate(headers, 1):
            result[hour][header] = items[index].text.strip()

    return result, headers


def _to_datetime(
        year, month, day,
        hour_text,
        timezone='+0800'
        ):
    """
    Return timezone-aware datetime with corrected day.

    Note that NEA is incorrect in PSI readings for 12am,
    e.g. their 2016-01-01 12am is really the next day 2016-01-02 00:00.
    This function fixes that ambiguity by reporting the correct time.

    hour_text -- as of 2016, NEA displays it as '1am', '2am', '3pm', ...
    timezone -- Singapore is UTC+8
    """
    date_string = '{year}-{month}-{day} {hour_text} {timezone}'

    date_string = date_string.format(
                                    year=year,
                                    month=month,
                                    day=day,
                                    hour_text=hour_text,
                                    timezone=timezone
                                    )
    dt = datetime.datetime.strptime(date_string, '%Y-%m-%d %I%p %z')

    # see docstring, we correct NEA
    if dt.hour == 0:
        dt = dt + datetime.timedelta(days=1)

    return dt


def _download_df(
                base_url,
                year_start=2010,
                year_end=None,
                month_start=1,
                month_end=12,
                day_start=1,
                day_end=None,
                verbose=True
                ):
    """
    Return a dataframe containing PSI and/or PM2.5 readings.

    Note that 2010-01-01 is the earliest possible date as per the NEA website.

    base_url -- NEA_URL
    all other date parameters are inclusive [start, end]
    verbose -- True to print every time a month is complete
    """
    result_odict = {}
    df_headers = []

    today = datetime.datetime.now()

    if year_end is None:
        year_end = today.year

    for year in range(year_start, year_end + 1):
        for month in range(month_start, month_end + 1):
            if verbose:
                print("Processing {}-{}".format(year, month))

            _, num_days = calendar.monthrange(year, month)

            first_day = 1
            last_day = num_days

            if (year == year_start and
                    month == month_start):
                first_day = day_start

            if (day_end is not None and
                    year == year_end and
                    month == month_end):
                last_day = day_end

            for day in range(first_day, last_day + 1):

                try:
                    ymd = datetime.datetime(year, month, day)
                    data, headers = _get_nea_dict(base_url, ymd)
                    if len(headers) > len(df_headers):
                        df_headers = headers

                    for hour_text in data:
                        timestamp = _to_datetime(year, month, day, hour_text)
                        result_odict[timestamp] = data[hour_text]

                except requests.exceptions.RequestException as e:
                    err_msg = 'Error for {}-{}-{}: {}\n'
                    err_msg = err_msg.format(year, month, day, str(e))
                    print(err_msg)

    df = pd.DataFrame.from_dict(result_odict, orient='index')
    df = df[df_headers]
    return df


def _save_csv_per_day(df, save_folder):
    """
    Save the dataframe data per day into individual CSV files. Sorts dataframe.

    save_folder -- CSV save folder
    """
    os.makedirs(save_folder, exist_ok=True)
    df.sort_index()

    curr_day = df.index.min()
    last_day = df.index.max()

    while curr_day <= last_day:
        curr = curr_day.replace(hour=0)
        until = curr_day.replace(hour=23)
        short_date = '{}.csv'.format(str(curr.date()))
        file_name = os.path.join(save_folder, short_date)

        df[curr:until].to_csv(file_name, index_label='Timestamp')
        curr_day = curr_day + datetime.timedelta(days=1)


def main(base_url):
    print('This will download PSI/PM2.5 readings published by NEA Singapore.')
    print('This may utilize significant amounts of bandwidth.')
    print()

    choice = input('To proceed, type Y, to abort, type N > ')
    if choice.lower() != 'y':
        return
    print()

    choice = input('Please enter the start year, month, and day\n'
                   'as three numbers, e.g. "2010 5 1" for May 1, 2010.\n'
                   'Or press enter to download from the start > ')
    year_start, month_start, day_start = 2010, 1, 1  # earliest possible date
    if choice != '':
        year_start, month_start, day_start = [int(x) for x in choice.split()]
    print()

    choice = input('Please enter the end year, month, and day\n'
                   'as three numbers e.g. "2010 5 1" for May 1, 2010.\n'
                   'Or press enter to download until today \n'
                   'PLEASE NOTE THAT NEA DATA MAY NOT BE COMPLETE\n'
                   'AND IS IN FACT ACCURATE ONLY UNTIL YESTERDAY > ')
    d = datetime.datetime.now()
    year_end, month_end, day_end = d.year, d.month, d.day
    if choice != '':
        year_end, month_end, day_end = [int(x) for x in choice.split()]
    print()

    choice = input('Do you want to keep track of the download?\n'
                   'Y for yes, N otherwise > ')
    verbose = False
    if choice.lower() == 'y':
        verbose = True
    print()

    filename = input('Please enter a filename to save as > ')

    choice = input('Please choose which file types to save:\n'
                   '1. pickled dataframe\n'
                   '2. csv (all)\n'
                   '3. csv (per day)\n'
                   'You may make multiple choices,\n'
                   'e.g. "1 3" without quotes\n\n'
                   'Choice > ')
    print()
    save_options = choice.split()

    print('Now downloading, please wait.')
    df = _download_df(
                    base_url,
                    year_start, year_end,
                    month_start, month_end,
                    day_start, day_end,
                    verbose
                    )
    print('Finished downloading.')
    print('Please check the above output for error messages, if any.\n')

    if '1' in save_options:
        df.to_pickle('{}.pickle'.format(filename))
    if '2' in save_options:
        df.to_csv('{}.csv'.format(filename))
    if '3' in save_options:
        _save_csv_per_day(df, filename)

    print('Files saved. Please check the folder this script is in.')

if __name__ == '__main__':
    main(NEA_URL)
