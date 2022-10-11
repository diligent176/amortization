"""
project.py - must have a main function and at least three other functions,
each of which accompanied by tests to be executed with pytest.
Your main function must be in project.py in the root of your project.
Your 3 required custom functions other than main must also be in project.py 
and defined at the same indentation level as main (not nested under classes or functions).
Your test functions must be in a file called test_project.py in the root of your project.
Be sure they have the same name as your custom functions, prepended with test_ 
(test_custom_function, where custom_function is a function you implemented in project.py).
Implement additional classes and functions as you see fit beyond the minimum requirement.
Any pip-installable libraries that your project requires must be listed, one per line,
in a file called requirements.txt in the root of your project
"""
import PySimpleGUI as sg
import spiders
import csv


TERM_YEARS = [1, 2, 3, 5, 7, 10]
AMORT_YEARS = [10, 15, 20, 25, 30, 35]
PAYMENT_FREQS = ["Monthly", "Bi-Weekly", "Weekly", "Accelerated Bi-Weekly", "Accelerated Weekly"]
BANK_RATE_HEADERS = ["Lender", "Interest Rate", "Rate Type", "Term Length", "Term Type", "Amortization"]
SCHEDULE_HEADERS =  ["Payment #", "Starting Balance", "Payment Amount", "Principal Paid", "Interest Paid", "Total Principal Paid", "Total Interest Paid"]

