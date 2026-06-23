from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sohrabi-campaign-2026'

DATA_FILE = os.path.join('data', 'villages_data.json')
CITIES_FILE = os.path.join('data', 'cities_data.json')
WORKGROUPS_FILE = os.path.join('data', 'workgroups_data.json')

# ============================================
# داده‌های پیش‌فرض
# ============================================
DEFAULT_VILLAGES = [
    {
        'id': 1, 'name': 'اندبیل', 'section': 'مرکزی', 'population': 2400, 'households': 650,
        'martyrs': 'شهید رحیمی، شهید عباس‌زاده', 'lat': 38.2850, 'lng': 45.7750, 'status': 'good',
        'capacities': 'باغات سیب\nچشمه معدنی\nفرش دستباف',
        'problems': 'کمبود آب\nنبود سردخانه\nمهاجرت جوانان', 'avg_vote': 850, 'opponent': 'فلاحی',
        'influencers': [
            {'name': 'حاج رضا محمدی', 'phone': '09141234567', 'role': 'رئیس شورا', 'status': 'موافق', 'section': 'مرکزی', 'city': 'شبستر', 'village': 'اندبیل', 'workgroup': 'کشاورزان', 'referrer': 'خودم', 'referrer_phone': '09140000000', 'last_call_date': '1404/12/15', 'last_call_result': 'قرار ملاقات', 'next_call_date': '1404/12/20'},
            {'name': 'خانم زهرا حسینی', 'phone': '09149876543', 'role': 'مدیر کارگاه فرش', 'status': 'مردد', 'section': 'مرکزی', 'city': 'شبستر', 'village': 'اندبیل', 'workgroup': 'بانوان', 'referrer': 'حاج رضا محمدی', 'referrer_phone': '09141234567', 'last_call_date': '1404/12/10', 'last_call_result': 'نیاز به صحبت', 'next_call_date': '1404/12/18'},
            {'name': 'علی نادری', 'phone': '09365543210', 'role': 'مربی فوتبال', 'status': 'مخالف', 'section': 'مرکزی', 'city': 'شبستر', 'village': 'اندبیل', 'workgroup': 'ورزشکاران', 'referrer': '', 'referrer_phone': '', 'last_call_date': '', 'last_call_result': '', 'next_call_date': ''}
        ]
    },
    {
        'id': 2, 'name': 'تسوج', 'section': 'تسوج', 'population': 8000, 'households': 2200,
        'martyrs': 'شهید قاسمی، شهید اکبری', 'lat': 38.3200, 'lng': 45.3600, 'status': 'warning',
        'capacities': 'باغات زردآلو\nگردشگری آبگرم\nصنایع دستی',
        'problems': 'کمبود صنایع تبدیلی\nمهاجرت تحصیل‌کردگان\nضعف زیرساخت گردشگری', 'avg_vote': 3200, 'opponent': 'فلاحی',
        'influencers': [
            {'name': 'حاج اکبر تسوجی', 'phone': '09141234568', 'role': 'معتمد محلی', 'status': 'موافق', 'section': 'تسوج', 'city': 'تسوج', 'village': 'تسوج', 'workgroup': 'اصناف', 'referrer': 'خودم', 'referrer_phone': '09140000000', 'last_call_date': '1404/12/12', 'last_call_result': 'حامی قطعی', 'next_call_date': '1404/12/22'},
            {'name': 'دکتر امینی', 'phone': '09149876544', 'role': 'پزشک', 'status': 'مردد', 'section': 'تسوج', 'city': 'تسوج', 'village': 'تسوج', 'workgroup': 'فرهنگیان', 'referrer': 'حاج اکبر', 'referrer_phone': '09141234568', 'last_call_date': '', 'last_call_result': '', 'next_call_date': '1404/12/18'}
        ]
    },
    {
        'id': 3, 'name': 'صوفیان', 'section': 'صوفیان', 'population': 10000, 'households': 2800,
        'martyrs': 'شهید رضایی، شهید موسوی', 'lat': 38.2500, 'lng': 45.9800, 'status': 'danger',
        'capacities': 'شهرک صنعتی\nترانزیت ریلی\nتولید مصالح ساختمانی',
        'problems': 'ترافیک سنگین\nآلودگی هوا\nکمبود فضای سبز', 'avg_vote': 4100, 'opponent': 'فلاحی',
        'influencers': [
            {'name': 'مهندس صوفیانی', 'phone': '09141234569', 'role': 'فعال صنعتی', 'status': 'مخالف', 'section': 'صوفیان', 'city': 'صوفیان', 'village': 'صوفیان', 'workgroup': 'اصناف', 'referrer': '', 'referrer_phone': '', 'last_call_date': '', 'last_call_result': '', 'next_call_date': '1404/12/17'},
            {'name': 'حاجیه خانم رضوی', 'phone': '09149876545', 'role': 'خیر', 'status': 'موافق', 'section': 'صوفیان', 'city': 'صوفیان', 'village': 'صوفیان', 'workgroup': 'بانوان', 'referrer': 'خودم', 'referrer_phone': '09140000000', 'last_call_date': '1404/12/14', 'last_call_result': 'حامی مالی', 'next_call_date': ''}
        ]
    },
    {
        'id': 4, 'name': 'شرفخانه', 'section': 'تسوج', 'population': 3500, 'households': 950,
        'martyrs': 'شهید بحری', 'lat': 38.1800, 'lng': 45.4800, 'status': 'danger',
        'capacities': 'بندر شرفخانه\nگردشگری ساحلی\nماهیگیری',
        'problems': 'خشک شدن دریاچه ارومیه\nبیکاری\nنابودی گردشگری', 'avg_vote': 1400, 'opponent': 'فلاحی',
        'influencers': [
            {'name': 'کاپیتان بحری', 'phone': '09141234570', 'role': 'صیاد', 'status': 'موافق', 'section': 'تسوج', 'city': 'شرفخانه', 'village': 'شرفخانه', 'workgroup': 'کشاورزان', 'referrer': 'خودم', 'referrer_phone': '09140000000', 'last_call_date': '1404/12/16', 'last_call_result': 'قرار با صیادان', 'next_call_date': '1404/12/19'}
        ]
    },
    {
        'id': 5, 'name': 'وایقان', 'section': 'مرکزی', 'population': 5000, 'households': 1400,
        'martyrs': 'شهید شیرینی', 'lat': 38.2200, 'lng': 45.7100, 'status': 'good',
        'capacities': 'شهر ملی باسلوق\nشیرینی جات سنگی\nگردشگری غذایی',
        'problems': 'عدم برندسازی جهانی\nمشکلات مواد اولیه\nفاضلاب شهری', 'avg_vote': 2100, 'opponent': 'فلاحی',
        'influencers': [
            {'name': 'استاد کریمی', 'phone': '09141234571', 'role': 'تولیدکننده باسلوق', 'status': 'موافق', 'section': 'مرکزی', 'city': 'وایقان', 'village': 'وایقان', 'workgroup': 'اصناف', 'referrer': 'خودم', 'referrer_phone': '09140000000', 'last_call_date': '1404/12/11', 'last_call_result': 'حامی قطعی', 'next_call_date': ''}
        ]
    }
]

