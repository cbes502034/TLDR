# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re

# Insert a thin space between CJK-block characters (ideographs, fullwidth
# punctuation/brackets, CJK quotes) and adjacent Latin/digit runs. Without
# this, reportlab's line-wrapper can treat a CJK-glued English word (e.g.
# "。OpenAI" or "（prompt）") as one unbreakable token and hard-split it
# mid-word (e.g. "Ope" / "nAI"), which is far more confusing to a reader
# than the occasional bracket landing alone at a line break.
_CJK = r'一-鿿　-〿＀-￯‘-‟'
_RE_CJK_LATIN = re.compile(f'([{_CJK}])([A-Za-z0-9])')
_RE_LATIN_CJK = re.compile(f'([A-Za-z0-9])([{_CJK}])')

def zsp(text):
    text = _RE_CJK_LATIN.sub(r'\1 \2', text)
    text = _RE_LATIN_CJK.sub(r'\1 \2', text)
    return text

# Use real TrueType CJK fonts (Microsoft JhengHei) with embedded Unicode cmaps.
# reportlab's legacy UnicodeCIDFont ('MSung-Light' etc.) relies on external Adobe
# CMap resources that mis-map glyphs in this environment, producing garbled text,
# so we avoid it entirely and embed TTFonts directly instead.
pdfmetrics.registerFont(TTFont('ZHRegular', r'C:\Windows\Fonts\msjh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('ZHBold', r'C:\Windows\Fonts\msjhbd.ttc', subfontIndex=0))

ZH = 'ZHRegular'
ZH_BOLD = 'ZHBold'
EN = 'Helvetica'
EN_B = 'Helvetica-Bold'
EN_I = 'Helvetica-Oblique'

NAVY = colors.HexColor('#1c3d5a')
ACCENT = colors.HexColor('#2c6e91')
GRAY = colors.HexColor('#555555')
LIGHTBG = colors.HexColor('#eef4f8')
VOCABBG = colors.HexColor('#fff8e6')
VOCABBORDER = colors.HexColor('#e0c078')
LINE = colors.HexColor('#cccccc')

styles = {}
styles['DocTitle'] = ParagraphStyle('DocTitle', fontName=ZH_BOLD, fontSize=20, leading=26,
                                     textColor=NAVY, alignment=TA_LEFT, spaceAfter=4)
styles['DocSub'] = ParagraphStyle('DocSub', fontName=ZH, fontSize=10.5, leading=15,
                                   textColor=GRAY, alignment=TA_LEFT, spaceAfter=2)
styles['SectionHead'] = ParagraphStyle('SectionHead', fontName=ZH_BOLD, fontSize=14, leading=18,
                                        textColor=colors.white, alignment=TA_LEFT)
styles['ArtNum'] = ParagraphStyle('ArtNum', fontName=EN_B, fontSize=11, leading=14, textColor=colors.white)
styles['TitleEN'] = ParagraphStyle('TitleEN', fontName=EN_B, fontSize=12, leading=16,
                                    textColor=NAVY, spaceAfter=2)
styles['TitleZH'] = ParagraphStyle('TitleZH', fontName=ZH_BOLD, fontSize=12, leading=17,
                                    textColor=NAVY, spaceAfter=6)
styles['Meta'] = ParagraphStyle('Meta', fontName=EN, fontSize=8.5, leading=11, textColor=GRAY, spaceAfter=6)
styles['BodyEN'] = ParagraphStyle('BodyEN', fontName=EN, fontSize=9.5, leading=14.5,
                                   textColor=colors.black, spaceAfter=6, alignment=TA_LEFT)
styles['BodyZH'] = ParagraphStyle('BodyZH', fontName=ZH, fontSize=10, leading=16.5,
                                   textColor=colors.HexColor('#222222'), spaceAfter=6, alignment=TA_LEFT)
styles['VocabHead'] = ParagraphStyle('VocabHead', fontName=ZH_BOLD, fontSize=9.5, leading=13,
                                      textColor=colors.HexColor('#8a6400'), spaceAfter=3)
styles['VocabItem'] = ParagraphStyle('VocabItem', fontName=ZH, fontSize=9, leading=13.5,
                                      textColor=colors.HexColor('#3a2f00'), spaceAfter=3)
styles['SummaryGroupHead'] = ParagraphStyle('SummaryGroupHead', fontName=ZH_BOLD, fontSize=11.5, leading=16,
                                             textColor=NAVY, spaceBefore=8, spaceAfter=4)
styles['SummaryBullet'] = ParagraphStyle('SummaryBullet', fontName=ZH, fontSize=10, leading=15,
                                          textColor=colors.HexColor('#222222'), spaceAfter=5)
styles['Footer'] = ParagraphStyle('Footer', fontName=ZH, fontSize=8, leading=11, textColor=GRAY)

def art_header_flowable(num, title_en, title_zh, meta):
    tbl = Table(
        [[Paragraph(str(num), styles['ArtNum']), Paragraph(title_en, ParagraphStyle(
            'h', fontName=EN_B, fontSize=11.5, leading=15, textColor=colors.white))]],
        colWidths=[9*mm, None]
    )
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,0), 6),
        ('LEFTPADDING', (1,0), (1,0), 4),
        ('RIGHTPADDING', (1,0), (1,0), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    out = [tbl, Spacer(1, 4)]
    out.append(Paragraph(zsp(title_zh), styles['TitleZH']))
    out.append(Paragraph(zsp(meta), styles['Meta']))
    return out

def vocab_box(items):
    rows = [Paragraph('值得注意的單字／句型文法', styles['VocabHead'])]
    for term, expl in items:
        rows.append(Paragraph(f'<font face="{ZH_BOLD}" color="#8a6400">{zsp(term)}</font>　{zsp(expl)}', styles['VocabItem']))
    inner = Table([[r] for r in rows], colWidths=[168*mm])
    inner.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (0,0), 8),
        ('BOTTOMPADDING', (0,0), (0,0), 2),
        ('TOPPADDING', (0,1), (-1,-1), 1),
        ('BOTTOMPADDING', (0,-1), (0,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.8, VOCABBORDER),
        ('BACKGROUND', (0,0), (-1,-1), VOCABBG),
    ]))
    return inner

