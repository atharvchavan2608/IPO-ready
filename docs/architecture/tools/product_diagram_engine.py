from pathlib import Path
from dataclasses import dataclass
import math, html, json, textwrap, zipfile, sys
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path.cwd()
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'output/ipo-ready-architecture'
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'tmp').mkdir(exist_ok=True)
W,H=1700,1200
INK='#142B43'; MUTED='#52677C'; LINE='#B8C7D5'; BG='#F4F7FA'
BLUE='#2463AA'; TEAL='#117F82'; GOLD='#A36B12'; PURPLE='#7353A3'; RED='#B54C51'
PALE_BLUE='#EAF2FD'; PALE_TEAL='#E9F6F3'; PALE_GOLD='#FFF5DE'; PALE_PURPLE='#F1ECF8'; PALE_RED='#FCEEEF'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if Path(FONT).exists() and Path(BOLD).exists():
    pdfmetrics.registerFont(TTFont('D',FONT));pdfmetrics.registerFont(TTFont('DB',BOLD))
else:
    from reportlab.pdfbase.pdfmetrics import Font
    pdfmetrics.registerFont(Font('D','Helvetica','WinAnsiEncoding'))
    pdfmetrics.registerFont(Font('DB','Helvetica-Bold','WinAnsiEncoding'))

def wrap(s,width,size,bold=False):
    ans=[]
    for para in s.split('\n'):
        line=''
        for word in para.split(' '):
            test=(line+' '+word).strip()
            if pdfmetrics.stringWidth(test,'DB' if bold else 'D',size)>width and line:
                ans.append(line);line=word
            else:line=test
        ans.append(line)
    return ans

