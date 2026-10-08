# -*- coding: utf-8 -*-
# 内容排版风格数据：转写自开源项目 html-anything（github.com/clockless-org/html-anything，MIT）
# 18 个「内容排版风格」——与 styles.csv 的视觉风格正交：它们决定页面如何组织与讲述内容。
# 样张演示主题统一为「2026 阅读档案」，仅用于展示排版，不进提示词。

CONTENT_OUT = 'content-demos'

CONTENT_STYLES = [
dict(id='timeline-story', zh='时间线叙事', en='Timeline Story',
    use='个人历史与档案：购买记录、浏览/搜索历史、听歌观影、健康趋势、项目日记、年度回顾',
    system='滚动驱动的记忆系统——像走过一段人生，不是读仪表盘',
    scaffold=['开场时间透镜：覆盖时段、总量、一个作故事钩子的记忆模式',
              '时间主轴：年/月/周是主导航，选中时段过滤全页模块',
              '章节面板：每个时段一个紧凑场景（最高频项/重复习惯/峰值/沉寂期）',
              '节奏条：热力图或堆叠条展示节奏，不做运营图表',
              '记忆抽屉：可搜索的条目浏览器，按章节过滤'],
    vocab='.story-shell .time-lens .timeline-spine .chapter-panel .period-scrubber .rhythm-strip .memory-drawer',
    motion='时间主轴一次描边生长',
    anti='不做运营仪表盘；时间是主轴而不是下拉筛选器',
    t=dict(bg='#F7F3EA', panel='#FFFFFF', ink='#2C2A26', muted='#8A8272',
           accent='#B4552D', line='#D8D2C4', fh='Noto Serif SC', fb='Noto Serif SC', radius='10px'),
    hero='timeline'),
dict(id='teaching', zh='教学工作室', en='Teaching Studio',
    use='教程、课程页、交互讲解、"教我 X"、任何需要引导式学习序列的页面',
    system='引导式学习装置：看着学、改着学、测着学、走向下一个概念',
    scaffold=['左侧课程栏：标题、目标、模式控制、对象列表',
              '中央模型舞台：选中对象或模式即切换的主教学面',
              '右侧检查器：所选对象的事实与"为什么重要"',
              '步骤进度轨：贯穿学习序列的骨架',
              '自测关卡：小步检查而非期末考试'],
    vocab='.lesson-rail .object-stage .inspector .step-track .check-gate',
    motion='模型舞台一次旋转入场',
    anti='不像论文、博客或仪表盘；不是滚动长文而是分段工作室',
    t=dict(bg='#FBF9F4', panel='#FFFFFF', ink='#1F2429', muted='#6E7568',
           accent='#2F6F4F', line='#DCE2D8', fh='Zilla Slab', fb='IBM Plex Sans', radius='12px'),
    hero='teaching'),
dict(id='living-essay', zh='菌丝长文', en='Living Essay',
    use='高亮摘录、个人随笔、思想笔记、文章合集、阅读清单——该被"读"而不是被"操作"的内容',
    system='菌丝发酵式慢读环境：诗意阅读工具，不是产品仪表盘',
    scaffold=['纸面手稿：单一中央阅读栏、宽行距、准正文、极少元数据',
              '竖排问题胶囊：左缘一枚竖排文字的胶囊，边框缓慢呼吸',
              '菌丝层：内联 SVG 细线在胶囊与"孢子词"之间缓慢生长又淡出',
              '孢子词：正文内被连接/选中时下划线的术语',
              '安静附录：阅读节奏、书架、主题等以细线条列表收尾，不做卡片'],
    vocab='.layout .mycelium-layer .question-zone .capsule-container .spore',
    motion='菌丝 SVG 一次生长',
    anti='不做产品化卡片墙；装饰必须服务于词与概念的连接',
    t=dict(bg='#F4F1E8', panel='#FBF9F2', ink='#33322D', muted='#8C8878',
           accent='#6B7F3E', line='#DDD8C8', fh='Noto Serif SC', fb='Noto Serif SC', radius='6px'),
    hero='essay'),
dict(id='dashboard', zh='运营控制台', en='Ops Dashboard',
    use='CSV、表格、财务/后台数据、日志、工单、日历导出等结构化数据集',
    system='为反复扫视、筛选、决策而生的运营台',
    scaffold=['命令栏：标题、时段/来源、搜索、筛选、导出与激活筛选片汇成一行',
              'KPI 栏：等宽数字的密集指标格，带环比与上下文',
              '主工作面：趋势/热力/漏斗/队列，大到能快速对比',
              '异常队列：待处理、重复、失败的任务行',
              '数据网格：可搜索排序的表格或虚拟行'],
    vocab='.ops-shell .command-bar .kpi-rail .work-surface .flag-queue .data-grid',
    motion='主图表条形一次生长',
    anti='不做 storytelling 大卡片；紧凑行、标签页、分段控件优先',
    t=dict(bg='#F2F4F7', panel='#FFFFFF', ink='#1B2733', muted='#69788C',
           accent='#0F62FE', line='#D5DBE3', fh='IBM Plex Sans', fb='IBM Plex Sans', radius='8px'),
    hero='dashboard'),
dict(id='soft-saas', zh='轻软控制台', en='Soft SaaS',
    use='客服邮箱、邮件营销、客户成功队列、轻量产品分析——要"好操作"但别成重后台',
    system='淡灰画布上的悬浮面板：精确、友好、低摩擦、安静地活着',
    scaffold=['淡灰画布：大留白，无营销 hero',
              '白色圆角面板：细边框、软阴影、几乎不用饱和底色',
              '不对称拼贴：左身份栏、中央大图表面、右状态栏、下活动条',
              '小蓝胶囊标签与状态圆点，替代大声的徽章',
              '迷你指标：等宽百分比、迷你走势、微热力图'],
    vocab='.saas-shell .float-panel .metric-card .status-dot .activity-strip',
    motion='中央图表一次揭示',
    anti='禁止剧场式滚动与装饰动效；hover 抬升、联动选中这类产品级动效',
    t=dict(bg='#F5F7FA', panel='#FFFFFF', ink='#2A2F38', muted='#7A8494',
           accent='#4F6BFF', line='#E3E8F0', fh='Manrope', fb='Inter', radius='16px'),
    hero='saas'),
dict(id='kinetic-scoreboard', zh='动能计分板', en='Kinetic Scoreboard',
    use='多参与者流：群聊活跃度、销售、客服、作者、玩家——"谁做了多少、何时、效果如何"',
    system='实时竞标赛场：首屏像一块锦标赛转播屏，不是报表',
    scaffold=['锦标赛头：细条 ruled 的赛事标题、来源日期与实时榜单',
              '选手泳道：3-6 条全高泳道，各自有编号、名字、排名、超大分数',
              '动能体：活动化作运动的条/波/柱，动作必须有数据支撑',
              '遥测页脚：每条泳道的阶段/负载/配速标签',
              '证据坑：下方的回合分析、原始记录浏览器'],
    vocab='.scoreboard .lane .kinetic-body .telemetry .evidence-pit',
    motion='泳道分数一次滚动到位',
    anti='不是报表/仪表盘/文章；克制使用网格纸与黑 rule 线，数字是主角',
    t=dict(bg='#F5F2E8', panel='#FFFFFF', ink='#141414', muted='#6F6A5E',
           accent='#D7263D', line='#C9C4B4', fh='Archivo Black', fb='JetBrains Mono', radius='4px'),
    hero='scoreboard'),
dict(id='map-atlas', zh='地图图集', en='Map Atlas',
    use='收藏地点、GPX/KML 路线、旅行行程、照片地理数据、地点历史、房源清单',
    system='空间探索系统：首屏被一张地图/路线/散点锚定',
    scaffold=['图集舞台：离线 SVG/canvas 地图或示意地场，不引外部瓦片',
              '地点抽屉：选中点/簇/段的详情',
              '时空控件：时段刷、城市片、图层开关、类目筛选',
              '移动指标：距离/停留/频次作上下文，不做 KPI 墙',
              '路点浏览器：与舞台联动的可搜索列表'],
    vocab='.map-shell .atlas-stage .place-drawer .city-chip .period-scrubber .waypoint-browser',
    motion='航线一次描边',
    anti='地图是主角；列表与指标都是配角',
    t=dict(bg='#EEF1EA', panel='#FFFFFF', ink='#2B3230', muted='#75796F',
           accent='#2E6E4E', line='#D3D9CF', fh='Fraunces', fb='IBM Plex Sans', radius='10px'),
    hero='atlas'),
dict(id='global-travel', zh='环球旅册', en='Global Travel',
    use='个人旅行史、网约车导出、行程日志、机场足迹——首读应是优雅的全球移动版面',
    system='居中式旅行档案：优雅 dossier，不是地图应用',
    scaffold=['居中标题块：一个强标题、一句副题、紧凑选择器与主行动',
              '点阵世界地图：低对比点阵充满首屏，SVG/CSS 绘制',
              '暖色图钉与一个浮标卡：标注选中城市/路线',
              '数字跑道：4-6 个大计数器配细描边图标，数字即节奏',
              '折叠线以下的细节：时间线、花费、下钻都从属于地图舞台'],
    vocab='.travel-shell .world-field .pin .callout-card .metric-runway',
    motion='点阵地图一次浮现',
    anti='不做密集图集或运营面板；淡蓝绿画布、珊瑚主行动',
    t=dict(bg='#EAF2F0', panel='#FFFFFF', ink='#22333B', muted='#6E8483',
           accent='#FF6B4A', line='#CFE0DC', fh='Fraunces', fb='Inter', radius='8px'),
    hero='travel'),
dict(id='network-map', zh='关系图谱', en='Network Map',
    use='人、组织、发送者、社群、联系人、社付记录、邮件档案——关系比原始行更重要',
    system='关系图系统：揭示簇、桥、反复交易对手与模式',
    scaffold=['网络画布：首屏 SVG/canvas 节点-连线图或邻接矩阵',
              '实体检查器：选中人物/组织的上下文与关联记录',
              '聚类控件：按组织/发送者/主题/关系类型分组',
              '桥与枢纽卡：最强连接、陈旧关系、未回复线程',
              '关联记录浏览器：随选中节点/边过滤'],
    vocab='.network-shell .network-canvas .entity-inspector .cluster-controls .hub-card',
    motion='节点一次弹入',
    anti='不做行列表首页；节点/边/簇/桥是语言',
    t=dict(bg='#F4F5F7', panel='#FFFFFF', ink='#23272E', muted='#737B88',
           accent='#5B4FFF', line='#DCDFE6', fh='Manrope', fb='Inter', radius='12px'),
    hero='network'),
dict(id='document', zh='档案审阅', en='Document Review',
    use='文章、阅读清单、研究合集、PDF/DOCX、法律/医疗/政策等高风险长文档',
    system='阅读与审阅系统：有主张、有证据、可追溯的结构化文档',
    scaffold=['封面/刊头：标题、范围、来源、中立摘要或论点、必要警示',
              '读者栏：章节导航、阅读模式（速览/大纲/证据）、主题筛选',
              '正文纸：章节按备忘录排布；叙事调性用引文，正式调性用事实表',
              '证据摊开：摘录、来源标签、日期、当事方',
              '审查脚注：定义、警示、版本与变更记录'],
    vocab='.masthead .reader-rail .body-sheet .evidence-spread .caveat',
    motion='目录条一次滑入',
    anti='不是营销页；两种调性（叙事/正式）只换语气密度与色板，骨架不变',
    t=dict(bg='#FBFAF7', panel='#FFFFFF', ink='#26282B', muted='#7D7A72',
           accent='#7A4E2D', line='#E0DCD0', fh='Source Serif 4', fb='IBM Plex Sans', radius='6px'),
    hero='document'),
dict(id='kami-reading', zh='羊皮长读', en='Kami Reading',
    use='该被读、翻、打印、回访的长文：随笔、备忘、长文、信件、研究笔记',
    system='温暖的印刷页面搬进浏览器：克制的文档系统，不是应用 UI',
    scaffold=['羊皮画布：#f5f4ed 系暖底，永远不用纯白',
              '衬线封面：顶部小标签、大标题、短导语、一条墨线、紧凑元数据',
              '细目录条：封面下方一列章节',
              '章节如可打印页：眉标、题、导语、正文',
              '无粘性侧栏、无应用顶栏、无营销 hero'],
    vocab='.parchment .cover .contents-strip .chapter .folio',
    motion='墨线一次展开',
    anti='不要任何应用壳；像一册书',
    t=dict(bg='#F5F4ED', panel='#FAF9F5', ink='#3A3631', muted='#8C8677',
           accent='#8A5A2B', line='#E4E0D2', fh='Noto Serif SC', fb='Noto Serif SC', radius='2px'),
    hero='kami'),
dict(id='architectural-spread', zh='建筑式跨页', en='Architectural Spread',
    use='视觉主导的编辑页：长文、文化评论、概念笔记、设计宣言、物件档案',
    system='全屏分跨页：更像被设计过的杂志跨页而不是网站',
    scaffold=['左视觉舱：大地色半屏、单个大视觉物件垂直居中、左下小插图',
              '右编辑栏：奶油色半屏、章节标签、大标题、衬线斜体强调词',
              '角落锚点：Close (X)/( More Visible Area )/Next Chapter (+) 的极小文字导航',
              '页码圆点：内容栏下中部的章节圆点',
              '安静动效：淡入/滑动、物件微漂移，无喧闹转场'],
    vocab='.spread .visual-bay .editorial-panel .corner-anchor .dot-nav',
    motion='左视觉物件一次淡入漂移',
    anti='不做滚动长文、仪表盘、卡片网格或营销 hero',
    t=dict(bg='#C9BFB0', panel='#F6F1E7', ink='#26221C', muted='#7C7264',
           accent='#A05000', line='#B4A896', fh='Playfair Display', fb='Noto Serif SC', radius='0px'),
    hero='spread'),
dict(id='digital-eguide', zh='电子指南册', en='Digital E-Guide',
    use='电子书/指南/lead magnet/创作者手册/课程预览——把长报告变成可分享的精美指南预览',
    system='暖桌上的两页 PDF 预览：纸页、衬线大字、目录、练习条',
    scaffold=['指南桌面：暖色桌面居中放两页纸，宽屏并排窄屏叠放',
              '封面页：等宽小眉标、超大衬线标题、斜体强调词、署名、3 格统计、What\'s inside、双栏点线目录、页脚 folio',
              '内页跨页：章节眉标、编辑体标题、deck 段、双栏正文或步骤列表、置顶引文、行动条',
              '工具层：搜索/复制/章节控件做成极小的 mono TOOLS 标签页'],
    vocab='.eguide-desk .guide-page .cover-page .inside-spread .exercise-strip',
    motion='书页一次翻开',
    anti='不是仪表盘、应用壳或普通文档页',
    t=dict(bg='#E9E2D6', panel='#FBF8F1', ink='#2E2A22', muted='#8A8172',
           accent='#B0483B', line='#D8CFBE', fh='Playfair Display', fb='Noto Serif SC', radius='6px'),
    hero='eguide'),
dict(id='editorial-carousel', zh='编辑轮播', en='Editorial Carousel',
    use='品牌策略文、创始人信、趋势解读、宣言、高管摘要、可分享的观点小卡组',
    system='高级社交杂志轮播：轮播本身即是页面骨架',
    scaffold=['轮播舞台：横向滚动 + scroll-snap，暖灰桌面背景',
              '固定画幅幻灯片：4-8 张 480×600 左右的编辑卡',
              '编号原则：超大数字 + 一句话原则',
              '版面语言：folio 页码、卷标、星芒贴纸、灰阶编辑图',
              '无 hero、无应用顶栏、无解释性壳'],
    vocab='.carousel-stage .slide .folio .volume-badge .starburst',
    motion='首帧幻灯一次滑入',
    anti='不是落地页/文章/应用；每张卡画幅稳定、字体混排（衬线/手写/等宽）',
    t=dict(bg='#DDD8CE', panel='#F4EFE6', ink='#17150F', muted='#797262',
           accent='#C0392B', line='#C9C1B2', fh='Playfair Display', fb='Noto Serif SC', radius='8px'),
    hero='carousel'),
dict(id='terminal-cli', zh='终端命令行', en='Terminal CLI',
    use='用户明说终端/CLI/shell/主机/黑客/服务器控制台；CI 日志、堆栈、runbook、技术时间线',
    system='磷光屏上的 tmux/vim 分屏：功能至上、仅深色、全等宽、围绕命令与原始证据',
    scaffold=['Shell 头：operator@host:~$ 命令行 + 闪烁光标 + 运行元数据',
              '状态轨：终端原生记号 [OK] [ERR] 与 ASCII 条 [||||..] 62%',
              '面板网格：1px 绿框 + 标题条 +--- RUN SUMMARY ---+ 的严格窗格',
              '命令控件：提示符式输入与 [ COPY SUMMARY ] 括号按钮',
              '原始证据：行号、可折叠、可搜索的源材料'],
    vocab='.shell-header .status-rail .pane-grid .command-control .raw-log',
    motion='首行命令一次打字（光标常闪不算动效）',
    anti='不是赛博朋克装饰：无 Matrix 雨、无霓虹紫渐变、无圆角 SaaS 卡、无玻璃拟态',
    t=dict(bg='#0B0F0C', panel='#101610', ink='#C8E6C9', muted='#5F7A62',
           accent='#37D67A', line='#2A3A2E', fh='JetBrains Mono', fb='JetBrains Mono', radius='2px'),
    hero='terminal'),
dict(id='developer', zh='取证工作台', en='Developer Workbench',
    use='GitHub 仓库、diff、PR 补丁、CI/构建/测试日志、堆栈跟踪等技术工件',
    system='终端取证工作台：像 tmux 分屏的事故控制台，可审计、扫读快',
    scaffold=['命令/发现栏：顶部 prompt 写状态、疑似原因、涉改文件、置信度标签',
              '终端面板格：审阅清单/风险热点/失败测试/堆栈帧/可复制交接',
              '风险清单：按严重度排序的发现，前缀 [ERR][WARN][OK][HYP]',
              'diff/日志/搜索窗：并排可扫读',
              '可复制交接：一段能贴走的结论块'],
    vocab='.finding-bar .pane .risk-checklist .stack-frame .handoff',
    motion='diff 行一次高亮扫过',
    anti='不做通用 SaaS 审阅页；一切以终端设计语言表达',
    t=dict(bg='#101418', panel='#161C22', ink='#D7DEE8', muted='#71818F',
           accent='#4FC3F7', line='#2A333D', fh='JetBrains Mono', fb='JetBrains Mono', radius='4px'),
    hero='workbench'),
dict(id='default', zh='洞察简报', en='Insight Brief',
    use='需求不明时的默认形态：仍要有设计感，不做文档倾倒',
    system='面向模糊输入的紧凑简报系统：不是仪表盘也不是文章',
    scaffold=['答案头：一个直给的标题、一句有用的话、2-4 枚"关键点"片',
              '主洞察面板：唯一最有用的一张图/对比/时间线/摘要面',
              '证据堆：3-5 节按有用度排序，各带主张与支撑行',
              '局部下钻：解读之后的搜索/筛选/浏览'],
    vocab='.brief-header .answer-strip .primary-insight .evidence-stack .useful-chip',
    motion='主面板一次轻抬升入场',
    anti='少用卡片；一个好面板 + 分组证据行优先',
    t=dict(bg='#FAFAF8', panel='#FFFFFF', ink='#202124', muted='#787D85',
           accent='#3452FF', line='#E4E5E8', fh='Inter', fb='Inter', radius='12px'),
    hero='brief'),
dict(id='love-romance-3d', zh='恋爱纪念 3D', en='Keepsake 3D',
    use='情侣聊天导出、情人节年度回顾、浪漫消息汇总——软 3D 纪念品质感',
    system='关系节奏的纪念品界面：圆润形体、透明高光、粉红渐变、小金饰',
    scaffold=['3D 纪念品封面：关系主题句 + 图标舞台 + 最安全的聚合统计',
              '图标舞台指标：带高光与软影的立体小方块承载指标',
              '消息脉冲板：圆糖果格热力图，不做企业图表',
              '软对比泳道：A/B 双人经均衡泳道、共同词、回应节奏',
              '隐私证据抽屉：证据匿名化且极小，不做原始聊天回放器'],
    vocab='.keepsake-cover .icon-stage .pulse-board .compare-lane .privacy-drawer',
    motion='漂浮物件一次入场',
    anti='不做中性报告页；也不变成原始聊天记录浏览器',
    t=dict(bg='#FDF0F3', panel='#FFFFFF', ink='#3A2530', muted='#9C7A87',
           accent='#E85D8A', line='#F2DCE3', fh='Quicksand', fb='Noto Sans SC', radius='20px'),
    hero='keepsake'),
]

