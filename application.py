from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
# import requests
# from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

# scrapetube for you tube scraping and other imports

import os
import pyfiglet
import scrapetube
from datetime import datetime
import pandas as pd
import requests

# debugging and logging
import logging
logging.basicConfig(filename='YOutube.log',level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

application = Flask(__name__) # initializing a flask app
app=application

# from utils import extract_number
# extract number function to be exported to a different module

def extract_number(string):
    numbers = []
    for char in string:
        if char.isdigit():
            numbers.append(char)
        else:
            continue
    if numbers:
        extracted_number = int("".join(numbers))
    return extracted_number

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            channel_name = request.form['content'].replace(" ","")
            limit=request.form['num']


            logging.info("channel_name=input Enter Channel Name")

            channel_url=f"https://www.youtube.com/@{channel_name}/videos"

            # channel_url = input("Insert channel URL: ")

            if channel_url == "":

                return render_template("index.html")

            while True:
                # limit = input("How many videos do you want? ")
                if limit == "":
                    print("No input received. Exiting...")
                    # exit()
                    return render_template('index.html')

                elif limit.isdigit():
                    limit = int(limit)
                    break
                else:
                    print("Invalid input. Please insert a number.")
            print("")


            print("Searching {} videos for {}".format(limit, channel_url))

            videos = scrapetube.get_channel(channel_url=channel_url, limit=limit)

            now = datetime.now()
            videos_data = []
            x = -1
            for video in videos:
                video_id = video['videoId']
                title = video['title']['runs'][x+1]['text']
                thumbnail_url = video['thumbnail']['thumbnails'][-1]['url']
               
                view_count = extract_number(video['viewCountText']['simpleText'])

                # Extract time of posting
                logging.info("Extractig the time of posting ")

                post_time_text = video['publishedTimeText']['simpleText']
                
                # Extract video URL
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos_data.append((now, video_id,video_url, title,thumbnail_url,view_count,post_time_text))

                response = requests.get(thumbnail_url)


            videos_data.reverse()
            df = pd.DataFrame(videos_data, columns=['date_time', 'video_id','video_url','title','thumbnail_url','view_count','post_time_text'])
         
            mydict=df.to_dict('records')
          

            # Save file to the Csv file
            logging.info("checking the cvs file and then creating the csv file  to store the data after the scrappibg")

            if os.path.isfile('videos_data.csv'):
                existing_df = pd.read_csv('videos_data.csv', nrows=1)
                existing_columns = set(existing_df.columns)
                new_columns = set(df.columns)
                if existing_columns == new_columns:

                    df.to_csv('videos_data.csv', mode='a', header=False, index=False)
                else:
                    missing_columns = new_columns.difference(existing_columns)
                    raise ValueError(f"Columns {missing_columns} do not match between new DataFrame and existing csv file.")
            else:
                df.to_csv('videos_data.csv', index=False)
            
#saving the data to the mongodb

            logging.info("Saving Data in the Mongodb After scrapping")

            client = pymongo.MongoClient("mongodb+srv://sachinsharma95:passsachin@cluster0.qx6p45u.mongodb.net/?retryWrites=true&w=majority")

            db=client['you_tubeData']
            utube_col=db['utube_col']
            utube_col.insert_many(mydict)

            return render_template("results.html",mydict=mydict)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong '

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
	#app.run(debug=True)

logging.info("this file is rendering over the 8000 port ")