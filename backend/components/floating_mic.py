import streamlit.components.v1 as components


# =========================================
# FLOATING VOICE ASSISTANT
# =========================================

def render_floating_mic():

    component_html = r"""

    <style>

    #helios-mic-root{

        position:fixed;

        right:28px;
        bottom:24px;

        z-index:999999;

        font-family:Inter,sans-serif;

        pointer-events:none;
    }

    .helios-shell{

        display:flex;

        flex-direction:column;

        align-items:flex-end;

        gap:16px;
    }

    .voice-panel{

        width:290px;

        position:relative;

        overflow:hidden;

        border-radius:28px;

        padding:18px;

        background:
        linear-gradient(
            180deg,
            rgba(15,23,42,0.88),
            rgba(2,6,23,0.96)
        );

        border:
        1px solid rgba(255,255,255,0.06);

        backdrop-filter:blur(28px);

        box-shadow:
        0 14px 40px rgba(0,0,0,0.28);

        pointer-events:auto;
    }

    .voice-panel::before{

        content:"";

        position:absolute;

        width:220px;
        height:220px;

        border-radius:999px;

        background:
        rgba(124,58,237,0.12);

        top:-120px;
        right:-100px;

        filter:blur(40px);
    }

    .voice-top{

        position:relative;
        z-index:2;

        display:flex;

        align-items:center;

        gap:14px;

        margin-bottom:18px;
    }

    .voice-icon{

        width:52px;
        height:52px;

        border-radius:18px;

        display:flex;
        align-items:center;
        justify-content:center;

        font-size:22px;

        background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );

        color:white;

        box-shadow:
        0 0 24px rgba(124,58,237,0.35);
    }

    .voice-title{

        color:white;

        font-size:16px;
        font-weight:800;

        margin-bottom:4px;

        letter-spacing:-0.3px;
    }

    .voice-sub{

        color:#94a3b8;

        font-size:12px;

        line-height:1.6;
    }

    .wave-wrap{

        position:relative;
        z-index:2;

        padding:14px;

        border-radius:22px;

        background:
        rgba(255,255,255,0.03);

        border:
        1px solid rgba(255,255,255,0.05);
    }

    #wave-canvas{

        width:100%;
        height:76px;

        border-radius:16px;
    }

    .wave-status{

        margin-top:14px;

        display:flex;
        align-items:center;
        justify-content:space-between;

        gap:12px;
    }

    .status-pill{

        padding:6px 12px;

        border-radius:999px;

        background:
        rgba(124,58,237,0.12);

        border:
        1px solid rgba(168,85,247,0.18);

        color:#d8b4fe;

        font-size:11px;
        font-weight:800;

        letter-spacing:0.4px;
    }

    .status-text{

        color:#cbd5e1;

        font-size:12px;
    }

    .mic-wrap{

        position:relative;

        pointer-events:auto;
    }

    .pulse-ring{

        position:absolute;

        inset:-10px;

        border-radius:999px;

        border:
        2px solid rgba(124,58,237,0.28);

        opacity:0;

        pointer-events:none;
    }

    .mic-btn.active + .pulse-ring{

        opacity:1;

        animation:pulse 1.8s infinite;
    }

    .mic-btn{

        position:relative;

        width:82px;
        height:82px;

        border-radius:999px;

        border:
        1px solid rgba(255,255,255,0.08);

        background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );

        display:flex;
        align-items:center;
        justify-content:center;

        cursor:pointer;

        overflow:hidden;

        transition:
        transform .22s ease,
        box-shadow .22s ease;

        backdrop-filter:blur(20px);

        box-shadow:
        0 12px 42px rgba(124,58,237,0.35);
    }

    .mic-btn:hover{

        transform:
        translateY(-3px) scale(1.03);

        box-shadow:
        0 18px 56px rgba(124,58,237,0.45);
    }

    .mic-btn.active{

        box-shadow:
        0 0 60px rgba(124,58,237,0.6);
    }

    .mic-btn::before{

        content:"";

        position:absolute;

        inset:0;

        background:
        radial-gradient(
            circle at top,
            rgba(255,255,255,0.22),
            transparent
        );
    }

    .mic-emoji{

        position:relative;
        z-index:2;

        font-size:32px;

        color:white;
    }

    @keyframes pulse{

        0%{

            transform:scale(0.92);

            opacity:0.85;
        }

        70%{

            transform:scale(1.28);

            opacity:0;
        }

        100%{

            transform:scale(1.35);

            opacity:0;
        }
    }

    </style>

    <div id="helios-mic-root">

        <div class="helios-shell">

            <div class="voice-panel">

                <div class="voice-top">

                    <div class="voice-icon">
                        ⚡
                    </div>

                    <div>

                        <div class="voice-title">
                            HELIOS Voice Intelligence
                        </div>

                        <div class="voice-sub">
                            Realtime conversational cognition and neural voice orchestration
                        </div>

                    </div>

                </div>

                <div class="wave-wrap">

                    <canvas
                        id="wave-canvas"
                        width="260"
                        height="76"
                    ></canvas>

                    <div class="wave-status">

                        <div class="status-pill">
                            LIVE
                        </div>

                        <div
                            id="voiceStatus"
                            class="status-text"
                        >
                            Listening standby
                        </div>

                    </div>

                </div>

            </div>

            <div class="mic-wrap">

                <div
                    id="micBtn"
                    class="mic-btn"
                >

                    <div class="mic-emoji">
                        🎤
                    </div>

                </div>

                <div class="pulse-ring"></div>

            </div>

        </div>

    </div>

    <script>

    const micBtn =
        document.getElementById('micBtn');

    const canvas =
        document.getElementById('wave-canvas');

    const ctx =
        canvas.getContext('2d');

    const statusText =
        document.getElementById('voiceStatus');

    let running = false;

    let raf = null;

    let audioStream = null;

    window.heliosAudioContext = null;

    function roundRect(
        ctx,
        x,
        y,
        w,
        h,
        r,
        fill
    ){

        ctx.beginPath();

        ctx.moveTo(x+r,y);

        ctx.arcTo(x+w,y,x+w,y+h,r);

        ctx.arcTo(x+w,y+h,x,y+h,r);

        ctx.arcTo(x,y+h,x,y,r);

        ctx.arcTo(x,y,x+w,y,r);

        ctx.closePath();

        if(fill){
            ctx.fill();
        }
    }

    function drawIdle(){

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        const bars = 48;

        const width =
            canvas.width / bars;

        for(let i=0;i<bars;i++){

            const variance =
                Math.random()*0.12 + 0.04;

            const h =
                variance * canvas.height;

            const x = i * width;

            const y =
                (canvas.height - h)/2;

            ctx.fillStyle =
                'rgba(124,58,237,' +
                (0.15 + variance*0.6) +
                ')';

            roundRect(
                ctx,
                x+2,
                y,
                width-4,
                h,
                10,
                true
            );
        }

        raf =
            requestAnimationFrame(drawIdle);
    }

    async function startMic(){

        running = true;

        micBtn.classList.add('active');

        statusText.innerText =
            "Voice stream active";

        try{

            audioStream =
                await navigator.mediaDevices
                .getUserMedia({
                    audio:true
                });

            window.heliosAudioContext =
                new (
                    window.AudioContext ||
                    window.webkitAudioContext
                )();

            const audioCtx =
                window.heliosAudioContext;

            const source =
                audioCtx.createMediaStreamSource(
                    audioStream
                );

            const analyser =
                audioCtx.createAnalyser();

            analyser.fftSize = 256;

            source.connect(analyser);

            const data =
                new Uint8Array(
                    analyser.frequencyBinCount
                );

            function drawLive(){

                analyser.getByteFrequencyData(
                    data
                );

                ctx.clearRect(
                    0,
                    0,
                    canvas.width,
                    canvas.height
                );

                const bars = 48;

                const width =
                    canvas.width / bars;

                const step =
                    Math.floor(
                        data.length / bars
                    );

                for(let i=0;i<bars;i++){

                    const value =
                        data[i*step] / 255;

                    const h =
                        Math.max(
                            10,
                            value * canvas.height
                        );

                    const x =
                        i * width;

                    const y =
                        (canvas.height - h)/2;

                    ctx.fillStyle =
                        'rgba(37,99,235,' +
                        (0.18 + value*0.9) +
                        ')';

                    roundRect(
                        ctx,
                        x+2,
                        y,
                        width-4,
                        h,
                        10,
                        true
                    );
                }

                raf =
                    requestAnimationFrame(
                        drawLive
                    );
            }

            cancelAnimationFrame(raf);

            drawLive();

        }catch(err){

            console.error(err);

            statusText.innerText =
                "Microphone access denied";

            stopMic();
        }
    }

    function stopMic(){

        running = false;

        micBtn.classList.remove('active');

        statusText.innerText =
            "Listening standby";

        if(audioStream){

            audioStream
            .getTracks()
            .forEach(
                track => track.stop()
            );

            audioStream = null;
        }

        if(window.heliosAudioContext){

            window.heliosAudioContext.close();

            window.heliosAudioContext = null;
        }

        cancelAnimationFrame(raf);

        drawIdle();
    }

    micBtn.addEventListener(
        'click',
        () => {

            if(running){

                stopMic();

            }else{

                startMic();
            }
        }
    );

    drawIdle();

    </script>

    """

    components.html(
        component_html,
        height=390,
        scrolling=False
    )