# ---------- 样张主视觉块（每风格一段静态示意，token 由 CSS 变量驱动） ----------

def hero_html(s):
    t = s['t']
    v = dict(bg=t['bg'], panel=t['panel'], ink=t['ink'], muted=t['muted'],
             accent=t['accent'], line=t['line'], radius=t['radius'])
    return _HEROES[s['hero']](v)

def _timeline(v):
    return f'''<div class="hx" style="--a:{v['accent']};--l:{v['line']}">
  <div class="tl">
    <div class="tl-node"><i></i><div class="tl-card"><b>3 月 · 峰值月</b><span>读完 6 本，最长连胜 11 天</span></div></div>
    <div class="tl-node"><i></i><div class="tl-card"><b>7 月 · 沉寂期</b><span>只补完了 1 本随笔</span></div></div>
    <div class="tl-node"><i></i><div class="tl-card"><b>11 月 · 回归</b><span>科幻月：4 本长篇连读</span></div></div>
  </div></div>'''

def _teaching(v):
    return f'''<div class="hx grid3" style="--l:{v['line']}">
  <div class="p mini"><b>课程栏</b><span>目标 · 模式</span><span>对象 01/02/03</span></div>
  <div class="p stage"><b>模型舞台</b><svg viewBox="0 0 120 60" aria-hidden="true"><circle cx="60" cy="30" r="22" fill="none" stroke="{v['accent']}" stroke-width="3"/><circle cx="60" cy="30" r="4" fill="{v['accent']}"/></svg></div>
  <div class="p mini"><b>检查器</b><span>事实 · 为什么重要</span></div>
</div>'''

