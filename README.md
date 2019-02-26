# mint-cli
Display account net worth, emergency budget and current monthly budget in your terminal from your Mint account.

## Requirements
```> pip3 install mintapi python-dotenv tabulate```

```> pacman -S(apt install) chromium-chromedriver```

## Setup

```> cp .env.example .env```
```> vim .env```

Use editor to edit .env file.

## Usage

```
./mint-cli
usage: mint-cli [-h] [-v] [-n] [-b] [-e] [-r]

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbosity  increase output verbosity
  -n, --net        show net worth and account amounts
  -b, --budget     show current budget and savings rate
  -e, --emergency  show emergency fund timeline
  -r, --refresh    refresh data from mint account
  ```

## Usage Example
Display buget using info from mint.com account and .env
### .env
![alt text](https://i.imgur.com/bw07nJm.jpg)

### Output
```> ./mint-cli -rb```
![alt text](https://i.imgur.com/D2vZ066.jpg)