DEFAULT_CITIES = [
    {'id': 1, 'name': 'صوفیان', 'section': 'صوفیان', 'population': 10000, 'description': 'مرکز ترانزیت ریلی و جاده‌ای، شهرک صنعتی', 'key_people': ''},
    {'id': 2, 'name': 'شندآباد', 'section': 'صوفیان', 'population': 4000, 'description': 'شهرک صنعتی خصوصی، تولید پوشاک', 'key_people': ''},
    {'id': 3, 'name': 'شبستر', 'section': 'مرکزی', 'population': 20000, 'description': 'مرکز شهرستان، قطب اداری و دانشگاهی', 'key_people': ''},
    {'id': 4, 'name': 'وایقان', 'section': 'مرکزی', 'population': 5000, 'description': 'شهر ملی باسلوق، قطب شیرینی‌جات سنگی', 'key_people': ''},
    {'id': 5, 'name': 'کوزه‌کنان', 'section': 'مرکزی', 'population': 4500, 'description': 'شهر تاریخی با قدمت ۷ هزار ساله', 'key_people': ''},
    {'id': 6, 'name': 'خامنه', 'section': 'مرکزی', 'population': 3500, 'description': 'باغات وسیع زردآلو و آلبالو', 'key_people': ''},
    {'id': 7, 'name': 'تسوج', 'section': 'تسوج', 'population': 8000, 'description': 'قطب باغات زردآلو و گردو، منطقه گردشگری', 'key_people': ''},
    {'id': 8, 'name': 'شرفخانه', 'section': 'تسوج', 'population': 3500, 'description': 'بندر سابق دریاچه ارومیه', 'key_people': ''},
]

