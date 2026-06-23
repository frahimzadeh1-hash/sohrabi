from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sohrabi-campaign-2026'

DATA_FILE = os.path.join('data', 'villages_data.json')
CITIES_FILE = os.path.join('data', 'cities_data.json')
WORKGROUPS_FILE = os.path.join('data', 'workgroups_data.json')

# ============================================
# داده‌های پیش‌فرض (کوتاه شده برای تست)
# ============================================
DEFAULT_VILLAGES = [
    {
        'id': 1, 'name': 'اندبیل', 'section': 'مرکزی', 'population': 2400, 'households': 650,
        'martyrs': 'شهید رحیمی، شهید عباس‌زاده', 'lat': 38.2850, 'lng': 45.7750, 'status': 'good',
        'capacities': 'باغات سیب\nچشمه معدنی\nفرش دستباف',
        'problems': 'کمبود آب\nنبود سردخانه\nمهاجرت جوانان', 'avg_vote': 850, 'opponent': 'فلاحی',
        'influencers': []
    }
]

DEFAULT_CITIES = [
    {'id': 1, 'name': 'شبستر', 'section': 'مرکزی', 'population': 20000, 'description': 'مرکز شهرستان', 'key_people': ''}
]

DEFAULT_WORKGROUPS = [
    {'id': 1, 'name': 'بانوان', 'section': 'ستادی', 'icon': '👩‍👧‍👧', 'tasks': '', 'members': ''}
]

# ============================================
# توابع
# ============================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_VILLAGES

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cities():
    if os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CITIES

