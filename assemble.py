# -*- coding: utf-8 -*-
"""組裝最終輸出：每主題挑 2 篇最重要的文章 -> PDF + 語音稿。"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

bd = _load('build_daily', os.path.join(HERE, 'build_daily.py'))
t1 = _load('topics_1', os.path.join(HERE, 'topics_1.py'))
t2 = _load('topics_2', os.path.join(HERE, 'topics_2.py'))
t3 = _load('topics_3', os.path.join(HERE, 'topics_3.py'))

ALL = t1.TOPICS + t2.TOPICS + t3.TOPICS  # 14 個主題，順序：Tech,Dev,AI,InfoSec,Product,DevOps,Founders,Design,Marketing,Crypto,Fintech,IT,Data,Hardware

# 每個主題挑選「最重要的 2 篇」在該主題 arts 清單中的索引（0-based）
PICKS = {
    '科技綜合': [0, 1],   # OpenAI 訓練暫停 / Meta 200 億求償
    '軟體開發': [0, 10],  # Cursor 重建 Git 代管 / GitHub 事故報告
    '人工智慧': [2, 11],  # Cerebras CS-4 / Nvidia 護城河轉向資本
    '資訊安全': [0, 2],   # Heights Finance 外洩 / Unisoc VoLTE 漏洞
    '產品管理': [0, 1],   # IC work / Nvidia's Risky Business
    'DevOps':   [0, 2],   # Claude Opus 5 GovCloud / DuckDB v2.0
    '新創與創業': [0, 3], # ARR 不再是原本的意思 / 800萬歸零後重建 200萬 ARR
    '設計':     [0, 4],   # 相機 AirPods / Instagram 品牌系統
    '行銷':     [0, 1],   # 平台變怪 / AI Overview 9個月數據
    '加密貨幣': [0, 3],   # 白宮加密峰會 / Stripe 收購 OpenRouter
    '金融科技': [3, 1],   # Nvidia 最大金融科技公司 / Workday 收購傳聞
    'IT 產業':  [1, 6],   # 微軟整併 Copilot / 惡意程式偽裝微軟服務
    '資料工程': [2, 5],   # AI 是儲存負載 / 16年 SQLite 臭蟲
    '硬體':     [0, 3],   # Etched 估值翻倍 / Nvidia 訂 TSMC 1.6nm
}

for topic in ALL:
    idxs = PICKS[topic['zh']]
    topic['arts'] = [topic['arts'][i] for i in idxs]

TOTAL = sum(len(t['arts']) for t in ALL)
print(f'Selected {TOTAL} articles across {len(ALL)} topics')

# ---------------------------------------------------------------- PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak, ListFlowable, ListItem
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

OUTDIR = bd.OUTDIR
os.makedirs(OUTDIR, exist_ok=True)
PDF_PATH = bd.PDF_PATH

doc = SimpleDocTemplate(PDF_PATH, pagesize=A4,
                         leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm,
                         title='TLDR 每日新聞整理', author='Claude')
story = []

story.append(Spacer(1, 55))
story.append(Paragraph('TLDR 每日新聞整理', bd.S['CoverTitle']))
story.append(Paragraph('沉浸式翻譯 ＆ 語音版', bd.S['CoverTitle2']))
story.append(Paragraph(bd.zsp('產出日期：2026-08-19（星期三）'), bd.S['CoverSub']))
story.append(Paragraph(bd.zsp('涵蓋範圍：14 個主題，每主題精選 2 篇最重要新聞'), bd.S['CoverSmall']))
story.append(Paragraph(bd.zsp(f'共 {TOTAL} 篇文章　｜　內容為本機獨立撰寫之摘要與翻譯，非原文轉載'), bd.S['CoverCount']))
story.append(Spacer(1, 16))
story.append(Paragraph(bd.zsp('使用情境：軟體工程師快速吸收，內容含逐段中英對照＋單字文法筆記；隨附語音版可用聽的複習'), bd.S['CoverSub']))

for topic in ALL:
    story.append(PageBreak())
    story.extend(bd.topic_header(topic['zh'], topic['en'], f"資料來源日期：{topic['date']}"))
    for i, a in enumerate(topic['arts'], start=1):
        story.extend(bd.article_block(i, a))

# ---- 摘要頁 ----
story.append(PageBreak())
story.append(Paragraph('會議快讀重點整理', bd.S['DocTitle']))
story.append(Paragraph(bd.zsp('30 秒掃描版：依 14 主題分類'), bd.S['DocSub']))
story.append(Spacer(1, 6))
story.append(HRFlowable(width='100%', thickness=1.2, color=bd.BAR))
story.append(Spacer(1, 8))

def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(bd.zsp(t), bd.S['SumBullet']), leftIndent=9, bulletColor=bd.ACCENT) for t in items],
        bulletType='bullet', start='•', leftIndent=12, bulletFontSize=8)

for topic in ALL:
    story.append(Paragraph(topic['zh'], bd.S['SumHead']))
    story.append(bullets([a['title_zh'] for a in topic['arts']]))

story.append(Spacer(1, 14))
story.append(HRFlowable(width='100%', thickness=0.6, color=bd.LINE))
story.append(Spacer(1, 4))
story.append(Paragraph(bd.zsp('內容說明：本文件中的英文摘要與中文翻譯，均由 Claude 依 tldr.tech 當日 14 份子報之新聞事實自行撰寫，非原文逐字轉載。翻譯與單字整理僅供個人學習參考，正式引用請查核原始報導。'), bd.S['Footer']))

doc.build(story, onFirstPage=bd.paint_bg, onLaterPages=bd.paint_bg)
print('PDF written:', PDF_PATH)

# ---------------------------------------------------------------- 語音稿
lines = []
lines.append('TLDR 每日新聞整理，語音版。二零二六年八月十九日，星期三。')
for topic in ALL:
    lines.append(f'-- 主題：{topic["zh"]} --')
    for i, a in enumerate(topic['arts'], start=1):
        lines.append(f'第{i}篇。{a["title_zh"]}。')
        lines.append(f'[EN] {a["gist_en"]}')
        lines.append(f'[ZH] {a["body_zh"]}')
with open(bd.NARRATION_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Narration script written:', bd.NARRATION_PATH)
