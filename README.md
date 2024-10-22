# Zoom Rooms Basic Dialer

Put simply, the basic dialer takes a comma separated values file (meetings.csv) as input and uses it to automatically dial Zoom Rooms into Zoom Meetings.

## Requirements

- [Python 3.10+](https://www.python.org)
  - [requests 2.32.3+ (via pip)](https://pypi.org/project/requests/)

## Setup

### Zoom App Marketplace

Basic dailer requires use of the Zoom API.  There are exactly two required API endpoints:

- [GET: List Zoom Rooms](https://developers.zoom.us/docs/api/rooms/#tag/zoom-rooms/GET/rooms)
- [PATCH: Use Zoom Room Controls](https://developers.zoom.us/docs/api/rooms/#tag/zoom-rooms/PATCH/rooms/{id}/events)

For basic dialer to access these APIs you will need to create a Server to Server OAuth app via the Zoop App Marketplace:

- [Create a Server-to-Server OAuth App](https://developers.zoom.us/docs/internal-apps/create/)

Your app will need the following two granular scopes:

- zoom_rooms:read:list_rooms:admin (for obtaining the Zoom Rooms list)
- zoom_rooms:update:room_control:admin (to send meeting join commands to Zoom)

Be sure to activate the app once you have added the necessary scopes.

### app_credentials.py

Copy and paste your app credentials into app_credentials.py (don't forget to save the file when finished).

## Principle of Operation

When executed, dialer.py does the following:

- reads meetings.csv into a nested list (to be interated over later)
- establishes Zoom API client session
- gets current Zoom Room list via Zoom API
- gets current time (system clock) in H:MM AM/PM format
- determines the character representing the current day of the week (system clock)
- iterates over the nested meeting list looking for meetings to automatically dial
- skips meetings not scheduled today (matching day of week character)
- skips meetings that do not fall within the start and end dates
- skips meetings where the current time is not equal to the join time (matches join time string)
- automatically joins meetings where all these conditions are otherwise met.

It generally takes only a matter of seconds for the program to execute.  It is intended to be scheduled to run minutely (top of each minute) using the underlying task scheduler from your operating system of choice.

## File Descriptions

### api_client.py

This module serves to establish a client for calling the Zoom API.  As part of its operation, it handles the Server to Server OAuth handshake.  Intentionally, it can only process GET and PATCH HTTP methods as these are the only two needed for the dialer to operate.

### api_endpoints.py

This module contains the "get_rooms" and "connect_room_to_meeting" functions that are used to identify and control Zoom Rooms.

### app_credentials.py

This module exists to store the secure contants needed to access the Zoom API:

- Account ID
- Client ID
- Client Secret

These values are found within your Server to Server OAuth app configuration within the Zoom App Marketplace management console.  Simply paste the values into app_credentials.py and save.

### dailer.py

This is the main module which is executed (on a minutely schedule) to perform the automatic dialing of Zoom Rooms into meetings.

### meetings.csv

File containing all required details to allow Zoom Rooms to connect to meetings on a weekly recurrence basis.  An example file is provided for reference.

The header row exists for reference and is not used by the program.

- start_date in the format of YYYY-MM-DD
- end_date in the format of YYYY-MM-DD
- join_time in the format of H:MM AM/PM (no leading zero on hour, space between AM or PM, upper case)
- days can contain a combination of M, T, W, R and F (upper case)
- zoom_room is a case sensitive, semicolon delimited list of Zoom Room names (the program resolves the room name to the actual room_id automatically)
- meeting_id is self explanatory
- meeting_passcode is also self explanatory

NOTE:  In our environment, we require all meetings to have a six digit passcode.

### requirements.txt

Contains the single 3rd party requirement, that being the popular "requests" library.  If requests is not already installed in your Python environment, you can accomplish this using one of two methods:

`pip install -r requirements.txt`
`pip install requests`

## Miscellaneous

Meetings used with the basic dialer should have the "allow participants to join anytime" option enabled.  This will allow rooms to join the meeting regardless of whether the meeting host has already started the meeting.

Basic dialer can be used to join any Zoom meeting regardless of whether the meeting belongs to an external Zoom account.

While not required, it is also recommended to set the meeting type to "recurring" with a recurrence of "no fixed time" (aka "meet anytime")

As dialer.py depends on accurate time, please also ensure time is set correctly on the host system.  All times are local.

It is not possible to issue commands to a Zoom Room directly.  Instead, commands are relayed via Zoom's cloud infrastructure.  When a join command is sent to the Zoom API (because we can't send it to the room directly), Zoom's servers will only respond with HTTP 202 Accepted.  For this reason, the dialer does not listen for a server response.  See:

- [HTTP 202: Accepted](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202)