"""This with fetch forecast data from Dark Sky
    This works as below.
    - Reads two must arguments as required one
    - Provide date in mm-dd-yyyy in string format"""

from datetime import datetime as dt, timedelta as td, date
import time, sys
import json, pandas as pd
import requests


def is_valide_date(date_text):
    try:
        if date_text != dt.strptime(date_text, '%m-%d-%Y').strftime('%m-%d-%Y'):
            raise ValueError
        return True
    except ValueError:
        return False


def weather_frcst(startdate, enddate):
    weather_keys = {
        'key': "ProvideYourKey",
        'location': "52.100759,-106.358137",
    }
    forecase_3yr = {}
    bad_responses = {}
    history_data={}
    url = "https://api.darksky.net/forecast/" + weather_keys.get("key") + "/" + weather_keys.get("location")
    date_format = '%m-%d-%Y'
    if is_valide_date(startdate) and is_valide_date(enddate) and startdate < enddate:
        startdate = dt.strptime(startdate, date_format)
        enddate = dt.strptime(enddate, date_format)
        years = list(range(startdate.year, enddate.year+1))
        diff_days = (enddate - startdate).days
        history_data = {year:[] for year in years}
        for a_day in range(diff_days,-1,-1):  # year=365 days and 1 day less at a time
            current_day = enddate-td(days=a_day)
            time_stamp = str(time.mktime(current_day.timetuple()))
            time_stamp = time_stamp[:time_stamp.index('.')]
            url = url + ',' + time_stamp
            day_forcast = requests.get(url=url)
            url = "https://api.darksky.net/forecast/" + weather_keys.get("key") + "/" + weather_keys.get("location")
            if day_forcast.status_code in (200, 201):
                json_forecast = json.loads(day_forcast.text)
                if current_day.year in years:
                    history_data[current_day.year].append(json_forecast["hourly"]["data"])
            else:
                bad_responses[str(current_day)] = day_forcast.text

    return history_data, bad_responses

if __name__ == '__main__':
    try:
        if isinstance(sys.argv[1], str) and isinstance(sys.argv[2], str):
            startdate = sys.argv[1]
            enddate = sys.argv[2]
            weather_hstry, bad_responses = weather_frcst(startdate,enddate)
            filename = "forecast_"
            for year in weather_hstry.keys():
                resp_data = [x for y in weather_hstry[year] for x in y]
                filename=filename+str(year)
                pd.read_json(json.dumps(resp_data)).to_csv(filename, index=False)
    except:
        raise ValueError