def _essay(v):
    return f'''<div class="hx essayh" style="--a:{v['accent']}">
  <div class="capsule">何为慢读</div>
  <p>阅读不是采集，而是让概念在<span class="spore">缓慢发酵</span>中彼此连接，像菌丝穿过一页页<span class="spore">纸的季节</span>。</p>
</div>'''

def _dashboard(v):
    return f'''<div class="hx" style="--a:{v['accent']};--l:{v['line']}">
  <div class="kpis"><div class="kpi"><b>128</b><span>本年读完 · +12%</span></div><div class="kpi"><b>42</b><span>高亮条数</span></div><div class="kpi"><b>11</b><span>最长连胜（天）</span></div></div>
  <div class="bars"><i style="height:40%"></i><i style="height:70%"></i><i style="height:55%"></i><i style="height:95%"></i><i style="height:60%"></i><i style="height:80%"></i></div>
</div>'''

def _saas(v):
    return f'''<div class="hx saash" style="--a:{v['accent']};--l:{v['line']}">
  <div class="p"><span class="dot"></span>收件队列 <b>37</b></div>
  <div class="p big"><span>打开率走势</span><svg viewBox="0 0 200 48" aria-hidden="true"><polyline points="0,38 40,30 80,33 120,18 160,22 200,8" fill="none" stroke="{v['accent']}" stroke-width="3"/></svg></div>
  <div class="p"><span class="dot ok"></span>送达 99.2%</div>
</div>'''

