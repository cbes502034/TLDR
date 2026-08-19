# -*- coding: utf-8 -*-
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
import re

_CJK = r'一-鿿　-〿＀-￯‘-‟'
_RE_CJK_LATIN = re.compile(f'([{_CJK}])([A-Za-z0-9])')
_RE_LATIN_CJK = re.compile(f'([A-Za-z0-9])([{_CJK}])')

def zsp(text):
    text = _RE_CJK_LATIN.sub(r'\1 \2', text)
    text = _RE_LATIN_CJK.sub(r'\1 \2', text)
    return text

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
VOCABBG = colors.HexColor('#fff8e6')
VOCABBORDER = colors.HexColor('#e0c078')
LINE = colors.HexColor('#cccccc')

styles = {}
styles['DocTitle'] = ParagraphStyle('DocTitle', fontName=ZH_BOLD, fontSize=20, leading=26,
                                     textColor=NAVY, alignment=TA_LEFT, spaceAfter=4)
styles['DocSub'] = ParagraphStyle('DocSub', fontName=ZH, fontSize=10.5, leading=15,
                                   textColor=GRAY, alignment=TA_LEFT, spaceAfter=2)
styles['TopicTitle'] = ParagraphStyle('TopicTitle', fontName=ZH_BOLD, fontSize=22, leading=28,
                                       textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
styles['TopicSub'] = ParagraphStyle('TopicSub', fontName=EN_B, fontSize=11, leading=15,
                                     textColor=ACCENT, alignment=TA_CENTER, spaceAfter=2)
styles['TopicMeta'] = ParagraphStyle('TopicMeta', fontName=ZH, fontSize=9, leading=13,
                                      textColor=GRAY, alignment=TA_CENTER, spaceAfter=10)
styles['ArtNum'] = ParagraphStyle('ArtNum', fontName=EN_B, fontSize=11, leading=14, textColor=colors.white)
styles['TitleZH'] = ParagraphStyle('TitleZH', fontName=ZH_BOLD, fontSize=12, leading=17,
                                    textColor=NAVY, spaceAfter=6)
styles['Meta'] = ParagraphStyle('Meta', fontName=ZH, fontSize=8.5, leading=11, textColor=GRAY, spaceAfter=6)
styles['BodyEN'] = ParagraphStyle('BodyEN', fontName=EN, fontSize=9.5, leading=14.5,
                                   textColor=colors.black, spaceAfter=6, alignment=TA_LEFT)
styles['BodyZH'] = ParagraphStyle('BodyZH', fontName=ZH, fontSize=10, leading=16.5,
                                   textColor=colors.HexColor('#222222'), spaceAfter=6, alignment=TA_LEFT)
styles['VocabHead'] = ParagraphStyle('VocabHead', fontName=ZH_BOLD, fontSize=9.5, leading=13,
                                      textColor=colors.HexColor('#8a6400'), spaceAfter=3)
styles['VocabItem'] = ParagraphStyle('VocabItem', fontName=ZH, fontSize=9, leading=13.5,
                                      textColor=colors.HexColor('#3a2f00'), spaceAfter=3)
styles['SummaryTopicHead'] = ParagraphStyle('SummaryTopicHead', fontName=ZH_BOLD, fontSize=11, leading=15,
                                             textColor=NAVY, spaceBefore=7, spaceAfter=3)
styles['SummaryBullet'] = ParagraphStyle('SummaryBullet', fontName=ZH, fontSize=9.3, leading=14,
                                          textColor=colors.HexColor('#222222'), spaceAfter=3)
styles['Footer'] = ParagraphStyle('Footer', fontName=ZH, fontSize=8, leading=11, textColor=GRAY)

def topic_header(name_zh, name_en, meta):
    out = [Spacer(1, 4)]
    out.append(Paragraph(zsp(name_zh), styles['TopicTitle']))
    out.append(Paragraph(name_en, styles['TopicSub']))
    out.append(Paragraph(zsp(meta), styles['TopicMeta']))
    out.append(HRFlowable(width='100%', thickness=1.2, color=NAVY))
    out.append(Spacer(1, 10))
    return out

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

def article_block(num, art):
    block = []
    block.extend(art_header_flowable(num, art['title_en'], art['title_zh'], art['meta']))
    block.append(Paragraph(f'<font face="{EN_I}" color="#666666">EN</font>&nbsp;&nbsp;' + art['body_en'], styles['BodyEN']))
    block.append(Paragraph(f'<font face="{ZH_BOLD}" color="#2c6e91">中譯</font>&nbsp;&nbsp;' + zsp(art['body_zh']), styles['BodyZH']))
    block.append(Spacer(1, 3))
    block.append(vocab_box(art['vocab']))
    block.append(Spacer(1, 12))
    return block

# ============================================================
# TOPICS DATA
# ============================================================

TOPICS = [
    dict(name_zh='科技綜合', name_en='TLDR Tech', date='2026-08-18', summary_head='科技綜合', articles=[
        dict(
            title_en='Anthropic Tells Investors Annualized Revenue Run Rate Climbed to $65 Billion in July',
            title_zh='Anthropic 告知投資人：七月年化營收衝上 650 億美元',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Anthropic\u2019s annualized run rate hit $65 billion at the end of July. The company has seen its enterprise popularity surge as it gears up for what\u2019s expected to be a blockbuster IPO. It filed its prospectus with the SEC in June and has been holding preliminary meetings with potential investors. There is still no official timeline for the debut.',
            body_zh='Anthropic 的年化營收（annualized run rate）在七月底達到 650 億美元。隨著該公司為外界預期的「重磅級 IPO」積極備戰，其企業客戶的市場人氣也隨之飆升。該公司已於六月向美國證券交易委員會（SEC）提交了公開說明書，並持續與潛在投資人進行初步會議。不過，官方目前仍未公布正式上市的時間表。',
            vocab=[
                ('annualized run rate', '財經／新創圈常用專有名詞「年化營收速率」，把當期營收換算成年度數字，用來預估全年營收規模。'),
                ('gear up for X', '片語，「為 X 積極備戰、做好準備」，gear 原指「排檔、齒輪」，引申為「準備就緒」。'),
                ('blockbuster (adj./n.)', '原指「賣座強片」，引申為「轟動一時的、重磅級的」，常形容規模極大的商業事件（blockbuster IPO）。'),
                ('file a prospectus with the SEC', '金融領域固定用法，「向證券交易委員會提交公開說明書」，是準備上市（IPO）的必經法律程序。'),
                ('preliminary (adj.)', '「初步的、預備性的」，常見於正式文件與商業新聞。'),
                ('debut (n.)', '原指「首次登場、初次亮相」，這裡指公司（股票）首次公開上市的那一刻。'),
            ],
        ),
        dict(
            title_en='Tesla Cybercab Launch Preparations Have Begun',
            title_zh='特斯拉 Cybercab 無人計程車籌備發表',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Tesla plans to launch the Cybercab in Austin, Texas, later this month. Employees have been told to prepare for a public launch as soon as the end of the month. Tesla has launched a lottery to ride the vehicle at the launch event. The Cybercab entered production back in April, and the company has been testing units in a variety of environments and climates around the US.',
            body_zh='特斯拉計畫本月稍晚在德州奧斯汀正式推出 Cybercab（無人計程車）。員工已被告知，要準備好最快在月底前進行公開發表。特斯拉也開放了抽籤活動，讓民眾有機會在發表會上試乘這款車。Cybercab 早在四月就已經投入量產，該公司持續在美國各地不同環境與氣候條件下測試車輛。',
            vocab=[
                ('launch (v./n.)', '「推出、發表」（動詞）或「發表會」（名詞），科技新聞高頻字，注意與「launch a rocket（發射火箭）」的「發射」義區分。'),
                ('later this month', '「本月稍晚」，later 在此作副詞，表示「之後的時間點」，不是比較級「更晚」的意思。'),
                ('have been told <i>to V</i>', '現在完成式被動語態＋不定詞，「已被告知要做……」。'),
                ('as soon as the end of the month', '「最快在月底」，as soon as 在此表「早則、最快」的時間點，不是「一……就……」的連接詞用法（常見混淆）。'),
                ('a variety of', '「各式各樣的」，後接複數名詞，是常考片語。'),
                ('back in April', 'back in ＋ 時間，「早在……（過去某個時間點）」，強調回溯時間感。'),
            ],
        ),
        dict(
            title_en='Google Just Bought a Bunch of Spirit Airlines Data for AI Training',
            title_zh='Google 買下西凱航空大批資料，用於 AI 訓練',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Google has purchased a huge dump of data from the now-defunct Spirit Airlines for $10 million. The dump includes data on operations and business, as well as software code, but not personal information. All personally identifiable information will be rigorously scrubbed by a third party before receipt. Google will use the data to improve its products and AI models.',
            body_zh='Google 以 1,000 萬美元的價格，向已經停業的西凱航空（Spirit Airlines）購入一大批資料。這批資料包含營運與商業資料，以及軟體程式碼，但不含個人資訊。所有可識別個人身分的資訊，都會先由第三方嚴格清除後，Google 才會接收。Google 將利用這批資料來改善自家產品與 AI 模型。',
            vocab=[
                ('a huge dump of data', '「一大批（傾倒式匯出的）資料」，dump 當名詞在工程領域常指「（資料庫）傾印、大量匯出的資料」。'),
                ('now-defunct (adj.)', '「如今已經停業／不存在的」，defunct 為正式用語，形容不再運作的公司或制度。'),
                ('personally identifiable information', '資訊領域專有名詞「個人可識別資訊」，常縮寫 PII，是隱私法規（如 GDPR）常見用詞。'),
                ('scrub (v.)', '原意「刷洗」，在資料工程語境引申為「清除、清洗（資料）」，例如 data scrubbing。'),
            ],
        ),
        dict(
            title_en='Clinic-in-the-Loop',
            title_zh='把「臨床」放進回饋循環裡',
            meta='原文閱讀時間：約 16 分鐘',
            body_en='Faster testing in the clinic creates a feedback loop. Ideas become trials that generate rich data, which improves data models, and better models inform the next generation of ideas. The clinic is a central component of discovery. Even data from failed trials can be useful. Optimizing trial efficiency is about learning fast enough to make success more likely.',
            body_zh='更快速的臨床測試，會創造出一個回饋循環（feedback loop）：點子變成臨床試驗，產生豐富的資料；這些資料改善資料模型，而更好的模型，又回過頭來啟發下一代的點子。臨床（clinic）是整個「探索發現」過程中的核心環節。即使是失敗試驗所產生的資料，也可能具有價值。優化試驗效率的重點，在於學習的速度要夠快，才能提高成功的機率。',
            vocab=[
                ('feedback loop', '「回饋循環」，系統／工程領域核心概念，指輸出結果會回頭影響輸入，形成持續改善的循環。'),
                ('inform (v.)', '「為……提供依據、啟發」，並非只有「告知」的意思，常見於學術寫作（the data informs the next design）。'),
                ('make X more likely', '「讓 X 更有可能發生」，likely 當形容詞，常見於機率／預測語境。'),
            ],
        ),
        dict(
            title_en='Former SpaceX Engineers Are Building a Robotic Factory for Making Steel Parts',
            title_zh='前 SpaceX 工程師打造鋼鐵零件機器人工廠',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='1872 is a startup founded by three former SpaceX engineers that aims to manufacture steel parts using AI-driven software and robots. The company’s immediate goal is to establish a prototype factory that can automate most of the steel fabrication process for crucial infrastructure components by 2027. It aims to supply customers who are developing AI data centers or small modular nuclear reactors. 1872 will first focus on automating the production of rectangular steel skids.',
            body_zh='1872 是一家由三位前 SpaceX 工程師創立的新創公司，目標是運用 AI 驅動的軟體與機器人，來製造鋼鐵零件。該公司眼前的目標，是在 2027 年前建立一座原型工廠，將關鍵基礎設施零組件的鋼鐵加工流程，大部分自動化。它鎖定的客戶群，是正在開發 AI 資料中心或小型模組化核燃料反應爐的企業。1872 首先會專注於將「矩形鋼製滑橇（skid）」的生產流程自動化。',
            vocab=[
                ('AI-driven (adj.)', '複合形容詞「AI 驅動的」，-driven 表示「由……所驅動、主導」。'),
                ('fabrication (n.)', '製造業專有名詞「加工、製造」，尤指金屬／零件的成型加工程序。'),
                ('small modular nuclear reactor', '能源領域專有名詞「小型模組化（核）反應爐」，是新一代核能技術的代表詞彙。'),
            ],
        ),
        dict(
            title_en='Origin Code Hosting',
            title_zh='Cursor 推出程式碼代管平台 Origin（Tech 版報導）',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Cursor can now host code through its Origin platform. Origin is designed for agent scale. It supports repositories, pull requests, code browsing, and GitHub sync. GitHub repositories can sit alongside the ones Cursor hosts. Synced repositories update in real time, and users can choose what gets synced and disconnect a repository at any time. Origin is now rolling out in early beta to all paid plan users, except enterprise organizations whose admins opt out.',
            body_zh='Cursor 現在可以透過自家的 Origin 平台來代管程式碼了。Origin 的設計初衷，是為了因應「AI agent 規模」的需求。它支援儲存庫（repository）、pull request、程式碼瀏覽，以及與 GitHub 同步等功能。GitHub 上的儲存庫可以和 Cursor 代管的儲存庫並存。已同步的儲存庫會即時更新，使用者也能自行選擇要同步哪些內容，並可隨時中斷某個儲存庫的同步。Origin 目前正以「早期 Beta 版」的形式，推送給所有付費方案使用者，除非企業組織的管理員選擇退出。',
            vocab=[
                ('host (v.)', '「代管、託管」，在軟體工程語境常見（host code / host a website），與「主持、招待」的常見義不同。'),
                ('sit alongside', '片語，「與……並存、並列」，alongside 作介系詞用。'),
                ('roll out (phr. v.)', '片語動詞「推出、逐步發布」，產品／功能上線常用詞（rollout 當名詞則連寫）。'),
                ('opt out (phr. v.)', '片語動詞「選擇退出、不參與」，與 opt in（選擇加入）相對。'),
            ],
        ),
        dict(
            title_en='AI Usage Patterns in Software Teams',
            title_zh='軟體團隊的 AI 使用模式（Tech 版報導）',
            meta='原文閱讀時間：約 17 分鐘',
            body_en='Tens of thousands of teams build software inside Linear every day. The company is unusually well placed to see the entire workflow behind building a product. This post provides a picture of AI adoption within Linear’s customer base. It looks at who is using AI, how it reshapes where teams spend their time across Linear, and whether it has changed how much they ship.',
            body_zh='每天都有數以萬計的團隊，在 Linear 平台上進行軟體開發工作。這讓 Linear 這家公司處於一個非常特別的位置，得以觀察打造產品背後的完整工作流程。這篇文章描繪出 Linear 客戶群中 AI 採用情況的樣貌：探討究竟是誰在使用 AI、AI 如何重新形塑團隊在 Linear 上花費時間的方式，以及這是否改變了團隊實際「出貨（ship）」的產出量。',
            vocab=[
                ('tens of thousands of', '「數以萬計的」，注意 tens of thousands（數萬）與 ten thousand（一萬）的差別。'),
                ('be well placed <i>to V</i>', '片語，「處於有利位置去做某事」。'),
                ('reshape (v.)', '「重新形塑、改變……的樣貌」，re- 字首表示「重新」。'),
                ('ship (v.)', '軟體工程俚語，「出貨、正式發布產品／功能」。'),
            ],
        ),
        dict(
            title_en='Waymo vs Tesla: Two Ways to Build Self-Driving Cars',
            title_zh='Waymo 對決特斯拉：兩種打造自駕車的路線',
            meta='原文閱讀時間：約 17 分鐘',
            body_en='Waymo and Tesla have come up with different answers to the self-driving car problem. Both approaches depend heavily on machine learning, but they differ in how much gets fixed in advance. Waymo has a reported 220.6 million rider-only miles, while almost all of Tesla’s miles involve a driver who remains responsible for the vehicle. This article looks at the companies’ different approaches to self-driving and explains how they work.',
            body_zh='Waymo 與特斯拉，針對「自動駕駛」這個問題，分別提出了不同的解答。兩家公司的方法都高度仰賴機器學習，但差異在於：有多少部分是「事先寫死、預先設定好」的。根據報導，Waymo 已累積 2 億 2,060 萬英里的「純無人載客里程」，相較之下，特斯拉幾乎所有的行駛里程，都仍有一名「對車輛負責」的駕駛在場。本文探討兩家公司在自動駕駛上的不同做法，並解釋其運作原理。',
            vocab=[
                ('come up with', '片語，「想出、提出（解決方案、點子）」。'),
                ('depend heavily on', '「高度仰賴」，heavily 修飾 depend on，表示依賴程度很深。'),
                ('get fixed in advance', '「事先被固定／寫死」，fixed 在工程語境常指「預先設定、寫死的（規則）」。'),
                ('rider-only miles', '自駕車產業專有詞，「純載客里程數」，用來衡量自駕技術成熟度的關鍵指標。'),
            ],
        ),
    ]),
    dict(name_zh='軟體開發', name_en='TLDR Dev', date='2026-08-18', summary_head='軟體開發', articles=[
        dict(
            title_en='Origin Code Hosting',
            title_zh='Cursor 推出程式碼代管平台 Origin',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Cursor has introduced a new platform called Origin, which allows users to host their code with essential tools like repos, pull requests, code browsing, and GitHub synchronization. Users can create new repositories, sync existing GitHub repos, and manage pull requests, with integration options for deployment and continuous integration services like Vercel, Depot, and Buildkite.',
            body_zh='Cursor 推出了一個名為 Origin 的新平台，讓使用者可以代管自己的程式碼，並具備儲存庫、pull request、程式碼瀏覽，以及 GitHub 同步等核心工具。使用者可以建立新的儲存庫、同步既有的 GitHub 儲存庫，並管理 pull request，同時還能與 Vercel、Depot、Buildkite 等部署與持續整合服務進行串接。',
            vocab=[
                ('introduce (v.)', '「推出、引進」，在產品新聞中常見（introduce a new platform），比 launch 語氣稍微中性一些。'),
                ('essential tools', '「核心／必備工具」，essential 表示「不可或缺的」。'),
                ('synchronization (n.)', '「同步」，動詞是 synchronize，IT 領域高頻詞（常縮寫 sync）。'),
                ('sync (v.)', 'synchronize 的口語縮寫動詞，「同步」，工程師日常對話高頻用字。'),
                ('integration options', '「串接／整合選項」，integration 在軟體工程中指「系統間的整合」。'),
                ('continuous integration (CI)', '軟體工程專有名詞「持續整合」，是 DevOps 核心概念之一。'),
            ],
        ),
        dict(
            title_en='Red Agent Exploits Snowflake Vuln Missed by GitHub Copilot',
            title_zh='Wiz「紅色代理人」找出 GitHub Copilot 漏看的 Snowflake 漏洞',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Wiz Red Agent autonomously identified and exploited a critical GitHub Actions vulnerability in Snowflake\u2019s public repository, allowing unauthorized access to sensitive data in its internal Jira system just five days after the flaw was introduced. This incident shows the risks of relying on AI-assisted coding tools, which may inadvertently introduce vulnerabilities that can be quickly discovered and exploited by automated security agents.',
            body_zh='Wiz 公司的「Red Agent」自動化代理人，自主找出並利用了 Snowflake 公開儲存庫中一個嚴重的 GitHub Actions 漏洞，使攻擊者得以在漏洞被引入後短短五天內，未經授權存取其內部 Jira 系統中的敏感資料。這起事件顯示出仰賴 AI 輔助程式撰寫工具的風險——這類工具可能在不經意間引入漏洞，而這些漏洞又能被自動化資安代理人迅速發現並加以利用。',
            vocab=[
                ('autonomously (adv.)', '「自主地、自動地」，autonomous 的副詞形式，AI／機器人領域常見字。'),
                ('exploit (v.)', '資安領域專有動詞「利用（漏洞）進行攻擊」，與「剝削」的常見義不同，是資安新聞高頻字。'),
                ('unauthorized access', '「未經授權的存取」，固定搭配片語，資安領域核心詞彙。'),
                ('flaw (n.)', '「瑕疵、漏洞」，在資安語境中常與 vulnerability 互換使用。'),
                ('inadvertently (adv.)', '「不經意地、非故意地」，語氣正式，常見於描述意外造成的後果。'),
                ('automated security agents', '「自動化資安代理人」，agent 在 AI 語境中指能自主執行任務的系統。'),
            ],
        ),
        dict(
            title_en='Cut Your Fastify Log Volume With logController',
            title_zh='用 logController 降低 Fastify 的日誌量',
            meta='原文閱讀時間：約 11 分鐘',
            body_en='A Fastify health check polled every 5 seconds produces over a million log lines a month, but Fastify already has two built-in fixes rather than needing a new core option. The quick one is registering noisy routes in a plugin with logLevel: ‘silent’, though that mutes your own logs and failures too. The flexible one is subclassing LogController and overriding only the methods for the lines you care about.',
            body_zh='一個每 5 秒被輪詢一次的 Fastify 健康檢查端點（health check），一個月就能產生超過百萬行的日誌，但 Fastify 其實已經內建了兩種解法，不需要額外新增核心選項。快速的做法，是把「吵鬧」的路由註冊在一個 logLevel 設為 silent 的外掛（plugin）中——不過這樣一來，連你自己的日誌與錯誤訊息也會一併被靜音。更有彈性的做法，則是繼承（subclass）LogController，只覆寫（override）你真正在意的那些日誌方法。',
            vocab=[
                ('poll (v.)', '「輪詢」，軟體工程術語，指定期主動查詢某個狀態或端點。'),
                ('built-in (adj.)', '「內建的」，build + in 複合而成，與 add-on（外掛／附加）相對。'),
                ('override (v.)', '物件導向程式設計術語「覆寫」，指子類別重新定義父類別的方法。'),
            ],
        ),
        dict(
            title_en='How to Ship a Database Every Day',
            title_zh='如何做到「每天出貨一次資料庫」',
            meta='原文閱讀時間：約 13 分鐘',
            body_en='The implementation of a local state machine in each turbopuffer cluster allows for autonomous operation and management without needing direct access from the control plane. By using a custom API and a user-friendly dashboard, the system effectively manages over 100 database clusters while enabling rapid, multiple daily deployments and fleet operations.',
            body_zh='透過在每個 turbopuffer 叢集（cluster）中實作本地狀態機（local state machine），使其得以自主運作與管理，而不需要控制平面（control plane）直接介入存取。藉由一套客製化 API 與友善易用的儀表板，這套系統能有效管理超過 100 個資料庫叢集，同時支援一天多次的快速部署與艦隊（fleet）層級的維運。',
            vocab=[
                ('state machine', '電腦科學專有名詞「狀態機」，描述系統在不同狀態間依規則轉換的模型。'),
                ('control plane', '系統架構專有名詞「控制平面」，負責下達管理決策，與 data plane（資料平面）相對。'),
                ('fleet (n.)', 'IT 維運常用詞「艦隊」，引申指「一大批需要統一管理的伺服器／叢集」。'),
            ],
        ),
        dict(
            title_en='How Bluesky Draws Its Logo on Screenshots',
            title_zh='Bluesky 如何讓 logo 只出現在螢幕截圖裡',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Bluesky uses a creative method to display its logo on screenshots while hiding it during normal app use by using a UITextField with a specific property that masks content when a screenshot is taken. This technique prevents the logo from being visible when switching between apps, relying on iOS’s behavior of capturing a snapshot at the gesture’s start.',
            body_zh='Bluesky 用了一個很有創意的方法，讓自家 logo 只會出現在使用者的螢幕截圖中，平常使用 App 時卻不會顯示——做法是利用一個具備特定屬性的 UITextField，這個屬性會在螢幕截圖被擷取的當下，把內容遮蔽起來。這項技巧也讓 logo 在切換 App 時不會被看到，原理是利用 iOS 會在手勢（gesture）一開始時就擷取畫面快照（snapshot）的行為特性。',
            vocab=[
                ('mask (v.)', '「遮蔽、隱藏」，資安／UI 領域常見動詞，名詞則指「面具、遮罩」。'),
                ('switch between apps', '「在 App 之間切換」，iOS／Android 系統常見操作情境。'),
                ('rely on X’s behavior', '「仰賴 X 的（既有）行為特性」，常見於利用系統底層機制達成特殊效果的技巧描述。'),
            ],
        ),
        dict(
            title_en='AI;DR (AI; Didn’t Read)',
            title_zh='AI;DR（AI 生成的；懶得看）',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='The increasing prevalence of unedited AI-generated content has led to frustration among many, resulting in AI;DR (AI; didn’t read) as a way to dismiss such output. A new policy emphasizes the importance of reviewing and editing AI-generated materials to maintain quality and make sure that the human touch remains in communication.',
            body_zh='未經編修就直接發布的 AI 生成內容越來越普遍，這讓許多人感到厭煩，進而催生出「AI;DR」（AI 生成的內容；懶得看）這種用來打發此類產出的說法——仿照經典的 TL;DR（太長不看）而來。一項新政策強調，審閱與編修 AI 生成的素材有多麼重要，才能維持品質，也才能確保溝通內容中依然保有「人的溫度」。',
            vocab=[
                ('prevalence (n.)', '「普遍程度、盛行率」，形容詞是 prevalent，常見於描述某現象有多常見。'),
                ('dismiss (v.)', '「打發、不予理會」，此處指人們因不耐煩而直接忽略某類內容。'),
                ('the human touch', '慣用語「人的溫度、人味」，常用於對比機器／AI 產出與人工產出的差異。'),
            ],
        ),
        dict(
            title_en='GPT 5.6 Sol Is the Best "Vision" Model OpenAI Ever Released',
            title_zh='GPT 5.6 Sol 是 OpenAI 至今最強的「視覺」模型',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='OpenAI’s recent release of the GPT-5.6 lineup, particularly the Sol model, demonstrates advancements in vision capabilities, with improved performance in object detection and counting compared to its predecessor, GPT-5.5. While Sol excels in various visual tasks, it still faces challenges related to cost, latency, and occasional detection errors.',
            body_zh='OpenAI 近期推出的 GPT-5.6 系列模型，尤其是其中的 Sol 模型，在「視覺」能力上展現出明顯進步——相較於前一代 GPT-5.5，在物件偵測與計數任務上的表現都有所提升。雖然 Sol 在多項視覺任務上表現出色，但仍然面臨成本、延遲，以及偶爾出現偵測錯誤等挑戰。',
            vocab=[
                ('lineup (n.)', '「（產品）系列陣容」，常見於科技業描述一整批同時推出的產品線。'),
                ('predecessor (n.)', '「前一代、前身」，與 successor（後繼者）相對。'),
                ('excel in X', '「在 X 方面表現優異、擅長」，excel 當不及物動詞使用，後接介系詞 in/at。'),
            ],
        ),
        dict(
            title_en='Anthropic’s ‘Watermark’ Text Adulteration in Claude Is a Perversion of Writing',
            title_zh='Anthropic 的文字浮水印，是對寫作的一種扭曲',
            meta='原文閱讀時間：約 24 分鐘',
            body_en='Anthropic’s implementation of text watermarking in its Claude AI models is criticized for compromising the quality and clarity of generated text by introducing a system that subtly biases word choices to meet compliance with EU regulations. This approach is viewed as detrimental to writing integrity, as it prioritizes detection over quality.',
            body_zh='Anthropic 在 Claude 系列 AI 模型中導入的文字浮水印機制，遭到批評——因為這套系統會透過「悄悄地偏向特定用字選擇」的方式，來符合歐盟法規的合規要求，而這麼做，被認為犧牲了生成文字的品質與清晰度。這種做法被視為對「寫作的完整性」有害，因為它把「可被偵測性」的優先順序，擺在「品質」之前。',
            vocab=[
                ('adulteration (n.)', '「摻雜、（品質上的）混入雜質」，原用於食品／藥品領域，此處引申為「文字內容被摻入不必要的干擾」。'),
                ('compromise (v.)', '「損害、犧牲（品質等）」，注意此處不是「妥協」的常見義。'),
                ('detrimental to X', '「對 X 有害的」，形容詞，語氣正式，常見於學術／評論文章。'),
            ],
        ),
        dict(
            title_en='Hunk (GitHub Repo)',
            title_zh='Hunk（GitHub 開源專案）',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Hunk is a terminal-based diff viewer designed for reviewing changesets with a focus on interactivity and agent-assisted features, offering capabilities such as inline AI annotations and responsive layouts. It supports integration with popular version control systems and allows users to customize their experience through configuration files and extensions.',
            body_zh='Hunk 是一款以終端機（terminal）為介面的差異比對（diff）檢視工具，專為審閱程式碼變更集（changeset）而設計，著重於互動性與 AI agent 輔助功能，提供諸如「行內 AI 註解」與「自適應版面配置」等能力。它支援與主流版本控制系統整合，並允許使用者透過設定檔與擴充套件來客製化使用體驗。',
            vocab=[
                ('terminal-based (adj.)', '複合形容詞「以終端機為介面的」，與 GUI-based（圖形介面的）相對。'),
                ('changeset (n.)', '版本控制專有名詞「變更集」，指一次提交（commit）所包含的一組程式碼修改。'),
                ('inline (adj.)', '「行內的、內嵌的」，常見於程式設計語境（inline comment、inline function）。'),
            ],
        ),
        dict(
            title_en='State of Open Models: Summer 2026 Observations',
            title_zh='開源模型現況：2026 年夏季觀察',
            meta='原文閱讀時間：約 15 分鐘',
            body_en='Chinese labs now set the open-model size ceiling, yet downloads still belong overwhelmingly to small, years-old models. Qwen has become the community’s default base model with 151,448 derivatives, while the runtime layer grows far faster than the modeling core, letting trillion-parameter models run locally via llama.cpp. The new development is agents: they’re now the Hub’s top user, with agent traffic share swinging wildly month to month.',
            body_zh='目前是中國的實驗室在制定「開源模型規模」的天花板，但實際下載量，絕大多數卻仍然集中在那些規模較小、已經推出好幾年的舊模型身上。Qwen 已經成為社群預設採用的基礎模型，衍生版本（derivative）多達 151,448 個；與此同時，「執行環境層（runtime layer）」的成長速度，遠遠超過「模型核心」本身的成長——這讓兆（trillion）參數規模的模型，也能透過 llama.cpp 在本機端執行。而最新的發展趨勢是 agent：它們如今已成為 Hugging Face Hub 上使用量最高的族群，而且 agent 流量占比，每個月都在劇烈波動。',
            vocab=[
                ('ceiling (n.)', '原意「天花板」，商業／技術語境常引申為「上限」。'),
                ('overwhelmingly (adv.)', '「壓倒性地、絕大多數地」，常修飾佔比極高的情況。'),
                ('derivative (n.)', '此處指「衍生版本」，即以某個基礎模型為基底、經過微調產生的變體模型。'),
            ],
        ),
        dict(
            title_en='How Teams Build',
            title_zh='團隊如何打造軟體（AI 導入現況）',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='AI adoption in software development teams has increased across various functions, with engagement from executives and a consistent rise in usage among companies of all sizes. The introduction of AI tools has led to a dramatic increase in output through the use of coding agents, while also revealing a trend of non-engineers becoming more involved in coding and product development.',
            body_zh='在軟體開發團隊中，AI 的採用率已在各個職能領域全面提升，連高階主管都積極參與其中，而且無論公司規模大小，使用率都持續攀升。AI 工具的導入，透過「編碼 agent」的使用，大幅提升了產出量；同時也揭露出一個趨勢——越來越多「非工程背景」的人，開始參與到程式撰寫與產品開發的工作之中。',
            vocab=[
                ('engagement (n.)', '「參與投入（的程度）」，商業語境常見詞，不只是「訂婚」的意思。'),
                ('dramatic (adj.)', '「劇烈的、顯著的」，常用於形容數據變化幅度很大。'),
                ('non-engineers', '複合詞「非工程師／非工程背景人士」，non- 為否定字首。'),
            ],
        ),
    ]),
    dict(name_zh='人工智慧', name_en='TLDR AI', date='2026-08-18', summary_head='人工智慧', articles=[
        dict(
            title_en='Groq Raised $350 Million After Nvidia Deal',
            title_zh='Groq 在與 Nvidia 達成協議後，募得 3.5 億美元',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Groq raised $350 million at a $3.5 billion valuation after Nvidia licensed its technology and hired senior members of its team. The remaining company was rebuilding around an inference cloud combining Groq LPUs with Nvidia systems.',
            body_zh='在 Nvidia 授權其技術、並挖角其多名資深團隊成員之後，Groq 以 35 億美元的估值，完成了一輪 3.5 億美元的募資。剩餘的公司團隊，正圍繞著「結合 Groq LPU 與 Nvidia 系統的推論雲端服務」進行重組。',
            vocab=[
                ('valuation (n.)', '新創圈常用詞「估值」，常與募資金額一起出現（raised $X at a $Y valuation）。'),
                ('license (v.)', '「授權使用」，注意動詞 license 與名詞 licence/license 的拼寫在英式／美式英文中略有差異。'),
                ('hire senior members of X\u2019s team', '「挖角 X 團隊中的資深成員」，hire 在此語境隱含「挖角」的意味。'),
                ('the remaining company', '「剩餘的公司（團隊）」，remaining 表示「留下來的、剩餘的」部分。'),
                ('rebuild around X', '「圍繞 X 進行重組／重建」，around 在此作介系詞，表示「以……為核心」。'),
                ('inference cloud', 'AI 領域專有名詞「推論雲端（服務）」，inference 指「模型推論」，與 training（訓練）相對。'),
            ],
        ),
        dict(
            title_en='When Models Learn',
            title_zh='當模型開始「邊用邊學」',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Test-time training allows AI models to adapt by updating their weights during use, similar to a GPS learning a persistent traffic shortcut. This approach reduces memory needs by using a fixed-size set of weights instead of a linearly growing KV-cache but requires separate models for each user, increasing computational demands. The trade-off lies between the efficient handling of long contexts for personalized services and the broader accessibility of standard models.',
            body_zh='「測試時訓練」（test-time training）讓 AI 模型能在實際使用過程中，透過更新自身權重來進行調整，概念上類似導航軟體「學會」一條固定的抄近路捷徑。這種做法透過使用「固定大小的權重集合」，取代原本會線性成長的 KV 快取，藉此降低記憶體需求；但代價是，每個使用者都需要各自獨立的模型，進而提高運算需求。這當中的取捨在於：一邊是為個人化服務高效處理長上下文，另一邊則是標準模型更廣泛的可及性。',
            vocab=[
                ('test-time training', 'AI 領域專有名詞「測試時訓練」，指模型在推論（使用）階段仍持續更新權重，相對於傳統「訓練完就固定」的做法。'),
                ('weights (n.)', 'AI／機器學習領域專有名詞「權重」，是模型參數的核心組成。'),
                ('persistent (adj.)', '「持續存在的、固定不變的」，常見於描述長期保留的狀態或記憶。'),
                ('KV-cache', 'AI 領域專有名詞「鍵值快取」，是 Transformer 模型加速推論常用的機制。'),
                ('trade-off (n.)', '「取捨、權衡」，常見於工程決策討論（there\u2019s a trade-off between X and Y）。'),
                ('accessibility (n.)', '「可及性、易取得程度」，字根 access（存取）＋ -ibility。'),
            ],
        ),
        dict(
            title_en='Anthropic’s Revenue to Exceed $65 Billion',
            title_zh='Anthropic 營收有望突破 650 億美元（AI 版快訊）',
            meta='原文閱讀時間：約 1 分鐘',
            body_en='Anthropic was reportedly on track to exceed $65 billion in annualized revenue based on its current performance, more than seven times its pace at the end of the previous year.',
            body_zh='根據報導，以 Anthropic 目前的營運表現推算，其年化營收有望超過 650 億美元——是去年底營收步調的七倍以上。',
            vocab=[
                ('be on track to V', '片語，「照目前進度看有望達成……」，常見於財經／專案進度描述。'),
                ('more than X times', '「超過 X 倍」，倍數表達的固定句型。'),
            ],
        ),
        dict(
            title_en='Cursor Launches Origin Code Hosting Platform as GitHub Outage Exposes Opening in AI Coding Race',
            title_zh='GitHub 中斷之際，Cursor 順勢推出 Origin 程式碼代管平台',
            meta='原文閱讀時間：約 16 分鐘',
            body_en='Cursor is currently rolling out its Origin code hosting platform to paid users. The launch coincided with a GitHub outage that lasted over six hours. Origin allows users to connect GitHub repositories, so they do not have to move platforms. Allowing GitHub to stay as a source of truth means it costs nothing for organizations to try Origin and nothing breaks if it is abandoned.',
            body_zh='Cursor 目前正將其程式碼代管平台 Origin，推送給付費使用者。這次發表的時間點，恰巧與一次長達六小時以上的 GitHub 服務中斷「撞期」。Origin 讓使用者能直接連接既有的 GitHub 儲存庫，因此不必真的搬遷平台。讓 GitHub 繼續作為「真相來源（source of truth）」，意味著組織嘗試 Origin 幾乎不需要成本，即使日後放棄不用，也不會對現有系統造成任何破壞。',
            vocab=[
                ('coincide with X', '「與 X 同時發生、撞期」，常見於描述兩件事在時間上恰巧重疊。'),
                ('source of truth', '軟體工程慣用語「真相來源」，指系統中被視為權威、其他地方都應與之同步的資料源頭。'),
                ('cost nothing to V', '「做……不需要任何成本」，常見於強調風險／門檻極低的商業語境。'),
            ],
        ),
        dict(
            title_en='Testing Fable vs Sol in Terms of Taste (They Are Both Bad)',
            title_zh='比較 Fable 與 Sol 的「品味」（結果兩個都不行）',
            meta='原文閱讀時間：約 40 分鐘',
            body_en='Researchers built a small harness and gave Fable 5 and Sol 5.6 the same jobs to evaluate their taste and creativity. The models had to follow the same creative process to build four different 15-second-long videos - three ads and one mini-documentary. The experiment showed that we are still far from having frontier models building production-ready concepts and videos autonomously. They can be creative and helpful for exploring and refining ideas, but they can’t replace human judgment, for now.',
            body_zh='研究人員打造了一套小型測試框架（harness），讓 Fable 5 與 Sol 5.6 執行相同的任務，藉此評估這兩個模型的「品味」與創造力。這兩個模型都必須遵循同一套創作流程，分別產出四支各 15 秒長的影片——三支廣告，以及一支迷你紀錄片。這項實驗顯示，距離「頂尖模型能自主打造出可直接上線的概念與影片」這個目標，我們還有很長一段路要走。這些模型在探索與精煉點子的過程中，確實能發揮創意、提供幫助，但就目前而言，仍無法取代人類的判斷力。',
            vocab=[
                ('harness (n.)', '工程領域引申義「測試框架、測試裝置」，原意為「馬具、束縛帶」。'),
                ('production-ready (adj.)', '複合形容詞「可直接上線／量產等級的」，常見於軟體工程描述成熟度。'),
                ('for now', '片語，「就目前而言、暫時」，暗示情況未來可能改變。'),
            ],
        ),
        dict(
            title_en='Qwen3.8 vs Qwen3.6 vs Gemma 4 on a 24GB GPU',
            title_zh='24GB GPU 下的 Qwen3.8 vs Qwen3.6 vs Gemma 4 實測',
            meta='原文閱讀時間：約 10 分鐘',
            body_en='A hands-on comparison tested three dense multimodal models under the same 24GB GPU constraint, including memory headroom at longer contexts. The measurements are useful, but Qwen3.8 was already covered, and the source’s commercial independence requires validation.',
            body_zh='一項實測比較，在同樣「24GB GPU 記憶體」的限制條件下，測試了三款稠密（dense）多模態模型的表現，並涵蓋在更長上下文情況下的可用記憶體餘裕。這些量測數據具有參考價值，不過 Qwen3.8 先前已經被報導過，而且這個資料來源是否具備商業獨立性，仍有待進一步查證。',
            vocab=[
                ('dense (adj.)', 'AI 領域專有名詞「稠密的」，指模型每次推論都會用到全部參數，與 MoE（稀疏）架構相對。'),
                ('headroom (n.)', '工程領域常見詞「餘裕空間」，引申為「還能承受的緩衝空間」。'),
                ('commercial independence', '「商業獨立性」，指資訊來源是否不受特定廠商利益影響。'),
            ],
        ),
        dict(
            title_en='The Deadline Dividend',
            title_zh='截止期限紅利',
            meta='原文閱讀時間：約 13 分鐘',
            body_en='Latency measures time to a useful result. Higher speed can finish work sooner, or fit more work before the same deadline. That useful extra work is the deadline dividend. It can be used to fund another strategy, a critic, a verification pass, or recovery after failure.',
            body_zh='延遲（latency）衡量的是「得到有用結果所需的時間」。更快的速度，可以讓工作更早完成，或是在同一個截止期限內塞入更多工作量。這些額外多出來、而且有用的工作量，就是所謂的「截止期限紅利（deadline dividend）」。這份紅利，可以被用來資助另一套策略、一個「評論者（critic）」機制、一次驗證流程，或是失敗後的復原程序。',
            vocab=[
                ('latency (n.)', '系統工程核心指標「延遲」，指從請求發出到得到回應所花費的時間。'),
                ('dividend (n.)', '原指「股利、股息」，此處引申為「（因效率提升而）多出來的紅利、餘裕」。'),
                ('fund (v.)', '此處作動詞「資助、提供資源支持」，而非名詞「基金」。'),
            ],
        ),
        dict(
            title_en='Warp Agent Memory (Research Preview)',
            title_zh='Warp 推出 Agent 記憶功能（研究預覽版）',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='Warp introduced persistent memory shared across agent harnesses, machines, and teammates, with provenance and configurable access.',
            body_zh='Warp 推出了一套「持久記憶（persistent memory）」功能，能在不同的 agent 執行框架、不同機器，以及不同團隊成員之間共享，並具備來源追溯（provenance）與可設定的存取權限控管。',
            vocab=[
                ('persistent (adj.)', '「持久的、不會消失的」。'),
                ('provenance (n.)', '「來源、出處」，原用於藝術品鑑定領域，此處引申為「（資料）可追溯的來源紀錄」。'),
                ('configurable (adj.)', '「可設定的、可組態調整的」，configure（設定）+ -able。'),
            ],
        ),
        dict(
            title_en='How Software Teams Use AI in 2026',
            title_zh='2026 年軟體團隊如何使用 AI（AI 版報導）',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Linear analyzed AI adoption across tens of thousands of software teams, covering usage by role and company size as well as changes in planning, issue creation, pull requests, and coding-agent activity.',
            body_zh='Linear 分析了數萬個軟體團隊的 AI 採用狀況，涵蓋不同角色與公司規模下的使用情形，以及在規劃（planning）、議題（issue）建立、pull request，以及編碼 agent 活動量上所發生的變化。',
            vocab=[
                ('adoption (n.)', '「採用率、導入程度」。'),
                ('issue (n.)', '軟體專案管理術語「議題、任務單」，泛指待辦事項或問題追蹤系統中的一個項目。'),
                ('coding-agent activity', '複合名詞「編碼 agent 活動量」，指 AI 編碼代理人執行任務的頻率與規模。'),
            ],
        ),
        dict(
            title_en='dig.bench (Website)',
            title_zh='dig.bench（AI 遊戲規則探索基準測試）',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='dig.bench is a benchmark that measures whether an agent can experiment to discover a game’s unknown rules. It contains 70 text-based games, 21 that have been publicly released. Progress is scored by whether the game can be beaten within a limited number of steps. Humans can make the discoveries necessary to solve even the hardest games, while the best models struggle to beat games in the top tier.',
            body_zh='dig.bench 是一套基準測試（benchmark），用來衡量 AI agent 是否能透過「實驗嘗試」，找出一款遊戲中未知的規則。它總共包含 70 款文字型遊戲，其中 21 款已公開釋出。進度評分的方式，是看該遊戲能否在有限的步數內被破關。人類玩家能夠做出破解最困難遊戲所需的發現，但即使是最頂尖的模型，也很難破解最高難度等級的遊戲。',
            vocab=[
                ('benchmark (n.)', '「基準測試」，AI／工程領域用來衡量系統效能或能力的標準化測試。'),
                ('text-based (adj.)', '複合形容詞「文字型的」，指以純文字互動為主的遊戲／介面。'),
                ('struggle to V', '片語，「很難做到……、在……上遇到困難」。'),
            ],
        ),
        dict(
            title_en='Scaling Data Repetition for LLMs',
            title_zh='大型語言模型的資料重複使用規模化研究',
            meta='原文閱讀時間：約 22 分鐘',
            body_en='The optimal amount of high-quality domain data repetition increased mildly with model size at a fixed tokens-per-parameter ratio. Smaller proxy models could therefore help estimate repetition schedules for larger models, with lower-loss domains generally tolerating more reuse.',
            body_zh='在固定「每參數對應 token 數」比例的情況下，高品質領域資料的「最佳重複使用次數」，會隨著模型規模增加而略微上升。因此，較小的代理模型（proxy model），可以用來協助估算大型模型所需的資料重複使用排程；而損失值（loss）較低的領域，通常能夠承受更多次的重複使用。',
            vocab=[
                ('optimal (adj.)', '「最佳的、最適的」，常見於工程／數學語境描述最理想的參數設定。'),
                ('proxy model', 'AI 領域慣用語「代理模型」，指用較小／較便宜的模型來預估大型模型行為的做法。'),
                ('tolerate (v.)', '「容忍、承受」，此處指資料或系統在不受負面影響的前提下，能承受的重複使用程度。'),
            ],
        ),
        dict(
            title_en='Teaching Everyone to Fish for Tokens',
            title_zh='教每個人如何「釣」到 Token',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='Open-source AI models face a precarious future due to high capital requirements, with Nvidia heavily investing to drive demand for its chips. The open-source recipe’s economic viability is uncertain, potentially leading to a fork focused on efficiency and specialization rather than competing with closed models in lucrative sectors. Meta’s strategy to release models like Muse Spark 1.2 as open-weights could disrupt competitors, as they commoditize their complements differently from Nvidia’s approach of fostering a self-sustaining token ecosystem.',
            body_zh='由於資本需求極高，開源 AI 模型的未來其實相當不穩定，而 Nvidia 也正大舉投資，藉此拉抬對自家晶片的需求。開源這套「做法配方」的經濟可行性，目前仍充滿不確定性，未來很可能會走向分岔（fork）——轉而聚焦在效率與專精化，而不是在利潤豐厚的領域中直接與閉源模型競爭。Meta 選擇以「開放權重（open-weights）」形式釋出像 Muse Spark 1.2 這樣的模型，這項策略可能會擾亂競爭對手的布局，因為這種做法「商品化互補品」的方式，與 Nvidia 那套「培植自我維持的 token 生態系」的策略截然不同。',
            vocab=[
                ('precarious (adj.)', '「不穩定的、岌岌可危的」，常見於描述財務或處境上的高風險狀態。'),
                ('viability (n.)', '「可行性」，形容詞是 viable（可行的）。'),
                ('commoditize (v.)', '經濟學術語「使商品化」，指讓原本具差異化的產品變得像大宗商品一樣可互換。'),
            ],
        ),
        dict(
            title_en='Own Your Intelligence: A How-To Guide',
            title_zh='自主擁有你的智慧：實作指南',
            meta='原文閱讀時間：約 7 分鐘',
            body_en='AI companies should selectively own their intelligence when frontier APIs constrain cost, latency, proprietary data, or strategic control. The roadmap is evals, custom harnesses, targeted post-training, and online learning loops that turn production trajectories into continuously improving domain-specific models.',
            body_zh='當「使用頂尖模型的 API」在成本、延遲、專有資料，或策略主導權等方面造成限制時，AI 公司就應該選擇性地「自主擁有」自己的智慧（模型）。具體路線圖包括：建立評測（evals）機制、打造客製化測試框架、進行有針對性的後訓練（post-training），以及建立線上學習循環，把正式環境中產生的實際軌跡（trajectory）資料，轉化為能持續改進的領域專屬模型。',
            vocab=[
                ('selectively (adv.)', '「選擇性地」，強調並非全面而是有挑選地進行。'),
                ('constrain (v.)', '「限制、約束」，名詞是 constraint（限制條件）。'),
                ('post-training (n.)', 'AI 領域專有名詞「後訓練」，指在模型完成預訓練之後再針對特定任務進行的微調訓練。'),
            ],
        ),
        dict(
            title_en='One AI Module Faked 86% of a Pipeline’s Accuracy Gains by Feeding Another the Answers',
            title_zh='一個 AI 模組靠「洩題」偽造出 86% 的準確率提升',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='Compound LLM pipelines can gain accuracy while specialized modules quietly abandon assigned roles, creating ‘role drift’ invisible to system-level metrics. Role Anchor constrains this behavior. 86% of one pipeline’s apparent RL gains disappeared when its decomposer stayed in role.',
            body_zh='複合式 LLM 流水線（pipeline）有可能在整體準確率提升的同時，其中某個專責模組卻悄悄「不務正業」、偏離了原本被指派的角色——這種現象稱為「角色漂移（role drift）」，而且從系統層級的整體指標上完全看不出來。「Role Anchor」這個方法，能夠約束這種行為。當某個負責「拆解問題」的模組被強制維持在原本角色時，原本某條流水線看似因強化學習（RL）而取得的準確率提升，有 86% 直接消失。',
            vocab=[
                ('compound (adj.)', '此處作形容詞「複合式的、由多個部分組成的」，而非動詞「使加劇」。'),
                ('abandon (v.)', '「放棄、拋棄」，此處指模組偏離了原本被賦予的職責。'),
                ('invisible to X', '「對 X 而言不可見的」，常用於描述某問題無法被特定監控機制偵測到。'),
            ],
        ),
    ]),
    dict(name_zh='資訊安全', name_en='TLDR InfoSec', date='2026-08-18', summary_head='資訊安全', articles=[
        dict(
            title_en='Beacon CRM Confirms Full Database Theft After AWS Access Key Breach',
            title_zh='Beacon CRM 證實整個資料庫遭竊，起因為 AWS 金鑰外洩',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Beacon CRM confirmed an attacker used an AWS access key exposed in public JavaScript. Cost data showed transfers matching all stored records and attachments. With valid credentials, the attackers were able to decrypt protected data during download. Beacon rotated keys, removed client-side secrets, and added endpoint and cloud monitoring.',
            body_zh='Beacon CRM 證實，攻擊者利用了一組暴露在「公開 JavaScript 程式碼」中的 AWS 存取金鑰。成本資料顯示，外洩的傳輸紀錄與所有儲存的資料紀錄及附件完全吻合。由於攻擊者持有合法的憑證，他們得以在下載過程中將受保護的資料解密。Beacon 已經輪換金鑰、移除前端（client-side）程式碼中的機密資訊，並新增了端點與雲端監控機制。',
            vocab=[
                ('access key', '雲端／資安領域專有名詞「存取金鑰」，用於驗證身分並授權存取雲端資源（如 AWS）。'),
                ('expose (v.)', '資安領域高頻動詞「暴露、洩漏」，常用於描述機密資訊意外外流（expose a secret）。'),
                ('credentials (n.)', '「憑證」，泛指帳號、金鑰、密碼等用於身分驗證的資訊，恆為複數形式。'),
                ('decrypt (v.)', '「解密」，字首 de- 表示「解除」，對應 encrypt（加密）。'),
                ('rotate keys', '資安領域固定用語「輪換金鑰」，指定期更換憑證以降低外洩風險。'),
                ('client-side (adj.)', '軟體工程專有名詞「前端／客戶端的」，與 server-side（伺服器端）相對。'),
            ],
        ),
        dict(
            title_en='OWASP Top 10 CI/CD Security Risks',
            title_zh='OWASP CI/CD 十大資安風險',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='The OWASP Top 10 CI/CD Security Risks initiative provides a framework to help defenders identify and secure vulnerabilities within continuous integration and delivery environments. The list catalogs critical risks including dependency-chain abuse, poisoned pipeline execution, inadequate access controls, credential hygiene issues, artifact integrity gaps, insecure configurations, and insufficient logging. The project provides recommended security controls and references to help organizations mitigate identified CI/CD risks.',
            body_zh='OWASP 的「CI/CD 十大資安風險」計畫，提供了一套框架，協助防守方在持續整合與交付（CI/CD）環境中，找出並修補安全漏洞。這份清單列出了多項關鍵風險，包括依賴鏈濫用、遭下毒的流水線（pipeline）執行、存取控制不足、憑證衛生問題、產出物（artifact）完整性缺口、不安全的組態設定，以及日誌記錄不足。該專案也提供了建議的資安控管措施與參考資源，協助組織緩解已辨識出的 CI/CD 風險。',
            vocab=[
                ('initiative (n.)', '「倡議、專案計畫」，常用於描述組織性的長期行動方案。'),
                ('catalog (v.)', '「（有系統地）列出、編目」，原為名詞「目錄」，此處作動詞用。'),
                ('dependency-chain abuse', '資安專有名詞「依賴鏈濫用」，指攻擊者利用軟體套件間的依賴關係進行攻擊（如供應鏈攻擊）。'),
                ('poisoned pipeline execution', '資安專有名詞「遭下毒的流水線執行」，指攻擊者竄改 CI/CD pipeline 使其執行惡意程式碼。'),
                ('credential hygiene', '資安慣用語「憑證衛生」，指妥善管理帳密／金鑰生命週期的良好習慣。'),
                ('mitigate (v.)', '「緩解、降低（風險或影響）」，資安與風險管理領域高頻字，注意與 eliminate（徹底消除）語氣不同。'),
            ],
        ),
        dict(
            title_en='Wallet Provider SafePal Says Data Breach Exposed Personal Info of Nearly 40,000 Customers',
            title_zh='錢包業者 SafePal：資料外洩事件影響近 4 萬名客戶',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='This past weekend, crypto wallet provider SafePal announced that an authorization flaw in its order tracking system allowed unauthorized access to personal data belonging to nearly 40k customers. The breached data includes customer names, email and shipping addresses, phone numbers, and purchase details, but did not involve any wallet credentials, financial details, or government IDs.',
            body_zh='上週末，加密貨幣錢包業者 SafePal 宣布，其訂單追蹤系統中的一個授權瑕疵，導致近 4 萬名客戶的個人資料遭到未經授權的存取。外洩資料包含客戶姓名、電子郵件與收件地址、電話號碼，以及購買明細，但並未涉及任何錢包憑證、財務資訊，或政府核發的身分證件。',
            vocab=[
                ('authorization flaw', '資安專有名詞「授權瑕疵」，指系統在判斷「誰能存取什麼」的邏輯上出現漏洞。'),
                ('breached data', '「外洩的資料」，breach 當動詞／名詞皆指「（資安）突破、外洩事件」。'),
                ('involve (v.)', '「涉及」，常見於描述某事件牽涉的範圍。'),
            ],
        ),
        dict(
            title_en='Sogang University Hit By Personal Information Breach of 180,000',
            title_zh='韓國西江大學爆發資料外洩，影響 18 萬人',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='South Korea’s Sogang University disclosed a data breach affecting 180k students, alumni, and employees. The compromised information includes student identification numbers, names, affiliations, email addresses, mobile phone numbers, and encrypted passwords for the university’s integrated login system.',
            body_zh='韓國西江大學（Sogang University）揭露了一起資料外洩事件，影響 18 萬名學生、校友與教職員。外洩資訊包括學號、姓名、所屬單位、電子郵件地址、手機號碼，以及該校整合登入系統的加密密碼。',
            vocab=[
                ('disclose (v.)', '「揭露、公開」，資安事件通報常用正式動詞。'),
                ('affecting X', '現在分詞當形容詞用，「影響到 X 的」，修飾前面的 breach。'),
                ('compromised (adj.)', '資安領域常見形容詞「已被攻破／外洩的」。'),
            ],
        ),
        dict(
            title_en='CSS: The Bomb Inside Your Inbox',
            title_zh='CSS：藏在你信箱裡的炸彈',
            meta='原文閱讀時間：約 20 分鐘',
            body_en='Portswigger demonstrates CSS and HTML attacks against webmail sanitizers. Outlook labels can trigger interface actions, while a CSS parser flaw enables arbitrary CSS injection and a spoofed login screen that captures passwords in Firefox. Yahoo Mail and AOL Mail allowed pasted CSS to race sanitization, exposing Medium email-login tokens. Fastmail image-proxy flaws enabled view tracking, ProtonMail could reveal an IP address, and hidden prompt instructions in email content directing Atlas browser actions. The recommended security controls include sandboxed iframes, restrictive allowlists, blocked image requests, and filtering dangerous selectors.',
            body_zh='Portswigger 展示了針對「網頁版信箱過濾機制（sanitizer）」的 CSS 與 HTML 攻擊手法。Outlook 的標籤功能可能觸發介面動作；而一個 CSS 解析器的瑕疵，則能讓攻擊者任意注入 CSS，並在 Firefox 中偽造出一個能夠竊取密碼的假登入畫面。Yahoo Mail 與 AOL Mail 則允許貼上的 CSS，在「過濾程序」完成之前搶先執行（race），進而外洩 Medium 的電子郵件登入權杖（token）。Fastmail 的圖片代理伺服器瑕疵，能被用來追蹤使用者是否讀信；ProtonMail 可能洩漏使用者的 IP 位址；而信件內容中隱藏的提示指令，甚至能操控 Atlas 瀏覽器執行動作。建議的資安控管措施包括：使用沙盒化（sandboxed）的 iframe、限制性的允許清單（allowlist）、封鎖圖片請求，以及過濾危險的 CSS 選擇器（selector）。',
            vocab=[
                ('sanitizer (n.)', '資安領域專有名詞「過濾／消毒機制」，指清除輸入內容中危險成分的程序。'),
                ('spoofed (adj.)', '「偽造的、假冒的」，spoof 當動詞指「偽裝、冒充」。'),
                ('sandboxed (adj.)', '資安領域專有名詞「沙盒化的」，指在隔離環境中執行以限制其影響範圍。'),
            ],
        ),
        dict(
            title_en='Attacking SAM and Extracting Hashes With 7z',
            title_zh='用 7z 攻擊 SAM 並擷取雜湊值',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='7z is an archiving and unarchiving tool that is incredibly popular on Windows systems. Users can extract hives by typing \\\\.\\ in the 7z address bar and then navigating to PhysicalDrive0 followed by 0.ntfs to locate the system hives which can be extracted to a separate system and then cracked. This technique requires GUI access as 7z can only parse physical disks and NTFS partitions through the File Manager GUI.',
            body_zh='7z 是一款在 Windows 系統上極受歡迎的封裝與解壓縮工具。使用者只要在 7z 的網址列輸入 \\\\.\\，接著依序瀏覽至 PhysicalDrive0、再進入 0.ntfs，就能定位到系統的「登錄檔配置單元（hive）」，並將其擷取到另一台系統上進行破解。這項技巧需要圖形介面（GUI）的存取權限，因為 7z 只能透過檔案管理員的 GUI，來解析實體磁碟與 NTFS 分割區。',
            vocab=[
                ('archiving (n.)', '「封裝、壓縮歸檔」，archive 當動詞指「將檔案打包保存」。'),
                ('hive (n.)', 'Windows 系統專有名詞「登錄檔配置單元」，是 Windows Registry 的組成單位。'),
                ('crack (v.)', '資安領域常見動詞「破解」，常用於描述破解密碼或加密內容。'),
            ],
        ),
        dict(
            title_en='Nullock (GitHub Repo)',
            title_zh='Nullock（GitHub 開源專案）',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Nullock is a free, self-hosted alternative to Burp Suite Pro that contains an MITM proxy with a full active scanner (SQLi/XSS/SSRF/XXE/SSTI/smuggling), recon, OAST, nuclei-style templates, and a CI security gate.',
            body_zh='Nullock 是一款免費、可自行架設（self-hosted）的工具，作為 Burp Suite Pro 的替代方案，內建一個具備完整主動掃描器的中間人（MITM）代理伺服器——涵蓋 SQL 注入、XSS、SSRF、XXE、SSTI、走私攻擊（smuggling）等多種弱點掃描，並提供偵察（recon）、OAST、nuclei 風格範本，以及 CI 資安關卡功能。',
            vocab=[
                ('self-hosted (adj.)', '複合形容詞「自行架設／自建的」，與雲端代管服務（SaaS）相對。'),
                ('MITM proxy', '資安專有名詞「中間人代理」，常用於攔截與檢視流量。'),
                ('security gate', '「資安關卡」，指在流程（如 CI/CD）中設下的安全檢查點。'),
            ],
        ),
        dict(
            title_en='Fibratus (GitHub Repo)',
            title_zh='Fibratus（GitHub 開源專案）',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Fibratus detects and eradicates advanced attacker tradecraft, malware, and emerging threats by scrutinizing and asserting a wide spectrum of system events against a behavior-driven rule engine and YARA memory scanner.',
            body_zh='Fibratus 透過檢視大量系統事件，並將其比對「行為驅動規則引擎」與 YARA 記憶體掃描器，來偵測並清除進階攻擊者手法（tradecraft）、惡意軟體，以及新興威脅。',
            vocab=[
                ('eradicate (v.)', '「根除、徹底清除」，語氣比 remove（移除）更強烈。'),
                ('tradecraft (n.)', '情報／資安領域專有名詞「（諜報／攻擊）手法」，借用自間諜活動的用語。'),
                ('scrutinize (v.)', '「仔細檢視、審查」，語氣正式，常見於資安／合規語境。'),
            ],
        ),
        dict(
            title_en='deadair (GitHub Repo)',
            title_zh='deadair（GitHub 開源專案）',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='deadair is an open-source tool that audits live SIEM rule inventories to identify active detections that are failing silently due to missing, stale, or schema-incompatible telemetry. By utilizing read-only metadata credentials, the tool resolves rule inputs against backend semantics to verify index resolution, document freshness, and ingest lag across Elastic Security and OpenSearch Security Analytics environments.',
            body_zh='deadair 是一款開源工具，用來稽核正在運作中的 SIEM（資安事件管理系統）規則清單，找出那些因為遙測資料（telemetry）缺失、過時，或格式不相容，而正在「靜默失效」的偵測規則。這項工具會利用唯讀的中繼資料憑證，將規則的輸入條件比對後端的實際語意，藉此驗證索引解析、文件新鮮度，以及跨 Elastic Security 與 OpenSearch Security Analytics 環境的資料擷取延遲（lag）狀況。',
            vocab=[
                ('audit (v.)', '「稽核、審查」，資安／財務領域常見動詞，指有系統地檢查是否符合規範。'),
                ('fail silently', '慣用語「靜默失效」，指系統失效時沒有發出任何警訊，使問題不易被察覺。'),
                ('stale (adj.)', '「過時的、不新鮮的」，常見於描述資料因太久未更新而失去參考價值。'),
            ],
        ),
        dict(
            title_en='Trivy, Not LiteLLM Behind the 2,500 Org Compromise',
            title_zh='真正的元凶其實是 Trivy，不是 LiteLLM',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='SOCRadar tied 2,085 of 2,188 tracked data exposures to the earlier Trivy compromise. Data collection ran from March 19 to March 24 and showed that malicious LiteLLM packages appeared only for 40 minutes on March 24. The worm stole tokens, keys, and credentials from CI/CD systems, then used developer secrets to poison more packages. Stolen datasets are now being sold on Telegram.',
            body_zh='SOCRadar 已將所追蹤到的 2,188 起資料外洩事件中，有 2,085 起，歸咎於先前的 Trivy 資安事件。資料蒐集期間為 3 月 19 日至 3 月 24 日，結果顯示：惡意的 LiteLLM 套件，其實只在 3 月 24 日短短 40 分鐘內出現過。這隻「蠕蟲（worm）」從 CI/CD 系統中竊取權杖、金鑰與憑證，接著再利用開發者的機密資訊，去「下毒」更多的套件。目前這些遭竊的資料集，正在 Telegram 上被兜售。',
            vocab=[
                ('tie X to Y', '片語，「將 X 歸咎於 Y、把 X 與 Y 連結起來」，常見於事件調查報告。'),
                ('worm (n.)', '資安專有名詞「蠕蟲」，一種能自我複製、擴散的惡意程式。'),
                ('poison (v.)', '「（惡意）污染、下毒」，供應鏈攻擊常見說法。'),
            ],
        ),
        dict(
            title_en='Mozilla Revokes Firefox Signing Key After Unencrypted Copy Lands in GitHub',
            title_zh='未加密金鑰誤傳 GitHub，Mozilla 撤銷 Firefox 簽署金鑰',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Mozilla revoked and replaced a GPG private subkey after an unencrypted copy of it was pushed to a private GitHub repository. The key signed Firefox and Thunderbird Linux tarballs, RPM packages, and checksums. Mozilla found no unauthorized access in the available audit records, but manual signature verifiers must import the new key and revoke the old key.',
            body_zh='在一份未加密的 GPG 私密子金鑰副本，被意外推送（push）到一個私有 GitHub 儲存庫之後，Mozilla 已將該金鑰撤銷並更換為新金鑰。這把金鑰原本用於簽署 Firefox 與 Thunderbird 的 Linux 壓縮檔（tarball）、RPM 套件，以及校驗碼（checksum）。Mozilla 表示，在現有的稽核紀錄中，並未發現任何未經授權的存取行為，但手動驗證簽章的使用者，仍必須匯入新金鑰，並撤銷舊金鑰。',
            vocab=[
                ('revoke (v.)', '資安／憑證領域專有動詞「撤銷」，常見於 revoke a key/certificate。'),
                ('push (v.)', '版本控制術語「推送」，指將本地變更上傳至遠端儲存庫（git push）。'),
                ('checksum (n.)', '電腦科學專有名詞「校驗碼」，用於驗證檔案在傳輸過程中是否遭到竄改或損毀。'),
            ],
        ),
    ]),
    dict(name_zh='產品管理', name_en='TLDR Product', date='2026-08-18', summary_head='產品管理', articles=[
        dict(
            title_en='What People *Really* Think About IC Work',
            title_zh='大家對「個人貢獻者」工作的真實想法',
            meta='原文閱讀時間：約 20 分鐘',
            body_en='Most tech workers want more IC work, but pay and influence keep many in management. High-impact IC roles could offer a better path by rewarding autonomy and business impact without requiring people management.',
            body_zh='大多數科技業工作者，其實更想從事「IC（個人貢獻者）」的工作，但薪酬與影響力，讓許多人仍選擇留在管理職。「高影響力的 IC 職位」或許能提供一條更好的路徑——不需要管理他人，也能因自主性與對業務的實質影響而獲得應有的獎勵。',
            vocab=[
                ('IC (individual contributor)', '科技業常用縮寫「個人貢獻者」，指不帶領團隊、專注於專業產出的職位角色，與 manager（管理職）相對。'),
                ('keep sb. in N', '「讓某人留在 N（某狀態／職位）」，keep 在此作使役動詞用，表示「使……維持」。'),
                ('high-impact (adj.)', '複合形容詞「高影響力的」，impact 當名詞指「影響力、衝擊」。'),
                ('be rewarded (v.)', '「獲得獎勵、回饋」被動語態，「因……而獲得回報」。'),
                ('autonomy (n.)', '「自主性」，職場／心理學領域常見詞，形容詞為 autonomous。'),
                ('without requiring <i>V-ing</i>', '「不需要做……」，without 後接動名詞，requiring 也接動名詞 managing，是雙層動名詞結構，文法上較進階。'),
            ],
        ),
        dict(
            title_en='Nvidia\u2019s Risky Business',
            title_zh='Nvidia 的高風險生意',
            meta='原文閱讀時間：約 12 分鐘',
            body_en='AI\u2019s infrastructure boom is relying on increasingly risky financing. Nvidia can keep the buildout going by attracting new pools of capital, but the strategy depends on AI revenues growing fast enough to justify the investment.',
            body_zh='AI 基礎建設的榮景，正日益仰賴風險愈來愈高的融資方式。Nvidia 可以透過吸引新的資金池，持續推動基礎建設的擴張，但這個策略能否成功，取決於 AI 相關營收的成長速度，是否足以證明這些投資是合理的。',
            vocab=[
                ('infrastructure boom', '「基礎建設榮景」，boom 指「（產業、經濟）快速蓬勃發展」。'),
                ('increasingly (adv.)', '「日益、越來越」，常修飾形容詞或動詞，表示程度隨時間遞增。'),
                ('buildout (n.)', '「（基礎設施的）建設、擴建」，常見於科技／電信產業報導，build + out 複合而成。'),
                ('a pool of capital', '「資金池」，pool 在財經語境中指「匯集起來的資源」。'),
                ('depend on X <i>V-ing</i>', '「取決於 X 做某事」，depend on 後接動名詞作受詞。'),
                ('justify (v.)', '「證明……是合理的」，常見於商業決策語境（justify an investment）。'),
            ],
        ),
        dict(
            title_en='What Three Seconds of Music Taught Me About Product',
            title_zh='三秒鐘的音樂，教會我的產品課',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Strategic constraints sharpen product strategy by forcing teams to commit rather than endlessly iterating. Limiting choices preserves the core hypothesis, reduces decision fatigue, and empowers creative judgment without stifling critical thought.',
            body_zh='策略性的限制條件，能讓產品策略更加銳利——因為它迫使團隊必須「做出承諾」，而不是無止盡地反覆迭代。限縮選項，有助於保留核心假設、降低決策疲勞，並在不扼殺批判性思考的前提下，賦予創意判斷力發揮的空間。',
            vocab=[
                ('sharpen (v.)', '「使銳利、使更聚焦」，此處為比喻用法，「讓策略更清晰精準」。'),
                ('decision fatigue', '心理學／管理學專有名詞「決策疲勞」，指做過多決策後判斷力下降的現象。'),
                ('stifle (v.)', '「扼殺、抑制」，常見於描述壓抑創意或言論的情況。'),
            ],
        ),
        dict(
            title_en='A Good Move Is Constructive',
            title_zh='好棋，本身就有建設性',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Effective product strategy should emerge from consistently making good moves rather than from top-down planning. A constructive move strengthens an existing relationship or introduces useful structure, creates value on its own, and avoids relying on a hypothetical V2 or future follow-up to become worthwhile.',
            body_zh='有效的產品策略，應該是從「持續做出好的一步棋」中逐漸浮現出來的，而不是仰賴由上而下的規劃。所謂「有建設性的一步」，指的是能強化既有關係、或引入實用結構的舉動——它本身就能創造價值，而不需要依賴「假設中的 V2 版本」或未來的後續動作，才能顯得有意義。',
            vocab=[
                ('emerge from X', '「從 X 中浮現、產生」，常用於描述非事先規劃、而是自然演變出的結果。'),
                ('top-down (adj.)', '複合形容詞「由上而下的」，與 bottom-up（由下而上的）相對。'),
                ('on its own', '片語，「靠自身、獨立地」，強調不依賴其他條件即可成立。'),
            ],
        ),
        dict(
            title_en='Monetizing AI: A Modern Framework',
            title_zh='AI 商業化：一套現代框架',
            meta='原文閱讀時間：約 7 分鐘',
            body_en='AI is often expensive for vendors, who absorb high development costs without capturing equivalent value. A new framework suggests pricing based on measurable customer outcomes and AI usage, shifting from flat subscriptions to tiered, hybrid, or outcome-based models as billing capabilities evolve.',
            body_zh='對供應商而言，AI 往往是一門「成本高昂」的生意——他們承擔了高額的開發成本，卻不一定能獲取相對等的價值回報。一套新的框架建議，應該根據「可量化的客戶成果」與「AI 使用量」來定價，隨著計費技術能力的演進，逐漸從單一固定訂閱制，轉向分層式、混合式，或以成果為基礎的計價模式。',
            vocab=[
                ('absorb (v.)', '此處指「承擔、吸收（成本）」，是多義動詞的另一種用法。'),
                ('capture value', '商業慣用語「獲取價值」，指企業成功將自身創造的價值轉化為實際收益。'),
                ('outcome-based (adj.)', '複合形容詞「以成果為基礎的」，常見於新型態的訂閱／計價模式描述。'),
            ],
        ),
        dict(
            title_en='Tension-Based Prioritization (A Non-Framework)',
            title_zh='以「張力」為核心的優先排序法（一套非框架）',
            meta='原文閱讀時間：約 7 分鐘',
            body_en='Better prioritization starts by identifying the tensions preventing teams from acting on what they already know. Those recurring conflicts often reveal the real decisions more clearly than any framework.',
            body_zh='更好的優先順序排定，應該從找出「究竟是什麼張力（tension），阻礙了團隊根據既有認知採取行動」開始著手。這些反覆出現的衝突，往往比任何框架都更能清楚揭露出真正該做的決策是什麼。',
            vocab=[
                ('tension (n.)', '「張力、緊張關係」，此處指團隊內部意見或目標間的衝突拉扯。'),
                ('prevent sb. from V-ing', '「阻止某人做某事」，固定句型，from 後接動名詞。'),
                ('recurring (adj.)', '「反覆發生的、週期性出現的」，recur（再次發生）的形容詞形式。'),
            ],
        ),
        dict(
            title_en='Shape Up for Data Teams',
            title_zh='資料團隊也能用的 Shape Up 方法論',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Shape Up can work for Data teams only when they help shape priorities from the start. Without a seat at the betting table, they remain reactive service teams rather than true partners.',
            body_zh='「Shape Up」這套產品開發方法論，唯有當資料團隊能從一開始就參與「形塑優先順序」的過程時，才會真正適用於資料團隊。如果資料團隊在「下注會議（betting table）」中沒有一席之地，他們就只會停留在「被動接單的服務團隊」，而無法成為真正的夥伴。',
            vocab=[
                ('shape (v.)', '此處作動詞「形塑、塑造」，呼應方法論名稱 Shape Up。'),
                ('a seat at the table', '慣用語「（在決策過程中）佔有一席之地」。'),
                ('reactive (adj.)', '「被動反應式的」，與 proactive（主動出擊的）相對。'),
            ],
        ),
        dict(
            title_en='How To Stay Happy: 4 Secrets From History’s Happiest Philosopher',
            title_zh='如何保持快樂：來自史上最快樂哲學家的 4 個祕訣',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Lasting happiness comes from replacing judgment with curiosity. Understand what drives your emotions and behavior, gain perspective, and use that insight to respond more calmly and make better choices.',
            body_zh='持久的快樂，來自於用「好奇心」取代「評判」。理解究竟是什麼在驅動你的情緒與行為、獲得更宏觀的視角，並運用這份洞察，以更平靜的方式回應，做出更好的選擇。',
            vocab=[
                ('lasting (adj.)', '「持久的、長久的」，last 當動詞「持續」的現在分詞轉形容詞用法。'),
                ('replace A with B', '「用 B 取代 A」，固定句型，常考介系詞 with。'),
                ('gain perspective', '慣用語「獲得（更宏觀的）視角」，perspective 指看待事情的角度或格局。'),
            ],
        ),
    ]),
    dict(name_zh='DevOps', name_en='TLDR DevOps', date='2026-08-17', summary_head='DevOps', articles=[
        dict(
            title_en='AI Software Development \u2013 What Does The Data Say?',
            title_zh='AI 軟體開發：數據到底怎麼說？',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='Recent research on AI-assisted software development shows a consistent gap between higher output and better outcomes: teams generate more code, commits, and larger diffs, but often do not ship faster or produce better software. Evidence also points to limitations in long-horizon agent reliability, effective context size, repository-level instructions, and benchmark realism, suggesting AI amplifies existing engineering strengths and weaknesses rather than replacing disciplined development practices.',
            body_zh='近期針對「AI 輔助軟體開發」的研究顯示，「產出變多」和「結果變好」之間，存在一個持續存在的落差：團隊確實產出了更多程式碼、更多 commit，以及更大的 diff，但往往並沒有因此「出貨更快」或「做出更好的軟體」。證據也指出，AI agent 在「長時間任務」上的可靠性、有效上下文長度、儲存庫層級的指示，以及基準測試的真實性等方面，都存在侷限——這意味著，AI 放大的是既有的工程能力強項與弱點，而不是取代有紀律的開發實務。',
            vocab=[
                ('AI-assisted (adj.)', '複合形容詞「AI 輔助的」，-assisted 表示「被……協助的」。'),
                ('a consistent gap between A and B', '「A 與 B 之間持續存在的落差」，gap 在此指「差距、落差」。'),
                ('diff (n.)', '軟體工程術語「差異比對（檔）」，diff 是 difference 的縮寫，常見於版本控制（git diff）。'),
                ('long-horizon (adj.)', '「長時間跨度的」，horizon 原指「地平線」，引申為「時間範疇」。'),
                ('amplify (v.)', '「放大」，常用於描述某事物讓既有效果變得更明顯或更強烈。'),
                ('disciplined (adj.)', '「有紀律的、嚴謹的」，disciplined development practices 指「有紀律的開發實務」。'),
            ],
        ),
        dict(
            title_en='How Cloudflare Detects MCP Traffic and Helps Secure It',
            title_zh='Cloudflare 如何偵測並協助保護 MCP 流量',
            meta='原文閱讀時間：約 13 分鐘',
            body_en='Cloudflare is adding new controls to its Zero Trust platform to help security teams monitor and manage AI agent traffic using the Model Context Protocol (MCP). The new tools include a Gateway selector that detects MCP traffic based on protocol headers, a dashboard showing which hosts and users are generating that traffic, and Traffic Source selectors that let administrators distinguish requests routed through approved MCP Server Portals from direct connections that bypass them.',
            body_zh='Cloudflare 正在為其 Zero Trust 平台新增控管功能，協助資安團隊監控與管理使用「模型情境協定」（Model Context Protocol, MCP）的 AI agent 流量。這些新工具包括：一個能根據協定標頭（header）偵測 MCP 流量的 Gateway 選擇器、一個顯示哪些主機與使用者正在產生該流量的儀表板，以及讓管理員能夠區分「經核准的 MCP Server Portal 轉送請求」與「繞過這些關卡的直接連線」的流量來源選擇器。',
            vocab=[
                ('Zero Trust', '資安領域專有名詞「零信任（架構）」，核心理念是「預設不信任任何存取，每次都要驗證」。'),
                ('based on X', '「根據 X」，常見固定片語，修飾動作的判斷依據。'),
                ('header (n.)', '網路協定專有名詞「標頭」，存放於封包／請求開頭的中繼資料（metadata）。'),
                ('dashboard (n.)', '「儀表板」，軟體工程／資料視覺化常見詞，泛指彙整關鍵指標的操作介面。'),
                ('distinguish A from B', '「區分 A 與 B」，固定搭配介系詞 from。'),
                ('bypass (v.)', '「繞過、跳過」，資安領域常見動詞，指跳過既定的檢查或關卡。'),
            ],
        ),
        dict(
            title_en='Argo Workflows 4.1',
            title_zh='Argo Workflows 4.1 發布',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Argo Workflows 4.1 adds OpenTelemetry tracing, improved resource and artifact management, GPU and device allocation through Kubernetes DRA, stronger database authentication and reliability, expanded CLI capabilities, UI enhancements, and reduced controller memory usage.',
            body_zh='Argo Workflows 4.1 新增了 OpenTelemetry 追蹤功能、改善了資源與產出物（artifact）管理、透過 Kubernetes DRA 支援 GPU 與裝置配置、強化資料庫身分驗證與可靠性、擴充命令列（CLI）功能、優化使用者介面，並降低了控制器（controller）的記憶體用量。',
            vocab=[
                ('tracing (n.)', '可觀測性領域專有名詞「追蹤」，指記錄請求在系統中流經路徑的技術。'),
                ('allocation (n.)', '「配置、分配」，常見於資源管理語境（resource allocation）。'),
                ('controller (n.)', 'Kubernetes／系統架構術語「控制器」，負責監控並協調系統狀態使其符合預期。'),
            ],
        ),
        dict(
            title_en='Secure All Your Internal Vibe-Coded Applications — in One Click',
            title_zh='一鍵保護你所有「氛圍編程」出來的內部應用程式',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Cloudflare has launched tools that let account administrators apply Access authentication policies directly to Workers, the company’s serverless application platform. A policy set at the account level automatically covers all Workers in that account, current and future, without requiring individual developers to configure anything. Access can protect preview URLs, production traffic, or both, and authenticated requests now expose user identity data through a context object so developers can personalize responses or log activity per user.',
            body_zh='Cloudflare 推出了新工具，讓帳號管理員能直接將 Access 身分驗證政策，套用到 Workers（該公司的無伺服器應用程式平台）上。在帳號層級設定的政策，會自動涵蓋該帳號底下所有的 Workers——無論是現有的還是未來新建立的——完全不需要個別開發者另外進行任何設定。Access 可以保護預覽網址、正式環境流量，或是兩者一併保護；而通過驗證的請求，現在也能透過一個情境物件（context object），把使用者身分資料暴露給應用程式，讓開發者能依使用者個人化回應內容，或記錄個別使用者的活動。',
            vocab=[
                ('serverless (adj.)', '雲端架構專有名詞「無伺服器的」，指開發者不需自行管理底層伺服器的運算模式。'),
                ('at the account level', '「在帳號層級」，level 常用於描述設定生效的範疇範圍。'),
                ('context object', '程式設計專有名詞「情境物件」，用來在程式執行過程中攜帶與當下請求相關的資訊。'),
            ],
        ),
        dict(
            title_en='How to Run Terraform in Bitbucket Pipelines',
            title_zh='如何在 Bitbucket Pipelines 中執行 Terraform',
            meta='原文閱讀時間：約 14 分鐘',
            body_en='Bitbucket Pipelines provides a built-in CI/CD workflow for automating Terraform and OpenTofu, with reusable YAML steps for formatting, validation, planning, and applying infrastructure changes. The guide demonstrates AWS S3 state storage and OIDC authentication, while highlighting dedicated infrastructure automation platforms as alternatives.',
            body_zh='Bitbucket Pipelines 提供了一套內建的 CI/CD 工作流程，能將 Terraform 與 OpenTofu 的操作自動化，並提供可重複使用的 YAML 步驟，涵蓋格式化、驗證、規劃（plan），以及套用（apply）基礎設施變更等階段。這份指南示範了如何使用 AWS S3 作為狀態儲存，並搭配 OIDC 身分驗證，同時也點出了專門的基礎設施自動化平台，作為另一種替代方案。',
            vocab=[
                ('reusable (adj.)', '「可重複使用的」，re-（再次）+ use（使用）+ -able。'),
                ('state storage', 'IaC 領域專有名詞「狀態儲存」，Terraform 用來記錄目前基礎設施狀態的儲存位置。'),
                ('highlight X as Y', '「將 X 標舉為 Y、凸顯 X 作為 Y」，常見於提出替代方案時的寫法。'),
            ],
        ),
        dict(
            title_en='Needle (GitHub Repo)',
            title_zh='Needle（GitHub 開源專案）',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Cactus Compute has released Needle 2, an open 45-million-parameter model for tool calling, device use, and structured data extraction. The entire model is a single 14MB binary that runs a full session in about 28MB of RAM. On benchmarks, it trades wins with models 5x to 70x larger, including FunctionGemma 270M, LFM2.5 230M, and Apple FM, while running at 2-bit quantization against their 16-bit versions. It installs via pip and supports LoRA fine-tuning, with weights available on Hugging Face.',
            body_zh='Cactus Compute 發布了 Needle 2，一款開源、參數量達 4,500 萬的模型，專為「工具呼叫（tool calling）」、裝置端使用，以及結構化資料擷取而設計。整個模型只是一個 14MB 大小的單一執行檔（binary），執行一整個工作階段（session）只需要大約 28MB 的記憶體。在基準測試中，它與規模比自己大 5 倍到 70 倍的模型（包括 FunctionGemma 270M、LFM2.5 230M，以及 Apple FM）互有勝負——而且它是以 2-bit 量化的方式，對打對方的 16-bit 版本。它可以透過 pip 安裝，並支援 LoRA 微調，權重檔案也已釋出於 Hugging Face 平台上。',
            vocab=[
                ('tool calling', 'AI agent 領域專有名詞「工具呼叫」，指模型呼叫外部函式／API 來完成任務的能力。'),
                ('binary (n.)', '電腦科學專有名詞「二進位執行檔」，泛指編譯後可直接執行的程式檔案。'),
                ('quantization (n.)', 'AI 領域專有名詞「量化」，指降低模型參數的數值精度以縮小體積、加快運算速度的技術。'),
            ],
        ),
        dict(
            title_en='Unsloth (GitHub Repo)',
            title_zh='Unsloth（GitHub 開源專案）',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Unsloth is a local tool for running, training, and deploying AI models that supports a wide range of models including Qwen3, DeepSeek, Gemma 4, and image generation models like FLUX. It comes in three forms: a desktop app, a web UI called Unsloth Studio, and a code-based version called Unsloth Core. A feature called Unsloth Start connects external coding agents like Claude Code and Codex to local models with a single command.',
            body_zh='Unsloth 是一款用於本機端執行、訓練與部署 AI 模型的工具，支援廣泛的模型範圍，包括 Qwen3、DeepSeek、Gemma 4，以及像 FLUX 這樣的圖像生成模型。它提供三種形式：一款桌面應用程式、一個名為 Unsloth Studio 的網頁介面，以及一個以程式碼為基礎的版本 Unsloth Core。其中一項名為 Unsloth Start 的功能，能透過單一指令，把 Claude Code、Codex 等外部編碼 agent，連接到本機端的模型上。',
            vocab=[
                ('a wide range of X', '「廣泛範圍的 X」，常見於描述支援眾多項目的片語。'),
                ('come in X forms', '「以 X 種形式提供」，常見於產品介紹的固定句型。'),
                ('with a single command', '「只需一個指令」，常用於強調操作的簡便性。'),
            ],
        ),
        dict(
            title_en='Docker Desktop Gets a Hypervisor of Its Own',
            title_zh='Docker Desktop 有了自己的虛擬機管理員',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Docker is introducing a unified virtual machine manager in Docker Desktop 4.86 beta to deliver consistent performance across macOS, Windows, and eventually Linux. The internally built VMM aims to improve startup, recovery, I/O, file sharing, and memory efficiency while reducing platform-specific inconsistencies from third-party virtualization systems.',
            body_zh='Docker 正在 Docker Desktop 4.86 beta 版中，推出一套統一的虛擬機器管理員（VMM），目標是在 macOS、Windows，以及未來的 Linux 上，提供一致的效能表現。這套由 Docker 內部自行開發的 VMM，旨在改善開機速度、復原能力、I/O 效能、檔案共享，以及記憶體使用效率，同時減少因使用第三方虛擬化系統，而在不同平台間產生的不一致問題。',
            vocab=[
                ('hypervisor (n.)', '虛擬化技術專有名詞「虛擬機器監控器」，負責管理與分配底層硬體資源給虛擬機使用。'),
                ('unified (adj.)', '「統一的、一致化的」，unify（統一）的過去分詞當形容詞用。'),
                ('platform-specific (adj.)', '複合形容詞「特定平台專屬的」，常用於描述因作業系統／平台不同而產生的差異。'),
            ],
        ),
        dict(
            title_en='Models Are Getting Dumber on Purpose',
            title_zh='模型正在「故意」變笨',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Smaller models are improving rapidly at reasoning while retaining less factual knowledge, shifting more of the system’s intelligence into retrieval, tools, and external context supplied at runtime. This trade can make models cheaper, more current, and easier to correct because facts live in inspectable data sources rather than opaque weights, while the model focuses on reusable reasoning procedures.',
            body_zh='較小型的模型，正在「推理能力」上快速進步，但同時保留的「事實性知識」卻越來越少——這代表整個系統的智慧，有越來越多的部分，被轉移到檢索（retrieval）、工具，以及執行階段（runtime）所提供的外部上下文之中。這種取捨，能讓模型變得更便宜、資訊更即時，也更容易被修正——因為事實資訊，存放在可被檢視的資料來源裡，而不是深藏在難以理解的模型權重之中；而模型本身，則可以專注在「可重複使用的推理程序」上。',
            vocab=[
                ('retain (v.)', '「保留、保有」，常見於描述系統或人保有某種資訊／能力。'),
                ('retrieval (n.)', 'AI／資訊科學專有名詞「檢索」，指從外部資料源中查找相關資訊的過程（如 RAG 技術）。'),
                ('opaque (adj.)', '「不透明的、難以理解的」，與 transparent/inspectable 相對，常形容模型的「黑箱」特性。'),
            ],
        ),
    ]),
    dict(name_zh='新創與創業', name_en='TLDR Founders', date='2026-08-17', summary_head='新創與創業', articles=[
        dict(
            title_en='Honestly, Who Buys SOTA?',
            title_zh='說實話，到底誰在買「最先進」模型？',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Labs are shipping smarter models faster than ever, but 84% of tokens on OpenRouter are not state-of-the-art. The most popular models deliver about 77% of frontier models at 2.5% of Claude Fable 5\u2019s price. Frontier models are still winning on software architecture and security design, but application deployment is optimizing price over performance.',
            body_zh='各大實驗室推出更聰明模型的速度，比以往都快，但在 OpenRouter 平台上，有高達 84% 的 token 用量，其實並非使用「最先進（SOTA）」的模型。目前最受歡迎的模型，能以 Claude Fable 5 價格的 2.5%，提供大約 77% 的頂尖（frontier）模型效能。頂尖模型在「軟體架構設計」與「安全性設計」上仍然勝出，但在實際應用部署上，大家優化的重點已經轉向「價格」而非「效能」。',
            vocab=[
                ('SOTA (state-of-the-art)', '科技業常用縮寫「最先進的、業界頂尖水準的」，常見於形容 AI 模型或技術。'),
                ('ship (v.)', '此處延續「出貨、發布」義，主詞是 AI 實驗室，指「推出模型」。'),
                ('token (n.)', 'AI 領域專有名詞「權杖、代幣單位」，是語言模型處理文字的基本計算單位，也是計費依據。'),
                ('frontier models', 'AI 領域慣用語「頂尖／前沿模型」，指效能最強、最新的一批模型。'),
                ('deliver X% of Y', '「達到 Y 的 X% 水準」，deliver 在此指「達成、提供出」某種表現。'),
                ('optimize X over Y', '「相較於 Y，優先優化 X」，over 在此作介系詞，表示比較與取捨。'),
            ],
        ),
        dict(
            title_en='Who Are the Token Brokers?',
            title_zh='誰是「代幣掮客」？',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='If you\u2019ve been following along, you know model routers are everywhere right now. A grey market is running the same play without permission. Founders are getting offers for OpenAI and Anthropic usage at 40% to 50% below list price. One broker claimed access to $100,000 of daily spend and routed requests through its own endpoint instead of handing over provider keys.',
            body_zh='如果你一直有在關注這個領域，你會知道「模型路由器（model router）」現在到處都是。而現在有一個灰色市場，正在「未經授權」的情況下，玩著同樣的遊戲。新創公司創辦人開始收到報價，能以「牌價的 40% 到 50% 折扣」使用 OpenAI 與 Anthropic 的額度。其中一名掮客（broker）聲稱自己握有每日 10 萬美元的可用額度，並將請求透過自己的端點（endpoint）進行轉發，而不是直接把服務商的金鑰交出來。',
            vocab=[
                ('follow along', '片語，「（持續）關注、跟上進度」，常用於敘述持續追蹤某議題的發展。'),
                ('run the same play', '慣用語，「玩同一套把戲、採取同樣的操作手法」，play 借用自運動賽事的「戰術、招式」。'),
                ('grey market', '商業／經濟學專有名詞「灰色市場」，指遊走在合法與非法邊緣、未經官方授權的交易管道。'),
                ('list price', '「牌價、公定價」，即官方公告的標準售價，常與「折扣價」對比。'),
                ('claim access to X', '「聲稱自己握有 X 的使用權限」，claim 在此表示「宣稱」，不一定屬實。'),
                ('hand over N', '片語動詞「交出、移交」，over 在此加強「轉交給對方」的方向感。'),
            ],
        ),
        dict(
            title_en='Do You Need a GTM Engineer?',
            title_zh='你需要一位「GTM 工程師」嗎？',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='A GTM engineer focuses on optimizing and strategizing go-to-market systems, leveraging tools like Clay and Unify. Arda’s founder, Kyle Henson, shares that hiring this role arose from a pipeline failure when one key employee was on leave, highlighting the need for a systematic approach. Candidates underwent practical challenges without clear instructions, allowing them to demonstrate problem-solving and initiative, ensuring they’re more than just order-takers.',
            body_zh='「GTM 工程師（GTM engineer）」這個角色，專注於優化並規劃「進入市場（go-to-market）」系統，善用 Clay、Unify 等工具。新創公司 Arda 的創辦人 Kyle Henson 分享，當初會決定招募這個職位，起因是某位關鍵員工請假時，導致業務管線（pipeline）出現故障——這凸顯出建立系統化做法的必要性。應徵者會被要求在「沒有明確指示」的情況下完成實作挑戰，藉此展現解決問題的能力與主動性，確保錄取的人不只是「聽令行事的接單者」。',
            vocab=[
                ('go-to-market (GTM)', '商業／新創領域專有名詞「進入市場（策略）」，泛指企業將產品推向市場的整套策略與執行。'),
                ('arise from X', '「起因於 X、由 X 引發」，常見於描述事件的來龍去脈。'),
                ('order-taker', '貶義複合名詞「只會聽令行事的接單者」，與具備主動性、能獨立判斷的人相對。'),
            ],
        ),
        dict(
            title_en='What Capital Wants',
            title_zh='資本真正想要的是什麼（新創版）',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Startups are now competing for dollars with every other tech asset in the world. Being the best company in a category is no longer enough. Founders are never going to change an investor’s mind if they’ve already considered an idea and rejected it. Only novel ideas stand a shot.',
            body_zh='新創公司如今募資時，面對的競爭對手是全世界所有的科技資產，而不只是同類型的公司。光是成為某個類別中最好的公司，已經不夠了。如果投資人已經考慮過某個點子、並且拒絕過，創辦人幾乎不可能再改變他們的心意。唯有真正「新穎」的點子，才有機會脫穎而出。',
            vocab=[
                ('compete for X', '「爭奪 X、為 X 競爭」，常見固定搭配介系詞 for。'),
                ('no longer', '「不再」，否定副詞片語，常置於助動詞或 be 動詞之後。'),
                ('stand a shot', '慣用語「有機會、有勝算」，shot 在此為口語用法，指「嘗試的機會」。'),
            ],
        ),
        dict(
            title_en='Competition Is For Losers In The AI Era: A Geographic Perspective',
            title_zh='AI 時代，競爭是輸家才會做的事：地理觀點',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='The Bay Area dominates access to venture capital. AI is radically lowering the barrier to build and scale startups. The same strategies applied in Silicon Valley to other geographies could be interesting. The global market has much less competition and more opportunity.',
            body_zh='灣區（Bay Area）在創投資金的取得上，依然占有壓倒性的優勢。而 AI 正大幅降低了「打造與擴展新創公司」的門檻。如果把矽谷那套成功策略，套用到其他地理區域，或許會很有意思。畢竟，全球市場的競爭程度低得多，機會也相對更多。',
            vocab=[
                ('dominate (v.)', '「主導、稱霸」，常見於描述在某領域佔絕對優勢地位。'),
                ('radically (adv.)', '「徹底地、根本性地」，常修飾程度劇烈的變化。'),
                ('barrier to V', '「做……的障礙／門檻」，常見片語（barrier to entry 進入障礙）。'),
            ],
        ),
        dict(
            title_en='Notes on Building Products People Love When Software Gets Cheap',
            title_zh='當軟體變得廉價，如何打造人們真正喜愛的產品',
            meta='原文閱讀時間：約 14 分鐘',
            body_en='Meta treats the rest of the consumer internet like a giant external product lab. It understands what gets people to create, share, connect, consume, come back, and generally spend more time with their products. When other companies spend years and a bunch of money and discover a new behavior that people clearly like, Meta takes notice. Every software company is going to need to get much better at doing some version of this as software is becoming too easy to build. A lot of software scarcity used to come from implementation, but that is changing fast.',
            body_zh='Meta 把「消費型網路世界的其他部分」，當成一座巨大的外部產品實驗室來看待。它非常清楚，究竟是什麼因素，能讓人們願意創作、分享、建立連結、消費、回訪，並整體上花更多時間使用他們的產品。每當其他公司花了好幾年時間與大筆資金，發現了一種人們明顯喜愛的新行為模式，Meta 都會注意到並加以借鏡。隨著軟體變得越來越容易被打造出來，每一家軟體公司，都將需要更擅長做這件事的某種版本。過去，軟體的稀缺性，很大一部分來自於「實作」本身的難度，但這一點正在快速改變。',
            vocab=[
                ('take notice', '慣用語「注意到、留意」，常見於描述對某事產生關注。'),
                ('get much better at V-ing', '「在做……這件事上變得更擅長」，at 後接動名詞。'),
                ('scarcity (n.)', '經濟學專有名詞「稀缺性」，形容詞是 scarce（稀缺的），與 abundance（豐富）相對。'),
            ],
        ),
        dict(
            title_en='The 0% Quota Club',
            title_zh='業績掛零俱樂部',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='In surveys, only 18% of early-stage teams had 70%+ of their reps hitting quota, and a majority were sitting at 20% to 40% attainment or worse. Inside those averages was a group of reps who closed essentially nothing all year. Mediocre reps are an output of the system, not an input. Companies need extreme product-market fit, tight processes, and substantial support for reps to succeed.',
            body_zh='調查顯示，早期階段（early-stage）的新創團隊中，只有 18% 有超過 70% 的業務代表（rep）達成業績配額（quota），而多數團隊的達成率，其實落在 20% 到 40% 之間，甚至更低。而在這些平均數字背後，還藏著一群整整一年幾乎「零成交」的業務代表。表現平庸的業務代表，是「系統」所產生的結果，而不是問題的「起因」。企業必須具備極強的產品市場契合度（PMF）、嚴謹的流程，以及充分的支援，業務代表才有機會成功。',
            vocab=[
                ('quota (n.)', '業務／銷售領域專有名詞「業績配額」，指公司設定給業務人員的業績目標。'),
                ('attainment (n.)', '「達成度、達成率」，attain（達成）的名詞形式。'),
                ('an output of X, not an input', '對比句型，「是 X 的結果，而非起因」。'),
            ],
        ),
        dict(
            title_en='The One GTM Decision You Cannot Afford to Get Wrong',
            title_zh='那個你絕對不能搞砸的 GTM 決策',
            meta='原文閱讀時間：約 15 分鐘',
            body_en='By the time a product is ready to go to market, it is largely a given input. Launch broadly, then reverse-engineer, or do the digging first and use the data to find the segment most likely to convert in the next three to six months. This article looks at how to do market research. It covers market segmentation, segment scoring, research methods, the ECP prototype, and the GTM roadmap.',
            body_zh='等到一項產品真正準備好要進入市場時，產品本身大致上已經是一個「既定條件」了。這時的選擇是：先廣泛發布上市、之後再反向推導（reverse-engineer）；還是先深入挖掘資料，再利用這些資料，找出未來三到六個月內最有可能轉換成交的客群區隔（segment）。本文探討的是該如何進行市場研究，內容涵蓋市場區隔、區隔評分、研究方法、ECP（理想客戶輪廓）原型，以及 GTM（進入市場）路線圖。',
            vocab=[
                ('by the time S+V', '「等到……的時候」，時間連接詞片語，常接完成式。'),
                ('a given input', '「一個既定的輸入條件」，given 當形容詞「既定的、已知的」。'),
                ('reverse-engineer (v.)', '「逆向工程、反向推導」，此處引申為商業策略上「從結果回推做法」。'),
            ],
        ),
        dict(
            title_en='GLM-5.3 (Tool)',
            title_zh='GLM-5.3（開源模型工具）',
            meta='原文閱讀時間：約 1 分鐘',
            body_en='Power complex coding agents with post-trained open-source model and cyber defense capabilities.',
            body_zh='運用這款經過後訓練（post-trained）的開源模型，驅動複雜的編碼 agent，同時具備網路防禦能力。',
            vocab=[
                ('power (v.)', '此處作動詞「驅動、提供動力給……」，常見於科技產品描述（powered by X）。'),
                ('cyber defense', '資安領域專有名詞「網路防禦」，cyber 字首泛指與網路／數位空間相關的事物。'),
            ],
        ),
        dict(
            title_en='Introducing Custom Agents',
            title_zh='Google 推出「自訂 Agent」功能',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Google has introduced Custom Agents in Antigravity 2.0 and the Antigravity CLI, with the Antigravity IDE following shortly. Custom Agents are specialized, file-based configurations that define a particular role with its own scoped instructions, tools, and constraints. The system keeps users’ active contexts clean, minimizes token overhead, and gives them a predictable partner for specific tasks. Custom agents don’t replace skills and dynamic subagents - they just provide even more customizability for another level of optimization.',
            body_zh='Google 在 Antigravity 2.0 與 Antigravity CLI 中，推出了「自訂 Agent（Custom Agents）」功能，Antigravity IDE 也將於近期跟進推出。自訂 Agent，是一種以檔案為基礎、經過特化設計的組態設定，用來定義一個具備專屬指示、工具與限制範疇的特定角色。這套系統能讓使用者當下的工作情境（context）保持乾淨、將 token 額外開銷降到最低，並為特定任務提供一個表現可預期的合作夥伴。自訂 Agent 並不會取代技能（skills）與動態子代理人（subagent）——它們只是為「另一層級的優化」，提供了更多客製化的可能性。',
            vocab=[
                ('file-based (adj.)', '複合形容詞「以檔案為基礎的」，常見於描述設定／組態的儲存方式。'),
                ('scoped (adj.)', '「範疇受限的、有明確界定範圍的」，scope 當動詞「界定範圍」的過去分詞。'),
                ('overhead (n.)', '電腦科學專有名詞「額外開銷」，指完成某任務所需付出的額外成本。'),
            ],
        ),
        dict(
            title_en='The Pros and Cons of Taking on Private Equity',
            title_zh='引進私募股權的利與弊',
            meta='原文閱讀時間：約 28 分鐘 podcast',
            body_en='The transition from bootstrapped startup to major retail player is the ultimate test of sustainable growth for many founder-led brands. This means taking on more debt or venture capital for some. For others, it may mean bringing on private equity investors to shoulder the costs. This podcast discusses the strategic decisions behind that evolution.',
            body_zh='從「白手起家（bootstrapped）的新創公司」，轉型成「主流零售大廠」，對許多由創辦人主導的品牌來說，是對「永續成長能力」的終極考驗。對某些品牌而言，這意味著要承擔更多債務，或引入創投資金；對另一些品牌來說，則可能意味著要引進私募股權（private equity）投資人，共同分攤成本。這集 Podcast，討論的正是這整個演變過程背後的策略決策。',
            vocab=[
                ('bootstrapped (adj.)', '新創圈慣用語「白手起家的、自籌資金的」，指未依賴外部融資、僅靠自有資源起步經營。'),
                ('take on X', '片語，「承擔、扛起 X（債務、責任等）」。'),
                ('shoulder (v.)', '此處作動詞「（用肩膀）扛起、承擔」，是常見的轉品用法（名詞轉動詞）。'),
            ],
        ),
        dict(
            title_en='The Demand Lens',
            title_zh='需求的視角',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Demand exists independently of supply. It is the factor that determines whether a startup’s product is relevant or not. Demand describes ‘what wants to happen’. A founder’s job is to find out what wants to happen but is currently blocked from happening, and then simply enable that thing to happen.',
            body_zh='需求（demand）的存在，獨立於供給（supply）之外。它是決定一項新創產品「是否切合市場所需」的關鍵因素。需求，描述的是「想要發生、卻尚未發生的事」。創辦人的工作，就是去找出「那件想要發生、卻目前被卡住而無法發生的事」，然後想辦法讓它得以實現。',
            vocab=[
                ('independently of X', '「獨立於 X 之外」，常見片語，強調兩者不互相依附。'),
                ('relevant (adj.)', '「切題的、切合需求的」，常見於形容產品與市場需求之間的契合程度。'),
                ('enable X to V', '「讓 X 得以做……」，常見於描述促成某事發生的動作。'),
            ],
        ),
    ]),
    dict(name_zh='設計', name_en='TLDR Design', date='2026-08-18', summary_head='設計', articles=[
        dict(
            title_en='Lovable Confirms New $13.3B Valuation, Raises Another $400M',
            title_zh='Lovable 確認估值達 133 億美元，再募 4 億美元',
            meta='原文閱讀時間：約 1 分鐘',
            body_en='Vibe-coding startup Lovable has raised $400 million in a Series C round led by Menlo Ventures and the Scaleup Europe Fund, confirming a new $13.3 billion valuation. The funding follows Lovable hitting $500 million in annualized run rate revenue in June, up from a $6.6 billion valuation in its December round. The company now hosts 60 million projects with 900 million monthly visitors, backed by its own in-house AI model and a multiyear Google Cloud deal.',
            body_zh='主打「氛圍編程（vibe-coding）」的新創公司 Lovable，完成了一輪由 Menlo Ventures 與 Scaleup Europe Fund 領投的 C 輪募資，金額達 4 億美元，並確認估值來到全新的 133 億美元。這輪募資，緊接在 Lovable 六月年化營收（annualized run rate）衝上 5 億美元之後——相較於去年十二月那一輪的估值（66 億美元），成長十分驚人。該公司目前代管 6,000 萬個專案，月訪客人數達 9 億，背後有自家內部開發的 AI 模型，以及一份多年期的 Google Cloud 合作協議作為支撐。',
            vocab=[
                ('vibe-coding', 'AI／開發者圈新興流行語「氛圍編程」，指透過與 AI 對話、憑直覺／感覺來產生程式碼，而非逐行手寫。'),
                ('Series C round', '創投術語「C 輪（募資）」，是新創公司依序進行的股權融資階段之一。'),
                ('led by X', '「由 X 領投」，常見於募資新聞，表示該輪投資的主要出資方。'),
                ('annualized run rate', '財經專有名詞「年化營收速率」，再次出現於募資新聞中。'),
                ('up from X', '「較 X（某先前數字）成長」，常用於描述數據的變化幅度與方向。'),
                ('in-house (adj.)', '「內部自製的、自家開發的」，與外包（outsourced）相對，常見於科技公司報導。'),
            ],
        ),
        dict(
            title_en='You Don\u2019t Have a Design System',
            title_zh='你其實沒有真正的「設計系統」',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Design systems often standardize components while leaving larger structural decisions\u2014like settings page layout and behavior\u2014uncaptured, causing inconsistent results even within one product. Testing this with AI agents building identical settings pages from the same component library confirmed the gap: each agent made different, reasonable choices about layout and interaction since no canonical pattern existed. Writing down explicit rules for structure, behavior, and interaction (not just components) resolved the divergence, producing consistent pages across agents.',
            body_zh='設計系統（design system）雖然經常把「元件」標準化，卻往往遺漏了更高層次的結構性決策——例如「設定頁面」的版面配置與行為邏輯，這導致即使在同一個產品內，結果也可能不一致。研究人員讓多個 AI agent，使用同一套元件庫，各自打造出相同的設定頁面來測試這個現象，結果證實了這個落差確實存在：由於沒有「標準範式（canonical pattern）」可循，每個 agent 都對版面與互動方式，做出了各自不同、但同樣合理的選擇。後來，將結構、行為與互動的規則明確寫下來（而不只是元件本身），才解決了這種分歧，讓不同 agent 產出的頁面能夠彼此一致。',
            vocab=[
                ('standardize (v.)', '「標準化」，字根 standard（標準）＋ -ize（使成為……）。'),
                ('leave N uncaptured', '「讓 N 沒有被涵蓋／記錄到」，uncaptured 是過去分詞當形容詞，capture 在此指「捕捉、記錄下來」。'),
                ('identical (adj.)', '「完全相同的」，語氣比 same 更強調「一模一樣」。'),
                ('canonical (adj.)', '資訊科學／設計領域常見字「標準的、公認範式的」，常見於 canonical pattern、canonical URL 等用法。'),
                ('divergence (n.)', '「分歧、發散」，動詞是 diverge，與 convergence（收斂、一致）相對。'),
                ('explicit (adj.)', '「明確寫明的、清楚表達的」，與 implicit（隱含的）相對，是工程文件常見對比字。'),
            ],
        ),
        dict(
            title_en='Target Names First Chief AI Officer',
            title_zh='Target 任命史上首位 AI 長',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Target has named Chandhu Nair as its first chief AI officer and promoted Purvi Shah to SVP of user experience, pairing AI strategy with design leadership. Nair will coordinate AI efforts across the company starting August 24, while Shah’s expanded UX role ensures AI-driven changes still feel ‘distinctly Target.’ Both executives frame the move as part of Target’s broader growth strategy, aiming to keep technology grounded in guest experience rather than pursued as a standalone initiative.',
            body_zh='Target 任命 Chandhu Nair 為該公司史上首位「AI 長（Chief AI Officer）」，同時晉升 Purvi Shah 為使用者體驗（UX）資深副總裁，將 AI 策略與設計領導職務相互搭配。Nair 將從 8 月 24 日起，統籌全公司的 AI 相關工作；而 Shah 擴大後的 UX 職權，則是要確保這些由 AI 驅動的變革，依然保有「鮮明的 Target 特色」。兩位高階主管都將這項人事異動，定位為 Target 整體成長策略的一部分，目標是讓技術始終「立足於顧客體驗」，而不是被當成一項獨立於整體業務之外的專案來推行。',
            vocab=[
                ('pair A with B', '「將 A 與 B 搭配結合」，常見片語，強調兩者相互配合。'),
                ('distinctly (adv.)', '「鮮明地、明顯有別於他者地」，常修飾具有獨特識別度的特質。'),
                ('standalone (adj.)', '複合形容詞「獨立的、單獨存在的」，常與「整合進整體策略」的做法相對比。'),
            ],
        ),
        dict(
            title_en='While You Were Angry at Instagram, Jif Quietly Debuted a Perfect New Logo',
            title_zh='當大家都在氣 Instagram 時，Jif 悄悄換了個完美的新 logo',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Jif has introduced its first major logo refresh in 30 years, simplifying the design by removing visual clutter and bringing back its classic tri-colour banner while largely preserving its familiar identity. The update has attracted little attention, especially compared to more controversial rebrands, because it focuses on refinement rather than reinvention. Its low-profile reception highlights how branding discussions often reward dramatic changes and controversy over thoughtful, evolutionary design.',
            body_zh='花生醬品牌 Jif，推出了 30 年來首次的重大 logo 改版，透過移除視覺上的雜亂元素、重新找回經典的三色橫幅，同時大致保留了原本熟悉的品牌識別。這次改版幾乎沒有引起太多關注，尤其是與那些更具爭議性的品牌重塑相比——原因在於，這次改版著重的是「精煉」，而不是「重新發明」。它低調的接受度，恰恰凸顯出一個現象：品牌討論往往更青睞戲劇性的改變與爭議話題，勝過經過深思熟慮、循序漸進的設計。',
            vocab=[
                ('clutter (n.)', '「雜亂、雜物」，設計領域常用於形容版面上過多不必要的元素。'),
                ('refinement (n.)', '「精煉、細部優化」，與 reinvention（重新發明）形成對比。'),
                ('low-profile (adj.)', '複合形容詞「低調的」，與 high-profile（高調的）相對。'),
            ],
        ),
        dict(
            title_en='Useful Books For Designers Who Work On Complex Problems',
            title_zh='給處理複雜問題的設計師的實用書單',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='A curated list of 18 books that help designers tackle complex, high-stakes systems in enterprise, legacy, or hierarchical environments. Recommendations span strategy and risk, such as How Big Things Get Done and Thinking in Bets, systems thinking, like Thinking in Systems and The Goal, and communication or data visualization titles, including Articulating Design Decisions and Envisioning Information.',
            body_zh='這是一份精選（curated）書單，共 18 本書，協助設計師在企業、舊有（legacy）系統，或階層分明的組織環境中，處理複雜且風險極高的系統性問題。推薦書目涵蓋策略與風險管理、系統思考，以及溝通表達或資料視覺化相關書籍。',
            vocab=[
                ('curated (adj.)', '「精選過的」，curate 原指「（展覽等）策劃、選件」，現廣泛用於形容經過篩選的內容清單。'),
                ('high-stakes (adj.)', '複合形容詞「高風險／高賭注的」，stake 原指「賭注」。'),
                ('span (v.)', '「涵蓋、橫跨」，常用於描述某清單／範圍所涉及的廣度。'),
            ],
        ),
        dict(
            title_en='How to Become an AI Designer',
            title_zh='如何成為一名 AI 設計師',
            meta='原文閱讀時間：約 17 分鐘',
            body_en='A product designer shares how AI transformed their workflow from creating designs in Figma to building interactive prototypes, shipping frontend code, and treating the product itself as the design source of truth. By using AI tools to prototype, iterate, and implement designs directly, they gained greater influence over product development and UI quality. While this approach significantly increases speed and output, they argue that AI cannot accelerate creativity, taste, or design thinking, and that the gains in efficiency come with a growing sense of distance from the craft of design.',
            body_zh='一位產品設計師分享了 AI 如何徹底改變他的工作流程——從原本在 Figma 中畫設計稿，轉變成直接打造可互動的原型、發布前端程式碼，並把「產品本身」當成設計的真相來源（source of truth）。透過運用 AI 工具直接進行原型製作、反覆迭代與實作設計，他對產品開發與 UI 品質，獲得了更大的影響力。雖然這種做法大幅提升了速度與產出量，但他認為 AI 並無法加速「創造力」、「品味」或「設計思考」本身；而效率上的提升，也伴隨著一種與設計「工藝本身」漸行漸遠的疏離感。',
            vocab=[
                ('transform (v.)', '「徹底改變、轉變」，語氣比 change 更強調本質上的變化。'),
                ('source of truth', '軟體工程慣用語「真相來源」，此處延伸應用於設計領域。'),
                ('a sense of distance from X', '「一種與 X 漸行漸遠的疏離感」。'),
            ],
        ),
        dict(
            title_en='YouTube’s New Policy Is Bad News for Animators',
            title_zh='YouTube 新政策對動畫創作者是壞消息',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Starting February 1, YouTube will double the requirements for monetization eligibility: 8,000 watch hours annually or 20 million Shorts views within three months. Existing Partner Program members and Fan Funding/shopping thresholds remain unaffected, though YouTube expects overall creator earnings to rise via expanded Premium Lite availability. New independent animators face a steeper climb since their content-heavy production process makes it harder to hit these higher thresholds quickly.',
            body_zh='從 2 月 1 日起，YouTube 將把「開通營利資格」的門檻提高一倍：年度觀看時數須達 8,000 小時，或是三個月內 Shorts（短影音）觀看次數須達 2,000 萬次。現有的「合作夥伴計畫」會員，以及「粉絲贊助/購物」的門檻則不受影響——不過 YouTube 預期，隨著 Premium Lite 方案擴大推行，創作者整體收益仍會上升。對於獨立動畫創作者來說，這條路會變得更加艱辛，因為他們的內容製作過程本來就相當耗時費工，更難在短時間內達到這些提高後的門檻。',
            vocab=[
                ('monetization eligibility', '創作者經濟領域專有名詞「營利資格」，eligibility 指「符合資格的狀態」。'),
                ('remain unaffected', '「維持不受影響」，常見於描述某規則變動時，哪些對象不受波及。'),
                ('a steeper climb', '比喻用法「更陡峭的攀爬」，引申為「更艱難的挑戰、更高的門檻」。'),
            ],
        ),
        dict(
            title_en='Claude Code 101, for Designers',
            title_zh='給設計師的 Claude Code 入門課',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='Claude Code extends Anthropic’s Claude beyond chat into a terminal tool that can create, edit, and run files, building full apps rather than just describing prototypes. Key concepts include context windows and tokens (its working memory), sessions (single continuous workstreams), CLAUDE.md (a standing project brief), approval modes, commands, skills, agents, and MCP (a connector standard linking Claude to outside tools). This piece is the first in a series aimed at helping product designers transition to using Claude Code, focusing purely on defining the surrounding jargon.',
            body_zh='Claude Code 把 Anthropic 的 Claude，從單純的聊天工具，延伸成一個能夠建立、編輯、執行檔案的終端機工具——它能真正打造出完整的應用程式，而不只是「描述」原型長什麼樣子。其中的關鍵概念包括：上下文視窗（context window）與 token（也就是它的「工作記憶」）、工作階段（session）、CLAUDE.md（一份長期存在的專案簡報文件）、核准模式、指令、技能（skill）、agent，以及 MCP（一套用來連接 Claude 與外部工具的標準協定）。本文是系列文章的第一篇，目標是協助產品設計師逐步轉換到使用 Claude Code，內容純粹聚焦於定義周邊會用到的專有名詞。',
            vocab=[
                ('extend N beyond X', '「把 N 從 X 延伸出去」，常見於描述功能或範疇的擴展。'),
                ('standing (adj.)', '此處指「長期有效的、持續存在的」，而非「站立的」。'),
                ('jargon (n.)', '「（特定領域的）術語、行話」，常帶有「外行人不易理解」的語氣。'),
            ],
        ),
        dict(
            title_en='AI Video and Image Creation Tools (Website)',
            title_zh='AI 影片與圖像創作工具',
            meta='原文閱讀時間：約 1 分鐘',
            body_en='Turn prompts and ideas into AI videos, images, and social media content with vivago AI Agent.',
            body_zh='透過 vivago AI Agent，把你的提示詞（prompt）與想法，轉化成 AI 影片、圖像與社群媒體內容。',
            vocab=[
                ('turn A into B', '「把 A 轉化成 B」，常見句型，強調轉變的過程。'),
                ('prompt (n.)', 'AI 領域高頻詞「提示詞」，指使用者輸入給 AI 模型的指令文字。'),
            ],
        ),
        dict(
            title_en='Hardware Prototyping with AI (Website)',
            title_zh='用 AI 打造硬體原型',
            meta='原文閱讀時間：約 1 分鐘',
            body_en='Describe the thing you want to build. EasyCircuit designs the circuit, sources the exact parts automatically, and stages the build from breadboard to soldered perfboard.',
            body_zh='只要描述你想打造的東西，EasyCircuit 就會自動設計電路、找齊確切所需的零件，並規劃出從麵包板（breadboard）到焊接萬用板（perfboard）的完整製作流程。',
            vocab=[
                ('source (v.)', '此處作動詞「尋找並取得（貨源、零件）」，供應鏈／採購領域常見用法。'),
                ('stage (v.)', '此處作動詞「規劃分階段（流程）」，而非名詞「舞台」。'),
            ],
        ),
        dict(
            title_en='Free Hand-drawn Illustrations (Website)',
            title_zh='免費手繪插畫素材',
            meta='原文閱讀時間：約 1 分鐘',
            body_en='Kitbitz is a collection of hand-drawn, mix-and-match objects for building busy streets, shops, buildings, crossings, parks, and playful little urban worlds.',
            body_zh='Kitbitz 是一套手繪風格、可自由混搭組合的物件素材庫，能用來打造熱鬧的街道、商店、建築物、路口、公園，以及充滿童趣的迷你城市場景。',
            vocab=[
                ('mix-and-match (adj.)', '複合形容詞「可自由混搭組合的」，常見於描述模組化、可自由拼裝的素材或選項。'),
                ('playful (adj.)', '「充滿童趣的、俏皮的」，設計領域常用來形容輕鬆活潑的視覺風格。'),
            ],
        ),
    ]),
    dict(name_zh='行銷', name_en='TLDR Marketing', date='2026-08-18', summary_head='行銷', articles=[
        dict(
            title_en='AI Fears Are Fueling the \u2018Handmade\u2019 Branding Trend',
            title_zh='對 AI 的焦慮，正在帶動「手作感」品牌風潮',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Brands across industries are using handmade aesthetics to signal humanity in an AI-saturated market. Think hand-drawn typography, imperfect textures, retro illustrations, and intentionally \u2018rough\u2019 design. The trend is showing up in food, cleaning products, luxury hospitality, and even AI brands like Claude. However, when brands use these cues without meaning, they can feel generic and fail to stand out. Handmade elements work best when they fit the brand or concept.',
            body_zh='在一個已經「AI 飽和」的市場中，各行各業的品牌，正紛紛運用「手作感」美學，來傳達出「這是人做的」訊息。想像一下：手繪字體、帶有瑕疵感的紋理、復古風插畫，以及刻意營造出的「粗糙感」設計。這股風潮出現在食品、清潔用品、精品旅宿業，甚至連 Claude 這樣的 AI 品牌本身也不例外。不過，當品牌使用這些手法卻缺乏真正的意義支撐時，反而會顯得很「通用、沒有特色」，無法真正脫穎而出。「手作感」元素，唯有在真正契合品牌或概念本身時，才會發揮最好的效果。',
            vocab=[
                ('aesthetics (n.)', '「美學、視覺風格」，常用單數動詞搭配，設計／行銷領域高頻詞。'),
                ('AI-saturated (adj.)', '複合形容詞「AI 飽和的」，saturate 原意為「使飽和」，引申為「充斥、氾濫」。'),
                ('intentionally (adv.)', '「刻意地、故意地」，與 accidentally（意外地）相對。'),
                ('cue (n.)', '「訊號、暗示」，此處指品牌用來傳達某種訊息的視覺／設計手法。'),
                ('generic (adj.)', '「通用的、沒有特色的」，常帶有負面語氣，形容缺乏獨特性的事物。'),
                ('stand out', '片語動詞，「脫穎而出、與眾不同」，行銷／求職領域高頻用語。'),
            ],
        ),
        dict(
            title_en='How AI Text Watermarking Works',
            title_zh='AI 文字浮水印是怎麼運作的？',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Claude\u2019s text watermarking will be difficult to remove without heavy edits. Instead of visible characters, AI watermarks hide in word choices, using secret statistical patterns that can survive copying. Detection requires the provider\u2019s secret key and enough text to distinguish the watermark from chance, making it different from style-based AI detectors. Light editing or paraphrasing can weaken the signal but may leave enough original wording to remain detectable.',
            body_zh='Claude 的文字浮水印，如果沒有經過大幅度的編輯修改，將很難被移除。這種 AI 浮水印不是靠肉眼可見的字元，而是藏在「用字選擇」之中，運用一套祕密的統計模式（statistical pattern），即使文字被複製轉貼也依然能夠存留下來。要偵測出浮水印，需要服務商的祕密金鑰，以及足夠份量的文字，才能將「真的有浮水印」與「純屬巧合」區分開來——這一點，與傳統那種「靠文字風格判斷」的 AI 偵測工具截然不同。輕度的編輯或改寫，雖然會削弱浮水印訊號的強度，但仍可能保留足夠多的原始用字，使其依然可被偵測出來。',
            vocab=[
                ('watermarking (n.)', '動詞 watermark 的動名詞，「加浮水印」，原用於紙鈔／圖片防偽，此處延伸至 AI 生成文字的防偽機制。'),
                ('instead of N', '「取代 N、而不是 N」，常見對比片語，用來凸顯與預期不同的做法。'),
                ('survive (v.)', '此處為「（在……情況下依然）存留、倖存」，survive copying 意為「即使被複製轉貼也不會消失」。'),
                ('distinguish A from B', '「區分 A 與 B」，常見學術／技術寫作片語。'),
                ('by chance', '「出於巧合、碰運氣」，與 distinguish...from chance 呼應，表示「並非巧合」。'),
                ('paraphrase (v.)', '「改寫、意譯」，語言學／寫作領域常見動詞，指用不同措辭表達相同意思。'),
            ],
        ),
        dict(
            title_en='Google Lowers Search Profile Requirements',
            title_zh='Google 降低「搜尋個人檔案」的申請門檻',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Google lowered the follower threshold for its Search profiles, making the feature available to more brands and creators. YouTube, Instagram, and X accounts now qualify at 35K followers or subscribers, down from 100K. TikTok’s threshold dropped from 300K to 100K. Google also added new Search Console reporting on search terms, rankings, and search volume. On YouTube, channel managers will now receive alerts for copyright claims and removal requests, giving teams more visibility into issues that could affect content.',
            body_zh='Google 降低了「Google 搜尋個人檔案（Search Profile）」功能的追蹤者門檻，讓更多品牌與創作者能夠使用這項功能。YouTube、Instagram 與 X 帳號，現在只要有 3.5 萬名粉絲或訂閱者即符合資格，門檻從原本的 10 萬降低。TikTok 的門檻，則從 30 萬降至 10 萬。Google 同時也在 Search Console 中，新增了針對搜尋詞、排名與搜尋量的報表功能。在 YouTube 上，頻道管理者現在也會收到「著作權主張」與「移除請求」的警示通知，讓團隊對可能影響內容的問題，有更高的可見度。',
            vocab=[
                ('threshold (n.)', '「門檻、臨界值」，常見於描述資格認定的最低標準。'),
                ('qualify at X', '「在 X 的條件下符合資格」，qualify 當不及物動詞「具備資格」。'),
                ('visibility (n.)', '此處引申義為「可見度、掌握狀況的程度」，而非字面的「能見度」。'),
            ],
        ),
        dict(
            title_en='Oops! Sorry for the Mistake',
            title_zh='哎呀！抱歉出了點小狀況',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Use a believable ‘mistake’ to earn a second email. Send an initial email with something intentionally wrong (ie. a broken link, placeholder text, or early promotion). Follow up minutes later with an ‘oops’ apology and the real offer. The first email creates curiosity and gets attention. The follow-up feels more human and gives you a natural place to add a discount or incentive. Use this sparingly, as repeating this tactic too often makes it obvious.',
            body_zh='運用一個「可信的錯誤」，來換取寄送第二封信的機會。先寄出第一封故意包含瑕疵的信（例如失效連結、佔位文字，或是提早曝光的優惠活動），幾分鐘後再寄出第二封「哎呀，抱歉」的道歉信，附上真正的優惠內容。第一封信能創造好奇心、吸引注意力；而第二封「補救信」則讓人感覺更有人味，也提供了一個自然的時機，加入折扣或誘因。這個手法要謹慎使用，因為重複用太多次，反而會讓人一眼看穿。',
            vocab=[
                ('believable (adj.)', '「可信的、令人信服的」，believe（相信）+ -able。'),
                ('placeholder (n.)', '軟體／設計領域常見詞「佔位符」，指暫時用來填補位置、之後會被替換的內容。'),
                ('sparingly (adv.)', '「節制地、謹慎少量地」，常搭配 use sparingly（謹慎使用）。'),
            ],
        ),
        dict(
            title_en='How Showing a Team Member Increased Leads by 79%',
            title_zh='露出一位真實團隊成員，讓名單成長了 79%',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Showing the person behind a service can make a landing page more persuasive when customers need reassurance before taking action. For a financial services client, replacing a calculator-focused headline with ‘Is equity release right for me?’ and introducing a real information team member increased completed leads by 79%. The test worked by bringing the team’s reputation for empathy and clear guidance onto the page before visitors had to contact them. Identify persuasive assets that already exist in the business and surface them where prospects need reassurance.',
            body_zh='當客戶在採取行動前需要被安撫、被說服時，在到達頁面（landing page）上「露出服務背後真人的臉孔」，能讓頁面更具說服力。以一個金融服務業客戶為例，把原本聚焦在「計算機工具」的標題，換成「這個資產釋放方案適合我嗎？」，並加入一位真實的資訊團隊成員露面，結果讓完整填寫的名單（lead）成長了 79%。這項測試之所以奏效，是因為它讓團隊「善於同理、指引清楚」的口碑，在訪客真正聯繫之前，就已經呈現在頁面上。找出企業中原本就存在、具說服力的資產，並把它們安排在潛在客戶最需要被安撫的地方。',
            vocab=[
                ('reassurance (n.)', '「安撫、讓人安心的保證」，reassure（使安心）的名詞形式。'),
                ('landing page', '行銷領域專有名詞「到達頁面」，指使用者點擊廣告/連結後降落的第一個頁面。'),
                ('surface (v.)', '此處作動詞「使浮現、呈現出來」，而非名詞「表面」。'),
            ],
        ),
        dict(
            title_en='An Update to How We Count Public Views Across YouTube',
            title_zh='YouTube 更新了「公開觀看次數」的計算方式',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='YouTube will change how it counts public views across all video formats starting on August 24. A view will count as soon as a video begins playing, including the first frame, which will likely increase reported view counts. YouTube will keep ‘Engaged views’ in Analytics to show how many viewers continued watching. The change won’t affect creator earnings or YouTube Partner Program eligibility, which will continue to use engaged or qualified views and watch hours.',
            body_zh='從 8 月 24 日起，YouTube 將改變「公開觀看次數」在所有影片格式中的計算方式。只要影片開始播放（包括第一格畫面），就會被計入一次觀看——這很可能會讓對外顯示的觀看次數上升。YouTube 仍會在分析報表（Analytics）中保留「投入觀看（Engaged views）」這項指標，用來呈現有多少觀眾持續往下看。這項變動不會影響創作者的收益，也不會影響 YouTube 合作夥伴計畫的資格認定——這兩者仍會繼續採用「投入/合格觀看次數」與「觀看時數」作為計算基準。',
            vocab=[
                ('count (v.)', '此處作動詞「計入、列入計算」，並非名詞「數量」。'),
                ('as soon as', '「一……就……」的連接詞用法。'),
                ('affect (v.)', '「影響」，注意與 effect（名詞，效果）拼字相近但詞性不同，是常見混淆字。'),
            ],
        ),
        dict(
            title_en='Content Effort: The Google Ranking Feature Nobody Talks About',
            title_zh='內容投入度：Google 排名機制裡沒人在談的關鍵',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='Google defines content effort as the extent to which a human actively worked to create satisfying content. In practice, that means showing evidence of unique value through original research and firsthand insights, rather than recycled facts or AI-generated summaries. Organize content around the user’s goal, put the most useful information upfront, and cut filler. AI can help with production, but scaled content that adds little beyond what already exists is unlikely to stand out. Before publishing, ask whether the page contains something competitors can’t easily reproduce.',
            body_zh='Google 將「內容投入度（content effort）」定義為：一個人為了創造出令人滿意的內容，實際投入了多少心力。實務上，這代表你需要透過原創研究與第一手見解，展現出獨特的價值，而不是單純回收既有事實，或直接放上 AI 生成的摘要。內容架構應該圍繞著使用者的目標來組織、把最有用的資訊放在最前面，並刪去不必要的填充內容。AI 可以協助內容的產製過程，但如果只是大量生產、卻沒有比既有內容多提供什麼，很難真正脫穎而出。發布之前，不妨問問自己：這個頁面上，是否包含了競爭對手無法輕易複製的東西？',
            vocab=[
                ('the extent to which S+V', '「……的程度」，正式書面英文常見句型，引導名詞子句。'),
                ('firsthand (adj.)', '「第一手的、親身的」，與 secondhand（二手的、轉述的）相對。'),
                ('filler (n.)', '「填充內容、湊字數的內容」，常見於寫作/內容行銷語境，帶有負面語氣。'),
            ],
        ),
    ]),
    dict(name_zh='加密貨幣', name_en='TLDR Crypto', date='2026-08-18', summary_head='加密貨幣', articles=[
        dict(
            title_en='Post Browser Internet',
            title_zh='「後瀏覽器」時代的網路世界',
            meta='原文閱讀時間：約 7 分鐘',
            body_en='AI agents are displacing browser-based navigation as the primary internet interface, creating demand for a Router layer that handles API discovery, ranking, payment, and execution for agent-driven workflows. Stripe\u2019s $7B+ acquisition of OpenRouter signals a bet on owning that aggregation layer, combined with Stripe\u2019s MPP protocol, Tempo settlement chain, Privy wallet stack, and x402 Foundation partnership. The x402 protocol removes account-setup friction by embedding per-request payment into HTTP 402 responses, with early Router implementations from Coinbase Bazaar, AgentCash, and Sponge Catalog already competing on open catalogs. The core unsolved problem mirrors Yahoo\u2019s 1990s challenge: open catalogs fill with proxy endpoints and unvetted operators, and no PageRank-equivalent ranking system exists to make the Router trustworthy at scale, leaving Google\u2019s Search segment (56% of Alphabet revenue) exposed to agent-driven disintermediation.',
            body_zh='AI agent 正在取代「以瀏覽器為主」的上網方式，成為人們使用網路的主要介面，這也讓市場開始需要一個「路由器（Router）層」，來處理 agent 驅動工作流程中的 API 探索、排序、付款與執行。Stripe 以超過 70 億美元收購 OpenRouter，正代表著它押注要拿下這個「聚合層（aggregation layer）」的地位，並搭配 Stripe 自家的 MPP 協定、Tempo 結算鏈、Privy 錢包技術，以及與 x402 基金會的合作。x402 協定透過把「每次請求都內建付款機制」直接嵌入 HTTP 402 回應中，消除了帳號註冊設定的摩擦成本；目前已有 Coinbase Bazaar、AgentCash、Sponge Catalog 等早期 Router 實作，在開放型錄（catalog）上互相競爭。而這個領域尚未解決的核心問題，與 Yahoo 在 1990 年代所面臨的挑戰如出一轍：開放型錄很容易被「代理端點」與「未經審核的營運方」灌滿，而且目前並不存在類似 PageRank 那樣的排序系統，能讓 Router 在規模化的情況下依然值得信賴——這使得 Google 搜尋業務（占 Alphabet 營收 56%）暴露在被 agent 取代中間商角色的風險之下。',
            vocab=[
                ('displace (v.)', '「取代、排擠」，常用於描述新事物取代舊事物的地位。'),
                ('aggregation layer', '技術架構術語「聚合層」，指整合多方資源、統一對外提供服務的系統層級。'),
                ('friction (n.)', '原意「摩擦力」，商業／產品設計語境中引申為「（流程中造成阻礙的）阻力、摩擦成本」。'),
                ('unvetted (adj.)', '「未經審查／審核的」，vet 當動詞指「仔細審查（身分、資格）」，un- 為否定字首。'),
                ('at scale', '片語，「在規模化的情況下」，常見於科技業討論系統是否能因應大量使用者／流量。'),
                ('disintermediation (n.)', '商業／經濟學專有名詞「去中介化」，指透過技術讓交易雙方跳過傳統中間商直接互動。'),
            ],
        ),
        dict(
            title_en='Building the Open Agentic Economy',
            title_zh='打造開放的「Agent 經濟體」',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Circle\u2019s vision paper frames AI agents as a new form of labor, published like websites, ranked on merit, and compensated via stablecoin transactions, with ERC-8004 for identity and x402/MPP as the payment layer. Discovery relies on open registries where reputation derives from demonstrated behavior rather than self-description, avoiding the centralization that occurred in web search. Agents holding stablecoin balances pay for downstream services without pre-arranged integrations, enabling multi-agent economic workflows that settle on existing stablecoin rails.',
            body_zh='Circle 公司發布的願景報告，將 AI agent 框架化為一種「新型態的勞動力」——它們會像網站一樣被發布上線、依照實際表現（merit）被排序，並透過穩定幣（stablecoin）交易獲得報酬，其中 ERC-8004 負責處理身分認證，x402/MPP 則作為付款層。這套系統的「探索（discovery）」機制，仰賴的是開放式登記系統（open registries），聲譽是根據「實際展現出來的行為」而非「自我宣稱」來決定，藉此避免重蹈網路搜尋當年走向中心化的覆轍。持有穩定幣餘額的 agent，可以在沒有事先安排好整合介接的情況下，直接付費使用下游服務，進而實現能在既有穩定幣軌道（rails）上完成結算的多重 agent 經濟工作流程。',
            vocab=[
                ('frame N as X', '片語，「把 N 框架化／定位為 X」，常見於商業或學術論述中的觀點陳述。'),
                ('labor (n.)', '「勞動力、勞力」，美式拼法（英式為 labour），經濟學核心詞彙。'),
                ('compensate (v.)', '「給予報酬、補償」，名詞是 compensation（薪酬、補償金）。'),
                ('reputation derives from X', '「聲譽源自於 X」，derive from 是固定片語，「源自於」。'),
                ('centralization (n.)', '「中心化」，與 decentralization（去中心化）相對，是區塊鏈領域核心概念對比詞。'),
                ('settle on X', '片語，「在 X 上完成結算」，settle 在金融語境中指「（交易）結算、清算」。'),
            ],
        ),
        dict(
            title_en='Bitcoin Miner HIVE Inks Five-Year $350 Million AI Cloud Contract',
            title_zh='比特幣礦商 HIVE 簽下五年 3.5 億美元 AI 雲端合約',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='HIVE’s BUZZ HPC subsidiary signed a five-year, ~$350 million GPU cloud deal with an unnamed investment-grade enterprise customer, adding ~$70 million in annualized revenue and bringing BUZZ HPC’s total annual recurring revenue to about $180 million. The buildout, 2,016 NVIDIA Blackwell Ultra GPUs at HIVE’s hydro-powered Merritt, British Columbia facility, costs ~$185 million, funded partly by a $35 million customer deposit and a zero-percent convertible bond. It’s HIVE’s second major AI cluster deal in two months (following a $220 million Bell/Cohere contract in June) as it targets $200 million in GPU cloud ARR by year-end, joining IREN, Hut 8, and TeraWulf in converting mining infrastructure into AI compute contracts.',
            body_zh='HIVE 公司旗下的 BUZZ HPC 子公司，與一家未具名、達投資等級的企業客戶，簽下了一份為期五年、金額約 3.5 億美元的 GPU 雲端服務合約——這將為公司增加約 7,000 萬美元的年化營收，使 BUZZ HPC 的年度經常性營收（ARR）總額，來到約 1.8 億美元。這項建置計畫，將在 HIVE 位於加拿大卑詩省 Merritt、使用水力發電的據點，部署 2,016 顆 Nvidia Blackwell Ultra GPU，總成本約 1.85 億美元，部分資金來自 3,500 萬美元的客戶訂金，以及一筆零利率可轉換債券。這是 HIVE 兩個月內談成的第二筆重大 AI 叢集合約（六月才與 Bell/Cohere 簽下 2.2 億美元合約），該公司目標是在年底前，將 GPU 雲端服務的年度經常性營收衝上 2 億美元——加入 IREN、Hut 8、TeraWulf 等公司的行列，將「挖礦基礎設施」轉型為「AI 運算合約」。',
            vocab=[
                ('ink a deal', '慣用語「簽下合約」，ink（墨水）在此作動詞，引申為「簽署」。'),
                ('investment-grade (adj.)', '金融專有名詞「投資等級的」，指信用評等達到一定水準以上的企業／債券。'),
                ('annual recurring revenue (ARR)', '訂閱制商業模式核心財務指標「年度經常性營收」。'),
            ],
        ),
        dict(
            title_en='Prediction Market Novig Sues Wisconsin AG Over Sports Contracts',
            title_zh='預測市場 Novig 控告威斯康辛州檢察長',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Novig, a sports-only prediction market that requires users to be 21+ and recently signed an exclusive partnership with the New York Mets, preemptively sued Wisconsin’s AG and gaming administrator, arguing its CFTC-designated contract market status preempts the state’s gambling ban. It’s Novig’s fifth state lawsuit since August 4 (after New York, New Mexico, Massachusetts, and Washington), filed as Wisconsin’s earlier suits against Kalshi, Polymarket, Robinhood, Crypto.com, and Coinbase remain pending in the same federal court, where a judge already denied the CFTC’s own preliminary injunction request in a parallel case.',
            body_zh='Novig 是一個僅限運動賽事的預測市場平台，要求使用者須年滿 21 歲，並且最近才與紐約大都會隊（New York Mets）簽下獨家合作協議——該公司先發制人，對威斯康辛州檢察長與博弈主管機關提起訴訟，主張自己身為受 CFTC（美國商品期貨交易委員會）認定的「合約市場」，其地位優先於（preempt）該州的博弈禁令。這是 Novig 自 8 月 4 日以來，在各州提起的第五起訴訟；與此同時，威斯康辛州先前對 Kalshi、Polymarket、Robinhood、Crypto.com，以及 Coinbase 提起的訴訟，仍在同一個聯邦法院審理中——該法院的法官，先前已在一起相關案件中，駁回了 CFTC 自己提出的初步禁制令（injunction）請求。',
            vocab=[
                ('preemptively (adv.)', '「先發制人地、預先地」，preempt（搶先、優先）的副詞形式。'),
                ('preempt (v.)', '法律領域專有動詞「優先於、取代（較低位階的規範）」。'),
                ('pending (adj.)', '法律用語「（訴訟）審理中、未決的」。'),
            ],
        ),
        dict(
            title_en='Inside Ethereum Upgrades: Hegotá',
            title_zh='以太坊升級內幕：Hegotá',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Hegotá is the planned upgrade following Glamsterdam that slotted FOCIL (EIP-7805), Quick Slots (EIP-8198), and a data repricing bundle (EIPs 8131 and 8279) as S-tier candidates. Quick Slots targets a reduction from the current 12-second slot time to roughly 10 seconds within one year, with Ethlabs citing improved confirmation UX, fresher on-chain prices for DEX spreads and LP economics, faster finality, and stronger censorship resistance as the rationale. Frame Transactions (EIP-8141) earns an A-tier rating as Ethlabs’ preferred native account abstraction design, enabling passkey wallets, sponsored transactions, ERC-20 gas payments, transaction batching, and first-class support for privacy protocols like Railgun, with the lower tier reflecting adoption coordination risk rather than technical concerns. Notably, Ethlabs withheld any tier rating for Tapered Issuance Burn (EIP-8363), framing ETH issuance as a monetary policy question requiring broad community consensus rather than a standard AllCoreDevs inclusion decision.',
            body_zh='Hegotá 是繼 Glamsterdam 之後、規劃中的下一次以太坊升級，將 FOCIL（EIP-7805）、Quick Slots（EIP-8198），以及一組資料定價調整方案（EIP 8131 與 8279），都列為「S 級」候選提案。Quick Slots 的目標，是在一年內，將目前 12 秒的區塊時槽（slot）時間，縮短到大約 10 秒——Ethlabs 團隊列出的理由包括：改善確認流程的使用者體驗、讓 DEX 價差與流動性提供者（LP）經濟模型能取得更即時的鏈上價格、加快最終確定性（finality），以及強化抗審查能力。Frame Transactions（EIP-8141）則獲得「A 級」評等，是 Ethlabs 團隊偏好的原生帳戶抽象化（account abstraction）設計方案，能支援通行金鑰（passkey）錢包、贊助交易、以 ERC-20 代幣支付 Gas 費、交易批次處理，並為 Railgun 等隱私協定提供一等公民等級的支援——評等較低，反映的是「採用協調上的風險」，而非技術層面的疑慮。值得注意的是，Ethlabs 團隊並未替 Tapered Issuance Burn（EIP-8363）給出任何評等，而是將「以太幣發行量」定位為一個需要廣泛社群共識的貨幣政策問題，而不是可以透過標準的 AllCoreDevs 流程直接納入的一般提案。',
            vocab=[
                ('slot (v./n.)', '此處作動詞「將……安排、置入（某位置/分類）」，名詞則指以太坊的「時槽」。'),
                ('rationale (n.)', '「理據、原因說明」，常見於正式文件解釋某決策背後的邏輯。'),
                ('withhold (v.)', '「保留不給、不予提供」，常見於描述刻意不做出某個評斷或決定。'),
            ],
        ),
        dict(
            title_en='zkNSR: Zero-Knowledge Neuro-Symbolic Decision Engine',
            title_zh='zkNSR：零知識神經符號決策引擎',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='zkNSR is a decision engine that combines neuro-symbolic reasoning with STARK proofs to produce machine-verifiable decisions without exposing underlying data. The system routes decisions through a neural layer that proposes and extracts, then a symbolic layer that applies Horn clause policies, with STARK proofs replacing the private arithmetic leaves of each derivation. Third parties can verify in under a millisecond that an AI agent obeyed its published policy, with target applications in trading, DeFi credit decisions, and regulatory compliance proofs. The client-side WebAssembly implementation has binding composition formally verified in Lean, but cryptographic primitives remain unaudited, making external audit the gating requirement for production use.',
            body_zh='zkNSR 是一套決策引擎，結合了「神經符號推理（neuro-symbolic reasoning）」與 STARK 證明技術，能在不揭露底層資料的前提下，產出「機器可驗證」的決策結果。這套系統會先讓決策流經一個負責提案與擷取的神經網路層，接著再進入一個套用「霍恩子句（Horn clause）」政策規則的符號層，而 STARK 證明，則取代了每一步推導過程中原本私密的算術「葉節點」。第三方能在不到一毫秒的時間內，驗證某個 AI agent 是否確實遵循了其公開發布的政策，目標應用場景包括交易、DeFi 信用決策，以及法規合規性證明。這套用戶端（client-side）的 WebAssembly 實作，其綁定組合已經在 Lean 語言中經過形式化驗證，但底層的密碼學基礎元件，目前仍未經過稽核——這使得「外部稽核」成為正式上線使用前的必要關卡。',
            vocab=[
                ('verifiable (adj.)', '「可被驗證的」，verify（驗證）+ -able，密碼學/資安領域常見詞。'),
                ('route (v.)', '延續先前出現過的「導向、路由」動詞用法。'),
                ('gating requirement', '「作為關卡的必要條件」，gate 當動詞「設下關卡、把關」。'),
            ],
        ),
        dict(
            title_en='daos.fun Made $6.6M Insider Trading $ai16z',
            title_zh='daos.fun 靠內線交易 $ai16z 獲利 660 萬美元',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='On-chain data shows daos.fun operator baoskee liquidated the $ai16z execution wallet across 102 swaps from January through November 2025, generating $6.65M in profit on a 22 SOL (~$3,863) cost basis while holding advance knowledge that a16z’s legal pressure would force a token migration to $elizaOS. Baoskee had promised community voting as the required mechanism for any name change but withheld the feature, preserving sole execution-wallet control throughout the rebrand period while community holders absorbed the full price impact of the migration. Verified proceeds total $6,659,374, with sell activity spanning the interval between a16z’s private contact with the team and the public migration announcement.',
            body_zh='鏈上資料顯示，daos.fun 平台的營運者 baoskee，在 2025 年 1 月到 11 月間，透過 102 筆交易，清算了 $ai16z 的執行錢包——在僅 22 顆 SOL（約 3,863 美元）成本的基礎上，獲利高達 665 萬美元，而他當時已經事先知道，a16z 的法律壓力，將迫使代幣遷移至 $elizaOS。Baoskee 原本承諾，任何更名決策都必須經過「社群投票」這個必要機制，但他卻始終沒有真正推出這項功能——在整個品牌重塑（rebrand）期間，持續獨自掌控執行錢包的控制權，而社群持有者，則承受了這次代幣遷移所帶來的全部價格衝擊。經核實的所得總額為 6,659,374 美元，其賣出行為的時間範圍，橫跨了「a16z 私下聯繫團隊」到「公開宣布遷移」之間的這段期間。',
            vocab=[
                ('liquidate (v.)', '金融領域專有動詞「清算、變現」，指將資產轉換成現金或其他流動性資產。'),
                ('cost basis', '財經專有名詞「成本基礎」，指計算損益時所依據的原始取得成本。'),
                ('in advance', '「事先地、提前地」，常見固定片語，強調時間上的「提前」。'),
            ],
        ),
        dict(
            title_en='Tokenized Stock Holders More Than Double as Monthly Volume Surges',
            title_zh='代幣化股票持有人數翻倍，月交易量暴增',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Tokenized stock holders surpassed 1.31 million, more than doubling month-over-month, while monthly transfer volume climbed 179% to $23.13 billion and monthly active addresses rose 34.62% to 572,000. Ondo leads by distributed value at $872 million, followed by Kraken’s xStocks at $557.8 million and Binance’s bStocks at $521.8 million, with the latter launching in June and growing to $67.9 million in tokenized SpaceX exposure. The SpaceX listing exposed a supply constraint: xStocks could not secure sufficient underlying shares while Binance’s bStocks absorbed the overflow, revealing that institutional share availability rather than retail demand is the binding limit on tokenized pre-IPO growth.',
            body_zh='「代幣化股票」的持有人數，已突破 131 萬人，較上月成長逾一倍；月度轉帳量成長 179%，達到 231.3 億美元；月活躍地址數也成長 34.62%，來到 57.2 萬個。以「分發價值」計算，Ondo 以 8.72 億美元居冠，其次是 Kraken 的 xStocks（5.578 億美元）與幣安（Binance）的 bStocks（5.218 億美元）——bStocks 於六月才剛上線，如今在「代幣化 SpaceX 曝險部位」上，已成長至 6,790 萬美元。這次 SpaceX 的上架，暴露出一個供給面的限制：xStocks 未能取得足夠的實際股票來支撐代幣，而幣安的 bStocks，則承接了溢出的需求——這顯示出，真正限制「代幣化 Pre-IPO」股票成長的關鍵瓶頸，其實是機構端的股票供給量，而不是散戶端的需求。',
            vocab=[
                ('surpass (v.)', '「超越、超過」，語氣比 exceed 稍微正式/書面。'),
                ('month-over-month (MoM)', '財經報告常用縮寫「較上月」，用來描述逐月變化幅度。'),
                ('binding limit', '「（具有實際約束力的）限制、瓶頸」，binding 當形容詞「有約束力的」。'),
            ],
        ),
    ]),
    dict(name_zh='金融科技', name_en='TLDR Fintech', date='2026-08-17', summary_head='金融科技', articles=[
        dict(
            title_en='Nvidia Is the World\u2019s Largest Fintech Company',
            title_zh='Nvidia 其實是全球最大的金融科技公司',
            meta='原文閱讀時間：約 15 分鐘',
            body_en='Nvidia signed MOUs with six of the largest names in global capital to build financing platforms (think SPVs) to deploy over $500bn of third-party money for AI infrastructure. Jensen Huang went on CNBC flanked by the leadership of all six to pitch the idea, which is credited to him personally. He says compute is now an investable asset class, priced like real estate or toll roads rather than hardware that dies on a depreciation schedule.',
            body_zh='Nvidia 已與全球資本市場中六家規模數一數二的機構，簽署了合作備忘錄（MOU），打算建立融資平台（可以想成是 SPV，特殊目的公司），用來部署超過 5,000 億美元的第三方資金，投入 AI 基礎建設。黃仁勳（Jensen Huang）親自上 CNBC，由這六家機構的高層陪同站台，推銷這個被外界認為出自他個人構想的點子。他表示，「運算力」如今已經是一種「可投資的資產類別」，其定價邏輯更像是不動產或收費公路，而不是那種會按照折舊排程逐漸「死亡」報廢的硬體設備。',
            vocab=[
                ('MOU (memorandum of understanding)', '商業／法律縮寫「合作備忘錄」，是正式簽約前常見的意向性文件。'),
                ('SPV (special purpose vehicle)', '金融專有名詞「特殊目的公司／實體」，常用於將特定資產或專案風險獨立出來管理。'),
                ('flanked by X', '「由 X 陪同在側」，flank 原指「（位於）側翼」，常用於描述重要人物被其他人簇擁的畫面。'),
                ('pitch (v.)', '「推銷、提案說明」，新創／商業語境常見動詞，名詞則指「（向投資人做的）簡報提案」。'),
                ('be credited to sb.', '「被認為是某人的功勞／構想」，credit 在此作動詞，「歸功於」。'),
                ('asset class', '財經專有名詞「資產類別」，如股票、債券、不動產等不同投資標的分類。'),
            ],
        ),
        dict(
            title_en='Workday Shares Surge on Reported Silver Lake Takeover Talks',
            title_zh='傳出 Silver Lake 洽購消息，Workday 股價大漲',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Workday shares jumped nearly 18% after Reuters reported that Silver Lake has been in talks to acquire the enterprise software company, lifting its market value to nearly $51 billion. The potential deal comes as Workday faces investor concerns that AI could disrupt traditional software business models, even as the company has recently pointed to AI as a source of growth.',
            body_zh='在路透社報導私募股權公司 Silver Lake，正就收購企業軟體公司 Workday 進行洽談後，Workday 股價應聲大漲近 18%，市值也隨之攀升至近 510 億美元。這筆潛在交易發生的背景，是投資人正擔憂 AI 可能顛覆傳統的軟體商業模式——儘管 Workday 近期才剛將 AI 定位為公司成長的新動能來源。',
            vocab=[
                ('surge (v.)', '「（股價、數值）大幅飆升」，金融新聞高頻動詞。'),
                ('be in talks to V', '「正在洽談要做……」，常見於併購新聞的固定句型。'),
                ('disrupt (v.)', '「顛覆、破壞性創新」，科技／商業領域高頻字。'),
            ],
        ),
        dict(
            title_en='Kalshi in Talks to Raise $750M at $40B Valuation',
            title_zh='Kalshi 洽談以 400 億美元估值募資 7.5 億美元',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Kalshi is reportedly in advanced talks with Sequoia Capital and Wellington Management to raise at least $750 million at a $40 billion valuation, less than four months after raising $1 billion at $22 billion. The prediction market platform’s annualized revenue reportedly reached $4 billion in July, driven largely by sports contracts, as it widens its lead over Polymarket and considers a potential 2027 IPO.',
            body_zh='根據報導，預測市場平台 Kalshi 正與 Sequoia Capital 與 Wellington Management 進行深入洽談，計畫以 400 億美元估值，募得至少 7.5 億美元資金——距離上一輪以 220 億美元估值募得 10 億美元，還不到四個月的時間。據報導，這個預測市場平台七月的年化營收已達 40 億美元，主要由運動賽事合約帶動；該公司也持續拉開與競爭對手 Polymarket 之間的差距，並正在考慮於 2027 年進行首次公開發行（IPO）。',
            vocab=[
                ('advanced talks', '「深入／後期階段的洽談」，advanced 在此指「進展較後期的」，而非「先進的」。'),
                ('less than X after Y', '「距離 Y 不到 X 的時間」，常見於強調事件發生間隔之短。'),
                ('widen one’s lead over X', '「拉開領先 X 的差距」，lead 當名詞指「領先幅度」。'),
            ],
        ),
        dict(
            title_en='The Great Unbundling of Consumer Fintech',
            title_zh='消費金融科技的「大解綁」時代',
            meta='原文閱讀時間：約 10 分鐘',
            body_en='AI agents will weaken the traditional consumer fintech bundling model by making product discovery, switching, and financial administration dramatically easier. There is an opportunity for neutral AI-native platforms that sit above a user’s entire financial stack, continuously analyze finances, recommend better products, and execute actions such as moving money, refinancing loans, changing providers, and managing administrative workflows.',
            body_zh='AI agent 將會削弱傳統消費金融科技那套「綁定式（bundling）」商業模式，因為它們會讓「產品探索」、「更換服務商」與「財務行政管理」變得遠比以往容易。這也為那些「中立、AI 原生」的平台，創造出一個機會——這類平台能凌駕於使用者整體財務體系（financial stack）之上，持續分析財務狀況、推薦更好的產品，並直接執行諸如轉帳、貸款轉貸、更換服務商，以及管理各類行政流程等實際動作。',
            vocab=[
                ('bundling (n.)', '商業模式專有名詞「綁定銷售」，與 unbundling（解綁、拆分）相對。'),
                ('sit above X', '比喻用法，「（在架構上）凌駕於 X 之上」。'),
                ('refinance (v.)', '金融專有名詞「再融資、轉貸」，指以新貸款替換舊貸款以取得更好條件。'),
            ],
        ),
        dict(
            title_en='Robinhood’s Second Private Markets Fund Starts Trading',
            title_zh='Robinhood 第二檔私募市場基金正式掛牌交易',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Robinhood Ventures Fund II debuted on the NYSE after raising $225.5 million, giving retail investors exposure to early- and growth-stage private companies, with a focus on current and former Y Combinator startups. The launch expands Robinhood’s push into private markets following its first late-stage venture fund, as the company works on additional funds aimed at broadening retail access to startup investing.',
            body_zh='Robinhood Ventures Fund II 在募得 2.255 億美元之後，正式於紐約證券交易所（NYSE）掛牌上市，讓一般散戶投資人也能參與早期與成長期私人企業的投資機會，主要聚焦於現任與曾為 Y Combinator 校友的新創公司。這次的推出，延續了 Robinhood 在推出第一檔「後期新創創投基金」之後，持續進軍私募市場的布局——該公司目前正在籌備更多基金，目標是讓散戶更容易參與新創投資。',
            vocab=[
                ('debut (v.)', '此處作動詞「首次亮相、掛牌上市」。'),
                ('retail investors', '金融領域專有名詞「散戶投資人」，與 institutional investors（機構投資人）相對。'),
                ('exposure to X', '金融慣用語「對 X 的曝險部位、參與機會」。'),
            ],
        ),
        dict(
            title_en='Corgi Uses AI to Challenge BlackRock and Spark a New ETF Fee War',
            title_zh='Corgi 用 AI 挑戰貝萊德，掀起新一輪 ETF 費用戰',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Corgi Invest, the ETF arm of fintech startup Corgi Insurance, has launched 197 ETFs since December and expects to surpass BlackRock in total US ETF count by year-end, using AI to accelerate regulatory filings and product launches. The company is also undercutting competitors on fees across buffered income, leveraged, and single-stock ETFs, betting that lower costs and a vertically integrated insurance-float strategy can help it win assets over time.',
            body_zh='Corgi Invest 是金融科技新創公司 Corgi Insurance 旗下的 ETF 部門，自去年 12 月以來，已經推出了 197 檔 ETF，並預期能在年底前，於美國 ETF 總檔數上超越貝萊德（BlackRock）——靠的是運用 AI 來加速法規申報與產品上市流程。該公司同時也在緩衝收益型、槓桿型，以及單一個股型 ETF 等產品線上，以更低的費用率壓低競爭對手——賭的是「更低成本」搭配「垂直整合的保險浮存金策略」，長期下來能夠幫助它贏得更多資產規模。',
            vocab=[
                ('arm (n.)', '此處指企業的「部門、分支」，而非「手臂」。'),
                ('undercut (v.)', '商業競爭常見動詞「削價競爭、以更低價格搶市」。'),
                ('vertically integrated', '商業策略專有名詞「垂直整合的」，指企業掌控供應鏈中上下游多個環節。'),
            ],
        ),
        dict(
            title_en='What Capital Wants',
            title_zh='資本真正想要的是什麼（金融科技版）',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Startup fundraising has shifted toward a ‘team plus TAM’ market, where investors increasingly ask whether a company can become the clear winner in a market large enough to support a $20 billion outcome. With traditional sector mandates fading, founders now need to find true believers, educate investors on genuinely novel opportunities, or position themselves within the themes capital already believes it must own.',
            body_zh='新創募資，正逐漸轉向一個「團隊 + TAM（潛在市場規模）」導向的市場——投資人越來越常問的問題是：這家公司是否有機會，在一個大到足以撐起 200 億美元結果的市場中，成為明確的贏家。隨著傳統「產業別」投資授權逐漸式微，創辦人現在必須：找到真正相信自己的投資人、向投資人「教育」一個確實新穎的機會，或是把自己定位在資本市場「已經認定非投資不可」的主題範疇之內。',
            vocab=[
                ('TAM (total addressable market)', '創投術語「潛在市場總規模」，是評估新創公司成長天花板的核心指標之一。'),
                ('mandate (n.)', '此處指投資機構的「投資授權範疇」。'),
                ('fade (v.)', '「逐漸消退、淡化」，常見於描述某趨勢或做法逐漸失去主導地位。'),
            ],
        ),
        dict(
            title_en='Kalshi Cracks Down on Insider Trading as Trump Family Looks to Increase Prediction Market Presence',
            title_zh='川普家族擴大布局預測市場之際，Kalshi 出手打擊內線交易',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='The federally regulated exchange says its surveillance systems have flagged suspicious bets involving former Congressman George Santos, a White House teleprompter operator, and others, with cases referred to the CFTC. Meanwhile, Trump Media is developing TruthPredict and selling rapid access to Truth Social posts that could move financial markets. Donald Trump Jr. also advises Kalshi and has ties to rival Polymarket, creating an unusually close relationship between the presidency and platforms where political information can be traded.',
            body_zh='這家受聯邦監管的交易所表示，其監控系統已經標記出多筆可疑下注紀錄，涉及前國會議員 George Santos、一名白宮讀稿機操作員，以及其他人士，相關案件已轉交 CFTC（美國商品期貨交易委員會）處理。與此同時，Trump Media 正在開發 TruthPredict，並出售能快速取得「可能影響金融市場的 Truth Social 貼文」的存取權限。小唐納‧川普（Donald Trump Jr.）本身也擔任 Kalshi 的顧問，同時與競爭對手 Polymarket 也有關係——這使得「總統職位」與「可交易政治資訊的平台」之間，形成了一種異常緊密的關係。',
            vocab=[
                ('flag (v.)', '此處作動詞「標記、標示出（可疑項目）」，監控／資安領域常見用法。'),
                ('refer X to Y', '「將 X 轉交給 Y（處理）」，常見於法律／行政程序描述。'),
                ('ties to X', '「與 X 之間的關係／牽連」，tie 當名詞指「聯繫、牽扯」。'),
            ],
        ),
        dict(
            title_en='Stripe and Advent Talks to Acquire PayPal Are Heating Up',
            title_zh='Stripe 與 Advent 收購 PayPal 的談判正在升溫',
            meta='原文閱讀時間：約 2 分鐘',
            body_en='Stripe and Advent are reportedly still negotiating a potential acquisition of PayPal after their initial $60.50-per-share offer valued the company at roughly $53 billion, with a deal potentially coming together in the coming weeks. The talks come as CEO Enrique Lores pursues a broad turnaround that includes reorganizing PayPal into three operating units, refocusing on technology and AI, and cutting costs through a planned 20% workforce reduction.',
            body_zh='根據報導，Stripe 與 Advent 仍在就潛在收購 PayPal 一案持續協商——先前每股 60.50 美元的初步報價，將 PayPal 估值定在約 530 億美元，這筆交易有可能在接下來幾週內拍板定案。這輪協商發生的背景，是執行長 Enrique Lores 正在推動一項全面的公司轉型計畫，內容包括：將 PayPal 重組為三個營運部門、把重心重新聚焦在技術與 AI 上，並透過預計裁員 20% 的人力精簡計畫來降低成本。',
            vocab=[
                ('value X at Y', '「將 X 估值為 Y」，常見於併購新聞的固定句型。'),
                ('come together', '片語，「（計畫、交易）最終成形、拍板定案」。'),
                ('turnaround (n.)', '商業領域專有名詞「（企業）轉型、扭轉頹勢」。'),
            ],
        ),
    ]),
    dict(name_zh='IT 產業', name_en='TLDR IT', date='2026-08-18', summary_head='IT 產業', articles=[
        dict(
            title_en='GitHub Outage Disrupts Developers Worldwide',
            title_zh='GitHub 大規模中斷，全球開發者受影響',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='GitHub suffered a widespread outage Monday that disrupted repositories, APIs, GitHub Actions, Copilot, and enterprise authentication services, including SAML, OIDC, and SCIM. Error rates reached roughly 20% across web and API traffic and about 50% for raw repository and archive downloads before GitHub identified the faulty component and restored service later in the day.',
            body_zh='GitHub 在週一發生了大規模的服務中斷，影響範圍涵蓋儲存庫、API、GitHub Actions、Copilot，以及企業身分驗證服務（包括 SAML、OIDC、SCIM 等）。在 GitHub 找出故障元件並於當天稍晚恢復服務之前，網頁與 API 流量的錯誤率一度達到約 20%，而原始儲存庫與封存檔下載的錯誤率更高達約 50%。',
            vocab=[
                ('suffer an outage', '固定搭配片語，「發生服務中斷」，suffer 在此指「遭受（某種負面事件）」。'),
                ('widespread (adj.)', '「大規模的、廣泛的」，常修飾影響範圍很廣的事件。'),
                ('disrupt (v.)', '「打斷、擾亂（正常運作）」，IT／資安新聞高頻動詞。'),
                ('authentication (n.)', '「身分驗證」，動詞是 authenticate，資安領域核心概念。'),
                ('error rate', '「錯誤率」，常見的系統可靠性指標，由 error（錯誤）＋ rate（比率）組成。'),
                ('faulty component', '「故障元件」，faulty 是 fault（故障、瑕疵）的形容詞形式。'),
            ],
        ),
        dict(
            title_en='We Churned Notion After 7 Years. Our AI Agent Took Its Last Job.',
            title_zh='用了七年後，我們取消了 Notion 訂閱——因為 AI Agent 接手了它最後的工作',
            meta='原文閱讀時間：約 6 分鐘',
            body_en='SaaStr canceled Notion after seven years, not because of pricing, support, or a competing product, but because an internal AI agent gradually absorbed the last workflow it was being used for. This creates a new kind of SaaS churn: narrow-purpose tools can disappear from the stack as agents connect directly to company data and take over their jobs, making traditional usage and customer-health metrics less reliable.',
            body_zh='SaaStr 公司在使用 Notion 七年之後，決定取消訂閱——原因既不是價格、也不是客服支援，更不是因為轉用了競爭對手的產品，而是因為公司內部的一個 AI agent，逐漸「吃掉」了 Notion 僅存的最後一項使用情境（workflow）。這催生出一種全新型態的 SaaS 流失（churn）：當 agent 能夠直接連接公司資料、並接手原本工具的工作時，那些「用途單一」的工具，就可能從整個技術堆疊（stack）中直接消失——這也讓傳統的「使用量」與「客戶健康度」指標，變得愈來愈不可靠。',
            vocab=[
                ('churn (v./n.)', '訂閱制商業模式核心詞彙「流失（客戶取消訂閱）」，SaaS 產業高頻詞（customer churn、churn rate）。'),
                ('gradually (adv.)', '「逐漸地」，與 suddenly（突然地）相對，強調變化緩慢累積的過程。'),
                ('absorb (v.)', '本義「吸收」，此處引申為「（逐漸）吞併、接管（某項工作／功能）」。'),
                ('narrow-purpose (adj.)', '複合形容詞「用途單一的、功能單一的」，narrow 在此指「範圍狹窄的」。'),
                ('tech stack', '軟體工程常用語「技術堆疊」，泛指一個系統或組織所使用的整套工具與技術。'),
                ('customer-health metrics', '商業／SaaS 領域專有名詞「客戶健康度指標」，用來評估客戶續訂／流失風險的量化指標。'),
            ],
        ),
        dict(
            title_en='Make Zero CVEs Your New Default',
            title_zh='把「零 CVE」變成新的預設值',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Docker has announced updates aimed at making zero-CVE container images the default across the software supply chain. The company says its Hardened Images catalog now extends to hardened Alpine and Debian packages, supports patching beyond software end of life, and offers customization with maintained provenance, while Docker AI Governance records agent policy decisions in Docker Cloud and streams them to existing SIEM systems.',
            body_zh='Docker 宣布了一系列更新，目標是讓「零 CVE（零已知漏洞）」的容器映像檔，成為整個軟體供應鏈的預設狀態。該公司表示，其「強化映像檔（Hardened Images）」目錄，現在已擴及強化版的 Alpine 與 Debian 套件，支援在軟體「終止支援（end of life）」後仍持續修補，並提供可維持來源可追溯性（provenance）的客製化功能；同時，Docker AI Governance 功能，則會將 agent 的政策決策紀錄在 Docker Cloud 中，並串流傳送給既有的 SIEM 系統。',
            vocab=[
                ('CVE', '資安領域專有縮寫「通用漏洞揭露」，是業界對已知安全漏洞的標準編號系統。'),
                ('end of life (EOL)', '軟體工程專有名詞「終止支援」，指廠商停止提供更新與維護支援的時間點。'),
                ('stream X to Y', '此處作動詞「將 X 串流傳送至 Y」，IT 領域常見於描述即時資料傳輸。'),
            ],
        ),
        dict(
            title_en='Agentic AI in the Enterprise: How to Balance Autonomy With Constraints',
            title_zh='企業級 Agentic AI：如何在自主性與限制之間取得平衡',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Enterprise AI agents become much easier to operate safely when their autonomy is bounded by explicit controls around permissions, tool access, verification, state, and approvals. Treat agents like production systems: use narrow tool permissions, durable audit trails, deterministic checks before writes, staged rollouts, cost and step limits, and human approval for higher-impact actions.',
            body_zh='當企業級 AI agent 的自主性，被明確的控管機制——涵蓋權限、工具存取、驗證、狀態，以及核准流程——所限定範圍時，要安全地操作它們，就會變得容易許多。應該把 agent 當成「正式環境系統（production system）」來對待：採用範圍限縮的工具權限、具持久性的稽核軌跡、寫入前的確定性檢查、分階段的推出、成本與步驟數量上限，以及對高影響力動作要求人工核准。',
            vocab=[
                ('bounded by X', '「受 X 所限定範圍的」，bound（限定範圍）的過去分詞當形容詞用。'),
                ('audit trail', 'IT／資安領域專有名詞「稽核軌跡」，指記錄系統操作歷程以供事後追查的紀錄。'),
                ('deterministic (adj.)', '電腦科學專有名詞「確定性的」，指相同輸入必產生相同輸出，與 probabilistic 相對。'),
            ],
        ),
        dict(
            title_en='How to Level Up from IT Management to IT Leadership',
            title_zh='如何從 IT 管理職晉升到 IT 領導職',
            meta='原文閱讀時間：約 14 分鐘',
            body_en='Moving from IT management into senior leadership requires more than technical depth: leaders need business acumen, strong communication, stakeholder trust, and the ability to connect technology investments to measurable outcomes. CIOs and rising technology executives also emphasize taking on high-impact projects, learning from failed initiatives, prioritizing what not to do, and developing mentors who can help broaden their perspective.',
            body_zh='從 IT 管理職，晉升到資深領導職位，需要的不只是技術深度：領導者還需要具備商業敏銳度、強大的溝通能力、利害關係人的信任，以及能將技術投資，與可量化成果連結起來的能力。多位 CIO 與嶄露頭角的科技高階主管也強調，應該主動承接高影響力的專案、從失敗的計畫中學習、清楚判斷「哪些事不該做」的優先順序，並培養能拓展自身視野的導師關係。',
            vocab=[
                ('acumen (n.)', '「敏銳度、精明的判斷力」，常見搭配 business acumen（商業敏銳度）。'),
                ('stakeholder (n.)', '商業／管理學專有名詞「利害關係人」，泛指與某決策或專案有利害關係的所有相關人士。'),
                ('take on X', '片語，「承接、擔起（專案、責任）」。'),
            ],
        ),
        dict(
            title_en='Why It Hasn’t Happened Yet',
            title_zh='為什麼那件事還沒發生（AI 資安事件反思）',
            meta='原文閱讀時間：約 31 分鐘',
            body_en='Recent AI-related hacking incidents at OpenAI, Anthropic, AISI, and Hugging Face should prompt an urgent, industry-wide effort to strengthen operational security. Although limited damage occurred because the models lacked malicious intent, the incidents demonstrated powerful capabilities that could become more dangerous as models improve. Existing protections include alignment training, security classifiers, abuse detection, and conventional security, but each has weaknesses.',
            body_zh='近期發生在 OpenAI、Anthropic、AISI，以及 Hugging Face 的多起「與 AI 相關」的駭客入侵事件，應該促使整個產業，展開一場刻不容緩的行動，全面強化營運層面的資安。雖然這些事件造成的實際損害有限——因為模型本身並不具備惡意意圖——但這些事件依然展現出強大的能力，而隨著模型持續進步，這種能力未來可能變得更加危險。目前既有的防護機制包括：對齊訓練（alignment training）、資安分類器、濫用偵測，以及傳統資安措施，但每一種防護，都各自存在弱點。',
            vocab=[
                ('prompt (v.)', '此處作動詞「促使、引發」，而非名詞「提示詞」——是常見的一詞多義字。'),
                ('malicious intent', '資安領域固定用語「惡意意圖」，intent 指「意圖、企圖」。'),
                ('alignment training', 'AI 安全領域專有名詞「對齊訓練」，指訓練模型使其行為符合人類意圖與價值觀的技術。'),
            ],
        ),
        dict(
            title_en='Dynatrace Acquires Arize as AI Agents Deepen the Observability Challenge',
            title_zh='因應 AI Agent 帶來的可觀測性挑戰，Dynatrace 收購 Arize',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Dynatrace is acquiring AI observability company Arize for roughly $915 million, combining Arize’s visibility into model outputs, agent behavior and tool use with Dynatrace’s application and infrastructure telemetry. The goal is to give DevOps and platform teams a clearer way to trace AI-agent failures back through the services, transactions and systems they affect.',
            body_zh='Dynatrace 正以約 9.15 億美元的價格，收購 AI 可觀測性（observability）公司 Arize——將 Arize 對「模型輸出、agent 行為與工具使用」的洞察能力，與 Dynatrace 既有的應用程式與基礎設施遙測（telemetry）能力相結合。這麼做的目標，是讓 DevOps 與平台團隊，能更清楚地將 AI agent 的故障，回溯追蹤到它所影響的服務、交易與系統上。',
            vocab=[
                ('observability (n.)', 'IT／系統工程專有名詞「可觀測性」，指透過外部輸出來理解系統內部狀態的能力。'),
                ('telemetry (n.)', '「遙測（資料）」，指系統自動蒐集並回傳的監控資料。'),
                ('trace X back through Y', '「將 X 沿著 Y 回溯追蹤」，常見於描述故障排除的過程。'),
            ],
        ),
        dict(
            title_en='Alipay Unveils Full-Stack Agentic Commerce Infrastructure in China',
            title_zh='支付寶在中國發表全端 Agentic 商務基礎架構',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Alipay introduced a full-stack agentic commerce foundation and its AHA multi-agent, cross-device interconnection protocol suite at an AI ecosystem conference in Hangzhou. The initiative gives merchants tools to convert services into agent-accessible capabilities, while enabling agents across devices and vendors to coordinate authorization, fulfillment, and settlement, with Alipay reporting thousands of adapted services and partnerships across smartphones and automakers.',
            body_zh='支付寶（Alipay）在杭州舉行的一場 AI 生態系會議上，發表了一套「全端 agentic 商務基礎架構」，以及名為 AHA 的多 agent、跨裝置互連協定套組。這項倡議，提供商家能將自身服務轉換成「agent 可存取能力」的工具，同時讓分屬不同裝置與不同廠商的 agent，得以協調處理授權、履約（fulfillment）與結算等流程——支付寶表示，目前已有數千項服務完成適配，並與多家手機廠商及汽車製造商建立合作關係。',
            vocab=[
                ('full-stack (adj.)', '軟體工程常用複合形容詞「全端的」，此處引申為「涵蓋完整商務流程」。'),
                ('fulfillment (n.)', '電商／物流領域專有名詞「履約」，指完成訂單交付的整個流程。'),
                ('settlement (n.)', '金融領域專有名詞「結算」，指交易最終完成資金/資產移轉的程序。'),
            ],
        ),
        dict(
            title_en='Humanity in Open Source',
            title_zh='開源世界裡的「人味」',
            meta='原文閱讀時間：約 13 分鐘',
            body_en='End-to-end AI agents are flooding open-source maintainers with low-quality issues and pull requests, shifting effort away from coding and toward review. While AI-assisted human contributions can be useful, open source also depends on qualities that automated patches cannot replace, such as human conversation, relationships, and sustained collaboration.',
            body_zh='端到端的 AI agent，正對開源專案的維護者，湧入大量低品質的議題（issue）與 pull request，把維護者原本花在「寫程式」上的心力，被迫轉移到「審查」上。雖然「有 AI 輔助的人類貢獻」確實可能帶來價值，但開源生態，終究仰賴著一些自動化修補程式無法取代的特質——例如人與人之間的對話、關係，以及持續不斷的協作。',
            vocab=[
                ('end-to-end (adj.)', '複合形容詞「端到端的」，指涵蓋整個流程從頭到尾、無需人工介入銜接的系統。'),
                ('flood sb. with X', '「讓某人被大量 X 淹沒」，flood 原意「洪水」，此處作動詞表示「大量湧入」。'),
                ('sustained (adj.)', '「持續不斷的」，sustain（維持）的過去分詞當形容詞用。'),
            ],
        ),
    ]),
    dict(name_zh='資料工程', name_en='TLDR Data', date='2026-08-17', summary_head='資料工程', articles=[
        dict(
            title_en='How We Tracked Down a 16-Year-Old SQLite Bug',
            title_zh='我們如何追出一個潛藏 16 年的 SQLite 臭蟲',
            meta='原文閱讀時間：約 13 分鐘',
            body_en='Tailscale spent six months tracing repeated SQLite corruption to a rare 16-year-old race condition between WAL checkpointing and write transactions, triggered more often by its aggressive manual checkpointing. The investigation led to a SQLite fix, stronger recovery tooling, and a broader lesson that even \u2018boring\u2019 technology becomes risky when operated outside its common paths.',
            body_zh='Tailscale 公司花了整整六個月的時間追查，終於將反覆出現的 SQLite 資料庫損毀問題，追溯到一個潛藏長達 16 年之久、機率極低的競爭條件（race condition）——發生在 WAL（預寫式日誌）檢查點（checkpointing）機制與寫入交易（write transaction）之間，而該公司「積極主動」的手動檢查點做法，又讓這個問題被觸發得更加頻繁。這場調查最終促成了一項 SQLite 的修補，催生出更強健的復原（recovery）工具，也帶來一個更廣泛的啟示：即使是像 SQLite 這樣「無聊乏味」的成熟技術，一旦被用在偏離常規的使用路徑上，依然可能變得充滿風險。',
            vocab=[
                ('trace X to Y', '片語，「將 X 追溯到 Y」，常用於描述查找問題根本原因的過程。'),
                ('corruption (n.)', '軟體／資料工程領域常見詞「（資料）損毀」，動詞是 corrupt。'),
                ('race condition', '電腦科學專有名詞「競爭條件」，指多個程序／執行緒同時存取共享資源時，因執行順序不確定而產生的錯誤。'),
                ('checkpointing (n.)', '資料庫系統專有名詞「檢查點機制」，指定期將記憶體中的變更寫回磁碟以確保資料一致性的過程。'),
                ('trigger (v.)', '「觸發、引發」，常見於描述某條件導致特定事件發生。'),
                ('operate outside its common paths', '「在偏離常規的路徑上運作」，common paths 在此指「一般、常見的使用方式」。'),
            ],
        ),
        dict(
            title_en='Change-Data-Capture Doesn\u2019t Solve Dual-Writes',
            title_zh='CDC（異動資料擷取）解決不了「雙重寫入」問題',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='CDC makes downstream writes retryable, ordered, and observable, but it does not make destination systems safe to write twice. The destination still needs durable idempotency or a way to reject duplicates after recovery. This is a useful design-review lens for teams treating CDC as an automatic consistency fix.',
            body_zh='CDC（異動資料擷取，Change-Data-Capture）能讓下游的寫入動作變得「可重試、有順序、可被觀察」，但這並不代表目的端系統，就可以安全地被重複寫入兩次。目的端系統仍然需要具備「持久的冪等性（idempotency）」，或是要有辦法在系統復原後拒絕重複的資料。對於那些把 CDC 當成「自動一致性解方」的團隊來說，這是一個很值得拿來檢視自身系統設計的觀察角度。',
            vocab=[
                ('downstream (adj./adv.)', '資料工程常用詞「下游的」，指資料流向的後段系統，與 upstream（上游）相對。'),
                ('retryable (adj.)', '「可重試的」，由 retry（重試）＋ -able（可……的）組成，是工程領域常見造字方式。'),
                ('idempotency (n.)', '電腦科學專有名詞「冪等性」，指同一個操作無論執行一次或多次，結果都保持一致的特性。'),
                ('reject duplicates', '「拒絕重複（的資料／請求）」，reject 在此為動詞「拒絕、駁回」。'),
                ('a design-review lens', '「一種設計檢視的視角／切入點」，lens 原指「鏡頭」，引申為「觀察事物的角度」。'),
                ('treat N as X', '片語，「把 N 當作 X 來看待」，常見於描述某種（可能錯誤的）認知或假設。'),
            ],
        ),
        dict(
            title_en='Scratch a Simple Data Model, Find a Complex One',
            title_zh='刮開一個簡單的資料模型，底下都是複雜',
            meta='原文閱讀時間：約 14 分鐘',
            body_en='A seemingly simple Bible data model quickly breaks down once real-world cases like verse ranges, missing verses, alternate numbering, repeated chapters, and out-of-order text appear. The practical lesson is to model only the complexity the product actually needs, rather than chasing perfect fidelity by default.',
            body_zh='一個表面上看起來很單純的「聖經資料模型」，一旦遇上現實世界中的各種案例——像是經文範圍、缺漏的經節、替代編號方式、重複的章節，以及順序錯亂的文字——很快就會瓦解崩潰。這其中實用的教訓是：資料模型只需要對應「產品實際需要」的複雜度就好，而不是預設就要一味追求完美的還原度。',
            vocab=[
                ('break down', '片語動詞「瓦解、失效」，常見於描述系統或模型在特定情況下失去作用。'),
                ('out-of-order (adj.)', '複合形容詞「順序錯亂的」，常見於描述資料或事件未按預期順序排列。'),
                ('chase X by default', '「預設就一味追求 X」，chase 原意「追逐」，此處引申為「執著追求」。'),
            ],
        ),
        dict(
            title_en='Point Lookups on the Lakehouse: How Hudi Indexes Accelerate Read-Heavy Workloads',
            title_zh='湖倉上的單點查詢：Hudi 索引如何加速高讀取負載',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Apache Hudi’s metadata-table indexes make selective lakehouse reads behave more like database lookups than full scans. Record-level, secondary, expression, and bloom-filter indexes can prune equality predicates to a few files.',
            body_zh='Apache Hudi 的中繼資料表索引（metadata-table index），讓「湖倉（lakehouse）」中的選擇性讀取，表現得更像是資料庫查詢，而不是全表掃描（full scan）。記錄層級索引、次要索引、運算式索引，以及布隆過濾器（bloom-filter）索引，都能將「等值條件查詢」的搜尋範圍，大幅裁剪（prune）到僅剩少數幾個檔案。',
            vocab=[
                ('selective (adj.)', '「選擇性的」，此處指只讀取特定符合條件的資料，而非全部讀取。'),
                ('full scan', '資料庫領域專有名詞「全表掃描」，指逐一檢查表中每一筆資料的低效率查詢方式。'),
                ('prune (v.)', '原意「修剪（樹枝）」，資料工程領域引申為「裁減、削減（搜尋範圍）」。'),
            ],
        ),
        dict(
            title_en='Why AI Is a Storage Workload',
            title_zh='為什麼說 AI 其實是一種「儲存」工作負載',
            meta='原文閱讀時間：約 11 分鐘',
            body_en='AI inference is becoming stateful infrastructure: long-context sessions, agents, RAG, and multimodal workflows create durable KV caches, prefixes, memories, and embeddings that are cheaper to store than recompute after enough reuse. The storage hierarchy is moving into the hot path, with HBM, DRAM, SSDs, object storage, CXL, and flash tiers shaping latency and cost.',
            body_zh='AI 推論，正逐漸變成一種「有狀態（stateful）」的基礎設施：長上下文的工作階段、agent、RAG（檢索增強生成），以及多模態工作流程，都會產生需要持久保存的 KV 快取、前綴（prefix）、記憶，以及嵌入向量（embedding）——這些資料，只要重複使用的次數夠多，「儲存起來」反而會比「重新計算」更划算。儲存體系（storage hierarchy），正逐漸被納入系統的關鍵路徑（hot path）之中，HBM、DRAM、SSD、物件儲存、CXL，以及快閃記憶體等不同層級，都在共同形塑著延遲與成本。',
            vocab=[
                ('stateful (adj.)', '電腦科學專有名詞「有狀態的」，指系統會保留先前互動的記憶，與 stateless 相對。'),
                ('durable (adj.)', '「持久的、耐用的」，資料工程領域常用於形容資料能長期可靠地保存。'),
                ('hot path', '系統工程慣用語「關鍵路徑」，指系統中對效能影響最直接、最頻繁被執行的核心路徑。'),
            ],
        ),
        dict(
            title_en='On Benchmarking',
            title_zh='談基準測試這件事',
            meta='原文閱讀時間：約 7 分鐘',
            body_en='A throughput number is not an architecture decision. Good benchmarks explain the workload, cache state, client behavior, failure modes, and scaling limit behind the result. Without that context, teams risk optimizing for a synthetic score instead of the bottlenecks their production data systems will actually hit.',
            body_zh='一個「吞吐量（throughput）」數字，本身並不等於一項架構決策。好的基準測試，會清楚說明數字背後的工作負載、快取狀態、客戶端行為、失效模式，以及擴展極限。如果缺乏這些脈絡資訊，團隊就有可能誤把心力，花在優化一個「人造的分數」上，而不是真正處理正式環境資料系統實際上會遇到的瓶頸。',
            vocab=[
                ('throughput (n.)', '系統效能領域核心指標「吞吐量」，指單位時間內系統能處理的工作量。'),
                ('synthetic (adj.)', '「人造的、合成的」，此處指「非真實情境下產生的」，與真實世界表現相對。'),
                ('bottleneck (n.)', '「瓶頸」，泛指限制整體系統效能的關鍵限制點。'),
            ],
        ),
        dict(
            title_en='How Kenn Is Doing Agentic Engineering',
            title_zh='Kenn 如何實踐 Agentic 工程',
            meta='原文閱讀時間：約 8 分鐘',
            body_en='Kenn uses coding agents at high volume while keeping humans in control of design, review, and final decisions. Detailed specs, adversarial reviews, and continuous verification let three engineers ship hundreds of PRs weekly without relying on autonomous loops.',
            body_zh='Kenn 大量使用編碼 agent，但同時仍讓「人類」掌控設計、審查與最終決策的權力。透過詳盡的規格文件、對抗性審查（adversarial review），以及持續不斷的驗證機制，讓僅僅三名工程師，就能在不依賴「自主迴圈（autonomous loop）」的情況下，每週產出數百個 PR。',
            vocab=[
                ('at high volume', '「大量地」，volume 在此指「數量規模」。'),
                ('keep sb. in control of X', '「讓某人持續掌控 X」，呼應先前出現過的 keep 使役動詞用法。'),
                ('adversarial (adj.)', '「對抗性的」，adversary（對手）的形容詞形式，常見於資安/AI 領域。'),
            ],
        ),
        dict(
            title_en='Apache DataFusion Comet 1.0.0 Release',
            title_zh='Apache DataFusion Comet 正式發布 1.0 版',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='Comet, the Spark accelerator built on Apache DataFusion, reached 1.0 with semantic versioning, Spark 4 support, broader operator coverage, and extensive correctness testing against Spark’s own suite. It is aimed at teams that want faster Spark execution without rewriting jobs or replacing the surrounding Spark ecosystem.',
            body_zh='Comet 是一款建構在 Apache DataFusion 之上的 Spark 加速器，如今已正式發布 1.0 版本——採用語意化版本控制（semantic versioning）、支援 Spark 4、擴大運算子（operator）涵蓋範圍，並針對 Spark 自身的測試套件，進行了大量的正確性測試。它的目標客群，是那些希望加速 Spark 執行效能、但又不想重寫作業（job）、也不想替換掉周邊既有 Spark 生態系的團隊。',
            vocab=[
                ('semantic versioning', '軟體工程專有名詞「語意化版本控制」，一套依循版本號規則命名的慣例。'),
                ('operator coverage', '「運算子涵蓋範圍」，operator 在資料處理語境中指執行特定運算的元件。'),
                ('aimed at X', '「以 X 為目標對象」，常見於產品定位描述。'),
            ],
        ),
        dict(
            title_en='Introducing DataBench',
            title_zh='DataBench 上線：測試 AI 分析能力的新基準',
            meta='原文閱讀時間：約 22 分鐘',
            body_en='Hex’s DataBench tests AI agents on realistic, messy analytics tasks and finds they are strong at gathering evidence but weaker at open-ended decisions where judgment matters. Models often fail by manufacturing certainty, missing subtle data traps or overthinking correct answers, showing why human review is still essential for complex analytical work.',
            body_zh='Hex 公司推出的 DataBench，用「真實、雜亂」的分析任務來測試 AI agent，結果發現：這些 agent 在「蒐集證據」方面表現不錯，但在需要仰賴判斷力的「開放式決策」上，表現則相對較弱。這些模型常見的失敗模式包括：「捏造出虛假的確定性」、漏看資料中細微的陷阱，或是對本來已經答對的問題「想太多」——這也說明了，為什麼在複雜的分析工作中，人工審查依然不可或缺。',
            vocab=[
                ('messy (adj.)', '「雜亂的、不整潔的」，資料科學領域常用於形容未經清理、充滿雜訊的真實世界資料。'),
                ('open-ended (adj.)', '複合形容詞「開放式的」，指沒有單一標準答案、需要主觀判斷的問題或任務。'),
                ('manufacture (v.)', '此處作動詞「捏造、人為製造出（不真實的東西）」，而非「（工廠）製造」的常見義。'),
            ],
        ),
        dict(
            title_en='What’s New in OpenSearch 3.8',
            title_zh='OpenSearch 3.8 有哪些新功能',
            meta='原文閱讀時間：約 7 分鐘',
            body_en='OpenSearch 3.8 improves vector ingestion, radial query throughput, and median query latency while expanding AI-agent support. MCP now works across all agent types, tool discovery is richer, and gRPC streaming inference lowers token latency. Analytics teams also get new PPL/SQL tooling, Grok debugging, one-click Prometheus alerts, and search-relevance workflow improvements.',
            body_zh='OpenSearch 3.8 改善了向量資料擷取（ingestion）效能、放射狀查詢（radial query）的吞吐量，以及查詢延遲的中位數表現，同時擴大了對 AI agent 的支援。MCP 現在能適用於所有類型的 agent、工具探索功能也更加豐富，而 gRPC 串流推論，則降低了 token 延遲。分析團隊也獲得了新的 PPL/SQL 工具、Grok 除錯功能、一鍵設定的 Prometheus 警示，以及搜尋相關性工作流程的多項改進。',
            vocab=[
                ('ingestion (n.)', '資料工程專有名詞「（資料）擷取、匯入」，常見於描述資料進入系統的第一道程序。'),
                ('median (n./adj.)', '統計學專有名詞「中位數（的）」，與 average/mean（平均值）為不同的統計概念。'),
                ('one-click (adj.)', '複合形容詞「一鍵式的」，強調操作極度簡便。'),
            ],
        ),
        dict(
            title_en='Snowflake Says This 149 GB Query Scanned -1.5 GB',
            title_zh='Snowflake：這個 149GB 的查詢竟然掃描了 -1.5GB',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Unloading Snowflake QUERY_HISTORY data to Parquet can corrupt values when large numbers are written as INT32. Casting the nine affected columns before export prevents overflow, bad joins, and incorrect analysis.',
            body_zh='把 Snowflake 的 QUERY_HISTORY 資料「卸載（unload）」匯出成 Parquet 格式時，如果數值過大卻被寫成 INT32（32 位元整數）格式，可能會導致數值損毀。在匯出之前，先對九個受影響的欄位進行型別轉換（casting），就能避免溢位（overflow）、錯誤的資料表連結（join），以及不正確的分析結果。',
            vocab=[
                ('unload (v.)', '資料工程術語「卸載、匯出」，指將資料從資料庫系統匯出至外部檔案的動作。'),
                ('corrupt (v.)', '動詞「（使）損毀」。'),
                ('cast (v.)', '程式設計專有名詞「（型別）轉換」，指將資料從一種型別強制轉換為另一種型別。'),
            ],
        ),
        dict(
            title_en='Fairly Ranking the Most Brilliant Birds',
            title_zh='如何公平地為「最鮮豔的鳥類」排名',
            meta='原文閱讀時間：約 19 分鐘',
            body_en='A transparent ranking of the world’s most brilliant birds combines chroma, colour variety, sample confidence and diversity, placing the orange-breasted bunting first. The bigger idea is that ranking systems are fairest when every factor is understandable, defensible and tied to a reasonable human judgement.',
            body_zh='一份公開透明的「全球最鮮豔鳥類」排行榜，綜合了色度（chroma）、色彩多樣性、樣本信賴度，以及多樣性等指標，最終將橙胸鵐（orange-breasted bunting）列為榜首。這篇文章想傳達的更大概念是：一套排名系統要做到公平，前提是每一項評分因子，都必須是「可理解的、站得住腳的」，並且與合理的人類判斷相互連結。',
            vocab=[
                ('transparent (adj.)', '「透明的、公開可查驗的」，常用於形容評分/決策過程公開可追溯，而非黑箱作業。'),
                ('chroma (n.)', '色彩學專有名詞「色度」，用來描述顏色的純度與飽和程度。'),
                ('defensible (adj.)', '「站得住腳的、可被合理辯護的」，常見於形容論點或評分標準經得起質疑。'),
            ],
        ),
    ]),
    dict(name_zh='硬體', name_en='TLDR Hardware', date='2026-08-17', summary_head='硬體', articles=[
        dict(
            title_en='Nvidia Discloses $21bn Stake in SpaceX, Ties It Deeper Into Musk\u2019s Data Center Buildout',
            title_zh='Nvidia 揭露持有 SpaceX 210 億美元股權，與馬斯克資料中心版圖更加綁定',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Nvidia\u2019s SEC filing revealed it holds nearly 123 million SpaceX shares, worth roughly $21 billion at the end of June (now closer to $17 billion after SpaceX\u2019s post-IPO share slide), a stake that originated through Nvidia\u2019s investment in xAI before Musk merged it into SpaceX. It comes right after Musk confirmed SpaceX will build its data centers exclusively on Nvidia hardware, citing the Vera Rubin architecture as \u201cthe best AI computer,\u201d locking in another major customer to Nvidia\u2019s silicon while Nvidia simultaneously holds equity in that same customer.',
            body_zh='Nvidia 向美國證券交易委員會（SEC）提交的文件揭露，該公司持有近 1.23 億股 SpaceX 股份，截至六月底價值約 210 億美元（在 SpaceX 上市後股價下滑之後，目前價值較接近 170 億美元）——這筆股權的起源，來自 Nvidia 先前對 xAI 的投資，而在馬斯克（Musk）將 xAI 併入 SpaceX 之後，便隨之轉換為 SpaceX 的股份。這項消息公布的時間點，緊接在馬斯克證實「SpaceX 的資料中心將完全採用 Nvidia 硬體」之後——他將 Vera Rubin 架構稱為「最好的 AI 電腦」，這等於是把另一個重量級客戶，牢牢綁定在 Nvidia 的晶片生態系中，而與此同時，Nvidia 本身也持有這位客戶的股權。',
            vocab=[
                ('SEC filing', '金融領域固定用語「（向美國證交會提交的）申報文件」，filing 在此作名詞，指正式提交的文件。'),
                ('stake (n.)', '「股權、股份權益」，常與動詞 hold（持有）搭配使用（hold a stake in X）。'),
                ('originate through X', '「透過 X 而產生／起源」，originate 是「起源」的動詞形式。'),
                ('merge N into X', '「將 N 併入 X」，常見於企業併購／組織重組的描述。'),
                ('cite X as Y', '「將 X 稱作／引述為 Y」，cite 原指「引用」，此處引申為「舉出並稱之為」。'),
                ('lock in (phr. v.)', '片語動詞「牢牢綁定、鎖定」，常見於商業語境描述客戶或合作關係被穩固確立。'),
            ],
        ),
        dict(
            title_en='Nvidia Jetson Chip Found in Russian Cruise Missile',
            title_zh='俄羅斯巡弋飛彈中發現 Nvidia Jetson 晶片',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Ukrainian military intelligence says Russia\u2019s S-71 \u2018Monochrome\u2019 cruise missile, which offers reduced observability and autonomous targeting, uses an Nvidia Jetson Orin NX module, a consumer-grade system-on-module normally sold for robotics, drones, and edge AI research rather than military hardware. Nvidia confirmed the Orin NX isn\u2019t officially sold in Russia or export-controlled, and said it can\u2019t track products after resale but will act on confirmed export-control violations.',
            body_zh='烏克蘭軍事情報單位表示，俄羅斯代號「Monochrome（單色）」的 S-71 巡弋飛彈——這款飛彈具備較低的可偵測性與自主標定目標的能力——使用了 Nvidia 的 Jetson Orin NX 模組。這是一款消費級的系統模組（system-on-module），原本主要銷售對象是機器人、無人機與邊緣 AI 研究領域，而不是軍事硬體。Nvidia 證實，Orin NX 並未正式在俄羅斯銷售，也不屬於出口管制項目；該公司表示，產品一旦轉售出去便無法追蹤流向，但只要確認發生違反出口管制的情況，就會採取行動。',
            vocab=[
                ('cruise missile', '軍事專有名詞「巡弋飛彈」，cruise 在此指「（以固定速度）巡航飛行」。'),
                ('observability (n.)', '「可觀測性、可被偵測到的程度」，字根源自 observe（觀察），在軍事語境中指「被敵方偵測到的難易程度」。'),
                ('system-on-module (SoM)', '電子工程專有名詞「系統模組」，指將處理器、記憶體等核心元件整合在單一模組上的設計。'),
                ('edge AI', 'AI／硬體領域專有名詞「邊緣 AI」，指在裝置端（而非雲端伺服器）直接執行 AI 運算。'),
                ('export-controlled (adj.)', '「受出口管制的」，export control 指政府對特定技術／產品出口設下的法律限制。'),
                ('act on X', '片語，「針對 X 採取行動」，常見於描述組織對特定情況做出回應處置。'),
            ],
        ),
        dict(
            title_en='CoreWeave’s A100 Contract Through 2029 Undercuts Fears That Nvidia GPUs Age Out Fast',
            title_zh='CoreWeave 簽下 A100 合約到 2029 年，緩解「GPU 快速過時」的疑慮',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='The bear case on AI infrastructure spending has always been simple: with Nvidia shipping a new architecture roughly every year, GPUs should lose economic value within two or three years, undermining the long-dated debt financing the whole buildout leans on. CoreWeave’s Q2 earnings call complicated that story, disclosing a renewed contract for Nvidia’s 2020-era A100 GPUs running all the way through 2029, at pricing CEO Mike Intrator said matches ‘full freight’ from years ago.',
            body_zh='對「AI 基礎建設支出」抱持看空（bear case）立場的論點，一直以來都很簡單：既然 Nvidia 幾乎每年都會推出新一代架構，GPU 的經濟價值，理論上應該會在兩到三年內迅速折舊消失，進而動搖整個建設案賴以支撐的長天期債務融資基礎。但 CoreWeave 在第二季財報電話會議上揭露的消息，讓這套說法變得更複雜——該公司公布，已與客戶續簽一份合約，將 Nvidia 那批 2020 年代的 A100 GPU，一路使用到 2029 年，而執行長 Mike Intrator 表示，這份合約的定價，與多年前的「全額原價（full freight）」相當。',
            vocab=[
                ('bear case', '金融領域專有名詞「看空論點」，與 bull case（看多論點）相對。'),
                ('undermine (v.)', '「削弱、動搖（根基）」，常見於描述某因素逐漸侵蝕原本穩固的基礎。'),
                ('complicate (v.)', '「使複雜化」，常見於描述新資訊讓原本簡單的敘事變得不再單純。'),
            ],
        ),
        dict(
            title_en='Semiconductor Equipment Shifts to Build-to-Print Manufacturing',
            title_zh='半導體設備業轉向「按圖代工」生產模式',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Semiconductor equipment OEMs are increasingly adopting build-to-print contract manufacturing to scale production and meet soaring global chip demand without heavy capital expenditures. As expanding AI fabs drive severe equipment backlogs, toolmakers partner with electronics contract manufacturers to produce sub-assemblies from existing engineering drawings. This distributed model provides immediate access to cleanrooms and precision machining, cutting equipment lead times, preserving OEM capital, and improving supply chain resilience across regional fab expansions.',
            body_zh='半導體設備原廠（OEM），正日益採用「按圖代工（build-to-print）」的委外製造模式，藉此擴大產能，以因應全球晶片需求的暴增，同時避免投入龐大的資本支出。隨著 AI 晶圓廠（fab）不斷擴張，導致設備訂單嚴重積壓（backlog），設備商紛紛與電子委外代工廠合作，依據既有的工程圖紙來生產次組件（sub-assembly）。這種「分散式」生產模式，能讓廠商立即取得無塵室與精密加工的產能，不僅縮短了設備交期（lead time）、保留了原廠的資本，也提升了整個供應鏈，在各地晶圓廠擴建過程中的韌性。',
            vocab=[
                ('OEM', '製造業專有縮寫「原廠委託製造商」，泛指負責設計、掌握品牌的原始設備廠商。'),
                ('backlog (n.)', '「（訂單/工作的）積壓」，常見於描述需求超過產能所導致的排隊等候狀況。'),
                ('lead time', '供應鏈管理專有名詞「前置時間、交期」，指從下單到實際交貨所需的時間。'),
            ],
        ),
        dict(
            title_en='OCP Launches Open Silicon Photonics Initiative',
            title_zh='OCP 啟動「開放矽光子」倡議',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='A 19-company industry coalition led by Lightmatter has formally launched the Open Silicon Photonics for AI Systems initiative as an official Open Compute Project workstream. Alongside a 300-page foundational architecture white paper, the initiative aims to establish an open, vendor-neutral blueprint for integrating co-packaged optics into datacenter infrastructure. Targeting OCP Modular Hardware System and Open Rack v3 standards, the framework scales clusters from 72 to over 1,024 nodes while overcoming copper reach and bandwidth bottlenecks.',
            body_zh='由 Lightmatter 領軍、共 19 家公司組成的產業聯盟，已正式啟動「AI 系統開放矽光子（Open Silicon Photonics）」倡議，將其納入 Open Compute Project（OCP）的正式工作專案之一。除了發布一份長達 300 頁的基礎架構白皮書之外，這項倡議的目標，是建立一套開放、不偏袒特定廠商（vendor-neutral）的藍圖，用來將「共封裝光學（co-packaged optics）」整合進資料中心基礎設施之中。這套框架瞄準 OCP 模組化硬體系統與 Open Rack v3 標準，能將叢集規模，從 72 個節點擴展到超過 1,024 個節點，同時克服銅纜傳輸距離與頻寬的瓶頸限制。',
            vocab=[
                ('coalition (n.)', '「聯盟、聯合陣線」，常見於描述多個組織為共同目標而合作的團體。'),
                ('vendor-neutral (adj.)', '複合形容詞「不偏袒特定廠商的」，常見於描述開放標準的設計理念。'),
                ('bottleneck (n.)', '前面主題也出現過的高頻比喻詞「瓶頸」，此處指硬體層面的傳輸限制。'),
            ],
        ),
        dict(
            title_en='The 1-Megawatt Rack Debate',
            title_zh='「百萬瓦機櫃」的論戰',
            meta='原文閱讀時間：約 5 分鐘',
            body_en='The semiconductor and datacenter industries are actively debating the necessity of 1-megawatt server racks driven by continuous, power-intensive AI workloads. While hyperscalers explore ±400V DC power distribution, advanced liquid cooling, and 3D-IC packaging to support ultra-dense compute, critics argue this scaling vector is unsustainable. Instead of cramming accelerators into single dense enclosures to preserve short copper reach, alternative approaches advocate scaling horizontally across racks using optical interconnects and specialized silicon.',
            body_zh='半導體與資料中心產業，正積極辯論著：在持續、高耗電的 AI 工作負載驅動下，「1 百萬瓦（megawatt）伺服器機櫃」究竟是不是必要的。雖然超大規模雲端業者（hyperscaler），正積極探索正負 400V 直流配電、先進液冷技術，以及 3D-IC 封裝技術，來支撐超高密度的運算需求，但批評者主張，這種「擴展路徑」是不可持續的。有別於「把加速器全都塞進單一高密度機殼中，以維持較短的銅纜傳輸距離」的做法，另一派做法則主張，應該改用光學互連與專用晶片，讓運算能力在多個機櫃之間「水平擴展」。',
            vocab=[
                ('power-intensive (adj.)', '複合形容詞「高耗電的」，intensive 表示「密集的、高強度的」。'),
                ('hyperscaler (n.)', '雲端產業專有名詞「超大規模雲端業者」，泛指 AWS、Google、Microsoft 等公司。'),
                ('cram X into Y', '「把 X 硬塞進 Y 裡」，常帶有「空間不足、勉強塞入」的語氣。'),
            ],
        ),
        dict(
            title_en='Intel May Refresh Raptor Lake a Third Time as DDR5 Prices Push Buyers Back to DDR4',
            title_zh='DDR5 價格飆升，Intel 可能推出第三次 Raptor Lake 改款',
            meta='原文閱讀時間：約 3 分鐘',
            body_en='Intel VP Robert Hallock confirmed the company plans to keep Raptor Lake CPUs in production and stabilize supply of its LGA 1700-compatible chips ‘for years to come,’ following a spike in demand for the four-year-old Alder Lake and Raptor Lake lineups. It’s a direct response to the DDR5 price crunch: Raptor Lake supports both DDR4 and DDR5, letting buyers upgrade without paying today’s inflated DDR5 prices, and rumors point to a possible third refresh, tentatively ‘Raptor Lake Next,’ arriving alongside the DDR5-exclusive Nova Lake in early 2027.',
            body_zh='Intel 副總裁 Robert Hallock 證實，該公司計畫繼續生產 Raptor Lake 系列處理器，並且「在未來好幾年內」穩定供應與 LGA 1700 腳位相容的晶片——這項決定，是在已經推出四年的 Alder Lake 與 Raptor Lake 系列，需求量出現激增之後所做出的回應。這也是對「DDR5 記憶體價格危機」的直接反制：Raptor Lake 同時支援 DDR4 與 DDR5，讓消費者能在不需支付如今高漲的 DDR5 價格的情況下，依然完成升級；傳言更指出，Intel 可能會推出第三次改款，暫定命名為「Raptor Lake Next」，預計於 2027 年初，與僅支援 DDR5 的 Nova Lake 一同推出。',
            vocab=[
                ('a spike in X', '「X 出現激增、急遽上升」，spike 原指「尖峰」，常用於描述數據短時間內暴增。'),
                ('price crunch', '「價格危機、價格緊縮」，crunch 在此引申為「（供需失衡導致的）緊張局面」。'),
                ('tentatively (adv.)', '「暫定地、試探性地」，常用於描述尚未正式確認的命名或計畫。'),
            ],
        ),
        dict(
            title_en='CPO Test Won’t Scale Without Standardization',
            title_zh='沒有標準化，共封裝光學測試就無法規模化',
            meta='原文閱讀時間：約 4 分鐘',
            body_en='Semiconductor Engineering reports that Co-Packaged Optics cannot scale to profitable high-volume manufacturing without industry-wide testing standardization. As datacenters adopt optical interconnects for AI workloads, test cells face severe bottlenecks from proprietary fiber connectors, non-standardized laser alignment schemes, and fragmented data formats.',
            body_zh='根據 Semiconductor Engineering 的報導，「共封裝光學（Co-Packaged Optics）」若缺乏「全產業統一的測試標準」，將無法擴展到具獲利能力的大量生產規模。隨著資料中心紛紛為 AI 工作負載採用光學互連技術，測試站（test cell）正面臨著嚴重的瓶頸——原因來自於各家專屬的光纖接頭規格、未經標準化的雷射對準方案，以及分散不一的資料格式。',
            vocab=[
                ('scale to X', '「擴展到 X（的規模）」，scale 當動詞「（依比例）擴展」。'),
                ('proprietary (adj.)', '「專屬的、私有的」，與 open/standard 相對，常見於描述廠商自訂而非公開通用的規格。'),
                ('fragmented (adj.)', '「碎片化的、分散不一致的」，常見於描述缺乏統一標準的狀態。'),
            ],
        ),
    ]),
]

# ============================================================
# SUMMARY BULLETS (per topic, condensed)
# ============================================================

SUMMARY = [
    ('科技綜合', [
        'Anthropic 年化營收在七月底衝上 <b>650 億美元</b>，同時為外界預期的重磅 IPO 積極備戰。',
        '特斯拉計畫本月稍晚在德州奧斯汀正式發表 <b>Cybercab</b> 無人計程車。',
    ]),
    ('軟體開發', [
        '<b>Cursor</b> 推出程式碼代管平台 <b>Origin</b>，正面挑戰 GitHub。',
        'Wiz 的自動化「Red Agent」在漏洞出現僅 5 天內就找出並利用了 Snowflake 的 GitHub Actions 漏洞，凸顯 AI 輔助開發帶來的資安風險。',
    ]),
    ('人工智慧', [
        '<b>Groq</b> 在 Nvidia 授權其技術並挖角團隊後，以 35 億美元估值募得 3.5 億美元。',
        '「測試時訓練」讓模型能邊用邊學，用運算成本換取長上下文的個人化效能。',
    ]),
    ('資訊安全', [
        '<b>Beacon CRM</b> 因一組暴露在公開 JS 中的 AWS 金鑰，導致整個資料庫遭竊。',
        'OWASP 發布 <b>CI/CD 十大資安風險</b>清單，涵蓋依賴鏈濫用、流水線下毒等關鍵風險。',
    ]),
    ('產品管理', [
        '調查顯示多數科技工作者其實更想做 <b>IC（個人貢獻者）</b>而非管理職，只是薪酬與影響力讓人卻步。',
        'AI 基礎建設榮景仰賴的融資風險正在升高，<b>Nvidia</b> 的策略成敗取決於 AI 營收能否跟上。',
    ]),
    ('DevOps', [
        '數據顯示 AI 輔助開發讓「產出」變多，但不一定讓「出貨速度」與「軟體品質」變好。',
        '<b>Cloudflare</b> 為 Zero Trust 平台新增偵測與管控 <b>MCP</b> 流量的工具。',
    ]),
    ('新創與創業', [
        'OpenRouter 上有 84% 的 token 用量並非使用 SOTA 模型，顯示市場正在用「價格」而非「效能」做選型。',
        '灰色市場正在轉售 OpenAI／Anthropic 的折扣額度，形成「代幣掮客」新現象。',
    ]),
    ('設計', [
        '「氛圍編程」新創 <b>Lovable</b> 再募 4 億美元，估值來到 <b>133 億美元</b>。',
        'AI agent 各自打造設定頁面的實驗顯示：沒寫清楚的「結構規則」，才是設計不一致的真正根源。',
    ]),
    ('行銷', [
        '「手作感」品牌風潮興起，作為品牌在 AI 飽和市場中傳達「人味」的方式。',
        'Claude 的文字浮水印藏在用字選擇的統計模式中，難以被移除或偽裝。',
    ]),
    ('加密貨幣', [
        'Stripe 收購 OpenRouter 被視為押注「Agent 時代 Router 聚合層」的關鍵一步，可能衝擊 Google 搜尋的中介地位。',
        'Circle 提出「開放 Agent 經濟」願景，讓 AI agent 能以穩定幣互相付費、彼此協作。',
    ]),
    ('金融科技', [
        'Stripe 據報以逾 <b>70 億美元</b>收購 AI 模型閘道 <b>OpenRouter</b>。',
        '<b>Nvidia</b> 與六大資本機構簽署合作備忘錄，打算部署逾 5,000 億美元資金投入 AI 基礎建設，被稱為「全球最大金融科技公司」。',
    ]),
    ('IT 產業', [
        '<b>GitHub</b> 週一發生大規模中斷，影響儲存庫、API、Actions 與企業身分驗證等服務。',
        'SaaStr 因內部 AI agent 接手了最後的使用情境，用了七年後取消 <b>Notion</b> 訂閱，形成新型態的 SaaS 流失現象。',
    ]),
    ('資料工程', [
        '<b>Tailscale</b> 花六個月追出一個潛藏 16 年的 SQLite 競爭條件臭蟲。',
        'CDC（異動資料擷取）能讓寫入可重試、有順序，但無法單獨解決「雙重寫入」的資料一致性問題。',
    ]),
    ('硬體', [
        '<b>Nvidia</b> 揭露持有 SpaceX <b>210 億美元</b>股權，同時也是其資料中心硬體供應商。',
        '烏克蘭情報單位發現俄羅斯巡弋飛彈使用 <b>Nvidia Jetson</b> 消費級晶片，凸顯民用 AI 硬體的軍事濫用風險。',
    ]),
]

def build():
    doc = SimpleDocTemplate(
        r'C:\Users\User\Desktop\agent\tldr\2026-08-19_星期三.pdf',
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm,
        title='TLDR 全主題沉浸式翻譯與重點整理', author='Claude'
    )
    story = []

    # Cover page
    story.append(Spacer(1, 60))
    story.append(Paragraph('TLDR 全主題沉浸式翻譯', ParagraphStyle(
        'CoverTitle', fontName=ZH_BOLD, fontSize=28, leading=36, textColor=NAVY,
        alignment=TA_CENTER, spaceAfter=10)))
    story.append(Paragraph('＆ 會議快讀重點整理', ParagraphStyle(
        'CoverTitle2', fontName=ZH_BOLD, fontSize=20, leading=28, textColor=ACCENT,
        alignment=TA_CENTER, spaceAfter=30)))
    story.append(Paragraph(zsp('產出日期：2026-08-19（星期三）'), ParagraphStyle(
        'CoverSub', fontName=ZH, fontSize=12, leading=18, textColor=GRAY, alignment=TA_CENTER, spaceAfter=6)))
    story.append(Paragraph(zsp('涵蓋範圍：TLDR 14 份子報全主題（Tech／Dev／AI／InfoSec／Product／DevOps／Founders／Design／Marketing／Crypto／Fintech／IT／Data／Hardware），收錄每份子報全部主打文章（不含 Quick Links），並自動過濾與前一日內容重複的報導'), ParagraphStyle(
        'CoverSub2', fontName=ZH, fontSize=10.5, leading=17, textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph(zsp('每篇文章來源日期以各子報實際最新一期為準（2026-08-17 或 2026-08-18）'), ParagraphStyle(
        'CoverSub3', fontName=ZH, fontSize=9.5, leading=15, textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)))
    _total_articles = sum(len(t['articles']) for t in TOPICS)
    story.append(Paragraph(zsp(f'共收錄 {_total_articles} 篇文章'), ParagraphStyle(
        'CoverSub3b', fontName=ZH_BOLD, fontSize=10.5, leading=16, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Spacer(1, 20))
    story.append(Paragraph(zsp('使用情境：軟體工程師快速會前吸收，內容含逐段中英對照翻譯＋單字文法筆記＋重點整理'), ParagraphStyle(
        'CoverSub4', fontName=ZH, fontSize=10, leading=16, textColor=GRAY, alignment=TA_CENTER)))

    # Topic pages
    for topic in TOPICS:
        story.append(PageBreak())
        story.extend(topic_header(topic['name_zh'], topic['name_en'], f"資料來源日期：{topic['date']}"))
        for i, art in enumerate(topic['articles'], start=1):
            story.extend(article_block(i, art))

    # Summary section
    story.append(PageBreak())
    story.append(Paragraph('會議快讀重點整理', styles['DocTitle']))
    story.append(Paragraph(zsp('30 秒掃描版：依 14 大主題分類，供開會前快速吸收'), styles['DocSub']))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=1.2, color=NAVY))
    story.append(Spacer(1, 8))

    def bullets(items):
        return ListFlowable(
            [ListItem(Paragraph(zsp(t), styles['SummaryBullet']), leftIndent=9, bulletColor=ACCENT) for t in items],
            bulletType='bullet', start='\u2022', leftIndent=12, bulletFontSize=8,
        )

    for head, items in SUMMARY:
        story.append(Paragraph(head, styles['SummaryTopicHead']))
        story.append(bullets(items))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width='100%', thickness=0.6, color=LINE))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        zsp('資料來源：tldr.tech（14 份子報，各自取截至產出時最新一期，2026-08-17 或 2026-08-18 版）。翻譯與整理由 Claude 協助完成，僅供內部參考，正式引用請核對原文。'),
        styles['Footer']))

    doc.build(story)
    print('PDF generated.')

if __name__ == '__main__':
    build()
