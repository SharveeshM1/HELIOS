APP_CSS = """
<style>

:root{
    --bg:#0a0707;
    --bg-2:#100b0b;
    --panel:#161111;
    --panel-2:#1d1716;
    --panel-3:#2a2420;
    --line:#2a2420;
    --line-2:rgba(255,255,255,0.105);
    --text:#ffffff;
    --text-2:#e8e3e0;
    --muted:#a0a0a0;
    --muted-2:#6f6865;
    --primary:#661518;
    --accent:#8b1a1e;
    --rose:#a30037;
    --blue:#54a2ff;
    --indigo:#7d87ff;
    --ok:#83e2a1;
    --warn:#ffc56d;
    --danger:#ff6568;
    --radius:14px;
    --radius-sm:10px;
    --shadow:0 26px 80px rgba(0,0,0,.34);
}

*{box-sizing:border-box}

html,
body,
.stApp,
.stApp *{
    font-family:Geist,Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif !important;
    letter-spacing:0 !important;
}

html,
body,
.stApp{
    margin:0;
    background:var(--bg) !important;
    color:var(--text) !important;
    width:100%;
    max-width:100%;
    overflow-x:hidden !important;
}

.stApp,
div[data-testid="stAppViewContainer"],
section[data-testid="stMain"]{
    width:100% !important;
    max-width:100vw !important;
    overflow-x:hidden !important;
    background:
        radial-gradient(circle at 16% -8%,rgba(102,21,24,.42),transparent 32%),
        radial-gradient(circle at 86% 8%,rgba(139,26,30,.26),transparent 30%),
        linear-gradient(rgba(102,21,24,.13) 1px,transparent 1px),
        linear-gradient(90deg,rgba(102,21,24,.11) 1px,transparent 1px),
        linear-gradient(180deg,#0a0707 0%,#080606 100%) !important;
    background-size:auto,auto,44px 44px,44px 44px,auto !important;
}

.stApp:before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:0;
    background:
        linear-gradient(90deg,rgba(0,0,0,.34),transparent 18%,transparent 78%,rgba(0,0,0,.28)),
        radial-gradient(circle at 50% 0%,rgba(255,255,255,.05),transparent 42%);
}

#MainMenu,
footer,
header,
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label*="sidebar" i],
button[title*="sidebar" i]{
    display:none !important;
}

.block-container{
    width:100% !important;
    max-width:none !important;
    padding:18px 28px 300px 326px !important;
    position:relative;
    z-index:1;
    overflow-x:hidden !important;
}

.helios-recovery-sidebar{
    position:fixed;
    z-index:999999;
    top:0;
    left:0;
    bottom:0;
    width:292px;
    padding:16px 14px 22px;
    overflow-y:auto;
    background:
        linear-gradient(90deg,rgba(255,101,104,.18),transparent 28%,transparent 72%,rgba(255,255,255,.035)),
        radial-gradient(circle at 22% 0%,rgba(102,21,24,.26),transparent 34%),
        radial-gradient(circle at 44% 9%,rgba(163,0,55,.16),transparent 22%),
        linear-gradient(180deg,rgba(16,11,11,.985),rgba(7,5,5,.995));
    border-right:1px solid rgba(255,255,255,.12);
    box-shadow:18px 0 52px rgba(0,0,0,.42);
    transition:width .22s cubic-bezier(.2,.8,.2,1), padding .22s cubic-bezier(.2,.8,.2,1);
}

.helios-recovery-sidebar.is-collapsed{
    width:72px;
    padding:16px 10px 22px;
    overflow-x:hidden;
}

.helios-recovery-sidebar::-webkit-scrollbar{
    width:7px;
}

.helios-recovery-sidebar::-webkit-scrollbar-thumb{
    border-radius:999px;
    background:rgba(255,255,255,.16);
}

.helios-recovery-brand{
    display:flex;
    align-items:center;
    gap:11px;
    margin:2px 0 16px;
    position:relative;
}

.helios-recovery-brand > span{
    width:40px;
    height:40px;
    flex:0 0 40px;
    display:grid;
    place-items:center;
    border-radius:12px;
    color:#fff;
    font-size:16px;
    font-weight:860;
    background:
        radial-gradient(circle at 32% 22%,rgba(255,255,255,.36),transparent 30%),
        linear-gradient(135deg,var(--primary),var(--accent) 54%,var(--rose));
    border:1px solid rgba(255,255,255,.17);
    box-shadow:0 12px 26px rgba(102,21,24,.30);
    animation:heliosLogoFloat 4.2s ease-in-out infinite;
    will-change:transform,box-shadow;
}

.helios-recovery-toggle{
    width:30px;
    height:30px;
    display:grid;
    place-items:center;
    margin-left:auto;
    border-radius:999px;
    color:#eee5e1 !important;
    text-decoration:none !important;
    background:rgba(255,255,255,.055);
    border:1px solid rgba(255,255,255,.13);
    box-shadow:0 10px 24px rgba(0,0,0,.24);
    font-size:20px;
    font-weight:900;
    line-height:1;
    transition:transform .16s ease, background .16s ease, border-color .16s ease;
}

.helios-recovery-toggle:hover{
    transform:translateY(-1px);
    background:rgba(255,101,104,.18);
    border-color:rgba(255,101,104,.38);
}

.helios-recovery-sidebar.is-collapsed .helios-recovery-brand{
    justify-content:center;
    flex-direction:column;
    gap:12px;
}

.helios-recovery-sidebar.is-collapsed .helios-recovery-brand div,
.helios-recovery-sidebar.is-collapsed .helios-recovery-selected,
.helios-recovery-sidebar.is-collapsed .helios-recovery-group p,
.helios-recovery-sidebar.is-collapsed .helios-recovery-link strong,
.helios-recovery-sidebar.is-collapsed .helios-recovery-link em{
    display:none;
}

.helios-recovery-sidebar.is-collapsed .helios-recovery-toggle{
    margin:0;
}

.helios-recovery-brand strong,
.helios-recovery-selected b{
    display:block;
    color:#fff;
    font-size:14px;
    line-height:1.12;
    font-weight:820;
    white-space:nowrap;
}

.helios-recovery-brand em,
.helios-recovery-selected small,
.helios-recovery-group p,
.helios-recovery-link em{
    display:block;
    color:#8f8580;
    font-size:10px;
    font-style:normal;
    font-weight:780;
    text-transform:uppercase;
    letter-spacing:0 !important;
}

.helios-recovery-selected{
    margin:0 0 14px;
    padding:13px;
    border-radius:14px;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.10);
}

.helios-recovery-selected b{
    margin-top:6px;
    overflow:hidden;
    text-overflow:ellipsis;
}

.helios-recovery-group{
    margin:14px 0 0;
}

.helios-recovery-group p{
    margin:0 0 7px;
    color:#b9afaa !important;
}

.helios-recovery-link{
    min-height:42px;
    display:grid;
    grid-template-columns:34px minmax(0,1fr) auto;
    align-items:center;
    gap:8px;
    margin:5px 0;
    padding:0 10px;
    border-radius:12px;
    color:#aaa09c !important;
    text-decoration:none !important;
    background:rgba(255,255,255,.025);
    border:1px solid transparent;
    transition:background .16s ease,border-color .16s ease,transform .16s ease;
}

.helios-recovery-sidebar.is-collapsed .helios-recovery-link{
    width:50px;
    min-height:50px;
    display:grid;
    grid-template-columns:1fr;
    place-items:center;
    margin:8px 0;
    padding:0;
    border-radius:15px;
}

.helios-recovery-sidebar.is-collapsed .helios-recovery-link > span{
    width:36px;
    height:36px;
}

.helios-recovery-link:hover{
    transform:translateY(-1px);
    color:#fff !important;
    background:rgba(255,255,255,.06);
    border-color:rgba(255,255,255,.12);
}

.helios-recovery-link > span{
    width:30px;
    height:30px;
    display:grid;
    place-items:center;
    border-radius:10px;
    color:#fff;
    background:rgba(255,255,255,.055);
}

.helios-recovery-link strong{
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:inherit;
    font-size:12px;
    font-weight:780;
}

.helios-recovery-link.active{
    color:#fff !important;
    background:
        linear-gradient(90deg,rgba(255,101,104,.24),rgba(102,21,24,.13)),
        rgba(255,255,255,.06);
    border-color:rgba(255,101,104,.42);
    box-shadow:inset 3px 0 0 #ff6568;
}

h1,h2,h3,p{margin-top:0}
h1,h2,h3{color:var(--text) !important;font-weight:760 !important}
p{color:var(--muted) !important;line-height:1.55}

/* Sidebar */
section[data-testid="stSidebar"]{
    display:none !important;
    visibility:hidden !important;
    pointer-events:none !important;
    width:0 !important;
    min-width:0 !important;
    max-width:0 !important;
    background:
        linear-gradient(90deg,rgba(255,101,104,.18),transparent 28%,transparent 72%,rgba(255,255,255,.035)),
        radial-gradient(circle at 22% 0%,rgba(102,21,24,.26),transparent 34%),
        radial-gradient(circle at 44% 9%,rgba(163,0,55,.16),transparent 22%),
        linear-gradient(180deg,rgba(16,11,11,.98),rgba(7,5,5,.99)) !important;
    border-right:1px solid rgba(255,255,255,.11) !important;
    box-shadow:12px 0 44px rgba(0,0,0,.34) !important;
    transition:
        width .24s cubic-bezier(.2,.8,.2,1),
        min-width .24s cubic-bezier(.2,.8,.2,1),
        max-width .24s cubic-bezier(.2,.8,.2,1) !important;
}

section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{
    display:none !important;
    visibility:hidden !important;
    pointer-events:none !important;
    width:0 !important;
    min-width:0 !important;
    max-width:0 !important;
    padding:14px 12px 22px !important;
    transition:
        width .24s cubic-bezier(.2,.8,.2,1),
        min-width .24s cubic-bezier(.2,.8,.2,1),
        max-width .24s cubic-bezier(.2,.8,.2,1) !important;
}

div[data-testid="stSidebarHeader"],
div[data-testid="stSidebarHeader"] *,
section[data-testid="stSidebar"] header,
section[data-testid="stSidebar"] header *,
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] button[aria-label*="collapse" i],
section[data-testid="stSidebar"] button[aria-label*="expand" i]{
    display:none !important;
    visibility:hidden !important;
    pointer-events:none !important;
    width:0 !important;
    height:0 !important;
    min-height:0 !important;
    overflow:hidden !important;
}

.helios-sidebar-shell{
    width:100%;
}

.helios-sidebar-top{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    margin:2px 0 10px;
}

.helios-sidebar-wordmark{
    min-width:0;
    display:flex;
    align-items:center;
    gap:11px;
}

.helios-sidebar-wordmark > span{
    width:38px;
    height:38px;
    flex:0 0 38px;
    display:grid;
    place-items:center;
    border-radius:12px;
    color:#fff;
    font-size:16px;
    font-weight:860;
    background:
        radial-gradient(circle at 32% 22%,rgba(255,255,255,.36),transparent 30%),
        linear-gradient(135deg,var(--primary),var(--accent) 54%,var(--rose));
    border:1px solid rgba(255,255,255,.17);
    box-shadow:0 12px 26px rgba(102,21,24,.30);
    animation:heliosLogoFloat 4.2s ease-in-out infinite;
    will-change:transform,box-shadow;
}

.helios-sidebar-wordmark strong{
    display:block;
    color:#fff;
    font-size:14px;
    line-height:1.1;
    font-weight:820;
    white-space:nowrap;
}

.helios-sidebar-wordmark em{
    display:block;
    margin-top:3px;
    color:#8f8580;
    font-size:10px;
    font-style:normal;
    font-weight:780;
    text-transform:uppercase;
    white-space:nowrap;
}

.helios-sidebar-collapsed .helios-sidebar-wordmark{
    justify-content:center;
}

.helios-sidebar-collapsed .helios-sidebar-top{
    justify-content:center;
    margin-bottom:14px;
}

.helios-sidebar-collapsed .helios-sidebar-wordmark div{
    display:none;
}

.helios-sidebar-collapsed{
    position:relative;
}

.helios-sidebar-collapsed:before{
    content:"";
    position:absolute;
    top:72px;
    bottom:-720px;
    left:50%;
    width:1px;
    transform:translateX(-50%);
    background:
        linear-gradient(
            180deg,
            transparent,
            rgba(255,101,104,.26) 8%,
            rgba(255,255,255,.12) 38%,
            rgba(163,0,55,.24) 72%,
            transparent
        );
    box-shadow:0 0 22px rgba(255,101,104,.22);
    pointer-events:none;
}

@keyframes heliosLogoFloat{
    0%,
    100%{
        transform:translateY(0);
        box-shadow:0 12px 26px rgba(102,21,24,.30);
    }

    50%{
        transform:translateY(-6px);
        box-shadow:0 20px 34px rgba(163,0,55,.36);
    }
}

@keyframes heliosCompactPulse{
    0%,
    100%{
        opacity:.62;
        transform:scale(.96);
    }

    50%{
        opacity:1;
        transform:scale(1.05);
    }
}

.helios-rail-divider{
    height:1px;
    margin:12px auto 14px;
    width:72%;
    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,101,104,.46),
            rgba(255,255,255,.20),
            transparent
        );
    box-shadow:0 0 18px rgba(255,101,104,.24);
}

.helios-compact-nav-selected{
    position:relative;
    width:46px;
    height:46px;
    margin:8px auto;
    display:grid;
    place-items:center;
    border-radius:15px;
    color:#fff;
    background:
        radial-gradient(circle at 28% 22%,rgba(255,255,255,.28),transparent 32%),
        linear-gradient(135deg,rgba(255,101,104,.92),rgba(163,0,55,.72) 58%,rgba(84,162,255,.38));
    border:1px solid rgba(255,255,255,.28);
    box-shadow:
        0 0 0 1px rgba(255,101,104,.16),
        0 0 26px rgba(255,101,104,.40),
        0 18px 36px rgba(0,0,0,.34);
    isolation:isolate;
}

.helios-compact-nav-selected:before{
    content:"";
    position:absolute;
    inset:-6px;
    z-index:-1;
    border-radius:19px;
    border:1px solid rgba(255,101,104,.24);
    background:rgba(255,101,104,.08);
    animation:heliosCompactPulse 2.8s ease-in-out infinite;
}

.helios-compact-nav-selected:after{
    content:"";
    position:absolute;
    top:50%;
    right:-13px;
    width:5px;
    height:22px;
    transform:translateY(-50%);
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 16px rgba(255,101,104,.72);
}

.helios-compact-nav-selected span{
    font-size:17px;
    line-height:1;
    font-weight:900;
    text-shadow:0 0 16px rgba(255,255,255,.42);
}

.helios-module-rail{
    margin:14px 0 10px;
    padding:0;
    background:transparent;
    border:0;
}

.helios-module-rail-head{display:block}
.helios-module-rail-head span{display:none}

.helios-module-rail-head strong,
.helios-nav-group-label span{
    color:#8d8582;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-nav-group-label{
    min-height:22px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin:18px 0 7px;
}

.helios-nav-group-label em{
    min-width:23px;
    min-height:21px;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    border-radius:999px;
    color:#d8d0cc;
    background:rgba(255,255,255,.055);
    border:1px solid rgba(255,255,255,.10);
    font-size:10px;
    font-style:normal;
    font-weight:850;
}

.helios-inline-nav-selected{
    min-height:38px;
    display:flex;
    align-items:center;
    gap:9px;
    margin:4px 0;
    padding:0 10px;
    border-radius:10px;
    color:#fff;
    background:
        linear-gradient(90deg,rgba(102,21,24,.44),rgba(139,26,30,.20)),
        rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.13);
    box-shadow:inset 3px 0 0 #ff6568,0 10px 28px rgba(0,0,0,.18);
}

.helios-inline-nav-selected span{
    flex:0 0 24px;
    width:24px;
    height:24px;
    display:grid;
    place-items:center;
    border-radius:8px;
    color:#ff8a8d;
    background:rgba(255,255,255,.055);
    text-align:center;
    font-size:11px;
    font-weight:860;
}

.helios-inline-nav-selected strong{
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:#fff;
    font-size:12px;
    font-weight:780;
}

.helios-inline-nav-selected em{
    margin-left:auto;
    color:#ffd2d4;
    font-size:9px;
    font-style:normal;
    font-weight:850;
    text-transform:uppercase;
}

/* Controls */
.stButton button,
.stDownloadButton button,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stCheckbox"],
[data-testid="stToggle"]{
    min-height:40px !important;
    border-radius:12px !important;
    color:#ded8d5 !important;
    background:rgba(26,21,21,.72) !important;
    border:1px solid rgba(255,255,255,.10) !important;
    box-shadow:none !important;
    font-size:13px !important;
    font-weight:720 !important;
    transition:transform .18s cubic-bezier(.2,.8,.2,1),border-color .18s ease,background .18s ease,color .18s ease !important;
}

.stButton button:hover,
.stDownloadButton button:hover{
    transform:translateY(-1px) !important;
    color:#fff !important;
    background:rgba(102,21,24,.28) !important;
    border-color:rgba(255,101,104,.42) !important;
}

section[data-testid="stSidebar"] .stButton{
    margin:4px 0 !important;
}

section[data-testid="stSidebar"] .stButton button{
    min-height:38px !important;
    border-radius:10px !important;
    background:transparent !important;
    border-color:transparent !important;
    color:#aaa09c !important;
    font-size:12px !important;
    font-weight:760 !important;
    overflow:hidden !important;
    white-space:nowrap !important;
}

.helios-sidebar-collapsed + div,
section[data-testid="stSidebar"] .helios-sidebar-collapsed ~ div{
    min-width:0 !important;
}

section[data-testid="stSidebar"] .helios-sidebar-collapsed ~ .stButton button,
section[data-testid="stSidebar"] .helios-sidebar-collapsed ~ div .stButton button{
    position:relative !important;
    width:44px !important;
    min-width:44px !important;
    height:44px !important;
    min-height:44px !important;
    margin:8px auto !important;
    padding:0 !important;
    display:grid !important;
    place-items:center !important;
    border-radius:15px !important;
    color:#f1e8e5 !important;
    background:
        radial-gradient(circle at 28% 20%,rgba(255,255,255,.15),transparent 30%),
        linear-gradient(135deg,rgba(255,255,255,.08),rgba(102,21,24,.16)) !important;
    border:1px solid rgba(255,255,255,.12) !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.10),
        0 12px 24px rgba(0,0,0,.20) !important;
    font-size:15px !important;
    line-height:1 !important;
    font-weight:760 !important;
}

section[data-testid="stSidebar"] .helios-sidebar-collapsed ~ div .stButton button:hover{
    color:#fff !important;
    background:
        radial-gradient(circle at 30% 20%,rgba(255,255,255,.24),transparent 32%),
        linear-gradient(135deg,rgba(255,101,104,.44),rgba(163,0,55,.26)) !important;
    border-color:rgba(255,101,104,.54) !important;
    box-shadow:
        0 0 0 1px rgba(255,101,104,.14),
        0 0 24px rgba(255,101,104,.28),
        0 16px 32px rgba(0,0,0,.26) !important;
    transform:translateY(-1px) scale(1.04) !important;
}

section[data-testid="stSidebar"] .stButton button:hover{
    transform:none !important;
    color:#fff !important;
    background:rgba(255,255,255,.055) !important;
    border-color:rgba(255,255,255,.10) !important;
}

.stTextInput input,
.stTextArea textarea{
    min-height:42px !important;
    border-radius:12px !important;
    color:#fff !important;
    background:rgba(10,7,7,.72) !important;
    border:1px solid rgba(255,255,255,.10) !important;
    box-shadow:none !important;
    font-size:13px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder{
    color:#827977 !important;
}

/* Surfaces */
.helios-motion-card{
    animation:helios-rise .36s cubic-bezier(.2,.8,.2,1) both;
}

.helios-system-bar,
.helios-platform-chrome,
.helios-agent-presence,
.helios-platform-palette,
.helios-command-bridge,
.helios-command-card,
.helios-command-page,
.helios-mission-stack,
.helios-status-strip,
.helios-execution-lanes,
.helios-agent-matrix,
.helios-system-notice,
.helios-system-snapshot,
.helios-agent-status,
.helios-source-library,
.helios-source-intel,
.helios-live-hero,
.helios-live-panel,
.helios-live-backend-note,
.helios-command-palette,
.helios-upload-shell,
.helios-terminal,
.helios-empty-state,
.helios-user-message,
.helios-assistant-message,
.ai-response-card,
.helios-reactor-head,
.helios-reactor-shell,
.helios-thinking-card,
.helios-feature-card,
.helios-voice-cockpit,
.helios-tab-panel,
.helios-action-notice{
    border-radius:var(--radius) !important;
    color:#fff;
    background:
        linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.018)),
        rgba(26,21,21,.86) !important;
    border:1px solid rgba(255,255,255,.11) !important;
    box-shadow:var(--shadow) !important;
    overflow:hidden;
}

.helios-command-bridge{
    position:relative;
    min-height:146px;
    display:grid;
    grid-template-columns:minmax(360px,1fr) minmax(260px,360px);
    align-items:end;
    justify-content:space-between;
    gap:34px;
    margin:0 0 14px;
    padding:26px 28px 24px;
    border:0 !important;
    border-radius:0 !important;
    background:
        radial-gradient(circle at 8% 50%,rgba(255,101,104,.16),transparent 28%),
        radial-gradient(circle at 86% 46%,rgba(255,101,104,.12),transparent 30%),
        linear-gradient(90deg,rgba(255,101,104,.18),transparent 28%,transparent 72%,rgba(255,101,104,.12)),
        transparent !important;
    box-shadow:none !important;
    overflow:visible;
}

.helios-command-bridge:before{
    content:"";
    position:absolute;
    inset:8px 0;
    opacity:.58;
    pointer-events:none;
    border-top:1px solid rgba(255,101,104,.16);
    border-bottom:1px solid rgba(255,101,104,.10);
    background:
        linear-gradient(90deg,rgba(255,101,104,.24),transparent 18%,transparent 82%,rgba(255,101,104,.16)) top left/100% 1px no-repeat,
        linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent) 0 50%/100% 1px no-repeat;
    mask-image:linear-gradient(90deg,#000 0%,#000 84%,transparent 100%);
}

.helios-command-bridge:after{
    content:"";
    position:absolute;
    left:0;
    top:50%;
    width:4px;
    height:78%;
    transform:translateY(-50%);
    border-radius:999px;
    background:linear-gradient(transparent,#ff6568,transparent);
    box-shadow:0 0 24px rgba(255,101,104,.58);
}

.helios-command-bridge > *{
    position:relative;
    z-index:1;
}

.helios-bridge-copy span,
.helios-platform-main span,
.helios-platform-signals span,
.helios-presence-head span,
.helios-presence-grid span,
.helios-palette-copy span,
.helios-platform-jump span,
.helios-command-status,
.helios-system-label,
.helios-reactor-head span,
.helios-reactor-label,
.helios-status-strip span,
.helios-command-metrics span,
.helios-stat-card span,
.helios-mission-head span,
.helios-execution-head span,
.helios-agent-head span,
.helios-source-library-head span,
.helios-lane-grid span,
.helios-agent-grid span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-bridge-copy h1{
    margin:10px 0 10px !important;
    color:#fff !important;
    font-size:clamp(36px,4vw,64px) !important;
    line-height:.9 !important;
    font-weight:880 !important;
    text-shadow:0 0 34px rgba(255,255,255,.08);
    word-break:normal !important;
    overflow-wrap:normal !important;
    white-space:normal !important;
}

.helios-bridge-copy p{
    max-width:760px;
    margin:0 !important;
    color:#d0c8c4 !important;
    font-size:clamp(16px,1.45vw,24px) !important;
    line-height:1.34 !important;
    word-break:normal !important;
    overflow-wrap:normal !important;
}

.helios-bridge-status{
    position:relative;
    min-height:72px;
    display:flex;
    flex-wrap:wrap;
    align-items:center;
    justify-content:flex-end;
    gap:10px 12px;
    max-width:360px;
    margin-left:auto;
    padding:4px 0;
}

.helios-bridge-status:before{
    display:none;
}

.helios-bridge-status span,
.helios-system-right span,
.helios-model-pill,
.helios-mission-badges span,
.helios-reactor-pills span,
.helios-thinking-top em,
.helios-source-chip em,
.helios-source-library-head span,
.helios-execution-head em,
.ai-card-header em,
.helios-feature-status,
.helios-agent-grid em{
    position:relative;
    min-height:34px;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    gap:7px;
    padding:0 13px;
    border-radius:999px;
    color:#f7eeee;
    background:
        linear-gradient(135deg,rgba(255,255,255,.115),rgba(255,255,255,.035)),
        rgba(15,10,12,.54);
    border:1px solid rgba(255,255,255,.14);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.12),
        0 12px 28px rgba(0,0,0,.22);
    font-size:11px;
    font-style:normal;
    font-weight:820;
    line-height:1;
    white-space:nowrap;
    overflow:hidden;
    isolation:isolate;
    backdrop-filter:blur(18px) saturate(1.22);
}

.helios-bridge-status span{
    min-width:auto;
    min-height:32px;
    display:inline-flex;
    gap:7px;
    padding:0 12px;
    border:1px solid rgba(255,255,255,.13);
    border-radius:999px;
    background:rgba(15,10,12,.56);
    box-shadow:0 10px 22px rgba(0,0,0,.18);
    color:#fff;
    font-size:12px;
    font-weight:860;
    text-align:center;
    overflow:hidden;
    backdrop-filter:blur(14px);
}

.helios-bridge-status span:before,
.helios-system-right span:before,
.helios-model-pill:before,
.helios-mission-badges span:before,
.helios-reactor-pills span:before,
.helios-thinking-top em:before,
.helios-source-chip em:before,
.helios-source-library-head span:before,
.helios-execution-head em:before,
.ai-card-header em:before,
.helios-feature-status:before,
.helios-agent-grid em:before{
    content:"";
    width:6px;
    height:6px;
    flex:0 0 auto;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 14px rgba(255,101,104,.88);
}

.helios-bridge-status span:before{
    width:7px;
    height:7px;
    margin:0;
    background:#ff5c7a;
    box-shadow:
        0 0 0 8px rgba(255,92,122,.10),
        0 0 24px rgba(255,92,122,.88);
}

.helios-reactor-pills span{
    min-width:104px;
    min-height:44px;
    display:grid;
    grid-template-columns:8px minmax(0,1fr);
    grid-template-rows:auto auto;
    column-gap:9px;
    align-content:center;
    justify-content:stretch;
    padding:7px 13px;
    text-align:left;
    border-radius:16px;
}

.helios-reactor-pills span:before{
    grid-row:1 / span 2;
    align-self:center;
    width:7px;
    height:22px;
    border-radius:999px;
    background:linear-gradient(#ff8588,#ff355f);
}

.helios-reactor-pills small{
    min-width:0;
    color:#b8abaa;
    font-size:9px;
    font-weight:900;
    line-height:1.05;
    text-transform:uppercase;
}

.helios-reactor-pills b{
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    color:#fff7f7;
    font-size:13px;
    font-weight:860;
    line-height:1.16;
    text-transform:none;
}

.helios-bridge-status .is-live{
    color:#fff;
}

.helios-bridge-status .is-live:before{
    animation:helios-node-pulse 1.8s ease-in-out infinite;
}

.helios-status-strip{
    display:grid;
    grid-template-columns:repeat(7,minmax(0,1fr));
    gap:8px;
    margin:0 0 10px;
    padding:8px;
    background:rgba(10,7,7,.42) !important;
    box-shadow:none !important;
}

/* Global platform layer */
.helios-platform-chrome{
    position:relative;
    min-height:178px;
    display:grid;
    grid-template-columns:minmax(0,1fr) 180px minmax(420px,.82fr);
    align-items:center;
    gap:20px;
    margin:10px 0 12px;
    padding:18px;
    background:
        radial-gradient(circle at 10% 0%,rgba(84,162,255,.14),transparent 32%),
        radial-gradient(circle at 92% 16%,rgba(255,101,104,.16),transparent 28%),
        linear-gradient(135deg,rgba(255,255,255,.052),rgba(255,255,255,.018)),
        rgba(18,14,14,.88) !important;
    isolation:isolate;
}

.helios-platform-chrome:before{
    content:"";
    position:absolute;
    inset:0;
    z-index:-1;
    opacity:.62;
    background:
        linear-gradient(90deg,rgba(255,101,104,.18),transparent 26%,transparent 72%,rgba(84,162,255,.12)),
        linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px);
    background-size:auto,30px 30px,30px 30px;
}

.helios-platform-main h2{
    margin:7px 0 8px !important;
    color:#fff !important;
    font-size:clamp(28px,3vw,44px) !important;
    line-height:1 !important;
    font-weight:880 !important;
}

.helios-platform-main p{
    max-width:780px;
    margin:0 !important;
    color:#cfc7c3 !important;
    font-size:14px !important;
}

.helios-platform-orbit{
    position:relative;
    width:148px;
    height:148px;
    margin:auto;
    border-radius:999px;
    background:
        radial-gradient(circle at center,rgba(255,255,255,.08),transparent 34%),
        conic-gradient(from 90deg,rgba(255,101,104,.86),rgba(84,162,255,.62),rgba(131,226,161,.42),rgba(255,101,104,.86));
    border:1px solid rgba(255,255,255,.14);
    box-shadow:0 0 38px rgba(255,101,104,.18);
    animation:helios-orbit 12s linear infinite;
}

.helios-platform-orbit:before{
    content:"";
    position:absolute;
    inset:19px;
    border-radius:999px;
    background:#0a0707;
    border:1px solid rgba(255,255,255,.13);
}

.helios-platform-orbit span,
.helios-platform-orbit i,
.helios-platform-orbit b{
    position:absolute;
    width:9px;
    height:9px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 18px rgba(255,101,104,.78);
}

.helios-platform-orbit span{left:18px;top:50%}
.helios-platform-orbit i{right:24px;top:28px;background:#54a2ff;box-shadow:0 0 18px rgba(84,162,255,.70)}
.helios-platform-orbit b{right:34px;bottom:25px;background:#83e2a1;box-shadow:0 0 18px rgba(131,226,161,.62)}

.helios-platform-signals{
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:9px;
}

.helios-platform-signals div{
    min-height:66px;
    padding:11px;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-platform-signals strong{
    display:block;
    margin-top:6px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:#fff;
    font-size:15px;
    line-height:1.1;
}

.helios-agent-presence{
    display:grid;
    grid-template-columns:minmax(220px,.32fr) minmax(0,1fr);
    gap:12px;
    align-items:center;
    margin:0 0 10px;
    padding:12px;
    background:rgba(10,7,7,.40) !important;
    box-shadow:none !important;
}

.helios-presence-head strong{
    display:block;
    margin-top:5px;
    color:#fff;
    font-size:15px;
}

.helios-presence-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:8px;
}

.helios-presence-grid article{
    position:relative;
    min-height:64px;
    padding:11px;
    border-radius:12px;
    background:rgba(255,255,255,.036);
    border:1px solid rgba(255,255,255,.08);
}

.helios-presence-grid article.active{
    border-color:rgba(255,101,104,.38);
    background:rgba(255,101,104,.09);
}

.helios-presence-grid article.active:after{
    content:"";
    position:absolute;
    top:11px;
    right:11px;
    width:7px;
    height:7px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 16px rgba(255,101,104,.80);
}

.helios-presence-grid strong{
    display:block;
    margin-top:5px;
    color:#fff;
    font-size:14px;
}

.helios-presence-grid em{
    display:block;
    margin-top:5px;
    color:#8f8580;
    font-size:10px;
    font-style:normal;
    font-weight:800;
    text-transform:uppercase;
}

.helios-platform-palette{
    margin:10px 0;
    padding:14px;
    background:
        radial-gradient(circle at 0% 0%,rgba(84,162,255,.12),transparent 30%),
        rgba(18,14,14,.90) !important;
}

.helios-palette-copy strong{
    display:block;
    margin-top:5px;
    color:#fff;
    font-size:16px;
}

.helios-platform-jump{
    min-height:142px;
    margin:8px 0;
    padding:13px;
    border-radius:13px;
    color:#fff;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-platform-jump.active{
    border-color:rgba(255,101,104,.38);
    background:rgba(255,101,104,.08);
}

.helios-platform-jump strong{
    display:block;
    margin-top:7px;
    color:#fff;
    font-size:15px;
}

.helios-platform-jump p{
    margin:8px 0 0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
    line-height:1.5 !important;
}

.helios-platform-empty{
    margin:8px 0;
    padding:12px;
    border-radius:13px;
    color:#aaa09c;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-status-strip div,
.helios-command-metrics div,
.helios-stat-card,
.helios-mission-grid article,
.helios-lane-grid article,
.helios-agent-grid article,
.ai-response-grid section,
.ai-response-grid aside{
    min-height:58px;
    padding:10px;
    border-radius:12px;
    background:rgba(255,255,255,.032);
    border:1px solid rgba(255,255,255,.085);
}

.helios-status-strip strong,
.helios-command-metrics strong,
.helios-stat-card strong{
    display:block;
    margin-top:6px;
    color:#fff;
    font-size:15px;
    line-height:1.08;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.helios-stat-card p{
    margin:7px 0 0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
    line-height:1.4 !important;
}

.helios-chart-title{
    margin:8px 0 8px;
    padding:10px 12px;
    border-radius:12px;
    color:#e8e3e0;
    background:rgba(10,7,7,.44);
    border:1px solid rgba(255,255,255,.08);
    font-size:13px;
    font-weight:820;
}

.helios-feed-row{
    min-height:52px;
    display:flex;
    align-items:center;
    gap:10px;
    margin:8px 0;
    padding:12px 14px;
    border-radius:12px !important;
    background:rgba(255,255,255,.035) !important;
    border:1px solid rgba(255,255,255,.08) !important;
    box-shadow:none !important;
}

.helios-feed-row strong{
    min-width:0;
    color:#e8e3e0;
    font-size:13px;
    line-height:1.3;
}

.helios-command-card{
    position:relative;
    display:grid;
    grid-template-columns:52px minmax(0,1fr) auto;
    gap:14px;
    align-items:center;
    margin:10px 0;
    padding:18px;
    background:
        linear-gradient(135deg,rgba(102,21,24,.18),rgba(26,21,21,.92)),
        rgba(26,21,21,.9) !important;
}

.helios-command-card:before{
    content:"";
    position:absolute;
    inset:0 auto 0 0;
    width:4px;
    background:linear-gradient(var(--primary),#ff6568,var(--rose));
}

.helios-command-icon,
.helios-feature-icon,
.helios-upload-icon{
    width:50px;
    height:50px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:15px;
    color:#ffd6d8;
    background:rgba(102,21,24,.34);
    border:1px solid rgba(255,101,104,.30);
}

.helios-command-icon svg,
.helios-feature-icon svg{
    width:24px;
    height:24px;
}

.helios-command-icon svg *,
.helios-feature-icon svg *,
.helios-command-actions svg *{
    fill:none;
    stroke:currentColor;
    stroke-width:2.2;
    stroke-linecap:round;
    stroke-linejoin:round;
}

.helios-command-icon svg [fill="currentColor"],
.helios-feature-icon svg [fill="currentColor"]{
    fill:currentColor !important;
    stroke:none !important;
}

.helios-command-card h2{
    margin:4px 0 5px !important;
    font-size:30px !important;
    line-height:1.02 !important;
    font-weight:820 !important;
}

.helios-command-card p{
    max-width:820px;
    margin:0 !important;
    color:#c8bfbb !important;
    font-size:14px !important;
}

.helios-command-card-aside{
    display:flex;
    flex-direction:column;
    align-items:flex-end;
    gap:5px;
}

.helios-command-card-aside span{
    color:#9a8f8b;
    font-size:11px;
    font-weight:780;
}

.helios-command-card-aside strong{
    color:#ffd6d8;
    font-size:20px;
}

.helios-system-bar{display:none !important}

.helios-command-page,
.helios-mission-stack,
.helios-execution-lanes,
.helios-agent-matrix,
.helios-source-library,
.helios-source-intel{
    margin:10px 0;
    padding:14px;
}

.helios-command-metrics,
.helios-mission-grid,
.helios-lane-grid,
.helios-agent-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-mission-grid{
    grid-template-columns:repeat(3,minmax(0,1fr));
}

.helios-mission-head,
.helios-execution-head,
.helios-agent-head,
.helios-source-library-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:14px;
}

.helios-mission-head strong,
.helios-execution-head strong,
.helios-agent-head strong,
.helios-source-library-head strong,
.helios-lane-grid strong,
.helios-agent-grid strong{
    display:block;
    color:#e8e3e0;
    font-size:13px;
    line-height:1.4;
}

.helios-mission-head strong,
.helios-execution-head strong,
.helios-agent-head strong{
    color:#fff;
    font-size:17px;
}

.helios-lane-grid article.active,
.helios-agent-grid article.active{
    border-color:rgba(255,101,104,.34);
    background:rgba(102,21,24,.16);
    box-shadow:inset 3px 0 0 #ff6568;
}

.helios-source-intel{
    margin:12px 0 18px;
    padding:16px;
}

.helios-source-intel-head{
    display:grid;
    grid-template-columns:minmax(0,220px) minmax(0,1fr);
    align-items:center;
    gap:16px;
    margin-bottom:14px;
}

.helios-source-intel-head span,
.helios-source-intel-grid span,
.helios-source-intel-title span,
.helios-source-intel-row small{
    color:#9a8f8b;
    font-size:11px;
    font-weight:780;
}

.helios-source-intel-head strong{
    display:block;
    margin-top:4px;
    color:#fff;
    font-size:28px;
    line-height:1;
}

.helios-source-intel-meter{
    height:10px;
    border-radius:999px;
    overflow:hidden;
    background:rgba(10,7,7,.52);
    border:1px solid rgba(255,255,255,.08);
}

.helios-source-intel-meter i{
    display:block;
    height:100%;
    border-radius:inherit;
    background:linear-gradient(90deg,#ff6568,#54a2ff,#83e2a1);
    box-shadow:0 0 22px rgba(255,101,104,.22);
}

.helios-source-intel-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
    margin-bottom:14px;
}

.helios-source-intel-grid article{
    min-width:0;
    padding:13px;
    border-radius:13px;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.08);
}

.helios-source-intel-grid strong{
    display:block;
    margin-top:6px;
    color:#fff;
    font-size:20px;
}

.helios-source-intel-split{
    display:grid;
    grid-template-columns:minmax(0,1fr) minmax(220px,.34fr);
    gap:12px;
}

.helios-source-intel-list,
.helios-source-intel-aside{
    min-width:0;
    padding:13px;
    border-radius:14px;
    background:rgba(10,7,7,.36);
    border:1px solid rgba(255,255,255,.08);
}

.helios-source-intel-title{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    margin-bottom:10px;
}

.helios-source-intel-title strong,
.helios-source-intel-aside strong,
.helios-source-intel-empty strong{
    color:#fff;
    font-size:14px;
}

.helios-source-intel-row{
    display:grid;
    grid-template-columns:48px minmax(0,1fr) auto;
    align-items:center;
    gap:10px;
    min-height:48px;
    padding:9px 0;
    border-top:1px solid rgba(255,255,255,.07);
}

.helios-source-intel-row > span{
    display:grid;
    place-items:center;
    width:38px;
    height:30px;
    border-radius:10px;
    color:#ffd2d4;
    background:rgba(255,101,104,.10);
    border:1px solid rgba(255,101,104,.20);
    font-size:10px;
    font-weight:860;
}

.helios-source-intel-row strong,
.helios-source-intel-row small{
    display:block;
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.helios-source-intel-row strong{
    color:#e8e3e0;
    font-size:13px;
}

.helios-source-intel-row em{
    padding:5px 8px;
    border-radius:999px;
    color:#d8fff0;
    background:rgba(131,226,161,.08);
    border:1px solid rgba(131,226,161,.22);
    font-size:10px;
    font-style:normal;
    font-weight:820;
    white-space:nowrap;
}

.helios-source-intel-aside{
    display:grid;
    gap:12px;
    align-content:start;
}

.helios-source-intel-aside div{
    display:grid;
    gap:7px;
}

.helios-source-intel-aside span{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    min-height:32px;
    padding:0 10px;
    border-radius:10px;
    color:#cfc6c2;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.07);
    font-size:11px;
    font-weight:760;
}

.helios-source-intel-aside b{
    color:#ffd2d4;
}

.helios-source-intel-empty{
    padding:16px;
    border-radius:13px;
    background:rgba(255,255,255,.032);
    border:1px solid rgba(255,255,255,.08);
}

.helios-source-intel-empty p{
    margin:7px 0 0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
}

/* Reactor */
.helios-reactor-head{
    width:100%;
    max-width:100%;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin:12px 0 8px;
    padding:12px 14px;
}

.helios-reactor-head strong{
    display:block;
    margin-top:3px;
    color:#fff;
    font-size:16px;
}

.helios-reactor-head em{
    color:#aaa09c;
    font-size:12px;
    font-style:normal;
    font-weight:720;
}

[data-testid="stSegmentedControl"] [role="radiogroup"],
div[role="radiogroup"]{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin:8px 0 12px;
}

[data-testid="stSegmentedControl"] label,
[data-testid="stSegmentedControl"] button,
div[role="radiogroup"] label{
    min-height:40px !important;
    padding:0 14px !important;
    border-radius:12px !important;
    color:#aaa09c !important;
    background:rgba(26,21,21,.68) !important;
    border:1px solid rgba(255,255,255,.10) !important;
    font-size:13px !important;
    font-weight:760 !important;
}

[data-testid="stSegmentedControl"] label:has(input:checked),
[data-testid="stSegmentedControl"] button[aria-pressed="true"],
div[role="radiogroup"] label:has(input:checked){
    color:#fff !important;
    background:rgba(102,21,24,.34) !important;
    border-color:rgba(255,101,104,.45) !important;
    box-shadow:0 0 0 3px rgba(102,21,24,.18) !important;
}

.helios-reactor-shell{
    width:100%;
    max-width:100%;
    min-width:0;
    min-height:230px;
    display:grid;
    grid-template-columns:72px minmax(0,1fr) minmax(420px,.92fr);
    align-items:center;
    gap:22px;
    margin:8px 0 12px;
    padding:28px;
    background:
        radial-gradient(circle at 72% 48%,rgba(255,101,104,.13),transparent 28%),
        linear-gradient(135deg,rgba(102,21,24,.22),rgba(26,21,21,.82) 58%,rgba(139,26,30,.11)),
        rgba(26,21,21,.88) !important;
}

.helios-reactor-orb,
.helios-thinking-orb,
.helios-voice-orb{
    position:relative;
    width:54px;
    height:54px;
    display:grid;
    place-items:center;
    border-radius:999px;
    background:
        conic-gradient(from 120deg,var(--primary),#ff6568,var(--rose),var(--primary));
    border:1px solid rgba(255,255,255,.18);
    animation:helios-orbit 6s linear infinite;
}

.helios-reactor-orb span,
.helios-thinking-orb span,
.helios-voice-orb span{
    width:25px;
    height:25px;
    display:block;
    border-radius:999px;
    background:#0a0707;
    border:1px solid rgba(255,255,255,.18);
}

.helios-reactor-orb i{
    position:absolute;
    width:8px;
    height:8px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 18px #ff6568;
}

.helios-reactor-main strong{
    display:block;
    margin:4px 0 5px;
    color:#fff;
    font-size:24px;
    line-height:1.06;
}

.helios-reactor-main p{
    margin:0 !important;
    color:#c8bfbb !important;
    font-size:13px !important;
}

.helios-mode-contract{
    margin:8px 0 12px;
    padding:14px;
}

.helios-mode-contract-head{
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:12px;
    margin-bottom:12px;
}

.helios-mode-contract-head span,
.helios-mode-contract-grid span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mode-contract-head strong{
    color:#fff;
    font-size:17px;
    line-height:1.2;
}

.helios-mode-contract-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-mode-contract-grid article{
    min-width:0;
    min-height:104px;
    padding:12px;
    border-radius:13px;
    background:rgba(10,7,7,.36);
    border:1px solid rgba(255,255,255,.08);
}

.helios-mode-contract-grid p{
    margin:8px 0 0 !important;
    color:#d8d1ce !important;
    font-size:12px !important;
    line-height:1.46 !important;
}

.helios-thinking-card{
    min-height:126px;
    display:grid;
    grid-template-columns:58px minmax(0,1fr);
    align-items:center;
    gap:18px;
    margin:12px 0 18px;
    padding:22px 26px !important;
    background:
        radial-gradient(circle at 18% 18%,rgba(255,101,104,.16),transparent 30%),
        linear-gradient(135deg,rgba(102,21,24,.18),rgba(26,21,21,.88) 64%),
        rgba(26,21,21,.90) !important;
}

.helios-thinking-orb{
    width:48px;
    height:48px;
    align-self:start;
    margin-top:2px;
}

.helios-thinking-orb span{
    width:22px;
    height:22px;
}

.helios-thinking-main{
    min-width:0;
    display:grid;
    gap:11px;
}

.helios-thinking-top{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
}

.helios-thinking-top strong{
    min-width:0;
    color:#fff;
    font-size:20px;
    font-weight:860;
    line-height:1.1;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.helios-thinking-top em{
    flex:0 0 auto;
    min-height:30px;
    padding:0 12px;
    font-size:12px;
    font-style:normal;
    font-weight:820;
}

.helios-thinking-main p{
    margin:0 !important;
    color:#c8bfbb !important;
    font-size:15px !important;
    line-height:1.45 !important;
}

.helios-processing-steps{
    justify-content:flex-start;
    gap:6px;
}

.helios-processing-steps span{
    min-height:28px;
    display:inline-flex;
    align-items:center;
    padding:0 10px;
    border-radius:999px;
    color:#a89f9c;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.08);
    font-size:11px;
    font-weight:820;
}

.helios-processing-steps span.active{
    color:#fff1f1;
    border-color:rgba(255,101,104,.34);
    background:rgba(255,101,104,.12);
}

.helios-thinking-bars{
    width:96px;
    height:24px;
    display:flex;
    align-items:center;
    gap:4px;
}

.helios-reactor-pills,
.helios-mission-badges,
.helios-processing-steps{
    display:flex;
    flex-wrap:wrap;
    justify-content:flex-end;
    gap:7px;
}

.helios-processing-steps{
    justify-content:flex-start;
    gap:6px;
}

.helios-reactor-pills{
    position:relative;
    max-width:620px;
    min-height:178px;
    display:grid;
    grid-template-columns:repeat(4,minmax(84px,1fr));
    grid-auto-rows:minmax(44px,auto);
    align-content:center;
    justify-content:end;
    gap:20px 28px;
    padding:8px 4px;
    isolation:isolate;
}

.helios-reactor-pills:before{
    content:"";
    position:absolute;
    inset:12px 20px;
    z-index:-1;
    opacity:.55;
    background:
        linear-gradient(90deg,transparent,rgba(255,101,104,.18),transparent) 0 33%/100% 1px no-repeat,
        linear-gradient(90deg,transparent,rgba(255,101,104,.12),transparent) 0 66%/100% 1px no-repeat,
        linear-gradient(180deg,transparent,rgba(255,255,255,.10),transparent) 24% 0/1px 100% no-repeat,
        linear-gradient(180deg,transparent,rgba(255,255,255,.08),transparent) 52% 0/1px 100% no-repeat,
        linear-gradient(180deg,transparent,rgba(255,255,255,.10),transparent) 78% 0/1px 100% no-repeat;
    mask-image:radial-gradient(ellipse at center,#000 38%,transparent 78%);
}

.helios-reactor-pills span{
    position:relative;
    min-width:0;
    min-height:0;
    display:grid;
    grid-template-columns:14px minmax(0,1fr);
    grid-template-rows:auto auto;
    align-content:center;
    column-gap:10px;
    padding:0;
    border:0;
    border-radius:0;
    background:transparent;
    box-shadow:none;
    text-align:left;
    backdrop-filter:none;
    overflow:visible;
}

.helios-reactor-pills span:nth-child(4n + 2){
    transform:translateY(-8px);
}

.helios-reactor-pills span:nth-child(4n + 3){
    transform:translateY(8px);
}

.helios-reactor-pills span:nth-child(8){
    grid-column:4;
}

.helios-reactor-pills span:before{
    content:"";
    grid-row:1 / span 2;
    align-self:center;
    width:10px;
    height:10px;
    border-radius:999px;
    background:#ff5c7a;
    box-shadow:
        0 0 0 7px rgba(255,92,122,.10),
        0 0 22px rgba(255,92,122,.78);
}

.helios-reactor-pills span:after{
    content:"";
    position:absolute;
    left:5px;
    top:50%;
    width:42px;
    height:1px;
    transform:translateY(-50%);
    background:linear-gradient(90deg,rgba(255,92,122,.70),transparent);
    pointer-events:none;
}

.helios-reactor-pills small{
    min-width:0;
    color:#a99e9c;
    font-size:9px;
    font-weight:900;
    line-height:1.05;
    text-transform:uppercase;
}

.helios-reactor-pills b{
    min-width:0;
    margin-top:4px;
    overflow:hidden;
    text-overflow:ellipsis;
    color:#fff;
    font-size:15px;
    font-weight:860;
    line-height:1.1;
    text-transform:none;
    text-shadow:0 0 18px rgba(255,255,255,.13);
}

/* Mission Control */
.helios-mission-control-hero,
.helios-mission-timeline,
.helios-mission-council,
.helios-mission-review,
.helios-mission-memory,
.helios-mission-templates,
.helios-agent-network,
.helios-mission-replay,
.helios-risk-radar,
.helios-next-actions,
.helios-mission-archive,
.helios-mission-artifact,
.helios-futuristic-deck,
.helios-mission-input-head{
    border-radius:var(--radius) !important;
    color:#fff;
    background:
        linear-gradient(135deg,rgba(84,162,255,.095),rgba(255,101,104,.10) 42%,rgba(26,21,21,.90)),
        rgba(18,14,14,.92) !important;
    border:1px solid rgba(255,255,255,.12) !important;
    box-shadow:var(--shadow) !important;
    overflow:hidden;
}

.helios-mission-control-hero{
    position:relative;
    min-height:268px;
    display:grid;
    grid-template-columns:minmax(0,1fr) 270px minmax(300px,.48fr);
    align-items:center;
    gap:24px;
    margin:0 0 12px;
    padding:26px;
    isolation:isolate;
}

.helios-mission-control-hero:before{
    content:"";
    position:absolute;
    inset:0;
    z-index:-1;
    background:
        linear-gradient(90deg,rgba(255,101,104,.20),transparent 28%,transparent 74%,rgba(84,162,255,.12)),
        linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);
    background-size:auto,28px 28px,28px 28px;
    mask-image:linear-gradient(90deg,#000 0%,#000 82%,transparent 100%);
}

.helios-mission-control-copy span,
.helios-mission-section-head span,
.helios-mission-step-grid span,
.helios-mission-council-grid span,
.helios-mission-artifact-grid span,
.helios-deck-card > span,
.helios-deck-memory-list span,
.helios-deck-pulse-grid span,
.helios-mission-input-head span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mission-control-copy h1{
    max-width:780px;
    margin:9px 0 12px !important;
    color:#fff !important;
    font-size:clamp(34px,4vw,58px) !important;
    line-height:.94 !important;
    font-weight:880 !important;
}

.helios-mission-control-copy p{
    max-width:820px;
    margin:0 !important;
    color:#d7cfcb !important;
    font-size:15px !important;
    line-height:1.56 !important;
}

.helios-mission-control-lattice{
    position:relative;
    min-height:194px;
    border-radius:18px;
    background:
        linear-gradient(90deg,transparent,rgba(255,101,104,.20),transparent) 0 28%/100% 1px no-repeat,
        linear-gradient(90deg,transparent,rgba(84,162,255,.16),transparent) 0 72%/100% 1px no-repeat,
        linear-gradient(180deg,transparent,rgba(255,255,255,.12),transparent) 34% 0/1px 100% no-repeat,
        linear-gradient(180deg,transparent,rgba(255,101,104,.14),transparent) 68% 0/1px 100% no-repeat,
        rgba(10,7,7,.34);
    border:1px solid rgba(255,255,255,.10);
}

.helios-mission-control-lattice span{
    position:absolute;
    width:10px;
    height:10px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:
        0 0 0 7px rgba(255,101,104,.08),
        0 0 22px rgba(255,101,104,.70);
}

.helios-mission-control-lattice span:nth-child(1){left:18%;top:28%}
.helios-mission-control-lattice span:nth-child(2){left:44%;top:68%;background:#54a2ff;box-shadow:0 0 0 7px rgba(84,162,255,.08),0 0 22px rgba(84,162,255,.62)}
.helios-mission-control-lattice span:nth-child(3){left:70%;top:32%;background:#83e2a1;box-shadow:0 0 0 7px rgba(131,226,161,.08),0 0 22px rgba(131,226,161,.54)}
.helios-mission-control-lattice span:nth-child(4){left:84%;top:74%}

.helios-mission-control-metrics{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:10px;
}

.helios-mission-control-metrics div,
.helios-mission-step-grid article,
.helios-mission-council-grid article,
.helios-mission-artifact-grid div{
    min-width:0;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-mission-control-metrics div{
    min-height:78px;
    padding:13px;
}

.helios-mission-control-metrics span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mission-control-metrics strong{
    display:block;
    margin-top:10px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:#fff;
    font-size:20px;
    line-height:1.08;
}

.helios-mission-input-head{
    margin:12px 0 8px;
    padding:13px 15px;
    box-shadow:none !important;
}

.helios-mission-input-head strong{
    display:block;
    margin-top:4px;
    color:#fff;
    font-size:16px;
}

.helios-mission-timeline,
.helios-mission-council,
.helios-mission-review,
.helios-mission-memory,
.helios-mission-templates,
.helios-agent-network,
.helios-mission-replay,
.helios-risk-radar,
.helios-next-actions,
.helios-mission-archive,
.helios-mission-artifact,
.helios-futuristic-deck{
    margin:12px 0;
    padding:16px;
}

.helios-mission-section-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:14px;
}

.helios-mission-section-head strong{
    display:block;
    margin-top:4px;
    color:#fff;
    font-size:17px;
    line-height:1.2;
}

.helios-mission-section-head em{
    min-height:32px;
    display:inline-flex;
    align-items:center;
    padding:0 12px;
    border-radius:999px;
    color:#f7eeee;
    background:rgba(10,7,7,.46);
    border:1px solid rgba(255,255,255,.12);
    font-size:11px;
    font-style:normal;
    font-weight:820;
    white-space:nowrap;
}

.helios-mission-step-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-mission-step-grid article{
    position:relative;
    min-height:172px;
    display:flex;
    flex-direction:column;
    gap:12px;
    padding:14px;
}

.helios-mission-step-grid article:before{
    content:"";
    position:absolute;
    top:14px;
    right:14px;
    width:8px;
    height:26px;
    border-radius:999px;
    background:rgba(255,255,255,.16);
}

.helios-mission-step-grid article.mission-step-active{
    border-color:rgba(255,101,104,.42);
    background:rgba(102,21,24,.18);
}

.helios-mission-step-grid article.mission-step-active:before{
    background:#ff6568;
    box-shadow:0 0 18px rgba(255,101,104,.72);
}

.helios-mission-step-grid article.mission-step-done{
    border-color:rgba(131,226,161,.28);
    background:rgba(131,226,161,.07);
}

.helios-mission-step-grid article.mission-step-done:before{
    background:#83e2a1;
    box-shadow:0 0 18px rgba(131,226,161,.54);
}

.helios-mission-step-grid strong,
.helios-mission-council-grid strong,
.helios-mission-artifact-grid strong,
.helios-deck-card > strong{
    display:block;
    margin-top:5px;
    color:#fff;
    font-size:16px;
    line-height:1.16;
}

.helios-mission-step-grid p,
.helios-mission-council-grid p,
.helios-deck-card p{
    margin:0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
    line-height:1.55 !important;
}

.helios-futuristic-deck{
    background:
        radial-gradient(circle at 12% 0%,rgba(255,101,104,.18),transparent 34%),
        radial-gradient(circle at 88% 0%,rgba(84,162,255,.15),transparent 32%),
        linear-gradient(135deg,rgba(255,101,104,.10),rgba(84,162,255,.065),rgba(26,21,21,.92)),
        rgba(18,14,14,.92) !important;
}

.helios-futuristic-deck-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-deck-card,
.helios-deck-memory-list article,
.helios-deck-pulse-grid div{
    min-width:0;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-deck-card{
    min-height:246px;
    padding:14px;
}

.helios-deck-card > strong{
    min-height:42px;
    font-size:17px;
}

.helios-deck-card p{
    min-height:58px;
    margin-top:10px !important;
    overflow:hidden;
    display:-webkit-box;
    -webkit-line-clamp:3;
    -webkit-box-orient:vertical;
}

.helios-deck-card > em{
    min-height:28px;
    display:inline-flex;
    align-items:center;
    margin-top:14px;
    padding:0 10px;
    border-radius:999px;
    color:#ffd2d4;
    background:rgba(102,21,24,.20);
    border:1px solid rgba(255,101,104,.24);
    font-size:10px;
    font-style:normal;
    font-weight:850;
    text-transform:uppercase;
}

.helios-deck-radar-map{
    position:relative;
    min-height:162px;
    margin-top:12px;
    border-radius:13px;
    border:1px solid rgba(255,255,255,.08);
    background:
        radial-gradient(circle at center,rgba(255,101,104,.16),transparent 26%),
        radial-gradient(circle at center,transparent 46%,rgba(84,162,255,.12) 47%,transparent 49%),
        rgba(10,7,7,.32);
    overflow:hidden;
}

.helios-deck-radar-map div,
.helios-deck-radar-map article{
    position:absolute;
    display:grid;
    place-items:center;
    text-align:center;
    border-radius:12px;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.10);
}

.helios-deck-radar-map div{
    left:50%;
    top:50%;
    width:76px;
    min-height:58px;
    transform:translate(-50%,-50%);
    border-color:rgba(255,101,104,.30);
    background:rgba(102,21,24,.20);
}

.helios-deck-radar-map b{
    color:#fff;
    font-size:13px;
}

.helios-deck-radar-map small,
.helios-deck-radar-map span{
    color:#9a8f8b;
    font-size:9px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-deck-radar-map strong{
    margin-top:4px;
    color:#fff;
    font-size:12px;
}

.helios-deck-radar-map article{
    width:70px;
    min-height:48px;
    padding:7px;
}

.helios-deck-radar-map article.active{
    border-color:rgba(84,162,255,.32);
    background:rgba(84,162,255,.08);
}

.helios-deck-radar-map article.current{
    border-color:rgba(255,101,104,.48);
    background:rgba(255,101,104,.13);
    box-shadow:0 0 0 1px rgba(255,101,104,.12),0 12px 30px rgba(0,0,0,.25);
}

.helios-deck-radar-map .deck-node-top{left:50%;top:8px;transform:translateX(-50%)}
.helios-deck-radar-map .deck-node-left{left:8px;top:50%;transform:translateY(-50%)}
.helios-deck-radar-map .deck-node-right{right:8px;top:50%;transform:translateY(-50%)}
.helios-deck-radar-map .deck-node-bottom{left:50%;bottom:8px;transform:translateX(-50%)}

.helios-deck-memory-list,
.helios-deck-pulse-grid{
    display:grid;
    gap:8px;
    margin-top:12px;
}

.helios-deck-memory-list article{
    min-height:48px;
    padding:9px 10px;
}

.helios-deck-memory-list strong,
.helios-deck-pulse-grid strong{
    display:block;
    margin-top:4px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:#fff;
    font-size:12px;
}

.helios-deck-pulse-grid{
    grid-template-columns:repeat(2,minmax(0,1fr));
}

.helios-deck-pulse-grid div{
    min-height:72px;
    padding:10px;
}

.helios-deck-pulse-grid i{
    display:block;
    height:5px;
    margin-top:9px;
    border-radius:999px;
    background:linear-gradient(90deg,#ff6568,#54a2ff,#83e2a1);
}

.helios-mission-step-grid em{
    margin-top:auto;
    width:max-content;
    max-width:100%;
    min-height:28px;
    display:inline-flex;
    align-items:center;
    padding:0 10px;
    border-radius:999px;
    color:#ffd2d4;
    background:rgba(102,21,24,.18);
    border:1px solid rgba(255,101,104,.28);
    font-size:10px;
    font-style:normal;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mission-council-grid,
.helios-mission-artifact-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:10px;
}

.helios-mission-council-grid article{
    min-height:142px;
    padding:14px;
}

.helios-mission-council-grid article.active{
    border-color:rgba(84,162,255,.34);
    background:rgba(84,162,255,.075);
}

.helios-mission-artifact-grid div{
    min-height:98px;
    padding:13px;
}

.helios-mission-artifact-grid strong{
    font-size:13px;
    line-height:1.45;
    overflow-wrap:anywhere;
}

.helios-mission-review{
    background:
        radial-gradient(circle at 8% 0%,rgba(84,162,255,.16),transparent 30%),
        linear-gradient(135deg,rgba(255,101,104,.10),rgba(26,21,21,.92)),
        rgba(18,14,14,.92) !important;
}

.helios-mission-review-meta{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:10px;
    margin-bottom:10px;
}

.helios-mission-review-meta div,
.helios-mission-review-empty,
.helios-mission-review-grid article{
    min-width:0;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-mission-review-meta div{
    min-height:64px;
    padding:12px;
}

.helios-mission-review-meta span,
.helios-mission-review-grid span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mission-review-meta strong,
.helios-mission-review-empty strong,
.helios-mission-review-grid strong{
    display:block;
    margin-top:5px;
    color:#fff;
    font-size:16px;
    line-height:1.18;
}

.helios-mission-review-empty{
    padding:15px;
}

.helios-mission-review-empty p{
    margin:8px 0 0 !important;
    color:#aaa09c !important;
    font-size:13px !important;
}

.helios-mission-review-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-mission-review-grid article{
    min-height:178px;
    padding:14px;
}

.helios-mission-review-grid b{
    display:block;
    margin:10px 0 8px;
    color:#ffd2d4;
    font-size:13px;
    line-height:1.35;
}

.helios-mission-review-grid p{
    margin:0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
    line-height:1.55 !important;
}

.helios-mission-memory{
    background:
        radial-gradient(circle at 92% 0%,rgba(131,226,161,.12),transparent 30%),
        linear-gradient(135deg,rgba(84,162,255,.08),rgba(26,21,21,.92)),
        rgba(18,14,14,.92) !important;
}

.helios-mission-memory-rail{
    position:relative;
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-mission-memory-rail:before{
    content:"";
    position:absolute;
    left:24px;
    right:24px;
    top:20px;
    height:1px;
    background:linear-gradient(90deg,rgba(255,101,104,.62),rgba(84,162,255,.38),rgba(131,226,161,.42));
    opacity:.58;
    pointer-events:none;
}

.helios-mission-memory-rail article{
    position:relative;
    min-width:0;
    min-height:154px;
    padding:40px 14px 14px;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-mission-memory-rail article:before{
    content:"";
    position:absolute;
    left:16px;
    top:15px;
    width:11px;
    height:11px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 0 7px rgba(255,101,104,.08),0 0 20px rgba(255,101,104,.72);
}

.helios-mission-memory-rail article.memory-kind-checkpoint:before{
    background:#54a2ff;
    box-shadow:0 0 0 7px rgba(84,162,255,.08),0 0 20px rgba(84,162,255,.62);
}

.helios-mission-memory-rail article.memory-kind-decision:before{
    background:#ffc56d;
    box-shadow:0 0 0 7px rgba(255,197,109,.08),0 0 20px rgba(255,197,109,.56);
}

.helios-mission-memory-rail article.memory-kind-progress:before{
    background:#83e2a1;
    box-shadow:0 0 0 7px rgba(131,226,161,.08),0 0 20px rgba(131,226,161,.54);
}

.helios-mission-memory-rail span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mission-memory-rail strong{
    display:block;
    margin-top:7px;
    color:#fff;
    font-size:13px;
    line-height:1.45;
    overflow-wrap:anywhere;
}

.helios-mission-memory-rail em{
    display:block;
    margin-top:12px;
    color:#8f8580;
    font-size:10px;
    font-style:normal;
    font-weight:760;
}

.helios-risk-radar{
    background:
        radial-gradient(circle at 92% 0%,rgba(255,197,109,.14),transparent 30%),
        linear-gradient(135deg,rgba(255,101,104,.10),rgba(26,21,21,.92)),
        rgba(18,14,14,.92) !important;
}

.helios-risk-radar.risk-level-critical{
    border-color:rgba(255,101,104,.34) !important;
}

.helios-risk-radar.risk-level-watch{
    border-color:rgba(255,197,109,.30) !important;
}

.helios-risk-radar-grid,
.helios-next-action-grid,
.helios-mission-archive-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:10px;
}

.helios-risk-radar-grid article,
.helios-next-action-grid article,
.helios-mission-archive-grid article{
    min-width:0;
    min-height:96px;
    padding:12px;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-risk-radar-grid span,
.helios-next-action-grid span,
.helios-mission-archive-grid span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-risk-radar-grid strong,
.helios-next-action-grid strong,
.helios-mission-archive-grid strong{
    display:block;
    margin-top:7px;
    color:#fff;
    font-size:13px;
    line-height:1.32;
    overflow-wrap:normal;
}

.helios-next-action-grid strong{
    font-size:14px;
}

.helios-mission-section-head strong{
    font-size:18px !important;
    line-height:1.18 !important;
}

.helios-risk-radar-grid em,
.helios-mission-archive-grid em{
    display:inline-flex;
    align-items:center;
    width:max-content;
    max-width:100%;
    min-height:26px;
    margin-top:12px;
    padding:0 9px;
    border-radius:999px;
    color:#ffd2d4;
    background:rgba(102,21,24,.20);
    border:1px solid rgba(255,101,104,.24);
    font-size:10px;
    font-style:normal;
    font-weight:850;
    text-transform:uppercase;
}

.helios-risk-radar-grid article.risk-tone-high{
    border-color:rgba(255,101,104,.34);
    background:rgba(255,101,104,.07);
}

.helios-risk-radar-grid article.risk-tone-medium{
    border-color:rgba(255,197,109,.30);
    background:rgba(255,197,109,.06);
}

.helios-risk-radar-grid article.risk-tone-low{
    border-color:rgba(131,226,161,.24);
    background:rgba(131,226,161,.045);
}

.helios-next-actions{
    background:
        radial-gradient(circle at 8% 0%,rgba(84,162,255,.14),transparent 30%),
        linear-gradient(135deg,rgba(84,162,255,.08),rgba(26,21,21,.92)),
        rgba(18,14,14,.92) !important;
}

.helios-mission-action-notice{
    margin:8px 0 10px;
    padding:11px 14px;
    border-radius:13px;
    color:#e8e3e0;
    background:rgba(10,7,7,.46);
    border:1px solid rgba(255,255,255,.10);
    font-size:13px;
    font-weight:720;
}

.helios-mission-archive{
    background:
        radial-gradient(circle at 90% 0%,rgba(84,162,255,.12),transparent 30%),
        linear-gradient(135deg,rgba(255,101,104,.08),rgba(26,21,21,.92)),
        rgba(18,14,14,.92) !important;
}

.helios-mission-archive-grid{
    grid-template-columns:repeat(4,minmax(0,1fr));
}

.helios-mission-archive-grid article{
    min-height:154px;
}

.helios-mission-archive-grid p{
    margin:8px 0 0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
    line-height:1.5 !important;
    overflow-wrap:anywhere;
}

.helios-mission-template-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
}

.helios-mission-template-grid article{
    min-width:0;
    min-height:172px;
    padding:14px;
    border-radius:13px;
    background:
        linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.018)),
        rgba(10,7,7,.32);
    border:1px solid rgba(255,255,255,.09);
}

.helios-mission-template-grid span,
.helios-mission-replay-track span,
.helios-agent-network-map article span,
.helios-agent-network-core span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-mission-template-grid strong,
.helios-mission-replay-track strong,
.helios-agent-network-map article strong,
.helios-agent-network-core strong{
    display:block;
    margin-top:7px;
    color:#fff;
    font-size:15px;
    line-height:1.25;
}

.helios-mission-template-grid p{
    margin:9px 0 0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
    line-height:1.5 !important;
}

.helios-mission-template-grid em{
    display:inline-flex;
    align-items:center;
    min-height:26px;
    margin-top:13px;
    padding:0 9px;
    border-radius:999px;
    color:#ffd2d4;
    background:rgba(102,21,24,.20);
    border:1px solid rgba(255,101,104,.24);
    font-size:10px;
    font-style:normal;
    font-weight:850;
    text-transform:uppercase;
}

.helios-agent-network-map{
    position:relative;
    min-height:350px;
    border-radius:14px;
    background:
        linear-gradient(90deg,transparent,rgba(255,101,104,.16),transparent) 0 50%/100% 1px no-repeat,
        linear-gradient(180deg,transparent,rgba(84,162,255,.14),transparent) 50% 0/1px 100% no-repeat,
        radial-gradient(circle at center,rgba(84,162,255,.08),transparent 42%),
        rgba(10,7,7,.28);
    border:1px solid rgba(255,255,255,.08);
    overflow:hidden;
}

.helios-agent-network-map:before,
.helios-agent-network-map:after{
    content:"";
    position:absolute;
    inset:54px;
    border:1px solid rgba(255,255,255,.07);
    border-radius:999px;
    pointer-events:none;
}

.helios-agent-network-map:after{
    inset:98px;
    border-color:rgba(255,101,104,.12);
}

.helios-agent-network-core,
.helios-agent-network-map article{
    position:absolute;
    display:grid;
    place-items:center;
    text-align:center;
    border-radius:15px;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.10);
    box-shadow:0 18px 40px rgba(0,0,0,.22);
}

.helios-agent-network-core{
    left:50%;
    top:50%;
    width:150px;
    min-height:92px;
    transform:translate(-50%,-50%);
    border-color:rgba(255,101,104,.24);
    background:rgba(102,21,24,.18);
}

.helios-agent-network-map article{
    width:128px;
    min-height:82px;
    padding:12px;
}

.helios-agent-network-map article.active{
    border-color:rgba(84,162,255,.30);
    background:rgba(84,162,255,.08);
}

.helios-agent-network-map article.current{
    border-color:rgba(255,101,104,.44);
    background:rgba(255,101,104,.12);
    box-shadow:0 0 0 1px rgba(255,101,104,.12),0 18px 44px rgba(0,0,0,.28);
}

.helios-agent-network-map article.current:before{
    content:"";
    position:absolute;
    top:10px;
    right:10px;
    width:8px;
    height:8px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 18px rgba(255,101,104,.78);
}

.helios-agent-network-map .node-top{left:50%;top:24px;transform:translateX(-50%)}
.helios-agent-network-map .node-left{left:24px;top:50%;transform:translateY(-50%)}
.helios-agent-network-map .node-right{right:24px;top:50%;transform:translateY(-50%)}
.helios-agent-network-map .node-bottom{left:50%;bottom:24px;transform:translateX(-50%)}

.helios-mission-replay-track{
    position:relative;
    display:grid;
    gap:10px;
}

.helios-mission-replay-track:before{
    content:"";
    position:absolute;
    left:16px;
    top:12px;
    bottom:12px;
    width:1px;
    background:linear-gradient(transparent,rgba(255,101,104,.60),rgba(84,162,255,.35),transparent);
    pointer-events:none;
}

.helios-mission-replay-track article{
    position:relative;
    min-height:74px;
    padding:12px 12px 12px 42px;
    border-radius:13px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
}

.helios-mission-replay-track article:before{
    content:"";
    position:absolute;
    left:11px;
    top:17px;
    width:11px;
    height:11px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 0 7px rgba(255,101,104,.08),0 0 20px rgba(255,101,104,.70);
}

.helios-mission-replay-track em{
    display:block;
    margin-top:8px;
    color:#8f8580;
    font-size:10px;
    font-style:normal;
    font-weight:760;
}

/* Tabs and content */
.helios-tab-panel{
    display:flex;
    align-items:center;
    gap:8px;
    margin:8px 0;
    padding:10px 12px;
    color:#c8bfbb;
    box-shadow:none !important;
}

.helios-tab-panel strong{
    color:#fff;
    font-size:14px;
}

.helios-tab-panel span{
    color:#aaa09c;
    font-size:13px;
}

.helios-command-message{
    padding:14px;
    border-radius:13px;
    background:rgba(255,255,255,.032);
    border:1px solid rgba(255,255,255,.08);
}

.helios-command-message strong{
    display:block;
    color:#fff;
    font-size:16px;
    margin-bottom:6px;
}

.helios-command-message p{
    margin:0 !important;
    color:#c8bfbb !important;
}

.helios-command-palette{
    margin:12px 0;
    padding:16px;
}

.helios-palette-title{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:14px;
    padding-bottom:12px;
    border-bottom:1px solid rgba(255,255,255,.08);
}

.helios-palette-title strong{
    display:block;
    color:#fff;
    font-size:18px;
    line-height:1.2;
}

.helios-palette-title span{
    display:block;
    margin-top:5px;
    color:#aaa09c;
    font-size:12px;
    line-height:1.45;
}

.helios-palette-group-label{
    margin:12px 0 8px;
    color:#ffd2d4;
    font-size:10px;
    font-weight:880;
    text-transform:uppercase;
}

.helios-palette-command-card{
    display:grid;
    grid-template-columns:minmax(0,1fr) auto;
    align-items:center;
    gap:14px;
    margin:8px 0 5px;
    padding:13px 14px;
    border-radius:14px;
    background:
        radial-gradient(circle at 0% 0%,rgba(255,101,104,.13),transparent 32%),
        rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.08);
}

.helios-palette-command-card.compact{
    grid-template-columns:1fr;
    background:rgba(255,255,255,.028);
}

.helios-palette-command-card strong,
.helios-palette-command-card span{
    display:block;
    min-width:0;
}

.helios-palette-command-card strong{
    color:#fff;
    font-size:14px;
}

.helios-palette-command-card span{
    margin-top:4px;
    color:#aaa09c;
    font-size:12px;
    line-height:1.45;
}

.helios-palette-command-card em{
    padding:7px 10px;
    border-radius:999px;
    color:#ffe3e4;
    background:rgba(102,21,24,.20);
    border:1px solid rgba(255,101,104,.26);
    font-size:10px;
    font-style:normal;
    font-weight:850;
    white-space:nowrap;
}

.helios-action-notice,
.helios-tab-panel{
    background:rgba(10,7,7,.46) !important;
}

.helios-action-notice{
    margin:8px 0 10px;
    padding:11px 14px;
    color:#e8e3e0;
    font-size:13px;
    font-weight:720;
}

.helios-section-header{
    margin:20px 0 12px;
}

.helios-section-header h2{
    margin:0 !important;
    font-size:24px !important;
}

.helios-section-header p{
    max-width:820px;
    margin:6px 0 0 !important;
    color:#aaa09c !important;
    font-size:13px !important;
}

.helios-feature-card{
    min-height:172px;
    padding:16px;
    margin-bottom:10px;
    transition:transform .18s cubic-bezier(.2,.8,.2,1),border-color .18s ease !important;
}

.helios-feature-card:hover{
    transform:translateY(-3px);
    border-color:rgba(255,101,104,.32) !important;
}

.helios-feature-top{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:10px;
    margin-bottom:14px;
}

.helios-feature-card h3{
    margin:0 !important;
    font-size:17px !important;
}

.helios-feature-card p{
    margin:9px 0 0 !important;
    color:#aaa09c !important;
    font-size:12px !important;
}

.helios-feature-foot{
    margin-top:16px;
    display:flex;
    align-items:center;
    gap:8px;
    color:#ff9b9d;
    font-size:11px;
    font-weight:820;
}

.helios-feature-foot span,
.helios-feed-row span,
.helios-terminal-top span{
    width:8px;
    height:8px;
    border-radius:999px;
    background:#83e2a1;
}

.helios-terminal-grid{
    display:grid;
    gap:8px;
    margin-top:12px;
}

.helios-terminal-top{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding-bottom:12px;
    border-bottom:1px solid rgba(255,255,255,.08);
}

.helios-terminal-top div{
    display:flex;
    align-items:center;
    gap:8px;
}

.helios-terminal-top strong,
.helios-terminal-top small{
    color:#e8e3e0;
    font-size:11px;
    font-weight:820;
    text-transform:uppercase;
}

.helios-terminal-top small{
    color:#7f7673;
}

.helios-terminal-row{
    min-width:0;
    display:grid;
    grid-template-columns:70px 74px minmax(0,1fr) minmax(132px,.34fr) 48px;
    align-items:center;
    gap:10px;
    min-height:42px;
    padding:9px 11px;
    border-radius:12px;
    background:rgba(10,7,7,.38);
    border:1px solid rgba(255,255,255,.075);
}

.helios-terminal-row span,
.helios-terminal-row strong,
.helios-terminal-row small,
.helios-terminal-row em{
    white-space:nowrap;
}

.helios-terminal-row span{
    color:#7f7673;
    font-size:11px;
    font-weight:760;
}

.helios-terminal-row strong{
    color:#ffd2d4;
    font-size:11px;
    font-weight:860;
}

.helios-terminal-row p{
    min-width:0;
    margin:0 !important;
    color:#d8d1ce !important;
    font-size:12px !important;
    line-height:1.35 !important;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.helios-terminal-row small{
    min-width:0;
    color:#9a908c;
    font-size:10px;
    font-weight:760;
    overflow:hidden;
    text-overflow:ellipsis;
}

.helios-terminal-row em{
    justify-self:end;
    min-width:38px;
    text-align:center;
    padding:4px 7px;
    border-radius:999px;
    color:#d8fff0;
    background:rgba(131,226,161,.08);
    border:1px solid rgba(131,226,161,.24);
    font-size:9px;
    font-style:normal;
    font-weight:860;
}

.helios-terminal-row.status-live em{
    color:#fff3d8;
    background:rgba(255,197,109,.08);
    border-color:rgba(255,197,109,.26);
}

.helios-terminal-row.status-warn em,
.helios-terminal-row.status-idle em{
    color:#ffdcb0;
    background:rgba(255,197,109,.07);
    border-color:rgba(255,197,109,.22);
}

.helios-terminal-row.status-err em{
    color:#ffd2d4;
    background:rgba(255,101,104,.09);
    border-color:rgba(255,101,104,.30);
}

.helios-log-drawer{
    margin-top:12px;
    border-top:1px solid rgba(255,255,255,.08);
    padding-top:10px;
}

.helios-log-drawer summary{
    cursor:pointer;
    color:#aaa09c;
    font-size:11px;
    font-weight:820;
    text-transform:uppercase;
}

.helios-log-drawer > div{
    display:grid;
    gap:8px;
    margin-top:10px;
    max-height:360px;
    overflow:auto;
}

/* Upload */
.helios-upload-shell{
    width:100%;
    max-width:100%;
    display:grid;
    grid-template-columns:52px minmax(0,1fr);
    gap:14px;
    align-items:center;
    margin:10px 0 12px;
    padding:16px;
}

.helios-upload-shell h3{
    margin:0 0 5px !important;
    color:#fff !important;
    font-size:18px !important;
}

.helios-upload-shell p{
    margin:0 !important;
    color:#aaa09c !important;
    font-size:13px !important;
}

div[data-testid="stFileUploader"]{
    width:100% !important;
    max-width:100% !important;
    margin:10px 0 14px !important;
    overflow:hidden !important;
}

div[data-testid="stFileUploader"] section{
    position:relative !important;
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    min-height:92px !important;
    display:grid !important;
    grid-template-columns:168px minmax(0,1fr) !important;
    align-items:center !important;
    gap:16px !important;
    padding:18px 20px !important;
    border-radius:18px !important;
    color:#e8e3e0 !important;
    background:
        radial-gradient(circle at 0% 0%,rgba(255,101,104,.11),transparent 34%),
        linear-gradient(135deg,rgba(255,255,255,.052),rgba(255,255,255,.018)),
        rgba(26,21,21,.78) !important;
    border:1px dashed rgba(255,101,104,.32) !important;
    overflow:hidden !important;
}

div[data-testid="stFileUploader"] section > div{
    min-width:0 !important;
    display:contents !important;
}

div[data-testid="stFileUploader"] button{
    position:relative !important;
    width:144px !important;
    min-width:144px !important;
    max-width:144px !important;
    min-height:42px !important;
    flex:0 0 auto !important;
    border-radius:999px !important;
    padding:0 16px !important;
    justify-content:center !important;
    overflow:visible !important;
    white-space:nowrap !important;
    text-transform:capitalize !important;
    color:transparent !important;
    font-size:0 !important;
    background:
        radial-gradient(circle at 30% 18%,rgba(255,255,255,.20),transparent 30%),
        linear-gradient(135deg,rgba(255,101,104,.92),rgba(139,26,30,.84)) !important;
    border-color:rgba(255,255,255,.16) !important;
    box-shadow:0 14px 30px rgba(102,21,24,.24) !important;
}

div[data-testid="stFileUploader"] button:hover{
    transform:translateY(-1px) !important;
    border-color:rgba(255,101,104,.54) !important;
    box-shadow:0 18px 38px rgba(102,21,24,.34) !important;
}

div[data-testid="stFileUploader"] button *,
div[data-testid="stFileUploader"] button p,
div[data-testid="stFileUploader"] button span{
    visibility:hidden !important;
    font-size:0 !important;
}

div[data-testid="stFileUploader"] button:after{
    content:"Upload";
    color:#fff;
    font-size:13px;
    font-weight:840;
    line-height:1;
}

div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"]{
    display:none !important;
}

div[data-testid="stFileUploader"] section:after{
    content:"Drop file here • TXT, PY, MD";
    min-width:0;
    color:#c8bfbb;
    font-size:13px;
    font-weight:780;
    line-height:1.35;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.helios-reactor-head strong,
.helios-mission-section-head strong,
.helios-next-action-grid strong,
.helios-risk-radar-grid strong,
.helios-mission-review-empty strong,
.helios-mission-review-empty p{
    word-break:normal !important;
    overflow-wrap:normal !important;
}

div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"]{
    min-width:0 !important;
    border-radius:12px !important;
    background:rgba(10,7,7,.42) !important;
    border:1px solid rgba(255,255,255,.10) !important;
}

/* Chat history */
.helios-memory-vault{
    position:relative;
    display:grid;
    grid-template-columns:58px minmax(0,1fr) auto;
    align-items:center;
    gap:16px;
    margin:12px 0;
    padding:17px 18px;
    background:
        radial-gradient(circle at 4% 20%,rgba(255,101,104,.22),transparent 28%),
        linear-gradient(120deg,rgba(255,255,255,.055),rgba(255,255,255,.016)),
        rgba(26,21,21,.84) !important;
}

.helios-memory-vault:before{
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    border-radius:inherit;
    background:
        linear-gradient(90deg,rgba(255,101,104,.16),transparent 34%,rgba(84,162,255,.10));
}

.helios-vault-sigil{
    width:50px;
    height:50px;
    display:grid;
    place-items:center;
    border-radius:16px;
    color:#fff;
    background:
        radial-gradient(circle at 28% 22%,rgba(255,255,255,.30),transparent 34%),
        linear-gradient(135deg,rgba(255,101,104,.82),rgba(163,0,55,.62),rgba(84,162,255,.30));
    border:1px solid rgba(255,255,255,.20);
    box-shadow:0 0 28px rgba(255,101,104,.30);
    font-size:20px;
}

.helios-memory-vault span,
.helios-vault-metrics span,
.helios-session-rail-head span,
.helios-session-card span,
.helios-memory-detail-head span,
.helios-memory-thread article > span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-memory-vault strong{
    display:block;
    margin:4px 0 5px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:#fff;
    font-size:19px;
    line-height:1.2;
}

.helios-memory-vault p{
    margin:0 !important;
    color:#a99f9b !important;
    font-size:13px;
}

.helios-memory-vault em{
    position:relative;
    z-index:1;
    min-height:32px;
    display:inline-flex;
    align-items:center;
    padding:0 11px;
    border-radius:999px;
    color:#ffd2d4;
    background:rgba(102,21,24,.24);
    border:1px solid rgba(255,101,104,.34);
    font-size:11px;
    font-style:normal;
    font-weight:820;
    white-space:nowrap;
}

.helios-vault-metrics{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
    margin:12px 0;
}

.helios-vault-metrics div{
    min-height:74px;
    padding:12px;
    border-radius:14px;
    background:
        linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.018)),
        rgba(20,15,15,.74);
    border:1px solid rgba(255,255,255,.10);
}

.helios-vault-metrics strong{
    display:block;
    margin-top:9px;
    color:#fff;
    font-size:23px;
    line-height:1;
}

.helios-session-rail{
    margin:0 0 10px;
    padding:14px;
    border-radius:14px;
    background:
        linear-gradient(135deg,rgba(255,101,104,.12),rgba(84,162,255,.055)),
        rgba(26,21,21,.70);
    border:1px solid rgba(255,255,255,.10);
}

.st-key-helios_memory_scroll_container{
    position:relative;
    height:640px !important;
    width:100% !important;
    max-width:100% !important;
    overflow:hidden !important;
    border-radius:18px;
    background:
        linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.012)),
        rgba(10,7,7,.36);
    border:1px solid rgba(255,255,255,.08);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.05);
}

.st-key-helios_memory_scroll_container:before,
.st-key-helios_memory_scroll_container:after{
    content:"";
    position:absolute;
    left:0;
    right:0;
    height:54px;
    z-index:4;
    pointer-events:none;
}

.st-key-helios_memory_scroll_container:before{
    top:0;
    background:linear-gradient(180deg,rgba(10,7,7,.92),transparent);
}

.st-key-helios_memory_scroll_container:after{
    bottom:0;
    background:linear-gradient(0deg,rgba(10,7,7,.92),transparent);
}

.st-key-helios_memory_scroll_container [data-testid="stVerticalBlock"]{
    width:100% !important;
    max-width:100% !important;
    gap:8px !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stVerticalBlockBorderWrapper"]{
    width:100% !important;
    max-width:100% !important;
    border:0 !important;
}

.st-key-helios_memory_scroll_container ::-webkit-scrollbar{
    width:8px;
}

.st-key-helios_memory_scroll_container ::-webkit-scrollbar-track{
    background:rgba(255,255,255,.035);
    border-radius:999px;
}

.st-key-helios_memory_scroll_container ::-webkit-scrollbar-thumb{
    border-radius:999px;
    background:linear-gradient(#ff6568,#661518);
}

.helios-session-rail-head strong{
    display:block;
    margin-top:4px;
    color:#fff;
    font-size:18px;
}

.helios-session-rail-head p{
    margin:6px 0 0 !important;
    color:#9f9693 !important;
    font-size:12px;
    line-height:1.42;
}

.helios-session-focus{
    margin:12px 0;
    padding:15px;
    border-radius:16px;
    background:
        radial-gradient(circle at 8% 0%,rgba(255,101,104,.20),transparent 36%),
        linear-gradient(135deg,rgba(255,101,104,.13),rgba(84,162,255,.045)),
        rgba(22,16,16,.90);
    border:1px solid rgba(255,101,104,.28);
    box-shadow:0 18px 44px rgba(0,0,0,.24);
}

.helios-session-focus span{
    color:#ffb5b7;
    font-size:10px;
    font-weight:880;
    text-transform:uppercase;
}

.helios-session-focus strong{
    display:block;
    margin:8px 0 8px;
    color:#fff;
    font-size:15px;
    line-height:1.28;
}

.helios-session-focus p{
    margin:0 0 11px !important;
    color:#b8afab !important;
    font-size:12px;
    line-height:1.5;
}

.helios-session-focus em,
.helios-history-page-indicator{
    color:#8f8580;
    font-size:11px;
    font-style:normal;
    font-weight:760;
}

.helios-history-page-indicator{
    min-height:42px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:12px;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.09);
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"]{
    width:100% !important;
    max-width:100% !important;
    margin:4px 0 10px !important;
    overflow:hidden !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"] > div{
    width:100% !important;
    max-width:100% !important;
    gap:7px !important;
    overflow:hidden !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"] label{
    width:100% !important;
    max-width:100% !important;
    min-height:54px !important;
    display:flex !important;
    align-items:flex-start !important;
    gap:9px !important;
    padding:10px 12px !important;
    border-radius:12px !important;
    color:#bdb3af !important;
    background:rgba(255,255,255,.026) !important;
    border:1px solid rgba(255,255,255,.08) !important;
    overflow:hidden !important;
    transition:background .16s ease,border-color .16s ease,transform .16s ease !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"] label > div:first-child{
    flex:0 0 18px !important;
    margin-top:2px !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"] label:hover{
    transform:translateX(2px);
    background:rgba(255,255,255,.05) !important;
    border-color:rgba(255,255,255,.14) !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"] label p{
    margin:0 !important;
    min-width:0;
    max-width:100% !important;
    display:block !important;
    flex:1 1 auto !important;
    overflow:visible !important;
    color:inherit !important;
    font-size:12.5px !important;
    font-weight:760 !important;
    line-height:1.32 !important;
    text-overflow:clip !important;
    white-space:normal !important;
    overflow-wrap:anywhere !important;
    word-break:break-word !important;
}

.st-key-helios_memory_scroll_container div[data-testid="stRadio"] label:has(input:checked){
    color:#fff !important;
    background:
        linear-gradient(90deg,rgba(255,101,104,.20),rgba(102,21,24,.10)),
        rgba(255,255,255,.045) !important;
    border-color:rgba(255,101,104,.38) !important;
    box-shadow:inset 3px 0 0 #ff6568;
}

.helios-session-card{
    position:relative;
    margin:10px 0 7px;
    padding:13px 13px 12px;
    border-radius:14px;
    background:
        linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.014)),
        rgba(18,14,14,.82);
    border:1px solid rgba(255,255,255,.10);
    box-shadow:0 14px 34px rgba(0,0,0,.20);
}

.helios-session-card.active{
    border-color:rgba(255,101,104,.52);
    background:
        radial-gradient(circle at 12% 0%,rgba(255,101,104,.20),transparent 36%),
        linear-gradient(135deg,rgba(255,101,104,.18),rgba(84,162,255,.06)),
        rgba(24,17,17,.92);
    box-shadow:0 0 0 1px rgba(255,101,104,.12),0 18px 42px rgba(0,0,0,.30);
}

.helios-session-card.active:after{
    content:"";
    position:absolute;
    top:14px;
    right:12px;
    width:7px;
    height:24px;
    border-radius:999px;
    background:#ff6568;
    box-shadow:0 0 16px rgba(255,101,104,.70);
}

.helios-session-card strong{
    display:block;
    margin:6px 18px 7px 0;
    color:#fff;
    font-size:14px;
    line-height:1.32;
}

.helios-session-card p{
    margin:0 0 10px !important;
    color:#aaa09c !important;
    font-size:12px;
    line-height:1.48;
}

.helios-session-card em{
    color:#7f7673;
    font-size:10px;
    font-style:normal;
    font-weight:760;
}

.helios-memory-detail{
    position:sticky;
    top:18px;
    width:100%;
    max-width:100%;
    max-height:calc(100vh - 220px);
    overflow:hidden auto;
    padding:18px;
    background:
        radial-gradient(circle at 90% 0%,rgba(84,162,255,.12),transparent 30%),
        radial-gradient(circle at 0% 8%,rgba(255,101,104,.18),transparent 32%),
        rgba(22,17,17,.86) !important;
}

div[data-testid="column"]{
    min-width:0 !important;
}

.helios-memory-detail::-webkit-scrollbar{
    width:8px;
}

.helios-memory-detail::-webkit-scrollbar-track{
    background:rgba(255,255,255,.035);
}

.helios-memory-detail::-webkit-scrollbar-thumb{
    border-radius:999px;
    background:linear-gradient(#ff6568,#661518);
}

.helios-memory-detail-head{
    display:flex;
    justify-content:space-between;
    gap:16px;
    min-width:0;
    padding-bottom:15px;
    border-bottom:1px solid rgba(255,255,255,.10);
}

.helios-memory-detail-head > div{
    min-width:0;
}

.helios-memory-detail-head strong{
    display:block;
    margin:6px 0 7px;
    color:#fff;
    font-size:23px;
    line-height:1.18;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.helios-memory-detail-head em{
    color:#8b817e;
    font-size:11px;
    font-style:normal;
    font-weight:780;
}

.helios-memory-detail-head b{
    flex:0 0 auto;
    height:32px;
    display:inline-flex;
    align-items:center;
    padding:0 11px;
    border-radius:999px;
    color:#ffd2d4;
    background:rgba(102,21,24,.22);
    border:1px solid rgba(255,101,104,.34);
    font-size:11px;
}

.helios-memory-thread{
    display:grid;
    gap:13px;
    margin-top:15px;
}

.helios-memory-thread article{
    min-width:0;
    max-width:100%;
    overflow:hidden;
    padding:15px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,.10);
}

.helios-memory-thread article.user{
    background:rgba(84,162,255,.075);
    border-color:rgba(84,162,255,.26);
}

.helios-memory-thread article.ai{
    background:rgba(255,255,255,.035);
    border-color:rgba(255,101,104,.18);
}

.helios-memory-thread article div{
    max-width:100%;
    margin-top:9px;
    color:#e8e3e0;
    font-size:14px;
    line-height:1.68;
    overflow-wrap:anywhere;
    word-break:break-word;
}

.helios-memory-thread article p,
.helios-memory-thread article li{
    max-width:100%;
    overflow-wrap:anywhere;
    word-break:break-word;
}

.helios-memory-thread article p{
    margin:0 0 10px !important;
    color:#e8e3e0 !important;
}

.helios-memory-thread article ul,
.helios-memory-thread article ol{
    margin:8px 0 8px 20px;
    padding:0;
}

.helios-memory-thread article code{
    white-space:pre-wrap;
    overflow-wrap:anywhere;
}

.helios-memory-actions{
    width:100%;
    max-width:100%;
    margin-top:10px;
    overflow:hidden;
}

.helios-memory-actions [data-testid="column"]{
    min-width:0 !important;
}

.helios-memory-actions button,
.helios-memory-actions [data-testid="stDownloadButton"] button{
    min-height:44px !important;
    padding:0 12px !important;
    overflow:hidden !important;
    text-overflow:ellipsis !important;
    white-space:nowrap !important;
    font-size:13px !important;
}

[data-testid="stDownloadButton"] button,
.stButton button{
    overflow:hidden !important;
    text-overflow:ellipsis !important;
    white-space:nowrap !important;
}

@media (max-width:900px){
    .helios-memory-vault{
        grid-template-columns:1fr;
    }

    .helios-memory-vault em{
        width:max-content;
    }

    .helios-vault-metrics{
        grid-template-columns:repeat(2,minmax(0,1fr));
    }

    .helios-memory-detail-head{
        display:grid;
    }
}

/* Voice / response */
.helios-voice-cockpit{
    display:grid;
    grid-template-columns:64px minmax(0,1fr);
    gap:16px;
    align-items:center;
    margin:14px 0;
    padding:18px;
}

.helios-voice-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    margin-bottom:10px;
}

.helios-voice-head span{
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-voice-head strong{
    color:#fff;
    font-size:17px;
}

.helios-waveform{
    height:36px;
    display:flex;
    align-items:center;
    gap:4px;
    padding:8px;
    border-radius:12px;
    background:rgba(10,7,7,.48);
    border:1px solid rgba(255,255,255,.08);
}

.helios-waveform span,
.helios-thinking-bars span{
    width:5px;
    border-radius:999px;
    background:#ff6568;
    animation:helios-bar 1.24s ease-in-out infinite;
}

.helios-waveform span:nth-child(3n){height:24px;background:#ffa2ae}
.helios-waveform span:nth-child(4n){height:30px;background:#8b1a1e}

.helios-live-voice-shell{
    margin:0 0 18px;
}

.helios-live-hero{
    position:relative;
    min-height:292px;
    display:grid;
    grid-template-columns:minmax(220px,330px) minmax(300px,1fr) minmax(240px,360px);
    align-items:center;
    gap:28px;
    padding:28px !important;
    border-color:rgba(255,101,104,.22) !important;
    background:
        radial-gradient(circle at 18% 48%,rgba(255,101,104,.20),transparent 28%),
        radial-gradient(circle at 82% 18%,rgba(86,156,255,.14),transparent 30%),
        linear-gradient(110deg,rgba(255,101,104,.12),rgba(255,255,255,.025) 48%,rgba(64,214,158,.08)),
        rgba(18,13,14,.92) !important;
}

.helios-live-orb{
    position:relative;
    width:min(28vw,260px);
    min-width:190px;
    aspect-ratio:1;
    margin:auto;
    display:grid;
    place-items:center;
    border-radius:50%;
    background:
        conic-gradient(from 20deg,#ff6568,#569cff,#40d69e,#ffb36b,#ff6568);
    box-shadow:
        0 0 70px rgba(255,101,104,.25),
        inset 0 0 30px rgba(255,255,255,.18);
}

.helios-live-orb:before{
    content:"";
    position:absolute;
    inset:18px;
    border-radius:50%;
    background:#050303;
    box-shadow:
        inset 0 0 60px rgba(255,101,104,.10),
        0 0 0 1px rgba(255,255,255,.08);
}

.helios-live-orb span{
    position:absolute;
    inset:42px;
    border-radius:50%;
    border:1px solid rgba(255,255,255,.18);
    box-shadow:0 0 45px rgba(86,156,255,.18);
}

.helios-live-orb i{
    position:relative;
    z-index:1;
    width:18px;
    height:18px;
    border-radius:50%;
    background:#ff6568;
    box-shadow:
        0 0 0 14px rgba(255,101,104,.12),
        0 0 36px rgba(255,101,104,.92);
}

.helios-live-hero.state-listening .helios-live-orb i{
    background:#40d69e;
    box-shadow:
        0 0 0 14px rgba(64,214,158,.12),
        0 0 36px rgba(64,214,158,.92);
}

.helios-live-hero.state-speaking .helios-live-orb i{
    background:#569cff;
    box-shadow:
        0 0 0 14px rgba(86,156,255,.12),
        0 0 36px rgba(86,156,255,.92);
}

.helios-live-copy span,
.helios-live-status span,
.helios-live-panel-head span,
.helios-live-backend-note span{
    display:block;
    color:#9a8f8b;
    font-size:10px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-live-copy strong{
    display:block;
    margin:8px 0 10px;
    color:#fff;
    font-size:clamp(34px,4vw,62px);
    font-weight:900;
    line-height:.92;
}

.helios-live-copy p{
    max-width:640px;
    margin:0 0 22px !important;
    color:#d0c8c4 !important;
    font-size:18px !important;
    line-height:1.4 !important;
}

.helios-live-waveform{
    height:62px;
    display:flex;
    align-items:center;
    gap:6px;
    overflow:hidden;
}

.helios-live-waveform span{
    width:8px;
    height:24px;
    border-radius:999px;
    background:linear-gradient(180deg,#fff,#ff6568);
    opacity:.82;
    box-shadow:0 0 18px rgba(255,101,104,.22);
}

.helios-live-waveform span:nth-child(3n){
    background:linear-gradient(180deg,#a9ccff,#569cff);
}

.helios-live-waveform span:nth-child(4n){
    height:42px;
    background:linear-gradient(180deg,#a8ffe0,#40d69e);
}

.helios-live-waveform span:nth-child(5n){
    height:52px;
}

.helios-live-status{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:12px;
}

.helios-live-status div{
    min-height:92px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    padding:16px;
    border-radius:16px;
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.10);
}

.helios-live-status strong{
    display:block;
    margin-top:8px;
    color:#fff;
    font-size:19px;
    font-weight:880;
    line-height:1.15;
}

.helios-live-panel{
    margin:16px 0;
    padding:18px !important;
}

.helios-live-panel-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    margin-bottom:14px;
}

.helios-live-panel-head strong{
    color:#fff;
    font-size:15px;
    font-weight:860;
}

.helios-live-timeline{
    display:grid;
    gap:12px;
}

.helios-live-turn{
    display:grid;
    grid-template-columns:74px 90px minmax(0,1fr);
    gap:12px;
    align-items:start;
    padding:14px;
    border-radius:14px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.10);
}

.helios-live-turn span{
    color:#9a8f8b;
    font-size:12px;
    font-weight:780;
}

.helios-live-turn strong{
    color:#fff;
    font-size:14px;
    font-weight:860;
}

.helios-live-turn p{
    margin:0 !important;
    color:#d8d0cc !important;
    font-size:15px !important;
    line-height:1.5 !important;
}

.helios-context-files{
    display:flex;
    flex-wrap:wrap;
    gap:9px;
}

.helios-context-files em{
    min-height:32px;
    display:inline-flex;
    align-items:center;
    padding:0 11px;
    border-radius:999px;
    color:#f7eeee;
    background:rgba(255,255,255,.065);
    border:1px solid rgba(255,255,255,.12);
    font-size:12px;
    font-style:normal;
    font-weight:780;
}

.helios-live-backend-note{
    margin:12px 0 18px;
    padding:16px 18px !important;
    border-color:rgba(86,156,255,.20) !important;
}

.helios-live-backend-note strong{
    display:block;
    margin:5px 0;
    color:#fff;
    font-size:16px;
    font-weight:860;
}

.helios-live-backend-note p{
    margin:0 !important;
    color:#aaa09c !important;
    font-size:14px !important;
    line-height:1.5 !important;
}

.helios-voice-launch{
    min-height:520px;
    display:grid;
    grid-template-columns:minmax(180px,300px) minmax(0,560px);
    align-items:center;
    justify-content:center;
    gap:42px;
    padding:40px !important;
    margin:18px 0;
    background:
        radial-gradient(circle at 35% 50%,rgba(67,221,201,.10),transparent 34%),
        linear-gradient(180deg,rgba(255,255,255,.04),transparent 58%),
        rgba(7,9,13,.94) !important;
    border-color:rgba(67,221,201,.18) !important;
}

.helios-voice-launch-orb{
    position:relative;
    width:min(280px,52vw);
    aspect-ratio:1;
    border-radius:50%;
    background:conic-gradient(from 180deg,#43ddc9,#64a8ff,#ff5c7a,#f7c764,#43ddc9);
    box-shadow:0 36px 100px rgba(0,0,0,.45),0 0 90px rgba(67,221,201,.12);
}

.helios-voice-launch-orb:before{
    content:"";
    position:absolute;
    inset:20px;
    border-radius:50%;
    background:#05070a;
    border:1px solid rgba(255,255,255,.08);
}

.helios-voice-launch-orb span{
    position:absolute;
    inset:50%;
    width:24px;
    height:24px;
    transform:translate(-50%,-50%);
    border-radius:50%;
    background:#43ddc9;
    box-shadow:0 0 0 18px rgba(67,221,201,.11),0 0 54px rgba(67,221,201,.65);
}

.helios-voice-launch span{
    display:block;
    color:#9a8f8b;
    font-size:11px;
    font-weight:850;
    text-transform:uppercase;
}

.helios-voice-launch strong{
    display:block;
    margin:8px 0 12px;
    color:#fff;
    font-size:clamp(38px,5vw,72px);
    font-weight:900;
    line-height:.92;
}

.helios-voice-launch p{
    max-width:520px;
    margin:0 0 22px !important;
    color:#d0c8c4 !important;
    font-size:17px !important;
    line-height:1.5 !important;
}

.helios-voice-launch a{
    min-height:48px;
    display:inline-flex;
    align-items:center;
    padding:0 18px;
    border-radius:999px;
    color:#061014;
    background:#43ddc9;
    font-size:15px;
    font-weight:880;
    text-decoration:none;
}

.ai-response-grid{
    display:grid;
    grid-template-columns:minmax(0,1fr) minmax(240px,320px);
    gap:14px;
}

.helios-user-message{
    max-width:920px;
    margin:18px 0 10px auto;
    padding:16px 18px !important;
    border-color:rgba(255,101,104,.26) !important;
    background:
        linear-gradient(135deg,rgba(255,101,104,.18),rgba(255,255,255,.028)),
        rgba(26,21,21,.88) !important;
}

.helios-user-message-header{
    display:grid;
    grid-template-columns:38px minmax(0,1fr);
    align-items:center;
    gap:11px;
    margin-bottom:12px;
}

.helios-user-avatar{
    width:38px;
    height:38px;
    display:grid;
    place-items:center;
    border-radius:12px;
    color:#fff;
    font-size:15px;
    font-weight:900;
    background:linear-gradient(135deg,#fff,#ff6568);
    border:1px solid rgba(255,255,255,.18);
    box-shadow:0 14px 28px rgba(255,101,104,.18);
}

.helios-user-message-header strong,
.helios-user-message-header span{
    display:block;
}

.helios-user-message-header strong{
    color:#fff;
    font-size:16px;
    font-weight:880;
    line-height:1.15;
}

.helios-user-message-header span{
    margin-top:4px;
    color:#aaa09c;
    font-size:12px;
    font-weight:760;
    line-height:1.25;
}

.helios-user-message-body{
    color:#f4eeee;
    font-size:15px;
    line-height:1.62;
    overflow-wrap:anywhere;
}

.helios-assistant-message{
    max-width:760px;
    margin:12px auto 16px 0;
    padding:16px 18px !important;
}

.helios-assistant-message-header{
    display:grid;
    grid-template-columns:42px minmax(0,1fr);
    align-items:center;
    gap:12px;
    margin-bottom:12px;
}

.helios-assistant-message-header strong,
.helios-assistant-message-header span{
    display:block;
}

.helios-assistant-message-header strong{
    color:#fff;
    font-size:17px;
    font-weight:880;
    line-height:1.15;
}

.helios-assistant-message-header span{
    margin-top:4px;
    color:#aaa09c;
    font-size:12px;
    font-weight:760;
    line-height:1.25;
}

.helios-assistant-message-body{
    color:#e8e3e0;
    font-size:15px;
    line-height:1.62;
    overflow-wrap:anywhere;
}

.ai-response-card{
    margin:18px 0 16px;
    padding:18px !important;
}

.ai-card-header{
    display:grid;
    grid-template-columns:42px minmax(0,1fr) auto;
    align-items:center;
    gap:12px;
    margin-bottom:14px;
}

.ai-avatar{
    width:42px;
    height:42px;
    display:grid;
    place-items:center;
    border-radius:14px;
    color:#fff;
    font-size:18px;
    font-weight:900;
    background:linear-gradient(135deg,#ff6568,#8b1a1e);
    border:1px solid rgba(255,255,255,.18);
    box-shadow:0 16px 34px rgba(255,101,104,.18);
}

.ai-card-header strong,
.ai-card-header span{
    display:block;
}

.ai-card-header strong{
    color:#fff;
    font-size:18px;
    font-weight:880;
    line-height:1.12;
}

.ai-card-header span{
    margin-top:4px;
    color:#aaa09c;
    font-size:12px;
    font-weight:760;
    line-height:1.25;
}

.ai-card-header em{
    min-height:32px;
    font-style:normal;
    font-size:12px;
    font-weight:840;
}

.ai-response-grid section,
.ai-response-grid aside{
    padding:18px !important;
    border-radius:16px;
}

.ai-response-grid section > span,
.ai-response-grid aside > span{
    display:block;
    margin-bottom:10px;
    color:#fff;
    font-size:17px;
    font-weight:860;
    line-height:1.2;
}

.ai-response-body{
    color:#e8e3e0;
    line-height:1.72;
    font-size:15px;
    overflow-wrap:anywhere;
    white-space:normal;
}

.ai-response-body br{
    display:block;
    content:"";
    margin:8px 0;
}

.ai-response-grid aside strong{
    display:block;
    margin:0 0 10px;
    color:#fff;
    font-size:15px;
    line-height:1.35;
}

.ai-response-grid aside p{
    margin:0 !important;
    color:#aaa09c !important;
    font-size:14px !important;
    line-height:1.55 !important;
}

.ai-action-list{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-top:18px;
}

.ai-action-list em{
    min-height:30px;
    display:inline-flex;
    align-items:center;
    padding:0 11px;
    border-radius:999px;
    color:#fff0f0;
    font-size:12px;
    font-style:normal;
    font-weight:780;
    background:rgba(255,101,104,.10);
    border:1px solid rgba(255,101,104,.22);
}

.helios-system-notice{
    margin:14px 0;
    padding:14px 16px;
}

.notice-warning{
    background:rgba(255,197,109,.08) !important;
    border-color:rgba(255,197,109,.34) !important;
}

.notice-error{
    background:rgba(255,101,104,.08) !important;
    border-color:rgba(255,101,104,.34) !important;
}

.notice-success{
    background:rgba(131,226,161,.08) !important;
    border-color:rgba(131,226,161,.34) !important;
}

/* Bottom command input */
div[data-testid="stBottomBlockContainer"]{
    position:fixed !important;
    left:326px !important;
    right:28px !important;
    bottom:18px !important;
    z-index:999998 !important;
    width:auto !important;
    min-height:auto !important;
    padding:0 !important;
    background:transparent !important;
    pointer-events:none !important;
}

[data-testid="stChatInput"]{
    position:relative !important;
    width:min(100%,1320px) !important;
    min-height:72px !important;
    margin:0 auto !important;
    padding:10px 12px !important;
    border-radius:22px !important;
    background:
        radial-gradient(circle at 8% 0%,rgba(255,101,104,.18),transparent 34%),
        linear-gradient(135deg,rgba(44,18,22,.96),rgba(13,10,12,.97) 68%),
        rgba(16,11,13,.98) !important;
    border:1px solid rgba(255,101,104,.40) !important;
    box-shadow:
        0 26px 80px rgba(0,0,0,.62),
        0 0 0 1px rgba(255,255,255,.055) inset,
        0 0 42px rgba(255,101,104,.10) !important;
    pointer-events:auto !important;
    overflow:hidden !important;
    backdrop-filter:blur(22px) saturate(1.25);
}

[data-testid="stChatInput"]:after{
    content:"";
    position:absolute;
    pointer-events:none;
}

[data-testid="stChatInput"]:after{
    inset:0;
    border-radius:inherit;
    background:
        linear-gradient(90deg,rgba(255,101,104,.28),transparent 22%,transparent 78%,rgba(255,101,104,.18)) top left/100% 1px no-repeat;
    opacity:.9;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div{
    background:transparent !important;
    border-color:transparent !important;
    box-shadow:none !important;
}

[data-testid="stChatInput"] textarea{
    min-height:46px !important;
    padding:10px 58px 8px 54px !important;
    color:#fff !important;
    font-size:16px !important;
    line-height:1.45 !important;
    font-weight:650 !important;
    caret-color:#ff6568 !important;
}

[data-testid="stChatInput"] textarea::placeholder{
    color:#bfb4b1 !important;
}

[data-testid="stChatInput"] button{
    width:42px !important;
    height:42px !important;
    border-radius:999px !important;
    color:#fff !important;
    background:
        linear-gradient(135deg,rgba(255,101,104,.92),rgba(139,26,30,.82)) !important;
    border:1px solid rgba(255,255,255,.18) !important;
    box-shadow:0 14px 34px rgba(255,101,104,.22) !important;
    transition:transform .16s ease, box-shadow .16s ease, background .16s ease !important;
}

[data-testid="stChatInput"] button:hover{
    transform:translateY(-1px);
    box-shadow:0 18px 44px rgba(255,101,104,.32) !important;
}

[data-testid="stChatInput"] button:first-of-type{
    background:
        radial-gradient(circle at 50% 42%,rgba(255,255,255,.16),transparent 30%),
        rgba(255,255,255,.055) !important;
    border-color:rgba(255,255,255,.14) !important;
    box-shadow:0 10px 28px rgba(0,0,0,.28) !important;
}

[data-testid="stChatInput"] button:first-of-type:hover{
    background:rgba(255,101,104,.18) !important;
    border-color:rgba(255,101,104,.34) !important;
}

[data-testid="stChatInput"] button:last-of-type{
    background:
        linear-gradient(135deg,rgba(255,101,104,.92),rgba(139,26,30,.82)) !important;
    border-color:rgba(255,255,255,.18) !important;
    box-shadow:0 14px 34px rgba(255,101,104,.22) !important;
}

pre{white-space:pre-wrap !important;overflow-x:auto !important}
code{color:#ffd2d4 !important}

::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{border-radius:999px;background:rgba(255,255,255,.18)}

@keyframes helios-rise{
    from{opacity:0;transform:translateY(10px) scale(.992)}
    to{opacity:1;transform:translateY(0) scale(1)}
}

@keyframes helios-orbit{
    from{filter:hue-rotate(0deg);transform:rotate(0deg)}
    to{filter:hue-rotate(8deg);transform:rotate(360deg)}
}

@keyframes helios-bar{
    0%,100%{height:11px;opacity:.55}
    50%{height:28px;opacity:1}
}

@keyframes helios-node-pulse{
    0%,100%{
        transform:scale(1);
        box-shadow:
            0 0 0 7px rgba(255,92,122,.10),
            0 0 22px rgba(255,92,122,.78);
    }
    50%{
        transform:scale(1.18);
        box-shadow:
            0 0 0 12px rgba(255,92,122,.06),
            0 0 34px rgba(255,92,122,.98);
    }
}

@media (prefers-reduced-motion:reduce){
    *,*:before,*:after{
        animation:none !important;
        transition:none !important;
    }
}

@media (max-width:1180px){
    .block-container{padding:22px 22px 124px !important}
    .helios-status-strip{grid-template-columns:repeat(3,minmax(0,1fr))}
    .helios-platform-chrome,
    .helios-agent-presence{grid-template-columns:1fr}
    .helios-platform-signals{grid-template-columns:repeat(3,minmax(0,1fr))}
    .helios-command-metrics,
    .helios-lane-grid,
    .helios-agent-grid,
    .helios-mission-review-grid,
    .helios-mission-memory-rail,
    .helios-mission-template-grid,
    .helios-mission-archive-grid,
    .helios-mission-step-grid,
    .helios-mode-contract-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
    .helios-mission-grid,
    .helios-mission-control-hero,
    .ai-response-grid{grid-template-columns:1fr}
    .helios-thinking-top{
        align-items:flex-start;
        flex-direction:column;
    }
    .helios-thinking-top strong{
        white-space:normal;
    }
    .helios-bridge-copy h1{font-size:40px !important}
}

@media (max-width:860px){
    .block-container{padding:16px 14px 118px !important}
    .helios-command-bridge{grid-template-columns:1fr;min-height:auto;padding:20px}
    .helios-bridge-status{grid-template-columns:repeat(3,minmax(72px,1fr));justify-content:flex-start;margin-top:18px;margin-left:0}
    .helios-command-card,
    .helios-reactor-shell,
    .helios-voice-cockpit,
    .helios-thinking-card,
    .helios-status-strip,
    .helios-platform-signals,
    .helios-presence-grid,
    .helios-mission-control-metrics,
    .helios-mission-step-grid,
    .helios-mission-council-grid,
    .helios-mission-review-grid,
    .helios-mission-review-meta,
    .helios-mission-memory-rail,
    .helios-mission-template-grid,
    .helios-risk-radar-grid,
    .helios-next-action-grid,
    .helios-mission-archive-grid,
    .helios-mission-artifact-grid,
    .helios-command-metrics,
    .helios-mode-contract-grid,
    .helios-lane-grid,
    .helios-agent-grid,
    .helios-system-snapshot{grid-template-columns:1fr}
    .helios-command-card-aside{align-items:flex-start}
    .helios-reactor-pills,
    .helios-mission-badges{justify-content:flex-start}
    .helios-thinking-card{
        grid-template-columns:1fr;
        padding:18px !important;
    }
    .helios-thinking-orb{
        width:42px;
        height:42px;
    }
    .helios-mission-memory-rail:before{display:none}
    .helios-agent-network-map{
        min-height:auto;
        display:grid;
        grid-template-columns:1fr;
        gap:10px;
        padding:12px;
    }
    .helios-agent-network-map:before,
    .helios-agent-network-map:after{display:none}
    .helios-agent-network-core,
    .helios-agent-network-map article{
        position:relative;
        inset:auto !important;
        left:auto !important;
        right:auto !important;
        top:auto !important;
        bottom:auto !important;
        width:auto;
        min-height:76px;
        transform:none !important;
    }
    div[data-testid="stFileUploader"] section{
        grid-template-columns:1fr !important;
        min-height:116px !important;
        gap:12px !important;
    }
    div[data-testid="stFileUploader"] button{
        width:100% !important;
        max-width:none !important;
    }
    div[data-testid="stFileUploader"] section:after{
        white-space:normal;
    }
    div[data-testid="stBottomBlockContainer"]{padding:10px 14px 16px !important}
}

/* Scroll and browser-tab stability overrides */
html,
body,
.stApp,
div[data-testid="stAppViewContainer"],
section[data-testid="stMain"],
div[data-testid="stMainBlockContainer"],
.main{
    height:auto !important;
    min-height:100vh !important;
    max-height:none !important;
    overflow-y:visible !important;
}

body{
    overflow-y:auto !important;
}

.block-container{
    min-height:100vh !important;
    padding-bottom:340px !important;
}

.block-container:after{
    content:"";
    display:block;
    height:180px;
    pointer-events:none;
}

div[data-testid="stBottomBlockContainer"]{
    z-index:999998 !important;
}

@media (max-width:1180px){
    div[data-testid="stBottomBlockContainer"]{
        left:104px !important;
        right:18px !important;
        bottom:14px !important;
        padding:0 !important;
    }
    .helios-live-hero{
        grid-template-columns:220px minmax(0,1fr);
    }
    .helios-live-status{
        grid-column:1 / -1;
        grid-template-columns:repeat(4,minmax(0,1fr));
    }
    .ai-response-grid{
        grid-template-columns:1fr;
    }
}

@media (max-width:860px){
    div[data-testid="stBottomBlockContainer"]{
        left:14px !important;
        right:14px !important;
        bottom:12px !important;
        padding:0 !important;
    }
    [data-testid="stChatInput"]{
        min-height:64px !important;
        border-radius:18px !important;
    }
    [data-testid="stChatInput"] textarea{
        min-height:40px !important;
        padding-left:48px !important;
        font-size:15px !important;
    }
    .ai-card-header{
        grid-template-columns:38px minmax(0,1fr);
    }
    .ai-card-header em{
        grid-column:1 / -1;
        justify-self:start;
    }
    .helios-live-hero{
        grid-template-columns:1fr;
        padding:20px !important;
    }
    .helios-live-orb{
        width:min(64vw,220px);
        min-width:168px;
    }
    .helios-live-status,
    .helios-live-turn{
        grid-template-columns:1fr;
    }
    .helios-live-copy strong{
        font-size:34px;
    }
    .helios-live-copy p{
        font-size:15px !important;
    }
}

.helios-mission-memory,
.helios-mission-archive{
    scroll-margin-top:24px;
    scroll-margin-bottom:180px;
}

</style>
"""
