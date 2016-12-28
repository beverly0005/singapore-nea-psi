# singapore-nea-psi
Python script to scrape historical [PSI](https://en.wikipedia.org/wiki/Pollutant_Standards_Index#Definition_of_the_PSI_used_in_Singapore) readings from www.haze.gov.sg into [pandas DataFrame](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) and [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) formats.

## Context
During the 2013 Southeast Asian haze, I was interning with the Solar Energy Research Institute of Singapore (SERIS). One of my tasks was to transcribe a year of PSI readings (one day of PSI readings -> one CSV file), which I chose to automate.

Although my 3-year NDA has expired, I will not publish the photovoltaic system data that was examined in connection with this dataset. Because I played no role in its collection, I continue to identify that photovoltaic system data as the property of SERIS.

Consequently, this dataset is of limited use in and of itself. It may however be useful when paired with other datasets, for example in searching for possible correlations with PSI.

**As of April 2016, data.gov.sg publishes an API for obtaining [PSI](https://data.gov.sg/dataset/psi) and [PM2.5](https://data.gov.sg/dataset/pm2-5) readings**. Because as of December 2016 the documentation links are still broken, I have chosen to publish this script - for future data collection, however, **I recommend using the data.gov.sg API directly**.

## Usage Notes

### Script

Run this script from the command line with `python psi_scraper.py`. This script should continue to work as long as the HTML structure of the `www.haze.gov.sg/haze-updates/historical-psi-readings/` page does not change.

### Dataset

There are three convenience datasets provided in the `datasets` folder, 

1. `datasets/sg-nea-psi.pickle`: one `pickle` containing a DataFrame with all the data
2. `datasets/sg-nea-psi.csv`: one `CSV` containing all the data
3. `datasets/sg-nea-psi.zip`: individual `CSV` files by day

The provided datasets range from the beginning of published data until the end of November 2016, i.e. **2010-01-01 to 2016-11-30**. The data is as-is from the NEA website, i.e. you will still need to perform data munging.

Furthermore note that prior to April 1, 2014, there were PM2.5 readings. However, beginning from that date inclusive, PM2.5 readings were subsumed into PSI.

## Requirements

This script has been ported to [Python 3.5](https://www.python.org/downloads/release/python-350/) and uses the following libraries:

- [bs4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [requests](http://docs.python-requests.org/en/master/) for HTTP requests
- [pandas](http://pandas.pydata.org/) for data analysis

## Legal

Do whatever you want to the code, attribution is up to you. Note, however, that the dataset ultimately belongs to the [National Environment Agency of Singapore](http://www.nea.gov.sg/). If there are any legal and/or licensing issues related to this repository, please send me a pull request or email.