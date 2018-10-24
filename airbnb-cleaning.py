#!/usr/bin/env python
import os
import sys
from icalendar import Calendar, Event
import datetime
import requests
import pytz
from yaml import load as load_yaml

def cal_from_url(url):
    r = requests.get(url)
    cal = Calendar.from_ical(r.text)
    return cal

def get_events(cal, start_date, end_date, ctx = {}):
    for component in cal.walk():
        if component.name == "VEVENT":
            cal_start_date = component.get('dtstart').dt
            if cal_start_date >= start_date and cal_start_date <= end_date:
                component.update(ctx)
                yield component

def add_time_of_day(dt, hh, mm = 0):
    return datetime.datetime(dt.year, dt.month, dt.day, hh, mm, 0, tzinfo=pytz.timezone('America/Chicago'))

def update_event_time(event, key, hh, mm = 0):
    dt = add_time_of_day(event.get(key).dt, hh, mm)
    del event[key]
    event.add(key, dt)

if __name__ == "__main__":
    with open('cals.yaml', 'r') as f:
        cal_config = load_yaml(f)
    today = datetime.date.today()
    start_date = today + datetime.timedelta(-today.weekday()-1)
    end_date = start_date + datetime.timedelta(days=cal_config.get('days_future', 100))

    print('Generating schedule for %s - %s' % (start_date, end_date))
    print('')
    print('Calendars:')

    cleaning_cal = Calendar()
    combined_reservation_cal = Calendar()

    reservations = []
    for cal_info in cal_config['calendars']:
        cal = cal_from_url(cal_info['url'])
        print('- %s' % cal_info['name'])
        reservations += get_events(cal, start_date, end_date, {'unit' : cal_info['name']})
        for res_event in reservations:
            event_clean = Event()

            dt = res_event.get('dtstart').dt

            event_clean['uid'] = 'x-clean.' + res_event['uid']
            event_clean.add('dtstart', add_time_of_day(dt, 12))
            event_clean.add('dtend', add_time_of_day(dt, 15))
            event_clean.add('summary', 'Clean ' + res_event.get('unit'))

            update_event_time(res_event, 'dtstart', 15)
            update_event_time(res_event, 'dtend', 12)

            combined_reservation_cal.add_component(res_event)
            cleaning_cal.add_component(event_clean)

    print('')
    print('Writing:')
    print('- Cleaning.ics')
    with open('Cleaning.ics', 'wb') as f:
        f.write(cleaning_cal.to_ical())
        f.close()

    print('- Reservations.ics')
    with open('Reservations.ics', 'wb') as f:
        f.write(combined_reservation_cal.to_ical())
        f.close()

    print('')
    print('Cleaning Summary:')
    print('')
    reservations = sorted(reservations, key=lambda r: r.get('dtstart').dt)

    last_date = None
    for res in reservations:
        show_header = False
        dt = res.get('dtstart').dt
        if dt != last_date:
            if last_date is not None:
                print('\n')
            last_date = dt
            show_header = True
        if show_header:
            txt = dt.strftime('%A %B %d, %Y')
            txt += '\n' + '-' * len(txt) + '\n'
            print(txt)
        print('☐ Clean ' + res.get('unit'))
