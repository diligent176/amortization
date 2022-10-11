"""
spiders.py module
scrapes Canadian banks for mortgage rates
scrapy shell "https://www.rbcroyalbank.com/mortgages/mortgage-rates.html"
scrapy shell "https://www.bmo.com/main/personal/mortgages/mortgage-rates/"
scrapy shell "https://www.bmo.com/public-data/api/v1.1/mortgages.json"
"""
import re
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from pprint import pprint


class BmoSpider(scrapy.Spider):
    
    name = "bmo_spider"
    start_urls = ["https://www.bmo.com/public-data/api/v1.1/mortgages.json"]

    def parse(self, response):

        # iterate over lines in json object mortgage-rates
        for rate_name, rate_float in response.json()["mortgage-rates"].items():

            # parse out values for rate dict
            if "fixed" in rate_name.lower():
                rate_type = "Fixed"
            else:
                rate_type = "Variable"

            if "over-25" in rate_name.lower():
                amort_years = 30
            else:
                amort_years = 25

            if "-closed" in rate_name.lower():
                term_type = "Closed"
            else:
                term_type = "Open"

            # get term length
            if matches := re.search(r"^.*-(?P<t_years>\d{1,2})-year.*", rate_name):
                try:
                    term_years = int(matches.group("t_years"))
                except ValueError:
                    # convert to int() failed
                    print(f"Error converting {matches.group('t_years')} to int()")
                    continue
            else:
                # no match on TERM regex, continue to next row
                continue

            # create a rate dict
            rate_dict = {
                "lender": "BMO",
                "amort_years": amort_years,
                "rate_percent": rate_float,
                "rate_type": rate_type,
                "term_years": term_years,
                "term_type": term_type,
            }
            
            # yield result back to caller
            yield rate_dict


class RbcSpider(scrapy.Spider):

    name = "rbc_spider"
    start_urls = ["https://www.rbcroyalbank.com/mortgages/mortgage-rates.html"]

    def parse(self, response):

        # find div id=special-rates
        special_rates = response.xpath('//*[@id="special-rates"]')

        # inside special_rates Selector, find amortization timeframes
        amort_headers = special_rates.xpath("h4/text()")

        # find tables with class='table-striped' within special-rates
        stripe_tables = special_rates.css("table.table-striped")

        # collapsing buttons above each stripe-table shows fixed OR variable
        cbuttons = special_rates.css("button.collapse-toggle::text")

        # iterate over stripe_tables (4)
        # i_table is one of 4 stripe_tables holding RBC rates
        for i_table, stripe_table in enumerate(stripe_tables):

            # stripe_table 0 = 25 years or less amortization, FIXED
            # stripe_table 1 = 25 years or less amortization, VARIABLE
            # stripe_table 2 = more than 25 years amortization, FIXED
            # stripe_table 3 = more than 25 years amortization, VARIABLE
            match i_table:
                case 0 | 1:  # 25 years or less amortization
                    amort = amort_headers[0].get().strip()
                case 2 | 3:  # more than 25 years amortization
                    amort = amort_headers[1].get().strip()

            # for each TABLEROW in current stripe_table
            for tr in stripe_table.css("tr"):

                # fixed or variable, based on which stripe table (i_table)
                # collapsing buttons text says whether fixed/variable
                fixed_var = cbuttons[i_table].get().strip()

                if "fixed" in fixed_var.lower():
                    rate_type = "Fixed"
                elif "variable" in fixed_var.lower():
                    rate_type = "Variable"
                else:
                    rate_type = "Unknown"

                # find term and rate from table data cells 0, 1
                term = tr.xpath("td/text()")[0].get().strip()
                rate = tr.xpath("td/text()")[1].get().strip()

                # make sure table row contains a valid term and rate
                if "year" in term.lower() and "%" in rate:

                    # determine if amortization is > 25, or 25 and less
                    if "greater than 25" in amort.lower():
                        amort_years = 30
                    else:
                        amort_years = 25

                    # get rate percentage as a float from a string
                    if matches := re.search(r"^.*(\d{1,2}\.\d{1,3}%)", rate):
                        try:
                            rate_percent = float((matches.group(1)).replace('%', ''))

                        except ValueError:
                            # rate can't be converted to int(), move on to next table row
                            print(f"Error converting {matches.group(1)} to float()")
                            continue
                    else:
                        # no match on RATE regex, move on to next table row
                        continue

                    # get term type and length
                    if matches := re.search(r"^.*(?P<t_years>\d{1}).*(?P<t_type>Closed|Open)", term):
                        try:
                            term_years = int(matches.group("t_years"))
                            if "open" in matches.group("t_type").lower():
                                term_type = "Open"
                            else:
                                term_type = "Closed"

                        except ValueError:
                            # term could not be converted to int, move on next table row
                            print(f"Error converting {matches.group('t_years')} to int()")
                            continue
                    else:
                        # no match on TERMS regex, continue on with next row
                        continue

                    # create a rate dict
                    rate_dict = {
                        "lender": "RBC",
                        "amort_years": amort_years,
                        "rate_percent": rate_percent,
                        "rate_type": rate_type,
                        "term_years": term_years,
                        "term_type": term_type,
                    }

                    # yield result back to caller
                    yield rate_dict


"""
Crawls Canadian Bank websites
Returns a list of dicts (bank rates) sorted by lowest rate first
"""
def crawl_bank_rates():

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process = CrawlerProcess()

    # crawl one or more spiders
    process.crawl(BmoSpider)
    process.crawl(RbcSpider)

    # start crawling, script will block here until crawling jobs finish
    process.start()

    if results:
        # return the sorted results list
        return sorted(results, key=lambda d: d['rate_percent'])
    else:
        return None


def main():
    # main function is only here for standalone test (to run without project.py)
    bank_rates = crawl_bank_rates()

    if bank_rates:
        pprint(bank_rates)
        print(f"\nLength of results: {len(bank_rates)}")
    else:
        print("\nNo results")

    print("\n######## DONE ########\n")


if __name__ == "__main__":
    main()
