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
import time
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
    print(Style.BRIGHT + Fore.BLUE + "Net Worth" + Style.NORMAL + Fore.RESET)
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
            balance_str = Fore.RED + str(balance) + Fore.RESET
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


def monthly_budget(verbosity):
    """
    1) Display monthly budget in table format
    2) Display monthly savings rate

    Table has attributes that are found from the transaction table. Will print
    timegraph of the current balance of a budget. These values are created from
    the .env file.
    """
    # TODO: Add showing the mint total for a specific month(not just current)

    print(Style.BRIGHT + Fore.BLUE + "Monthly Budget" + Style.NORMAL + Fore.RESET)

    # get budgets
    budgets = load_json('budgets')
    income = budgets["income"]
    spend = budgets["spend"]

    # Load .env and check for values.
    reg401kDeductionRate = float(os.environ['401K_DEDUCTION_RATE']) if os.environ['401K_DEDUCTION_RATE'] != "" else 0.0
    roth401kDeductionRate = float(os.environ['ROTH_401K_DEDUCTION_RATE']) if os.environ['ROTH_401K_DEDUCTION_RATE'] != "" else 0.0
    HSADeductionAmount = float(os.environ['HSA_DEDUCTION_AMOUNT']) if os.environ['HSA_DEDUCTION_AMOUNT'] != "" else 0.0
    if float(os.environ['HOUR_A_DAY']) != "":
        hour_a_day = float(os.environ['HOUR_A_DAY'])
    else:
        print("Please enter .env data, missing HOUR_A_DAY")
    if float(os.environ['PAY_RATE']) != "":
        pay_rate = float(os.environ['PAY_RATE'])
    else:
        print("Please enter .env data, missing PAY_RATE")
    if float(os.environ['TAX_RATE']) != "":
        tax_rate = float(os.environ['TAX_RATE'])
    else:
        print("Please enter .env data, missing TAX_RATE")

    # TODO Add Roth IRA(divide up leftover)

    # Estimate Gross income from environment variables provided.
    estimate_gross_income = (hour_a_day * pay_rate * 21.74)

    # Figure out Before Tax Deductions
    reg401k_estimate_deductions = estimate_gross_income * reg401kDeductionRate
    HSA_estimate_deductions = HSADeductionAmount

    estimate_tax_costs = ((estimate_gross_income - reg401k_estimate_deductions - HSA_estimate_deductions) * tax_rate)

    # Figure out After Tax Deductions
    roth401k_estimate_deductions = estimate_gross_income * roth401kDeductionRate


    if verbosity:
        print(f"Estimated Gross Income: ${format(estimate_gross_income, '.2f')}\n")
        print(Style.BRIGHT + "Before Tax Deductions:" + Style.NORMAL)
        print(f"Estimated 401k Deduction: ${format(reg401k_estimate_deductions, '.2f')}")
        print(f"Estimated HSA Deduction: ${format(HSA_estimate_deductions, '.2f')}\n")
        print(Style.BRIGHT + "After Tax Deductions:" + Style.NORMAL)
        print(f"Estimated Roth 401k Deduction: ${format(roth401k_estimate_deductions, '.2f')}\n")
        print(f"Estimated Taxes: ${format(estimate_tax_costs, '.2f')}\n")

    # find net income from mint budget
    #net_income = income[0]["bgt"]
    #if verbosity:
    #    print(f"(Mint) Total Net Income: ${format(net_income, '.2f')}")

    # Find net income from env variables
    net_income = (estimate_gross_income - (reg401k_estimate_deductions + HSA_estimate_deductions))
    net_income -= (net_income * tax_rate)
    net_income -= roth401k_estimate_deductions
    if verbosity:
        print(f"(Env) Total Net Income: ${format(net_income, '.2f')}")

    # find total expense from mint budget
    total_expense = 0
    for i in spend:
        total_expense += i['bgt']
    if verbosity:
        print(f"(Mint) Total Expense: ${format(total_expense, '.2f')}")

    # find total expense of real mint budget amount
    real_total_expense = 0
    for i in spend:
        real_total_expense += i['amt']
    if verbosity:
        print(f"(Mint) Real Total Expense: ${format(real_total_expense, '.2f')}")

    # find total expense of real mint budget amount
    real_total_expense = 0
    for i in spend:
        real_total_expense += i['amt']
    print(f"(Mint) Real Total Expense: ${format(real_total_expense, '.2f')}")

    leftover = net_income - total_expense
    if verbosity:
        print(f"Budget Leftover: ${format(leftover, '.2f')}")

    real_leftover = net_income - real_total_expense
    if verbosity:
        print(f"Real Budget Leftover: ${format(real_leftover, '.2f')}")

    # Create budget list, then sort the list by total current amount
    budget = []
    for i in spend:
        budget.append([
            f"{i['cat']}",
            f"${format(i['bgt'], '.2f')}",
            f"${format(round(i['amt'], 2), '.2f')}",
            f"${format(round(i['rbal'], 2), '.2f')}",
            f"{create_timegraph(round(((i['amt']/i['bgt'])*100), 1))}",
            f"{round((i['bgt'] / total_expense) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{round((i['bgt'] / net_income) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{round((i['amt'] / net_income) * 100, 2) if i['bgt'] >= 0 else '0'}%",
            f"{str(round((i['bgt'] / estimate_gross_income) * 100, 2) if i['bgt'] >= 0 else '0').strip()}%",
            f"{str(round((i['amt'] / estimate_gross_income) * 100, 2) if i['amt'] >= 0 else '0').strip()}%"])
        budget = sorted(budget, key=lambda x: float(x[1][1:]))

    budget.append(['Leftover', f"${format(leftover, '.2f')}", f"${format(real_leftover, '.2f')}", None,
                  None, None, f"{round((leftover / net_income) * 100, 2)}%",
                  f"{round((real_leftover / net_income) * 100, 2)}%",
                  f"{round((leftover / estimate_gross_income) * 100, 2)}%",
                  f"{round((real_leftover / estimate_gross_income) * 100, 2)}%"])
    budget.append([None, None, None, None, None])
    budget.append(['Regular 401k', f"${format(reg401k_estimate_deductions, '.2f')}",
                  None, None, None, None, None, None,
                  f"{round((reg401k_estimate_deductions / estimate_gross_income) *  100, 2)}%",
                  f"{round((reg401k_estimate_deductions / estimate_gross_income) *  100, 2)}%"])
    budget.append(['Roth 401k', f"${format(roth401k_estimate_deductions, '.2f')}",
                  None, None, None, None, None, None,
                  f"{round((roth401k_estimate_deductions / estimate_gross_income) *  100, 2)}%",
                  f"{round((roth401k_estimate_deductions / estimate_gross_income) *  100, 2)}%"])
    budget.append(['HSA', f"${format(HSA_estimate_deductions, '.2f')}",
                  None, None, None, None, None, None,
                  f"{round((HSA_estimate_deductions / estimate_gross_income) *  100, 2)}%",
                  f"{round((HSA_estimate_deductions / estimate_gross_income) *  100, 2)}%"])
    budget.append(['Taxes', f"${format(estimate_tax_costs, '.2f')}",
                  None, None, None, None, None, None,
                  f"{round((estimate_tax_costs / estimate_gross_income) * 100, 2)}%",
                  f"{round((estimate_tax_costs / estimate_gross_income) * 100, 2)}%"])

    # Print list as tabulate table
    print(tabulate(budget, numalign="left", floatfmt=".2f",
          tablefmt="grid",
          headers=["Name",
                   "(Budget) Total",
                   "Current Amount",
                   "Remaining Balance",
                   "",
                   "(Budget) Percent of Expenses",
                   "(Budget) Percent of Net Income",
                   "(Real Budget) Percent of Net Income",
                   "(Budget) Percent of Gross Income",
                   "(Real Budget) Percent of Gross Income"]))

    timeModified = time.ctime(os.path.getmtime("data/budgets.json"))
    print('\nData Last updated ' + timeModified + "\n")

    ##
    # Savings Rate
    #
    # Displays savings rate as described by the Bureau of Analysis.
    # Disposable personal income - personal outlay / disposable personal income
    # aka. (total savings)/(gross-taxes)
    ##
    savings = reg401k_estimate_deductions + roth401k_estimate_deductions + HSA_estimate_deductions
    savings_rate_estimate = (savings + leftover)/(estimate_gross_income - estimate_tax_costs) * 100
    savings_rate_real = (savings + real_leftover)/(estimate_gross_income - estimate_tax_costs) * 100
    print(f"(Estimate) Savings Rate (BoA): {format(savings_rate_estimate, '.2f')}%")
    print(f"(Real) Savings Rate (BoA): {format(savings_rate_real, '.2f')}%\n")