class Scene:
    def __init__(self,name,title,subtitle,num):
        self.name=name;self.items=[];self.boxes=[];self.num=num
        self.rect(0,0,W,H,'#FFFFFF',None,0)
        self.rect(0,0,W,10,TEAL,None,0)
        self.text(48,40,'IPO-READY  /  PRODUCT ARCHITECTURE',15,TEAL,True)
        self.text(48,75,title,33,INK,True)
        self.text(48,121,subtitle,16,MUTED)
        self.line([(48,163),(1652,163)],LINE,1)
        self.line([(48,1148),(1652,1148)],LINE,1)
        self.text(48,1165,'MBA (Business Analytics) | Programming Analytics Lab | Target product design | 29 Oct 2026',12,MUTED)
        self.text(1535,1165,f'{num:02d} / 07',12,MUTED,True)
    def rect(self,x,y,w,h,fill='#FFFFFF',stroke=LINE,r=12,dash=False):
        self.items.append(dict(kind='rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,r=r,dash=dash))
    def text(self,x,y,s,size=16,color=INK,bold=False):
        self.items.append(dict(kind='text',x=x,y=y,s=s,size=size,color=color,bold=bold))
    def para(self,x,y,s,width,size=16,color=MUTED,bold=False,leading=None):
        leading=leading or size*1.4
        lines=wrap(s,width,size,bold)
        for i,l in enumerate(lines):self.text(x,y+i*leading,l,size,color,bold)
        return y+len(lines)*leading
    def line(self,pts,color=LINE,width=2,dash=False,arrow=False,label=None,labelpos=None):
        self.items.append(dict(kind='line',pts=pts,color=color,width=width,dash=dash,arrow=arrow))
        if label:
            if labelpos is None:labelpos=((pts[0][0]+pts[-1][0])/2,(pts[0][1]+pts[-1][1])/2-19)
            lw=pdfmetrics.stringWidth(label,'D',12)+12
            self.rect(labelpos[0]-4,labelpos[1]-2,lw,18,'#FFFFFF',None,2)
            self.text(*labelpos,label,12,color)
    def arrow(self,pts,**kw):self.line(pts,arrow=True,**kw)
    def card(self,x,y,w,h,title,body='',accent=BLUE,fill='#FFFFFF',size=15,tag=None):
        self.rect(x,y,w,h,fill,accent,12)
        self.rect(x,y+15,4,h-30,accent,None,0)
        ty=y+19
        if tag:self.text(x+18,ty,tag,11,accent,True);ty+=21
        ts=17 if h<=150 else 19
        tl=22 if h<=150 else 24
        ty=self.para(x+18,ty,title,w-36,ts,INK,True,tl)+7
        if body:
            while len(wrap(body,w-36,size))*size*1.38>y+h-ty-12 and size>10.8:size-=.2
            assert len(wrap(body,w-36,size))*size*1.38<=y+h-ty-10,(title,size)
            self.para(x+18,ty,body,w-36,size,MUTED,False,size*1.38)
        self.boxes.append((x,y,w,h,title))
    def band(self,y,title,body,accent=TEAL,fill=PALE_TEAL,h=64):
        self.rect(48,y,1604,h,fill,None,10)
        self.text(66,y+14,title,15,accent,True)
        self.text(66,y+38,body,13,MUTED)
    def chip(self,x,y,label,color=BLUE,fill=PALE_BLUE):
        tw=pdfmetrics.stringWidth(label,'DB',12)+22
        self.rect(x,y,tw,26,fill,None,6);self.text(x+11,y+6,label,12,color,True)
        return tw

def svg(scene):
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>']
    for a in scene.items:
        if a['kind']=='rect':
            out.append(f'<rect x="{a["x"]}" y="{a["y"]}" width="{a["w"]}" height="{a["h"]}" rx="{a["r"]}" fill="{a["fill"] or "none"}" stroke="{a["stroke"] or "none"}" stroke-width="1.2"'+(' stroke-dasharray="6 5"' if a['dash'] else '')+'/>')
        elif a['kind']=='text':
            out.append(f'<text x="{a["x"]}" y="{a["y"]+a["size"]*.82}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{a["size"]}" fill="{a["color"]}" font-weight="{700 if a["bold"] else 400}">{html.escape(a["s"])}</text>')
        else:
            pts=' '.join(f'{x},{y}' for x,y in a['pts'])
            out.append(f'<polyline points="{pts}" fill="none" stroke="{a["color"]}" stroke-width="{a["width"]}"'+(' stroke-dasharray="6 5"' if a['dash'] else '')+(' marker-end="url(#arrow)"' if a['arrow'] else '')+'/>')
    out.append('</svg>');return '\n'.join(out)

def pdf_page(c,scene,sz):
    c.setPageSize(sz);c.saveState();c.scale(sz[0]/W,sz[1]/H)
    for a in scene.items:
        if a['kind']=='rect':
            if a['fill']:c.setFillColor(HexColor(a['fill']))
            if a['stroke']:c.setStrokeColor(HexColor(a['stroke']))
            c.setLineWidth(1.2);c.setDash([6,5] if a['dash'] else [])
            c.roundRect(a['x'],H-a['y']-a['h'],a['w'],a['h'],a['r'],fill=int(bool(a['fill'])),stroke=int(bool(a['stroke'])))
        elif a['kind']=='text':
            c.setFont('DB' if a['bold'] else 'D',a['size']);c.setFillColor(HexColor(a['color']))
            c.drawString(a['x'],H-a['y']-a['size']*.82,a['s'])
        else:
            c.setStrokeColor(HexColor(a['color']));c.setFillColor(HexColor(a['color']));c.setLineWidth(a['width']);c.setDash([6,5] if a['dash'] else [])
            p=c.beginPath();p.moveTo(a['pts'][0][0],H-a['pts'][0][1])
            for x,y in a['pts'][1:]:p.lineTo(x,H-y)
            c.drawPath(p)
            if a['arrow']:
                x,y=a['pts'][-1];x0,y0=a['pts'][-2];theta=math.atan2(y-y0,x-x0);size=8
                p=c.beginPath();p.moveTo(x,H-y)
                for off in [2.65,-2.65]:
                    xx=x+size*math.cos(theta+off);yy=y+size*math.sin(theta+off);p.lineTo(xx,H-yy)
                p.close();c.drawPath(p,fill=1,stroke=0)
    c.restoreState();c.showPage()

def drawio(pages):
    root=ET.Element('mxfile',host='app.diagrams.net',modified='2026-10-29T00:00:00.000Z',agent='IPO-Ready Architecture',version='24.7.17',type='device')
    for scene in pages:
        dg=ET.SubElement(root,'diagram',id=scene.name,name=scene.name)
        model=ET.SubElement(dg,'mxGraphModel',dx='1700',dy='1200',grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H),math='0',shadow='0')
        rr=ET.SubElement(model,'root');ET.SubElement(rr,'mxCell',id='0');ET.SubElement(rr,'mxCell',id='1',parent='0')
        for n,a in enumerate(scene.items,2):
            cell=ET.SubElement(rr,'mxCell',id=str(n),parent='1')
            if a['kind']=='line':
                style=f'endArrow={"block" if a["arrow"] else "none"};endFill=1;strokeColor={a["color"]};strokeWidth={a["width"]};dashed={int(a["dash"])};html=1;'
                cell.set('style',style);cell.set('edge','1')
                geo=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
                ET.SubElement(geo,'mxPoint',x=str(a['pts'][0][0]),y=str(a['pts'][0][1]),attrib={'as':'sourcePoint'})
                ET.SubElement(geo,'mxPoint',x=str(a['pts'][-1][0]),y=str(a['pts'][-1][1]),attrib={'as':'targetPoint'})
                if len(a['pts'])>2:
                    arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
                    for x,y in a['pts'][1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
            else:
                cell.set('vertex','1')
                if a['kind']=='rect':
                    cell.set('style',f'rounded={int(a["r"]>0)};arcSize=8;whiteSpace=wrap;html=1;fillColor={a["fill"] or "none"};strokeColor={a["stroke"] or "none"};strokeWidth=1.2;dashed={int(a["dash"])};')
                    x,y,w,h=a['x'],a['y'],a['w'],a['h']
                else:
                    cell.set('value',html.escape(a['s']))
                    cell.set('style',f'text;html=1;whiteSpace=nowrap;align=left;verticalAlign=top;spacing=0;fontFamily=DejaVu Sans;fontSize={a["size"]};fontStyle={int(a["bold"])};fontColor={a["color"]};fillColor=none;strokeColor=none;')
                    x,y,w,h=a['x'],a['y'],max(20,pdfmetrics.stringWidth(a['s'],'DB' if a['bold'] else 'D',a['size'])+5),a['size']*1.4
                ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
    return ET.tostring(root,encoding='unicode',xml_declaration=True)

