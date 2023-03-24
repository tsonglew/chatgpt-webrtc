// [1] Prompt: 有一个用于 webrtc 视频通话的页面，页面上有个视频标签，用来播放远端的视频流。页面上还有 1 个 start button 用于开始通话
// 请完成以下几个功能:
// - 当用户点击 start button 时，创建一个 RTC 连接对象，并通过服务端提供的 POST /offer 将浏览器的 sdp 发给服务端，并建立 webrtc 连接。当服务端返回的 sdp 信息到达时，将其设置到 RTC 连接对象中。
//   当检测到服务端的轨道时，将其设置到 RTC 连接对象中。
// - 当 webrtc 连接建立成功后，把获取到的远端的视频流绑定到视频标签上


// [2] Prompt: startButton 的 id 应该是 startButton, video 的 id 应该是 localVideo
// const startButton = document.querySelector('#start-button');
// const video = document.querySelector('#remote-video');
const startButton = document.querySelector('#startButton');
const video = document.querySelector('#localVideo');

let pc = null;
let localStream = null;


startButton.addEventListener('click', async () => {
  try {
    var config = {
        sdpSemantics: 'unified-plan',
        // [4] Prompt: 使用 stun server
        iceServers: [
            {
                urls: 'stun:stun.l.google.com:19302'
            }
        ]
    };

    pc = new RTCPeerConnection(config);
    pc.addEventListener('track', function (evt) {
      if (evt.track.kind == 'video') {
         video.srcObject = evt.streams[0];
      }
    });


    // [5] Prompt: 本地连接需要创建一个 offer，将这个 offer 设置为本地的 sdp。然后开始收集本地的 ice candidate，当 ice candidate 收集完成后，将本地的 sdp 发送给服务端
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        // [6] 手动添加 ice candidate 收集
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState () {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        console.log(answer);
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        alert(e);
    });
  } catch (error) {
    console.error(error);
  }
});