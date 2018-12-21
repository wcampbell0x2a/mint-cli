#!/usr/bin/python3
##
# Script for displaying Mint.com information via terminal.
# See here for API usage: https://github.com/mrooney/mintapi
#
# See Example env file and create your own with identify as .env
#
# Author Wayne Campbell
# Found original net worth use on github somewhere
##

import argparse
import calendar
import datetime
import datetime
import json
import mintapi
import pprint
import os
from dotenv import load_dotenv, find_dotenv
from tabulate import tabulate
from colorama import init, Fore, Style

init()


def datetime_handler(x):
    """
    Helper function to load datetime json formats into python datetime.
    mintapi json files if saved need this functionality to work without
    throwing errors.
    """
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


def load_json(name):
    """
    Load json file in data directory
    Args:
        name(string): name of file to be loaded
    """
    try:
        with open(f'data/{name}.json') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Use -r to refresh and save json files")


def save_json(name, data):
    """
    Helper function to save python json data as files.
    Args:
        name(string): name of file
        data(json): data of file created
    """
    with open(f'data/{name}.json', 'w') as outfile:
        json.dump(data, outfile, default=datetime_handler)


def refresh(verbose):
    """
    Create json data files from the data provided by mintapi.
    Args:
        verbose(bool): If true, will print current username and password.
    """
    username = os.environ['MINT_USER']
    password = os.environ['MINT_PASS']
    if verbose:
        print(f'Logging as {username} with password: {password}')
    mint = mintapi.Mint(username, password)

    save_json('accounts', mint.get_accounts())
    save_json('net_worth', mint.get_net_worth())
    save_json('budgets', mint.get_budgets())

    print("mint data saved successfully")


def net_worth():
    """
    Display all accounts with the total amount in each account.
    Show the total amount at the end
    """
    print(Style.BRIGHT + Fore.BLUE + "ACCOUNTS" + Style.NORMAL + Fore.RESET)
    negativeAccounts = ['loan', 'credit']
    prevInstitution = ''
    accounts = []

    # Load data
    jsonaccounts = load_json('accounts')
    net_worth = load_json('net_worth')

    # Loop through accounts and display with due date
    for jsonaccount in jsonaccounts:
        institution = jsonaccount['fiName']
        if (institution == prevInstitution):
            institution = ''
        prevInstitution = jsonaccount['fiName']
        accountName = jsonaccount['accountName']
        balance = jsonaccount['currentBalance']
        due = None
        dueby = ''
        currency = jsonaccount['currency']
        if (jsonaccount['accountType'] in negativeAccounts):
            balance *= -1
            balance = Fore.RED + str(balance) + Fore.RESET
            due = jsonaccount['dueAmt']
            dueby = currency + ' @ ' + jsonaccount['dueDate']
        else:
            if (balance < 100):
                balance_str = Fore.YELLOW + str(balance) + Fore.RESET
            else:
                balance_str = Fore.GREEN + str(balance) + Fore.RESET
        percentage = balance/net_worth
        accounts.append([institution, accountName.title(), balance_str,
                        currency, due, dueby, f'{round(percentage*100, 0)}%'])

    accounts.append(['', '', None, '', None, ''])
    accounts.append(['', Style.BRIGHT + '               NET WORTH',
                    net_worth, 'USD' + Style.NORMAL, None, ''])

    print(tabulate(accounts, numalign="right", floatfmt=".2f",
          tablefmt="plain"))


