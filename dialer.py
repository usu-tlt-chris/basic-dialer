#standard library imports
import datetime
import sys
import csv
from pathlib import Path

#local application/library specific imports
from api_client import ZoomClient
import app_credentials as app_credentials

#read meetings.csv into a nested list
if Path('meetings.csv').is_file():
    with open('meetings.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None) #skip header row
        meetings = list(reader)
else:
    exit(1)

#establish Zoom client
zoom = ZoomClient('https://api.zoom.us', app_credentials.ZOOM_ACCOUNT_ID, app_credentials.ZOOM_CLIENT_ID, app_credentials.ZOOM_CLIENT_SECRET)

#place fresh list of Zoom Rooms from Zoom into memory
rooms = zoom.rooms.get_rooms()

#get current time in H:MM AM/PM format
current_datetime = datetime.datetime.now()
current_time = current_datetime.strftime('%I:%M %p').lstrip('0')

#determine character representing the current day of the week
days_tuple = ('#', 'M', 'T', 'W', 'R', 'F')
today_integer = datetime.date.today().strftime('%w')
today_character = days_tuple[int(today_integer)]

#attempt Zoom Room automatic dail
for meeting in meetings:
    start_date = str(meeting[0])
    end_date = str(meeting[1])
    join_time = str(meeting[2])
    days = str(meeting[3])
    rooms_string = str(meeting[4])
    meeting_id = str(meeting[5])
    meeting_passcode = str(meeting[6])

    #skip meetings not scheduled today
    if today_character not in days:
        continue

    #skip meetings that do not fall within the start and end dates
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    if not start_datetime <= today <= end_datetime:
        continue

    if current_time == join_time: #then we've found a meeting to dial into
        rooms_list = rooms_string.split(';')
        for room in rooms_list:
            #check to see if provided room name actually exists in Zoom and get the list index for the Zoom Room if it does
            room_index = next((index for index, room_object in enumerate(rooms) if room_object['name'] == room), None)
            #skip invalid room names
            if room_index is None:
                continue
            #dial into meeting
            zoom.rooms.connect_room_to_meeting(room_id=rooms[room_index]['id'], meeting_id=meeting_id, meeting_passcode=meeting_passcode)
            continue

sys.exit(0)
