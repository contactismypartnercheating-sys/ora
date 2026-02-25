#!/usr/bin/env python3
"""
Orastria SAMPLE Book Generator
- Exact same design as full book (navy theme, CREAM pages, same fonts)
- Actual unicode zodiac symbols via DejaVuSans
- All 12 compatibility signs (top 3 visible, 9 properly locked/opaque)
- Hidden Pattern teaser page (mid-sentence cliffhanger)
- CTA page with €7.99, checkout URL, "book in your chosen color" feature
"""

import math
import os
import textwrap
import urllib.request
import random
import requests

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# PROKERALA CONFIG
# ============================================================

PROKERALA_CLIENT_ID     = os.environ.get('PROKERALA_CLIENT_ID', '')
PROKERALA_CLIENT_SECRET = os.environ.get('PROKERALA_CLIENT_SECRET', '')

ZODIAC_SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
                'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
AYANAMSA = 24.0


def get_prokerala_token():
    url  = "https://api.prokerala.com/token"
    data = {'grant_type':'client_credentials',
            'client_id': PROKERALA_CLIENT_ID,
            'client_secret': PROKERALA_CLIENT_SECRET}
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()['access_token']


def longitude_to_tropical_sign(longitude):
    return ZODIAC_SIGNS[int(((longitude + AYANAMSA) % 360) / 30)]


def get_tz_offset(timezone):
    offsets = {
        'Asia/Beirut':'+02:00','America/New_York':'-05:00','America/Chicago':'-06:00',
        'America/Los_Angeles':'-08:00','America/Denver':'-07:00','Europe/London':'+00:00',
        'Europe/Paris':'+01:00','Europe/Berlin':'+01:00','Europe/Rome':'+01:00',
        'Europe/Madrid':'+01:00','Europe/Moscow':'+03:00','Asia/Dubai':'+04:00',
        'Asia/Kolkata':'+05:30','Asia/Shanghai':'+08:00','Asia/Tokyo':'+09:00',
        'Australia/Sydney':'+11:00','Pacific/Auckland':'+13:00','UTC':'+00:00'
    }
    return offsets.get(timezone, '+00:00')


def guess_timezone_from_coords(lat, lon, place_name):
    place_lower = place_name.lower()
    if 'paris' in place_lower or 'france' in place_lower: return 'Europe/Paris'
    if 'london' in place_lower or 'uk' in place_lower:    return 'Europe/London'
    if 'new york' in place_lower:                          return 'America/New_York'
    if 'los angeles' in place_lower:                       return 'America/Los_Angeles'
    if 'chicago' in place_lower:                           return 'America/Chicago'
    if 'dubai' in place_lower or 'uae' in place_lower:    return 'Asia/Dubai'
    if 'tokyo' in place_lower or 'japan' in place_lower:  return 'Asia/Tokyo'
    if 'sydney' in place_lower or 'australia' in place_lower: return 'Australia/Sydney'
    if 'berlin' in place_lower or 'germany' in place_lower: return 'Europe/Berlin'
    if 'moscow' in place_lower or 'russia' in place_lower: return 'Europe/Moscow'
    if 'beijing' in place_lower or 'china' in place_lower: return 'Asia/Shanghai'
    if 'india' in place_lower or 'mumbai' in place_lower or 'delhi' in place_lower: return 'Asia/Kolkata'
    if 'beirut' in place_lower or 'lebanon' in place_lower: return 'Asia/Beirut'
    if lon < -100: return 'America/Los_Angeles'
    elif lon < -60: return 'America/New_York'
    elif lon < 0:   return 'Europe/London'
    elif lon < 30:  return 'Europe/Paris'
    elif lon < 60:  return 'Asia/Dubai'
    elif lon < 100: return 'Asia/Kolkata'
    elif lon < 130: return 'Asia/Shanghai'
    else:           return 'Asia/Tokyo'


def get_timezone_from_coords(lat, lon, place_name):
    try:
        from timezonefinder import TimezoneFinder
        tz = TimezoneFinder().timezone_at(lat=lat, lng=lon)
        if tz: return tz
    except Exception:
        pass
    return guess_timezone_from_coords(lat, lon, place_name)


def geocode_location(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': place_name, 'format': 'json', 'limit': 1}
    r = requests.get(url, params=params, headers={'User-Agent':'OrastriaApp/1.0'}, timeout=30)
    r.raise_for_status()
    results = r.json()
    if not results:
        raise ValueError(f"Could not find location: {place_name}")
    lat = float(results[0]['lat'])
    lon = float(results[0]['lon'])
    return lat, lon, get_timezone_from_coords(lat, lon, place_name)


def parse_chart_data(planet_data, kundli_data):
    chart = {k: 'Aries' for k in ['sun_sign','moon_sign','rising_sign','mercury',
                                    'venus','mars','jupiter','saturn','north_node']}
    name_map = {'Sun':'sun_sign','Moon':'moon_sign','Mercury':'mercury','Venus':'venus',
                'Mars':'mars','Jupiter':'jupiter','Saturn':'saturn',
                'Rahu':'north_node','Ascendant':'rising_sign'}
    for planet in planet_data.get('planet_position', []):
        nm  = planet.get('name', '')
        lon = planet.get('longitude', 0)
        if lon > 0:
            sign = longitude_to_tropical_sign(lon)
        else:
            rasi_id = planet.get('rasi', {}).get('id', -1)
            sign = ZODIAC_SIGNS[(rasi_id + 1) % 12] if 0 <= rasi_id < 12 else 'Aries'
        if nm in name_map:
            chart[name_map[nm]] = sign
    if kundli_data:
        asc_lon = kundli_data.get('ascendant', {}).get('longitude', 0)
        if asc_lon > 0:
            chart['rising_sign'] = longitude_to_tropical_sign(asc_lon)
    return chart


def get_chart_from_prokerala(birth_date, birth_time, birth_place):
    if not PROKERALA_CLIENT_ID or not PROKERALA_CLIENT_SECRET:
        print("⚠️  Prokerala credentials not set")
        return None
    try:
        print(f"📍 Geocoding: {birth_place}")
        lat, lon, tz = geocode_location(birth_place)
        token = get_prokerala_token()
        datetime_str = f"{birth_date}T{birth_time}:00{get_tz_offset(tz)}"
        headers = {"Authorization": f"Bearer {token}"}
        params  = {"ayanamsa": 1, "coordinates": f"{lat},{lon}", "datetime": datetime_str}

        r = requests.get("https://api.prokerala.com/v2/astrology/planet-position",
                         headers=headers, params=params, timeout=30)
        r.raise_for_status()
        planet_data = r.json()['data']

        asc_r = requests.get("https://api.prokerala.com/v2/astrology/kundli",
                              headers=headers, params=params, timeout=30)
        kundli_data = asc_r.json()['data'] if asc_r.ok else None

        chart = parse_chart_data(planet_data, kundli_data)
        print(f"✅ Chart: Sun={chart['sun_sign']}, Moon={chart['moon_sign']}, Rising={chart['rising_sign']}")
        return chart
    except Exception as e:
        print(f"❌ Prokerala error: {e}")
        return None


# ============================================================
# FONT MANAGEMENT (identical to full book)
# ============================================================

FONT_URLS = {
    'Raleway-Regular.ttf':   'https://cdn.jsdelivr.net/fontsource/fonts/raleway@latest/latin-400-normal.ttf',
    'Raleway-Bold.ttf':      'https://cdn.jsdelivr.net/fontsource/fonts/raleway@latest/latin-700-normal.ttf',
    'Raleway-Italic.ttf':    'https://cdn.jsdelivr.net/fontsource/fonts/raleway@latest/latin-400-italic.ttf',
    'EBGaramond-Regular.ttf':'https://cdn.jsdelivr.net/fontsource/fonts/eb-garamond@latest/latin-400-normal.ttf',
    'EBGaramond-Bold.ttf':   'https://cdn.jsdelivr.net/fontsource/fonts/eb-garamond@latest/latin-700-normal.ttf',
    'DejaVuSans.ttf':        'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf',
    'DejaVuSans-Bold.ttf':   'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans-Bold.ttf',
}

def ensure_fonts():
    if os.path.exists('/app'):
        font_dir = '/app/fonts'
    else:
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)

    for font_name, url in FONT_URLS.items():
        font_path = os.path.join(font_dir, font_name)
        if not os.path.exists(font_path):
            try:
                print(f"Downloading {font_name}...")
                urllib.request.urlretrieve(url, font_path)
            except Exception as e:
                print(f"Failed to download {font_name}: {e}")

    registered = {}
    for font_name, font_file in {
        'Raleway':        'Raleway-Regular.ttf',
        'Raleway-Bold':   'Raleway-Bold.ttf',
        'Raleway-Italic': 'Raleway-Italic.ttf',
        'EBGaramond':     'EBGaramond-Regular.ttf',
        'EBGaramond-Bold':'EBGaramond-Bold.ttf',
        'DejaVuSans':     'DejaVuSans.ttf',
        'DejaVuSans-Bold':'DejaVuSans-Bold.ttf',
    }.items():
        fp = os.path.join(font_dir, font_file)
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont(font_name, fp))
                registered[font_name] = True
            except Exception as e:
                print(f"Failed to register {font_name}: {e}")
    return registered

