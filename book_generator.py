"""
Orastria Sample Book Generator v3
DEEPLY PERSONALIZED - Makes readers feel SEEN
- Rich pre-written zodiac content (not generic)
- Quiz answer integration
- One Claude API call for 4 "wow" sentences
- Blurred preview section for FOMO
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

# ==================== FONT SETUP ====================
def find_font(font_name):
    """Find font file path across different systems"""
    import glob
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

dejavu_regular = find_font('DejaVuSans.ttf')
dejavu_bold = find_font('DejaVuSans-Bold.ttf')

if dejavu_regular:
    pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_regular))
if dejavu_bold:
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold))

FONT_REGULAR = 'DejaVuSans' if dejavu_regular else 'Helvetica'
FONT_BOLD = 'DejaVuSans-Bold' if dejavu_bold else 'Helvetica-Bold'
FONTS_AVAILABLE = dejavu_regular is not None

# ==================== BRAND COLORS ====================
NAVY = HexColor('#1a1f3c')
GOLD = HexColor('#c9a961')
CREAM = HexColor('#f5f0e8')
SOFT_GOLD = HexColor('#d4b87a')
LIGHT_NAVY = HexColor('#2d3561')

# ==================== ZODIAC SYMBOLS ====================
ZODIAC_SYMBOLS = {
    'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
    'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
    'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
}

# ==================== DEEP ZODIAC DATA ====================
# This is the KEY - real, specific content that makes people feel SEEN

ZODIAC_DEEP_DATA = {
    'Aries': {
        'core_essence': "You don't just enter a room—you ignite it. Your Aries Sun gives you a warrior's spirit wrapped in impatience. You start things brilliantly but finishing them? That's where your chart gets complicated.",
        'secret_wound': "being told to slow down, wait your turn, or think before you act—when your whole being screams to MOVE",
        'hidden_fear': "that if you stop pushing forward, you'll realize you don't know who you are when you're still",
        'what_others_miss': "behind your confidence is someone who genuinely doesn't understand why everyone else hesitates so much",
        'relationship_pattern': "you chase hard, win them over, then wonder why the spark fades once there's no challenge left",
        'core_traits': ['Fearlessly direct', 'Impatiently passionate', 'Competitively driven', 'Instinctively protective', 'Restlessly energetic', 'Courageously honest'],
        'strengths': ['Starting what others only talk about', 'Defending the underdog without hesitation', 'Bouncing back faster than anyone expects', 'Making bold moves others admire'],
        'careers': ['Entrepreneur', 'Emergency Services', 'Sports/Athletics', 'Sales Leader', 'Military/Defense', 'Startup Founder'],
        'lucky_numbers': '1, 9, 17, 28',
        'lucky_colors': 'Red, Orange, Gold',
        'element': 'Fire',
        'modality': 'Cardinal',
    },
    'Taurus': {
        'core_essence': "You're not stubborn—you're certain. Your Taurus Sun gives you an unshakeable core that others mistake for inflexibility. You simply know what you want and refuse to apologize for it.",
        'secret_wound': "being rushed, pressured to change, or told your need for security is a weakness",
        'hidden_fear': "that the ground beneath you will shift before you're ready—that stability is just an illusion",
        'what_others_miss': "your sensuality runs deeper than pleasure—you experience life through touch, taste, and texture in ways others can't fathom",
        'relationship_pattern': "you take forever to commit, but once you do, you'll weather any storm—except betrayal, which you never forget",
        'core_traits': ['Unshakeably loyal', 'Sensually grounded', 'Patiently determined', 'Quietly strong', 'Materially savvy', 'Stubbornly devoted'],
        'strengths': ['Building wealth and security from nothing', 'Creating beauty in everyday moments', 'Standing firm when others crumble', 'Providing comfort that heals'],
        'careers': ['Financial Advisor', 'Chef/Restaurateur', 'Interior Designer', 'Real Estate', 'Music/Voice Artist', 'Luxury Brand Manager'],
        'lucky_numbers': '2, 6, 15, 24',
        'lucky_colors': 'Green, Pink, Earth tones',
        'element': 'Earth',
        'modality': 'Fixed',
    },
    'Gemini': {
        'core_essence': "Your mind never stops—and that's both your superpower and your curse. Your Gemini Sun processes information faster than others can speak. You're not two-faced; you're multi-dimensional.",
        'secret_wound': "being called shallow, flaky, or 'too much' when you're just trying to experience everything life offers",
        'hidden_fear': "that you'll never find someone or something interesting enough to hold your attention forever",
        'what_others_miss': "your constant movement isn't avoidance—it's how you process a world that would overwhelm most people",
        'relationship_pattern': "you need mental stimulation as much as emotional connection—bore you and you'll ghost without meaning to",
        'core_traits': ['Intellectually restless', 'Verbally gifted', 'Adaptively curious', 'Socially versatile', 'Mentally agile', 'Charmingly scattered'],
        'strengths': ['Connecting ideas no one else sees', 'Making anyone feel interesting', 'Learning faster than seems possible', 'Talking your way into (or out of) anything'],
        'careers': ['Journalist/Writer', 'Marketing/PR', 'Teacher/Professor', 'Podcaster/Content Creator', 'Sales/Negotiations', 'Tech/Programming'],
        'lucky_numbers': '3, 5, 14, 23',
        'lucky_colors': 'Yellow, Light Blue, Silver',
        'element': 'Air',
        'modality': 'Mutable',
    },
    'Cancer': {
        'core_essence': "You feel everything—and you remember it all. Your Cancer Sun gives you emotional sonar that picks up what others miss. Your shell isn't weakness; it's wisdom from wounds that made you stronger.",
        'secret_wound': "having your sensitivity used against you, being told you're 'too emotional' when you're actually too perceptive",
        'hidden_fear': "that the people you nurture will leave once they no longer need you",
        'what_others_miss': "your 'moodiness' is actually you processing everyone's emotions in the room, not just your own",
        'relationship_pattern': "you give until empty, then retreat into your shell wondering why no one noticed you were drowning",
        'core_traits': ['Deeply intuitive', 'Fiercely protective', 'Emotionally intelligent', 'Nostalgically sentimental', 'Nurturingly devoted', 'Psychically sensitive'],
        'strengths': ['Creating home wherever you go', 'Reading people before they speak', 'Remembering what matters to others', 'Loving with your whole being'],
        'careers': ['Therapist/Counselor', 'Chef/Baker', 'Nurse/Healthcare', 'Real Estate/Property', 'Social Worker', 'Historian/Genealogist'],
        'lucky_numbers': '2, 7, 11, 20',
        'lucky_colors': 'Silver, White, Sea Green',
        'element': 'Water',
        'modality': 'Cardinal',
    },
    'Leo': {
        'core_essence': "You're not seeking attention—you're radiating energy you can't contain. Your Leo Sun makes you impossible to ignore, and honestly, why would you want to be? You were born to be seen.",
        'secret_wound': "being overlooked, dismissed, or made to feel your light is 'too bright' for others' comfort",
        'hidden_fear': "that without an audience, without impact, you might not matter at all",
        'what_others_miss': "your need for appreciation isn't ego—it's a genuine desire to know your warmth reaches others",
        'relationship_pattern': "you love grandly and generously, but sulk dramatically when that love isn't visibly reciprocated",
        'core_traits': ['Magnetically confident', 'Generously warm', 'Dramatically expressive', 'Loyally protective', 'Creatively bold', 'Royally dignified'],
        'strengths': ['Inspiring others just by showing up', 'Leading without trying', 'Making everyone feel special', 'Turning ordinary into extraordinary'],
        'careers': ['Actor/Performer', 'CEO/Executive', 'Event Planner', 'Creative Director', 'Motivational Speaker', 'Influencer/Public Figure'],
        'lucky_numbers': '1, 5, 9, 19',
        'lucky_colors': 'Gold, Orange, Royal Purple',
        'element': 'Fire',
        'modality': 'Fixed',
    },
    'Virgo': {
        'core_essence': "Your mind is a precision instrument that notices what others overlook. Your Virgo Sun isn't critical—it's discerning. You see potential everywhere, including all the ways it could be better.",
        'secret_wound': "being called nitpicky or negative when you're just trying to help things reach their potential",
        'hidden_fear': "that despite all your effort to be useful and perfect, you'll still somehow not be enough",
        'what_others_miss': "your criticism of others is nothing compared to the relentless standards you hold yourself to",
        'relationship_pattern': "you show love through acts of service, then feel hurt when others don't notice the invisible labor",
        'core_traits': ['Analytically precise', 'Helpfully devoted', 'Practically grounded', 'Quietly perfectionist', 'Observantly intelligent', 'Modestly capable'],
        'strengths': ['Solving problems others cannot see', 'Creating order from chaos', 'Noticing details that matter', 'Being reliable when it counts'],
        'careers': ['Data Analyst', 'Healthcare/Medicine', 'Editor/Writer', 'Accountant/Finance', 'Quality Assurance', 'Nutritionist/Wellness'],
        'lucky_numbers': '5, 14, 23, 32',
        'lucky_colors': 'Navy, Gray, Forest Green',
        'element': 'Earth',
        'modality': 'Mutable',
    },
    'Libra': {
        'core_essence': "You see both sides of everything—which is why deciding feels impossible. Your Libra Sun craves harmony so deeply that conflict feels like physical pain. You're not indecisive; you're comprehensive.",
        'secret_wound': "being forced to choose sides, deal with ugliness, or accept that some situations have no fair solution",
        'hidden_fear': "that if you state your true opinion, someone will be hurt, and the balance will be destroyed",
        'what_others_miss': "your people-pleasing isn't weakness—it's a sophisticated strategy to keep the peace you desperately need",
        'relationship_pattern': "you mirror partners so perfectly they fall for a reflection, then wonder why you feel unseen",
        'core_traits': ['Diplomatically graceful', 'Aesthetically refined', 'Socially intelligent', 'Harmoniously balanced', 'Romantically idealistic', 'Intellectually fair'],
        'strengths': ['Making others feel heard and valued', 'Creating beauty wherever you go', 'Finding compromise in impossible situations', 'Building connections that last'],
        'careers': ['Lawyer/Mediator', 'Interior Designer', 'Diplomat/PR', 'Wedding Planner', 'Art Director', 'Human Resources'],
        'lucky_numbers': '6, 15, 24, 33',
        'lucky_colors': 'Pink, Light Blue, Lavender',
        'element': 'Air',
        'modality': 'Cardinal',
    },
    'Scorpio': {
        'core_essence': "You don't do surface-level anything. Your Scorpio Sun experiences life at depths others find terrifying. You're not intense—you're fully alive while others sleepwalk through existence.",
        'secret_wound': "being betrayed by someone you let past your walls, proving that vulnerability is dangerous",
        'hidden_fear': "that if people saw the full truth of your darkness, they'd run—and never come back",
        'what_others_miss': "your suspicion isn't paranoia—you simply see the shadows others pretend don't exist",
        'relationship_pattern': "you test loyalty repeatedly, pushing people away to see who'll fight to stay",
        'core_traits': ['Intensely passionate', 'Psychologically perceptive', 'Magnetically powerful', 'Fiercely loyal', 'Transformatively resilient', 'Mysteriously deep'],
        'strengths': ['Seeing through lies instantly', 'Rising from any destruction', 'Creating profound intimacy', 'Wielding power without force'],
        'careers': ['Psychologist/Therapist', 'Detective/Investigator', 'Surgeon/Medical', 'Financial Strategist', 'Crisis Manager', 'Researcher'],
        'lucky_numbers': '8, 11, 18, 22',
        'lucky_colors': 'Black, Burgundy, Deep Red',
        'element': 'Water',
        'modality': 'Fixed',
    },
    'Sagittarius': {
        'core_essence': "You're allergic to limitation in all its forms. Your Sagittarius Sun needs freedom like others need air. You're not commitment-phobic—you just refuse to shrink yourself to fit small spaces.",
        'secret_wound': "being caged, controlled, or told to be 'realistic' about your impossibly expansive dreams",
        'hidden_fear': "that you'll run out of new horizons—that someday, there will be nothing left to explore",
        'what_others_miss': "your bluntness isn't cruelty—you genuinely believe the truth sets people free",
        'relationship_pattern': "you idealize the chase, then feel trapped once you've 'won'—not because love isn't real, but because routine feels like death",
        'core_traits': ['Expansively optimistic', 'Philosophically curious', 'Adventurously bold', 'Honestly blunt', 'Restlessly free', 'Inspiringly enthusiastic'],
        'strengths': ['Inspiring others to think bigger', 'Finding meaning in chaos', 'Turning disasters into adventures', 'Speaking truth others will not'],
        'careers': ['Travel/Tourism', 'Professor/Teacher', 'Publisher/Writer', 'Life Coach', 'International Business', 'Philosophy/Theology'],
        'lucky_numbers': '3, 9, 12, 21',
        'lucky_colors': 'Purple, Turquoise, Orange',
        'element': 'Fire',
        'modality': 'Mutable',
    },
    'Capricorn': {
        'core_essence': "You're playing a longer game than anyone realizes. Your Capricorn Sun makes you ancient beyond your years—you were born knowing life is hard and decided to become harder.",
        'secret_wound': "being forced to grow up too fast, carry too much responsibility, or achieve without acknowledgment",
        'hidden_fear': "that despite all your sacrifice and discipline, you'll reach the top only to find it empty",
        'what_others_miss': "your coldness is protection—underneath that armor is someone who feels deeply but can't afford to show it",
        'relationship_pattern': "you choose partners like investments, then struggle to access emotions you've suppressed for efficiency",
        'core_traits': ['Ambitiously driven', 'Practically wise', 'Responsibly mature', 'Strategically patient', 'Quietly powerful', 'Traditionally grounded'],
        'strengths': ['Building empires from nothing', 'Maintaining composure in crisis', 'Playing the long game masterfully', 'Earning respect without demanding it'],
        'careers': ['CEO/Executive', 'Finance/Banking', 'Government/Politics', 'Architecture/Engineering', 'Law', 'Business Owner'],
        'lucky_numbers': '4, 8, 13, 22',
        'lucky_colors': 'Black, Brown, Dark Green',
        'element': 'Earth',
        'modality': 'Cardinal',
    },
    'Aquarius': {
        'core_essence': "You're living in a future others haven't imagined yet. Your Aquarius Sun makes you feel like an alien—because you're here to change things, not fit in.",
        'secret_wound': "being called weird, cold, or 'too much' when you're just being authentically yourself",
        'hidden_fear': "that your difference makes you unlovable—that intimacy requires losing your uniqueness",
        'what_others_miss': "your detachment isn't lack of feeling—it's how you survive feeling connected to all of humanity at once",
        'relationship_pattern': "you need intellectual equals who won't try to domesticate you, but you'll run from anyone who gets too close",
        'core_traits': ['Radically original', 'Intellectually rebellious', 'Humanistically idealistic', 'Emotionally detached', 'Futuristically visionary', 'Stubbornly independent'],
        'strengths': ['Seeing solutions invisible to others', 'Challenging systems that need breaking', 'Befriending anyone authentically', 'Staying true to yourself always'],
        'careers': ['Tech/Innovation', 'Social Activism', 'Science/Research', 'Aviation/Space', 'Humanitarian Work', 'Inventor/Creator'],
        'lucky_numbers': '4, 7, 11, 22',
        'lucky_colors': 'Electric Blue, Silver, Violet',
        'element': 'Air',
        'modality': 'Fixed',
    },
    'Pisces': {
        'core_essence': "You absorb emotions like a sponge—sometimes not knowing where others end and you begin. Your Pisces Sun connects you to something beyond the visible world.",
        'secret_wound': "being called 'too sensitive' when you're actually too perceptive for a world that rewards numbness",
        'hidden_fear': "that reality will crush the magic you work so hard to preserve inside yourself",
        'what_others_miss': "your escapism isn't weakness—it's survival in a world that feels unbearably harsh to your unfiltered soul",
        'relationship_pattern': "you fall for potential, not reality—loving who someone could be while ignoring who they are",
        'core_traits': ['Spiritually intuitive', 'Emotionally boundless', 'Creatively gifted', 'Compassionately selfless', 'Dreamily imaginative', 'Psychically sensitive'],
        'strengths': ['Healing others with your presence', 'Creating art from pain', 'Understanding without words', 'Accessing realms others can\'t'],
        'careers': ['Artist/Musician', 'Healer/Therapist', 'Spiritual Guide', 'Filmmaker/Photographer', 'Nurse/Caregiver', 'Marine Biology'],
        'lucky_numbers': '3, 7, 12, 21',
        'lucky_colors': 'Sea Green, Lavender, Silver',
        'element': 'Water',
        'modality': 'Mutable',
    },
}

# ==================== MOON SIGN DATA ====================
MOON_DEEP_DATA = {
    'Aries': {
        'essence': "Your emotional responses are instant and fierce. You process feelings by taking action—sitting with emotions feels unbearable. You need to move, fight, or fix something.",
        'needs': ['Freedom to express anger', 'Action over discussion', 'Independence in relationships', 'A partner who can handle intensity'],
        'emotional_pattern': "You fall fast, burn hot, and move on quickly—not from lack of depth, but because your heart processes at lightning speed.",
    },
    'Taurus': {
        'essence': "Your emotions move like honey—slowly, sweetly, and with staying power. Once you feel something, it takes root. You process through physical comfort and sensory experience.",
        'needs': ['Physical affection and touch', 'Financial security', 'Routine and predictability', 'Beauty in your environment'],
        'emotional_pattern': "You're the person who replays the same song when sad, craves comfort food when stressed, and stays loyal long past expiration dates.",
    },
    'Gemini': {
        'essence': "You process emotions by talking them out—sometimes with others, sometimes just with yourself. Your feelings need intellectual understanding before you can fully feel them.",
        'needs': ['Mental stimulation always', 'Variety in emotional expression', 'A partner who talks through everything', 'Space to change your mind'],
        'emotional_pattern': "You can rationalize any feeling until it almost disappears—which is both your superpower and your avoidance strategy.",
    },
    'Cancer': {
        'essence': "Your emotional world is oceanic—deep, tidal, and full of currents no one else can see. You feel the emotional temperature of every room you enter.",
        'needs': ['A safe home base to return to', 'Emotional reciprocity', 'Permission to nurture', 'Connection to family or chosen family'],
        'emotional_pattern': "You remember every emotional slight—not from bitterness, but because your heart literally cannot forget how things felt.",
    },
    'Leo': {
        'essence': "Your emotions want an audience—not for validation, but because feelings this big deserve to be witnessed. You process through expression and recognition.",
        'needs': ['Appreciation and admiration', 'Creative emotional outlets', 'Loyalty from your inner circle', 'Dramatic gestures of love'],
        'emotional_pattern': "When hurt, you either roar or retreat into dignified silence—there's no in-between for a wounded Leo Moon.",
    },
    'Virgo': {
        'essence': "You process emotions by analyzing them, categorizing them, and figuring out how to fix them. Messiness in feelings makes you anxious.",
        'needs': ['Order and routine', 'Feeling useful to others', 'Health and wellness practices', 'A partner who appreciates your help'],
        'emotional_pattern': "You show love through acts of service, then feel invisible when others don't notice the thousand small things you do.",
    },
    'Libra': {
        'essence': "Your emotional wellbeing is tied to harmony around you. Discord hits you physically—you literally cannot relax when conflict exists.",
        'needs': ['Partnership above all', 'Beauty and aesthetics', 'Peaceful environments', 'Feeling chosen and valued'],
        'emotional_pattern': "You suppress your needs to keep the peace, then resent others for not reading your mind.",
    },
    'Scorpio': {
        'essence': "Your emotions run to depths that would terrify most people. You don't just feel sad—you plunge into the underworld of grief and emerge transformed.",
        'needs': ['Absolute emotional honesty', 'Privacy for processing', 'Intense intimate connection', 'Power over your own life'],
        'emotional_pattern': "You test people's loyalty before letting them close, pushing to see who'll fight to stay.",
    },
    'Sagittarius': {
        'essence': "You process emotions by finding their meaning—every feeling must lead to wisdom, growth, or a good story. Pointless pain is unbearable.",
        'needs': ['Freedom from emotional obligation', 'Adventure and new experiences', 'Philosophical understanding', 'A partner who grows with you'],
        'emotional_pattern': "You escape difficult emotions through movement, travel, or humor—sitting with discomfort feels like death.",
    },
    'Capricorn': {
        'essence': "Your emotions are disciplined, controlled, and often postponed for more convenient times. You learned early that feelings are a luxury.",
        'needs': ['Respect and recognition', 'Achievement and progress', 'Stability in relationships', 'Time to process privately'],
        'emotional_pattern': "You struggle to access feelings in real-time, processing them days or years later when it's 'safe.'",
    },
    'Aquarius': {
        'essence': "You intellectualize emotions to survive them. Feelings are fascinating phenomena to observe—from a safe distance inside your own head.",
        'needs': ['Space and independence', 'Intellectual connection', 'Freedom to be unconventional', 'Friends who feel like found family'],
        'emotional_pattern': "You care deeply about humanity but struggle with one-on-one emotional intimacy—crowds feel safer than closeness.",
    },
    'Pisces': {
        'essence': "Your emotional boundaries are permeable—you feel everything around you, absorbing others' pain and joy until you can't tell what's yours.",
        'needs': ['Alone time to decompress', 'Creative and spiritual outlets', 'Gentle, non-judgmental love', 'Escape hatches from harsh reality'],
        'emotional_pattern': "You'd rather suffer in silence than burden others, then wonder why no one comes to rescue you.",
    },
}

# ==================== VENUS LOVE STYLES ====================
VENUS_LOVE_STYLES = {
    'Aries': "You love like a conquest—the chase is intoxicating, but keeping that fire alive after you've 'won' is your real challenge.",
    'Taurus': "You love through devotion and physical presence. For you, real love is showing up consistently, building something tangible and lasting.",
    'Gemini': "You love through conversation and intellectual flirtation. A partner who bores you mentally will lose you, no matter how attractive.",
    'Cancer': "You love by nurturing and creating emotional sanctuary. Your love is protective, sometimes possessive, always deeply felt.",
    'Leo': "You love grandly and expect to be adored in return. For you, love should feel like being chosen above all others, every single day.",
    'Virgo': "You love through acts of service and attention to detail. You show devotion by noticing what others need before they ask.",
    'Libra': "You love through partnership and romance. You need a plus-one for life—someone who makes you feel complete.",
    'Scorpio': "You love with volcanic intensity. Casual isn't in your vocabulary—you want soul-merging depth or nothing at all.",
    'Sagittarius': "You love through shared adventure and growth. A partner who clips your wings will lose you to the horizon.",
    'Capricorn': "You love by building—a life, a legacy, a future. Your devotion shows through commitment and provision, not poetry.",
    'Aquarius': "You love from a slight distance—intimacy without possessiveness. You need a partner who's also a best friend and fellow weirdo.",
    'Pisces': "You love transcendently, seeing your partner's soul more than their flaws. The danger is loving potential instead of reality.",
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

# ==================== REPLICATE API INTEGRATION ====================
REPLICATE_URL = os.environ.get('REPLICATE_MODEL_URL', 'https://api.replicate.com/v1/models/anthropic/claude-3.5-sonnet/predictions')
REPLICATE_API_KEY = os.environ.get('REPLICATE_API_KEY', '')


def generate_ai_insights(name, sun_sign, moon_sign, rising_sign, quiz_data):
    """
    Generate 4 personalized 'wow' sentences using Replicate API (Claude)
    Cost: ~$0.008 per book
    """
    if not REPLICATE_API_KEY:
        print("⚠️ No REPLICATE_API_KEY found, using fallback insights")
        return get_fallback_insights(name, sun_sign, moon_sign, quiz_data)
    
    # Extract key quiz answers
    need_to_be_liked = quiz_data.get('need_to_be_liked', '')
    overthink = quiz_data.get('overthink_relationships', '')
    life_dreams = quiz_data.get('life_dreams', '')
    career_question = quiz_data.get('career_question', '')
    decision_worry = quiz_data.get('decision_worry', '')
    relationship_status = quiz_data.get('relationship_status', '')
    
    prompt = f"""You are writing personalized astrology insights for {name}'s sample book.

