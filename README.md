# Mortgage Amortization Schedule & Payment Calculator

----

### Video Demo:  <URL HERE>


### Description:

This program has 4 main functions:

1. To retrieve & display **current interest rates** from (some) Canadian banks
2. To determine the **mortgage payment amount**
3. To calculate & display a complete **amortization schedule**
4. To **export** the amortization schedule as a CSV file


These features are implemented as a **graphical user interface** using [**PySimpleGUI**](https://www.pysimplegui.org/) library. Interest rates are retrieved from bank websites using [**Scrapy**](https://scrapy.org/) web scraping library. 

![Main screen](screen1.png)

The interest rate can be entered manually, as web-scraping is an optional feature. When **<u>F</u>etch Bank Rates** is clicked, the Bank Rates table is populated. When selecting any row from Bank Rates table, the interest rate field is updated, and the payment and amortization schedules are re-calculated.

When **<u>E</u>xport to CSV** is clicked, the user is prompted by a File Save dialog to select a path and file name. The amortization schedule is then saved to the specified file name.




### Program Structure:

The program consists of 2 python modules, and a test module:

| File                | Description |
| ------------------- | ----------- |
| **project.py**      | the main GUI and helper functions |
| **spiders.py**      | the web scraping spider module |
| **test_project.py** | test cases for the functions in project.py |



#### PyTest tests:

The testing module contains 9 tests.


#### Design considerations:

##### PySimpleGUI

sdsd
sdsd


##### Scrapy

sdsd
sdsdsd