def _scoreboard(v):
    return f'''<div class="hx lanes" style="--a:{v['accent']};--l:{v['line']}">
  <div class="lane"><span class="rank">01</span><b>科幻</b><em>48 本</em></div>
  <div class="lane"><span class="rank">02</span><b>随笔</b><em>31 本</em></div>
  <div class="lane"><span class="rank">03</span><b>历史</b><em>22 本</em></div>
</div>'''

def _atlas(v):
    return f'''<div class="hx atlas" style="--a:{v['accent']}">
  <svg viewBox="0 0 320 120" aria-hidden="true">
    <path d="M20 90 C 90 20, 180 100, 300 30" fill="none" stroke="{v['accent']}" stroke-width="2.5" stroke-dasharray="1 6"/>
    <circle cx="20" cy="90" r="6" fill="{v['accent']}"/><circle cx="300" cy="30" r="6" fill="{v['accent']}"/>
    <circle cx="120" cy="58" r="3" fill="{v['accent']}" opacity=".45"/><circle cx="220" cy="70" r="3" fill="{v['accent']}" opacity=".45"/>
  </svg>
  <div class="drawer">京都 → 里斯本 · 停留 9 天 · 3 次回访</div>
</div>'''

def _travel(v):
    return f'''<div class="hx travel" style="--a:{v['accent']}">
  <div class="dots">{''.join('<i></i>' for _ in range(80))}</div>
  <div class="runway"><div><b>12</b><span>城市</span></div><div><b>38k</b><span>公里</span></div><div><b>5</b><span>洲</span></div></div>
</div>'''