FONTS = ensure_fonts()

FONT_BODY        = 'Raleway'        if 'Raleway'        in FONTS else 'Helvetica'
FONT_BODY_BOLD   = 'Raleway-Bold'   if 'Raleway-Bold'   in FONTS else 'Helvetica-Bold'
FONT_BODY_ITALIC = 'Raleway-Italic' if 'Raleway-Italic' in FONTS else 'Helvetica-Oblique'
FONT_HEADING     = 'EBGaramond'     if 'EBGaramond'     in FONTS else 'Times-Roman'
FONT_HEADING_BOLD= 'EBGaramond-Bold'if 'EBGaramond-Bold'in FONTS else 'Times-Bold'
FONT_SYMBOL      = 'DejaVuSans'     if 'DejaVuSans'     in FONTS else 'Helvetica'
FONT_SYMBOL_BOLD = 'DejaVuSans-Bold'if 'DejaVuSans-Bold'in FONTS else 'Helvetica-Bold'

print(f"Fonts: Body={FONT_BODY}, Heading={FONT_HEADING}, Symbol={FONT_SYMBOL}")

# ============================================================
# COLORS  (identical to full book)
# ============================================================
NAVY      = HexColor('#1a1f3c')
GOLD      = HexColor('#c9a961')
CREAM     = HexColor('#f8f5f0')
SOFT_GOLD = HexColor('#d4b87a')
LIGHT_NAVY= HexColor('#2d3561')
GREEN     = HexColor('#2ecc71')
YELLOW    = HexColor('#f1c40f')
ORANGE    = HexColor('#e67e22')
RED       = HexColor('#e74c3c')
LIGHT_GRAY= HexColor('#ecf0f1')

# ============================================================
# ZODIAC DATA  (identical to full book)
# ============================================================
ZODIAC_SYMBOLS = {
    'Aries':'♈','Taurus':'♉','Gemini':'♊','Cancer':'♋',
    'Leo':'♌','Virgo':'♍','Libra':'♎','Scorpio':'♏',
    'Sagittarius':'♐','Capricorn':'♑','Aquarius':'♒','Pisces':'♓'
}
ZODIAC_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
ZODIAC_DATA = {
    "Aries":      {"element":"Fire",  "modality":"Cardinal","ruler":"Mars",   "crystal":"Carnelian"},
    "Taurus":     {"element":"Earth", "modality":"Fixed",   "ruler":"Venus",  "crystal":"Rose Quartz"},
    "Gemini":     {"element":"Air",   "modality":"Mutable", "ruler":"Mercury","crystal":"Citrine"},
    "Cancer":     {"element":"Water", "modality":"Cardinal","ruler":"Moon",   "crystal":"Moonstone"},
    "Leo":        {"element":"Fire",  "modality":"Fixed",   "ruler":"Sun",    "crystal":"Tiger's Eye"},
    "Virgo":      {"element":"Earth", "modality":"Mutable", "ruler":"Mercury","crystal":"Green Aventurine"},
    "Libra":      {"element":"Air",   "modality":"Cardinal","ruler":"Venus",  "crystal":"Lapis Lazuli"},
    "Scorpio":    {"element":"Water", "modality":"Fixed",   "ruler":"Pluto",  "crystal":"Black Obsidian"},
    "Sagittarius":{"element":"Fire",  "modality":"Mutable", "ruler":"Jupiter","crystal":"Turquoise"},
    "Capricorn":  {"element":"Earth", "modality":"Cardinal","ruler":"Saturn", "crystal":"Garnet"},
    "Aquarius":   {"element":"Air",   "modality":"Fixed",   "ruler":"Uranus", "crystal":"Amethyst"},
    "Pisces":     {"element":"Water", "modality":"Mutable", "ruler":"Neptune","crystal":"Aquamarine"},
}

# ============================================================
# SAMPLE BOOK CONTENT DATA
# ============================================================
ZODIAC_DEEP = {
    'Aries':      {'essence':"You don't just enter a room—you ignite it. Your Aries Sun gives you a warrior's spirit wrapped in impatience. You start things brilliantly. Finishing them? That's where your chart gets complicated. Behind your confidence is someone who genuinely doesn't understand why everyone else hesitates so much.",'hpt':"There's a cycle you keep repeating in relationships that began long before you were aware of it. Your chart reveals a wound around being seen as 'too much'—and how it causes you to"},
    'Taurus':     {'essence':"You're not stubborn—you're certain. Your Taurus Sun gives you an unshakeable core others mistake for inflexibility. You simply know what you want and refuse to apologize for it. Your sensuality runs deeper than pleasure—you experience life through touch, taste, and texture in ways others can't fathom.",'hpt':"Your chart reveals a self-sabotage pattern that activates specifically when you're close to getting what you want. It traces to a core belief about whether you truly deserve"},
    'Gemini':     {'essence':"Your mind never stops—and that's both your superpower and your curse. Your Gemini Sun processes information faster than others can speak. You're not two-faced; you're multi-dimensional. Your constant movement isn't avoidance—it's how you process a world that would overwhelm most people.",'hpt':"There is a specific trigger that causes you to intellectualize your feelings instead of truly feeling them. Your chart shows exactly when this activates—and what you're actually running from when"},
    'Cancer':     {'essence':"You feel everything—and you remember it all. Your Cancer Sun gives you emotional sonar that picks up what others miss entirely. Your shell isn't weakness; it's wisdom from wounds that made you stronger. Your 'moodiness' is actually you processing everyone's emotions in the room, not just your own.",'hpt':"Your chart reveals a giving pattern that secretly keeps people at a distance. When you nurture others compulsively, it's actually a way of avoiding the vulnerability of asking for what"},
    'Leo':        {'essence':"You're not seeking attention—you're radiating energy you can't contain. Your Leo Sun makes you impossible to ignore, and honestly, why would you want to be? You were born to be seen. Your need for appreciation isn't ego—it's a genuine desire to know your warmth actually reaches others.",'hpt':"Your chart shows a pattern of shrinking yourself for people who can't hold your light—then resenting them for it. The root of this traces back to your earliest experience of being told"},
    'Virgo':      {'essence':"Your mind is a precision instrument that notices what others overlook. Your Virgo Sun isn't critical—it's discerning. You see potential everywhere, including all the ways things could be better. Your criticism of others is nothing compared to the relentless standards you hold yourself to.",'hpt':"Your chart reveals a specific anxiety trigger that activates when things feel out of control. Your perfectionism is actually a protection mechanism built to guard against the deep fear of being"},
    'Libra':      {'essence':"You see both sides of everything—which is why deciding feels impossible. Your Libra Sun craves harmony so deeply that conflict feels like physical pain. You're not indecisive; you're comprehensive. Your people-pleasing isn't weakness—it's a sophisticated strategy to maintain the peace you desperately need.",'hpt':"There is a deeply buried resentment your chart reveals—one that builds silently because you consistently choose harmony over honesty. The pattern activates whenever someone asks you to"},
    'Scorpio':    {'essence':"You don't do surface-level anything. Your Scorpio Sun experiences life at depths others find terrifying. You're not intense—you're fully alive while others sleepwalk through existence. Your suspicion isn't paranoia—you simply see the shadows others pretend don't exist.",'hpt':"Your chart reveals a self-protective pattern that ironically creates the very abandonment you fear. It begins the moment you start to truly trust someone—your chart shows exactly how you"},
    'Sagittarius':{'essence':"You're allergic to limitation in all its forms. Your Sagittarius Sun needs freedom like others need air. You're not commitment-phobic—you just refuse to shrink yourself to fit small spaces. Your bluntness isn't cruelty—you genuinely believe the truth sets people free.",'hpt':"Your chart shows a pattern of pursuing freedom as a way of avoiding a specific type of intimacy that feels genuinely dangerous to you. The fear underneath all of this traces back to"},
    'Capricorn':  {'essence':"You're playing a longer game than anyone realizes. Your Capricorn Sun makes you ancient beyond your years—you were born knowing life is hard and decided to become harder. Your coldness is protection—underneath that armor is someone who feels deeply but can't afford to show it.",'hpt':"Your chart reveals a deeply buried grief about joy—a belief that you aren't allowed to rest, play, or want things simply for pleasure. This pattern began when you learned that love was"},
    'Aquarius':   {'essence':"You're living in a future others haven't imagined yet. Your Aquarius Sun makes you feel like an alien—because you're here to change things, not fit in. Your detachment isn't lack of feeling—it's how you survive feeling connected to all of humanity at once.",'hpt':"There is a paradox in your chart: you crave deep connection but unconsciously create distance the moment you begin to feel it. The trigger for this pattern is something that happened when"},
    'Pisces':     {'essence':"You absorb emotions like a sponge—sometimes not knowing where others end and you begin. Your Pisces Sun connects you to something beyond the visible world. Your escapism isn't weakness—it's survival in a world that feels unbearably harsh to your unfiltered soul.",'hpt':"Your chart shows a deep longing for a love that dissolves the self completely—and a pattern of attracting partners who take advantage of exactly that openness. The wound at the root is"},
}