DEFAULT_WORKGROUPS = [
    {'id': 1, 'name': 'بانوان', 'section': 'ستادی', 'icon': '👩‍👧‍👧', 'tasks': 'فعالیت‌های فرهنگی بانوان، اشتغال خانگی، بیمه', 'members': ''},
    {'id': 2, 'name': 'ورزشکاران', 'section': 'ستادی', 'icon': '⚽', 'tasks': 'مسابقات محلی، رفع مشکلات باشگاه‌ها', 'members': ''},
    {'id': 3, 'name': 'طلاب', 'section': 'ستادی', 'icon': '📿', 'tasks': 'ارتباط با مساجد و هیئات مذهبی', 'members': ''},
    {'id': 4, 'name': 'فرهنگیان', 'section': 'ستادی', 'icon': '📚', 'tasks': 'ارتباط با معلمان، برنامه‌های آموزشی', 'members': ''},
    {'id': 5, 'name': 'دانشجویان', 'section': 'ستادی', 'icon': '🎓', 'tasks': 'فضای مجازی، تبلیغات مدرن', 'members': ''},
    {'id': 6, 'name': 'کشاورزان', 'section': 'ستادی', 'icon': '🌾', 'tasks': 'پیگیری بیمه، بازار فروش', 'members': ''},
    {'id': 7, 'name': 'اصناف', 'section': 'ستادی', 'icon': '🏪', 'tasks': 'مشکلات مالیاتی و صنفی', 'members': ''},
    {'id': 8, 'name': 'بازنشستگان', 'section': 'ستادی', 'icon': '👴', 'tasks': 'حقوق و مزایا، برنامه‌های رفاهی', 'members': ''},
    {'id': 9, 'name': 'جوانان', 'section': 'ستادی', 'icon': '💪', 'tasks': 'اشتغال، مسکن، ازدواج', 'members': ''},
]

# ============================================
# توابع کمکی
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
# صفحات اصلی
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
    return render_template('index.html', total_villages=total_villages, total_population=total_population,
                         total_households=total_households, total_avg_vote=total_avg_vote,
                         good=good, warning=warning, danger=danger, sections=sections, villages=villages)

@app.route('/map')
def map_view():
    return render_template('map.html', villages=load_data())

@app.route('/village/<village_name>')
def village_profile(village_name):
    villages = load_data()
    village = next((v for v in villages if v['name'] == village_name), None)
    if village:
        return render_template('village.html', village=village, village_name=village_name)
    return f"<h1>روستای {village_name} یافت نشد</h1>"

@app.route('/speech', methods=['GET', 'POST'])
def generate_speech():
    if request.method == 'POST':
        village_name = request.form.get('village_name', 'روستای عزیز')
        section = request.form.get('section', 'شبستر')
        martyrs = request.form.get('martyrs', '')
        capacities = request.form.get('capacities', '')
        problems = request.form.get('problems', '')
        key_people = request.form.get('key_people', '')
        cap_list = [c.strip() for c in capacities.split('\n') if c.strip()]
        prob_list = [p.strip() for p in problems.split('\n') if p.strip()]
        cap_text = "\n".join([f"        {i}. {cap}" for i, cap in enumerate(cap_list, 1)])
        prob_text = "\n".join([f"        {i}. {prob}" for i, prob in enumerate(prob_list, 1)])
        
        speech = f"""
بسم الله الرحمن الرحیم

السلام علیکم و رحمة الله و برکاته

خدمت تکتک شما مردم شریف، نجیب و بزرگوار روستای {village_name}، سلام و درود میفرستم."""
        
        if martyrs:
            speech += f"""

🏴 یاد و خاطره شهدای گرانقدر این روستا را گرامی میداریم:
{martyrs}
از خداوند متعال برای این عزیزان علو درجات مسئلت داریم."""
        
        speech += f"""

⭐ ظرفیت های بی نظیر {village_name}:
{cap_text if cap_text else "        • نیروی انسانی پرتلاش"}

❌ مشکلاتی که باید حل شوند:
{prob_text if prob_text else "        • کمبود زیرساخت ها"}

💡 برنامه من برای {village_name}:
۱. ایجاد صندوق حمایت از کشاورزان
۲. راه اندازی صنایع تبدیلی
۳. پیگیری ویژه برای حل مشکل آب
۴. حمایت از کسب و کارهای خانگی
۵. ایجاد سامانه اشتغال برای جوانان

🚀 مردم {village_name}، انتخابات پیش رو فقط انتخاب یک نماینده نیست.
دستم را بگیرید تا با هم {village_name} را بسازیم.

با احترام
دکتر سهرابی - خادم مردم شریف شهرستان شبستر 🇮🇷"""
        
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
    villages = load_data()
    cities = load_cities()
    workgroups = load_workgroups()
    return render_template('manage.html', villages=villages, cities=cities, workgroups=workgroups)