def _network(v):
    return f'''<div class="hx net" style="--a:{v['accent']}">
  <svg viewBox="0 0 300 110" aria-hidden="true">
    <line x1="60" y1="55" x2="150" y2="25" stroke="{v['line']}" stroke-width="1.5"/><line x1="60" y1="55" x2="150" y2="85" stroke="{v['line']}" stroke-width="1.5"/><line x1="150" y1="25" x2="240" y2="55" stroke="{v['line']}" stroke-width="1.5"/><line x1="150" y1="85" x2="240" y2="55" stroke="{v['line']}" stroke-width="1.5"/><line x1="150" y1="25" x2="150" y2="85" stroke="{v['line']}" stroke-width="1.5"/>
    <circle cx="60" cy="55" r="9" fill="{v['accent']}"/><circle cx="150" cy="25" r="7" fill="{v['ink']}" opacity=".65"/><circle cx="150" cy="85" r="7" fill="{v['ink']}" opacity=".65"/><circle cx="240" cy="55" r="8" fill="{v['accent']}" opacity=".7"/>
  </svg>
</div>'''

def _document(v):
    return f'''<div class="hx doch" style="--a:{v['accent']};--l:{v['line']}">
  <div class="mast"><b>2026 阅读档案 · 审阅版</b><span>范围：全年 · 来源：Kindle 导出</span></div>
  <div class="rail">速览 | 大纲 | 证据</div>
  <p>主张：长篇胜过碎片——证据见第 3 节。</p>
</div>'''

def _kami(v):
    return f'''<div class="hx kamih" style="--a:{v['accent']}">
  <small>READINGS · 2026</small>
  <b>一年，三十八本书</b>
  <i class="inkline"></i>
  <span>目录：春读三卷 / 夏夜长谈 / 秋收与冬藏</span>
</div>'''

