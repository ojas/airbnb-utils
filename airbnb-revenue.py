#!/usr/bin/env python
from collections import Counter
import csv
import json
import requests
import os
from dateutil.parser import parse as parse_date
from calendar import monthrange
import datetime

FIRST_AVAIL_DATES = {
    'Modern, Minimal, Chill Airstream in East Austin' : datetime.datetime(2017,2,10),
    'Modern Condo with Amazing Rooftop!' : datetime.datetime(2017,3,1),
    'Chic East Side House' : datetime.datetime(2017,1,1),
    'Cute Tiny Home with Loft and Deck in East Austin' : datetime.datetime(2017,1,1),
}

class Reservation:
    def __init__(self, row):
        # self.start_date = parse_date(row['Start Date'])
        self.start_date = parse_date(row['Date']) - datetime.timedelta(days=1)
        self.confirmation_code = row['Confirmation Code']
        self.nights = int(row['Nights'])

        days_in_month = monthrange(self.start_date.year, self.start_date.month)[1]

        if self.nights > days_in_month:
            # print(self.start_date, days_in_month)
            self.nights = days_in_month

        self.end_date = self.start_date + datetime.timedelta(days=self.nights)

        self.amount = float(row['Amount'])
        self.host_fee = float(row['Host Fee'] if row['Host Fee'] != '' else 0)
        self.cleaning_fee = float(row['Cleaning Fee'] if row['Cleaning Fee'] != '' else 0)
        self.nightly_price = self.amount / self.nights
        self.listing = row['Listing']
        self.month = '%s.%s' % (self.start_date.year, self.start_date.month)


DAY_OF_WEEK_BY_IDX = [
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun',
]

SOURCES = [
    './airbnb-data/airbnb_2018.csv',
    './airbnb-data/airbnb_pending.csv',
]

OUTFILE = './airbnb-data/airbnb-to-date.csv'

OCCUPANCY_TARGETS = {
    'Chic East Side House' : 0.95,
    'Modern, Minimal, Chill Airstream in East Austin' : 0.9,
    'Modern Condo with Amazing Rooftop!' : 0.1,
    'Cute Tiny Home with Loft and Deck in East Austin' : 0.9,
}

