"""
content.py — المحتوى الثابت لصفحات الموقع العام.
ثوابت بالكود لا جداول (كما هو مقرر في قرارات المشروع): لتعديل نص أو خبر أو شعار شريك، عدّله هنا مباشرة.
"""
from django.templatetags.static import static


# ── مشترك بين "الرئيسية" و"قبول المنح": مراحل رحلة المانح (مع إحداثيات الرسم الدائري) ──

PROGRAM_STEPS = [
    {"title": "تبدأ", "desc": "تقديم طلب الرغبة في الدعم عبر قنوات التواصل الخاصة بالإدارة",
     "color": "#B3DEC7", "cx": 563, "cy": 117, "lx": 483, "ly": 4, "lw": 160, "lh": 60},
    {"title": "تختار", "desc": "اختيار واعتماد المشروع بعد عرض عدد من المشاريع المقترحة",
     "color": "#5AB379", "cx": 650, "cy": 290, "lx": 700, "ly": 252, "lw": 160, "lh": 76},
    {"title": "تمنح", "desc": "إصدار قرار قبول المنحة والتوقيع رسمياً والإعلان عنها",
     "color": "#31715F", "cx": 563, "cy": 463, "lx": 483, "ly": 516, "lw": 160, "lh": 62},
    {"title": "تؤثر", "desc": "عكس أثر المنحة من خلال تقارير دورية أثر وقصص النجاح",
     "color": "#6B7787", "cx": 337, "cy": 463, "lx": 257, "ly": 516, "lw": 160, "lh": 62},
    {"title": "تستفيد", "desc": "الاستفادة من المزايا المقدمة لتعظيم الأثر وتحقيق القيمة",
     "color": "#17343D", "cx": 250, "cy": 290, "lx": 40, "ly": 252, "lw": 160, "lh": 76},
    {"title": "تكرم", "desc": "تكرم مساهمة المانح تقديراً لعطائه وأثره",
     "color": "#D7CF60", "cx": 337, "cy": 117, "lx": 257, "ly": 4, "lw": 160, "lh": 60},
]


# ── الصفحة الرئيسية ──────────────────────────────────────────────────────

GOALS = [
    "بناء وتعزيز العلاقات مع المانحين بما يحقق طموحاتهم ويتواءم مع استراتيجيات الجامعة.",
    "المساهمة في تحقيق أهداف رؤية المملكة 2030 من خلال الشراكة مع القطاعين العام والخاص.",
    "المساهمة في خدمة احتياجات المجتمع بإبراز الأثر الناتج عن العلاقة المتبادلة بين الجامعة ومانحيها.",
    "تحقيق الاستدامة المالية وتعزيز انخراط الشركاء والمانحين في خدمة المجتمع.",
]

