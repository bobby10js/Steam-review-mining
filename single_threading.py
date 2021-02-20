import requests
import json 
import csv
import urllib.parse
import sys
cursor="*"
game_id=sys.argv[1] if(len(sys.argv)>1) else input("Game id: ")
file_name=game_id + (":"+sys.argv[2] if(len(sys.argv)>2) else "")
URL = "https://store.steampowered.com/appreviews/"+game_id+"?json=1&num_per_page=100&review_type=positive&purchase_type=steam&day_range=92233720368547760000&language=all&cursor=" #filter=recent,updated day_range=92233720368547760000
cursor_lst=[]
with open(file_name+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header= ['id','language','review','num_reviews','votes_up','timestamp_created']
    writer.writerow(header)
    cnt = 0
    while(cursor!=None):
        # print(cursor)
        if(cursor in cursor_lst):
            print("Duplicate Cursor")
            break                     # comment 'break' if you are okay with having duplicate pages/json file
        cursor_lst.append(cursor)
        page = requests.get(URL+urllib.parse.quote_plus(cursor))
        y = json.loads(page.content)
        # print(y["query_summary"]["num_reviews"])
        for i in y["reviews"]:
            author= i["author"]
            # print(user_id)
            p =  int(author['num_reviews'])/int(author['num_games_owned']) if author['num_games_owned']!=0 else 0
            if(p>=0.1 or int (author['num_reviews'])>40 or len(i['review'])>250):
                writer.writerow([author['steamid'],i['language'],i['review'],author['num_reviews'],i['votes_up'],i['timestamp_created']])
                cnt+=1 #,i['voted_up'],i['steam_purchase'],author['num_games_owned'], int(author['num_reviews'])/int(author['num_games_owned']) if author['num_games_owned']!=0 else 0 ,i['timestamp_updated']]
        cursor=y['cursor']
        # print(cnt)
    print('\n',game_id+': Completed.\nCollected '+str(cnt)+' review(s)\nData written to '+game_id+'.csv')
    writer.writerow(["success tag"])