MOON_DEEP = {
    'Aries':      {'essence':"Your emotional responses are instant and fierce. You process feelings by taking action—sitting with emotions feels unbearable.",'needs':["Freedom to express anger","Action over discussion","Independence","A partner who can handle intensity"],'pattern':"You fall fast, burn hot, and move on—not from lack of depth, but because your heart processes at lightning speed."},
    'Taurus':     {'essence':"Your emotions move like honey—slowly, sweetly, and with staying power. Once you feel something, it takes root.",'needs':["Physical affection and touch","Financial security","Routine and predictability","Beauty in your environment"],'pattern':"You're the person who replays the same song when sad, craves comfort when stressed, and stays loyal long past expiration dates."},
    'Gemini':     {'essence':"You process emotions by talking them out—sometimes with others, sometimes just with yourself.",'needs':["Mental stimulation always","Variety in emotional expression","A partner who talks through everything","Space to change your mind"],'pattern':"You can rationalize any feeling until it almost disappears—which is both your superpower and your avoidance strategy."},
    'Cancer':     {'essence':"Your emotional world is oceanic—deep, tidal, and full of currents no one else can see.",'needs':["A safe home base","Emotional reciprocity","Permission to nurture","Connection to chosen family"],'pattern':"You remember every emotional moment—not from bitterness, but because your heart literally cannot forget how things felt."},
    'Leo':        {'essence':"Your emotions want an audience—not for validation, but because feelings this big deserve to be witnessed.",'needs':["Appreciation and admiration","Creative emotional outlets","Loyalty from your inner circle","Grand gestures of love"],'pattern':"When hurt, you either roar or retreat into dignified silence—there's no in-between for a wounded Leo Moon."},
    'Virgo':      {'essence':"You process emotions by analyzing them, categorizing them, and figuring out how to fix them.",'needs':["Order and routine","Feeling useful to others","Health and wellness practices","A partner who appreciates your help"],'pattern':"You show love through acts of service, then feel invisible when others don't notice the thousand small things you do."},
    'Libra':      {'essence':"Your emotional wellbeing is tied to harmony around you. Discord hits you physically.",'needs':["Partnership above all","Beauty and aesthetics","Peaceful environments","Feeling chosen and valued"],'pattern':"You suppress your needs to keep the peace, then quietly resent others for not reading your mind."},
    'Scorpio':    {'essence':"Your emotions run to depths that would terrify most people. You don't just feel sad—you plunge into the underworld of grief.",'needs':["Absolute emotional honesty","Privacy for processing","Intense intimate connection","Power over your own life"],'pattern':"You test people's loyalty before letting them close, pushing to see who'll fight to stay."},
    'Sagittarius':{'essence':"You process emotions by finding their meaning—every feeling must lead to wisdom, growth, or a good story.",'needs':["Freedom from emotional obligation","Adventure and new experiences","Philosophical understanding","A partner who grows with you"],'pattern':"You escape difficult emotions through movement, humor, or philosophy—sitting with discomfort feels like death."},
    'Capricorn':  {'essence':"Your emotions are disciplined, controlled, and often postponed for more convenient times.",'needs':["Respect and recognition","Achievement and progress","Stability in relationships","Time to process privately"],'pattern':"You struggle to access feelings in real-time, processing them days or even years later when it finally feels safe."},
    'Aquarius':   {'essence':"You intellectualize emotions to survive them. Feelings are fascinating phenomena to observe—from a safe distance.",'needs':["Space and independence","Intellectual connection","Freedom to be unconventional","Friends who feel like chosen family"],'pattern':"You care deeply about humanity but struggle with one-on-one emotional intimacy."},
    'Pisces':     {'essence':"Your emotional boundaries are permeable—you feel everything around you, absorbing others' pain and joy alike.",'needs':["Alone time to decompress","Creative and spiritual outlets","Gentle, non-judgmental love","Escape hatches from harsh reality"],'pattern':"You'd rather suffer in silence than burden others, then wonder why no one comes to rescue you."},
}

VENUS_STYLES = {
    'Aries':      "You love like a conquest—the chase is intoxicating, but keeping fire alive after you've 'won' is your real challenge.",
    'Taurus':     "You love through devotion and physical presence. For you, real love is showing up consistently, building something lasting.",
    'Gemini':     "You love through conversation and intellectual flirtation. A partner who bores you mentally will lose you.",
    'Cancer':     "You love by nurturing and creating emotional sanctuary. Your love is protective, always deeply felt.",
    'Leo':        "You love grandly and expect to be adored in return. Love should feel like being chosen above all others.",
    'Virgo':      "You love through acts of service and attention to detail. You show devotion by noticing what others need.",
    'Libra':      "You love through partnership and romance. You need a plus-one for life—someone who completes you.",
    'Scorpio':    "You love with volcanic intensity. Casual isn't in your vocabulary—you want soul-merging depth or nothing.",
    'Sagittarius':"You love through shared adventure and growth. A partner who clips your wings will lose you.",
    'Capricorn':  "You love by building—a life, a legacy, a future. Your devotion shows through commitment, not poetry.",
    'Aquarius':   "You love from a slight distance—intimacy without possessiveness. You need a partner who's also a best friend.",
    'Pisces':     "You love transcendently, seeing your partner's soul more than their flaws. The danger is loving potential over reality.",
}

# Base compatibility scores
COMPAT_SCORES = {
    'Aries':      [('Leo',94),('Sagittarius',91),('Aquarius',85),('Gemini',82),('Libra',78),('Scorpio',74),('Capricorn',70),('Virgo',68),('Pisces',65),('Cancer',60),('Taurus',58)],
    'Taurus':     [('Cancer',93),('Virgo',90),('Capricorn',88),('Pisces',83),('Scorpio',80),('Libra',75),('Gemini',68),('Leo',65),('Aquarius',62),('Sagittarius',56),('Aries',54)],
    'Gemini':     [('Libra',92),('Aquarius',90),('Aries',84),('Leo',80),('Sagittarius',76),('Virgo',68),('Cancer',60),('Taurus',58),('Scorpio',55),('Capricorn',53),('Pisces',52)],
    'Cancer':     [('Scorpio',95),('Pisces',93),('Taurus',89),('Virgo',82),('Capricorn',78),('Libra',70),('Leo',68),('Gemini',60),('Aries',57),('Aquarius',52),('Sagittarius',50)],
    'Leo':        [('Aries',94),('Sagittarius',91),('Libra',87),('Gemini',80),('Aquarius',75),('Capricorn',67),('Cancer',65),('Taurus',63),('Scorpio',62),('Virgo',60),('Pisces',58)],
    'Virgo':      [('Taurus',91),('Capricorn',90),('Cancer',86),('Scorpio',80),('Pisces',76),('Gemini',68),('Leo',62),('Libra',62),('Aries',57),('Aquarius',55),('Sagittarius',52)],
    'Libra':      [('Gemini',92),('Aquarius',89),('Leo',87),('Sagittarius',81),('Taurus',75),('Cancer',70),('Aries',68),('Virgo',65),('Scorpio',62),('Capricorn',60),('Pisces',58)],
    'Scorpio':    [('Cancer',95),('Pisces',93),('Capricorn',85),('Virgo',80),('Taurus',78),('Leo',65),('Aries',63),('Libra',60),('Gemini',58),('Aquarius',52),('Sagittarius',50)],
    'Sagittarius':[('Aries',91),('Leo',90),('Aquarius',88),('Libra',81),('Gemini',76),('Pisces',65),('Capricorn',60),('Taurus',56),('Virgo',54),('Cancer',52),('Scorpio',50)],
    'Capricorn':  [('Taurus',92),('Virgo',90),('Scorpio',85),('Pisces',78),('Cancer',76),('Aquarius',70),('Leo',67),('Sagittarius',62),('Libra',60),('Gemini',58),('Aries',55)],
    'Aquarius':   [('Gemini',92),('Libra',89),('Sagittarius',88),('Aries',85),('Leo',75),('Capricorn',70),('Pisces',65),('Virgo',60),('Taurus',58),('Scorpio',52),('Cancer',50)],
    'Pisces':     [('Cancer',95),('Scorpio',93),('Taurus',86),('Capricorn',78),('Virgo',76),('Sagittarius',65),('Aquarius',63),('Aries',60),('Leo',58),('Libra',56),('Gemini',54)],
}