def build():
    doc = SimpleDocTemplate(
        r'C:\Users\User\Desktop\agent\tldr\2026-08-18_星期二.pdf',
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm,
        title='TLDR 科技新聞沉浸式翻譯與重點整理', author='Claude'
    )
    story = []

    story.append(Paragraph('TLDR 科技新聞 — 沉浸式翻譯 ＆ 會議快讀重點', styles['DocTitle']))
    story.append(Paragraph(zsp('產出日期：2026-08-18（星期二）　｜　新聞來源：TLDR Tech Newsletter 2026-08-17 版（截至產出時最新一期）'), styles['DocSub']))
    story.append(Paragraph(zsp('使用情境：軟體工程師快速會前吸收，內容含逐段中英對照翻譯＋單字文法筆記＋重點整理'), styles['DocSub']))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=1.2, color=NAVY))
    story.append(Spacer(1, 10))

    articles = [
        dict(
            title_en='Stripe Clinches Over $7 Billion Deal to Buy AI Firm OpenRouter',
            title_zh='Stripe 敲定逾 70 億美元交易，收購 AI 新創 OpenRouter',
            meta='分類：Big Tech & Startups　｜　原文閱讀時間：約 3 分鐘',
            body_en='Stripe has finalized an agreement to acquire OpenRouter, a startup that helps companies switch between AI models. The sale price of more than $7 billion could change and the discussions are not public. OpenRouter\u2019s rise highlights the industry\u2019s growing scrutiny on AI costs. The acquisition will give Stripe a stronger footing in the fast-growing AI sector.',
            body_zh='Stripe 已敲定協議，將收購 OpenRouter——一家協助企業在不同 AI 模型間切換的新創公司。這筆超過 70 億美元的收購金額仍可能變動，且相關討論尚未公開。OpenRouter 的崛起，凸顯出業界對 AI 成本審視日益嚴格的趨勢。這筆收購案將讓 Stripe 在快速成長的 AI 產業中站穩更穩固的腳步。',
            vocab=[
                ('clinch (v.)', '敲定、拍板定案，常用於商業／體育新聞（clinch a deal）。標題用現在式 Clinches，內文用 has finalized 呼應。'),
                ('finalize an agreement <i>to V</i>', '敲定協議「去做」某事，to acquire 為不定詞片語修飾 agreement。'),
                ('a startup <i>that</i> helps companies switch...', 'that 引導的限定關係子句，修飾 startup，說明這家公司是做什麼的（高中文法：關代 that 代替先行詞）。'),
                ('scrutiny (n.)', '仔細的審查、監督；growing scrutiny on X＝對 X 日益嚴格的檢視。'),
                ('footing (n.)', '立足點、基礎；stronger footing＝更穩固的地位。'),
                ('fast-growing (adj.)', '複合形容詞（現在分詞＋形容詞修飾名詞），意為「快速成長的」。'),
            ],
        ),
        dict(
            title_en='Anthropic Sees AI Risks Rising, No Plan to Release Stronger "Model 2"',
            title_zh='Anthropic：AI 風險正在上升，暫無計畫發布更強的「Model 2」',
            meta='分類：Big Tech & Startups　｜　原文閱讀時間：約 2 分鐘',
            body_en='Anthropic says it will not release an internal model it claims to be more powerful than Mythos and that it will not slow development broadly. The company believes that the risks of the most serious harms from its models are still low. While the company is seeing signs of acceleration in its models\u2019 ability to conduct automated research and development, it appears to be signaling that it is getting harder to understand the capabilities and risks of its own models. OpenAI says it is slowing down the release of an upcoming model called Astra because it can\u2019t rule out critical cyber capabilities.',
            body_zh='Anthropic 表示，不會發布一款內部模型——該公司聲稱這款模型比 Mythos 更強大——同時也不會全面放慢研發腳步。該公司認為，其模型造成最嚴重危害的風險目前仍然偏低。雖然該公司觀察到旗下模型在「自動化研發能力」上出現加速跡象，但這似乎也顯示，要理解自家模型的能力與風險正變得越來越困難。OpenAI 則表示，將放緩代號為 Astra 的新模型上市時程，原因是無法排除該模型具備關鍵的網路攻擊能力。',
            vocab=[
                ('an internal model <i>it claims</i> to be...', '關係子句省略了 that/which（＝a model [that] it claims to be...），是受詞子句省略連接詞的常見用法。'),
                ('broadly (adv.)', '副詞修飾動詞片語，意為「廣泛地、全面地」，非「寬廣地」的字面翻譯。'),
                ('conduct (v.)', '「進行、執行」之意（conduct research），並非「導電」或「指揮」，是常見多義字。'),
                ('appear to V', '「似乎、看起來」；signal (v.) 在此為「透露訊息、顯示」。'),
                ('rule out (phr. v.)', '片語動詞「排除」，rule out + N（不能排除某可能性）。'),
                ('critical (adj.)', '在此意為「關鍵的、重大的」，不是「批評的」——是常考的一詞多義陷阱字。'),
            ],
        ),
        dict(
            title_en='A Quick Look at Zero-Knowledge Proofs',
            title_zh='零知識證明（ZKP）快速入門',
            meta='分類：Programming, Design & Data Science　｜　原文閱讀時間：約 14 分鐘',
            body_en='The idea of a zero-knowledge proof (ZKP) is that there are two parties: the prover and the verifier. The prover asserts that it has a solution to a (generally NP-complete) problem. The prover can convince the verifier of this without sharing the actual solution to the problem. While they are used to secure some cryptocurrencies, that is not their only use case. This article looks at how ZKPs work and how they can be applied to other problems like age verification.',
            body_zh='零知識證明（Zero-Knowledge Proof, ZKP）的核心概念是：存在兩方——「證明者」與「驗證者」。證明者聲稱自己擁有某個（通常屬於 NP-完備）問題的解答。證明者能夠說服驗證者相信這一點，卻不需要透露問題的實際解答內容。雖然 ZKP 被用來保護部分加密貨幣的安全，但那並非它唯一的應用場景。本文介紹 ZKP 的運作原理，以及它如何被應用在其他問題上，例如年齡驗證。',
            vocab=[
                ('assert (v.)', '「主張、聲稱」，語氣比 say 正式，常見於學術／法律語境。'),
                ('convince sb. <i>of</i> sth.', '說服某人相信某事，固定搭配介系詞 of（高中文法常考）。'),
                ('without <i>V-ing</i>', 'without 後面接動名詞（without sharing...），介系詞後必接 Ving 是常見文法點。'),
                ('NP-complete', '電腦科學專有名詞「NP-完備」，計算複雜度理論的分類，軟工背景常見但值得記錄。'),
                ('use case (n. phr.)', '軟體工程常用詞「應用場景／使用案例」。'),
                ('While..., that is not...', 'While 在此作「雖然」的讓步子句，不是「當...的時候」——一詞多義易誤讀處。'),
            ],
        ),
        dict(
            title_en='No Plan Survives Contact With the Enemy (Reality)',
            title_zh='計畫一旦遇上「現實」就會失效——先做原型，再談設計',
            meta='分類：Programming, Design & Data Science　｜　原文閱讀時間：約 2 分鐘',
            body_en='If your most precious commodity is attention, ask your agents for the design after they\u2019ve built the thing. Let the agent spend extra cycles in the lab, and get one layer deeper on the design. A plan that\u2019s been prototyped is a better plan.',
            body_zh='如果你最寶貴的資源是「注意力」，不妨讓 AI 代理人（agent）先把東西做出來，事後再跟它要設計說明。讓 agent 在「實驗室」階段多花一些運算週期，把設計再往下鑽研一層。一個已經被實際做成原型（prototype）驗證過的計畫，才是更好的計畫。',
            vocab=[
                ('標題典故', '改編自軍事名言 "No plan survives first contact with the enemy"（計畫一旦接觸敵人就會失效），此處用 (Reality) 取代 the Enemy，比喻「現實」才是真正的敵人。'),
                ('precious commodity', 'commodity 原指「商品、大宗物資」，這裡引申為「珍貴的資源」。'),
                ('spend cycles', 'cycles 在工程語境常指「運算週期」，也可引申為「花費心力／時間」。'),
                ('get one layer deeper on X', '片語：「在 X 上再深入一層」，layer（層）常見於分層架構描述。'),
                ('A plan <i>that\u2019s been</i> prototyped', 'that\u2019s been = that has been，現在完成式被動語態的關係子句，修飾 plan。'),
            ],
        ),
        dict(
            title_en='AI Just Had Another Math Breakthrough\u2014With Help From a High-School Dropout',
            title_zh='AI 再創數學突破——這次的推手竟是「高中輟學生」',
            meta='分類：Miscellaneous　｜　原文閱讀時間：約 11 分鐘',
            body_en='Anthropic employee Jarred Sumner used the Claude app on his phone to try to solve the infamous Riemann hypothesis. The model didn\u2019t succeed, but it made a related finding that one Stanford number theorist has called the most impressive result that AI has produced in math so far. Sumner\u2019s formal mathematical education ended after just one semester of high-school geometry, and he identifies as very much not a mathematician. Most of the prompting he gave to the model was variations of \u2018keep going\u2019 and \u2018believe in yourself\u2019.',
            body_zh='Anthropic 員工 Jarred Sumner 用手機上的 Claude App，嘗試挑戰惡名昭彰的「黎曼猜想」（Riemann hypothesis）。雖然模型最終沒有成功解出，卻意外做出一項相關發現——一位史丹佛大學的數論學家稱這是「AI 至今在數學領域產出過、最令人印象深刻的成果」。Sumner 正式的數學教育，僅止於高中幾何學一個學期，他自認完全不是數學家。他給模型下的提示（prompt），大多只是「繼續」、「相信自己」之類的變化版本。',
            vocab=[
                ('infamous (adj.)', '「惡名昭彰的」，注意跟 famous（有名的）僅差一個 in-，但語意偏負面，是常見混淆字。'),
                ('Riemann hypothesis', '數學專有名詞「黎曼猜想」，千禧年七大數學難題之一。'),
                ('a finding <i>that</i> S+V...', '此處 that 子句是同位語子句，修飾 finding，說明發現的具體內容是什麼。'),
                ('the most impressive result <i>that</i>...', '最高級（the most...）＋ that 引導的關係子句，修飾 result。'),
                ('identify as N', '片語，「自我認同為……」，現代英文常見用法（identify as a mathematician / not a mathematician）。'),
                ('prompting (n.)', '動詞 prompt 的動名詞，「提示、下指令」，AI 領域 prompt engineering 一詞的字根。'),
            ],
        ),
        dict(
            title_en='The World\u2019s Largest Electric Plane Takes Flight',
            title_zh='全球最大電動飛機成功首航',
            meta='分類：Science & Futuristic Technology　｜　原文閱讀時間：約 8 分鐘',
            body_en='Heart Aerospace\u2019s X1 electric aircraft has a 106-foot wingspan and weighs more than 25,000 pounds. It flew for 27 minutes on battery power alone and reached an altitude of 1,100 feet during its recent maiden flight. Heart plans to bring a hybrid-electric plane into commercial service by 2031. The company\u2019s technology promises lower maintenance costs and insulation from volatile jet fuel prices for airlines.',
            body_zh='Heart Aerospace 公司的 X1 電動飛機，翼展達 106 英尺，機身重量超過 25,000 磅。在近期的「首航」（maiden flight）中，這架飛機僅靠電池動力就飛行了 27 分鐘，並爬升到 1,100 英尺的高度。Heart 公司計畫在 2031 年前，讓一款油電混合動力飛機正式投入商業營運。該公司的技術有望為航空公司帶來更低的維修成本，並讓航空公司不再受「劇烈波動的航空燃油價格」所影響。',
            vocab=[
                ('wingspan (n.)', '「翼展」，航空專有名詞，由 wing（翅膀）＋ span（跨距）組成。'),
                ('on battery power <i>alone</i>', 'alone 放在名詞後面表示「單靠、僅憑」，強調唯一條件（on X alone）。'),
                ('maiden flight (n. phr.)', '「首航、處女航」；maiden 當形容詞表示「第一次的」（maiden voyage 用於船艦同理）。'),
                ('bring N into commercial service', '片語，「讓 N 正式投入商業營運」。'),
                ('insulation from X', '本義為「隔絕、絕緣」（insulation 電學上指絕緣體），這裡引申為「不受 X 影響、免受波及」。'),
                ('volatile (adj.)', '「（價格、局勢）劇烈波動的、不穩定的」，金融新聞常見字，注意勿與 violent（暴力的）混淆。'),
            ],
        ),
    ]

    for i, art in enumerate(articles, start=1):
        block = []
        block.extend(art_header_flowable(i, art['title_en'], art['title_zh'], art['meta']))
        block.append(Paragraph(f'<font face="{EN_I}" color="#666666">EN</font>&nbsp;&nbsp;' + art['body_en'], styles['BodyEN']))
        block.append(Paragraph(f'<font face="{ZH_BOLD}" color="#2c6e91">中譯</font>&nbsp;&nbsp;' + zsp(art['body_zh']), styles['BodyZH']))
        block.append(Spacer(1, 3))
        block.append(vocab_box(art['vocab']))
        block.append(Spacer(1, 12))
        story.extend(block)

    # ---- Summary section ----
    story.append(PageBreak())
    story.append(Paragraph('會議快讀重點整理', styles['DocTitle']))
    story.append(Paragraph(zsp('30 秒掃描版：依主題分類，供開會前快速吸收'), styles['DocSub']))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=1.2, color=NAVY))
    story.append(Spacer(1, 8))

    def bullets(items):
        return ListFlowable(
            [ListItem(Paragraph(zsp(t), styles['SummaryBullet']), leftIndent=10, bulletColor=ACCENT) for t in items],
            bulletType='bullet', start='\u2022', leftIndent=14, bulletFontSize=9,
        )

    story.append(Paragraph('AI 產業動態', styles['SummaryGroupHead']))
    story.append(bullets([
        'Stripe 以超過 <b>70 億美元</b>收購 AI 模型路由新創 <b>OpenRouter</b>，強化其在 AI 產業的布局，反映市場對 AI 使用成本管控的關注升溫。',
        'Anthropic 表示暫不發布更強的內部模型「Model 2」，認為現階段嚴重風險仍偏低，但坦言越來越難掌握自家模型的真實能力與風險；<b>OpenAI</b> 也因無法排除新模型 Astra 的網攻能力而放緩發布。',
        '一名 Anthropic 員工（非數學專業出身）僅靠 Claude App 手機提示，在挑戰<b>黎曼猜想</b>的過程中意外做出被史丹佛數論學家譽為「AI 迄今最佳數學成果」的發現。',
    ]))
    story.append(Paragraph('工程與技術', styles['SummaryGroupHead']))
    story.append(bullets([
        '<b>零知識證明（ZKP）</b>科普：讓一方能在不揭露答案的情況下，證明自己知道答案；應用不限於加密貨幣，也可用於年齡驗證等場景。',
        'Agentic 工程觀點：建議先讓 AI agent 把東西做出來、跑過一輪「原型」驗證，再回頭要設計文件——經過原型驗證的計畫品質更高。',
    ]))
    story.append(Paragraph('一般科技', styles['SummaryGroupHead']))
    story.append(bullets([
        'Heart Aerospace 全球最大電動飛機 <b>X1</b> 完成首航，續航 27 分鐘、飛高 1,100 英尺，預計 2031 年投入油電混合商轉，可望降低航空公司維修成本並減少燃油價格波動風險。',
    ]))
    story.append(Paragraph('給軟體工程師的啟示', styles['SummaryGroupHead']))
    story.append(bullets([
        'AI 模型能力與風險的「可解釋性」正變得更困難，連開發商自己都難以完全掌握——導入 AI 工具／agent 到工作流程時需特別留意風險評估。',
        '「先做原型、後補設計」的 agentic 開發模式，可能比傳統「先設計後實作」更有效率，值得評估導入團隊工作流程。',
        '若團隊有隱私驗證需求（如年齡驗證、憑證驗證），ZKP 是值得追蹤的技術方向。',
        'AI 大廠間的併購（Stripe/OpenRouter）顯示 <b>AI 模型路由與成本控管</b>正成為重要賽道，若團隊有多模型串接需求可留意相關工具。',
    ]))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width='100%', thickness=0.6, color=LINE))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        zsp('資料來源：tldr.tech（TLDR Tech Newsletter, 2026-08-17 版，產出當下最新一期）。翻譯與整理由 Claude 協助完成，僅供內部會議快速閱讀參考，正式引用請核對原文。'),
        styles['Footer']))

    doc.build(story)
    print('PDF generated.')

if __name__ == '__main__':
    build()
