# [1] prompt: 使用 aiohttp + aiortc 生成一个 webrtc 服务后端，当客户端连上服务端后，获取服务端本地的视频流，与客户端建立连接，
# 有这几个路由：
# - / ，返回 index.html 文件
# - /client.js，返回 client.js 文件
# - /offer，处理信令相关逻辑

from aiohttp import web
import asyncio
import aiortc
from aiortc.contrib.media import MediaPlayer, MediaRelay

# [5] Prompt: 修复所有缺失的 import 
import platform
from aiortc import RTCPeerConnection, RTCSessionDescription
import json

pcs = set()

relay = None
webcam = None


async def index(request):
    content = open('index.html', 'r').read()
    return web.Response(content_type='text/html', text=content)

async def client_js(request):
    content = open('client.js', 'r').read()
    return web.Response(content_type='application/javascript', text=content)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    print('========= offer ===========')
    print(offer)
    
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # -- [4][2] 手动添加
    video = await get_local_video_track()
    pc.addTrack(video)
    
    # --- [2] prompt: 用 python 3.8 的语法优化一下
    # answer = yield from pc.createAnswer()
    # await pc.setLocalDescription(answer)
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    print(answer)
    await pc.setLocalDescription(answer)
    
    # -- [3] prompt: 将本地 PeerConnection 的 sdp 返回给客户端，格式为 json，包含 sdp 和 type 两个字段
    # return web.Response(content_type='application/json', text=json.dumps({'result': 'ok'}))
    response = {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type}
    print(f"Response: {response}")
    return web.Response(content_type='application/json', text=json.dumps(response))

async def on_shutdown(app):
    for pc in pcs:
        await pc.close()


# -- [4][1] prompt: 写一个 mac 获取本地视频流的方法，从本地的摄像头上获取640*480分辨率、30fps 的视频轨道
async def get_local_video_track():
    # -- [6] 手动修改 video = MediaPlayer('/dev/video0', format='v4l2', options={'video_size': '640x480', 'framerate': '30'})
    global relay, webcam
    options = {"framerate": "30", "video_size": "640x480"}
    if relay is None:
        if platform.system() == "Darwin":
            webcam = MediaPlayer(
                "default:none", format="avfoundation", options=options
            )
        elif platform.system() == "Windows":
            webcam = MediaPlayer(
                "video=Integrated Camera", format="dshow", options=options
            )
        else:
            webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
        relay = MediaRelay()
    return relay.subscribe(webcam.video)


app = web.Application()
app.on_shutdown.append(on_shutdown)
app.router.add_get('/', index)
app.router.add_get('/client.js', client_js)
app.router.add_post('/offer', offer)


# -- [7] by ChatGPT Prompt: 增加一个可以获取二维码的路由，就叫 /qrcode 吧。客户端访问这个路由时会在服务端生成一个二维码的图片，并以 png 的格式返回给客户端,
import qrcode
import io
async def qr_code(request):
    # 获取根路径dict
    root_path = request.url.with_path('/').human_repr()
    print(root_path)
    # 创建一个二维码对象并设置内容为根路径
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(root_path)
    qr.make(fit=True)
    # 将二维码转换成图片
    img = qr.make_image(fill_color="black", back_color="white")
    # 将图片保存到内存中
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    # 返回图片
    return web.Response(body=img_byte_arr, content_type='image/png', headers={'Location': root_path})

  
app.router.add_get('/qrcode', qr_code)

web.run_app(app)
