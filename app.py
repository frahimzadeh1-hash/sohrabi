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
        import requests
        
        village_name = request.form.get('village_name', 'روستای عزیز')
        section = request.form.get('section', 'شبستر')
        martyrs = request.form.get('martyrs', '')
        capacities = request.form.get('capacities', '')
        problems = request.form.get('problems', '')
        key_people = request.form.get('key_people', '')
        opponent = request.form.get('opponent', '')
        
        prompt = f"""یک سخنرانی انتخاباتی حرفه‌ای، احساسی و تأثیرگذار برای دکتر سهرابی کاندیدای نمایندگی شهرستان شبستر به زبان فارسی بنویس.

اطلاعات روستا:
- نام روستا: {village_name}
- بخش: {section}
- شهدا: {martyrs if martyrs else 'ندارد'}
- ظرفیت‌ها: {capacities if capacities else 'در حال تکمیل'}
- مشکلات: {problems if problems else 'در حال تکمیل'}
- افراد حاضر: {key_people if key_people else 'مردم شریف روستا'}
- رقیب: {opponent if opponent else 'ندارد'}

سبک سخنرانی:
- با بسم الله و سلام و درود شروع شود
- یاد شهدا گرامی داشته شود
- به ظرفیت‌های روستا اشاره شود
- مشکلات با همدردی بیان شود
- برنامه‌های عملی دکتر سهرابی ذکر شود
- از رقیب به صورت غیرمستقیم انتقاد شود
- پایان حماسی و امیدوارکننده باشد
- لحن صمیمی، مردمی، متعهد و حرفه‌ای
- حداکثر ۴۰۰ کلمه"""

        speech = ""
        use_ai = request.form.get('use_ai', 'off') == 'on'
        
        if use_ai:
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer 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",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "google/gemini-2.0-flash-001",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 600,
                        "temperature": 0.8
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        speech = result['choices'][0]['message']['content'].strip()
                
                if not speech:
                    use_ai = False
            except Exception as e:
                use_ai = False
        
        if not use_ai or not speech:
            speech = f"""بسم الله الرحمن الرحیم
السلام علیکم و رحمة الله و برکاته
خدمت مردم شریف {village_name} سلام و درود میفرستم.
{f'🏴 یاد شهدای گرانقدر: {martyrs}' if martyrs else ''}
⭐ ظرفیت‌ها: {capacities if capacities else 'در حال تکمیل'}
❌ مشکلات: {problems if problems else 'در حال تکمیل'}
💡 با برنامه و عمل، {village_name} را میسازیم.
دکتر سهرابی - خادم مردم شبستر 🇮🇷"""
        
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
@app.route('/test-ai2')
def test_ai2():
    import requests
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",,
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": "سلام بگو سلام"}],
                "max_tokens": 30
            },
            timeout=20
        )
        return f"Status: {response.status_code}<br>Response: {response.text[:300]}"
    except Exception as e:
        return f"Error: {str(e)}"
# ============================================
if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    app.run()