def get_reservations():
    rows = []
    for path in SOURCES:
        full_path = os.path.expanduser(path)
        with open(os.path.expanduser(path), 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Type'] == 'Reservation':
                    rows.append(Reservation(row))
                # if row['Start Date']:
                #     row['Date'] = parse_date(row['Start Date'])
                # rows.append(row)
    return rows

# def get_end_of_month(dt):
#     yr = dt.year
#     mo = dt.month + 1
#     if mo>12:
#         mo = 1
#         yr += 1
#     return datetime.datetime(yr, mo, 1) - datetime.timedelta(days=1)


if __name__ == "__main__":
    reservations = get_reservations()
    now = datetime.datetime.now()
    # end_date = get_end_of_month(now)
    end_date = datetime.datetime(now.year, now.month, now.day)
    # now = end_of_month
    #
#    TODO: monthly income by property

    # reservations = [r for r in reservations if r.start_date <= end_date]
    print('Filtering thru %s' % end_date)
    print()

    listings = []
    listing_infos = {}
    for r in reservations:
        if r.listing not in listings:
            listings.append(r.listing)
            listing_infos[r.listing] = {
                'name' : r.listing,
                'date_start' : FIRST_AVAIL_DATES[r.listing],
                # 'date_start' : datetime.datetime(2099, 1, 1)
            }
        # if r.start_date < listing_infos[r.listing]['date_start']:
        #     listing_infos[r.listing]['date_start'] = r.start_date

        # row['Nights'] = int(row['Nights'])
        # row['Amount'] = int(row['Amount'])
        # row['Host Fee'] = int(row['Host Fee'])
        # row['Cleaning Fee'] = int(row['Cleaning Fee'])
        # row['Nightly Price'] = row['Amount'] / row['Nights']
        # # row['Nightly Price'] = float(row['Nightly Price'])


    # days might be off by 1
    print(listing_infos)

    c = Counter()
    weekday_counter = Counter()
    weekday_listing_counter = Counter()

    conf_ids = {}

    for r in reservations:

        # actual_days_booked = r.end_date
        if end_date > r.end_date:
            recognized_days = r.nights
        elif r.start_date > end_date:
            pass
        else:
            recognized_days = (end_date - r.start_date).days
            # print(recognized_days, r.start_date, r.end_date, end_date)

        if 'Condo' in r.listing:
            # recognized_days = r.end_date - r.start_date
            print(recognized_days)
        c['TotalAmount_%s' % r.listing] += r.amount # TODO - this is wrong given recognized_days
        # c['TotalNights_%s' % r.listing] += recognized_days
        c['TotalNights_%s' % r.listing] += r.nights

        for i in range(recognized_days):
            weekday = ( r.start_date.weekday() + i ) % 7
            weekday_counter['Nights_%s' % weekday] += 1
            weekday_counter['Amount_%s' % weekday] += r.nightly_price
            weekday_listing_counter['Nights_%s_%s' % (weekday, r.listing)] += 1
            weekday_listing_counter['Amount_%s_%s' % (weekday, r.listing)] += r.nightly_price

    summary = dict(c)


    for listing in listings:
        summary['AverageNightly Price_%s' % listing] = int(summary['TotalAmount_%s'%listing] / summary['TotalNights_%s'%listing])

        # actual_days_booked

        # end_date

        nums_days = now - listing_infos[listing]['date_start']
        actual_occu = summary['TotalNights_%s'%listing] / nums_days.days

        print(listing, nums_days.days, actual_occu)

        # summary['ActualOccupancy_%s' % listing] =


        int(summary['TotalAmount_%s'%listing] / summary['TotalNights_%s'%listing])
        summary['ProjectedAnnualIncome_%s' % listing] = int(summary['AverageNightly Price_%s' % listing] * 365 * OCCUPANCY_TARGETS[listing])

    # print(summary)
    # exit()

    weekday_summary = dict(weekday_counter)
    for i in range(7):
        weekday_summary['Avg_%s' % i] = int(weekday_summary['Amount_%s' % i] / weekday_summary['Nights_%s' % i])
        for l in listings:
            # try:
            weekday_listing_counter['Avg_%s_%s' % (i, l)] = int(weekday_listing_counter['Amount_%s_%s' % (i, l)] / weekday_listing_counter['Nights_%s_%s' % (i, l)])
            # except ZeroDivisionError:
            #     weekday_listing_counter['Avg_%s_%s' % (i, l)] = 0


    # print(json.dumps(weekday_listing_counter, indent=2))
    # exit()

    s = """
AVG...

S %(Avg_6)s
M %(Avg_0)s
T %(Avg_1)s
W %(Avg_2)s
R %(Avg_3)s
F %(Avg_4)s
S %(Avg_5)s

""".strip() % weekday_summary

    for i in [6,0,1,2,3,4,5]:
        print('%s\t%s' % (DAY_OF_WEEK_BY_IDX[i], weekday_summary['Avg_%s' % (i, )]))
    print()

    for listing in listings:
        avg = summary['AverageNightly Price_%s' % listing]
        print('Unit\t%s' % listing)
        print('Avg Nightly\t%s' % avg)
        print('Annual\t%s' % summary['ProjectedAnnualIncome_%s' % listing])
        for i in [6,0,1,2,3,4,5]:
            amt = weekday_listing_counter['Avg_%s_%s' % (i, listing)]
            print('%s\t%s\t%5s%%' % (DAY_OF_WEEK_BY_IDX[i], amt, int(amt/avg*100)))
        print()



    print(weekday_counter)
    fieldnames = [f for f in dir(reservations[0]) if not f.startswith('__')]

    with open(os.path.expanduser(OUTFILE), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in reservations:
            writer.writerow(r.__dict__)
