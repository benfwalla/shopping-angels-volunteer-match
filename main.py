import os
import json
import gspread
from fastapi import FastAPI
from volunteer_match import find_nearest_volunteers
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# use creds to create a client to interact with the Google Drive API
scopes = ['https://spreadsheets.google.com/feeds']
json_creds = os.getenv("GS_CREDS")
creds_dict = json.loads(json_creds)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)

gc = gspread.authorize(creds)

app = FastAPI()

@app.get("/volunteer-match/")
def get_nearest_volunteers(latlong: str, state: str, key: str, tablefmt: str=None):
    try:
        return find_nearest_volunteers(latlong, state, key, gc, tablefmt)
    except Exception as e:
        print(e)
