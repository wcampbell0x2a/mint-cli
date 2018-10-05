#!/usr/bin/python3
##
# Script for displaying Mint.com information via terminal.
# See here for API usage: https://github.com/mrooney/mintapi
#
# Use environment variables mUSER and mPASS as your mint account username
# and password.
#
# Author Wayne Campbell
# Found original net worth use on github somewhere
##

import argparse
import datetime
import json
import keyring
import mintapi
import pprint
import os
from dotenv import load_dotenv, find_dotenv
from tabulate import tabulate
from colorama import init
init()
from colorama import Fore, Style

def main():
    # load from .env file
    load_dotenv(find_dotenv())

    # Load username and passwords
    username = os.environ['MINT_USER']
    password = os.environ['MINT_PASS']
    print(f'Logging as {username} with password: {password}')
    mint = mintapi.Mint(username, password)

    negativeAccounts = ['loan', 'credit']
    prevInstitution = ''
    accounts = []

    # TODO print percentage of each account to each other
    # Get basic account information
    jsonaccounts = mint.get_accounts()
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
                balance = Fore.YELLOW + str(balance) + Fore.RESET
            else:
                balance = Fore.GREEN + str(balance) + Fore.RESET
        accounts.append([institution, accountName.title(), balance, currency, due, dueby])

    accounts.append(['', '', None, '', None, ''])
    accounts.append(['', Style.BRIGHT + '               NET WORTH', mint.get_net_worth(), 'USD' + Style.NORMAL, None, ''])

    print(tabulate(accounts, numalign="right", floatfmt=".2f", tablefmt="plain"))

    # get budgets
    budgets = mint.get_budgets()
    income = budgets["income"]
    spend = budgets["spend"]

    # TODO: Add showing the mint total for the month
    deductionRate = float(os.environ['DEDUCTION_RATE'])
    hour_a_week = float(os.environ['HOUR_A_WEEK'])
    pay_rate = float(os.environ['PAY_RATE'])
    tax_rate = float(os.environ['TAX_RATE'])

    estimate_gross_income = (hour_a_week * pay_rate * 5 * 4)
    estimate_deductions = estimate_gross_income * deductionRate
    estimate_tax_costs = (estimate_gross_income - estimate_deductions) * tax_rate

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
            f"{round((i['bgt'] / total_expense) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{round((i['bgt'] / total_income) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{round((i['bgt'] / estimate_gross_income) * 100, 2) if i['bgt'] >= 0 else '0'}%",
        ])
        budget_list = sorted(budget_list, key=lambda x: float(x[1][1:]))

    budget_list.append(['Leftover', f"${format(leftover, '.2f')}", None, None,
        None, f"{round((leftover / total_income) * 100, 2)}%",
        f"{round((leftover / estimate_gross_income) * 100, 2)}%"])
    budget_list.append([None, None, None, None, None])

    budget_list.append(['401k', f"${format(estimate_deductions, '.2f')}",
        None, None, None, None,
        f"{round((estimate_deductions / estimate_gross_income) *  100, 2)}%"
    ])
    budget_list.append(['Taxes', f"${format(estimate_tax_costs, '.2f')}",
        None, None, None, None,
        f"{round((estimate_tax_costs / estimate_gross_income) * 100, 2)}%"
    ])

    print(tabulate(budget_list, numalign="right", floatfmt=".2f", tablefmt="grid",
        headers=["Name",
            "Total",
            "Current Amount",
            "Remaining Balance",
            "Percent of Expense Budget ",
            "Percent of Budget(Take Home) Income",
            "Percent of Gross Income"

    ]))

    now = datetime.datetime.now().strftime("%a %d %b %H:%M")
    print('\nLast updated ' + now)

if __name__ == "__main__":
    main()