"""
Main calculator with PySimpleGUI
"""
def show_calculator():

    # setup empty variables for GUI to re-calc when changes detected
    bank_rates = []
    BORROWAMOUNT = ''
    BORROWRATE = ''
    AMORTIZATION = ''
    PAYMENTFREQ = ''

    left_col = [
        [sg.Text("Interest Rate:"), sg.Input(key="-BORROWRATE-", s=7, p=5, default_text="4.00%", enable_events=True),
         sg.Push(),
         sg.Button("Fetch Bank Rates...", k="-FETCH-", expand_x=True, tooltip="Select a bank rate to update the Amortization Calculator.")],
        [sg.Text("Principal amount to borrow:"), sg.Input(key="-BORROWAMOUNT-", s=11, p=5, default_text="$200,000", enable_events=True)],
        [sg.Text("Mortgage Term (years):"), sg.Combo(TERM_YEARS, default_value=5, key="-TERMYEARS-", s=3, p=5, enable_events=True)],
        [sg.Text("Mortgage Term Type:"), sg.Combo(["Closed", "Open"], key="-TERMTYPE-", default_value="Closed", p=5, readonly=True, enable_events=True)],
        [sg.Text("Amortization (years):"), sg.Combo(AMORT_YEARS, default_value=30, key="-AMORTIZATION-", s=3, p=5, enable_events=True)],
        [sg.Text("Payment frequency:"), sg.Combo(PAYMENT_FREQS, key="-PAYMENTFREQ-", default_value=PAYMENT_FREQS[0], p=5, readonly=True, enable_events=True)],
        [sg.Text("Payment amount:"), sg.Text("   $", k="-PAYMENT-", font="Verdana 14 bold", p=(0, 15))],
    ]

    right_col = [
        [sg.Text('Bank Rates', font='Verdana 12 bold', justification='l', expand_x=True)],
        [
            sg.Table(
                values=bank_rates,
                headings=BANK_RATE_HEADERS,
                justification="center",
                num_rows=12,
                key="-RATESTABLE-",
                selected_row_colors=('white', 'green'),
                select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                enable_events=True,
                expand_x=True,
                expand_y=True,
                vertical_scroll_only=False,
                tooltip="Canadian Bank Rates",
            )
        ],
    ]

    bottom_col = [
        [sg.Text('Amortization Schedule    ', font='Verdana 18 bold', justification='c'),
         sg.Input(visible=False, enable_events=True, key='-CSVFILE-'), 
         sg.FileSaveAs(button_text="Export to CSV...", k="-EXPORT-", default_extension=".csv", file_types = (('CSV File', '*.csv'),), tooltip="Choose where to save the file")],
        [sg.Table(values=[], headings=SCHEDULE_HEADERS, key="-AMORTSCHED-", num_rows=20, justification =('center'))],
    ]
    
    layout = [
        [sg.Column(left_col, vertical_alignment='t'), sg.VSeperator(), sg.Column(right_col, element_justification='c')],
        [sg.HorizontalSeparator(p=((0,0),(0,5)))],
        [sg.Column(bottom_col, element_justification='c', expand_x=True, expand_y=True)],
    ]

    # show calculator window
    window = sg.Window("Calculate Amortization Schedule", layout, ttk_theme="clam", font='Verdana 11', resizable=False, grab_anywhere=True, finalize=True)
    button_fetch, button_export = window['-FETCH-'], window['-EXPORT-']
    
    # Binding key events to window
    window.bind("<Alt_L><f>", "ALT-F")
    window.bind("<Alt_L><e>", "ALT-E")

    # Set index for underlined buttons
    button_fetch.Widget.configure(underline=0, takefocus=0)
    button_export.Widget.configure(underline=0, takefocus=0)
    
    # fire the calculate event at the start
    window.write_event_value("-CALCULATE-", None)

    # event loop
    while True:
        event, values = window.read()
        # print(event, values)

        match event:

            # event -FETCH-
            case '-FETCH-':
                # fetch bank rates ONE TIME ONLY
                if not bank_rates:
                    bank_rates = spiders.crawl_bank_rates()

                    if bank_rates:
                        # format bank rates (table_data) as list of lists
                        table_data = make_table_data(bank_rates)
                        # populate rates table
                        window['-RATESTABLE-'].update(values=table_data)

                    else:
                        # failed to fetch rates
                        sg.popup(f"Could not fetch bank rates.")

                else:
                    # no need to re-load table
                    print("\nBank rates already loaded. Close program to flush the bank rates.\n")

            # event -CALCULATE- triggered by multiple elements/events
            case "-CALCULATE-" | "-BORROWAMOUNT-" | "-AMORTIZATION-" | "-PAYMENTFREQ-" | "-BORROWRATE-":
                
                # event fires on every key press (including arrow key)
                # only RE-CALC if one of the 4 values changes
                if values['-BORROWAMOUNT-'] != BORROWAMOUNT or values['-BORROWRATE-'] != BORROWRATE or values['-AMORTIZATION-'] != AMORTIZATION or values['-PAYMENTFREQ-'] != PAYMENTFREQ:
                    
                    # save the current values
                    BORROWAMOUNT = values['-BORROWAMOUNT-']
                    BORROWRATE = values['-BORROWRATE-']
                    AMORTIZATION = values['-AMORTIZATION-']
                    PAYMENTFREQ = values['-PAYMENTFREQ-']

                    # recalculate
                    principal = values['-BORROWAMOUNT-'].strip().replace('$','').replace(',','')
                    amortization = values['-AMORTIZATION-']
                    rate = values['-BORROWRATE-'].strip().replace('%','')
                    pmts_per_year = payments_per_year(values['-PAYMENTFREQ-'])
                    if "accelerated" in values['-PAYMENTFREQ-'].lower():
                        payment = mortgage_payment_accelerated(principal, amortization, rate, pmts_per_year)
                    else:
                        payment = mortgage_payment_calc(principal, amortization, rate, pmts_per_year)

                    # build amortization schedule data
                    schedule_data = amortization_schedule(principal, amortization, rate, pmts_per_year, payment)
                    
                    # update the payment amount in the window
                    window['-PAYMENT-'].update(value=f"   ${payment}")

                    # update the amortizaton table
                    window['-AMORTSCHED-'].update(values=schedule_data)

            # event -RATESTABLE-
            case "-RATESTABLE-":
                # only 1 row can be selected in rates table (TABLE_SELECT_MODE_BROWSE)
                rate_row = values["-RATESTABLE-"][0]
                
                # update the selected rate and term values in the GUI
                window['-BORROWRATE-'].update(value=bank_rates[rate_row]['rate_percent'])
                window['-TERMYEARS-'].update(value=bank_rates[rate_row]['term_years'])
                window['-TERMTYPE-'].update(value=bank_rates[rate_row]['term_type'])
                window['-AMORTIZATION-'].update(value=bank_rates[rate_row]['amort_years'])

                # re-calculate the payment
                window.write_event_value("-CALCULATE-", None)

            # event -CSVFILE-
            case "-CSVFILE-":
                file_name = values["-CSVFILE-"]
                export_csv(window['-AMORTSCHED-'].Values, file_name)

            # event ALT-F
            case "ALT-F":
                window["-FETCH-"].click()

            # event ALT-E
            case "ALT-E":
                window["-EXPORT-"].click()

            # event WIN_CLOSED
            case sg.WIN_CLOSED:
                window.close()
                break


"""
make_table_data formats an input list of dicts (rates)
returns a list of lists for PySimpleGUI table object
"""
def make_table_data(ratelist):

    data = []

    for row in ratelist:
        try:
            rate = [
                row["lender"],
                f'{row["rate_percent"]}%',
                row["rate_type"],
                f'{row["term_years"]} years',
                row["term_type"],
                f'{row["amort_years"]} years',
            ]
            data.append(rate)
        except KeyError:
            pass

    return data