NEWS_ITEMS = [
    {
        "img": static("public_site/images/news/news-bandah.jpg"),
        "tag": "شراكة", "date": "17 يونيو 2025م",
        "title": "منحة بندة للتجزئة لدعم عيادات الأسنان المتنقلة",
        "desc": "وقّعت الجامعة اتفاقية شراكة مع بندة للتجزئة منحة لدعم عيادات الأسنان المتنقلة، لما لها من أثر في تحسين جودة الرعاية الصحية المقدمة للمجتمع، وتعزيز التدريب العملي لطلبة كلية طب الأسنان.",
        "link": "https://x.com/kauedu_sa/status/1935008353710649599?s=48&t=G7Y-7ksNJMZzV3q9M9rCqg",
    },
    {
        "img": static("public_site/images/news/news-aqeel.png"),
        "tag": "شراكة", "date": "19 يونيو 2025م",
        "title": "منحة بحثية من مؤسسة العقيل الخيرية لدعم البحث العلمي",
        "desc": 'وقّعت الجامعة اتفاقية تعاون مع مؤسسة أبناء عبدالرحمن العقيل الخيرية "جرير للاستثمار" لتقديم منحة بحثية تمتد لخمسة أعوام، لدعم منظومة البحث العلمي وتمكين الباحثين من المشاركة العالمية.',
        "link": "https://x.com/kauedu_sa/status/1935699904321519842?s=48&t=G7Y-7ksNJMZzV3q9M9rCqg",
    },
    {
        "img": static("public_site/images/news/news-kidney-dialysis.jpg"),
        "tag": "شراكة", "date": "",
        "title": "مجلس الجامعة يوافق على قبول التبرع لدعم مركز التميز في الرعاية الصحية لكلى الأطفال",
        "desc": "وافق مجلس جامعة الملك عبد العزيز على قبول التبرع العيني المقدم من أوقاف الشيخ عبد الرحمن عبد العزيز الراجحي، والمتمثل في توفير (9) أجهزة لغسيل الكلى مع محطة مياه متنقلة واحدة، لصالح مركز التميز في الرعاية الصحية لكلى الأطفال التابع للمستشفى الجامعي.",
    },
    {
        "img": static("public_site/images/news/news-media-lab.jpg"),
        "tag": "شراكة", "date": "",
        "title": "موافقة مجلس الجامعة على قبول التبرع العيني لصالح مشروع المعمل الإعلامي",
        "desc": "وافق مجلس الجامعة على قبول التبرع العيني المقدم من مؤسسة جرير للتسويق لدعم مشروع المعمل الإعلامي بكلية الاتصال والإعلام، وذلك في إطار تعزيز البيئة التعليمية والتدريبية، والارتقاء بالإمكانات التقنية التي تدعم العملية الأكاديمية.",
    },
    {
        "img": static("public_site/images/news/news-savvy-games.jpg"),
        "tag": "شراكة", "date": "",
        "title": "إبرام اتفاقية تعاون مع شركة الاستثمارات المحلية للألعاب الإلكترونية",
        "desc": "وافق مجلس الجامعة على إبرام اتفاقية تعاون بين الجامعة وشركة الاستثمارات المحلية للألعاب الإلكترونية (مجموعة سافي للألعاب)، وذلك في إطار تعزيز الشراكات الاستراتيجية مع القطاع الخاص، ودعم البرامج الأكاديمية المتخصصة التي تواكب متطلبات القطاعات الواعدة.",
    },
    {
        "img": static("public_site/images/news/news-children-voices.jpg"),
        "tag": "شراكة", "date": "",
        "title": 'مشروع "منهجية أصوات الأطفال" بمنحة من مؤسسة "أحياها" الإنسانية',
        "desc": 'أنجزت جامعة الملك عبد العزيز، ممثلة بكلية علوم الإنسان والتصاميم وقسم الطفولة المبكرة، المرحلة الأولى من مشروع "منهجية أصوات الأطفال"، الذي نفذ بدعم من مؤسسة الأمير عبد العزيز بن طلال وسُرى بنت سعود للتنمية الإنسانية (أحياها الإنسانية)، وبالشراكة مع جامعة كلية لندن الجامعية (UCL) ومؤسسة البداية المشرقة (Bright Start Foundation).',
    },
]

RESOURCE_CARDS = [
    {"img": "https://kau.edu.sa/web/static?path=uploads/2025/Jul/sections/REf9V0RFpkp7J06a.jfif", "title": "الخدمات"},
    {"img": "https://kau.edu.sa/web/static?path=uploads/2025/Jul/sections/gMmgcNnyngIHZo6J.jfif", "title": "السياسات والإجراءات"},
    {"img": "https://kau.edu.sa/web/static?path=uploads/2025/Jul/sections/40q7N5PKOjRcvRTh.jfif", "title": "النماذج والأدلة"},
    {"img": "https://kau.edu.sa/web/static?path=uploads/2025/Jul/sections/2qny7AcSHlBn8Rmx.jfif", "title": "دليل التواصل"},
]