def _spread(v):
    return f'''<div class="hx spreadh">
  <div class="bay" style="background:{v['bg']}"><svg viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="30" fill="none" stroke="{v['accent']}" stroke-width="3"/><circle cx="40" cy="40" r="8" fill="{v['accent']}"/></svg></div>
  <div class="panel" style="background:{v['panel']}"><small>第二章 · 秩序</small><b>阅读的<br>建筑学</b><span>Next Chapter ( + )</span></div>
</div>'''

def _eguide(v):
    return f'''<div class="hx eguideh" style="--a:{v['accent']}">
  <div class="pg cover"><small>READING GUIDE</small><b>怎样读完<br>一本书</b><span>3 格统计 · 目录 · 作者</span></div>
  <div class="pg"><small>第 1 章</small><span>步骤列表 / 引文 / 练习条</span></div>
</div>'''

def _carousel(v):
    return f'''<div class="hx carouselh" style="--a:{v['accent']}">
  <div class="sl"><em>01</em><span>原则一：<br>读得慢，才读得深</span></div>
  <div class="sl"><em>02</em><span>原则二：<br>重读胜过泛读</span></div>
  <div class="sl ghost"></div>
</div>'''

def _terminal(v):
    return f'''<div class="hx termh" style="--a:{v['accent']};--p:{v['panel']};--l:{v['line']}">
  <div class="prompt">reader@2026:~$ reading --summary --evidence<span class="cur">▌</span></div>
  <div class="rail2"><span>[OK] total=38</span><span>[||||||||..] 82%</span></div>
  <div class="pane">+--- TOP 3 ---+<br>1. 索拉里斯星  ★5<br>2. 万历十五年  ★5<br>3. 云游        ★4</div>
</div>'''

def _workbench(v):
    return f'''<div class="hx termh" style="--a:{v['accent']};--p:{v['panel']};--l:{v['line']}">
  <div class="prompt">review@kindle:~$ audit highlights.csv<span class="cur">▌</span></div>
  <div class="rail2"><span>[ERR] 未标注 14 条</span><span>[WARN] 重复 3 条</span><span>[OK] 导出可用</span></div>
  <div class="pane">diff 高亮行 / 堆栈帧 / 交接结论块</div>
</div>'''

def _brief(v):
    return f'''<div class="hx briefh" style="--a:{v['accent']};--l:{v['line']}">
  <div class="chips"><i>科幻占 38%</i><i>平均 4.2★</i><i>深夜读最多</i></div>
  <div class="p main"><b>主洞察：主题集中在 9-11 月</b><span>一张主图 · 对比 · 时间线</span></div>
</div>'''

def _keepsake(v):
    return f'''<div class="hx keeph" style="--a:{v['accent']}">
  <svg viewBox="0 0 60 54" aria-hidden="true" class="heart"><path d="M30 48 C 6 32, 8 10, 22 10 c 5 0 8 4 8 4 s 3-4 8-4 c 14 0 16 22-8 38z" fill="{v['accent']}"/></svg>
  <div class="kt"><b>1,204 条</b><span>这一年的对话</span></div>
  <div class="kt"><b>386 天</b><span>有记录的日子</span></div>
</div>'''

_HEROES = dict(timeline=_timeline, teaching=_teaching, essay=_essay, dashboard=_dashboard,
               saas=_saas, scoreboard=_scoreboard, atlas=_atlas, travel=_travel,
               network=_network, document=_document, kami=_kami, spread=_spread,
               eguide=_eguide, carousel=_carousel, terminal=_terminal, workbench=_workbench,
               brief=_brief, keepsake=_keepsake)


# ---------- 提示词与样张页 ----------

def content_prompt(s):
    t = s['t']
    return ('请以「%s %s」内容排版风格，设计实现：〔在这里写下你的内容与主题，主题由你确定〕\n\n'
            '▍适用：%s\n'
            '▍底层系统：%s\n'
            '▍页面骨架（逐条落实）：\n%s\n'
            '▍组件词汇：%s\n'
            '▍本页 token（可直接用）：底 %s / 面板 %s / 主字 %s / 弱文 %s / 强调 %s / 分隔线 %s / 圆角 %s / 标题字体 %s / 正文字体 %s\n'
            '▍动效（只此一次，别加第二处）：%s\n'
            '▍必须避开（AI 指纹清单）：ALL-CAPS 装饰性眉标（信息行必须有语义：批次/期号/时段）；按钮尾部箭头 →；中点分隔 meta 串；逐卡片 fade-in 上升；无语义 01/02/03 编号；emoji 图标（一律内联 SVG）；%s\n'
            '▍验收：对比度 ≥4.5:1；:focus-visible；prefers-reduced-motion；响应式 375/768/1440') % (
        s['zh'], s['en'], s['use'], s['system'],
        '\n'.join('- ' + x for x in s['scaffold']), s['vocab'],
        t['bg'], t['panel'], t['ink'], t['muted'], t['accent'], t['line'], t['radius'], t['fh'], t['fb'],
        s['motion'], s['anti'])