def emergency():
    print(Style.BRIGHT + Fore.BLUE + "Emergency Calculator" + Style.NORMAL + Fore.RESET)
    # Load data
    jsonaccounts = load_json('accounts')

    # Search accounts for accounts that are tagged as emergency accounts in .env
    balance = 0
    for jsonaccount in jsonaccounts:
        # Check if .env variables exist
        if str(os.environ['EMERGENCY']) != "":
            emergency_var_string = str(os.environ['EMERGENCY'])
        else:
            print("Please enter .env data, missing EMERGENCY")

        emergency_var_list = emergency_var_string.split(",")

        # Insert into searchable list
        for item in emergency_var_list:
            institutionName = item[item.find("(")+1:item.find(")")]
            accountName = item.split("(")[0]

            if (jsonaccount['accountName'] ==  institutionName  and jsonaccount['fiName'] == accountName):
                institution = jsonaccount['fiName']
                accountName = jsonaccount['accountName']
                balance += jsonaccount['currentBalance']


    # find total expense from mint budget
    budgets = load_json('budgets')
    spend = budgets["spend"]
    total_expense = 0
    for i in spend:
        total_expense += i['bgt']
    print(f"Total Amount in Emergency Fund marked Accounts: ${balance}")
    print(f"(Mint) Total Expense: ${format(total_expense, '.2f')}")
    print(f"Current Months in Emergency Fund: {round(float(format(balance/total_expense)), 2)}")

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

    # Print Timeline
    monthPercentage = int(round(currentDay/maxDaysMonth, 1)*10)
    r_string = "<"
    r_string += Fore.GREEN + print_string[:monthPercentage]
    r_string += Fore.RESET

    # Fill in rest of month
    r_string += print_string[monthPercentage:-1]

    # Print last red of over 10%
    if color_red:
        r_string += Fore.RED + print_string[-1:]
    else:
        # Check if end of month, if end of month print green
        # instead of reset color
        if (monthPercentage == 10):
            r_string += Fore.GREEN + print_string[-1:]
        else:
            r_string += print_string[-1:]

    # Correction for end of month (need to delete the last char if at the end)
    if (monthPercentage == 10):
        r_string = r_string[:15]  + r_string[16:]

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
                        help="show current budget and savings rate")
    parser.add_argument("-e", "--emergency", action="store_true",
                        help="show emergency fund timeline")
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
        monthly_budget(args.verbosity)
    if args.emergency:
        emergency()


if __name__ == "__main__":
    main()
