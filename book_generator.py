"""
Orastria Sample Book Generator v4
FIXES:
- Raleway font for body, Garamond for headings
- Fixed overlapping elements
- Text-based zodiac signs (no Unicode symbols that don't render)
- Guaranteed content in all sections
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math
import os
import requests
import urllib.request

# ==================== FONT SETUP ====================
def download_font(url, filename):
    """Download a font file if it doesn't exist"""
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, filename)
    
    if not os.path.exists(font_path):
        try:
            print(f"📥 Downloading {filename}...")
            urllib.request.urlretrieve(url, font_path)
            print(f"✅ Downloaded {filename}")
        except Exception as e:
            print(f"⚠️ Could not download {filename}: {e}")
            return None
    return font_path

def setup_fonts():
    """Setup Raleway and Garamond fonts"""
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    fonts = {
        'heading': None,
        'heading_bold': None,
        'body': None,
        'body_bold': None,
    }
    
    # Google Fonts URLs for Raleway and EB Garamond
    font_urls = {
        'Raleway-Regular': 'https://github.com/impallari/Raleway/raw/master/fonts/v4020/Raleway-Regular.ttf',
        'Raleway-Bold': 'https://github.com/impallari/Raleway/raw/master/fonts/v4020/Raleway-Bold.ttf',
        'EBGaramond-Regular': 'https://github.com/octaviopardo/EBGaramond12/raw/master/fonts/EBGaramond12-Regular.ttf',
        'EBGaramond-Bold': 'https://github.com/octaviopardo/EBGaramond12/raw/master/fonts/EBGaramond12-Bold.ttf',
    }
    
    # Try to find or download fonts
    for font_name, url in font_urls.items():
        font_path = os.path.join(font_dir, f'{font_name}.ttf')
        
        # Check if already exists
        if os.path.exists(font_path):
            fonts[font_name] = font_path
        else:
            # Try to download
            downloaded = download_font(url, f'{font_name}.ttf')
            if downloaded:
                fonts[font_name] = downloaded
    
    return fonts

# Try to setup custom fonts
CUSTOM_FONTS = setup_fonts()

# Register fonts with ReportLab
FONT_HEADING = 'Helvetica-Bold'  # Fallback
FONT_HEADING_BOLD = 'Helvetica-Bold'
FONT_BODY = 'Helvetica'  # Fallback
FONT_BODY_BOLD = 'Helvetica-Bold'

# Try to register Garamond for headings
garamond_path = CUSTOM_FONTS.get('EBGaramond-Regular') if CUSTOM_FONTS else None
garamond_bold_path = CUSTOM_FONTS.get('EBGaramond-Bold') if CUSTOM_FONTS else None

if garamond_path and os.path.exists(garamond_path):
    try:
        pdfmetrics.registerFont(TTFont('Garamond', garamond_path))
        FONT_HEADING = 'Garamond'
        print("✅ Garamond font loaded")
    except Exception as e:
        print(f"⚠️ Could not load Garamond: {e}")

if garamond_bold_path and os.path.exists(garamond_bold_path):
    try:
        pdfmetrics.registerFont(TTFont('Garamond-Bold', garamond_bold_path))
        FONT_HEADING_BOLD = 'Garamond-Bold'
    except:
        FONT_HEADING_BOLD = FONT_HEADING

# Try to register Raleway for body
raleway_path = CUSTOM_FONTS.get('Raleway-Regular') if CUSTOM_FONTS else None
raleway_bold_path = CUSTOM_FONTS.get('Raleway-Bold') if CUSTOM_FONTS else None

if raleway_path and os.path.exists(raleway_path):
    try:
        pdfmetrics.registerFont(TTFont('Raleway', raleway_path))
        FONT_BODY = 'Raleway'
        print("✅ Raleway font loaded")
    except Exception as e:
        print(f"⚠️ Could not load Raleway: {e}")

if raleway_bold_path and os.path.exists(raleway_bold_path):
    try:
        pdfmetrics.registerFont(TTFont('Raleway-Bold', raleway_bold_path))
        FONT_BODY_BOLD = 'Raleway-Bold'
    except:
        FONT_BODY_BOLD = FONT_BODY

# Fallback to DejaVu if custom fonts failed
import glob