PARTNERS = [
    {"src": static('public_site/images/partners/partner-01-acino.jpeg'), "alt": 'Acino', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-02-partner-02.jpg'), "alt": 'Alrajhi Endowments', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-03-partner-03.png'), "alt": 'Al Dhuwayan Charity', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-04-partner-04.png'), "alt": 'Damy', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-05-partner-05.png'), "alt": 'The National Home Health Care Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-06-partner-06.png'), "alt": 'Al Dahyan Endowments', "aspect": 'tall', "label": None},
    {"src": static('public_site/images/partners/partner-07-partner-07.png'), "alt": 'Saudi Orthodontic Society', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-08-partner-08.jpeg'), "alt": 'Afaq Educational Association', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-09-partner-09.jpg'), "alt": 'Safe Medical Care Org', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-10-partner-10.png'), "alt": 'Dr. Abeer Mohammed Nuwaisir', "aspect": 'wide', "label": 'د. عبير محمد نويصر'},
    {"src": static('public_site/images/partners/partner-11-partner-11.jpeg'), "alt": "Ta'alum", "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-12-partner-12.png'), "alt": 'Heart Patients Care Society', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-13-partner-13.png'), "alt": 'Al Amjaad Trading & Manufacturing Company', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-14-partner-14.png'), "alt": 'Al Tayyar International Travel & Tourism Agency', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-15-partner-15.png'), "alt": 'Baazeem Trading Co.', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-16-partner-16.jpeg'), "alt": 'Raz for Training Consultants', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-17-sela.png'), "alt": 'Sela', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-18-keysight.png'), "alt": 'Keysight', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-19-savvy-games-group.png'), "alt": 'Savvy Games Group', "aspect": 'square', "label": None},
    {"src": static('public_site/images/partners/partner-20-partner-20.png'), "alt": 'Ibrahim Al-Angary and His Descendants Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-21-partner-21.png'), "alt": 'Ahyaha', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-22-partner-22.png'), "alt": 'Hassan Taher Charity Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-23-partner-23.png'), "alt": 'Salem Bin Mahfouz Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-24-partner-24.png'), "alt": 'Berr Charity Fund - SABIC Employees', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-25-partner-25.png'), "alt": 'Bin Deajim', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-26-partner-26.png'), "alt": 'Al Subaie Charity Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-27-partner-27.png'), "alt": 'Ghaith', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-28-partner-28.png'), "alt": 'Nestlé', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-29-partner-29.png'), "alt": 'Allulwah Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-30-partner-30.png'), "alt": 'SABIC', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-31-partner-31.jpg'), "alt": 'Saudi Aramco', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-32-partner-32.png'), "alt": 'Dallah Albaraka', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-33-partner-33.png'), "alt": 'Baraa Society of Blood and Cancer in Makkah Children', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-34-partner-34.png'), "alt": 'Abdullah Taha Nejaish Endowment', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-35-partner-35.png'), "alt": 'Abudawood Group', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-36-partner-36.png'), "alt": 'Saudi National Bank', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-37-partner-37.jpeg'), "alt": 'Islamic Development Bank', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-38-partner-38.png'), "alt": 'Heart Friends Charitable Society', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-39-partner-39.jpeg'), "alt": 'Tamr', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-40-partner-40.jpg'), "alt": "Falathat Society for Children's Health Care", "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-41-partner-41.jpg'), "alt": 'Hassan Abbas Sharbatly Community Service Foundation', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-42-partner-42.png'), "alt": 'Haif Company', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-43-partner-43.jpeg'), "alt": 'Sheikh Saleh Hamza Sairafi Endowment', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-44-partner-44.png'), "alt": 'KAU Scientific Endowment', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-45-partner-45.jpeg'), "alt": 'Hoshan Group', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-46-partner-46.png'), "alt": 'Jarir Bookstore', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-47-partner-47.png'), "alt": 'Savola Group', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-48-partner-48.png'), "alt": 'Jameel Community Saudi Arabia', "aspect": 'wide', "label": None},
    {"src": static('public_site/images/partners/partner-49-partner-49.jpg'), "alt": 'Alagil Foundation', "aspect": 'wide', "label": None},
    {"src": None, "alt": 'وقف المدرسة الكشميرية', "aspect": 'wide', "label": 'وقف المدرسة الكشميرية'},
    {"src": None, "alt": 'الشيخ محمد حسين العامودي', "aspect": 'wide', "label": 'الشيخ محمد حسين العامودي'},
    {"src": None, "alt": 'الأمير نواف بن فيصل بن فهد آل سعود', "aspect": 'wide', "label": 'الأمير نواف بن فيصل بن فهد آل سعود'},
    {"src": None, "alt": 'الأمير بندر بن سلمان بن محمد آل سعود', "aspect": 'wide', "label": 'الأمير بندر بن سلمان بن محمد آل سعود'},
    {"src": None, "alt": 'سمو الأميرة الجوهرة الإبراهيم', "aspect": 'wide', "label": 'سمو الأميرة الجوهرة الإبراهيم'},
    {"src": None, "alt": 'الشيخ سالم صالح باعظيم', "aspect": 'wide', "label": 'الشيخ سالم صالح باعظيم'},
    {"src": None, "alt": 'الأمير خالد الفيصل آل سعود', "aspect": 'wide', "label": 'الأمير خالد الفيصل آل سعود'},
    {"src": None, "alt": 'أ.د. عصام أزهر', "aspect": 'wide', "label": 'أ.د. عصام أزهر'},
]


