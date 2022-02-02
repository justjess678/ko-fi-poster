#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 16:02:01 2022

@author: jess
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import xml.etree.ElementTree as ET
import os
import time
import pyautogui
import requests
import feedparser
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

rss_feed = "https://your-blog-here.tumblr.com/rss"
post_text = ""

kofi_user = "your username here"
kofi_pass = "your password here"

def post_to_kofi(title, text, image  = "ko-fi pics/tumblr_image.png"):
    options = webdriver.ChromeOptions()
    #prefs = {'profile.default_content_setting_values': {'images': 2, 'javascript': 2}}
    #options.add_argument("headless")
    #options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome("./lib/chromedriver", options=options)
    
    wait = WebDriverWait(driver, 10)
    
    driver.get("https://ko-fi.com/account/login")
    #TODO: login
    driver.find_element_by_id('UserName').send_keys(kofi_user)
    driver.find_element_by_id('Password').send_keys(kofi_pass)
    driver.find_element_by_id('formSubmitButton').click()
    
    # wait for the end of the redirection
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dash-left"]/div[2]/div[1]/div/div/div/div[1]/div/div[1]/div/div[1]/a')))

    #actually posting
    driver.get("https://ko-fi.com/transatlanticcrochet")

    driver.find_element_by_xpath('//i[@class="far fa-fw fa-chevron-down"]').click() #opens dropdown menu
    time.sleep(4)
    driver.find_element_by_xpath('//*[@id="tabsMenu"]/div[1]/div/div/div/div/ul/li[1]/a').click() #opens create post dialogue

    # create post window appears
    img_abs_path = os.path.join(os.getcwd(), image)
    choose_img = driver.find_element_by_xpath('//*[@id="addContentMenuModal"]/div/div/div/div[4]/a[1]') #select image post
    choose_img.click()

    #TODO: there must be a better way
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.press('enter')

    time.sleep(4)

    #make the post
    driver.find_element_by_id('postImageTitle').send_keys(title)
    driver.find_element_by_id('postImageDescription').send_keys(text)
    driver.find_element_by_id('imageUploadSumbit').click()
    time.sleep(4)

    driver.quit()

    

def get_latest_tumblr_post():
    Feed = feedparser.parse(rss_feed)
    post = Feed['entries'][0]['description']
    soup = BeautifulSoup(post, 'html.parser')

    for img in soup.find_all('img'):
        image_url = img.get('src')
    download_img(image_url)
    title = ""

    post_text = ""
    data = None


    if os.path.exists('../../tumblr/last_post.txt'):
        f = open('../../tumblr/last_post.txt', "r+")
        data = f.read()

    for desc in soup.find_all('p'):
        if title == "":
            title += desc.text
            if data is not None:
                if title in data:
                    f.close()
                    return False, False
        else:
            post_text += desc.text + "\n"

    p_text = ''.join(c for c in post_text if c <= '\uFFFF')

    if not os.path.exists('../../tumblr/last_post.txt'):
        f = open('../../tumblr/last_post.txt', "w")
    #write to post fill
    f.truncate(0)
    f.write(title)
    f.close()
    print(p_text)

    return p_text, title


def download_img(image_url):
    if not os.path.exists('../../tumblr'):
        os.makedirs('../../tumblr')

    if os.path.exists('../../tumblr/tumblr_image.png'):
        os.remove('../..//tumblr/tumblr_image.png')

    print("Using URL: ", image_url)

    img_down = requests.get(image_url)
    file = open("../../tumblr/tumblr_image.png", "wb")
    file.write(img_down.content)
    file.close()


post_text, title = get_latest_tumblr_post()
if title:
    post_to_kofi(title, post_text)