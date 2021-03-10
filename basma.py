from telethon import TelegramClient, events, Button, extensions, functions, utils
from telethon.tl.types import UpdateBotInlineSend
import demjson
import os
from os.path import dirname, realpath, join
import subprocess

admin = 637572531
api_id = 922976
api_hash = "39f163482b277156e2c81a1e50145787"
step = 0
caption = ""
client = TelegramClient("voice_bot_session", api_id, api_hash)
client.parse_mode = None
msgs = {}
config = {}
WD = dirname(realpath(__file__))


def get_config():
    global config
    file = open(join(WD, "config.json"), "r")
    config = demjson.decode(file.read())
    file.close()


def save_config():
    file = open(join(WD, "config.json"), "w")
    file.write(demjson.encode(config))
    file.close()


@client.on(events.NewMessage())
async def my_event_handler(event):
    global caption
    global step
    if len(config) == 0:
        try:
            get_config()
        except Exception as er:
            save_config()
            print(str(er))

    message = event.message
    print(len(message.text))
    if event.sender_id == admin:
        if len(message.text) != 0:
            caption = message.text
            step = 1
            await event.reply("أرسل الصوت الأن")
        elif message.voice is not None and step != 0:
            try:
                if message.voice is not None:
                    config[caption] = utils.pack_bot_file_id(message.voice)
                    await event.reply("تم اضافه الاغنيه")
                    save_config()
                    get_config()
            except Exception as er:
                save_config()
                print(str(er))
            step = 0
            caption = ""
            # await client.send_voice
        elif message.audio is not None and step != 0:
            try:
                file = await client.download_media(message.media, "tmp")
                os.rename(file.replace("\\", "/"), "tmp/file.mp3")
                command = "ffmpeg  -y -i ./tmp/file.mp3 -acodec libopus -b:a 44100 -ar 48000 -vbr on -compression_level 10 -ac 1 -max_muxing_queue_size 9999  -vsync 2 ./tmp/file.ogg"

                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                process.wait()
                if process.returncode == 0:
                    file = await client.send_file(
                        event.sender_id,
                        file=("./tmp/file.ogg"),
                        supports_streaming=True,
                    )
                    if file.voice is not None:
                        config[caption] = utils.pack_bot_file_id(file.voice)
                        await event.reply("تم اضافه الاغنيه")
                        save_config()
                        get_config()
                        os.remove("./tmp/file.mp3")
                        os.remove("./tmp/file.ogg")
            except Exception as er:
                os.remove("./tmp/file.mp3")
                os.remove("./tmp/file.ogg")
                print(str(er))
                print(type(er))
        elif message.video is not None and step != 0:
            try:
                file = await client.download_media(message.media, "tmp")
                os.rename(file.replace("\\", "/"), "tmp/file.mp4")
                command = "ffmpeg  -y -i ./tmp/file.mp4 -acodec libopus -b:a 44100 -vn ./tmp/file.ogg"
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                process.wait()
                if process.returncode == 0:
                    file = await client.send_file(
                        event.sender_id,
                        file=("./tmp/file.ogg"),
                        supports_streaming=True,
                    )
                    if file.voice is not None:
                        config[caption] = utils.pack_bot_file_id(file.voice)
                        await event.reply("تم اضافه الاغنيه")
                        save_config()
                        get_config()
                        os.remove("./tmp/file.mp4")
                        os.remove("./tmp/file.ogg")
            except Exception as er:
                os.remove("./tmp/file.mp4")
                os.remove("./tmp/file.ogg")
                print(str(er))
                print(type(er))
    else:
        await event.reply("لأضافه مقطع راسل  @anime19")


@client.on(events.InlineQuery)
async def handler(event):
    try:
        builder = event.builder
        to = event.query.query
        arr = [
            builder.document(
                file=utils.resolve_bot_file_id(value), title=key, type="voice"
            )
            for key, value in config.items()
            if to in key.lower()
        ]
        if len(arr) != 0:
            await event.answer(arr)
        else:
            await event.answer([builder.article("test", "test")])
    except Exception as er:
        print(er)


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


client.start()
client.run_until_disconnected()