_HERO_CSS = '''
.hx { border: 2.5px solid var(--ink); border-radius: var(--radius); background: var(--panel); padding: 22px; margin: 4px 0 26px; }
.hx b { font-family: var(--fh); }
.tl { border-left: 3px solid var(--a); padding-left: 18px; display: grid; gap: 14px; }
.tl-node { position: relative; }
.tl-node i { position: absolute; left: -24.5px; top: 5px; width: 11px; height: 11px; border-radius: 50%; background: var(--a); border: 2.5px solid var(--ink); }
.tl-card b { display: block; font-size: 15px; }
.tl-card span { color: var(--muted); font-size: 13px; }
.grid3 { display: grid; grid-template-columns: 1fr 1.6fr 1fr; gap: 12px; }
.grid3 .p { border: 1.5px solid var(--l); border-radius: 8px; padding: 12px; display: grid; gap: 6px; align-content: start; }
.grid3 .mini span, .grid3 .stage b { font-size: 12.5px; color: var(--muted); }
.grid3 .stage { align-items: center; justify-items: center; }
.essayh { display: grid; grid-template-columns: 44px 1fr; gap: 18px; align-items: start; }
.capsule { writing-mode: vertical-rl; font-size: 12.5px; letter-spacing: .35em; color: var(--a); border: 1.5px solid var(--a); border-radius: 999px; padding: 14px 8px; }
.essayh p { font-size: 16.5px; line-height: 2; margin: 0; }
.spore { border-bottom: 2px solid var(--a); font-weight: 700; }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
.kpi { border: 1.5px solid var(--l); border-radius: 8px; padding: 10px 12px; }
.kpi b { font-size: 24px; font-variant-numeric: tabular-nums; display: block; }
.kpi span { font-size: 12px; color: var(--muted); }
.bars { display: flex; align-items: flex-end; gap: 8px; height: 64px; }
.bars i { flex: 1; background: var(--a); border-radius: 3px 3px 0 0; opacity: .85; }
.saash { display: grid; grid-template-columns: 1fr 1.8fr 1fr; gap: 12px; }
.saash .p { border: 1.5px solid var(--l); border-radius: 14px; padding: 12px; font-size: 13px; display: grid; gap: 8px; align-content: start; }
.saash .big svg { width: 100%; height: 48px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--a); display: inline-block; margin-right: 6px; }
.dot.ok { background: #2FA463; }
.saash .p b { font-variant-numeric: tabular-nums; }
.lanes { display: grid; gap: 10px; }
.lane { display: grid; grid-template-columns: 44px 1fr auto; align-items: center; border: 2px solid var(--ink); border-radius: 6px; padding: 10px 14px; gap: 10px; }
.lane .rank { font-size: 22px; font-weight: 800; }
.lane em { font-size: 20px; font-style: normal; font-weight: 800; color: var(--a); font-variant-numeric: tabular-nums; }
.atlas svg { width: 100%; height: auto; }
.atlas .drawer { border: 1.5px solid var(--l); border-radius: 8px; padding: 8px 12px; font-size: 13px; color: var(--muted); margin-top: 10px; }
.travel .dots { display: grid; grid-template-columns: repeat(20, 1fr); gap: 5px; }
.travel .dots i { aspect-ratio: 1; border-radius: 50%; background: var(--a); opacity: .3; }
.travel .dots i:nth-child(3n) { opacity: .8; }
.runway { display: flex; gap: 26px; margin-top: 14px; }
.runway b { font-size: 26px; display: block; font-variant-numeric: tabular-nums; }
.runway span { font-size: 12px; color: var(--muted); }
.net svg { width: 100%; height: auto; }
.doch .mast { border-bottom: 2.5px solid var(--a); padding-bottom: 8px; }
.doch .mast b { font-size: 17px; display: block; }
.doch .mast span { font-size: 12.5px; color: var(--muted); }
.doch .rail { margin: 10px 0; font-size: 13px; color: var(--a); }
.doch p { margin: 0; font-size: 15px; }
.kamih { text-align: center; }
.kamih small { letter-spacing: .3em; font-size: 11px; color: var(--muted); }
.kamih b { display: block; font-size: clamp(24px, 5vw, 34px); margin: 6px 0; }
.inkline { display: block; width: 56px; height: 3px; background: var(--a); margin: 10px auto 12px; }
.kamih span { font-size: 13px; color: var(--muted); }
.spreadh { display: grid; grid-template-columns: 1fr 1fr; min-height: 220px; border: none; padding: 0; background: none; }
.spreadh .bay, .spreadh .panel { display: grid; place-items: center; border: 2.5px solid var(--ink); }
.spreadh .bay { border-right: none; border-radius: var(--radius) 0 0 var(--radius); }
.spreadh .panel { border-radius: 0 var(--radius) var(--radius) 0; text-align: left; align-content: center; gap: 8px; padding: 20px; }
.spreadh .panel small { font-size: 11px; letter-spacing: .25em; color: var(--muted); }
.spreadh .panel b { font-size: clamp(20px, 4vw, 30px); font-style: italic; }
.spreadh .panel span { font-size: 12px; }
.eguideh { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.eguideh .pg { border: 1.5px solid var(--l); border-radius: 4px; padding: 16px; display: grid; gap: 8px; align-content: start; aspect-ratio: 3/4; }
.eguideh small { font-size: 10.5px; letter-spacing: .2em; color: var(--muted); }
.eguideh .cover b { font-size: clamp(18px, 3.4vw, 26px); line-height: 1.2; }
.eguideh span { font-size: 12px; color: var(--muted); }
.carouselh { display: flex; gap: 12px; overflow: hidden; }
.carouselh .sl { flex: 0 0 31%; aspect-ratio: 4/5; border: 2px solid var(--ink); border-radius: 8px; padding: 14px; display: grid; align-content: end; gap: 8px; }
.carouselh .sl em { font-size: 34px; font-style: normal; font-weight: 800; color: var(--a); align-self: start; }
.carouselh .sl span { font-size: 13px; font-weight: 600; }
.carouselh .ghost { opacity: .35; }
.termh { font-family: 'JetBrains Mono', Consolas, monospace; background: var(--p); color: #C8E6C9; border-color: var(--l); font-size: 13px; }
.termh .prompt b, .termh b { color: inherit; font-family: inherit; }
.termh .prompt { color: #9FE8B0; }
.termh .cur { animation: blink 1.1s steps(1) infinite; color: var(--a); }
@keyframes blink { 50% { opacity: 0; } }
.termh .rail2 { display: flex; gap: 16px; flex-wrap: wrap; margin: 10px 0; color: #8FB99A; }
.termh .pane { border: 1px solid var(--a); padding: 10px 12px; line-height: 1.7; }
.briefh .chips { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.briefh .chips i { font-style: normal; font-size: 12px; border: 1.5px solid var(--l); border-radius: 999px; padding: 4px 12px; color: var(--muted); }
.briefh .main { border: 1.5px solid var(--l); border-radius: 12px; padding: 16px; display: grid; gap: 6px; }
.briefh .main b { font-size: 16px; }
.briefh .main span { font-size: 12.5px; color: var(--muted); }
.keeph { display: grid; grid-template-columns: 70px 1fr 1fr; gap: 14px; align-items: center; }
.keeph .heart { width: 100%; filter: drop-shadow(0 6px 12px rgba(232,93,138,.35)); }
.keeph .kt b { font-size: 22px; display: block; }
.keeph .kt span { font-size: 12.5px; color: var(--muted); }
@media (max-width: 640px) {
  .grid3, .saash, .spreadh, .eguideh { grid-template-columns: 1fr; }
  .keeph { grid-template-columns: 56px 1fr 1fr; }
}
@media (prefers-reduced-motion: reduce) { .termh .cur { animation: none; } }
'''




