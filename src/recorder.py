import asyncio

from aiortc import MediaRecorder, RTCPeerConnection
from nio import AsyncClient, CallAnswerEvent, CallHangupEvent, CallInviteEvent


class Recorder:
    def __init__(self, hs, user, token):
        self.client = AsyncClient(hs, user, device_id="RECORDER")
        self.client.restore_login(user, device_id="RECORDER", access_token=token)
        self.pc = None
        self.recorder = None
        self.room_id = None

        self.client.add_event_callback(self.on_invite, CallInviteEvent)
        self.client.add_event_callback(self.on_answer, CallAnswerEvent)
        self.client.add_event_callback(self.on_hangup, CallHangupEvent)

    async def on_invite(self, room, event):
        self.room_id = room.room_id
        self.pc = RTCPeerConnection()
        self.recorder = MediaRecorder(f"{self.room_id}.mp4")
        @self.pc.on("track")
        async def on_track(track):
            self.recorder.addTrack(track)
        offer = event.offer.sdp
        await self.pc.setRemoteDescription(event.offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        await self.client.send_call_answer(room.room_id, answer)

    async def on_answer(self, room, event):
        ...

    async def on_hangup(self, room, event):
        await self.recorder.stop()
        await self.client.room_send(
            self.room_id, 'm.room.message',
            {
                "msgtype": "m.video",
                "body": f"{self.room_id}.mp4",
                "url": await self.upload_video(f"{self.room_id}.mp4")
            }
        )

    async def upload_video(self, path):
        resp = await self.client.upload(path, content_type='video/mp4')
        return resp.content_uri

    async def run(self):
        await self.client.sync_forever(timeout=30000)

if __name__ == "__main__":
    bot = RecorderBot(
        "https://prodmatrix.roomimo.com",
        "@recorder:roomimo.com",
        "YOUR_ACCESS_TOKEN"
    )
    asyncio.run(bot.run())
