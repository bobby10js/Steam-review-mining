import requests
from bs4 import BeautifulSoup
import json
import os
page_size= 2000
n=0
cnt=0
print("Find the rank of a game in the suugestion list of steam")
game_name = input("enter game the name:")
while(n<page_size):
    URL = "https://store.steampowered.com/search/results/?query&start="+str(n)+"&count=50&dynamic_data=&sort_by=_ASC&term=point%20and%20click&snr=1_7_7_151_7&infinite=1"
    page = requests.get(URL)
    res = json.loads(page.content)
    soup = BeautifulSoup(res["results_html"], "html.parser")
    for i in soup.findAll("a"):
        name = "\""+i.find("span",class_="title").text+"\""
        print(name ,i["href"])
        cnt+=1
        if(game_name in name):
            print(cnt)
            exit()
    n+=50
print(n)