def content_page(s):
    t = s['t']
    fams = '+'.join('family=' + f.replace(' ', '+') for f in sorted({t['fh'], t['fb'], 'JetBrains Mono'}))
    steps = ''.join('<li><b>%02d</b><span>%s</span></li>' % (i + 1, x) for i, x in enumerate(s['scaffold']))
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<title>%s · 内容排版风格 — UI 设计提示词库</title>
<meta name="description" content="UI 设计提示词库 · 内容排版风格样张与官方提示词，复制后交给 AI 复刻同款网页。">
<style>
@import url('https://fonts.googleapis.com/css2?%s&display=swap');

:root {
  --bg: %s; --panel: %s; --ink: %s; --muted: %s;
  --accent: %s; --line: %s; --radius: %s;
  --fh: '%s', 'PingFang SC', 'Microsoft YaHei', serif;
  --fb: '%s', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: var(--fb); background: var(--bg); color: var(--ink); line-height: 1.65; padding: 44px 22px 70px; }
.wrap { max-width: 860px; margin: 0 auto; }
.back { display: inline-block; font-size: 13.5px; font-weight: 600; color: var(--ink); text-decoration: none; border: 2px solid var(--ink); border-radius: 999px; padding: 6px 16px; margin-bottom: 26px; background: var(--panel); box-shadow: 3px 3px 0 var(--ink); }
.back:hover { transform: translate(-1px,-1px); }
.back:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.kicker { font-size: 13px; font-weight: 600; color: var(--accent); }
h1 { font-family: var(--fh); font-size: clamp(30px, 6vw, 44px); line-height: 1.15; margin: 4px 0 10px; }
.sub { color: var(--muted); font-size: 15px; max-width: 640px; }
.meta { margin: 14px 0 6px; font-size: 13px; color: var(--muted); border-top: 1.5px dashed var(--line); border-bottom: 1.5px dashed var(--line); padding: 10px 2px; }
.meta code { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; color: var(--ink); }
h2 { font-family: var(--fh); font-size: 19px; margin: 34px 0 12px; }
.steps { list-style: none; display: grid; gap: 10px; }
.steps li { display: grid; grid-template-columns: 34px 1fr; gap: 10px; align-items: baseline; }
.steps b { font-size: 15px; color: var(--accent); font-variant-numeric: tabular-nums; }
.steps span { font-size: 14.5px; }
.vocab { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12.5px; color: var(--muted); background: var(--panel); border: 1.5px dashed var(--line); border-radius: 8px; padding: 10px 14px; word-break: break-word; }
.note { margin-top: 40px; font-size: 13px; color: var(--muted); }
.note a { color: var(--accent); font-weight: 600; }
%s
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../style-catalog.html">← 返回风格目录</a>
  <p class="kicker">内容排版风格 · %s</p>
  <h1>%s</h1>
  <p class="sub">%s。%s。</p>
  <p class="meta">本页 token：<code>底 %s</code> <code>面板 %s</code> <code>主字 %s</code> <code>强调 %s</code> <code>圆角 %s</code> · 标题 <code>%s</code> / 正文 <code>%s</code> · 动效：%s</p>

  <h2>结构示意</h2>
  %s

  <h2>页面骨架（官方定义，逐条落实）</h2>
  <ol class="steps">%s</ol>

  <h2>组件词汇</h2>
  <p class="vocab">%s</p>

  <p class="note">提示词在<a href="../style-catalog.html">风格目录</a>对应卡片中一键复制 · 主题由使用者确定，本页演示内容仅为排版示意。</p>
</div>
</body>
</html>''' % (s['zh'], fams, t['bg'], t['panel'], t['ink'], t['muted'], t['accent'], t['line'], t['radius'],
               t['fh'], t['fb'], _HERO_CSS, s['en'], s['zh'], s['system'], s['use'],
               t['bg'], t['panel'], t['ink'], t['accent'], t['radius'], t['fh'], t['fb'], s['motion'],
               hero_html(s), steps, s['vocab'])
