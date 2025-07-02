from logging import getLogger

from aiortc import MediaStreamTrack, RTCPeerConnection
from nio import (AsyncClient, CallAnswerEvent, CallHangupEvent,
                 CallInviteEvent, RoomKeyRequestMessage)

logger = getLogger(__name__)


class Connection:
    def __init__(self, client: AsyncClient, token: str):
        self.client = client
        self.client.access_token = token

        self.pc = None
        self.recorder = None
        self.room_id = None

        self.client.add_event_callback(self.on_invite, CallInviteEvent)
        self.client.add_event_callback(self.on_answer, CallAnswerEvent)
        self.client.add_event_callback(self.on_hangup, CallHangupEvent)

    async def on_invite(self, room: RoomKeyRequestMessage, event: CallInviteEvent):
        logger.info(f"Received call invite in room {room.room_id}")

        self.room_id = room.room_id
        self.pc = RTCPeerConnection()

        @self.pc.on("track")
        async def on_track(track: MediaStreamTrack) -> None:
            logger.debug(f"Track received: {track.kind}")

            @track.on("ended")
            async def on_ended() -> None:
                logger.info(f"Track {track.kind} ended")

        await self.pc.setRemoteDescription(event.offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

    async def on_answer(self, room, event):
        if self.pc is None:
            return
        await self.pc.setRemoteDescription(event.answer)
        await self.recorder.start()
        await self.client.send_call_answer(room.room_id, self.pc.localDescription)


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