Their chart: {sun_sign} Sun, {moon_sign} Moon, {rising_sign} Rising

What they shared in their quiz:
- Need to be liked: {need_to_be_liked}
- Overthinks relationships: {overthink}
- Life dream: {life_dreams}
- Career question: {career_question}
- Decision worry: {decision_worry}
- Relationship status: {relationship_status}

Write exactly 4 sentences, labeled 1-4. Each should feel like a "holy shit, that's me" moment:

1. Connect their {sun_sign} Sun to their approval/validation patterns. Make it specific and slightly uncomfortable in its accuracy.

2. Connect their {moon_sign} Moon to how they overthink or process emotions in relationships. Reference their actual patterns.

3. Write about their life dream ({life_dreams}) in a way that hints at deeper psychological meaning. Make them want to know more.

4. Address their career question ({career_question}) by connecting it to their chart. Give a teaser insight that makes them need the full book.

Rules:
- Be specific, not generic
- Use "you" language
- Each sentence should stand alone (they go on different pages)
- Make them feel SEEN, almost uncomfortably so
- Keep each sentence under 40 words"""

    try:
        # Create prediction
        response = requests.post(
            REPLICATE_URL,
            headers={
                'Authorization': f'Bearer {REPLICATE_API_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'wait'  # Wait for result instead of polling
            },
            json={
                'input': {
                    'prompt': prompt,
                    'max_tokens': 400
                }
            },
            timeout=60
        )
        
        if response.ok:
            result = response.json()
            
            # Handle different response formats
            if 'output' in result:
                content = result['output']
                if isinstance(content, list):
                    content = ''.join(content)
            elif 'predictions' in result:
                content = result['predictions'][0].get('output', '')
            else:
                content = str(result)
            
            print(f"✅ Replicate API returned insights")
            return parse_ai_response(content)
        else:
            print(f"⚠️ Replicate API error: {response.status_code} - {response.text[:200]}")
            return get_fallback_insights(name, sun_sign, moon_sign, quiz_data)
            
    except Exception as e:
        print(f"⚠️ Replicate API exception: {e}")
        return get_fallback_insights(name, sun_sign, moon_sign, quiz_data)


def parse_ai_response(content):
    """Parse the 4 numbered sentences from Claude's response"""
    insights = {
        'sun_insight': '',
        'moon_insight': '',
        'dream_insight': '',
        'career_insight': ''
    }
    
    lines = content.strip().split('\n')
    current_num = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('1'):
            current_num = 'sun_insight'
            insights[current_num] = line.lstrip('1.').strip()
        elif line.startswith('2'):
            current_num = 'moon_insight'
            insights[current_num] = line.lstrip('2.').strip()
        elif line.startswith('3'):
            current_num = 'dream_insight'
            insights[current_num] = line.lstrip('3.').strip()
        elif line.startswith('4'):
            current_num = 'career_insight'
            insights[current_num] = line.lstrip('4.').strip()
        elif current_num and line:
            insights[current_num] += ' ' + line
    
    return insights