# ── بيانات التواصل (تختلف التسميات قليلاً من صفحة لأخرى) ────────────────

# الصفحة الرئيسية
CONTACT_ITEMS = [
    {"label": "رقم الهاتف", "value": "0126951328"},
    {"label": "البريد الإلكتروني", "value": "dra@kau.edu.sa"},
    {"label": "موقع الإدارة", "value": "www.dra.kau.edu.sa"},
]

# صفحة "قبول المنح"
GRANT_CONTACT_ITEMS = [
    {"label": "الهاتف", "value": "0126951328"},
    {"label": "البريد الإلكتروني", "value": "dra@kau.edu.sa"},
    {"label": "الموقع الإلكتروني", "value": "www.dra.kau.edu.sa"},
]

# صفحة "اتصل بنا"
SUGGESTIONS_CONTACT_ITEMS = [
    {"label": "رقم الهاتف", "value": "0126951328"},
    {"label": "البريد الإلكتروني", "value": "dra@kau.edu.sa"},
    {"label": "موقع الإدارة", "value": "www.dra.kau.edu.sa"},
]


# ── نماذج الاقتراحات بصفحة "اتصل بنا" ───────────────────────────────────
# لكل نموذج: عنوان الإيميل + الحقول بالترتيب الذي تظهر به في الإيميل (التسمية، اسم الحقل بالنموذج)

SUGGESTION_FORMS = {
    "external": {
        "subject": "اقتراح جديد - جهة من خارج الجامعة",
        "fields": [
            ("الاسم", "name"),
            ("اسم الجهة", "org_name"),
            ("رقم التواصل", "phone"),
            ("البريد الإلكتروني", "email"),
            ("الاقتراح", "suggestion"),
        ],
    },
    "internal": {
        "subject": "اقتراح جديد - جهة من داخل الجامعة",
        "fields": [
            ("اسم الجهة", "org_name"),
            ("اسم المشروع", "project_name"),
            ("فكرة المشروع", "idea"),
            ("الفئة المستهدفة", "target_group"),
            ("الطاقة الاستيعابية", "capacity"),
            ("مخرجات المشروع", "outcomes"),
            ("التكلفة التقديرية", "estimated_cost"),
            ("ضابط الاتصال", "contact_officer"),
            ("ملاحظات", "notes"),
        ],
    },
    "members": {
        "subject": "اقتراح جديد - منسوبين وطلبة",
        "fields": [
            ("الاسم", "name"),
            ("الرقم الجامعي/الوظيفي", "id_number"),
            ("الكلية أو القسم", "department"),
            ("رقم التواصل", "phone"),
            ("اسم المشروع", "project_name"),
            ("الفئة المستهدفة", "target_group"),
            ("فكرة المشروع", "idea"),
            ("مخرجات المشروع", "outcomes"),
            ("ملاحظات", "notes"),
        ],
    },
}
