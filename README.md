# pynab_monzo

![CI](https://github.com/MBrighty/pynab_monzo/workflows/CI/badge.svg?branch=master&event=push)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

pynab_monzo is a Flask application for automatically importing Monzo transactions into You Need a Budget (YNAB) budgets.

## Environment Variables

* `YNAB_PAT`: YNAB API token -  used to make requests to YNAB.
* `MONZO_TOKEN`: Monzo API token - used to make requests to Monzo.
* `MONZO_ACCOUNT`: Monzo account ID - used in registering a webhook.
* `MONZO_ACCOUNT_NAME`: Name of Monzo account within YNAB - used in choosing which YNAB account to create the transaction in.
* `REDIS_URL`: URL of a Redis server - used to prevent duplicate requests creating multiple identical transactions.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Pull requests without tests will be declined.