COMPAT_LABELS = {
    (94,100):"Soulmate Energy",(88,93):"Deep Connection",(80,87):"Strong Match",
    (70,79):"Good Potential",(60,69):"Interesting Dynamic",(0,59):"Growth Opportunity"
}

def compat_label(score):
    for (lo,hi), label in COMPAT_LABELS.items():
        if lo <= score <= hi: return label
    return "Unique Dynamic"

def get_compatibility(sun_sign):
    scores = COMPAT_SCORES.get(sun_sign, [])
    seen = {s: sc for s, sc in scores}
    result = []
    for s, sc in scores:
        result.append((s, sc, compat_label(sc)))
    for s in ZODIAC_ORDER:
        if s != sun_sign and s not in seen:
            result.append((s, 55, "Unique Dynamic"))
    return result[:11]

def get_compat_color(pct):
    if pct >= 80: return GREEN
    elif pct >= 65: return YELLOW
    elif pct >= 50: return ORANGE
    return RED


# ============================================================
# SAMPLE BOOK CLASS
# ============================================================

class OrastriaBookGenerator:
    def __init__(self, output_path, person_data, quiz_data=None, book_type='sample', user_id=None):
        self.output_path = output_path
        self.person = person_data
        self.quiz   = quiz_data or {}
        self.width, self.height = letter
        self.margin = 0.75 * inch
        self.page_num = 0
        self.c = canvas.Canvas(output_path, pagesize=letter)

        # person fields — always capitalize
        raw_name        = person_data.get('name', 'Friend')
        self.name       = raw_name.title()
        self.first_name = self.name.split()[0]
        self.sun_sign   = person_data.get('sun_sign',   'Aries')
        self.moon_sign  = person_data.get('moon_sign',  'Aries')
        self.rising_sign= person_data.get('rising_sign','Aries')

        # Try to fetch full chart from Prokerala (same as full book)
        birth_date  = person_data.get('birth_date', '')
        birth_time  = person_data.get('birth_time', '12:00')
        birth_place = person_data.get('birth_place', '')

        # Normalise AM/PM time to 24h
        time_period = person_data.get('birth_time_period', '').upper()
        if time_period == 'PM' and ':' in birth_time:
            parts = birth_time.split(':')
            h = int(parts[0])
            if h != 12: h += 12
            birth_time = f"{h:02d}:{parts[1]}"
        elif time_period == 'AM' and ':' in birth_time:
            parts = birth_time.split(':')
            h = int(parts[0])
            if h == 12: h = 0
            birth_time = f"{h:02d}:{parts[1]}"

        chart = None
        if birth_date and birth_place:
            chart = get_chart_from_prokerala(birth_date, birth_time, birth_place)

        if chart:
            # Prokerala gives us everything — override whatever was passed in
            self.sun_sign    = chart.get('sun_sign',    self.sun_sign)
            self.moon_sign   = chart.get('moon_sign',   self.moon_sign)
            self.rising_sign = chart.get('rising_sign', self.rising_sign)
            # Merge into person_data so the planet table picks it up
            for key in ('mercury','venus','mars','jupiter','saturn','north_node'):
                person_data[key] = chart.get(key, person_data.get(key, ''))
        else:
            print("⚠️  Using chart data from person_data (no Prokerala)")

        # checkout
        uid = (user_id or '').strip()
        self.checkout_url = (f"http://tarot.orastria.com/book-checkout/?uid={uid}"
                             if uid else "http://tarot.orastria.com/book-checkout/")

        # format birth date
        bd = person_data.get('birth_date', '')
        if '-' in bd:
            parts = bd.split('-')
            months = ["","January","February","March","April","May","June",
                      "July","August","September","October","November","December"]
            try:
                self.birth_date_fmt = f"{months[int(parts[1])]} {int(parts[2])}, {parts[0]}"
            except:
                self.birth_date_fmt = bd
        else:
            self.birth_date_fmt = bd

    # ── page helpers (identical to full book) ───────────────────

    def new_page(self):
        self.page_num += 1
        c = self.c
        c.setFillColor(CREAM)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL, 10)
        c.drawCentredString(50, self.height - 50, '✦')
        c.drawCentredString(self.width - 50, self.height - 50, '✦')
        c.drawCentredString(50, 50, '✦')
        c.drawCentredString(self.width - 50, 50, '✦')
        c.setFillColor(NAVY)
        c.setFont(FONT_BODY, 10)
        c.drawCentredString(self.width/2, 30, f"— {self.page_num} —")
        return self.height - 80

    def draw_section_title(self, text, y):
        c = self.c
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 18)
        c.drawString(self.margin, y, text)
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.line(self.margin, y - 5, self.margin + 60, y - 5)
        return y - 35

    def draw_text(self, text, y, width=None, color=None):
        if not text:
            return y
        c = self.c
        c.setFillColor(color or NAVY)
        c.setFont(FONT_BODY, 11)
        if width is None:
            width = self.width - 2 * self.margin
        wrapper = textwrap.TextWrapper(width=int(width / 5.5))
        paragraphs = text.split('\n\n') if '\n\n' in text else text.split('\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            for line in wrapper.wrap(para):
                if y < self.margin + 50:
                    self.c.showPage()
                    y = self.new_page()
                    c.setFillColor(color or NAVY)
                    c.setFont(FONT_BODY, 11)
                c.drawString(self.margin, y, line)
                y -= 16
            y -= 8
        return y

    def draw_key_insight_box(self, title, points, y):
        c = self.c
        if y < self.margin + 150:
            c.showPage()
            y = self.new_page()
        box_height = 30 + len(points) * 22
        c.setFillColor(NAVY)
        c.roundRect(self.margin, y - box_height + 10, self.width - 2*self.margin, box_height, 8, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(self.margin + 15, y - 5, f"✧ {title}")
        c.setFillColor(white)
        c.setFont(FONT_BODY, 10)
        py = y - 28
        for pt in points:
            c.drawString(self.margin + 25, py, f"• {pt[:80]}")
            py -= 20
        return y - box_height - 15

    def draw_pull_quote(self, quote, y):
        c = self.c
        if y < self.margin + 100:
            c.showPage()
            y = self.new_page()
        box_h = 80
        c.setFillColor(HexColor('#f8f5f0'))
        c.roundRect(self.margin + 20, y - box_h + 20, self.width - 2*self.margin - 40, box_h, 8, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(self.margin + 20, y - box_h + 20, 4, box_h, fill=1, stroke=0)
        c.setFont(FONT_HEADING_BOLD, 36)
        c.setFillColor(SOFT_GOLD)
        c.drawString(self.margin + 35, y - 5, '"')
        c.setFillColor(NAVY)
        c.setFont(FONT_BODY_ITALIC, 11)
        wrapper = textwrap.TextWrapper(width=70)
        quote_y = y - 25
        for line in wrapper.wrap(quote)[:3]:
            c.drawString(self.margin + 50, quote_y, line)
            quote_y -= 16
        return y - box_h - 20

    # ── PAGE 1: COVER  (identical to full book) ─────────────────

    def draw_cover(self):
        c = self.c
        c.setFillColor(NAVY)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

        # double border
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.rect(0.4*inch, 0.4*inch, self.width - 0.8*inch, self.height - 0.8*inch)
        c.setLineWidth(1)
        c.rect(0.5*inch, 0.5*inch, self.width - 1*inch, self.height - 1*inch)

        # corner symbols
        c.setFont(FONT_SYMBOL_BOLD, 24)
        c.setFillColor(GOLD)
        c.drawCentredString(0.8*inch, self.height - 0.8*inch, '☉')
        c.drawCentredString(self.width - 0.8*inch, self.height - 0.8*inch, '☽')

        # title
        c.setFont(FONT_HEADING_BOLD, 36)
        c.drawCentredString(self.width/2, self.height - 1.8*inch, "YOUR COSMIC")
        c.drawCentredString(self.width/2, self.height - 2.3*inch, "BLUEPRINT")

        c.setLineWidth(1)
        c.setStrokeColor(GOLD)
        c.line(2*inch, self.height - 2.55*inch, self.width - 2*inch, self.height - 2.55*inch)

        # name
        c.setFillColor(white)
        c.setFont(FONT_HEADING_BOLD, 28)
        c.drawCentredString(self.width/2, self.height - 3.2*inch, self.name)

        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY, 12)
        bt = f"{self.person.get('birth_time','')} {self.person.get('birth_time_period','')}".strip()
        c.drawCentredString(self.width/2, self.height - 3.6*inch, f"{self.birth_date_fmt}  •  {bt}")
        c.drawCentredString(self.width/2, self.height - 3.85*inch, self.person.get('birth_place',''))

        # center zodiac circle
        center_y = self.height / 2 - 0.3*inch
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, center_y, 85)
        c.setLineWidth(1)
        c.circle(self.width/2, center_y, 95)

        # BIG zodiac symbol (actual unicode, NOT abbreviation)
        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL_BOLD, 72)
        c.drawCentredString(self.width/2, center_y - 15, ZODIAC_SYMBOLS.get(self.sun_sign, '★'))

        # sign name
        c.setFont(FONT_HEADING_BOLD, 18)
        c.drawCentredString(self.width/2, center_y - 60, self.sun_sign.upper())

        # big three line
        c.setFont(FONT_SYMBOL, 11)
        c.setFillColor(white)
        big3 = f"☉ Sun: {self.sun_sign}  •  ☽ Moon: {self.moon_sign}  •  ↑ Rising: {self.rising_sign}"
        c.drawCentredString(self.width/2, center_y - 115, big3)

        # branding
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 22)
        c.drawCentredString(self.width/2, 1.3*inch, "ORASTRIA")
        c.setFont(FONT_BODY, 10)
        c.drawCentredString(self.width/2, 1.0*inch, "Personalized Astrology  •  Written in the Stars")

        c.setFont(FONT_SYMBOL, 16)
        c.drawCentredString(0.8*inch, 0.8*inch, '☽')
        c.drawCentredString(self.width - 0.8*inch, 0.8*inch, '☽')

        c.showPage()

    # ── PAGE 2: BIRTH CHART WHEEL  (identical to full book) ─────

    def draw_birth_chart_page(self):
        y = self.new_page()
        c = self.c

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 24)
        c.drawCentredString(self.width/2, self.height - 100, "Your Birth Chart")
        c.setFillColor(HexColor('#666666'))
        c.setFont(FONT_BODY_ITALIC, 12)
        c.drawCentredString(self.width/2, self.height - 125, "A snapshot of the heavens at the moment you were born")

        cx = self.width / 2
        cy = self.height / 2 + 0.5*inch

        # rings
        c.setStrokeColor(NAVY)
        c.setLineWidth(2)
        c.circle(cx, cy, 140)
        c.setLineWidth(1)
        c.circle(cx, cy, 110)
        c.circle(cx, cy, 60)

        # house lines
        c.setStrokeColor(HexColor('#cccccc'))
        c.setLineWidth(0.5)
        for i in range(12):
            angle = (90 - i * 30) * math.pi / 180
            c.line(cx + 60*math.cos(angle), cy + 60*math.sin(angle),
                   cx + 140*math.cos(angle), cy + 140*math.sin(angle))

        # zodiac signs around wheel — actual symbols, not abbreviations
        for i, sign in enumerate(ZODIAC_ORDER):
            angle = (75 - i * 30) * math.pi / 180
            x = cx + 125 * math.cos(angle)
            y2 = cy + 125 * math.sin(angle)
            if sign == self.sun_sign:
                c.setFillColor(GOLD)
            elif sign == self.moon_sign:
                c.setFillColor(HexColor('#8899AA'))
            elif sign == self.rising_sign:
                c.setFillColor(HexColor('#AA7755'))
            else:
                c.setFillColor(NAVY)
            c.setFont(FONT_SYMBOL_BOLD, 14)
            c.drawCentredString(x, y2 - 5, ZODIAC_SYMBOLS.get(sign, '★'))

        # center
        c.setFillColor(HexColor('#faf8f5'))
        c.circle(cx, cy, 55, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.circle(cx, cy, 45)

        c.setStrokeColor(GOLD); c.setLineWidth(1.5)
        c.circle(cx - 18, cy + 8, 14, fill=0, stroke=1)
        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL_BOLD, 18)
        c.drawCentredString(cx - 18, cy + 3, '☉')

        c.setStrokeColor(HexColor('#7788AA')); c.setLineWidth(1.5)
        c.circle(cx + 18, cy + 8, 14, fill=0, stroke=1)
        c.setFillColor(HexColor('#7788AA'))
        c.setFont(FONT_SYMBOL_BOLD, 18)
        c.drawCentredString(cx + 18, cy + 3, '☽')

        c.setFillColor(NAVY)
        c.setFont(FONT_BODY_BOLD, 9)
        c.drawCentredString(cx, cy - 22,
            f"{self.sun_sign[:3]} / {self.moon_sign[:3]} / {self.rising_sign[:3]}")

        # planet table
        y_table = 2.8*inch
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 14)
        c.drawCentredString(self.width/2, y_table + 0.4*inch, "Your Planetary Positions")

        table_w = 5*inch
        table_x = (self.width - table_w) / 2
        c.setFillColor(CREAM)
        c.roundRect(table_x, y_table - 1.6*inch, table_w, 1.8*inch, 5, fill=1, stroke=0)

        planets_raw = [
            ("☉","Sun",       self.sun_sign),
            ("☽","Moon",      self.moon_sign),
            ("↑","Rising",    self.rising_sign),
            ("☿","Mercury",   self.person.get('mercury','')),
            ("♀","Venus",     self.person.get('venus','')),
            ("♂","Mars",      self.person.get('mars','')),
            ("♃","Jupiter",   self.person.get('jupiter','')),
            ("♄","Saturn",    self.person.get('saturn','')),
            ("MC","Midheaven",self.person.get('midheaven','')),
            ("☊","North Node",self.person.get('north_node','')),
        ]
        # Only show rows where we actually have data
        planets = [(s, n, v) for s, n, v in planets_raw if v and v.lower() not in ('', 'unknown')]
        col1_x = table_x + 20
        col2_x = table_x + table_w/2 + 20
        for i, (sym, nm, sign) in enumerate(planets):
            x = col1_x if i < 5 else col2_x
            row_y = y_table - (i % 5) * 0.3*inch
            c.setFillColor(GOLD); c.setFont(FONT_SYMBOL, 12); c.drawString(x, row_y, sym)
            c.setFillColor(NAVY); c.setFont(FONT_BODY, 10); c.drawString(x + 25, row_y, nm)
            c.setFillColor(HexColor('#444444')); c.drawString(x + 90, row_y, sign)

        c.showPage()

    # ── PAGE 3: INTRO ────────────────────────────────────────────

    def draw_intro_page(self):
        y = self.new_page()
        c = self.c

        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL, 24)
        c.drawCentredString(self.width/2, y, '✧')
        y -= 40

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 26)
        c.drawCentredString(self.width/2, y, "Your Cosmic Journey Begins")
        y -= 15

        c.setStrokeColor(GOLD); c.setLineWidth(1.5)
        c.line(self.width/2 - 80, y, self.width/2 + 80, y)
        y -= 30

        bd = self.birth_date_fmt
        bt = f"{self.person.get('birth_time','')} {self.person.get('birth_time_period','')}".strip()
        bp = self.person.get('birth_place','')

        intro = (
            f"Dear {self.first_name},\n\n"
            f"On {bd}, at {bt} in {bp}, something extraordinary happened. "
            f"The cosmos paused. Every planet aligned in a configuration that had never "
            f"existed before in the 13.8 billion year history of the universe—and will never exist again.\n\n"
            f"That moment was yours. Only yours.\n\n"
            f"This isn't a generic horoscope. This is your cosmic DNA—calculated to the exact "
            f"minute and location of your birth, analyzed through your unique planetary positions, "
            f"and written specifically for you.\n\n"
            f"What you're about to read may feel uncomfortably accurate. That's by design. "
            f"Your {self.sun_sign} Sun, {self.moon_sign} Moon, and {self.rising_sign} Rising "
            f"create a combination that fewer than 0.3% of people share—making you genuinely rare."
        )
        y = self.draw_section_title(f"Welcome, {self.first_name}", y)
        y = self.draw_text(intro, y)
        c.showPage()

    # ── PAGE 4: BIG THREE ────────────────────────────────────────

    def draw_big_three_page(self):
        y = self.new_page()
        c = self.c

        # Chapter icon
        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL_BOLD, 48)
        c.drawCentredString(self.width/2, y, '☉')
        y -= 55

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 28)
        c.drawCentredString(self.width/2, y, "Your Big Three")
        y -= 20

        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY_ITALIC, 13)
        c.drawCentredString(self.width/2, y, "Sun, Moon & Rising — the foundation of who you are")
        y -= 30

        c.setStrokeColor(GOLD); c.setLineWidth(1)
        c.line(self.width/2 - 60, y, self.width/2 + 60, y)
        y -= 30

        # 3-column cards
        placements = [
            ('☉','SUN',   self.sun_sign,   'Your Core Self',   'Who you are at center'),
            ('☽','MOON',  self.moon_sign,  'Your Inner World', 'How you feel & process'),
            ('↑','RISING',self.rising_sign,'Your Outer Mask',  'How the world sees you'),
        ]
        cw = (self.width - 2*self.margin) / 3
        card_h = 1.85*inch
        card_y = y - card_h

        for i, (sym, lbl, sign, d1, d2) in enumerate(placements):
            cx2 = self.margin + cw/2 + i * cw
            card_x = self.margin + i * cw

            c.setFillColor(NAVY)
            c.roundRect(card_x + 4, card_y, cw - 12, card_h, 8, fill=1, stroke=0)

            c.setFillColor(GOLD)
            c.setFont(FONT_SYMBOL_BOLD, 28)
            c.drawCentredString(cx2, card_y + card_h - 0.45*inch, sym)

            c.setFillColor(HexColor('#888888'))
            c.setFont(FONT_BODY, 9)
            c.drawCentredString(cx2, card_y + card_h - 0.72*inch, lbl)

            # actual zodiac symbol + sign name
            c.setFillColor(GOLD)
            c.setFont(FONT_SYMBOL_BOLD, 26)
            c.drawCentredString(cx2, card_y + card_h - 1.08*inch, ZODIAC_SYMBOLS.get(sign,'★'))

            c.setFillColor(white)
            c.setFont(FONT_BODY_BOLD, 12)
            c.drawCentredString(cx2, card_y + card_h - 1.38*inch, sign)

            c.setFillColor(HexColor('#aaaacc'))
            c.setFont(FONT_BODY, 8)
            c.drawCentredString(cx2, card_y + card_h - 1.6*inch, d1)
            c.setFont(FONT_BODY, 7)
            c.drawCentredString(cx2, card_y + card_h - 1.76*inch, d2)

        y = card_y - 0.25*inch

        # summary insight box
        sun_d  = ZODIAC_DEEP.get(self.sun_sign, {})
        moon_d = MOON_DEEP.get(self.moon_sign, {})
        essence = sun_d.get('essence', '')
        # Use first sentence only for the insight box — clean cut
        first_sentence = essence.split('.')[0] + '.' if '.' in essence else essence[:100]
        moon_pattern = moon_d.get('pattern', '')
        moon_sentence = moon_pattern.split('.')[0] + '.' if '.' in moon_pattern else moon_pattern[:100]
        y = self.draw_key_insight_box(
            f"What This Means For You, {self.first_name.upper()}",
            [f"Sun in {self.sun_sign}: {first_sentence[:85]}",
             f"Moon in {self.moon_sign}: {moon_sentence[:85]}"],
            y)

        c.showPage()

    # ── PAGE 5: SUN SIGN ─────────────────────────────────────────

    def draw_sun_page(self):
        y = self.new_page()
        c = self.c

        # big actual zodiac symbol
        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL_BOLD, 48)
        c.drawCentredString(self.width/2, y, ZODIAC_SYMBOLS.get(self.sun_sign,'★'))
        y -= 50

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 22)
        c.drawCentredString(self.width/2, y, f"Your Sun in {self.sun_sign}")
        y -= 35

        sun_d = ZODIAC_DEEP.get(self.sun_sign, {})
        essence = sun_d.get('essence', f"As a {self.sun_sign}, you possess unique gifts the world needs.")
        y = self.draw_text(essence, y)
        y -= 10

        # element / ruler / modality info box
        zd = ZODIAC_DATA.get(self.sun_sign, {})
        y = self.draw_key_insight_box(
            f"{self.sun_sign} at a Glance",
            [f"Element: {zd.get('element','?')}  •  Modality: {zd.get('modality','?')}",
             f"Ruler: {zd.get('ruler','?')}  •  Power Crystal: {zd.get('crystal','?')}"],
            y)
        y -= 10

        # relationship pattern
        pattern_text = f"In relationships, your {self.sun_sign} energy shows up like this: {sun_d.get('essence','')[:100]}..."
        y = self.draw_section_title("Your Relationship Pattern", y)
        y = self.draw_text(pattern_text, y)

        # teaser for hidden pattern
        c.setFillColor(HexColor('#888888'))
        c.setFont(FONT_BODY_ITALIC, 9)
        c.drawString(self.margin, y - 10,
            "◆  Your deeper pattern is revealed on the next page...")

        c.showPage()

    # ── PAGE 6: MOON SIGN ────────────────────────────────────────

    def draw_moon_page(self):
        y = self.new_page()
        c = self.c

        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL_BOLD, 48)
        c.drawCentredString(self.width/2, y, '☽')
        y -= 50

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 22)
        c.drawCentredString(self.width/2, y, f"Your Moon in {self.moon_sign}")
        y -= 35

        moon_d = MOON_DEEP.get(self.moon_sign, {})
        y = self.draw_text(moon_d.get('essence', ''), y)
        y -= 5
        y = self.draw_text(moon_d.get('pattern', ''), y)
        y -= 10

        y = self.draw_key_insight_box(
            f"What Your {self.moon_sign} Moon Needs",
            moon_d.get('needs', ['Security','Understanding','Space','Connection']),
            y)
        y -= 15

        venus = self.person.get('venus', 'Unknown')
        y = self.draw_section_title("Your Venus Love Style", y)
        y = self.draw_text(VENUS_STYLES.get(venus,
            f"Your Venus in {venus} shapes a unique way of loving."), y)

        c.showPage()

    # ── PAGE 7: HIDDEN PATTERN  ───────────────────────────────────

    def draw_hidden_pattern_page(self):
        y = self.new_page()
        c = self.c

        # chapter icon
        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL, 36)
        c.drawCentredString(self.width/2, y, '◆')
        y -= 45

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 26)
        c.drawCentredString(self.width/2, y, "Your Hidden Pattern")
        y -= 15

        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY_ITALIC, 13)
        c.drawCentredString(self.width/2, y, "The cycle your chart reveals — that you may not yet see")
        y -= 25

        c.setStrokeColor(GOLD); c.setLineWidth(1.5)
        c.line(self.width/2 - 80, y, self.width/2 + 80, y)
        y -= 30

        sun_d = ZODIAC_DEEP.get(self.sun_sign, {})

        intro = (f"{self.first_name}, of all the revelations in your chart, "
                 f"this is the one most clients say stopped them cold.")
        y = self.draw_text(intro, y)
        y -= 10

        # teaser card — gold-bordered box, text cuts mid-sentence
        teaser = sun_d.get('hpt',
            f"Your chart reveals a repeating cycle that began before you were fully aware. "
            f"Your {self.sun_sign} Sun and {self.moon_sign} Moon create a pattern around "
            f"vulnerability that causes you to")

        box_h = 1.65*inch
        c.setFillColor(NAVY)
        c.roundRect(self.margin, y - box_h, self.width - 2*self.margin, box_h, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD); c.setLineWidth(1.5)
        c.roundRect(self.margin, y - box_h, self.width - 2*self.margin, box_h, 8, fill=0, stroke=1)

        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawString(self.margin + 12, y - 14, "✧  YOUR PATTERN, REVEALED")

        # draw teaser text inside box, stopping mid-sentence
        c.setFillColor(white)
        c.setFont(FONT_BODY, 11)
        wrapper = textwrap.TextWrapper(width=int((self.width - 2*self.margin - 0.5*inch) / 5.5))
        lines = wrapper.wrap(teaser)
        ty = y - 38
        for line in lines[:4]:
            c.drawString(self.margin + 15, ty, line)
            ty -= 17
        # mid-sentence cutoff dots
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 18)
        c.drawString(self.margin + 15, ty, "...")

        y = y - box_h - 20

        # what this pattern affects
        y = self.draw_key_insight_box(
            "This Pattern Affects",
            ["How you respond the moment someone gets too close",
             "Why you attract the same relationship dynamics repeatedly",
             "When you self-sabotage—without understanding why"],
            y)
        y -= 15

        # lock teaser box
        lock_h = 1.0*inch
        c.setFillColor(HexColor('#f5f3ef'))
        c.roundRect(self.margin, y - lock_h, self.width - 2*self.margin, lock_h, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD); c.setLineWidth(1)
        c.roundRect(self.margin, y - lock_h, self.width - 2*self.margin, lock_h, 8, fill=0, stroke=1)

        c.setFillColor(NAVY)
        c.setFont(FONT_BODY_BOLD, 11)
        c.drawCentredString(self.width/2, y - 0.35*inch, "[LOCKED]  The full pattern + how to break it — in your complete book")
        c.setFillColor(HexColor('#888888'))
        c.setFont(FONT_BODY, 9)
        c.drawCentredString(self.width/2, y - 0.72*inch,
            "Root cause  •  When it activates  •  Step-by-step chart prescription")

        c.showPage()

    # ── PAGE 8: COMPATIBILITY  ────────────────────────────────────

    def draw_compatibility_page(self):
        y = self.new_page()
        c = self.c

        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL, 24)
        c.drawCentredString(self.width/2, y, '♡')
        y -= 35

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 24)
        c.drawCentredString(self.width/2, y, "Love & Compatibility")
        y -= 18

        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY_ITALIC, 12)
        c.drawCentredString(self.width/2, y, f"Your {self.sun_sign} compatibility with all 12 signs")
        y -= 25

        venus = self.person.get('venus', 'Unknown')
        c.setFillColor(NAVY)
        c.setFont(FONT_BODY, 10)
        wrapper = textwrap.TextWrapper(width=80)
        for line in wrapper.wrap(VENUS_STYLES.get(venus, '')):
            c.drawCentredString(self.width/2, y, line)
            y -= 15
        y -= 10

        c.setStrokeColor(HexColor('#dddddd'))
        c.setLineWidth(0.5)
        c.line(self.margin, y, self.width - self.margin, y)
        y -= 15

        # all 12 entries
        compat = get_compatibility(self.sun_sign)
        row_h = 0.48*inch

        for i, (sign, score, label) in enumerate(compat):
            locked = (i >= 3)

            if y < self.margin + row_h + 20:
                c.showPage()
                y = self.new_page()

            # alternating row bg
            if i % 2 == 0:
                c.setFillColor(HexColor('#f0eee8'))
                c.rect(self.margin - 5, y - row_h + 8, self.width - 2*self.margin + 10, row_h, fill=1, stroke=0)

            if not locked:
                # zodiac symbol
                c.setFillColor(GOLD)
                c.setFont(FONT_SYMBOL_BOLD, 18)
                c.drawString(self.margin, y - 8, ZODIAC_SYMBOLS.get(sign, '★'))
                # sign name
                c.setFillColor(NAVY)
                c.setFont(FONT_BODY_BOLD, 12)
                c.drawString(self.margin + 28, y - 6, sign)
                # label
                c.setFillColor(HexColor('#666666'))
                c.setFont(FONT_BODY, 10)
                c.drawString(self.margin + 28, y - 21, label)
                # bar track
                bar_w = 120; bar_h = 10
                bar_x = self.width - self.margin - bar_w - 55; bar_y = y - 12
                c.setFillColor(LIGHT_GRAY)
                c.rect(bar_x, bar_y, bar_w, bar_h, fill=1, stroke=0)
                c.setFillColor(get_compat_color(score))
                c.rect(bar_x, bar_y, bar_w * (score/100), bar_h, fill=1, stroke=0)
                # percentage
                c.setFillColor(NAVY)
                c.setFont(FONT_BODY_BOLD, 11)
                c.drawString(bar_x + bar_w + 8, bar_y - 1, f"{score}%")
            else:
                # LOCKED — opaque navy overlay completely covers content
                c.setFillColor(NAVY)
                c.setFont(FONT_SYMBOL_BOLD, 18)
                c.drawString(self.margin, y - 8, ZODIAC_SYMBOLS.get(sign, '★'))

                # Opaque solid block over sign name + label area
                c.setFillColor(HexColor('#c8c4bc'))
                c.roundRect(self.margin + 28, y - 28, 160, 28, 3, fill=1, stroke=0)

                c.setFillColor(HexColor('#888888'))
                c.setFont(FONT_BODY_BOLD, 9)
                c.drawCentredString(self.margin + 28 + 80, y - 14, '[LOCKED]')

                # Opaque solid block over bar area
                c.setFillColor(HexColor('#c8c4bc'))
                bar_w = 120
                bar_x = self.width - self.margin - bar_w - 55
                c.roundRect(bar_x, y - 18, bar_w + 55, 18, 3, fill=1, stroke=0)

            y -= row_h

        c.setFillColor(HexColor('#888888'))
        c.setFont(FONT_BODY_ITALIC, 9)
        c.drawCentredString(self.width/2, y - 8,
            "Unlock all 11 scores + detailed compatibility analysis in your complete book")

        c.showPage()

    # ── PAGE 9: CAREER ───────────────────────────────────────────

    def draw_career_page(self):
        y = self.new_page()
        c = self.c

        c.setFillColor(GOLD)
        c.setFont(FONT_SYMBOL, 36)
        c.drawCentredString(self.width/2, y, '★')
        y -= 45

        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 24)
        c.drawCentredString(self.width/2, y, "Career & Your Year Ahead")
        y -= 18

        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY_ITALIC, 12)
        c.drawCentredString(self.width/2, y, "Purpose, timing, and your 2026 opportunities")
        y -= 30

        zd = ZODIAC_DATA.get(self.sun_sign, {})
        career_text = (
            f"Your {self.sun_sign} {zd.get('element','')} energy gives you a natural drive that "
            f"points toward specific professional paths. The fulfillment you're seeking exists—your chart "
            f"reveals exactly which directions align with your soul's purpose and which paths will "
            f"drain you no matter how 'successful' they look on paper."
        )
        y = self.draw_section_title(f"Your {self.sun_sign} Career Path", y)
        y = self.draw_text(career_text, y)
        y -= 10

        # key dates 2026
        dates = [
            ("Mar 2026", "Jupiter expansion — new opportunities emerge"),
            ("Jun 2026", "Career breakthrough window opens"),
            ("Sep 2026", "Harvest period — past efforts finally pay off"),
            ("Nov 2026", "Bold energy for major professional changes"),
        ]
        y = self.draw_key_insight_box(
            "Your Key Dates: 2026",
            [f"{dt}  —  {ev}" for dt, ev in dates],
            y)
        y -= 15

        # lucky elements — 4 cards (same as full book)
        element = zd.get('element','Fire')
        lucky_colors = {'Fire':'Red, Orange, Gold','Earth':'Green, Brown, Tan','Air':'Yellow, Light Blue, White','Water':'Blue, Silver, Sea Green'}
        lucky_days   = {'Fire':'Tuesday, Sunday','Earth':'Friday, Saturday','Air':'Wednesday, Thursday','Water':'Monday, Friday'}
        cards = [
            ("Element",    element,                              ZODIAC_SYMBOLS.get(self.sun_sign,'★')),
            ("Colors",     lucky_colors.get(element,'Gold'),    "◆"),
            ("Lucky Days", lucky_days.get(element,'Sunday'),    "☆"),
            ("Crystal",    zd.get('crystal','Quartz'),          "◇"),
        ]
        card_w = (self.width - 2*self.margin - 24) / 4
        card_h = 75
        cy2 = y - card_h
        for i, (lbl, val, icon) in enumerate(cards):
            cx2 = self.margin + i*(card_w + 8)
            c.setFillColor(HexColor('#f5f3ef'))
            c.roundRect(cx2, cy2, card_w, card_h, 8, fill=1, stroke=0)
            c.setStrokeColor(HexColor('#e0dcd5')); c.setLineWidth(1)
            c.roundRect(cx2, cy2, card_w, card_h, 8, fill=0, stroke=1)
            c.setFillColor(GOLD); c.setFont(FONT_SYMBOL, 18)
            c.drawCentredString(cx2 + card_w/2, cy2 + card_h - 20, icon)
            c.setFillColor(HexColor('#888888')); c.setFont(FONT_BODY, 8)
            c.drawCentredString(cx2 + card_w/2, cy2 + card_h - 38, lbl)
            c.setFillColor(NAVY); c.setFont(FONT_BODY_BOLD, 8)
            c.drawCentredString(cx2 + card_w/2, cy2 + 12, val)

        c.showPage()

    # ── PAGE 10: CTA  ─────────────────────────────────────────────

    def draw_cta_page(self):
        c = self.c
        self.page_num += 1

        # Same dark navy as full book's upsell page
        DEEP_NAVY = HexColor('#0f1628')
        MID_NAVY  = HexColor('#252b4a')

        # gradient background (same technique as full book)
        steps = 60
        step_h = self.height / steps
        col1 = DEEP_NAVY; col2 = HexColor('#1a2040')
        for i in range(steps):
            r2 = i / steps
            r = col1.red   + (col2.red   - col1.red)   * r2
            g = col1.green + (col2.green - col1.green)  * r2
            b = col1.blue  + (col2.blue  - col1.blue)   * r2
            c.setFillColor(Color(r, g, b))
            c.rect(0, self.height - (i+1)*step_h, self.width, step_h + 1, fill=1, stroke=0)

        # gold top bar
        c.setFillColor(GOLD)
        c.rect(0, self.height - 6, self.width, 6, fill=1, stroke=0)

        # corners
        c.setFillColor(SOFT_GOLD); c.setFont(FONT_SYMBOL, 10)
        c.drawCentredString(35, self.height - 35, '✦')
        c.drawCentredString(self.width - 35, self.height - 35, '✦')

        # badge
        badge_y = self.height - 70
        c.setFillColor(GOLD)
        c.roundRect(self.width/2 - 100, badge_y - 9, 200, 24, 12, fill=1, stroke=0)
        c.setFillColor(DEEP_NAVY)
        c.setFont(FONT_BODY_BOLD, 9)
        c.drawCentredString(self.width/2, badge_y - 1, f"YOUR COMPLETE READING AWAITS, {self.first_name.upper()}")

        # headline
        c.setFillColor(white)
        c.setFont(FONT_HEADING_BOLD, 30)
        c.drawCentredString(self.width/2, self.height - 115, "This Was Just")
        c.drawCentredString(self.width/2, self.height - 148, "A Glimpse...")

        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY_ITALIC, 12)
        c.drawCentredString(self.width/2, self.height - 173,
            "Your full 60+ page book is ready to unlock")

        # locked items
        lock_items = [
            ("Your Hidden Pattern:",    "Root cause + how to break it for good"),
            ("Your Deepest Fear:",      "Why it drives every major decision"),
            ("Your Hidden Superpower:", "The gift you've been told is a flaw"),
            ("Your Soulmate Signature:","The chart placements to look for"),
            ("Month-by-Month 2026:",    "Every key date + what to do"),
            ("Your Shadow Self:",       "What you hide — and how to integrate it"),
        ]
        start_y = self.height - 205
        item_h   = 0.27*inch
        total_h  = len(lock_items) * item_h + 0.5*inch
        box_x = self.margin

        c.setFillColor(MID_NAVY)
        c.roundRect(box_x, start_y - total_h, self.width - 2*self.margin, total_h, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD); c.setLineWidth(1)
        c.roundRect(box_x, start_y - total_h, self.width - 2*self.margin, total_h, 8, fill=0, stroke=1)

        c.setFillColor(GOLD); c.setFont(FONT_BODY_BOLD, 10)
        c.drawCentredString(self.width/2, start_y - 0.22*inch, ">> LOCKED IN YOUR SAMPLE <<")
        c.setStrokeColor(HexColor('#3a4060')); c.setLineWidth(0.5)
        c.line(box_x + 20, start_y - 0.36*inch, self.width - box_x - 20, start_y - 0.36*inch)

        iy = start_y - 0.52*inch
        for lbl, blurred in lock_items:
            c.setFillColor(SOFT_GOLD); c.setFont(FONT_BODY_BOLD, 9)
            c.drawString(box_x + 15, iy, lbl)
            # solid opaque block — completely hides the text
            c.setFillColor(HexColor('#1a2040'))
            c.roundRect(box_x + 155, iy - 3, self.width - 2*self.margin - 170, 16, 3, fill=1, stroke=0)
            c.setFillColor(HexColor('#3a4060')); c.setFont(FONT_BODY, 7)
            c.drawString(box_x + 162, iy + 1, blurred[:42])
            iy -= item_h

        y_after_box = start_y - total_h - 15

        # features
        features = [
            ("☉", "60+ Personalized Pages",      "Written for your exact chart"),
            ("☽", "Full 12-Sign Compatibility",   "Detailed scores + analysis"),
            ("✧", "Month-by-Month 2026",          "Specific dates for every move"),
            ("♥", "Shadow & Soul Work",           "Deep psychological insights"),
            ("★", "Crystals, Tarot & Rituals",    "Practical spiritual tools"),
            ("◆", "Book in YOUR Chosen Color",    "The color you picked in the quiz"),
        ]
        feat_start = y_after_box - 15
        feat_h = 0.44*inch
        c.setFillColor(GOLD); c.setFont(FONT_HEADING_BOLD, 14)
        c.drawCentredString(self.width/2, feat_start, "Your Complete Book Includes")
        c.setStrokeColor(HexColor('#3a4060')); c.setLineWidth(0.5)
        c.line(self.margin + 80, feat_start - 12, self.width - self.margin - 80, feat_start - 12)

        col_w = 220; gap = 30
        total_w = col_w*2 + gap
        col1_x = (self.width - total_w) / 2
        col2_x = col1_x + col_w + gap
        PURPLE = HexColor('#6b4c9a'); LPURP = HexColor('#9b7bc7')

        for i, (icon, title, desc) in enumerate(features):
            col = i % 2; row = i // 2
            x = col1_x if col == 0 else col2_x
            fy = feat_start - 38 - row * feat_h

            c.setFillColor(PURPLE); c.circle(x + 16, fy + 6, 18, fill=1, stroke=0)
            c.setFillColor(LPURP);  c.circle(x + 16, fy + 7, 15, fill=1, stroke=0)
            c.setFillColor(white); c.setFont(FONT_SYMBOL_BOLD, 13)
            c.drawCentredString(x + 16, fy + 2, icon)
            c.setFillColor(white); c.setFont(FONT_BODY_BOLD, 10)
            c.drawString(x + 40, fy + 10, title)
            c.setFillColor(HexColor('#9999aa')); c.setFont(FONT_BODY, 8)
            c.drawString(x + 40, fy - 3, desc)

        # price + CTA
        cta_y = 115
        c.setStrokeColor(HexColor('#3a4060')); c.setLineWidth(0.5)
        c.line(self.margin + 80, cta_y + 62, self.width - self.margin - 80, cta_y + 62)

        # price
        c.setFillColor(white); c.setFont(FONT_HEADING_BOLD, 26)
        c.drawCentredString(self.width/2, cta_y + 44, "€7.99")
        c.setFillColor(SOFT_GOLD); c.setFont(FONT_BODY, 10)
        c.drawCentredString(self.width/2, cta_y + 27, "One-time payment  •  Instant PDF delivery")

        # gold CTA button
        c.setFillColor(HexColor('#a07d1f'))
        c.roundRect(self.width/2 - 142, cta_y - 2, 284, 42, 21, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.roundRect(self.width/2 - 140, cta_y, 280, 40, 20, fill=1, stroke=0)
        c.setFillColor(DEEP_NAVY); c.setFont(FONT_BODY_BOLD, 13)
        c.drawCentredString(self.width/2, cta_y + 13, "Unlock Your Complete Blueprint")

        # clickable link
        c.linkURL(self.checkout_url,
            (self.width/2 - 140, cta_y - 2, self.width/2 + 140, cta_y + 42), relative=0)

        # URL text
        c.setFillColor(SOFT_GOLD); c.setFont(FONT_BODY, 9)
        c.drawCentredString(self.width/2, cta_y - 14, self.checkout_url)
        c.linkURL(self.checkout_url,
            (self.margin, cta_y - 24, self.width - self.margin, cta_y - 4), relative=0)

        # footer
        c.setFillColor(SOFT_GOLD); c.setFont(FONT_SYMBOL, 10)
        c.drawCentredString(35, 35, '✦')
        c.drawCentredString(self.width - 35, 35, '✦')
        c.setFillColor(HexColor('#555566')); c.setFont(FONT_BODY, 8)
        c.drawCentredString(self.width/2, 22, "✓ 30-Day Money Back  •  ✓ Instant Delivery  •  ✓ 100% Personalized")

        c.showPage()

    # ── BUILD ─────────────────────────────────────────────────────

    def build(self):
        print(f"📖 Building sample book for {self.name}...")
        self.draw_cover()
        self.draw_birth_chart_page()
        self.draw_intro_page()
        self.draw_big_three_page()
        self.draw_sun_page()
        self.draw_moon_page()
        self.draw_hidden_pattern_page()
        self.draw_compatibility_page()
        self.draw_career_page()
        self.draw_cta_page()
        self.c.save()
        print(f"✅ Done: {self.output_path}  ({self.page_num} pages)")
        return self.output_path


# ── test ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    test = {
        'name':'Mahmoud','birth_date':'2005-11-10','birth_time':'11:35',
        'birth_time_period':'PM','birth_place':'Doha, Qatar',
        'sun_sign':'Scorpio','moon_sign':'Pisces','rising_sign':'Libra',
        'venus':'Sagittarius','mars':'Taurus','mercury':'Scorpio',
        'jupiter':'Libra','saturn':'Cancer',
    }
    book = OrastriaBookGenerator('/tmp/test_sample.pdf', test,
                                  user_id='ba424d68-66f4-4b03-ba72-27d5e4cbbdae')
    book.build()
