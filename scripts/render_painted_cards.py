#!/usr/bin/env python3
"""Paint rich project cards from the original approved illustration crops.

All counts are obtained from the live, verified GitHub REST payload. Decorative
reference artwork is static and never gets mistaken for performance data.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
IMG_W, IMG_H = 720, 695
INK = '#503827'
MUTED = '#7E6959'
BORDER = '#E7C6A4'
CREAM = '#FFF4E3'

CARD_CONTENT = {
    'rag-sec-10k': ('sec', 'SEC Insight AI', 'Grounded research over SEC 10-K filings', 'Hybrid retrieval  ·  Citations  ·  Evaluation', 'RAG', '#D6EAC8'),
    'RivalScope-AI': ('rivalscope', 'RivalScope AI', 'Evidence-backed competitive intelligence', 'Multi-track research  ·  Live traces', 'Research', '#D9D8F0'),
    'GlitchVision---Visual-Anomaly-Detection-for-Game-QA': ('glitchvision', 'GlitchVision', 'Spot suspicious moments in gameplay footage', 'ResNet-18  ·  Isolation Forest  ·  kNN', 'Game QA', '#CFEBEB'),
    'Nova-Learn': ('novalearn', 'NovaLearn', 'Connected learning and authentic assessment', 'Course graphs  ·  Student evidence', 'Education', '#EFD5E0'),
    'PACT---Protocol-for-Agentic-Commit-Transactions': ('pact', 'PACT', 'Safer multi-agent transactions and recovery', 'Commit gates  ·  Verification  ·  Receipts', 'Ongoing', '#F7DEB4'),
}


def font(sz, bold=False):
    name = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(name, sz)


def fit(draw, s, max_width, initial, bold=False, minimum=19):
    size=initial
    while size>=minimum and draw.textbbox((0,0),s,font=font(size,bold))[2]>max_width:
        size-=1
    if size < minimum:
        raise ValueError(f'Cannot fit text: {s}')
    return font(size,bold)


def draw_card(slug, github_repo=None):
    name, title, description, detail, category, accent = CARD_CONTENT[slug]
    source=ASSETS/f'art-{name}.jpg'
    if not source.is_file():
        raise FileNotFoundError(source)
    pic=Image.open(source).convert('RGB').resize((682,282),Image.Resampling.LANCZOS)
    card=Image.new('RGB',(IMG_W,IMG_H),'#FFF3DF')
    d=ImageDraw.Draw(card)
    d.rounded_rectangle((2,2,IMG_W-3,IMG_H-3),radius=26,fill=CREAM,outline=BORDER,width=5)
    mask=Image.new('L',pic.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,pic.width-1,pic.height-1),radius=19,fill=255)
    card.paste(pic,(19,18),mask)
    d=ImageDraw.Draw(card)
    d.rounded_rectangle((24,330,696,404),radius=16,fill='#FFF9EF')
    d.text((41,345),title,fill=INK,font=fit(d,title,620,43,True))
    d.text((39,432),description,fill=INK,font=fit(d,description,645,28,True))
    d.text((39,478),detail,fill=MUTED,font=fit(d,detail,643,24,False))
    d.rounded_rectangle((36,530,245,578),radius=17,fill=accent)
    d.text((55,540),category.upper(),fill='#436D50',font=fit(d,category.upper(),180,21,True))
    d.line((36,597,684,597),fill='#E5CBB1',width=3)
    if github_repo is None:
        metrics='GitHub repository stats pending verified update'
    else:
        stars=int(github_repo['stargazers_count'])
        forks=int(github_repo['forks_count'])
        metrics=f'{stars:,} stars    ·    {forks:,} forks'
    d.text((40,622),metrics,fill='#507C5B',font=fit(d,metrics,640,24,True))
    out=ASSETS/f'card-{name}.png'
    out.parent.mkdir(parents=True,exist_ok=True)
    card.save(out,optimize=True)
    return out


def draw_all(projects, data):
    for p in projects:
        slug=p['slug']
        if slug not in CARD_CONTENT:
            raise ValueError('Unknown project '+slug)
        repo=None if data is None else data['chosen'][slug]
        out=draw_card(slug,repo)
        print('painted',out, out.stat().st_size)


if __name__=='__main__':
    from types import SimpleNamespace
    ASSETS.mkdir(exist_ok=True)
    draw_all([{'slug':s} for s in CARD_CONTENT],None)