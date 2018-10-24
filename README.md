# airbnb-utils

## Airbnb Cleaning

Generate a consolidated calendars of reservations and cleanings from multiple
calendars.

`airbnb-cleaning.py`

## Airbnb Revenue

`airbnb-revenue.py`

1. Go to <https://www.airbnb.com/users/transaction_history>
2. From "Completed Payouts" tab
  - Choose date (typically YTD)
  - Press "Download CSV"
  - Save this as "airbnb_2018.csv"
3. From "Upcoming Payouts" tab
  - Choose date (typically thru end of year)
  - Press "Export to CSV"
  - Save this as "airbnb_pending.csv"
4. Run `./airbnb-revenue.py`