def monthly_budget():
    """
    Display monthly budget in table format

    Table has attributes that are found from the transaction table. Will print
    timegraph of the current balance of a budget. These values are created from
    the .env file.
    """
    # TODO: Add showing the mint total for a specific month(not just current)
    # TODO: Display time refreshed instead of current time.

    # get budgets
    budgets = load_json('budgets')
    income = budgets["income"]
    spend = budgets["spend"]

    deductionRate = float(os.environ['DEDUCTION_RATE'])
    hour_a_day = float(os.environ['HOUR_A_DAY'])
    pay_rate = float(os.environ['PAY_RATE'])
    tax_rate = float(os.environ['TAX_RATE'])

    estimate_gross_income = (hour_a_day * pay_rate * 21.74)
    estimate_deductions = estimate_gross_income * deductionRate
    estimate_tax_costs = (estimate_gross_income - estimate_deductions)
    estimate_tax_costs *= tax_rate

    print(f"Estimated Gross Income: ${format(estimate_gross_income, '.2f')}")
    print(f"Estimated 401k Deduction: ${format(estimate_deductions, '.2f')}")
    print(f"Estimated Taxes: ${format(estimate_tax_costs, '.2f')}")

    # find total income
    total_income = income[0]["bgt"]
    print(f"Total Net Income: "
          f"${format(total_income, '.2f')}")

    # find total expense
    total_expense = 0
    for i in spend:
        total_expense += i['bgt']
    print(f"Total Budgeted Expense: ${format(total_expense, '.2f')}")

    leftover = net_income - total_expense
    print(f"Leftover: ${format(leftover, '.2f')}")

    # Create budget list, then sort the list by total current amount
    budget = []
    for i in spend:
        budget.append([
            f"{i['cat']}",
            f"${format(i['bgt'], '.2f')}",
            f"{round(i['amt'], 2)}",
            f"{round(i['rbal'], 2)}",
            f"{create_timegraph(round(((i['amt']/i['bgt'])*100), 1))}",
            f"{round((i['bgt'] / total_expense) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{round((i['bgt'] / net_income) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{str(round((i['bgt'] / estimate_gross_income) * 100, 2) if i['bgt'] >= 0 else '0').strip()}%",
            f"{str(round((i['amt'] / estimate_gross_income) * 100, 2) if i['amt'] >= 0 else '0').strip()}%"])
        budget = sorted(budget, key=lambda x: float(x[1][1:]))

    budget.append(['Leftover', f"${format(leftover, '.2f')}", None, None,
                  None, None, f"{round((leftover / net_income) * 100, 2)}%",
                  f"{round((leftover / estimate_gross_income) * 100, 2)}%"])
    budget.append([None, None, None, None, None])
    budget.append(['401k', f"${format(estimate_deductions, '.2f')}",
                  None, None, None, None, None,
                  f"{round((estimate_deductions / estimate_gross_income) *  100, 2)}%"])
    budget.append(['Taxes', f"${format(estimate_tax_costs, '.2f')}",
                  None, None, None, None, None,
                  f"{round((estimate_tax_costs / estimate_gross_income) * 100, 2)}%"])

    # Print list as tabulate table
    print(tabulate(budget, numalign="left", floatfmt=".2f",
          tablefmt="grid",
          headers=["Name",
                   "Total",
                   "Current Amount",
                   "Remaining Balance",
                   "",
                   "(Budget) Percent of Expenses",
                   "(Budget) Percent of Net Income",
                   "(Budget) Percent of Gross Income",
                   "(Real) Percent of Gross Income"]))

    now = datetime.datetime.now().strftime("%a %d %b %H:%M")
    print('\nLast updated ' + now)


# @TODO Add pep8
def create_timegraph(percent):
    """
    Displays the percentage spend a month as a colored ASCII art.

    Args:
        percent(float): percentage of total spend on budget
    Returns:
        string of display
    """
    percentage = round(int(percent)/100, 1)
    color_red = False

    if percentage < 0:
        percentage = 0

    # if over 10%, display vertical bar as red
    if percentage >= 1.1:
        color_red = True

    if percentage > 1:
        percentage = 1

    print_string = ""
    for x in range(1, int(percentage*10), 1):
        print_string += "-"
    print_string += "|"
    if print_string == "|":
        start_r = 1
    else:
        start_r = 0
    for x in range(int(percentage*10) + start_r, 10, 1):
        print_string += "-"

    currentDay = datetime.datetime.today().day
    now = datetime.datetime.now()
    maxDaysMonth = calendar.monthrange(now.year, now.month)[1]

    monthPercentage = round(currentDay/maxDaysMonth, 1)
    r_string = "<"
    r_string += Fore.GREEN + print_string[:int(monthPercentage*10)]
    r_string += Fore.RESET
    r_string += print_string[int(monthPercentage*10):-1]
    if color_red:
        r_string += Fore.RED + print_string[-1:]
    else:
        r_string += print_string[-1:]
    r_string += Fore.RESET + ">"
    return r_string


def main():
    # Load arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-n", "--net", action="store_true",
                        help="show net worth and account amounts")
    parser.add_argument("-b", "--budget", action="store_true",
                        help="show current budget")
    parser.add_argument("-r", "--refresh", action="store_true",
                        help="refresh data from mint account")
    args = parser.parse_args()

    # load .env file
    load_dotenv(find_dotenv())

    # Load username and passwords
    if args.refresh:
        refresh(args.verbosity)
    # Load net worth
    if args.net:
        net_worth()
    # Load budget display
    if args.budget:
        monthly_budget()


if __name__ == "__main__":
    main()