"""
mortgage_payment_calc returns the periodic payment amount given these parameters:
 loan_amount: principal borrowed
 amortization_years: how many years to pay back entire loan
 interest_rate: the rate as a percentage (APR)
 payments_per_year: how many payments each calendar year
"""
def mortgage_payment_calc(loan_amount, amortization_years, interest_rate, payments_per_year):
    
    try:
        # get annual interest rate as decimal
        interest_fraction = float(interest_rate) / 100
        
        # periodic interest rate is annual rate divided by # of periodic payments
        periodic_interest = interest_fraction / payments_per_year

        # total payment periods is # amortization years * payments per year
        payment_periods = int(amortization_years) * payments_per_year
        
        # numerator (top) and denominator (bottom) for the payment formula
        numerator = periodic_interest * ((1 + periodic_interest)**payment_periods)
        denominator = (1 + periodic_interest)**payment_periods - 1
        
        # periodic payment formula
        periodic_payment_amount = float(loan_amount) * numerator / denominator

        # return payment to 2 decimals places
        return f"{periodic_payment_amount:.2f}"

    except (ValueError, TypeError, ZeroDivisionError):
        return " DATA ERROR!"


def mortgage_payment_accelerated(loan_amount, amortization_years, interest_rate, payments_per_year):
    # Accelerated weekly mortgage payment is when a monthly mortgage payment is divided by four,
    # and that amount is withdrawn weekly. Slighty higher payment than weekly, but cuts down the amortization
    
    # get MONTHLY payment the usual way
    try:
        monthly_payment = float(mortgage_payment_calc(loan_amount, amortization_years, interest_rate, 12))
    except ValueError:
        return " DATA ERROR!"

    if payments_per_year == 52:
        # weekly accelerated = monthly payment / 4
        periodic_payment_amount = monthly_payment / 4
    
    elif payments_per_year == 26:
        # bi-weekly accelerated = monthly payment / 2
        periodic_payment_amount = monthly_payment / 2
    
    else:
        # unexpected result
        return " DATA ERROR!"

    # return accelerated payment to 2 decimals places
    return f"{periodic_payment_amount:.2f}"


"""
payments_per_year takes a payment frequency (str) and 
returns the number of payments per year (int)
# see constant PAYMENT_FREQS = ["Monthly", "Bi-Weekly", "Weekly", "Accelerated Bi-Weekly", "Accelerated Weekly"]
"""
def payments_per_year(s_payment_frequency):

    match s_payment_frequency:
        case "Monthly":
            return 12
        case "Bi-Weekly":
            return 26
        case "Weekly":
            return 52
        case "Accelerated Bi-Weekly":
            return 26
        case "Accelerated Weekly":
            return 52
        case _:
            return None


"""
amortization_schedule 
returns a 2-dimensional list of periodic payments
"""
def amortization_schedule(loan_amount, amortization_years, interest_rate, payments_per_year, payment_amount):

    # check input types in a try block:
    try:
        loan_amount = float(loan_amount)
        amortization_years = int(amortization_years)
        interest_fraction = float(interest_rate) / 100
        payments_per_year = int(payments_per_year)
        payment_amount = float(payment_amount)

    except (ValueError, TypeError):
        # print("\nError while calculating the amortization schedule!\n")
        return None
    
    # periodic rate is the amount of interest charged per periodic payment
    # i.e. the APR divided by number of payments per year
    periodic_rate = interest_fraction / payments_per_year

    # total payment periods is # amortization years * payments per year
    payment_periods = amortization_years * payments_per_year

    # set a starting principal balance and empty amort_schedule (list)
    principal_balance = loan_amount
    amort_schedule = []
    running_interest_paid = 0
    running_principal_paid = 0

    # iterate over each payment to calculate principal and interest each period
    for payment_num in range(payment_periods):
        period_interest = principal_balance * periodic_rate
        period_principal = payment_amount - period_interest
        running_interest_paid += period_interest
        running_principal_paid += period_principal

        # create list for this data row
        row = [
            payment_num + 1,
            f"${principal_balance:.2f}",
            f"${payment_amount:.2f}",
            f"${period_principal:.2f}",
            f"${period_interest:.2f}",
            f"${running_principal_paid:.2f}",
            f"${running_interest_paid:.2f}",
        ]

        # append this row to amort_schedule
        amort_schedule.append(row)

        # deduct the principal paid AFTER writing out the row
        # each row indicates the STARTING principal amount (loan balance before payment)
        principal_balance = principal_balance - period_principal

        # stop data table if loan is paid early (i.e. for accelerated payment schedule)
        if principal_balance < 0:
            break


    # return the whole data table
    return amort_schedule


"""
export the amortization table to CSV file
"""
def export_csv(data, filename):
    # write the csv
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(SCHEDULE_HEADERS)
            writer.writerows(data)

    except:
        sg.popup(f"ERROR: Failed to save CSV file!!!\n\nCheck if file name is in use / locked by another program.", title="ERROR", font="Verdana 11", modal=True)

    else:
        sg.popup(f"Successfully saved CSV file.\n\n{filename}", title="Saved", font="Verdana 11", modal=True, auto_close=True, auto_close_duration=5)


def main():

    # show the main GUI
     show_calculator()


if __name__ == "__main__":
    main()
