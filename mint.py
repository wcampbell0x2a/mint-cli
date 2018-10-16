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
from colorama import init
init()
from colorama import Fore, Style

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def load_json(name):
    try:
        with open(f'data/{name}.json') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Use -r to refresh and save json files")

def save_json(name, data):
    with open(f'data/{name}.json', 'w') as outfile:
        json.dump(data, outfile, default=datetime_handler)

def refresh(verbose):
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
    print(Style.BRIGHT + Fore.BLUE + "ACCOUNTS" + Style.NORMAL + Fore.RESET)
    negativeAccounts = ['loan', 'credit']
    prevInstitution = ''
    accounts = []

    # Load data
    jsonaccounts = load_json('accounts')
    net_worth = load_json('net_worth')


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
        accounts.append([institution, accountName.title(), balance_str, currency, due, dueby, f'{round(percentage*100, 0)}%'])

    accounts.append(['', '', None, '', None, ''])
    accounts.append(['', Style.BRIGHT + '               NET WORTH', net_worth, 'USD' + Style.NORMAL, None, ''])

    print(tabulate(accounts, numalign="right", floatfmt=".2f", tablefmt="plain"))

def monthly_budget():
    # get budgets
    budgets = load_json('budgets')
    income = budgets["income"]
    spend = budgets["spend"]

    # TODO: Add showing the mint total for a specific month(not just current)
    deductionRate = float(os.environ['DEDUCTION_RATE'])
    hour_a_week = float(os.environ['HOUR_A_WEEK'])
    pay_rate = float(os.environ['PAY_RATE'])
    tax_rate = float(os.environ['TAX_RATE'])

    estimate_gross_income = (hour_a_week * pay_rate * 5 * 4)
    estimate_deductions = estimate_gross_income * deductionRate
    estimate_tax_costs = (estimate_gross_income - estimate_deductions) * tax_rate

    print("Estimated values from .env file")
    print(f'Estimated Gross Income: {estimate_gross_income}')
    print(f'Estimated 401k Deduction: {estimate_deductions}')
    print(f'Estimated Taxes: {estimate_tax_costs}')

    # find total income
    total_income = income[0]["bgt"]
    print(f"Total Budgeted(Net) Income(after taxes, 401k): ${format(total_income, '.2f')}")

    # find total expense
    total_expense = 0
    for i in spend:
        total_expense += i['bgt']
    print(f"Total Budgeted Expense: ${format(total_expense, '.2f')}")

    leftover = total_income - total_expense
    print(f"Leftover: ${format(leftover, '.2f')}")

    budget_list = []
    for i in spend:
        budget_list.append([
            f"{i['cat']}",
            f"${format(i['bgt'], '.2f')}",
            f"{round(i['amt'], 2)}",
            f"{round(i['rbal'], 2)}",
            f"{create_timegraph(round(((i['amt']/i['bgt'])*100), 1))}",
            f"{round((i['bgt'] / total_expense) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{round((i['bgt'] / total_income) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{str(round((i['bgt'] / estimate_gross_income) * 100, 2) if i['bgt'] >= 0 else '0').strip()}%"
        ])
        budget_list = sorted(budget_list, key=lambda x: float(x[1][1:]))

    budget_list.append(['Leftover', f"${format(leftover, '.2f')}", None, None,
        None, None, f"{round((leftover / total_income) * 100, 2)}%",
        f"{round((leftover / estimate_gross_income) * 100, 2)}%"])
    budget_list.append([None, None, None, None, None])

    budget_list.append(['401k', f"${format(estimate_deductions, '.2f')}",
        None, None, None, None, None,
        f"{round((estimate_deductions / estimate_gross_income) *  100, 2)}%"
    ])
    budget_list.append(['Taxes', f"${format(estimate_tax_costs, '.2f')}",
        None, None, None, None, None,
        f"{round((estimate_tax_costs / estimate_gross_income) * 100, 2)}%"
    ])

    print(tabulate(budget_list, numalign="left", floatfmt=".2f", tablefmt="grid",
        headers=["Name",
            "Total",
            "Current Amount",
            "Remaining Balance",
            "",
            "Percent of Expense Budget ",
            "Percent of Budget(Take Home) Income",
            "Percent of Gross Income"
    ]))

    now = datetime.datetime.now().strftime("%a %d %b %H:%M")
    print('\nLast updated ' + now)

# @TODO Add pep8
def create_timegraph(percent):
    """
    Displays the percentage spend a month as a colored ASCII art.

    Keywork Arguments:
    percent - percentage of total spend on budget
    return string of display
    """
    percentage = round(int(percent)/100, 1)

    if percentage < 0:
        percentage = 0

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
    return "<" + Fore.GREEN + print_string[:int(monthPercentage*10)] + Fore.RESET + print_string[int(monthPercentage*10):] + ">"

def main():
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

    if args.net:
        net_worth()
    if args.budget:
        monthly_budget()

if __name__ == "__main__":
    main()