@app.route('/war-room')
def war_room():
    villages = load_data()
    opponents = {}
    for v in villages:
        opp = v.get('opponent', 'نامشخص')
        if opp not in opponents:
            opponents[opp] = {'name': opp, 'villages': [], 'total_votes': 0, 'strongholds': 0, 'weak_areas': 0}
        opponents[opp]['villages'].append(v['name'])
        opponents[opp]['total_votes'] += v['avg_vote']
        if v['status'] == 'danger':
            opponents[opp]['strongholds'] += 1
        elif v['status'] == 'warning':
            opponents[opp]['weak_areas'] += 1
    return render_template('war_room.html', opponents=list(opponents.values()), villages=villages)

# ============================================
# API ها
# ============================================
@app.route('/api/villages')
def api_villages():
    return jsonify(load_data())

@app.route('/api/opponent-analysis/<village_name>')
def opponent_analysis(village_name):
    villages = load_data()
    village = next((v for v in villages if v['name'] == village_name), None)
    if village:
        analysis = {
            'village': village['name'], 'opponent': village.get('opponent', 'نامشخص'),
            'status': village['status'],
            'our_strength': 'قوی' if village['status'] == 'good' else 'متوسط' if village['status'] == 'warning' else 'ضعیف',
            'priority': 'پایین' if village['status'] == 'good' else 'متوسط' if village['status'] == 'warning' else 'فوری',
            'recommendation': ''
        }
        if village['status'] == 'good':
            analysis['recommendation'] = 'حفظ وضعیت، تقویت نیروهای حامی'
        elif village['status'] == 'warning':
            analysis['recommendation'] = 'تمرکز بر افراد مردد، جلسات چهره به چهره'
        else:
            analysis['recommendation'] = 'حضور فوری دکتر، استفاده از معتمدین محلی، برنامه ویژه'
        return jsonify(analysis)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/add_village', methods=['POST'])
def add_village():
    villages = load_data()
    new_village = {
        'id': max([v['id'] for v in villages]) + 1 if villages else 1,
        'name': request.form.get('name', ''), 'section': request.form.get('section', ''),
        'population': int(request.form.get('population', 0)),
        'households': int(request.form.get('households', 0)),
        'martyrs': request.form.get('martyrs', ''),
        'lat': float(request.form.get('lat', 38.28)), 'lng': float(request.form.get('lng', 45.77)),
        'status': request.form.get('status', 'warning'),
        'capacities': request.form.get('capacities', ''), 'problems': request.form.get('problems', ''),
        'avg_vote': int(request.form.get('avg_vote', 0)), 'opponent': request.form.get('opponent', ''),
        'influencers': []
    }
    villages.append(new_village)
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
    new_city = {
        'id': max([c['id'] for c in cities]) + 1 if cities else 1,
        'name': request.form.get('city_name', ''),
        'section': request.form.get('section', ''),
        'population': int(request.form.get('population', 0)),
        'description': request.form.get('description', ''),
        'key_people': request.form.get('key_people', '')
    }
    cities.append(new_city)
    save_cities(cities)
    return redirect(url_for('manage'))

@app.route('/api/delete_city/<int:city_id>')
def delete_city(city_id):
    cities = load_cities()
    cities = [c for c in cities if c['id'] != city_id]
    save_cities(cities)
    return redirect(url_for('manage'))

@app.route('/api/add_workgroup', methods=['POST'])
def add_workgroup():
    wgs = load_workgroups()
    new_wg = {
        'id': max([w['id'] for w in wgs]) + 1 if wgs else 1,
        'name': request.form.get('wg_name', ''),
        'section': request.form.get('section', 'ستادی'),
        'icon': request.form.get('icon', '👥'),
        'tasks': request.form.get('tasks', ''),
        'members': request.form.get('members', '')
    }
    wgs.append(new_wg)
    save_workgroups(wgs)
    return redirect(url_for('manage'))

@app.route('/api/delete_workgroup/<int:wg_id>')
def delete_workgroup(wg_id):
    wgs = load_workgroups()
    wgs = [w for w in wgs if w['id'] != wg_id]
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
# اجرا
# ============================================
if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    print("="*60)
    print("🗳️ داشبورد انتخاباتی دکتر سهرابی - شهرستان شبستر")
    print("📍 http://localhost:5000")
    print("📞 http://localhost:5000/contacts")
    print("📝 http://localhost:5000/manage")
    print("🎯 http://localhost:5000/war-room")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)