# Dependencies 
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from selenium import webdriver
import pandas as pd
import time
import pprint

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    ###########  NASA Mars News ###########
    # Get url to scape
    url= 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html, 'html.parser')

    # Collect the latest news title and paragraph
    news_title = soup.find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text

    ########### JPL Mars Space Images - Featured Image  ###########
    # URL for featured image 
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(image_url)

    # Go to full image
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)

    # Go to more info
    browser.click_link_by_partial_text('more info')

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    image_soup = bs(html, 'html.parser')

    # Scrape the URL
    img_url = image_soup.find('figure', class_='lede').a['href']
    featured_image_url = f'https://www.jpl.nasa.gov{img_url}'


    ########### Mars Facts  ###########
    # Visit Mars Facts webpage
    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)
    html = browser.html

    # Scrape the table containing facts about Mars
    table = pd.read_html(facts_url)
    mars_facts = table[2]

    # Rename columns
    mars_facts.columns = ['Description','Value']

    # Reset Index to be description
    mars_facts.set_index('Description')

    # Use Pandas to convert the data to a HTML table string
    mars_facts = mars_facts.to_html(classes="table table-striped")

    ########### Mars Hemispheres  ###########
    # Visit the USGS Astrogeology site
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    hemi_soup = bs(html, "html.parser")

    # Create list to hold titles & links to images
    hemisphere_image_urls = []

    # Retrieve all elements that contain image information
    results = hemi_soup.find("div", class_ = "result-list" )
    hemispheres = results.find_all("div", class_="item")

    # Loop through each image
    for hemisphere in hemispheres:
        hemi_title = hemisphere.find("h3").text
        hemi_title = hemi_title.replace("Enhanced", "")
        end_url = hemisphere.find("a")["href"]
        img_url = "https://astrogeology.usgs.gov/" + end_url    
        browser.visit(img_url)
        html = browser.html
        soup = bs(html, "html.parser")
        downloads = soup.find("div", class_="downloads")
        image_url = downloads.find("a")["href"]
        hemisphere_image_urls.append({"title": hemi_title, "img_url": image_url})


    
    ########### Store the return value in Mongo as a Python dictionary ###########
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_facts": mars_facts,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    ########### Close the browser after scraping ###########
    browser.quit()

    ########### Return results ###########
    return mars_data

if __name__ == '__main__':
    scrape()