def save_cities(data):
    with open(CITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_workgroups():
    if os.path.exists(WORKGROUPS_FILE):
        with open(WORKGROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_WORKGROUPS

def save_workgroups(data):
    with open(WORKGROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================
# صفحات
# ============================================
@app.route('/')
def index():
    villages = load_data()
    total_villages = len(villages)
    total_population = sum(v['population'] for v in villages)
    total_households = sum(v['households'] for v in villages)
    total_avg_vote = sum(v['avg_vote'] for v in villages)
    good = sum(1 for v in villages if v['status'] == 'good')
    warning = sum(1 for v in villages if v['status'] == 'warning')
    danger = sum(1 for v in villages if v['status'] == 'danger')
    
    sections = {}
    for v in villages:
        sec = v['section']
        if sec not in sections:
            sections[sec] = {'count': 0, 'population': 0, 'votes': 0}
        sections[sec]['count'] += 1
        sections[sec]['population'] += v['population']
        sections[sec]['votes'] += v['avg_vote']
    
    today = datetime.now().strftime('%Y/%m/%d')
    today_persian = today.replace('2026', '۱۴۰۴').replace('2025', '۱۴۰۴')
    
    today_calls = []
    total_contacts = 0
    moafeg = 0
    mordad = 0
    mokhalef = 0
    
    for v in villages:
        for inf in v.get('influencers', []):
            total_contacts += 1
            if inf.get('status') == 'موافق':
                moafeg += 1
            elif inf.get('status') == 'مردد':
                mordad += 1
            elif inf.get('status') == 'مخالف':
                mokhalef += 1
            
            if inf.get('next_call_date') == today_persian:
                today_calls.append({
                    'village': v['name'],
                    'section': v['section'],
                    'name': inf['name'],
                    'phone': inf['phone'],
                    'role': inf['role'],
                    'status': inf.get('status', ''),
                    'last_call_date': inf.get('last_call_date', ''),
                    'last_call_result': inf.get('last_call_result', ''),
                    'referrer': inf.get('referrer', ''),
                    'referrer_phone': inf.get('referrer_phone', '')
                })
    
    return render_template('index.html',
                         total_villages=total_villages,
                         total_population=total_population,
                         total_households=total_households,
                         total_avg_vote=total_avg_vote,
                         good=good, warning=warning, danger=danger,
                         sections=sections, villages=villages,
                         today_calls=today_calls, today_date=today_persian,
                         total_contacts=total_contacts, moafeg=moafeg,
                         mordad=mordad, mokhalef=mokhalef)

@app.route('/map')
def map_view():
    return render_template('map.html', villages=load_data())

@app.route('/village/<village_name>')
def village_profile(village_name):
    villages = load_data()
    village = next((v for v in villages if v['name'] == village_name), None)
    if village:
        return render_template('village.html', village=village, village_name=village_name)
    return "<h1>روستا یافت نشد</h1>"
@app.route('/speech', methods=['GET', 'POST'])
def generate_speech():
    if request.method == 'POST':
        village_name = request.form.get('village_name', 'روستای عزیز')
        section = request.form.get('section', 'شبستر')
        martyrs = request.form.get('martyrs', '')
        capacities = request.form.get('capacities', '')
        problems = request.form.get('problems', '')
        key_people = request.form.get('key_people', '')
        opponent = request.form.get('opponent', '')
        
        cap_list = [c.strip() for c in capacities.split('\n') if c.strip()]
        prob_list = [p.strip() for p in problems.split('\n') if p.strip()]
        
        # بخش شهدا
        shohada_section = ""
        if martyrs:
            shohada_list = [m.strip() for m in martyrs.replace('،', ',').split(',') if m.strip()]
            shohada_text = "، ".join(shohada_list)
            shohada_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🏴 بخش اول: ادای احترام به شهدای معزز
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    مردم شریف {village_name}،
    
    پیش از هر سخنی، وظیفه خود می‌دانم که به پاس ایثار و فداکاری فرزندان غیور این روستا، سر تعظیم فرود آورم. عزیزانی که جان شیرین خود را در طبق اخلاص نهاده و در راه عزت و سربلندی این مرز و بوم تقدیم کردند:
    
    🏴 {shohada_text}
    
    این عزیزان از میان ما برخاستند تا ما در امنیت و آرامش زندگی کنیم. یادشان را گرامی می‌داریم و راهشان را ادامه خواهیم داد.
    
    از شما می‌خواهم به احترام روح بلند این شهدای والامقام، صلواتی نثار فرمایید.
    اللهم صل علی محمد و آل محمد و عجل فرجهم"""
        
        # بخش ظرفیت‌ها
        capacities_section = ""
        if cap_list:
            cap_items = "\n".join([f"        {i}. {cap}" for i, cap in enumerate(cap_list, 1)])
            capacities_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ⭐ بخش دوم: {village_name}، نگین درخشان شبستر
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    مردم عزیز و بزرگوار،
    
    من با چشمانی باز و با شناختی عمیق به اینجا آمده‌ام. {village_name} فقط یک روستا نیست؛ {village_name} یکی از ارکان اصلی بخش {section} و شهرستان شبستر است. ظرفیت‌هایی که اگر شکوفا شوند، نه تنها این روستا، بلکه کل منطقه از آن بهره‌مند خواهد شد:
    
{cap_items}
    
    این‌ها را نمی‌گویم که فقط تعریف کرده باشم. می‌گویم چون باور دارم {village_name} لایق بهترین‌هاست. شما کشاورز زحمتکش، شما باغدار پرتلاش، شما زن روستایی کارآفرین، شما جوان تحصیل‌کرده – همه و همه سرمایه‌های واقعی این روستا هستید. سرمایه‌هایی که باید دیده شوند و به آنها افتخار کرد."""
        
        # بخش مشکلات
        problems_section = ""
        if prob_list:
            prob_items = "\n".join([f"        {i}. {prob}" for i, prob in enumerate(prob_list, 1)])
            problems_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ❌ بخش سوم: دردی که از نزدیک لمس کرده‌ام
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    برادران و خواهر گرامی،
    
    من مثل برخی نیامده‌ام اینجا فقط لبخند بزنم و قول بدهم و بروم. من دردهای شما را می‌دانم. مشکلاتی که سال‌هاست مثل خوره به جان این روستا افتاده و کسی به فریاد نرسیده است:
    
{prob_items}
    
    می‌دانم یعنی چه یک کشاورز بعد از یک سال زحمت طاقت‌فرسا، محصولش را به ثمن بخس بفروشد چون سردخانه و صنایع تبدیلی ندارد. می‌دانم یعنی چه یک مادر دلسوز، نگران آینده فرزند تحصیل‌کرده‌اش باشد که در روستا شغلی نمی‌یابد. می‌دانم یعنی چه جوانی که عاشق زادگاهش است، مجبور شود بار سفر ببندد و به حاشیه‌ی شهرها پناه ببرد.
    
    این‌ها فقط حرف نیست. این‌ها واقعیت تلخ زندگی شماست که من از نزدیک لمسش کرده‌ام."""
        
        # بخش رقیب
        opponent_section = ""
        if opponent:
            opponent_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ⚠️ بخش چهارم: شعار بس است، وقت عمل است
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    مردم شریف {village_name}،
    
    سال‌هاست که آقای {opponent} و امثال ایشان آمده‌اند، قول داده‌اند و رفته‌اند. از شما رأی گرفته‌اند و بعد فراموشتان کرده‌اند. شما بگویید، بعد از این همه سال، کدام یک از این مشکلات حل شده است؟ کدام قول رنگ عمل به خود دیده است؟
    
    من نمی‌خواهم تخریب کنم. تخریب کار من نیست. اما وجداناً بگویید: آیا وضعیت امروز {village_name} شایسته شما مردم نجیب و زحمتکش است؟ شما لایق نماینده‌ای هستید که فقط شب قبل از انتخابات به یادتان نیفتد. شما لایق نماینده‌ای هستید که ۴ سال، نه ۴ روز، در کنارتان باشد و پاسخگو."""
        
        # بخش راه‌حل‌ها
        solutions_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    💡 بخش پنجم: برنامه عملی، نه شعار توخالی
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    و اما برنامه من برای {village_name}. برنامه‌ای که حاصل ماه‌ها مطالعه، مشورت با کارشناسان و مهم‌تر از همه، گوش سپردن به درد دل شما مردم عزیز است:
    
    ۱. ایجاد صندوق حمایت از کشاورزان و باغداران با همکاری بخش خصوصی و بانک‌ها
    
    ۲. راه‌اندازی صنایع تبدیلی و بسته‌بندی برای جلوگیری از خام‌فروشی و افزایش درآمد شما
    
    ۳. پیگیری ویژه برای حل مشکلات آب کشاورزی از طریق وزارت نیرو و نمایندگی مجلس
    
    ۴. حمایت از کسب‌وکارهای خانگی و کارآفرینی بانوان با ارائه تسهیلات کم‌بهره
    
    ۵. ایجاد سامانه اشتغال برای جوانان تحصیل‌کرده و ارتباط با صنایع منطقه
    
    ۶. پیگیری بهبود راه‌های روستایی و زیرساخت‌های ارتباطی
    
    من یک نماینده سنتی نخواهم بود که فقط در دفترش بنشیند و منتظر مراجعه مردم باشد. دفتر من در روستاها و در میان مردم خواهد بود. هر ماه یکبار شخصاً در {village_name} حاضر می‌شوم و به مردم گزارش می‌دهم."""
        
        # بخش قدردانی
        thanks_section = ""
        if key_people:
            thanks_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🤝 بخش ششم: قدردانی از بزرگان و معتمدین
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    در اینجا لازم می‌دانم از حضور گرم و صمیمی بزرگان و معتمدین محترم که در این جلسه حاضرند، صمیمانه تشکر و قدردانی کنم:
    
    {key_people}
    
    حضور شما بزرگواران مایه دلگرمی و نشانه اعتماد و همراهی شما با آینده این روستا و این شهرستان است. دست یکایک شما را به گرمی می‌فشارم."""
        
        # بخش پایانی
        ending_section = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚀 بخش پایانی: فردا از آن ماست
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    مردم {village_name}،
    
    انتخابات پیش رو فقط انتخاب یک نماینده نیست. انتخابات پیش رو، انتخاب بین ادامه وضع موجود و یک شروع تازه است. انتخاب بین شعار و عمل است. انتخاب بین فراموشی و پاسخگویی است.
    
    من به تنهایی نمی‌توانم کاری انجام دهم. اما «ما» می‌توانیم. من آمده‌ام تا صدای شما باشم. صدای کشاورزی که دغدغه آب دارد. صدای جوانی که دغدغه اشتغال دارد. صدای مادری که دغدغه آینده فرزندش را دارد. صدای بیماری که دغدغه درمان دارد.
    
    دستم را بگیرید تا با هم {village_name} را بسازیم.
    دستم را بگیرید تا ندای عدالت باشیم.
    دستم را بگیرید تا فردایی بهتر برای فرزندانمان رقم بزنیم.
    
    رأی شما امانتی است در دست من. به خداوند بزرگ سوگند که پاسدار این امانت خواهم بود.
    
    از اعتماد شما سپاسگزارم.
    از صبوری شما سپاسگزارم.
    از محبت بی‌دریغ شما سپاسگزارم.
    
    یا علی مدد
    
    با احترام
    دکتر سهرابی
    خادم مردم شریف شهرستان شبستر
    🇮🇷
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📞 شماره تماس ستاد: [شماره ستاد]
    📱 کانال اطلاع‌رسانی: [آدرس شبکه اجتماعی]
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        # ترکیب نهایی
        speech = f"""بسم الله الرحمن الرحیم

«وَقُلِ اعْمَلُوا فَسَیَرَى اللَّهُ عَمَلَکُمْ وَرَسُولُهُ وَالْمُؤْمِنُونَ»
صدق الله العلی العظیم

السلام علیکم و رحمة الله و برکاته

خدمت تکتک شما مردم شریف، نجیب، زحمتکش و بزرگوار روستای {village_name}، سلام و درود می‌فرستم. سلامی به گرمای دل‌های پاکتان، سلامی به وسعت غیرت و همتتان، سلامی به بلندای قامت استوارتان.

عزیزان من، برادران و خواهران گرامی،

امروز برای من روز بسیار ویژه‌ای است. من به اینجا نیامده‌ام که فقط یک سخنرانی انتخاباتی انجام دهم. من آمده‌ام تا با شما درد دل کنم. آمده‌ام تا از جنس خودتان باشم. آمده‌ام تا بگویم که درد شما را می‌فهمم، رنج شما را درک می‌کنم و برای تک‌تک مشکلاتتان برنامه دارم.
{shohada_section}
{capacities_section}
{problems_section}
{opponent_section}
{solutions_section}
{thanks_section}
{ending_section}"""
        
        return render_template('speech.html', speech=speech, generated=True)
    
    return render_template('speech.html', generated=False)
@app.route('/contacts')
def contacts():
    villages = load_data()
    all_contacts = []
    for v in villages:
        for inf in v.get('influencers', []):
            all_contacts.append({
                'section': inf.get('section', v.get('section', '')),
                'city': inf.get('city', ''),
                'village': inf.get('village', v['name']),
                'workgroup': inf.get('workgroup', ''),
                'name': inf['name'],
                'phone': inf['phone'],
                'role': inf['role'],
                'status': inf['status'],
                'referrer': inf.get('referrer', ''),
                'referrer_phone': inf.get('referrer_phone', ''),
                'last_call_date': inf.get('last_call_date', ''),
                'last_call_result': inf.get('last_call_result', ''),
                'next_call_date': inf.get('next_call_date', '')
            })
    return render_template('contacts.html', contacts=all_contacts, villages=villages)

@app.route('/manage')
def manage():
    return render_template('manage.html', villages=load_data(), cities=load_cities(), workgroups=load_workgroups())

@app.route('/war-room')
def war_room():
    villages = load_data()
    opponents = {}
    for v in villages:
        opp = v.get('opponent', 'نامشخص')
        if opp not in opponents:
            opponents[opp] = {'name': opp, 'villages': [], 'total_votes': 0, 'strongholds': 0}
        opponents[opp]['villages'].append(v['name'])
        opponents[opp]['total_votes'] += v['avg_vote']
        if v['status'] == 'danger':
            opponents[opp]['strongholds'] += 1
    return render_template('war_room.html', opponents=list(opponents.values()), villages=villages)

@app.route('/api/villages')
def api_villages():
    return jsonify(load_data())

@app.route('/api/opponent-analysis/<village_name>')
def opponent_analysis(village_name):
    villages = load_data()
    village = next((v for v in villages if v['name'] == village_name), None)
    if village:
        return jsonify({
            'village': village['name'],
            'opponent': village.get('opponent', ''),
            'status': village['status'],
            'our_strength': 'قوی' if village['status'] == 'good' else 'متوسط' if village['status'] == 'warning' else 'ضعیف',
            'priority': 'فوری' if village['status'] == 'danger' else 'متوسط' if village['status'] == 'warning' else 'پایین',
            'recommendation': 'حفظ وضعیت' if village['status'] == 'good' else 'جلسات چهره به چهره' if village['status'] == 'warning' else 'حضور فوری دکتر'
        })
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/add_village', methods=['POST'])
def add_village():
    villages = load_data()
    villages.append({
        'id': max([v['id'] for v in villages]) + 1 if villages else 1,
        'name': request.form.get('name', ''),
        'section': request.form.get('section', ''),
        'population': int(request.form.get('population', 0)),
        'households': int(request.form.get('households', 0)),
        'martyrs': request.form.get('martyrs', ''),
        'lat': float(request.form.get('lat', 38.28)),
        'lng': float(request.form.get('lng', 45.77)),
        'status': request.form.get('status', 'warning'),
        'capacities': request.form.get('capacities', ''),
        'problems': request.form.get('problems', ''),
        'avg_vote': int(request.form.get('avg_vote', 0)),
        'opponent': request.form.get('opponent', ''),
        'influencers': []
    })
    save_data(villages)
    return redirect(url_for('manage'))

@app.route('/api/delete_village/<int:village_id>')
def delete_village(village_id):
    villages = load_data()
    villages = [v for v in villages if v['id'] != village_id]
    save_data(villages)
    return redirect(url_for('manage'))

@app.route('/api/add_city', methods=['POST'])
def add_city():
    cities = load_cities()
    cities.append({
        'id': max([c['id'] for c in cities]) + 1 if cities else 1,
        'name': request.form.get('city_name', ''),
        'section': request.form.get('section', ''),
        'population': int(request.form.get('population', 0)),
        'description': request.form.get('description', ''),
        'key_people': request.form.get('key_people', '')
    })
    save_cities(cities)
    return redirect(url_for('manage'))

@app.route('/api/add_workgroup', methods=['POST'])
def add_workgroup():
    wgs = load_workgroups()
    wgs.append({
        'id': max([w['id'] for w in wgs]) + 1 if wgs else 1,
        'name': request.form.get('wg_name', ''),
        'section': request.form.get('section', ''),
        'icon': request.form.get('icon', ''),
        'tasks': request.form.get('tasks', ''),
        'members': request.form.get('members', '')
    })
    save_workgroups(wgs)
    return redirect(url_for('manage'))

@app.route('/api/add_influencer', methods=['POST'])
def add_influencer():
    villages = load_data()
    village_name = request.form.get('village_name', '')
    new_inf = {
        'name': request.form.get('name', ''),
        'phone': request.form.get('phone', ''),
        'role': request.form.get('role', ''),
        'status': request.form.get('status', 'مردد'),
        'section': request.form.get('section', ''),
        'city': request.form.get('city', ''),
        'village': request.form.get('village_name', ''),
        'workgroup': request.form.get('workgroup', ''),
        'referrer': request.form.get('referrer', ''),
        'referrer_phone': request.form.get('referrer_phone', ''),
        'last_call_date': '',
        'last_call_result': '',
        'next_call_date': ''
    }
    for v in villages:
        if v['name'] == village_name:
            if 'influencers' not in v:
                v['influencers'] = []
            v['influencers'].append(new_inf)
            save_data(villages)
            break
    return redirect(url_for('manage'))

# ============================================
if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    app.run()