def find_font(font_name):
    """Find font file path across different systems"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_paths = [
        os.path.join(script_dir, 'fonts', font_name),
        f'/app/fonts/{font_name}',
        f'/usr/share/fonts/truetype/dejavu/{font_name}',
        f'/usr/share/fonts/dejavu/{font_name}',
        f'/usr/share/fonts/TTF/{font_name}',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    nix_patterns = ['/nix/store/*dejavu*/share/fonts/truetype/*.ttf']
    for pattern in nix_patterns:
        try:
            matches = glob.glob(pattern, recursive=True)
            for match in matches:
                if font_name in match:
                    return match
        except:
            pass
    return None

# If custom fonts didn't load, try DejaVu as fallback
if FONT_BODY == 'Helvetica':
    dejavu_regular = find_font('DejaVuSans.ttf')
    dejavu_bold = find_font('DejaVuSans-Bold.ttf')
    
    if dejavu_regular:
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_regular))
            FONT_BODY = 'DejaVuSans'
            print("✅ DejaVuSans font loaded as fallback")
        except:
            pass
    
    if dejavu_bold:
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold))
            FONT_BODY_BOLD = 'DejaVuSans-Bold'
        except:
            pass

print(f"📝 Using fonts - Heading: {FONT_HEADING}, Body: {FONT_BODY}")

# ==================== BRAND COLORS ====================
NAVY = HexColor('#1a1f3c')
GOLD = HexColor('#c9a961')
CREAM = HexColor('#f5f0e8')
SOFT_GOLD = HexColor('#d4b87a')
LIGHT_NAVY = HexColor('#2d3561')

# ==================== ZODIAC DATA (TEXT-BASED - NO UNICODE SYMBOLS) ====================
ZODIAC_GLYPHS = {
    'Aries': 'AR', 'Taurus': 'TA', 'Gemini': 'GE', 'Cancer': 'CA',
    'Leo': 'LE', 'Virgo': 'VI', 'Libra': 'LI', 'Scorpio': 'SC',
    'Sagittarius': 'SG', 'Capricorn': 'CP', 'Aquarius': 'AQ', 'Pisces': 'PI'
}

# ==================== DEEP ZODIAC DATA ====================
ZODIAC_DEEP_DATA = {
    'Aries': {
        'core_essence': "You don't just enter a room—you ignite it. Your Aries Sun gives you a warrior's spirit wrapped in impatience. You start things brilliantly but finishing them? That's where your chart gets complicated.",
        'secret_wound': "being told to slow down, wait your turn, or think before you act—when your whole being screams to MOVE",
        'hidden_fear': "that if you stop pushing forward, you'll realize you don't know who you are when you're still",
        'what_others_miss': "behind your confidence is someone who genuinely doesn't understand why everyone else hesitates so much",
        'relationship_pattern': "you chase hard, win them over, then wonder why the spark fades once there's no challenge left",
        'core_traits': ['Fearlessly direct', 'Impatiently passionate', 'Competitively driven', 'Instinctively protective', 'Restlessly energetic', 'Courageously honest'],
        'careers': ['Entrepreneur', 'Emergency Services', 'Sports/Athletics', 'Sales Leader', 'Military/Defense', 'Startup Founder'],
        'lucky_numbers': '1, 9, 17, 28',
        'lucky_colors': 'Red, Orange, Gold',
    },
    'Taurus': {
        'core_essence': "You're not stubborn—you're certain. Your Taurus Sun gives you an unshakeable core that others mistake for inflexibility. You simply know what you want and refuse to apologize for it.",
        'secret_wound': "being rushed, pressured to change, or told your need for security is a weakness",
        'hidden_fear': "that the ground beneath you will shift before you're ready—that stability is just an illusion",
        'what_others_miss': "your sensuality runs deeper than pleasure—you experience life through touch, taste, and texture in ways others can't fathom",
        'relationship_pattern': "you take forever to commit, but once you do, you'll weather any storm—except betrayal, which you never forget",
        'core_traits': ['Unshakeably loyal', 'Sensually grounded', 'Patiently determined', 'Quietly strong', 'Materially savvy', 'Stubbornly devoted'],
        'careers': ['Financial Advisor', 'Chef/Restaurateur', 'Interior Designer', 'Real Estate', 'Music/Voice Artist', 'Luxury Brand Manager'],
        'lucky_numbers': '2, 6, 15, 24',
        'lucky_colors': 'Green, Pink, Earth tones',
    },
    'Gemini': {
        'core_essence': "Your mind never stops—and that's both your superpower and your curse. Your Gemini Sun processes information faster than others can speak. You're not two-faced; you're multi-dimensional.",
        'secret_wound': "being called shallow, flaky, or 'too much' when you're just trying to experience everything life offers",
        'hidden_fear': "that you'll never find someone or something interesting enough to hold your attention forever",
        'what_others_miss': "your constant movement isn't avoidance—it's how you process a world that would overwhelm most people",
        'relationship_pattern': "you need mental stimulation as much as emotional connection—bore you and you'll ghost without meaning to",
        'core_traits': ['Intellectually restless', 'Verbally gifted', 'Adaptively curious', 'Socially versatile', 'Mentally agile', 'Charmingly scattered'],
        'careers': ['Journalist/Writer', 'Marketing/PR', 'Teacher/Professor', 'Podcaster/Content Creator', 'Sales/Negotiations', 'Tech/Programming'],
        'lucky_numbers': '3, 5, 14, 23',
        'lucky_colors': 'Yellow, Light Blue, Silver',
    },
    'Cancer': {
        'core_essence': "You feel everything—and you remember it all. Your Cancer Sun gives you emotional sonar that picks up what others miss. Your shell isn't weakness; it's wisdom from wounds that made you stronger.",
        'secret_wound': "having your sensitivity used against you, being told you're 'too emotional' when you're actually too perceptive",
        'hidden_fear': "that the people you nurture will leave once they no longer need you",
        'what_others_miss': "your 'moodiness' is actually you processing everyone's emotions in the room, not just your own",
        'relationship_pattern': "you give until empty, then retreat into your shell wondering why no one noticed you were drowning",
        'core_traits': ['Deeply intuitive', 'Fiercely protective', 'Emotionally intelligent', 'Nostalgically sentimental', 'Nurturingly devoted', 'Psychically sensitive'],
        'careers': ['Therapist/Counselor', 'Chef/Baker', 'Nurse/Healthcare', 'Real Estate/Property', 'Social Worker', 'Historian/Genealogist'],
        'lucky_numbers': '2, 7, 11, 20',
        'lucky_colors': 'Silver, White, Sea Green',
    },
    'Leo': {
        'core_essence': "You're not seeking attention—you're radiating energy you can't contain. Your Leo Sun makes you impossible to ignore, and honestly, why would you want to be? You were born to be seen.",
        'secret_wound': "being overlooked, dismissed, or made to feel your light is 'too bright' for others' comfort",
        'hidden_fear': "that without an audience, without impact, you might not matter at all",
        'what_others_miss': "your need for appreciation isn't ego—it's a genuine desire to know your warmth reaches others",
        'relationship_pattern': "you love grandly and generously, but sulk dramatically when that love isn't visibly reciprocated",
        'core_traits': ['Magnetically confident', 'Generously warm', 'Dramatically expressive', 'Loyally protective', 'Creatively bold', 'Royally dignified'],
        'careers': ['Actor/Performer', 'CEO/Executive', 'Event Planner', 'Creative Director', 'Motivational Speaker', 'Influencer/Public Figure'],
        'lucky_numbers': '1, 5, 9, 19',
        'lucky_colors': 'Gold, Orange, Royal Purple',
    },
    'Virgo': {
        'core_essence': "Your mind is a precision instrument that notices what others overlook. Your Virgo Sun isn't critical—it's discerning. You see potential everywhere, including all the ways it could be better.",
        'secret_wound': "being called nitpicky or negative when you're just trying to help things reach their potential",
        'hidden_fear': "that despite all your effort to be useful and perfect, you'll still somehow not be enough",
        'what_others_miss': "your criticism of others is nothing compared to the relentless standards you hold yourself to",
        'relationship_pattern': "you show love through acts of service, then feel hurt when others don't notice the invisible labor",
        'core_traits': ['Analytically precise', 'Helpfully devoted', 'Practically grounded', 'Quietly perfectionist', 'Observantly intelligent', 'Modestly capable'],
        'careers': ['Data Analyst', 'Healthcare/Medicine', 'Editor/Writer', 'Accountant/Finance', 'Quality Assurance', 'Nutritionist/Wellness'],
        'lucky_numbers': '5, 14, 23, 32',
        'lucky_colors': 'Navy, Gray, Forest Green',
    },
    'Libra': {
        'core_essence': "You see both sides of everything—which is why deciding feels impossible. Your Libra Sun craves harmony so deeply that conflict feels like physical pain. You're not indecisive; you're comprehensive.",
        'secret_wound': "being forced to choose sides, deal with ugliness, or accept that some situations have no fair solution",
        'hidden_fear': "that if you state your true opinion, someone will be hurt, and the balance will be destroyed",
        'what_others_miss': "your people-pleasing isn't weakness—it's a sophisticated strategy to keep the peace you desperately need",
        'relationship_pattern': "you mirror partners so perfectly they fall for a reflection, then wonder why you feel unseen",
        'core_traits': ['Diplomatically graceful', 'Aesthetically refined', 'Socially intelligent', 'Harmoniously balanced', 'Romantically idealistic', 'Intellectually fair'],
        'careers': ['Lawyer/Mediator', 'Interior Designer', 'Diplomat/PR', 'Wedding Planner', 'Art Director', 'Human Resources'],
        'lucky_numbers': '6, 15, 24, 33',
        'lucky_colors': 'Pink, Light Blue, Lavender',
    },
    'Scorpio': {
        'core_essence': "You don't do surface-level anything. Your Scorpio Sun experiences life at depths others find terrifying. You're not intense—you're fully alive while others sleepwalk through existence.",
        'secret_wound': "being betrayed by someone you let past your walls, proving that vulnerability is dangerous",
        'hidden_fear': "that if people saw the full truth of your darkness, they'd run—and never come back",
        'what_others_miss': "your suspicion isn't paranoia—you simply see the shadows others pretend don't exist",
        'relationship_pattern': "you test loyalty repeatedly, pushing people away to see who'll fight to stay",
        'core_traits': ['Intensely passionate', 'Psychologically perceptive', 'Magnetically powerful', 'Fiercely loyal', 'Transformatively resilient', 'Mysteriously deep'],
        'careers': ['Psychologist/Therapist', 'Detective/Investigator', 'Surgeon/Medical', 'Financial Strategist', 'Crisis Manager', 'Researcher'],
        'lucky_numbers': '8, 11, 18, 22',
        'lucky_colors': 'Black, Burgundy, Deep Red',
    },
    'Sagittarius': {
        'core_essence': "You're allergic to limitation in all its forms. Your Sagittarius Sun needs freedom like others need air. You're not commitment-phobic—you just refuse to shrink yourself to fit small spaces.",
        'secret_wound': "being caged, controlled, or told to be 'realistic' about your impossibly expansive dreams",
        'hidden_fear': "that you'll run out of new horizons—that someday, there will be nothing left to explore",
        'what_others_miss': "your bluntness isn't cruelty—you genuinely believe the truth sets people free",
        'relationship_pattern': "you idealize the chase, then feel trapped once you've 'won'—not because love isn't real, but because routine feels like death",
        'core_traits': ['Expansively optimistic', 'Philosophically curious', 'Adventurously bold', 'Honestly blunt', 'Restlessly free', 'Inspiringly enthusiastic'],
        'careers': ['Travel/Tourism', 'Professor/Teacher', 'Publisher/Writer', 'Life Coach', 'International Business', 'Philosophy/Theology'],
        'lucky_numbers': '3, 9, 12, 21',
        'lucky_colors': 'Purple, Turquoise, Orange',
    },
    'Capricorn': {
        'core_essence': "You're playing a longer game than anyone realizes. Your Capricorn Sun makes you ancient beyond your years—you were born knowing life is hard and decided to become harder.",
        'secret_wound': "being forced to grow up too fast, carry too much responsibility, or achieve without acknowledgment",
        'hidden_fear': "that despite all your sacrifice and discipline, you'll reach the top only to find it empty",
        'what_others_miss': "your coldness is protection—underneath that armor is someone who feels deeply but can't afford to show it",
        'relationship_pattern': "you choose partners like investments, then struggle to access emotions you've suppressed for efficiency",
        'core_traits': ['Ambitiously driven', 'Practically wise', 'Responsibly mature', 'Strategically patient', 'Quietly powerful', 'Traditionally grounded'],
        'careers': ['CEO/Executive', 'Finance/Banking', 'Government/Politics', 'Architecture/Engineering', 'Law', 'Business Owner'],
        'lucky_numbers': '4, 8, 13, 22',
        'lucky_colors': 'Black, Brown, Dark Green',
    },
    'Aquarius': {
        'core_essence': "You're living in a future others haven't imagined yet. Your Aquarius Sun makes you feel like an alien—because you're here to change things, not fit in.",
        'secret_wound': "being called weird, cold, or 'too much' when you're just being authentically yourself",
        'hidden_fear': "that your difference makes you unlovable—that intimacy requires losing your uniqueness",
        'what_others_miss': "your detachment isn't lack of feeling—it's how you survive feeling connected to all of humanity at once",
        'relationship_pattern': "you need intellectual equals who won't try to domesticate you, but you'll run from anyone who gets too close",
        'core_traits': ['Radically original', 'Intellectually rebellious', 'Humanistically idealistic', 'Emotionally detached', 'Futuristically visionary', 'Stubbornly independent'],
        'careers': ['Tech/Innovation', 'Social Activism', 'Science/Research', 'Aviation/Space', 'Humanitarian Work', 'Inventor/Creator'],
        'lucky_numbers': '4, 7, 11, 22',
        'lucky_colors': 'Electric Blue, Silver, Violet',
    },
    'Pisces': {
        'core_essence': "You absorb emotions like a sponge—sometimes not knowing where others end and you begin. Your Pisces Sun connects you to something beyond the visible world.",
        'secret_wound': "being called 'too sensitive' when you're actually too perceptive for a world that rewards numbness",
        'hidden_fear': "that reality will crush the magic you work so hard to preserve inside yourself",
        'what_others_miss': "your escapism isn't weakness—it's survival in a world that feels unbearably harsh to your unfiltered soul",
        'relationship_pattern': "you fall for potential, not reality—loving who someone could be while ignoring who they are",
        'core_traits': ['Spiritually intuitive', 'Emotionally boundless', 'Creatively gifted', 'Compassionately selfless', 'Dreamily imaginative', 'Psychically sensitive'],
        'careers': ['Artist/Musician', 'Healer/Therapist', 'Spiritual Guide', 'Filmmaker/Photographer', 'Nurse/Caregiver', 'Marine Biology'],
        'lucky_numbers': '3, 7, 12, 21',
        'lucky_colors': 'Sea Green, Lavender, Silver',
    },
}

# ==================== MOON SIGN DATA ====================
MOON_DEEP_DATA = {
    'Aries': {
        'essence': "Your emotional responses are instant and fierce. You process feelings by taking action—sitting with emotions feels unbearable.",
        'needs': ['Freedom to express anger', 'Action over discussion', 'Independence in relationships', 'A partner who can handle intensity'],
        'emotional_pattern': "You fall fast, burn hot, and move on quickly—not from lack of depth, but because your heart processes at lightning speed.",
    },
    'Taurus': {
        'essence': "Your emotions move like honey—slowly, sweetly, and with staying power. Once you feel something, it takes root.",
        'needs': ['Physical affection and touch', 'Financial security', 'Routine and predictability', 'Beauty in your environment'],
        'emotional_pattern': "You're the person who replays the same song when sad, craves comfort food when stressed, and stays loyal long past expiration dates.",
    },
    'Gemini': {
        'essence': "You process emotions by talking them out—sometimes with others, sometimes just with yourself.",
        'needs': ['Mental stimulation always', 'Variety in emotional expression', 'A partner who talks through everything', 'Space to change your mind'],
        'emotional_pattern': "You can rationalize any feeling until it almost disappears—which is both your superpower and your avoidance strategy.",
    },
    'Cancer': {
        'essence': "Your emotional world is oceanic—deep, tidal, and full of currents no one else can see.",
        'needs': ['A safe home base to return to', 'Emotional reciprocity', 'Permission to nurture', 'Connection to family or chosen family'],
        'emotional_pattern': "You remember every emotional slight—not from bitterness, but because your heart literally cannot forget how things felt.",
    },
    'Leo': {
        'essence': "Your emotions want an audience—not for validation, but because feelings this big deserve to be witnessed.",
        'needs': ['Appreciation and admiration', 'Creative emotional outlets', 'Loyalty from your inner circle', 'Dramatic gestures of love'],
        'emotional_pattern': "When hurt, you either roar or retreat into dignified silence—there's no in-between for a wounded Leo Moon.",
    },
    'Virgo': {
        'essence': "You process emotions by analyzing them, categorizing them, and figuring out how to fix them.",
        'needs': ['Order and routine', 'Feeling useful to others', 'Health and wellness practices', 'A partner who appreciates your help'],
        'emotional_pattern': "You show love through acts of service, then feel invisible when others don't notice the thousand small things you do.",
    },
    'Libra': {
        'essence': "Your emotional wellbeing is tied to harmony around you. Discord hits you physically.",
        'needs': ['Partnership above all', 'Beauty and aesthetics', 'Peaceful environments', 'Feeling chosen and valued'],
        'emotional_pattern': "You suppress your needs to keep the peace, then resent others for not reading your mind.",
    },
    'Scorpio': {
        'essence': "Your emotions run to depths that would terrify most people. You don't just feel sad—you plunge into the underworld of grief.",
        'needs': ['Absolute emotional honesty', 'Privacy for processing', 'Intense intimate connection', 'Power over your own life'],
        'emotional_pattern': "You test people's loyalty before letting them close, pushing to see who'll fight to stay.",
    },
    'Sagittarius': {
        'essence': "You process emotions by finding their meaning—every feeling must lead to wisdom, growth, or a good story.",
        'needs': ['Freedom from emotional obligation', 'Adventure and new experiences', 'Philosophical understanding', 'A partner who grows with you'],
        'emotional_pattern': "You escape difficult emotions through movement, travel, or humor—sitting with discomfort feels like death.",
    },
    'Capricorn': {
        'essence': "Your emotions are disciplined, controlled, and often postponed for more convenient times.",
        'needs': ['Respect and recognition', 'Achievement and progress', 'Stability in relationships', 'Time to process privately'],
        'emotional_pattern': "You struggle to access feelings in real-time, processing them days or years later when it's 'safe.'",
    },
    'Aquarius': {
        'essence': "You intellectualize emotions to survive them. Feelings are fascinating phenomena to observe—from a safe distance.",
        'needs': ['Space and independence', 'Intellectual connection', 'Freedom to be unconventional', 'Friends who feel like found family'],
        'emotional_pattern': "You care deeply about humanity but struggle with one-on-one emotional intimacy.",
    },
    'Pisces': {
        'essence': "Your emotional boundaries are permeable—you feel everything around you, absorbing others' pain and joy.",
        'needs': ['Alone time to decompress', 'Creative and spiritual outlets', 'Gentle, non-judgmental love', 'Escape hatches from harsh reality'],
        'emotional_pattern': "You'd rather suffer in silence than burden others, then wonder why no one comes to rescue you.",
    },
}

# ==================== VENUS LOVE STYLES ====================
VENUS_LOVE_STYLES = {
    'Aries': "You love like a conquest—the chase is intoxicating, but keeping that fire alive after you've 'won' is your real challenge.",
    'Taurus': "You love through devotion and physical presence. For you, real love is showing up consistently, building something lasting.",
    'Gemini': "You love through conversation and intellectual flirtation. A partner who bores you mentally will lose you.",
    'Cancer': "You love by nurturing and creating emotional sanctuary. Your love is protective, always deeply felt.",
    'Leo': "You love grandly and expect to be adored in return. Love should feel like being chosen above all others.",
    'Virgo': "You love through acts of service and attention to detail. You show devotion by noticing what others need.",
    'Libra': "You love through partnership and romance. You need a plus-one for life—someone who completes you.",
    'Scorpio': "You love with volcanic intensity. Casual isn't in your vocabulary—you want soul-merging depth or nothing.",
    'Sagittarius': "You love through shared adventure and growth. A partner who clips your wings will lose you.",
    'Capricorn': "You love by building—a life, a legacy, a future. Your devotion shows through commitment, not poetry.",
    'Aquarius': "You love from a slight distance—intimacy without possessiveness. You need a partner who's also a best friend.",
    'Pisces': "You love transcendently, seeing your partner's soul more than their flaws. The danger is loving potential over reality.",
}

# ==================== COMPATIBILITY DATA ====================
COMPATIBILITY_DATA = {
    'Aries': [('Leo', 'Passionate Fire', 94), ('Sagittarius', 'Adventure Partners', 91), ('Aquarius', 'Exciting Rebels', 85)],
    'Taurus': [('Cancer', 'Security Seekers', 93), ('Virgo', 'Grounded Love', 90), ('Capricorn', 'Building Together', 88)],
    'Gemini': [('Libra', 'Mental Connection', 92), ('Aquarius', 'Intellectual Equals', 90), ('Aries', 'Exciting Energy', 84)],
    'Cancer': [('Scorpio', 'Deep Waters', 95), ('Pisces', 'Soulmate Energy', 93), ('Taurus', 'Nurturing Bond', 89)],
    'Leo': [('Aries', 'Fire Passion', 94), ('Sagittarius', 'Grand Romance', 91), ('Libra', 'Adoring Balance', 87)],
    'Virgo': [('Taurus', 'Practical Love', 91), ('Capricorn', 'Ambitious Partners', 90), ('Cancer', 'Caring Match', 86)],
    'Libra': [('Gemini', 'Air Connection', 92), ('Aquarius', 'Intellectual Bond', 89), ('Leo', 'Romantic Drama', 87)],
    'Scorpio': [('Cancer', 'Emotional Depth', 95), ('Pisces', 'Mystical Union', 93), ('Capricorn', 'Power Couple', 85)],
    'Sagittarius': [('Aries', 'Fire Adventure', 91), ('Leo', 'Grand Passion', 90), ('Aquarius', 'Freedom Lovers', 88)],
    'Capricorn': [('Taurus', 'Empire Builders', 92), ('Virgo', 'Practical Match', 90), ('Scorpio', 'Intense Power', 85)],
    'Aquarius': [('Gemini', 'Mind Meld', 92), ('Libra', 'Social Harmony', 89), ('Sagittarius', 'Free Spirits', 88)],
    'Pisces': [('Cancer', 'Soul Connection', 95), ('Scorpio', 'Deep Magic', 93), ('Taurus', 'Grounding Love', 86)],
}

# ==================== AI INSIGHTS ====================
REPLICATE_URL = os.environ.get('REPLICATE_MODEL_URL', 'https://api.replicate.com/v1/models/anthropic/claude-3.5-sonnet/predictions')
REPLICATE_API_KEY = os.environ.get('REPLICATE_API_KEY', '')


def get_fallback_insights(name, sun_sign, moon_sign, quiz_data):
    """Fallback insights - these ALWAYS have content"""
    sun_data = ZODIAC_DEEP_DATA.get(sun_sign, ZODIAC_DEEP_DATA['Aries'])
    moon_data = MOON_DEEP_DATA.get(moon_sign, MOON_DEEP_DATA['Aries'])
    life_dreams = quiz_data.get('life_dreams', 'finding your true purpose')
    
    return {
        'sun_insight': f"Your {sun_sign} Sun means you've likely been told you're 'too much'—{sun_data.get('secret_wound', 'but what others see as excess is simply your authentic intensity')}.",
        'moon_insight': f"With your {moon_sign} Moon, {moon_data.get('emotional_pattern', 'your emotional world runs deeper than others realize')}.",
        'dream_insight': f"Your dream of '{life_dreams}' isn't random—your chart reveals exactly why this calls to you so deeply.",
        'career_insight': f"The career fulfillment you're seeking exists—and your {sun_sign} energy combined with your {moon_sign} emotional needs points to paths you haven't fully considered yet."
    }


def generate_ai_insights(name, sun_sign, moon_sign, rising_sign, quiz_data):
    """Generate AI insights with guaranteed fallback"""
    # Always return fallback for reliability
    return get_fallback_insights(name, sun_sign, moon_sign, quiz_data)


# ==================== MAIN BOOK CLASS ====================
class OrastriaSampleBookV4:
    def __init__(self, output_path, person_data, quiz_data=None, book_type='sample'):
        self.output_path = output_path
        self.person = person_data
        self.quiz = quiz_data or {}
        self.book_type = book_type
        self.width, self.height = letter
        self.margin = 0.75 * inch
        self.c = canvas.Canvas(output_path, pagesize=letter)
        self.page_num = 0
        
        # Get AI insights
        print("🤖 Generating personalized insights...")
        self.ai_insights = generate_ai_insights(
            self.person.get('name', 'Friend'),
            self.person.get('sun_sign', 'Unknown'),
            self.person.get('moon_sign', 'Unknown'),
            self.person.get('rising_sign', 'Unknown'),
            self.quiz
        )
        print("✅ Insights ready")
        
        # Get zodiac data
        self.sun_data = ZODIAC_DEEP_DATA.get(self.person.get('sun_sign'), ZODIAC_DEEP_DATA['Aries'])
        self.moon_data = MOON_DEEP_DATA.get(self.person.get('moon_sign'), MOON_DEEP_DATA['Aries'])
    
    def draw_border(self):
        """Draw elegant border"""
        c = self.c
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        margin = 0.5 * inch
        c.rect(margin, margin, self.width - 2*margin, self.height - 2*margin)
        
        # Corner decorations (simple dots instead of symbols)
        c.setFillColor(GOLD)
        corners = [(margin + 8, margin + 8), (self.width - margin - 8, margin + 8),
                   (margin + 8, self.height - margin - 8), (self.width - margin - 8, self.height - margin - 8)]
        for x, y in corners:
            c.circle(x, y, 3, fill=1, stroke=0)
    
    def add_page_number(self):
        """Add page number"""
        self.page_num += 1
        self.c.setFillColor(GOLD)
        self.c.setFont(FONT_BODY, 10)
        self.c.drawCentredString(self.width / 2, 0.6 * inch, f"— {self.page_num} —")
    
    def new_page(self):
        """Start new page with border"""
        self.c.showPage()
        self.draw_border()
        self.add_page_number()
    
    def draw_text(self, text, x, y, width, size=11, line_height=14, color=black, font=None, bold=False):
        """Draw wrapped text with proper handling"""
        if not text:
            return y
            
        c = self.c
        if font:
            use_font = font
        else:
            use_font = FONT_BODY_BOLD if bold else FONT_BODY
        
        c.setFillColor(color)
        c.setFont(use_font, size)
        
        words = str(text).split()
        if not words:
            return y
            
        current_line = ''
        current_y = y
        
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            if c.stringWidth(test_line, use_font, size) < width:
                current_line = test_line
            else:
                c.drawString(x, current_y, current_line)
                current_y -= line_height
                current_line = word
        
        if current_line:
            c.drawString(x, current_y, current_line)
            current_y -= line_height
        
        return current_y
    
    def draw_heading(self, text, x, y, size=22, centered=False):
        """Draw heading with Garamond font"""
        c = self.c
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, size)
        if centered:
            c.drawCentredString(x, y, text)
        else:
            c.drawString(x, y, text)
    
    def draw_subheading(self, text, x, y, size=11, centered=False):
        """Draw subheading"""
        c = self.c
        c.setFillColor(HexColor('#666666'))
        c.setFont(FONT_BODY, size)
        if centered:
            c.drawCentredString(x, y, text)
        else:
            c.drawString(x, y, text)
    
    # ==================== PAGE 1: COVER ====================
    def create_cover(self):
        """Stunning personalized cover"""
        c = self.c
        
        # Navy background
        c.setFillColor(NAVY)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        # Double border
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.rect(0.4*inch, 0.4*inch, self.width - 0.8*inch, self.height - 0.8*inch)
        c.setLineWidth(1)
        c.rect(0.5*inch, 0.5*inch, self.width - 1*inch, self.height - 1*inch)
        
        # Top decorations (simple text instead of symbols)
        c.setFont(FONT_HEADING_BOLD, 18)
        c.setFillColor(GOLD)
        c.drawCentredString(0.9*inch, self.height - 0.85*inch, "SUN")
        c.drawCentredString(self.width - 0.9*inch, self.height - 0.85*inch, "MOON")
        
        # Title
        c.setFont(FONT_HEADING_BOLD, 32)
        c.drawCentredString(self.width/2, self.height - 1.8*inch, "YOUR COSMIC")
        c.drawCentredString(self.width/2, self.height - 2.25*inch, "BLUEPRINT")
        
        # Line
        c.line(2.2*inch, self.height - 2.5*inch, self.width - 2.2*inch, self.height - 2.5*inch)
        
        # Name
        c.setFillColor(white)
        c.setFont(FONT_HEADING_BOLD, 26)
        c.drawCentredString(self.width/2, self.height - 3.2*inch, self.person.get('name', 'Friend'))
        
        # Birth info
        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_BODY, 12)
        birth_date = self.person.get('birth_date', '')
        birth_time = self.person.get('birth_time', '')
        birth_place = self.person.get('birth_place', '')
        c.drawCentredString(self.width/2, self.height - 3.6*inch, f"{birth_date}  •  {birth_time}")
        c.drawCentredString(self.width/2, self.height - 3.85*inch, birth_place)
        
        # Central circle with sign
        center_y = self.height / 2 - 0.3*inch
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, center_y, 85)
        c.setLineWidth(1)
        c.circle(self.width/2, center_y, 95)
        
        # Main zodiac sign (text based)
        sun_sign = self.person.get('sun_sign', 'Aries')
        c.setFont(FONT_HEADING_BOLD, 48)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, center_y + 10, sun_sign.upper()[:3])
        
        # Full sign name
        c.setFont(FONT_HEADING_BOLD, 16)
        c.drawCentredString(self.width/2, center_y - 35, sun_sign)
        
        # Big Three
        c.setFont(FONT_BODY, 11)
        c.setFillColor(white)
        moon_sign = self.person.get('moon_sign', 'Unknown')
        rising_sign = self.person.get('rising_sign', 'Unknown')
        c.drawCentredString(self.width/2, center_y - 115, f"Sun: {sun_sign}  •  Moon: {moon_sign}  •  Rising: {rising_sign}")
        
        # Bottom branding
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 20)
        c.drawCentredString(self.width/2, 1.3*inch, "ORASTRIA")
        c.setFont(FONT_BODY, 10)
        c.drawCentredString(self.width/2, 1*inch, "Personalized Astrology  •  Written in the Stars")
    
    # ==================== PAGE 2: INTRO ====================
    def create_intro_page(self):
        """Emotional hook intro"""
        self.new_page()
        c = self.c
        
        first_name = self.person.get('name', 'Friend').split()[0]
        sun_sign = self.person.get('sun_sign', 'Unknown')
        
        # Header
        self.draw_heading("The Stars Were Watching", self.width/2, self.height - 1.3*inch, centered=True)
        
        # Decorative line
        c.setFillColor(GOLD)
        c.setFont(FONT_BODY, 12)
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "• • •")
        
        # Personal letter
        birth_date = self.person.get('birth_date', 'your birth')
        birth_time = self.person.get('birth_time', 'that moment')
        birth_place = self.person.get('birth_place', 'where you entered this world')
        
        intro = f"""Dear {first_name},

