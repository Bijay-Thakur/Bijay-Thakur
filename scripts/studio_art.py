#!/usr/bin/env python3
"""Cozy Studio v2 artwork. Metrics only come from the verified GitHub payload."""
from __future__ import annotations

import calendar
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from math import sin
import random

ASSETS = Path(__file__).resolve().parents[1] / "assets"
INK="#593E30"; MUTED="#8C7162"; CREAM="#FFF8EA"; PAPER="#FBF0DA"
AMBER="#C5784D"; SAGE="#7FA76A"; MOSS="#3F7953"; BORDER="#E6CBA8"
FONT="Trebuchet MS,Segoe UI,Verdana,sans-serif"
random.seed(48)

def tag(w,h,body,name):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(name,quote=True)}">'
       '<defs>'
       '<linearGradient id="paper" x2="1" y2="1"><stop stop-color="#FFF8E8"/><stop offset="1" stop-color="#FAE4C9"/></linearGradient>'
       '<linearGradient id="dusk" x2="0" y2="1"><stop stop-color="#F7D4B9"/><stop offset=".55" stop-color="#FFE6A8"/><stop offset="1" stop-color="#B4D7AE"/></linearGradient>'
       '<linearGradient id="mount" x2="0" y2="1"><stop stop-color="#B7C8C9"/><stop offset="1" stop-color="#7B9B8A"/></linearGradient>'
       '<linearGradient id="purple" x2="0" y2="1"><stop stop-color="#E3B7DA"/><stop offset="1" stop-color="#8193CF"/></linearGradient>'
       '<linearGradient id="forest" x2="0" y2="1"><stop stop-color="#B1CE83"/><stop offset="1" stop-color="#4D875A"/></linearGradient>'
       '<linearGradient id="shadow" x2="0" y2="1"><stop stop-color="#F3CFA5"/><stop offset="1" stop-color="#E9C8B2"/></linearGradient>'
       '</defs>'+body+'</svg>')

