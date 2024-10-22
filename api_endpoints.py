class Rooms(object):
    def __init__(self, client):
        self.client = client

    #granular scope: zoom_rooms:read:list_rooms:admin
    def get_rooms(self):
        client = self.client
        response_json = client.get(f'/v2/rooms?page_size=300&type=ZoomRoom')
        return response_json['rooms']

    #granular scope: zoom_rooms:update:room_control:admin
    def connect_room_to_meeting(self, room_id, meeting_id, meeting_passcode):
        client = self.client
        data = {}
        data['method'] = 'zoomroom.meeting_join'
        data['params'] = {}
        data['params']['meeting_number'] = str(meeting_id)
        data['params']['passcode'] = str(meeting_passcode)
        data['params']['force_accept'] = 'true'
        client.patch(f'/v2/rooms/{room_id}/events', data=data)
