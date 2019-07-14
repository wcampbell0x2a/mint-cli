# mint-cli
Terminal interface for the Intuit Mint budget system
Displays account net worth, emergency budget and current monthly budget.

## Requirements
```python: mintapi python-dotenv tabulate colorama```

```> pacman -S(apt install) chromium-chromedriver```

## Install from AUR

https://aur.archlinux.org/packages/mint-cli-git

When installed from the aur, the .env file is located at `/etc/mint-cli/.env`

## Install from source

Make sure to use the -l flag when installed from local, the .env file is expected to be in the git repo.

```> cp .env.example .env```
```> vim .env```

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
  -l, --local      use local data and .env

```

## Usage Example
Display buget using info from mint.com account and .env
### .env
![alt text](https://i.imgur.com/bw07nJm.jpg)

### Output
```> ./mint-cli -rb```
![alt text](https://i.imgur.com/D2vZ066.jpg)
