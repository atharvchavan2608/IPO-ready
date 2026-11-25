"""Render the editable Markdown proposal into a compact academic PDF."""
from pathlib import Path
from xml.sax.saxutils import escape
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output/pdf/IPO_Ready_Project_Proposal.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyProposal',fontName='Helvetica',fontSize=10.2,leading=14,spaceAfter=7,textColor=colors.HexColor('#27364a')))
styles.add(ParagraphStyle(name='TitleProposal',fontName='Helvetica-Bold',fontSize=30,leading=35,spaceAfter=10,textColor=colors.HexColor('#12354b')))
styles.add(ParagraphStyle(name='H2Proposal',fontName='Helvetica-Bold',fontSize=16,leading=20,spaceAfter=12,textColor=colors.HexColor('#12354b')))
styles.add(ParagraphStyle(name='H3Proposal',fontName='Helvetica-Bold',fontSize=11.3,leading=14,spaceBefore=8,spaceAfter=5,textColor=colors.HexColor('#087e81'),keepWithNext=True))
styles.add(ParagraphStyle(name='BulletProposal',parent=styles['BodyProposal'],leftIndent=10,firstLineIndent=-7,spaceAfter=4))
styles.add(ParagraphStyle(name='ReferenceProposal',parent=styles['BodyProposal'],fontSize=9.3,leading=12,spaceAfter=6))
def markup(text):
    return re.sub(r'(https://[^\s]+)',lambda m:'<link href="'+m.group(1)+'" color="#087276">'+m.group(1)+'</link>',escape(text))
story=[]
for line in (ROOT/'docs/proposal/IPO_Ready_Project_Proposal.md').read_text(encoding='utf8').splitlines():
    if not line.strip():continue
    if line=='---':story.append(PageBreak());continue
    if line.startswith('### '):style='H3Proposal';line=line[4:]
    elif line.startswith('## '):style='H2Proposal';line=line[3:]
    elif line.startswith('# '):style='TitleProposal';line=line[2:]
    elif line.startswith('- '):style='BulletProposal';line='- '+line[2:]
    elif re.match(r'^\[\d+\]',line):style='ReferenceProposal'
    else:style='BodyProposal'
    story.append(Paragraph(markup(line),styles[style]))
def furniture(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#dce4ed'));canvas.line(43,43,A4[0]-43,43)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52657a'))
    canvas.drawString(43,30,'IPO-READY  |  PYTHON PROGRAMMING ANALYTICS  |  PROJECT PROPOSAL')
    canvas.drawRightString(A4[0]-43,30,str(doc.page))
SimpleDocTemplate(str(out),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=38,bottomMargin=57,title='IPO-Ready: Python Analytics Project Proposal',author='Project Team').build(story,onFirstPage=furniture,onLaterPages=furniture)
print(out)
