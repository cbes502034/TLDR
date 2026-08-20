# -*- coding: utf-8 -*-
"""
TLDR 每日新聞整理 — 深色主題 PDF + 語音稿產生器
內容為自行撰寫之英文摘要（gist）＋中文翻譯＋單字文法筆記，非原文轉載。
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re, os

OUTDIR = r'C:\Users\User\Desktop\agent\tldr\2026-08-19_星期三'
PDF_PATH = os.path.join(OUTDIR, '2026-08-19_星期三.pdf')
NARRATION_PATH = os.path.join(OUTDIR, '_narration.txt')

_CJK = r'一-鿿　-〿＀-￯‘-‟'
_RE_CJK_LATIN = re.compile(f'([{_CJK}])([A-Za-z0-9])')
_RE_LATIN_CJK = re.compile(f'([A-Za-z0-9])([{_CJK}])')

def zsp(t):
    t = _RE_CJK_LATIN.sub(r'\1 \2', t)
    return _RE_LATIN_CJK.sub(r'\1 \2', t)

pdfmetrics.registerFont(TTFont('ZHRegular', r'C:\Windows\Fonts\msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('ZHBold', r'C:\Windows\Fonts\msjhbd.ttc', subfontIndex=0))
ZH, ZH_BOLD = 'ZHRegular', 'ZHBold'
EN, EN_B, EN_I = 'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique'

# 深色主題（使用者偏好：新聞整理一律黑底）
PAGE_BG     = colors.HexColor('#0b0e13')
BAR         = colors.HexColor('#2c5d85')
ACCENT      = colors.HexColor('#6cc0e8')
GRAY        = colors.HexColor('#9aa1a8')
INK         = colors.HexColor('#e9e9ec')
VOCABBG     = colors.HexColor('#241d0d')
VOCABBORDER = colors.HexColor('#caa355')
VOCAB_HEAD  = colors.HexColor('#f0c869')
VOCAB_TEXT  = colors.HexColor('#e6d7ae')
LINE        = colors.HexColor('#3a4048')

S = {}
S['CoverTitle']  = ParagraphStyle('CoverTitle', fontName=ZH_BOLD, fontSize=27, leading=35, textColor=INK, alignment=TA_CENTER, spaceAfter=10)
S['CoverTitle2'] = ParagraphStyle('CoverTitle2', fontName=ZH_BOLD, fontSize=18, leading=26, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=26)
S['CoverSub']    = ParagraphStyle('CoverSub', fontName=ZH, fontSize=11.5, leading=18, textColor=GRAY, alignment=TA_CENTER, spaceAfter=6)
S['CoverSmall']  = ParagraphStyle('CoverSmall', fontName=ZH, fontSize=9.5, leading=16, textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)
S['CoverCount']  = ParagraphStyle('CoverCount', fontName=ZH_BOLD, fontSize=11, leading=17, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4)
S['DocTitle']    = ParagraphStyle('DocTitle', fontName=ZH_BOLD, fontSize=20, leading=26, textColor=INK, alignment=TA_LEFT, spaceAfter=4)
S['DocSub']      = ParagraphStyle('DocSub', fontName=ZH, fontSize=10.5, leading=15, textColor=GRAY, alignment=TA_LEFT, spaceAfter=2)
S['TopicTitle']  = ParagraphStyle('TopicTitle', fontName=ZH_BOLD, fontSize=22, leading=28, textColor=INK, alignment=TA_CENTER, spaceAfter=4)
S['TopicSub']    = ParagraphStyle('TopicSub', fontName=EN_B, fontSize=11, leading=15, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=2)
S['TopicMeta']   = ParagraphStyle('TopicMeta', fontName=ZH, fontSize=9, leading=13, textColor=GRAY, alignment=TA_CENTER, spaceAfter=10)
S['ArtNum']      = ParagraphStyle('ArtNum', fontName=EN_B, fontSize=11, leading=14, textColor=colors.white)
S['TitleZH']     = ParagraphStyle('TitleZH', fontName=ZH_BOLD, fontSize=11.5, leading=16, textColor=INK, spaceAfter=5)
S['BodyEN']      = ParagraphStyle('BodyEN', fontName=EN, fontSize=9.5, leading=14.5, textColor=INK, spaceAfter=5, alignment=TA_LEFT)
S['BodyZH']      = ParagraphStyle('BodyZH', fontName=ZH, fontSize=10, leading=16.5, textColor=INK, spaceAfter=5, alignment=TA_LEFT)
S['VocabHead']   = ParagraphStyle('VocabHead', fontName=ZH_BOLD, fontSize=9.5, leading=13, textColor=VOCAB_HEAD, spaceAfter=3)
S['VocabItem']   = ParagraphStyle('VocabItem', fontName=ZH, fontSize=9, leading=13.5, textColor=VOCAB_TEXT, spaceAfter=3)
S['SumHead']     = ParagraphStyle('SumHead', fontName=ZH_BOLD, fontSize=11, leading=15, textColor=ACCENT, spaceBefore=7, spaceAfter=3)
S['SumBullet']   = ParagraphStyle('SumBullet', fontName=ZH, fontSize=9.3, leading=14, textColor=INK, spaceAfter=3)
S['Footer']      = ParagraphStyle('Footer', fontName=ZH, fontSize=8, leading=12, textColor=GRAY)


def paint_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAGE_BG)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.restoreState()


def topic_header(zh, en, meta):
    return [Spacer(1, 4),
            Paragraph(zsp(zh), S['TopicTitle']),
            Paragraph(en, S['TopicSub']),
            Paragraph(zsp(meta), S['TopicMeta']),
            HRFlowable(width='100%', thickness=1.2, color=BAR),
            Spacer(1, 10)]


def art_header(num, title_en):
    t = Table([[Paragraph(str(num), S['ArtNum']),
                Paragraph(title_en, ParagraphStyle('h', fontName=EN_B, fontSize=11, leading=14.5, textColor=colors.white))]],
              colWidths=[9 * mm, None])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BAR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 6), ('LEFTPADDING', (1, 0), (1, 0), 4),
        ('RIGHTPADDING', (1, 0), (1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def vocab_box(items):
    rows = [Paragraph('值得注意的單字／句型文法', S['VocabHead'])]
    for term, expl in items:
        rows.append(Paragraph(f'<font face="{ZH_BOLD}" color="#f0c869">{zsp(term)}</font>　{zsp(expl)}', S['VocabItem']))
    tb = Table([[r] for r in rows], colWidths=[168 * mm])
    tb.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (0, 0), 8), ('BOTTOMPADDING', (0, 0), (0, 0), 2),
        ('TOPPADDING', (0, 1), (-1, -1), 1), ('BOTTOMPADDING', (0, -1), (0, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.8, VOCABBORDER),
        ('BACKGROUND', (0, 0), (-1, -1), VOCABBG),
    ]))
    return tb


def article_block(num, a):
    out = [art_header(num, a['title_en']), Spacer(1, 4),
           Paragraph(zsp(a['title_zh']), S['TitleZH']),
           Paragraph(f'<font face="{EN_I}" color="#9aa1a8">EN</font>&nbsp;&nbsp;' + a['gist_en'], S['BodyEN']),
           Paragraph(f'<font face="{ZH_BOLD}" color="#6cc0e8">中譯</font>&nbsp;&nbsp;' + zsp(a['body_zh']), S['BodyZH']),
           Spacer(1, 3), vocab_box(a['vocab']), Spacer(1, 12)]
    return out

