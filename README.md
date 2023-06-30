# Zillow Data Scraper

**Purpose:** I've always had an interest in the real estate market and I figured this was the best project where I can dip my toes into learning basic scraping. Since this is where my real estates interests and first educational scraping learnings aligned, I hope audiences find this useful and educational.

**Summary:** Developed a custom web scraper to extract housing data from Zillow. This utilizes Python and web scraping libraries to automate the process of gathering property information, including prices, features, and locations. This scraper significantly reduced manual data collection efforts.

Features and information scraped includes:
1. For sale/sold/for rent
2. Id
3. Latitude
4. Longitude
5. Floor size (sq ft)
6. Number of beds and bathrooms
7. Address
8. URL
9. Sale/Sold Price 
10. Rental price

## Limitations of the Scraper

I'm still working out the kinks but there are certain limitations to the scraper. Below are the limitations ordered from most aggregious to least:
1. Completeness - The scraper is currently scraping based off of the JSON script in the HTML. Unfortunately, Zillow has structured their code so that not every single listing will have a script. Future versions of this scraper may eventually address this issue but for now, this scraper will provide some details.
2. Information Details - While the above information we can scrape is a nice start, there are still plenty of information that would give more color to our listings. For example, what year was the house built? Does it have a pool? What other amenities are available to it? What is the external quality and condition of the house? Unfortunately, from Zillow's search page results, it is not possible to get many of these information. Future updates to this scraper will involve automated review of the listing details in-depth (i.e. clicking on the listing link to get more details than just those listed on the Zillow search results page) to scrape more details for each listing.

## How to Use:
You will see that the "Scrapers" folder contains 3 different scrapers (for rent, for sale, and sold) while the "data" folder contains the scraped information pulled from the scrappers. The way the scrapers work is that each time is scrapes the information and ran, it will update the excel files (if there's no such excel file, it will create a new excel file with the details).

For the purpose of checking to make sure it worked, I picked the two southern most counties of South Florida (Miami Dade and Broward) to scrape. I left the data folders for audiences to see the kind of data/information they can obtain from the scrapers.

Here's how to get the scrapers up and running:
1. Download the zip file into your desktop and open it up on your code editor of your choice.
2. For the scrapers to even run, you must:
    - first update the entirety of the "headers" variable. You can achieve this by going onto the Zillow webpage (either for sale, buy, or rent search page), 
    - updating any search results you prefer (location, types of houses/apartments, etc.), 
    - open your Chrome Developer tools and go to the Network tab,
    - Find the relevant "Name". Note that it will have a title something along the lines of: "GetSearchPageState...."
    - **IMPORTANT:** Click on the "GetSearchPageState...." and in the "Headers" section, update the code with your "Request Headers" information. Note that in my code, I have left some example headers but have marked "XXXXX" for most items. 
    - **IMPORTANT:** For each of the scrapers, the "parameters" variable must be updated. To do this, go to the "GetSearchPageState...." and click on the "Payload" section. This will have the "searchQueryState" details that you can copy and paste into your parameters. Note that in the pagination, you must update it to include: "currentPage": %s. As can be seen from the code, this is essentially running through Pages 1 - 21 (excluding 21) and scraping the information on each page. 
    - **IMPORTANT:** The page range should be updated based on your needs/preferences. I arbitrarily left the range(1, 21) (a good 20 pages) but you can update it to your needs.
3. Sometimes Zillow will run out of JSON script data if your page range is too large (i.e. you put a range of 1 - 21 but Zillow has run out of script data by page 5). This is why in the code, I have left a:  print("Page %s worked!" % page) so that you can know at what page to update the range to. If there is an error, Zillow will not update the csv files in the data folder with any of the search results it's identified before the error. 