def rect(x,y,w,h,fill,rx=15,stroke=None,stroke_w=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{stroke_w}"' if stroke else '')+'/>'

def path(d,fill="none",stroke=None,sw=2,extra=""):
    return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+f' {extra}/>'

def circle(cx,cy,r,fill,stroke=None,sw=2):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'

def t(x,y,s,size=24,color=INK,weight=500,anchor=None):
    att=f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" font-weight="{weight}" font-size="{size}"{att}>{escape(str(s))}</text>'

def shell(w,h,title=None):
    b=rect(2,2,w-4,h-4,"url(#paper)",25,BORDER,3)
    if title:b+=t(38,55,title,35,INK,800)
    return b

def petal(x,y,col="#DE9857",size=1):
    p=f'<g transform="translate({x} {y}) scale({size})">'
    for dx,dy in [(0,-10),(10,0),(0,10),(-10,0)]:
        p+=f'<ellipse cx="{dx}" cy="{dy}" rx="7" ry="11" fill="{col}" opacity=".9"/>'
    return p+circle(0,0,5,"#F4D768")+'</g>'

def foliage(w,h):
    a=path(f"M0 {h-61} Q{w//4} {h-90} {w//2} {h-54} Q{w*3//4} {h-110} {w} {h-58} V{h} H0Z","#D2E3A5")
    a+=path(f"M0 {h-23} Q{w//3} {h-62} {w//2} {h-29} Q{w*4//5} {h-61} {w} {h-20} V{h} H0Z","#91B977")
    for x in range(16,w,34):
        height=5+int(8*abs(sin(x*.1)))
        a+=path(f"M{x} {h-14} l-6 -{height} m6 {height} l5 -{height+3}",stroke="#4D865B",sw=2)
    for x,y,s,c in [(20,h-53,1,"#EE9779"),(64,h-37,.7,"#DE7899"),(w-42,h-47,1,"#E2A455"),(w-79,h-32,.75,"#F1A18D")]:
        a+=petal(x,y,c,s)
    return a

def butterfly(x,y):
    return f'<g transform="translate({x} {y})">'+path("M0 0 Q-28 -28 -38 -3 Q-34 20 0 5 Q34 20 38 -3 Q28 -28 0 0","#EEB048", "#C8794F",2)+path("M0 0 V15",stroke="#543D37",sw=3)+'</g>'

def garden(data):
    w,h=1500,380
    b=shell(w,h,"Contribution Garden")
    b+=t(38,91,"Real GitHub contribution days • rolling year",19,MUTED)
    b+=circle(w-110,77,43,"#FFE8A9")+butterfly(w-240,62)
    b+=foliage(w,h)
    if data:
        days=data["days"]
        weeks={}
        for d in days:
            dt=datetime.fromisoformat(d["date"])
            sunday=(dt.weekday()+1)%7
            wk=dt.toordinal()-sunday
            weeks.setdefault(wk,[]).append((sunday,int(d["contributionCount"])))
        columns=sorted(weeks.items())[-53:]
        m=max([int(d["contributionCount"]) for d in days] or [0]) or 1
        shades=["#ECE9D5","#D9E9B0","#B9D987","#8FBC67","#5E9C55","#2E744A"]
        bw=min(20,1270/len(columns)-4)
        sp=bw+4
        sx=110+(1270-sp*len(columns))/2
        for i,(_,week) in enumerate(columns):
            for day,count in week:
                shade=0 if count==0 else min(5,1+int(4*(count/m)**.55))
                b+=rect(round(sx+i*sp,1),140+day*22,round(bw,1),17,shades[shade],4)
        b+=t(1200,55,f"{int(data['total']):,} contributions",24,MOSS,800)
    else:
        b+=t(1120,54,"Awaiting GitHub API",22,MOSS,800)
        for i in range(53):
            for day in range(7):
                b+=rect(95+i*24,140+day*22,19,17,"#DFE6C8",4)
    b+=t(37,336,"Every square is one day. Darker green = more contributions.",18,INK,600)
    b+=t(w-36,341,"Source: GitHub GraphQL • updated every 30 min",17,MUTED,500,"end")
    return tag(w,h,b,"Real-time refreshed GitHub contribution calendar")

def hiker(x,y):
    a=circle(x,y-50,19,"#C88757")
    a+=path(f"M{x-19} {y-62} q20 -26 37 -3",stroke="#443A36",sw=14)
    a+=rect(x-16,y-29,36,50,"#414F61",12)
    a+=rect(x-41,y-21,31,43,"#C9824C",10,INK,2)
    a+=path(f"M{x-7} {y+19} l-14 45 m35 -44 l20 42",stroke="#424653",sw=12)
    a+=path(f"M{x-3} {y-9} l36 20",stroke="#B17E5D",sw=8)
    return a

def clouds(w):
    a=""
    for x,y,s in [(60,115,1),(430,80,.75),(900,100,1.1),(1270,77,.7)]:
        a+=f'<g transform="translate({x} {y}) scale({s})" opacity=".73">'+circle(0,0,28,"#FFF8EF")+circle(27,-12,34,"#FFF8EF")+circle(56,0,27,"#FFF8EF")+'</g>'
    return a

def mountains(w,h,base):
    b=""
    for x,y,scale in [(160,120,1.05),(525,93,1.4),(940,122,1.05),(1300,130,1.18)]:
        a=x-170*scale; c=x+170*scale
        b+=path(f"M{a:.1f} {base} L{x} {y} L{c:.1f} {base}Z","url(#mount)")
        b+=path(f"M{x-28*scale:.1f} {y+42} L{x} {y} L{x+32*scale:.1f} {y+46} L{x+11*scale:.1f} {y+38} L{x-7*scale:.1f} {y+18}Z","#FFF3E8")
    b+=path(f"M0 {base-15} Q200 {base-80} 400 {base-24} Q750 {base-84} 960 {base-21} Q1220 {base-75} {w} {base-20} V{h} H0Z","#AFCB9B")
    return b

def journey():
    w,h=1500,390
    b=shell(w,h)+rect(13,13,w-26,h-26,"url(#dusk)",20)
    b+=circle(w-210,110,68,"#FFE4A2")+clouds(w)+mountains(w,h,282)
    b+=path("M10 321 Q300 239 635 307 Q880 354 1190 260 Q1360 236 1500 281 V390 H10Z","#98BF7E")
    b+=path("M278 315 Q490 279 648 327 Q826 385 1102 307 Q1270 260 1486 294",stroke="#D5A86C",sw=42)
    b+=path("M278 315 Q490 279 648 327 Q826 385 1102 307 Q1270 260 1486 294",stroke="#FFF1BF",sw=30)
    b+=hiker(114,271)
    b+=t(38,58,"AI Engineering Journey",36,INK,800)
    b+=t(39,89,"From curious ideas to reliable, measured AI systems",21,MUTED,600)
    names=["Learn & Explore","Build","Evaluate","Improve","Deploy"]
    icons=["01","02","03","04","05"]
    for i,(name,num) in enumerate(zip(names,icons)):
        x=355+i*225
        y=167-(8 if i%2 else 0)
        b+=path(f"M{x+64} {y+75} V{316-(i%2)*14}",stroke="#916D4C",sw=7)
        b+=rect(x-24,y,175,71,"#FFF5DC",17,"#C38F64",3)
        b+=circle(x+2,y+35,19,"#F7D7A5")
        b+=t(x+2,y+41,num,17,INK,800,"middle")
        if name=="Learn & Explore":
            b+=t(x+48,y+28,"Learn &",20,INK,800)+t(x+48,y+52,"Explore",20,INK,800)
        else:b+=t(x+41,y+46,name,20,INK,800)
    b+=petal(600,361,"#DCA876",.75)+petal(1380,357,"#EE967B",.7)
    b+=path("M1455 217 l0 -70 l51 14 l-51 19Z","#C7694A")
    return tag(w,h,b,"AI engineering journey illustrated mountain road")

def stat_panel(data,project_count):
    w,h=1500,245
    b=shell(w,h,"At a Glance")
    if data:
        r=data["repos"]
        numbers=[f"{int(data['total']):,}",str(len(r)),str(sum(int(x.get("stargazers_count",0)) for x in r)),str(project_count)]
    else:numbers=["—"]*4
    labels=["YEARLY CONTRIBUTIONS","PUBLIC REPOSITORIES","PUBLIC STARS","FEATURED PROJECTS"]
    colors=["#FBE1CB","#E6EECF","#F3D8E1","#DDEBEE"]
    for i,(num,lab,color) in enumerate(zip(numbers,labels,colors)):
        x=28+i*371
        b+=rect(x,74,345,135,color,19)
        b+=t(x+20,135,num,47,INK,800)
        b+=t(x+20,172,lab,18,MOSS,800)
    b+=t(1470,54,"Verified GitHub API data",19,MUTED,500,"end")
    return tag(w,h,b,"Verified GitHub contribution and public repository statistics")

def toolbox():
    w,h=1500,170
    b=shell(w,h)+t(37,57,"Tech Stack / Toolbox",34,INK,800)
    names=["Python","PyTorch","OpenAI","LangGraph","FastAPI","Next.js","TypeScript","Supabase","Docker","GitHub"]
    col=["#FFE1B9","#F5D1BD","#D9E6D3","#EEDCCC","#BEE4D7","#D9D6ED","#DBE7EE","#CEE1CC","#DBE8F1","#E9DCCF"]
    for i,(label,color) in enumerate(zip(names,col)):
        x=24+i*147
        b+=rect(x,83,136,63,color,14,"#E8D3B9",1)
        b+=t(x+68,123,label,19,INK,750,"middle")
    return tag(w,h,b,"Technical toolbox")

def flower_vines(w):
    a=path("M0 0 Q65 25 145 0 M0 0 Q-5 80 36 116",stroke="#6E915F",sw=9)
    for x,y,s in [(23,28,1.05),(62,15,.9),(105,10,.75),(22,84,.85)]:
        a+=f'<ellipse cx="{x}" cy="{y}" rx="{12*s}" ry="{28*s}" fill="#76A265" transform="rotate(-25 {x} {y})"/>'
    return a

def scene(kind):
    w,h=380,210
    b=rect(0,0,w,h,"url(#dusk)",14)
    b+=circle(316,48,43,"#FFEBAA")
    b+=path("M0 156 Q100 104 215 156 Q300 118 380 158 V210 H0Z","#A4BE8E")
    b+=flower_vines(w)
    if kind=="sec":
        b+=path("M36 112 L156 45 L275 112Z","#FFF6E0","#96704D",3)
        b+=rect(48,114,215,15,"#BD996F",2)
        for x in [64,108,152,196,240]:b+=rect(x,129,19,62,"#FBF3DE",2,"#9A805E",2)
        b+=rect(43,183,225,14,"#C2A07E",2)
        b+=rect(215,129,127,82,"#FFF7E7",5,"#A28461",2)
        b+=t(235,166,"10-K",30,"#8C6248",800)
        b+=path("M228 179 H332",stroke="#CBB498",sw=3)
    elif kind=="rival":
        for x,hgt in [(56,60),(100,90),(150,110),(218,78),(278,132)]:
            b+=rect(x,202-hgt,38,hgt,"#8096A9",3)
            for y in range(203-hgt+16,196,23):
                b+=rect(x+9,y,7,8,"#FFE7A6",2)
        b+=rect(125,58,202,125,"#374E63",10,"#E8C49A",5)
        b+=path("M150 145 L188 124 L231 138 L267 88 L301 105",stroke="#F6CD71",sw=6)
        b+=circle(100,136,42,"#D5E6D4","#465B60",12)
        b+=path("M128 169 L161 200",stroke="#465B60",sw=15)
    elif kind=="game":
        b+=path("M40 210 L145 58 L265 58 L371 210Z","#777D8A")
        for x in [105,200,290]:b+=path(f"M{x} 210 L{200+(x-200)*.24} 60",stroke="#FFE2AC",sw=5,extra='stroke-dasharray="16 18"')
        for x,y in [(105,118),(292,150),(241,80)]:
            b+=circle(x,y,12,"#FFE572","#C88735",3)
        # Runner (red hoodie, legs and arms, chasing an on-screen visual glitch)
        b+=circle(192,100,19,"#9A583C")
        b+=rect(177,118,32,48,"#BD4C38",11)
        b+=path("M179 159 l-24 39 m46 -39 l29 40",stroke="#344F77",sw=11)
        b+=path("M181 128 l-20 21 m47 -21 l20 20",stroke="#A94B39",sw=9)
        b+=rect(274,111,78,62,"#F0B5C0",7,"#D64579",4)
        b+=rect(264,103,94,74,"none",5,"#FCE0F2",4)
        b+=path("M252 122 h-15 v18 m127 -32 h13 v19 m-122 47 h-14 v-17 m122 14 h15 v-17",stroke="#C62B72",sw=5)
        b+=t(321,151,"!",33,"#7E284B",800,"middle")
    elif kind=="learn":
        b+=rect(90,70,241,125,"#B88761",8)
        b+=rect(103,82,217,97,"#516C7E",7)
        b+=path("M155 121 l55 -28 l55 28 l-55 26Z","#F5D49A")
        b+=path("M265 121 v35",stroke="#F5D49A",sw=6)
        for x,y,col in [(34,151,"#EAB7A1"),(53,144,"#E5D3A2"),(70,159,"#B0C99B")]:
            b+=rect(x,y,29,52,col,2,"#AD8E72",1)
        b+=petal(320,56,"#EAA780",.65)
    elif kind=="pact":
        b=rect(0,0,w,h,"#373456",14)+circle(309,60,55,"#7663A2")
        for x,y in [(46,90),(329,91),(121,167),(295,176)]:
            b+=path(f"M{x} {y} L204 103",stroke="#9B8EDC",sw=3)
            b+=rect(x-15,y-15,30,30,"#E7B45F",5)
        b+=path("M145 51 l59 -25 l61 25 v70 l-61 31 l-59 -31Z","#C0A9E5","#F4D4B5",3)
        b+=path("M145 51 l59 26 l61 -26 M204 77 v75",stroke="#F8DFC8",sw=3)
        b+=path("M177 106 l22 20 l35 -42",stroke="#FFEBA9",sw=9)
    return b

def project_card(p,repo):
    w,h=410,465
    label=p["name"]
    key=p["art"]
    story={
        "sec":("SEC filings, grounded answers","Hybrid search · RAG"),
        "rival":("Evidence-backed competitor research","Agents · citations · traces"),
        "game":("Gameplay glitch detection","Visual anomaly triage"),
        "learn":("Learning graphs & assessments","Teaching · AI evidence"),
        "pact":("Reliable agent transactions","Validation · recovery"),
    }.get(key,("Applied AI engineering","Verified public repository"))
    b=shell(w,h)
    b+=rect(13,13,w-26,230,"#FCE7CD",17)
    b+=f'<g transform="translate(15 15)">{scene(key)}</g>'
    b+=t(21,284,label,29,INK,800)
    b+=t(21,321,story[0],22,INK,600)
    b+=t(21,348,story[1],20,MUTED,550)
    accent="#FCE5CE" if key!="pact" else "#E7D5EF"
    b+=rect(17,366,376,37,accent,12)
    b+=t(31,391,"ONGOING PROJECT" if key=="pact" else "PUBLIC REPOSITORY",17,MOSS,800)
    if repo is None:
        stats="Stars / forks: syncing with GitHub"
    else:
        stats=f"{int(repo.get('stargazers_count',0))} stars  ·  {int(repo.get('forks_count',0))} forks"
    b+=t(21,435,stats,21,INK,600)
    return tag(w,h,b,label+" illustrated project card with verified GitHub stats")

def button(label,symbol):
    w,h=290,74
    b=rect(2,2,w-4,h-4,"#80523E",18,"#D99A6A",3)
    b+=rect(8,8,w-16,h-16,"#975F47",14)
    b+=t(33,49,symbol,30,"#FFF4DA",800)
    b+=t(175,48,label,25,"#FFF4DA",800,"middle")
    return tag(w,h,b,label+" contact link")

def footer():
    w,h=1500,150
    b=rect(2,2,w-4,h-4,"url(#dusk)",22)
    b+=circle(745,74,42,"#F8D4A0")
    b+=path("M0 116 Q170 60 380 116 Q700 73 930 120 Q1220 60 1500 116 V150 H0Z","#A4B38C")
    b+=t(750,74,"From curious ideas to thoughtful AI products.",37,INK,700,"middle")
    b+=t(750,111,"Thanks for stopping by — there's always room for another builder at the table.",22,INK,500,"middle")
    return tag(w,h,b,"Warm sunset farewell illustration")

def save(name,src):
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS/name).write_text(src,encoding="utf-8")
    print("rendered",name)

def render_all(data,projects):
    save("contributions.svg",garden(data))
    save("ai-journey.svg",journey())
    save("overview.svg",stat_panel(data,len(projects)))
    save("toolbox-v2.svg",toolbox())
    save("footer-v2.svg",footer())
    for name,label,symbol in [
        ("portfolio","Portfolio","◈"),
        ("linkedin","LinkedIn","in"),
        ("email","Email","✉"),
    ]:save("link-"+name+".svg",button(label,symbol))
    for p in projects:
        repo=None if data is None else data["chosen"][p["slug"]]
        save(p["filename"],project_card(p,repo))