def get_fallback_insights(name, sun_sign, moon_sign, quiz_data):
    """Fallback insights if Claude API is unavailable"""
    first_name = name.split()[0]
    
    sun_data = ZODIAC_DEEP_DATA.get(sun_sign, {})
    moon_data = MOON_DEEP_DATA.get(moon_sign, {})
    
    return {
        'sun_insight': f"Your {sun_sign} Sun means you've likely been told you're 'too much'—{sun_data.get('secret_wound', 'but what others see as excess is simply your authentic intensity')}.",
        'moon_insight': f"With your {moon_sign} Moon, {moon_data.get('emotional_pattern', 'your emotional world runs deeper than others realize')}.",
        'dream_insight': f"Your dream of '{quiz_data.get('life_dreams', 'something greater')}' isn't random—your chart reveals exactly why this calls to you so deeply.",
        'career_insight': f"The career fulfillment you're seeking exists—and your {sun_sign} energy points to paths you haven't fully considered yet."
    }


# ==================== MAIN BOOK CLASS ====================
class OrastriaSampleBookV3:
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
        print("🤖 Generating personalized AI insights...")
        self.ai_insights = generate_ai_insights(
            self.person.get('name', 'Friend'),
            self.person.get('sun_sign', 'Unknown'),
            self.person.get('moon_sign', 'Unknown'),
            self.person.get('rising_sign', 'Unknown'),
            self.quiz
        )
        print("✅ AI insights ready")
        
        # Get zodiac data
        self.sun_data = ZODIAC_DEEP_DATA.get(self.person.get('sun_sign'), ZODIAC_DEEP_DATA['Aries'])
        self.moon_data = MOON_DEEP_DATA.get(self.person.get('moon_sign'), MOON_DEEP_DATA['Aries'])
    
    def get_symbol(self, sign):
        """Get zodiac symbol"""
        if FONTS_AVAILABLE:
            return ZODIAC_SYMBOLS.get(sign, '★')
        return f"[{sign[:3]}]"
    
    def draw_border(self):
        """Draw elegant border"""
        c = self.c
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        margin = 0.5 * inch
        c.rect(margin, margin, self.width - 2*margin, self.height - 2*margin)
        
        # Corner stars
        c.setFont(FONT_REGULAR, 12)
        c.setFillColor(GOLD)
        corners = [(margin + 10, margin + 5), (self.width - margin - 10, margin + 5),
                   (margin + 10, self.height - margin - 15), (self.width - margin - 10, self.height - margin - 15)]
        for x, y in corners:
            c.drawCentredString(x, y, '✦')
    
    def add_page_number(self):
        """Add page number"""
        self.page_num += 1
        self.c.setFillColor(GOLD)
        self.c.setFont(FONT_REGULAR, 10)
        self.c.drawCentredString(self.width / 2, 0.6 * inch, f"— {self.page_num} —")
    
    def new_page(self):
        """Start new page with border"""
        self.c.showPage()
        self.draw_border()
        self.add_page_number()
    
    def draw_text(self, text, x, y, width, size=11, line_height=14, color=black, font=None):
        """Draw wrapped text"""
        c = self.c
        font = font or FONT_REGULAR
        c.setFillColor(color)
        c.setFont(font, size)
        
        words = text.split()
        current_line = ''
        current_y = y
        
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            if c.stringWidth(test_line, font, size) < width:
                current_line = test_line
            else:
                c.drawString(x, current_y, current_line)
                current_y -= line_height
                current_line = word
        
        if current_line:
            c.drawString(x, current_y, current_line)
            current_y -= line_height
        
        return current_y
    
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
        
        # Top celestial symbols
        c.setFont(FONT_BOLD, 24)
        c.setFillColor(GOLD)
        c.drawCentredString(0.8*inch, self.height - 0.8*inch, '☉')
        c.drawCentredString(self.width - 0.8*inch, self.height - 0.8*inch, '☽')
        
        # Title
        c.setFont(FONT_BOLD, 32)
        c.drawCentredString(self.width/2, self.height - 1.8*inch, "YOUR COSMIC")
        c.drawCentredString(self.width/2, self.height - 2.25*inch, "BLUEPRINT")
        
        # Line
        c.line(2.2*inch, self.height - 2.5*inch, self.width - 2.2*inch, self.height - 2.5*inch)
        
        # Name
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 26)
        c.drawCentredString(self.width/2, self.height - 3.2*inch, self.person.get('name', 'Friend'))
        
        # Birth info
        c.setFillColor(SOFT_GOLD)
        c.setFont(FONT_REGULAR, 12)
        birth_date = self.person.get('birth_date', '')
        birth_time = self.person.get('birth_time', '')
        birth_place = self.person.get('birth_place', '')
        c.drawCentredString(self.width/2, self.height - 3.6*inch, f"{birth_date}  •  {birth_time}")
        c.drawCentredString(self.width/2, self.height - 3.85*inch, birth_place)
        
        # Central zodiac circle
        center_y = self.height / 2 - 0.3*inch
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, center_y, 85)
        c.setLineWidth(1)
        c.circle(self.width/2, center_y, 95)
        
        # Main zodiac symbol
        sun_sign = self.person.get('sun_sign', 'Aries')
        c.setFont(FONT_BOLD, 64)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, center_y - 20, self.get_symbol(sun_sign))
        
        # Sign name
        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(self.width/2, center_y - 55, sun_sign.upper())
        
        # Big Three
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(white)
        moon_sign = self.person.get('moon_sign', 'Unknown')
        rising_sign = self.person.get('rising_sign', 'Unknown')
        big_three = f"☉ Sun: {sun_sign}  •  ☽ Moon: {moon_sign}  •  ↑ Rising: {rising_sign}"
        c.drawCentredString(self.width/2, center_y - 115, big_three)
        
        # Bottom branding
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 20)
        c.drawCentredString(self.width/2, 1.3*inch, "ORASTRIA")
        c.setFont(FONT_REGULAR, 10)
        c.drawCentredString(self.width/2, 1*inch, "Personalized Astrology  •  Written in the Stars")
    
    # ==================== PAGE 2: THE STARS WERE WATCHING ====================
    def create_intro_page(self):
        """Emotional hook intro"""
        self.new_page()
        c = self.c
        
        first_name = self.person.get('name', 'Friend').split()[0]
        sun_sign = self.person.get('sun_sign', 'Unknown')
        
        # Header
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "The Stars Were Watching")
        
        c.setFont(FONT_REGULAR, 14)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "✧  ✦  ✧")
        
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

        self.draw_text(intro, 1*inch, self.height - 2*inch, self.width - 2*inch, size=11, line_height=15)
        
        # Rarity box
        y_box = 3.2*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.5*inch, self.width - 2*inch, 1.3*inch, 10, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.5*inch, self.width - 2*inch, 1.3*inch, 10, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 13)
        c.drawCentredString(self.width/2, y_box + 0.45*inch, "YOUR ASTROLOGICAL RARITY")
        
        # Calculate fake but specific percentage
        import random
        random.seed(hash(self.person.get('name', '')) % 1000)
        rarity = round(random.uniform(0.12, 0.34), 2)
        
        c.setFont(FONT_REGULAR, 10)
        c.setFillColor(HexColor('#444444'))
        c.drawCentredString(self.width/2, y_box + 0.12*inch, f"Only {rarity}% of people share your exact planetary configuration.")
        c.drawCentredString(self.width/2, y_box - 0.12*inch, f"Your {sun_sign} Sun with {self.person.get('moon_sign', 'your')} Moon is exceptionally rare.")
    
    # ==================== PAGE 3: BIRTH CHART ====================
    def create_birth_chart_page(self):
        """Visual birth chart"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Your Birth Chart")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "A snapshot of the heavens at your first breath")
        
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
        
        # Signs around wheel
        signs = list(ZODIAC_SYMBOLS.keys())
        sun_sign = self.person.get('sun_sign', 'Aries')
        
        c.setFont(FONT_BOLD, 14)
        for i, sign in enumerate(signs):
            angle = (75 - i * 30) * math.pi / 180
            x = center_x + 115 * math.cos(angle)
            y = center_y + 115 * math.sin(angle)
            c.setFillColor(GOLD if sign == sun_sign else NAVY)
            c.drawCentredString(x, y - 5, self.get_symbol(sign))
        
        # Center
        c.setFont(FONT_BOLD, 18)
        c.setFillColor(GOLD)
        c.drawCentredString(center_x, center_y + 10, "☉ ☽")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(NAVY)
        moon_sign = self.person.get('moon_sign', 'Unknown')
        c.drawCentredString(center_x, center_y - 8, f"{sun_sign[:3]} / {moon_sign[:3]}")
        
        # Planet table
        y_table = 2.5*inch
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawString(1*inch, y_table + 0.3*inch, "Your Planetary Positions")
        
        planets = [
            ("☉", "Sun", self.person.get('sun_sign', 'Unknown')),
            ("☽", "Moon", self.person.get('moon_sign', 'Unknown')),
            ("↑", "Rising", self.person.get('rising_sign', 'Unknown')),
            ("☿", "Mercury", self.person.get('mercury', 'Unknown')),
            ("♀", "Venus", self.person.get('venus', 'Unknown')),
            ("♂", "Mars", self.person.get('mars', 'Unknown')),
        ]
        
        c.setFont(FONT_REGULAR, 10)
        y = y_table
        for symbol, name, sign in planets:
            c.setFillColor(GOLD)
            c.drawString(1.2*inch, y, symbol)
            c.setFillColor(NAVY)
            c.drawString(1.5*inch, y, name)
            c.setFillColor(black)
            c.drawString(2.8*inch, y, sign)
            y -= 0.24*inch
    
    # ==================== PAGE 4: BIG THREE ====================
    def create_big_three_page(self):
        """Big Three overview"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 24)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Your Big Three")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "The three pillars of who you are")
        
        # Three columns
        col_width = (self.width - 1.5*inch) / 3
        y_start = self.height - 2.2*inch
        
        sun_sign = self.person.get('sun_sign', 'Unknown')
        moon_sign = self.person.get('moon_sign', 'Unknown')
        rising_sign = self.person.get('rising_sign', 'Unknown')
        
        placements = [
            ("☉", "SUN", sun_sign, "Your Core Self", "Who you are at your center"),
            ("☽", "MOON", moon_sign, "Your Inner World", "How you feel and process"),
            ("↑", "RISING", rising_sign, "Your Outer Mask", "How the world sees you"),
        ]
        
        for i, (symbol, label, sign, desc1, desc2) in enumerate(placements):
            x = 0.75*inch + col_width/2 + i * col_width
            
            c.setFont(FONT_BOLD, 36)
            c.setFillColor(GOLD)
            c.drawCentredString(x, y_start, symbol)
            
            c.setFont(FONT_BOLD, 11)
            c.setFillColor(NAVY)
            c.drawCentredString(x, y_start - 0.4*inch, label)
            
            c.setFont(FONT_BOLD, 13)
            c.setFillColor(GOLD)
            c.drawCentredString(x, y_start - 0.65*inch, sign)
            
            c.setFont(FONT_REGULAR, 9)
            c.setFillColor(HexColor('#555555'))
            c.drawCentredString(x, y_start - 0.95*inch, desc1)
            c.drawCentredString(x, y_start - 1.1*inch, desc2)
        
        # Summary with REAL content
        y_box = y_start - 1.8*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 1.5*inch, self.width - 2*inch, 1.7*inch, 10, fill=1, stroke=0)
        
        first_name = self.person.get('name', 'Friend').split()[0]
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 11)
        c.drawString(1.2*inch, y_box - 0.1*inch, f"What This Means For You, {first_name}:")
        
        # Use actual sign data
        sun_data = ZODIAC_DEEP_DATA.get(sun_sign, {})
        moon_data = MOON_DEEP_DATA.get(moon_sign, {})
        
        summary = f"Your {sun_sign} Sun means {sun_data.get('what_others_miss', 'you have unique gifts others overlook')}. Combined with your {moon_sign} Moon, {moon_data.get('emotional_pattern', 'your emotional world is rich and complex')}. This combination is rare—and powerful."
        
        self.draw_text(summary, 1.2*inch, y_box - 0.35*inch, self.width - 2.6*inch, size=10, line_height=13)
    
    # ==================== PAGE 5: SUN SIGN DEEP DIVE ====================
    def create_sun_sign_page(self):
        """Deep sun sign analysis with AI insight"""
        self.new_page()
        c = self.c
        
        sun_sign = self.person.get('sun_sign', 'Unknown')
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, f"Your Sun in {sun_sign}")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.55*inch, "Your core identity and life force")
        
        # Symbol
        c.setFont(FONT_BOLD, 56)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.3*inch, self.get_symbol(sun_sign))
        
        # Core essence - REAL content
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawString(1*inch, self.height - 2.8*inch, "The Truth About Your Core Self")
        
        essence = self.sun_data.get('core_essence', f"As a {sun_sign} Sun, you possess unique qualities that shape who you are.")
        y = self.draw_text(essence, 1*inch, self.height - 3.05*inch, self.width - 2*inch, size=10, line_height=13)
        
        # AI INSIGHT - The "holy shit" moment
        y -= 0.2*inch
        c.setFillColor(NAVY)
        c.roundRect(1*inch, y - 0.7*inch, self.width - 2*inch, 0.85*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 9)
        c.drawString(1.2*inch, y - 0.1*inch, "✧ PERSONAL INSIGHT")
        
        c.setFillColor(white)
        c.setFont(FONT_REGULAR, 10)
        ai_sun = self.ai_insights.get('sun_insight', f"Your {sun_sign} nature runs deeper than most realize.")
        self.draw_text(ai_sun, 1.2*inch, y - 0.3*inch, self.width - 2.6*inch, size=10, line_height=12, color=white)
        
        # Traits box
        y_box = 4*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.4*inch, self.width - 2*inch, 1.4*inch, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.4*inch, self.width - 2*inch, 1.4*inch, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 11)
        c.drawString(1.2*inch, y_box + 0.7*inch, f"Core {sun_sign} Traits:")
        
        traits = self.sun_data.get('core_traits', ['Unique', 'Complex', 'Evolving', 'Authentic', 'Powerful', 'Deep'])
        c.setFont(FONT_REGULAR, 10)
        c.setFillColor(black)
        y = y_box + 0.4*inch
        for i, trait in enumerate(traits[:3]):
            c.drawString(1.3*inch, y - i*0.25*inch, f"✧  {trait}")
        for i, trait in enumerate(traits[3:6]):
            c.drawString(4*inch, y - i*0.25*inch, f"✧  {trait}")
        
        # Secret wound teaser
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 10)
        wound = self.sun_data.get('secret_wound', 'something deep')
        c.drawString(1*inch, 2.3*inch, f"🔒 Your secret wound: {wound[:50]}...")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(HexColor('#888888'))
        c.drawString(1*inch, 2.05*inch, "[Full shadow work analysis in complete book]")
    
    # ==================== PAGE 6: MOON SIGN ====================
    def create_moon_sign_page(self):
        """Moon sign with AI insight"""
        self.new_page()
        c = self.c
        
        moon_sign = self.person.get('moon_sign', 'Unknown')
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, f"Your Moon in {moon_sign}")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.55*inch, "Your emotional nature and inner world")
        
        # Moon symbol
        c.setFont(FONT_BOLD, 56)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.3*inch, "☽")
        
        # Essence
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawString(1*inch, self.height - 2.8*inch, "Your Emotional Truth")
        
        essence = self.moon_data.get('essence', f"With your Moon in {moon_sign}, your emotional world has its own unique rhythm.")
        y = self.draw_text(essence, 1*inch, self.height - 3.05*inch, self.width - 2*inch, size=10, line_height=13)
        
        # AI INSIGHT
        y -= 0.2*inch
        c.setFillColor(NAVY)
        c.roundRect(1*inch, y - 0.7*inch, self.width - 2*inch, 0.85*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 9)
        c.drawString(1.2*inch, y - 0.1*inch, "✧ PERSONAL INSIGHT")
        
        c.setFillColor(white)
        ai_moon = self.ai_insights.get('moon_insight', f"Your {moon_sign} Moon shapes how you process everything.")
        self.draw_text(ai_moon, 1.2*inch, y - 0.3*inch, self.width - 2.6*inch, size=10, line_height=12, color=white)
        
        # Needs box
        y_box = 4*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.5*inch, self.width - 2*inch, 1.6*inch, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.5*inch, self.width - 2*inch, 1.6*inch, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 11)
        c.drawString(1.3*inch, y_box + 0.8*inch, f"What Your {moon_sign} Moon Needs:")
        
        needs = self.moon_data.get('needs', ['Emotional security', 'Understanding', 'Space to feel', 'Authentic connection'])
        c.setFont(FONT_REGULAR, 10)
        c.setFillColor(black)
        y = y_box + 0.5*inch
        for need in needs[:4]:
            c.drawString(1.4*inch, y, f"✧  {need}")
            y -= 0.28*inch
        
        # Teaser
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 10)
        c.drawString(1*inch, 2*inch, "→ [How your Moon affects your relationships in full book]")
    
    # ==================== PAGE 7: WHAT YOU SHARED ====================
    def create_quiz_reflection_page(self):
        """Reference their quiz answers - makes it PERSONAL"""
        self.new_page()
        c = self.c
        
        first_name = self.person.get('name', 'Friend').split()[0]
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "What You Told Us")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.55*inch, "And what your chart reveals about why")
        
        y = self.height - 2.1*inch
        
        # Reflection 1: Need to be liked
        need_liked = self.quiz.get('need_to_be_liked', '')
        if need_liked:
            c.setFillColor(CREAM)
            c.roundRect(1*inch, y - 0.9*inch, self.width - 2*inch, 1.1*inch, 8, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BOLD, 10)
            c.drawString(1.2*inch, y - 0.15*inch, f"You said: \"{need_liked}\" to needing others' approval")
            
            c.setFont(FONT_REGULAR, 10)
            c.setFillColor(HexColor('#444444'))
            sun_sign = self.person.get('sun_sign', 'Your sign')
            reflection = f"Your {sun_sign} Sun and {self.person.get('moon_sign', 'Moon')} Moon create a specific pattern around approval-seeking that your full book addresses in depth."
            self.draw_text(reflection, 1.2*inch, y - 0.4*inch, self.width - 2.6*inch, size=9, line_height=12)
            
            y -= 1.3*inch
        
        # Reflection 2: Overthinking
        overthink = self.quiz.get('overthink_relationships', '')
        if overthink:
            c.setFillColor(CREAM)
            c.roundRect(1*inch, y - 0.9*inch, self.width - 2*inch, 1.1*inch, 8, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BOLD, 10)
            c.drawString(1.2*inch, y - 0.15*inch, f"You said you \"{overthink}\" overthink relationships")
            
            c.setFont(FONT_REGULAR, 10)
            c.setFillColor(HexColor('#444444'))
            moon_pattern = self.moon_data.get('emotional_pattern', 'Your Moon reveals why.')
            self.draw_text(moon_pattern, 1.2*inch, y - 0.4*inch, self.width - 2.6*inch, size=9, line_height=12)
            
            y -= 1.3*inch
        
        # Reflection 3: Life dream with AI insight
        life_dreams = self.quiz.get('life_dreams', '')
        if life_dreams:
            c.setFillColor(NAVY)
            c.roundRect(1*inch, y - 1.1*inch, self.width - 2*inch, 1.3*inch, 8, fill=1, stroke=0)
            
            c.setFillColor(GOLD)
            c.setFont(FONT_BOLD, 10)
            c.drawString(1.2*inch, y - 0.15*inch, f"Your Dream: \"{life_dreams}\"")
            
            c.setFillColor(white)
            c.setFont(FONT_REGULAR, 10)
            dream_insight = self.ai_insights.get('dream_insight', 'Your chart reveals why this calls to you.')
            self.draw_text(dream_insight, 1.2*inch, y - 0.4*inch, self.width - 2.6*inch, size=10, line_height=12, color=white)
            
            y -= 1.5*inch
        
        # Locked teaser
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(self.width/2, 2.3*inch, "🔒 Your Full Psychological Profile")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, 2*inch, "Based on your quiz + chart: childhood patterns, relationship triggers,")
        c.drawCentredString(self.width/2, 1.8*inch, "career blocks, and specific healing pathways")
        c.drawCentredString(self.width/2, 1.5*inch, "[Available in your complete book]")
    
    # ==================== PAGE 8: LOVE & COMPATIBILITY ====================
    def create_love_page(self):
        """Love and compatibility"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Love & Compatibility")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.55*inch, "What the stars reveal about your heart")
        
        # Venus
        venus = self.person.get('venus', 'Unknown')
        c.setFont(FONT_BOLD, 42)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.1*inch, "♀")
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 13)
        c.drawCentredString(self.width/2, self.height - 2.4*inch, f"Venus in {venus}")
        
        # Venus love style - REAL content
        love_style = VENUS_LOVE_STYLES.get(venus, "Your Venus sign shapes how you give and receive love in unique ways.")
        c.setFillColor(black)
        y = self.draw_text(love_style, 1*inch, self.height - 2.7*inch, self.width - 2*inch, size=10, line_height=13)
        
        # Compatibility
        y -= 0.3*inch
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawString(1*inch, y, "Your Top Compatible Signs:")
        
        sun_sign = self.person.get('sun_sign', 'Aries')
        compatible = COMPATIBILITY_DATA.get(sun_sign, [('Leo', 'Fire Match', 90), ('Sagittarius', 'Adventure', 88), ('Aquarius', 'Unique Bond', 85)])
        
        y -= 0.35*inch
        for sign, match_type, score in compatible:
            c.setFillColor(CREAM)
            c.roundRect(1*inch, y - 0.15*inch, self.width - 2*inch, 0.5*inch, 5, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BOLD, 11)
            c.drawString(1.2*inch, y + 0.05*inch, f"{self.get_symbol(sign)}  {sign}")
            
            c.setFont(FONT_REGULAR, 10)
            c.setFillColor(HexColor('#666666'))
            c.drawString(2.8*inch, y + 0.05*inch, match_type)
            
            # Score bar
            c.setFillColor(HexColor('#e0e0e0'))
            c.rect(4.6*inch, y + 0.02*inch, 1.3*inch, 0.18*inch, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.rect(4.6*inch, y + 0.02*inch, 1.3*inch * (score/100), 0.18*inch, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BOLD, 9)
            c.drawString(6*inch, y + 0.03*inch, f"{score}%")
            
            y -= 0.6*inch
        
        # Locked box
        c.setFillColor(NAVY)
        c.roundRect(1*inch, 2*inch, self.width - 2*inch, 1.1*inch, 10, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(self.width/2, 2.8*inch, "★ In Your Full Book ★")
        
        c.setFillColor(white)
        c.setFont(FONT_REGULAR, 10)
        c.drawCentredString(self.width/2, 2.5*inch, "• Compatibility with ALL 12 signs • Your soulmate's chart signature")
        c.drawCentredString(self.width/2, 2.25*inch, "• Red flags your chart attracts • How to break your pattern")
    
    # ==================== PAGE 9: CAREER + 2025 ====================
    def create_career_page(self):
        """Career insights with AI + key dates"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Career & Your Year Ahead")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.55*inch, "Purpose, timing, and opportunity")
        
        # Career question they asked + AI insight
        career_q = self.quiz.get('career_question', '')
        if career_q:
            c.setFillColor(CREAM)
            c.roundRect(1*inch, self.height - 2.8*inch, self.width - 2*inch, 1*inch, 8, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont(FONT_BOLD, 10)
            c.drawString(1.2*inch, self.height - 2*inch, f"You asked: \"{career_q[:50]}...\"")
            
            c.setFillColor(HexColor('#444444'))
            c.setFont(FONT_REGULAR, 10)
            career_insight = self.ai_insights.get('career_insight', 'Your chart points to specific paths for fulfillment.')
            self.draw_text(career_insight, 1.2*inch, self.height - 2.25*inch, self.width - 2.6*inch, size=9, line_height=12)
        
        # Ideal careers
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawString(1*inch, 6.3*inch, "Ideal Career Paths For You:")
        
        careers = self.sun_data.get('careers', ['Creative Field', 'Leadership', 'Consulting', 'Entrepreneurship', 'Healing Arts', 'Education'])
        c.setFont(FONT_REGULAR, 10)
        c.setFillColor(black)
        y = 6*inch
        for i, career in enumerate(careers[:3]):
            c.drawString(1.2*inch, y - i*0.25*inch, f"✧  {career}")
        for i, career in enumerate(careers[3:6]):
            c.drawString(4*inch, y - i*0.25*inch, f"✧  {career}")
        
        # Key dates 2025
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawString(1*inch, 4.6*inch, "✧ Key Dates: 2025-2026")
        
        dates = [
            ("Mar 2025", "Jupiter expansion—new opportunities appear"),
            ("Jun 2025", "Career breakthrough window opens"),
            ("Sep 2025", "Harvest time—past efforts pay off"),
            ("Jan 2026", "Fresh start energy for major changes"),
        ]
        
        y = 4.3*inch
        for date, event in dates:
            c.setFillColor(GOLD)
            c.setFont(FONT_BOLD, 9)
            c.drawString(1.2*inch, y, date)
            c.setFillColor(black)
            c.setFont(FONT_REGULAR, 9)
            c.drawString(2.1*inch, y, event)
            y -= 0.26*inch
        
        # Lucky elements
        y_lucky = 2.8*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_lucky - 0.3*inch, self.width - 2*inch, 0.9*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 10)
        c.drawString(1.2*inch, y_lucky + 0.3*inch, "Your Lucky Elements:")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(black)
        lucky_nums = self.sun_data.get('lucky_numbers', '3, 7, 9')
        lucky_colors = self.sun_data.get('lucky_colors', 'Gold, Purple')
        c.drawString(1.3*inch, y_lucky + 0.05*inch, f"Numbers: {lucky_nums}")
        c.drawString(4*inch, y_lucky + 0.05*inch, f"Colors: {lucky_colors}")
    
    # ==================== PAGE 10: BLURRED PREVIEW + CTA ====================
    def create_cta_page(self):
        """Blurred preview for FOMO + call to action"""
        self.new_page()
        c = self.c
        
        first_name = self.person.get('name', 'Friend').split()[0]
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 20)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, f"{first_name}, This Was Just A Glimpse...")
        
        # Blurred preview section
        c.setFillColor(HexColor('#f0f0f0'))
        c.roundRect(1*inch, self.height - 4.2*inch, self.width - 2*inch, 2.5*inch, 10, fill=1, stroke=0)
        c.setStrokeColor(HexColor('#cccccc'))
        c.roundRect(1*inch, self.height - 4.2*inch, self.width - 2*inch, 2.5*inch, 10, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(self.width/2, self.height - 1.9*inch, "🔒 LOCKED: Your Complete Analysis")
        
        # Blurred items
        c.setFont(FONT_REGULAR, 10)
        c.setFillColor(HexColor('#999999'))
        locked_items = [
            "Your Deepest Fear: ████████████████████",
            "Your Hidden Superpower: ████████████████",
            "Your Soulmate's Sun Sign: ████████████",
            "Career You'll Thrive In: ████████████████",
            "Your Biggest Relationship Block: ████████",
            "Best Day for Major Decisions: ████████████",
            "Your Life Purpose Number: ████████",
        ]
        
        y = self.height - 2.25*inch
        for item in locked_items:
            c.drawCentredString(self.width/2, y, item)
            y -= 0.28*inch
        
        # Full book features
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 12)
        c.drawCentredString(self.width/2, 4.8*inch, "Your Complete Orastria Book Unlocks:")
        
        features = [
            "60+ pages written for YOUR exact birth chart",
            "Full compatibility with all 12 signs",
            "Month-by-month 2025-2026 predictions",
            "Shadow work specific to your placements",
            "Your ideal partner's chart signature",
        ]
        
        c.setFont(FONT_REGULAR, 10)
        c.setFillColor(black)
        y = 4.5*inch
        for feature in features:
            c.drawString(1.3*inch, y, f"✓  {feature}")
            y -= 0.26*inch
        
        # CTA box
        c.setFillColor(NAVY)
        c.roundRect(1*inch, 1.8*inch, self.width - 2*inch, 1.7*inch, 15, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 14)
        c.drawCentredString(self.width/2, 3.2*inch, "★ Unlock Your Complete Blueprint ★")
        
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 12)
        c.drawCentredString(self.width/2, 2.85*inch, "Get 50% Off — Limited Time")
        
        # Price
        c.setFillColor(HexColor('#888888'))
        c.setFont(FONT_REGULAR, 11)
        c.drawString(self.width/2 - 40, 2.5*inch, "$49.99")
        c.line(self.width/2 - 45, 2.55*inch, self.width/2 - 5, 2.55*inch)
        
        c.setFillColor(GOLD)
        c.setFont(FONT_BOLD, 16)
        c.drawString(self.width/2 + 5, 2.5*inch, "$24.99")
        
        c.setFillColor(white)
        c.setFont(FONT_REGULAR, 9)
        c.drawCentredString(self.width/2, 2.15*inch, "✓ Instant PDF Delivery  •  ✓ 30-Day Money Back Guarantee")
    
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
OrastriaBookGenerator = OrastriaSampleBookV3


# ==================== TESTING ====================
if __name__ == "__main__":
    print("🌟 Testing Orastria Sample Book v3...")
    
    test_person = {
        'name': 'Sarah Mitchell',
        'birth_date': 'March 15, 1995',
        'birth_time': '2:30 PM',
        'birth_place': 'Los Angeles, California',
        'sun_sign': 'Pisces',
        'moon_sign': 'Scorpio',
        'rising_sign': 'Cancer',
        'venus': 'Aquarius',
        'mars': 'Leo',
        'mercury': 'Pisces',
    }
    
    test_quiz = {
        'need_to_be_liked': 'Always',
        'overthink_relationships': 'Often',
        'life_dreams': 'Creating a loving family',
        'career_question': 'What job will bring me joy and fulfillment?',
        'decision_worry': 'Somewhat agree',
        'relationship_status': 'Single',
        'outlook': 'Optimistic',
    }
    
    book = OrastriaSampleBookV3('/tmp/test_sample_v3.pdf', test_person, test_quiz)
    book.build()
    
    print("\n✨ Test complete!")