On {birth_date}, at exactly {birth_time} in {birth_place}, something extraordinary happened.

The cosmos paused.

Every planet, every star, every celestial body aligned in a configuration that had never existed before in the 13.8 billion year history of the universe—and will never exist again.

That moment was yours. Only yours.

This isn't a generic horoscope pulled from a newspaper. This is YOUR cosmic DNA—calculated to the exact minute and location of your birth, analyzed through your unique planetary positions, and written specifically for the soul that entered this world at that precise moment.

What you're about to read may feel uncomfortably accurate. That's by design."""

        self.draw_text(intro, 1*inch, self.height - 2*inch, self.width - 2*inch, size=11, line_height=16)
        
        # Rarity box
        y_box = 3.0*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.4*inch, self.width - 2*inch, 1.1*inch, 10, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.4*inch, self.width - 2*inch, 1.1*inch, 10, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawCentredString(self.width/2, y_box + 0.4*inch, "YOUR ASTROLOGICAL RARITY")
        
        import random
        random.seed(hash(self.person.get('name', '')) % 1000)
        rarity = round(random.uniform(0.12, 0.34), 2)
        
        c.setFont(FONT_BODY, 10)
        c.setFillColor(HexColor('#444444'))
        c.drawCentredString(self.width/2, y_box + 0.1*inch, f"Only {rarity}% of people share your exact planetary configuration.")
        c.drawCentredString(self.width/2, y_box - 0.12*inch, f"Your {sun_sign} Sun with {self.person.get('moon_sign', 'your')} Moon is exceptionally rare.")
    
    # ==================== PAGE 3: BIRTH CHART ====================
    def create_birth_chart_page(self):
        """Visual birth chart"""
        self.new_page()
        c = self.c
        
        self.draw_heading("Your Birth Chart", self.width/2, self.height - 1.3*inch, centered=True)
        self.draw_subheading("A snapshot of the heavens at your first breath", self.width/2, self.height - 1.6*inch, centered=True)
        
        # Draw wheel
        center_x = self.width / 2
        center_y = self.height / 2 + 0.7*inch
        
        c.setStrokeColor(NAVY)
        c.setLineWidth(2)
        c.circle(center_x, center_y, 130)
        c.setLineWidth(1)
        c.circle(center_x, center_y, 100)
        c.circle(center_x, center_y, 50)
        
        # House lines
        c.setStrokeColor(HexColor('#cccccc'))
        c.setLineWidth(0.5)
        for i in range(12):
            angle = (90 - i * 30) * math.pi / 180
            x1 = center_x + 50 * math.cos(angle)
            y1 = center_y + 50 * math.sin(angle)
            x2 = center_x + 130 * math.cos(angle)
            y2 = center_y + 130 * math.sin(angle)
            c.line(x1, y1, x2, y2)
        
        # Signs around wheel (text abbreviations)
        signs = list(ZODIAC_GLYPHS.keys())
        sun_sign = self.person.get('sun_sign', 'Aries')
        
        c.setFont(FONT_BODY_BOLD, 10)
        for i, sign in enumerate(signs):
            angle = (75 - i * 30) * math.pi / 180
            x = center_x + 115 * math.cos(angle)
            y = center_y + 115 * math.sin(angle)
            c.setFillColor(GOLD if sign == sun_sign else NAVY)
            c.drawCentredString(x, y - 3, ZODIAC_GLYPHS[sign])
        
        # Center
        c.setFont(FONT_HEADING_BOLD, 14)
        c.setFillColor(GOLD)
        moon_sign = self.person.get('moon_sign', 'Unknown')
        c.drawCentredString(center_x, center_y + 8, f"{sun_sign[:3]}")
        c.setFont(FONT_BODY, 9)
        c.setFillColor(NAVY)
        c.drawCentredString(center_x, center_y - 8, f"/ {moon_sign[:3]}")
        
        # Planet table
        y_table = 2.5*inch
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(1*inch, y_table + 0.3*inch, "Your Planetary Positions")
        
        planets = [
            ("Sun", self.person.get('sun_sign', 'Unknown')),
            ("Moon", self.person.get('moon_sign', 'Unknown')),
            ("Rising", self.person.get('rising_sign', 'Unknown')),
            ("Mercury", self.person.get('mercury', 'Unknown')),
            ("Venus", self.person.get('venus', 'Unknown')),
            ("Mars", self.person.get('mars', 'Unknown')),
        ]
        
        c.setFont(FONT_BODY, 10)
        y = y_table
        for name, sign in planets:
            c.setFillColor(NAVY)
            c.drawString(1.2*inch, y, name)
            c.setFillColor(black)
            c.drawString(2.5*inch, y, sign)
            y -= 0.24*inch
    
    # ==================== PAGE 4: BIG THREE ====================
    def create_big_three_page(self):
        """Big Three overview"""
        self.new_page()
        c = self.c
        
        self.draw_heading("Your Big Three", self.width/2, self.height - 1.3*inch, size=24, centered=True)
        self.draw_subheading("The three pillars of who you are", self.width/2, self.height - 1.6*inch, centered=True)
        
        # Three columns
        col_width = (self.width - 1.5*inch) / 3
        y_start = self.height - 2.2*inch
        
        sun_sign = self.person.get('sun_sign', 'Unknown')
        moon_sign = self.person.get('moon_sign', 'Unknown')
        rising_sign = self.person.get('rising_sign', 'Unknown')
        
        placements = [
            ("SUN", sun_sign, "Your Core Self", "Who you are at your center"),
            ("MOON", moon_sign, "Your Inner World", "How you feel and process"),
            ("RISING", rising_sign, "Your Outer Mask", "How the world sees you"),
        ]
        
        for i, (label, sign, desc1, desc2) in enumerate(placements):
            x = 0.75*inch + col_width/2 + i * col_width
            
            # Circle with abbreviation
            c.setStrokeColor(GOLD)
            c.setLineWidth(2)
            c.circle(x, y_start, 25)
            
            c.setFont(FONT_HEADING_BOLD, 14)
            c.setFillColor(GOLD)
            c.drawCentredString(x, y_start - 5, sign[:3].upper())
            
            c.setFont(FONT_BODY_BOLD, 10)
            c.setFillColor(NAVY)
            c.drawCentredString(x, y_start - 0.5*inch, label)
            
            c.setFont(FONT_HEADING_BOLD, 12)
            c.setFillColor(GOLD)
            c.drawCentredString(x, y_start - 0.75*inch, sign)
            
            c.setFont(FONT_BODY, 9)
            c.setFillColor(HexColor('#555555'))
            c.drawCentredString(x, y_start - 1.0*inch, desc1)
            c.drawCentredString(x, y_start - 1.15*inch, desc2)
        
        # Summary box
        y_box = y_start - 1.7*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 1.3*inch, self.width - 2*inch, 1.5*inch, 10, fill=1, stroke=0)
        
        first_name = self.person.get('name', 'Friend').split()[0]
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawString(1.2*inch, y_box - 0.1*inch, f"What This Means For You, {first_name}:")
        
        sun_data = ZODIAC_DEEP_DATA.get(sun_sign, {})
        moon_data = MOON_DEEP_DATA.get(moon_sign, {})
        
        summary = f"Your {sun_sign} Sun means {sun_data.get('what_others_miss', 'you have unique gifts others overlook')}. Combined with your {moon_sign} Moon, {moon_data.get('emotional_pattern', 'your emotional world is rich and complex')}. This combination is rare—and powerful."
        
        self.draw_text(summary, 1.2*inch, y_box - 0.35*inch, self.width - 2.6*inch, size=10, line_height=14)
    
    # ==================== PAGE 5: SUN SIGN ====================
    def create_sun_sign_page(self):
        """Sun sign deep dive"""
        self.new_page()
        c = self.c
        
        sun_sign = self.person.get('sun_sign', 'Unknown')
        
        self.draw_heading(f"Your Sun in {sun_sign}", self.width/2, self.height - 1.3*inch, centered=True)
        self.draw_subheading("Your core identity and life force", self.width/2, self.height - 1.55*inch, centered=True)
        
        # Sign circle
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, self.height - 2.2*inch, 35)
        c.setFont(FONT_HEADING_BOLD, 24)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.28*inch, sun_sign[:3].upper())
        
        # Core essence
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(1*inch, self.height - 2.9*inch, "The Truth About Your Core Self")
        
        essence = self.sun_data.get('core_essence', f"As a {sun_sign} Sun, you possess unique qualities.")
        y = self.draw_text(essence, 1*inch, self.height - 3.15*inch, self.width - 2*inch, size=10, line_height=14)
        
        # AI Insight box
        y -= 0.25*inch
        box_top = y
        box_height = 0.9*inch
        c.setFillColor(NAVY)
        c.roundRect(1*inch, box_top - box_height, self.width - 2*inch, box_height, 8, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BODY_BOLD, 9)
        c.drawString(1.2*inch, box_top - 0.18*inch, "PERSONAL INSIGHT")
        
        ai_sun = self.ai_insights.get('sun_insight', f"Your {sun_sign} nature runs deeper than most realize.")
        self.draw_text(ai_sun, 1.2*inch, box_top - 0.4*inch, self.width - 2.6*inch, size=10, line_height=13, color=white)
        
        # Traits box - FIXED POSITION
        y_traits = 3.6*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_traits - 0.3*inch, self.width - 2*inch, 1.3*inch, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_traits - 0.3*inch, self.width - 2*inch, 1.3*inch, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawString(1.2*inch, y_traits + 0.7*inch, f"Core {sun_sign} Traits:")
        
        traits = self.sun_data.get('core_traits', ['Unique', 'Complex', 'Evolving', 'Authentic', 'Powerful', 'Deep'])
        c.setFont(FONT_BODY, 10)
        c.setFillColor(black)
        trait_y = y_traits + 0.4*inch
        for i, trait in enumerate(traits[:3]):
            c.drawString(1.3*inch, trait_y - i*0.22*inch, f"•  {trait}")
        for i, trait in enumerate(traits[3:6]):
            c.drawString(4*inch, trait_y - i*0.22*inch, f"•  {trait}")
        
        # Secret wound teaser
        c.setFillColor(GOLD)
        c.setFont(FONT_BODY_BOLD, 10)
        wound = self.sun_data.get('secret_wound', 'something deep')[:50]
        c.drawString(1*inch, 2.2*inch, f"Your secret wound: {wound}...")
        c.setFont(FONT_BODY, 9)
        c.setFillColor(HexColor('#888888'))
        c.drawString(1*inch, 2.0*inch, "[Full shadow work analysis in complete book]")
    
    # ==================== PAGE 6: MOON SIGN ====================
    def create_moon_sign_page(self):
        """Moon sign page"""
        self.new_page()
        c = self.c
        
        moon_sign = self.person.get('moon_sign', 'Unknown')
        
        self.draw_heading(f"Your Moon in {moon_sign}", self.width/2, self.height - 1.3*inch, centered=True)
        self.draw_subheading("Your emotional nature and inner world", self.width/2, self.height - 1.55*inch, centered=True)
        
        # Moon circle
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, self.height - 2.2*inch, 35)
        c.setFont(FONT_HEADING_BOLD, 24)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.28*inch, moon_sign[:3].upper())
        
        # Essence
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(1*inch, self.height - 2.9*inch, "Your Emotional Truth")
        
        essence = self.moon_data.get('essence', f"With your Moon in {moon_sign}, your emotional world is unique.")
        y = self.draw_text(essence, 1*inch, self.height - 3.15*inch, self.width - 2*inch, size=10, line_height=14)
        
        # AI Insight box
        y -= 0.25*inch
        box_top = y
        box_height = 0.9*inch
        c.setFillColor(NAVY)
        c.roundRect(1*inch, box_top - box_height, self.width - 2*inch, box_height, 8, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BODY_BOLD, 9)
        c.drawString(1.2*inch, box_top - 0.18*inch, "PERSONAL INSIGHT")
        
        ai_moon = self.ai_insights.get('moon_insight', f"Your {moon_sign} Moon shapes how you process everything.")
        self.draw_text(ai_moon, 1.2*inch, box_top - 0.4*inch, self.width - 2.6*inch, size=10, line_height=13, color=white)
        
        # Needs box - FIXED POSITION
        y_needs = 3.6*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_needs - 0.4*inch, self.width - 2*inch, 1.4*inch, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_needs - 0.4*inch, self.width - 2*inch, 1.4*inch, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawString(1.2*inch, y_needs + 0.7*inch, f"What Your {moon_sign} Moon Needs:")
        
        needs = self.moon_data.get('needs', ['Emotional security', 'Understanding', 'Space to feel', 'Connection'])
        c.setFont(FONT_BODY, 10)
        c.setFillColor(black)
        need_y = y_needs + 0.4*inch
        for i, need in enumerate(needs[:4]):
            c.drawString(1.3*inch, need_y - i*0.24*inch, f"•  {need}")
        
        # Teaser
        c.setFillColor(GOLD)
        c.setFont(FONT_BODY_BOLD, 10)
        c.drawString(1*inch, 2.0*inch, "[How your Moon affects your relationships in full book]")
    
    # ==================== PAGE 7: QUIZ REFLECTION ====================
    def create_quiz_reflection_page(self):
        """Quiz reflection - ALWAYS shows content"""
        self.new_page()
        c = self.c
        
        sun_sign = self.person.get('sun_sign', 'Unknown')
        moon_sign = self.person.get('moon_sign', 'Unknown')
        
        self.draw_heading("What You Told Us", self.width/2, self.height - 1.3*inch, centered=True)
        self.draw_subheading("And what your chart reveals about why", self.width/2, self.height - 1.55*inch, centered=True)
        
        y = self.height - 2.0*inch
        
        # Box 1: Approval patterns
        need_liked = self.quiz.get('need_to_be_liked', '')
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y - 0.85*inch, self.width - 2*inch, 1.0*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BODY_BOLD, 10)
        if need_liked:
            c.drawString(1.2*inch, y - 0.15*inch, f'You said: "{need_liked}" to needing others\' approval')
        else:
            c.drawString(1.2*inch, y - 0.15*inch, "Your relationship with approval and validation")
        
        reflection = f"Your {sun_sign} Sun and {moon_sign} Moon create a specific pattern around approval-seeking that your full book addresses in depth."
        self.draw_text(reflection, 1.2*inch, y - 0.38*inch, self.width - 2.6*inch, size=9, line_height=12)
        
        y -= 1.15*inch
        
        # Box 2: Overthinking
        overthink = self.quiz.get('overthink_relationships', '')
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y - 0.85*inch, self.width - 2*inch, 1.0*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BODY_BOLD, 10)
        if overthink:
            c.drawString(1.2*inch, y - 0.15*inch, f'You said you "{overthink}" overthink relationships')
        else:
            c.drawString(1.2*inch, y - 0.15*inch, "Your emotional processing patterns")
        
        moon_pattern = self.moon_data.get('emotional_pattern', 'Your Moon reveals why you process emotions the way you do.')
        self.draw_text(moon_pattern, 1.2*inch, y - 0.38*inch, self.width - 2.6*inch, size=9, line_height=12)
        
        y -= 1.15*inch
        
        # Box 3: Dreams (navy)
        life_dreams = self.quiz.get('life_dreams', 'finding your true purpose')
        c.setFillColor(NAVY)
        c.roundRect(1*inch, y - 1.0*inch, self.width - 2*inch, 1.15*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BODY_BOLD, 10)
        c.drawString(1.2*inch, y - 0.15*inch, f'Your Dream: "{life_dreams}"')
        
        dream_insight = self.ai_insights.get('dream_insight', f"Your dream isn't random—your chart reveals why this calls to you deeply.")
        self.draw_text(dream_insight, 1.2*inch, y - 0.4*inch, self.width - 2.6*inch, size=10, line_height=13, color=white)
        
        # Locked teaser - FIXED POSITION
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawCentredString(self.width/2, 2.4*inch, "Your Full Psychological Profile")
        
        c.setFont(FONT_BODY, 9)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, 2.15*inch, "Based on your quiz + chart: childhood patterns, relationship triggers,")
        c.drawCentredString(self.width/2, 1.95*inch, "career blocks, and specific healing pathways")
        c.drawCentredString(self.width/2, 1.7*inch, "[Available in your complete book]")
    
    # ==================== PAGE 8: LOVE ====================
    def create_love_page(self):
        """Love and compatibility"""
        self.new_page()
        c = self.c
        
        self.draw_heading("Love & Compatibility", self.width/2, self.height - 1.3*inch, centered=True)
        self.draw_subheading("What the stars reveal about your heart", self.width/2, self.height - 1.55*inch, centered=True)
        
        # Venus
        venus = self.person.get('venus', 'Unknown')
        
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, self.height - 2.1*inch, 25)
        c.setFont(FONT_HEADING_BOLD, 16)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.16*inch, "V")
        
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 13)
        c.drawCentredString(self.width/2, self.height - 2.5*inch, f"Venus in {venus}")
        
        love_style = VENUS_LOVE_STYLES.get(venus, "Your Venus sign shapes how you give and receive love.")
        y = self.draw_text(love_style, 1*inch, self.height - 2.8*inch, self.width - 2*inch, size=10, line_height=14)
        
        # Compatibility section
        y -= 0.25*inch
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(1*inch, y, "Your Top Compatible Signs:")
        
        sun_sign = self.person.get('sun_sign', 'Aries')
        compatible = COMPATIBILITY_DATA.get(sun_sign, [('Leo', 'Fire Match', 90), ('Sagittarius', 'Adventure', 88), ('Aquarius', 'Unique Bond', 85)])
        
        y -= 0.35*inch
        for sign, match_type, score in compatible:
            c.setFillColor(CREAM)
            c.roundRect(1*inch, y - 0.12*inch, self.width - 2*inch, 0.45*inch, 5, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BODY_BOLD, 11)
            c.drawString(1.2*inch, y + 0.05*inch, sign)
            
            c.setFont(FONT_BODY, 10)
            c.setFillColor(HexColor('#666666'))
            c.drawString(2.8*inch, y + 0.05*inch, match_type)
            
            # Score bar
            c.setFillColor(HexColor('#e0e0e0'))
            c.rect(4.6*inch, y + 0.05*inch, 1.2*inch, 0.15*inch, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.rect(4.6*inch, y + 0.05*inch, 1.2*inch * (score/100), 0.15*inch, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BODY_BOLD, 9)
            c.drawString(5.9*inch, y + 0.05*inch, f"{score}%")
            
            y -= 0.55*inch
        
        # Locked box - FIXED POSITION
        c.setFillColor(NAVY)
        c.roundRect(1*inch, 2.0*inch, self.width - 2*inch, 1.0*inch, 10, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawCentredString(self.width/2, 2.75*inch, "In Your Full Book")
        
        c.setFillColor(white)
        c.setFont(FONT_BODY, 10)
        c.drawCentredString(self.width/2, 2.5*inch, "• Compatibility with ALL 12 signs • Your soulmate's chart signature")
        c.drawCentredString(self.width/2, 2.28*inch, "• Red flags your chart attracts • How to break your pattern")
    
    # ==================== PAGE 9: CAREER ====================
    def create_career_page(self):
        """Career and year ahead"""
        self.new_page()
        c = self.c
        
        sun_sign = self.person.get('sun_sign', 'Unknown')
        
        self.draw_heading("Career & Your Year Ahead", self.width/2, self.height - 1.3*inch, centered=True)
        self.draw_subheading("Purpose, timing, and opportunity", self.width/2, self.height - 1.55*inch, centered=True)
        
        # Career insight box
        career_q = self.quiz.get('career_question', '')
        c.setFillColor(CREAM)
        c.roundRect(1*inch, self.height - 2.7*inch, self.width - 2*inch, 0.95*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BODY_BOLD, 10)
        if career_q:
            display_q = career_q[:45] + "..." if len(career_q) > 45 else career_q
            c.drawString(1.2*inch, self.height - 1.95*inch, f'You asked: "{display_q}"')
        else:
            c.drawString(1.2*inch, self.height - 1.95*inch, f"Your {sun_sign} Career Path")
        
        career_insight = self.ai_insights.get('career_insight', f"Your {sun_sign} energy points to paths you haven't fully considered.")
        self.draw_text(career_insight, 1.2*inch, self.height - 2.2*inch, self.width - 2.6*inch, size=9, line_height=12)
        
        # Ideal careers - FIXED POSITION
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(1*inch, 6.5*inch, "Ideal Career Paths For You:")
        
        careers = self.sun_data.get('careers', ['Creative Field', 'Leadership', 'Consulting', 'Entrepreneurship', 'Healing Arts', 'Education'])
        c.setFont(FONT_BODY, 10)
        c.setFillColor(black)
        for i, career in enumerate(careers[:3]):
            c.drawString(1.2*inch, 6.2*inch - i*0.23*inch, f"•  {career}")
        for i, career in enumerate(careers[3:6]):
            c.drawString(4*inch, 6.2*inch - i*0.23*inch, f"•  {career}")
        
        # Key dates - FIXED POSITION
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawString(1*inch, 4.9*inch, "Key Dates: 2025-2026")
        
        dates = [
            ("Mar 2025", "Jupiter expansion—new opportunities appear"),
            ("Jun 2025", "Career breakthrough window opens"),
            ("Sep 2025", "Harvest time—past efforts pay off"),
            ("Jan 2026", "Fresh start energy for major changes"),
        ]
        
        date_y = 4.6*inch
        for date, event in dates:
            c.setFillColor(GOLD)
            c.setFont(FONT_BODY_BOLD, 9)
            c.drawString(1.2*inch, date_y, date)
            c.setFillColor(black)
            c.setFont(FONT_BODY, 9)
            c.drawString(2.0*inch, date_y, event)
            date_y -= 0.24*inch
        
        # Lucky elements - FIXED POSITION
        c.setFillColor(CREAM)
        c.roundRect(1*inch, 2.7*inch, self.width - 2*inch, 0.8*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 10)
        c.drawString(1.2*inch, 3.25*inch, "Your Lucky Elements:")
        
        c.setFont(FONT_BODY, 9)
        c.setFillColor(black)
        lucky_nums = self.sun_data.get('lucky_numbers', '3, 7, 9')
        lucky_colors = self.sun_data.get('lucky_colors', 'Gold, Purple')
        c.drawString(1.3*inch, 3.0*inch, f"Numbers: {lucky_nums}")
        c.drawString(4*inch, 3.0*inch, f"Colors: {lucky_colors}")
    
    # ==================== PAGE 10: CTA ====================
    def create_cta_page(self):
        """Call to action page"""
        self.new_page()
        c = self.c
        
        first_name = self.person.get('name', 'Friend').split()[0]
        
        self.draw_heading(f"{first_name}, This Was Just A Glimpse...", self.width/2, self.height - 1.3*inch, size=20, centered=True)
        
        # Blurred preview section
        c.setFillColor(HexColor('#f0f0f0'))
        c.roundRect(1*inch, self.height - 4.0*inch, self.width - 2*inch, 2.3*inch, 10, fill=1, stroke=0)
        c.setStrokeColor(HexColor('#cccccc'))
        c.roundRect(1*inch, self.height - 4.0*inch, self.width - 2*inch, 2.3*inch, 10, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 11)
        c.drawCentredString(self.width/2, self.height - 1.85*inch, "LOCKED: Your Complete Analysis")
        
        # Blurred items
        c.setFont(FONT_BODY, 10)
        c.setFillColor(HexColor('#999999'))
        locked_items = [
            "Your Deepest Fear:",
            "Your Hidden Superpower:",
            "Your Soulmate's Sun Sign:",
            "Career You'll Thrive In:",
            "Your Biggest Relationship Block:",
            "Best Day for Major Decisions:",
        ]
        
        item_y = self.height - 2.2*inch
        for item in locked_items:
            c.setFillColor(HexColor('#666666'))
            c.drawString(1.3*inch, item_y, item)
            # Draw blur bar
            c.setFillColor(HexColor('#cccccc'))
            c.rect(3.5*inch, item_y - 0.02*inch, 2.5*inch, 0.18*inch, fill=1, stroke=0)
            item_y -= 0.28*inch
        
        # Features list - FIXED POSITION
        c.setFillColor(NAVY)
        c.setFont(FONT_HEADING_BOLD, 12)
        c.drawCentredString(self.width/2, 4.6*inch, "Your Complete Orastria Book Unlocks:")
        
        features = [
            "60+ pages written for YOUR exact birth chart",
            "Full compatibility with all 12 signs",
            "Month-by-month 2025-2026 predictions",
            "Shadow work specific to your placements",
            "Your ideal partner's chart signature",
        ]
        
        c.setFont(FONT_BODY, 10)
        c.setFillColor(black)
        feat_y = 4.3*inch
        for feature in features:
            c.drawString(1.3*inch, feat_y, f"✓  {feature}")
            feat_y -= 0.24*inch
        
        # CTA box - FIXED POSITION
        c.setFillColor(NAVY)
        c.roundRect(1*inch, 1.7*inch, self.width - 2*inch, 1.5*inch, 15, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 14)
        c.drawCentredString(self.width/2, 2.95*inch, "Unlock Your Complete Blueprint")
        
        c.setFillColor(white)
        c.setFont(FONT_BODY_BOLD, 12)
        c.drawCentredString(self.width/2, 2.65*inch, "Get 50% Off — Limited Time")
        
        # Price
        c.setFillColor(HexColor('#888888'))
        c.setFont(FONT_BODY, 11)
        c.drawString(self.width/2 - 35, 2.3*inch, "$49.99")
        c.line(self.width/2 - 40, 2.35*inch, self.width/2, 2.35*inch)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_HEADING_BOLD, 16)
        c.drawString(self.width/2 + 10, 2.3*inch, "$24.99")
        
        c.setFillColor(white)
        c.setFont(FONT_BODY, 9)
        c.drawCentredString(self.width/2, 2.0*inch, "Instant PDF Delivery  •  30-Day Money Back Guarantee")
    
    # ==================== BUILD ====================
    def build(self):
        """Generate the complete book"""
        print(f"📖 Building personalized sample book for {self.person.get('name', 'Unknown')}...")
        
        self.create_cover()
        self.create_intro_page()
        self.create_birth_chart_page()
        self.create_big_three_page()
        self.create_sun_sign_page()
        self.create_moon_sign_page()
        self.create_quiz_reflection_page()
        self.create_love_page()
        self.create_career_page()
        self.create_cta_page()
        
        self.c.save()
        print(f"✅ Sample book generated: {self.output_path}")
        return self.output_path


# Alias for compatibility
OrastriaBookGenerator = OrastriaSampleBookV4


# ==================== TESTING ====================
if __name__ == "__main__":
    print("🌟 Testing Orastria Sample Book v4...")
    
    test_person = {
        'name': 'Hassan ElHouadi',
        'birth_date': 'February 28, 1955',
        'birth_time': '05:20 PM',
        'birth_place': 'Paris, France',
        'sun_sign': 'Pisces',
        'moon_sign': 'Taurus',
        'rising_sign': 'Leo',
        'venus': 'Capricorn',
        'mars': 'Taurus',
        'mercury': 'Aquarius',
    }
    
    test_quiz = {}
    
    book = OrastriaSampleBookV4('/tmp/test_sample_v4.pdf', test_person, test_quiz)
    book.build()
    
    print("\n✨ Test complete!")
