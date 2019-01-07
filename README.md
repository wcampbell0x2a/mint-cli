# Mint Display
Display account net worth, emergency budget and current monthly budget in your terminal from your Mint account.

## Requirements
```> pip3 install mintapi python-dotenv tabulate```

```> pacman -S(apt install) chromium-chromedriver```

## Setup

```> cp .env.example .env```

Use editor to edit .env file.

## Usage

```
./mint.py
usage: mint.py [-h] [-v] [-n] [-b] [-e] [-r]

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbosity  increase output verbosity
  -n, --net        show net worth and account amounts
  -b, --budget     show current budget and savings rate
  -e, --emergency  show emergency fund timeline
  -r, --refresh    refresh data from mint account
  ```
