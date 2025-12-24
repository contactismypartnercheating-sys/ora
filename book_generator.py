"""
Orastria Sample Book Generator v2
Fixed zodiac symbols + improved visual design
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math

# Register DejaVu Sans for Unicode symbol support
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

# Brand Colors
NAVY = HexColor('#1a1f3c')
GOLD = HexColor('#c9a961')
CREAM = HexColor('#f5f0e8')
DARK_GOLD = HexColor('#a08040')
LIGHT_NAVY = HexColor('#2d3561')
SOFT_GOLD = HexColor('#d4b87a')

class OrastriaBookV2:
    def __init__(self, output_path, person_data, book_type='sample'):
        self.output_path = output_path
        self.person = person_data
        self.book_type = book_type  # 'sample' or 'full'
        self.width, self.height = letter
        self.margin = 0.75 * inch
        self.c = canvas.Canvas(output_path, pagesize=letter)
        self.page_num = 0

# Alias for API compatibility
OrastriaBookGenerator = OrastriaBookV2
        
    def get_zodiac_symbol(self, sign):
        """Return unicode symbol for zodiac sign"""
        symbols = {
            'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
            'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
            'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
        }
        return symbols.get(sign, '✧')
    
    def draw_zodiac_symbol(self, x, y, sign, size=48, color=GOLD):
        """Draw zodiac symbol using DejaVu font that supports Unicode"""
        c = self.c
        c.setFillColor(color)
        c.setFont("DejaVuSans-Bold", size)
        symbol = self.get_zodiac_symbol(sign)
        c.drawCentredString(x, y, symbol)
    
    def draw_celestial_symbol(self, x, y, symbol_type, size=36, color=GOLD):
        """Draw sun, moon, or other celestial symbols"""
        c = self.c
        c.setFillColor(color)
        c.setFont("DejaVuSans-Bold", size)
        
        symbols = {
            'sun': '☉',
            'moon': '☽',
            'rising': '↑',
            'venus': '♀',
            'mars': '♂',
            'mercury': '☿',
            'jupiter': '♃',
            'saturn': '♄',
            'star': '✧',
            'sparkle': '✨'
        }
        c.drawCentredString(x, y, symbols.get(symbol_type, '✧'))
    
    def draw_decorative_border(self):
        """Draw elegant border"""
        c = self.c
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        margin = 0.5 * inch
        c.rect(margin, margin, self.width - 2*margin, self.height - 2*margin)
        
        # Corner decorations using DejaVu
        c.setFont("DejaVuSans", 12)
        c.setFillColor(GOLD)
        corners = [
            (margin + 10, margin + 5),
            (self.width - margin - 10, margin + 5),
            (margin + 10, self.height - margin - 15),
            (self.width - margin - 10, self.height - margin - 15)
        ]
        for x, y in corners:
            c.drawCentredString(x, y, '✦')
    
    def add_page_number(self):
        """Add page number"""
        c = self.c
        self.page_num += 1
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans", 10)
        c.drawCentredString(self.width / 2, 0.6 * inch, f"— {self.page_num} —")
    
    def new_page(self, with_border=True):
        """Start a new page"""
        self.c.showPage()
        if with_border:
            self.draw_decorative_border()
            self.add_page_number()
    
    def draw_text_block(self, text, x, y, width, font="DejaVuSans", size=11, color=black, line_height=14):
        """Draw wrapped text block"""
        c = self.c
        c.setFillColor(color)
        c.setFont(font, size)
        
        paragraphs = text.split('\n\n')
        current_y = y
        
        for para in paragraphs:
            words = para.split()
            current_line = ''
            
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
            
            current_y -= line_height * 0.5  # Paragraph spacing
        
        return current_y
    
    # ==================== COVER PAGE ====================
    def create_cover(self):
        """Create stunning cover page"""
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
        
        # Top decorations
        c.setFont("DejaVuSans-Bold", 24)
        c.setFillColor(GOLD)
        c.drawCentredString(0.8*inch, self.height - 0.8*inch, '☉')
        c.drawCentredString(self.width - 0.8*inch, self.height - 0.8*inch, '☽')
        
        # Title
        c.setFont("DejaVuSans-Bold", 32)
        c.drawCentredString(self.width/2, self.height - 1.8*inch, "YOUR COSMIC")
        c.drawCentredString(self.width/2, self.height - 2.25*inch, "BLUEPRINT")
        
        # Decorative line
        c.setLineWidth(1)
        c.line(2.2*inch, self.height - 2.5*inch, self.width - 2.2*inch, self.height - 2.5*inch)
        
        # Person's name
        c.setFillColor(white)
        c.setFont("DejaVuSans-Bold", 26)
        c.drawCentredString(self.width/2, self.height - 3.2*inch, self.person['name'])
        
        # Birth info
        c.setFillColor(SOFT_GOLD)
        c.setFont("DejaVuSans", 12)
        c.drawCentredString(self.width/2, self.height - 3.6*inch, f"{self.person['birth_date']}  •  {self.person['birth_time']}")
        c.drawCentredString(self.width/2, self.height - 3.85*inch, self.person['birth_place'])
        
        # Central zodiac circle
        center_y = self.height / 2 - 0.3*inch
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.circle(self.width/2, center_y, 85)
        c.setLineWidth(1)
        c.circle(self.width/2, center_y, 95)
        
        # Main zodiac symbol in center - FIXED!
        self.draw_zodiac_symbol(self.width/2, center_y - 20, self.person['sun_sign'], size=64, color=GOLD)
        
        # Sign name below
        c.setFont("DejaVuSans-Bold", 16)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, center_y - 55, self.person['sun_sign'].upper())
        
        # The Big Three line
        c.setFont("DejaVuSans", 11)
        c.setFillColor(white)
        big_three = f"☉ Sun: {self.person['sun_sign']}  •  ☽ Moon: {self.person['moon_sign']}  •  ↑ Rising: {self.person['rising_sign']}"
        c.drawCentredString(self.width/2, center_y - 115, big_three)
        
        # Bottom branding
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 20)
        c.drawCentredString(self.width/2, 1.3*inch, "ORASTRIA")
        
        c.setFont("DejaVuSans", 10)
        c.drawCentredString(self.width/2, 1*inch, "Personalized Astrology  •  Written in the Stars")
        
        # Bottom corner moons
        c.setFont("DejaVuSans", 18)
        c.drawCentredString(0.8*inch, 0.8*inch, '☽')
        c.drawCentredString(self.width - 0.8*inch, 0.8*inch, '☽')
    
    # ==================== INTRO PAGE ====================
    def create_intro_page(self):
        """Personal introduction"""
        self.new_page()
        c = self.c
        
        # Header
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "A Message From The Stars")
        
        # Decorative star
        c.setFont("DejaVuSans", 14)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "✧  ✦  ✧")
        
        # Personal greeting
        first_name = self.person['name'].split()[0]
        intro_text = f"""Dear {first_name},

On {self.person['birth_date']}, at exactly {self.person['birth_time']} in {self.person['birth_place']}, the cosmos aligned in a configuration that had never existed before—and will never exist again.

This moment was uniquely yours.

The position of the Sun, Moon, and planets at your birth created a celestial fingerprint that shapes your personality, your relationships, your life path, and your destiny.

What you hold in your hands is not a generic horoscope. It is a deeply personal analysis of YOUR unique astrological DNA—calculated to the exact minute and location of your birth."""

        self.draw_text_block(intro_text, 1*inch, self.height - 2*inch, self.width - 2*inch)
        
        # Rarity box
        y_box = 4*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.4*inch, self.width - 2*inch, 1.3*inch, 10, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.roundRect(1*inch, y_box - 0.4*inch, self.width - 2*inch, 1.3*inch, 10, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawCentredString(self.width/2, y_box + 0.55*inch, "YOUR ASTROLOGICAL RARITY")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(HexColor('#444444'))
        c.drawCentredString(self.width/2, y_box + 0.25*inch, f"Only 0.23% of {self.person['sun_sign']}s share your exact planetary configuration.")
        c.drawCentredString(self.width/2, y_box, "Your combination of traits is exceptionally uncommon.")
        
        # What's inside
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 14)
        c.drawString(1*inch, 3.1*inch, "Inside Your Personal Book:")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(black)
        items = [
            "✧  Your Complete Birth Chart Analysis",
            "✧  Sun, Moon & Rising Sign Deep Dive",
            "✧  Love & Relationship Compatibility Guide",
            "✧  Career Path & Life Purpose Insights",
            "✧  Key Dates & Predictions for 2025-2026"
        ]
        y = 2.8*inch
        for item in items:
            c.drawString(1.2*inch, y, item)
            y -= 0.28*inch
    
    # ==================== BIRTH CHART PAGE ====================
    def create_birth_chart_page(self):
        """Birth chart visualization"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Your Birth Chart")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "A snapshot of the heavens at the moment you were born")
        
        # Draw birth chart wheel
        center_x = self.width / 2
        center_y = self.height / 2 + 0.7*inch
        
        # Outer ring
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
        
        # Zodiac signs around the wheel - FIXED with DejaVu font
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        c.setFont("DejaVuSans-Bold", 14)
        for i, sign in enumerate(signs):
            angle = (75 - i * 30) * math.pi / 180
            x = center_x + 115 * math.cos(angle)
            y = center_y + 115 * math.sin(angle)
            c.setFillColor(GOLD if sign == self.person['sun_sign'] else NAVY)
            symbol = self.get_zodiac_symbol(sign)
            c.drawCentredString(x, y - 5, symbol)
        
        # Center info
        c.setFont("DejaVuSans-Bold", 18)
        c.setFillColor(GOLD)
        c.drawCentredString(center_x, center_y + 10, "☉ ☽")
        c.setFont("DejaVuSans", 9)
        c.setFillColor(NAVY)
        c.drawCentredString(center_x, center_y - 8, f"{self.person['sun_sign'][:3]} / {self.person['moon_sign'][:3]}")
        
        # Planet positions table
        y_table = 2.5*inch
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(1*inch, y_table + 0.3*inch, "Your Planetary Positions")
        
        planets = [
            ("☉", "Sun", self.person['sun_sign']),
            ("☽", "Moon", self.person['moon_sign']),
            ("↑", "Rising", self.person['rising_sign']),
            ("☿", "Mercury", self.person.get('mercury', 'Capricorn')),
            ("♀", "Venus", self.person.get('venus', 'Aquarius')),
            ("♂", "Mars", self.person.get('mars', 'Scorpio')),
        ]
        
        c.setFont("DejaVuSans", 10)
        y = y_table
        for symbol, name, sign in planets:
            c.setFillColor(GOLD)
            c.drawString(1.2*inch, y, symbol)
            c.setFillColor(NAVY)
            c.drawString(1.5*inch, y, name)
            c.setFillColor(black)
            c.drawString(2.8*inch, y, sign)
            y -= 0.24*inch
    
    # ==================== BIG THREE OVERVIEW ====================
    def create_big_three_page(self):
        """The Big Three overview"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 24)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "The Big Three")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "The three pillars of your astrological identity")
        
        # Three columns
        col_width = (self.width - 1.5*inch) / 3
        y_start = self.height - 2.2*inch
        
        placements = [
            ("☉", "SUN", self.person['sun_sign'], "Your Core Identity", "Who you are at heart", "Your ego & life force"),
            ("☽", "MOON", self.person['moon_sign'], "Your Emotional Self", "How you feel & nurture", "Your inner world"),
            ("↑", "RISING", self.person['rising_sign'], "Your Outer Mask", "First impressions", "How others see you"),
        ]
        
        for i, (symbol, label, sign, desc1, desc2, desc3) in enumerate(placements):
            x = 0.75*inch + col_width/2 + i * col_width
            
            # Symbol
            c.setFont("DejaVuSans-Bold", 36)
            c.setFillColor(GOLD)
            c.drawCentredString(x, y_start, symbol)
            
            # Label
            c.setFont("DejaVuSans-Bold", 12)
            c.setFillColor(NAVY)
            c.drawCentredString(x, y_start - 0.4*inch, label)
            
            # Sign
            c.setFont("DejaVuSans-Bold", 14)
            c.setFillColor(GOLD)
            c.drawCentredString(x, y_start - 0.65*inch, sign)
            
            # Descriptions
            c.setFont("DejaVuSans", 9)
            c.setFillColor(HexColor('#555555'))
            c.drawCentredString(x, y_start - 0.95*inch, desc1)
            c.drawCentredString(x, y_start - 1.1*inch, desc2)
            c.drawCentredString(x, y_start - 1.25*inch, desc3)
        
        # Summary box
        y_box = y_start - 2*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 1.2*inch, self.width - 2*inch, 1.4*inch, 10, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 11)
        first_name = self.person['name'].split()[0]
        c.drawString(1.2*inch, y_box - 0.1*inch, f"What Your Big Three Reveals About You, {first_name}:")
        
        summary = self.get_big_three_summary()
        c.setFont("DejaVuSans", 10)
        c.setFillColor(HexColor('#333333'))
        self.draw_text_block(summary, 1.2*inch, y_box - 0.35*inch, self.width - 2.6*inch, size=10, line_height=13)
        
        # Teaser
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans", 10)
        c.drawCentredString(self.width/2, 1.8*inch, "→ Full analysis of each placement continues on the following pages...")
    
    def get_big_three_summary(self):
        """Generate big three summary"""
        traits = {
            'Sagittarius': "adventurous spirit and eternal optimism",
            'Scorpio': "emotional depth and transformative power",
            'Cancer': "nurturing heart and protective instincts",
            'Leo': "radiant confidence and creative fire",
            'Virgo': "analytical mind and desire for perfection",
            'Libra': "diplomatic grace and quest for harmony",
            'Capricorn': "ambitious drive and practical wisdom",
            'Aquarius': "innovative thinking and humanitarian vision",
            'Pisces': "intuitive gifts and boundless compassion",
            'Aries': "bold initiative and pioneering courage",
            'Taurus': "steady determination and sensual appreciation",
            'Gemini': "curious intellect and adaptable wit"
        }
        
        sun_trait = traits.get(self.person['sun_sign'], "unique essence")
        moon_trait = traits.get(self.person['moon_sign'], "emotional depth")
        
        return f"Your {self.person['sun_sign']} Sun gives you {sun_trait}. Combined with your {self.person['moon_sign']} Moon's {moon_trait}, you possess a rare combination that shapes every aspect of your life..."
    
    # ==================== SUN SIGN PAGE ====================
    def create_sun_sign_page(self):
        """Sun sign deep dive"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, f"Your Sun in {self.person['sun_sign']}")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "Your core identity and life force")
        
        # Large zodiac symbol - FIXED
        self.draw_zodiac_symbol(self.width/2, self.height - 2.5*inch, self.person['sun_sign'], size=72)
        
        # Content
        content = self.get_sun_content()
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 13)
        c.drawString(1*inch, self.height - 3.1*inch, "The Essence of Your Being")
        
        y = self.draw_text_block(content['essence'], 1*inch, self.height - 3.35*inch, self.width - 2*inch)
        
        # Traits box
        y_box = 4.8*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.3*inch, self.width - 2*inch, 1.3*inch, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.3*inch, self.width - 2*inch, 1.3*inch, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 11)
        c.drawString(1.2*inch, y_box + 0.7*inch, f"Core {self.person['sun_sign']} Traits:")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(black)
        traits = content['traits']
        y = y_box + 0.4*inch
        for i, trait in enumerate(traits[:3]):
            c.drawString(1.3*inch, y - i*0.25*inch, f"✧  {trait}")
        for i, trait in enumerate(traits[3:6]):
            c.drawString(4*inch, y - i*0.25*inch, f"✧  {trait}")
        
        # Strengths
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(1*inch, 3.8*inch, "Your Natural Strengths")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(black)
        y = 3.5*inch
        for strength in content['strengths'][:4]:
            c.drawString(1.2*inch, y, f"•  {strength}")
            y -= 0.24*inch
        
        # Teaser
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 10)
        c.drawString(1*inch, 2.1*inch, "→ [Full shadow work analysis in complete book]")
    
    def get_sun_content(self):
        """Get sun sign content"""
        content = {
            'Sagittarius': {
                'essence': "As a Sagittarius Sun, you are the archer of the zodiac—forever aiming your arrow toward distant horizons. You possess an innate optimism and an adventurous spirit that refuses to be contained. Your ruling planet Jupiter blesses you with natural enthusiasm and faith in life's journey.",
                'traits': ['Adventurous', 'Optimistic', 'Philosophical', 'Freedom-loving', 'Honest', 'Enthusiastic'],
                'strengths': ['Natural ability to inspire others', 'Gift for seeing the bigger picture', 'Fearless pursuit of truth', 'Adaptability across situations']
            },
            'Libra': {
                'essence': "As a Libra Sun, you are the diplomat of the zodiac—blessed with an innate understanding of harmony, beauty, and justice. You see both sides of every situation and have a natural talent for bringing balance. Ruled by Venus, you have an aesthetic sensibility that colors everything you do.",
                'traits': ['Diplomatic', 'Charming', 'Fair-minded', 'Social', 'Idealistic', 'Graceful'],
                'strengths': ['Natural peacemaking abilities', 'Gift for multiple perspectives', 'Creating beauty everywhere', 'Building meaningful partnerships']
            },
            'Scorpio': {
                'essence': "As a Scorpio Sun, you possess one of the most powerful energies in the zodiac. You are the phoenix—capable of complete destruction and rebirth. Your emotional depth is unmatched, and your ability to see through facades gives you almost psychic understanding of human nature.",
                'traits': ['Intense', 'Passionate', 'Resourceful', 'Determined', 'Magnetic', 'Perceptive'],
                'strengths': ['Extraordinary emotional resilience', 'Ability to transform adversity', 'Deep loyalty to loved ones', 'Natural investigative abilities']
            },
            'Cancer': {
                'essence': "As a Cancer Sun, you possess the most nurturing energy in the zodiac. You are deeply intuitive, emotionally intelligent, and fiercely protective of those you love. Ruled by the Moon, you are connected to the rhythms of emotion and intuition.",
                'traits': ['Nurturing', 'Intuitive', 'Protective', 'Emotional', 'Tenacious', 'Loyal'],
                'strengths': ['Extraordinary emotional intelligence', 'Creating sanctuary for loved ones', 'Deep intuitive wisdom', 'Unwavering loyalty']
            }
        }
        
        default = {
            'essence': f"As a {self.person['sun_sign']} Sun, your core identity is shaped by this powerful placement. Your sun sign represents your ego, your life force, and the essential nature of who you are at the deepest level.",
            'traits': ['Unique', 'Complex', 'Evolving', 'Authentic', 'Powerful', 'Distinctive'],
            'strengths': ['Your natural talents', 'Your innate wisdom', 'Your personal power', 'Your authentic expression']
        }
        
        return content.get(self.person['sun_sign'], default)
    
    # ==================== MOON SIGN PAGE ====================
    def create_moon_sign_page(self):
        """Moon sign deep dive"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, f"Your Moon in {self.person['moon_sign']}")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "Your emotional nature and inner world")
        
        # Moon symbol - centered better vertically (moved down)
        c.setFont("DejaVuSans-Bold", 72)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.8*inch, "☽")
        
        content = self.get_moon_content()
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 13)
        c.drawString(1*inch, self.height - 3.6*inch, "Your Emotional Landscape")
        
        self.draw_text_block(content['essence'], 1*inch, self.height - 3.85*inch, self.width - 2*inch)
        
        # Needs box - taller with more padding
        y_box = 3.8*inch
        box_height = 1.7*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.3*inch, self.width - 2*inch, box_height, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.3*inch, self.width - 2*inch, box_height, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 11)
        c.drawString(1.3*inch, y_box + 1.1*inch, f"What Your {self.person['moon_sign']} Moon Needs:")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(black)
        y = y_box + 0.75*inch
        for need in content['needs'][:4]:
            c.drawString(1.4*inch, y, f"✧  {need}")
            y -= 0.3*inch
        
        # Teaser - more space from box above
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 10)
        c.drawString(1*inch, 2*inch, "→ [Your Moon's influence on relationships in full book]")
    
    def get_moon_content(self):
        """Get moon sign content"""
        content = {
            'Cancer': {
                'essence': "With your Moon in Cancer, you have the deepest emotional reservoir in the zodiac. Your feelings run profound, your intuition is razor-sharp, and your capacity for nurturing is unmatched. Home and family are essential to your emotional wellbeing.",
                'needs': ['A safe, comfortable home', 'Deep emotional connections', 'Time to process feelings', 'Security in relationships']
            },
            'Pisces': {
                'essence': "With your Moon in Pisces, your emotional nature is boundless and deeply spiritual. You feel the interconnectedness of all things and often experience emotions that seem to come from beyond yourself. Your empathy is extraordinary.",
                'needs': ['Creative and spiritual outlets', 'Time alone for reflection', 'Beauty in your environment', 'A partner who honors your sensitivity']
            },
            'Scorpio': {
                'essence': "With your Moon in Scorpio, your emotional world is intense and transformative. You don't do surface-level feelings—when you feel, you feel with your entire being. This gives you incredible emotional resilience.",
                'needs': ['Emotional depth and authenticity', 'Privacy to process feelings', 'Trust and absolute loyalty', 'Opportunities for transformation']
            }
        }
        
        default = {
            'essence': f"With your Moon in {self.person['moon_sign']}, your emotional landscape is rich and nuanced. Your Moon sign reveals how you process feelings, what makes you feel secure, and how you nurture yourself and others.",
            'needs': ['Understanding of your nature', 'Space for your feelings', 'Security in relationships', 'Connection to comfort']
        }
        
        return content.get(self.person['moon_sign'], default)
    
    # ==================== LOVE PAGE ====================
    def create_love_page(self):
        """Love and compatibility"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Love & Compatibility")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "What the stars reveal about your heart")
        
        # Venus symbol
        c.setFont("DejaVuSans-Bold", 48)
        c.setFillColor(GOLD)
        c.drawCentredString(self.width/2, self.height - 2.2*inch, "♀")
        
        venus = self.person.get('venus', 'Aquarius')
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 14)
        c.drawCentredString(self.width/2, self.height - 2.6*inch, f"Venus in {venus}")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 2.85*inch, "How you love, what you value, and who you attract")
        
        # Love style text
        c.setFillColor(black)
        c.setFont("DejaVuSans", 11)
        love_text = f"With Venus in {venus}, your approach to love is distinctive and shaped by this placement. You attract partners who resonate with your unique energy, and you express affection in ways that reflect your Venus sign's qualities."
        self.draw_text_block(love_text, 1*inch, self.height - 3.2*inch, self.width - 2*inch)
        
        # Compatibility preview - moved up for better spacing
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 13)
        c.drawString(1*inch, 5.8*inch, "Your Top Compatible Signs:")
        
        compatible = [
            ('Aquarius', 'Intellectual Match', 92),
            ('Gemini', 'Mental Connection', 88),
            ('Libra', 'Harmonious Bond', 86),
        ]
        
        y = 5.4*inch
        for sign, match_type, score in compatible:
            # Box - taller for better padding
            c.setFillColor(CREAM)
            c.roundRect(1*inch, y - 0.15*inch, self.width - 2*inch, 0.55*inch, 5, fill=1, stroke=0)
            
            # Sign with symbol - centered vertically in box
            c.setFillColor(NAVY)
            c.setFont("DejaVuSans-Bold", 11)
            symbol = self.get_zodiac_symbol(sign)
            c.drawString(1.2*inch, y + 0.08*inch, f"{symbol}  {sign}")
            
            c.setFont("DejaVuSans", 10)
            c.setFillColor(HexColor('#666666'))
            c.drawString(3*inch, y + 0.08*inch, match_type)
            
            # Score bar - adjusted position
            bar_y = y + 0.05*inch
            c.setFillColor(HexColor('#e0e0e0'))
            c.rect(4.8*inch, bar_y, 1.3*inch, 0.2*inch, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.rect(4.8*inch, bar_y, 1.3*inch * (score/100), 0.2*inch, fill=1, stroke=0)
            
            c.setFillColor(NAVY)
            c.setFont("DejaVuSans-Bold", 9)
            c.drawString(6.2*inch, y + 0.06*inch, f"{score}%")
            
            y -= 0.65*inch
        
        # Locked content box
        y_lock = 2.5*inch
        c.setFillColor(NAVY)
        c.roundRect(1*inch, y_lock - 0.5*inch, self.width - 2*inch, 1.1*inch, 10, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawCentredString(self.width/2, y_lock + 0.3*inch, "★ In Your Full Book ★")
        
        c.setFillColor(white)
        c.setFont("DejaVuSans", 10)
        c.drawCentredString(self.width/2, y_lock, "• Detailed compatibility with ALL 12 signs")
        c.drawCentredString(self.width/2, y_lock - 0.22*inch, "• Your ideal partner's chart characteristics")
    
    # ==================== CAREER PAGE ====================
    def create_career_page(self):
        """Career and purpose"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Career & Life Purpose")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "Your destined path to success and fulfillment")
        
        # Career overview
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 13)
        c.drawString(1*inch, self.height - 2.1*inch, "Your Professional Destiny")
        
        career_text = f"Your {self.person['sun_sign']} Sun combined with your other placements creates a unique career blueprint. You thrive in environments that honor your natural gifts and allow authentic self-expression."
        c.setFillColor(black)
        self.draw_text_block(career_text, 1*inch, self.height - 2.35*inch, self.width - 2*inch)
        
        # Ideal careers box
        y_box = 6.2*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_box - 0.3*inch, self.width - 2*inch, 1.4*inch, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.roundRect(1*inch, y_box - 0.3*inch, self.width - 2*inch, 1.4*inch, 8, fill=0, stroke=1)
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 11)
        c.drawString(1.2*inch, y_box + 0.8*inch, "Ideal Career Paths For You:")
        
        careers = self.get_careers()
        c.setFont("DejaVuSans", 10)
        c.setFillColor(black)
        y = y_box + 0.5*inch
        for i, career in enumerate(careers[:3]):
            c.drawString(1.3*inch, y - i*0.25*inch, f"✧  {career}")
        for i, career in enumerate(careers[3:6]):
            c.drawString(4*inch, y - i*0.25*inch, f"✧  {career}")
        
        # Key dates
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(1*inch, 4.5*inch, "Key Career Dates: 2025")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(black)
        c.drawString(1.2*inch, 4.2*inch, "→ March 2025: Jupiter brings expansion opportunities")
        c.drawString(1.2*inch, 3.95*inch, "→ July 2025: Career breakthrough window opens")
        c.drawString(1.2*inch, 3.7*inch, "→ October 2025: Recognition for past efforts arrives")
        
        # Teaser
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 10)
        c.drawString(1*inch, 3*inch, "→ [Complete career timing & monthly forecasts in full book]")
    
    def get_careers(self):
        """Get ideal careers"""
        careers = {
            'Sagittarius': ['University Professor', 'Travel Writer', 'Life Coach', 'Publisher', 'International Business', 'Adventure Guide'],
            'Libra': ['Lawyer/Mediator', 'Interior Designer', 'Diplomat', 'HR Professional', 'Art Director', 'Wedding Planner'],
            'Scorpio': ['Psychologist', 'Detective', 'Surgeon', 'Financial Analyst', 'Researcher', 'Crisis Manager'],
            'Cancer': ['Therapist', 'Chef', 'Real Estate', 'Nurse', 'Social Worker', 'Historian'],
        }
        return careers.get(self.person['sun_sign'], ['Entrepreneur', 'Consultant', 'Creative', 'Manager', 'Specialist', 'Advisor'])
    
    # ==================== PREDICTIONS PAGE ====================
    def create_predictions_page(self):
        """2025 predictions"""
        self.new_page()
        c = self.c
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 22)
        c.drawCentredString(self.width/2, self.height - 1.3*inch, "Your Year Ahead: 2025")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.6*inch, "Key transits and timing for your success")
        
        # Overview
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 13)
        first_name = self.person['name'].split()[0]
        c.drawString(1*inch, self.height - 2.1*inch, f"2025 Overview for {first_name}")
        
        overview = "2025 brings significant planetary movements that will especially impact your sign. Jupiter's expansion energy moves through key areas of your chart, opening doors for growth and opportunity."
        c.setFillColor(black)
        self.draw_text_block(overview, 1*inch, self.height - 2.35*inch, self.width - 2*inch)
        
        # Key dates
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(1*inch, 6.3*inch, "✧ Key Dates to Watch:")
        
        dates = [
            ("Jan 13", "Mercury direct — decisions solid", GOLD),
            ("Mar 20", "Spring Equinox — new beginning energy", GOLD),
            ("Apr 8", "Venus enters your love sector", HexColor('#e74c3c')),
            ("Jun 15", "Career breakthrough window", HexColor('#27ae60')),
            ("Sep 7", "Harvest moon — manifestation power", GOLD),
        ]
        
        y = 6*inch
        for date, event, color in dates:
            c.setFillColor(color)
            c.setFont("DejaVuSans-Bold", 10)
            c.drawString(1.2*inch, y, date)
            c.setFillColor(black)
            c.setFont("DejaVuSans", 10)
            c.drawString(2.2*inch, y, event)
            y -= 0.28*inch
        
        # Lucky elements box
        y_lucky = 4*inch
        c.setFillColor(CREAM)
        c.roundRect(1*inch, y_lucky - 0.4*inch, self.width - 2*inch, 1.1*inch, 8, fill=1, stroke=0)
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 11)
        c.drawString(1.2*inch, y_lucky + 0.4*inch, "Your Lucky Elements for 2025:")
        
        c.setFont("DejaVuSans", 10)
        c.setFillColor(black)
        c.drawString(1.3*inch, y_lucky + 0.12*inch, "Lucky Numbers: 3, 7, 9, 12, 21")
        c.drawString(1.3*inch, y_lucky - 0.12*inch, "Lucky Days: Thursday, Sunday")
        c.drawString(4.2*inch, y_lucky + 0.12*inch, "Lucky Colors: Purple, Gold")
        c.drawString(4.2*inch, y_lucky - 0.12*inch, "Best Months: March, July")
        
        # Teaser - FIXED: removed broken emoji
        c.setFillColor(NAVY)
        c.roundRect(1*inch, 2.2*inch, self.width - 2*inch, 0.9*inch, 10, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 11)
        c.drawCentredString(self.width/2, 2.8*inch, "✧ Complete 2025-2026 Forecast ✧")
        
        c.setFillColor(white)
        c.setFont("DejaVuSans", 10)
        c.drawCentredString(self.width/2, 2.5*inch, "Month-by-month predictions  •  Best days for major decisions")
    
    # ==================== CTA PAGE ====================
    def create_cta_page(self):
        """Call to action"""
        self.new_page()
        c = self.c
        
        first_name = self.person['name'].split()[0]
        
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 20)
        c.drawCentredString(self.width/2, self.height - 1.4*inch, f"{first_name}, This Is Just The Beginning...")
        
        c.setFont("DejaVuSans", 11)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(self.width/2, self.height - 1.7*inch, "What you've read is only a preview of your complete cosmic blueprint")
        
        # What's included
        c.setFillColor(NAVY)
        c.setFont("DejaVuSans-Bold", 14)
        c.drawCentredString(self.width/2, self.height - 2.3*inch, "Your Complete Orastria Book Includes:")
        
        features = [
            ("60+ Personalized Pages", "Every page written for YOUR birth chart"),
            ("Complete Planet Analysis", "All planets + houses + aspects"),
            ("Full Compatibility Guide", "All 12 signs + ideal partner profile"),
            ("2025-2026 Predictions", "Month-by-month forecasts"),
            ("Shadow Work Guide", "Transform challenges into strengths"),
            ("Lucky Days Calendar", "Best dates for love & career"),
        ]
        
        y = self.height - 2.7*inch
        for title, desc in features:
            c.setFillColor(CREAM)
            c.roundRect(1.2*inch, y - 0.15*inch, self.width - 2.4*inch, 0.5*inch, 5, fill=1, stroke=0)
            
            c.setFillColor(GOLD)
            c.setFont("DejaVuSans-Bold", 10)
            c.drawString(1.4*inch, y + 0.1*inch, f"✧  {title}")
            c.setFillColor(HexColor('#666666'))
            c.setFont("DejaVuSans", 9)
            c.drawString(1.4*inch, y - 0.08*inch, desc)
            
            y -= 0.58*inch
        
        # CTA box
        y_cta = 2.6*inch
        c.setFillColor(NAVY)
        c.roundRect(1*inch, y_cta - 0.9*inch, self.width - 2*inch, 1.9*inch, 15, fill=1, stroke=0)
        
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 16)
        c.drawCentredString(self.width/2, y_cta + 0.65*inch, "★ Special Offer ★")
        
        c.setFillColor(white)
        c.setFont("DejaVuSans-Bold", 14)
        c.drawCentredString(self.width/2, y_cta + 0.3*inch, "Get Your Complete Book Now")
        
        # Price
        c.setFillColor(HexColor('#888888'))
        c.setFont("DejaVuSans", 12)
        c.drawString(self.width/2 - 50, y_cta - 0.05*inch, "$49.99")
        c.setStrokeColor(HexColor('#888888'))
        c.line(self.width/2 - 55, y_cta, self.width/2 - 10, y_cta)
        
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans-Bold", 18)
        c.drawString(self.width/2 + 10, y_cta - 0.05*inch, "$24.99")
        
        c.setFillColor(white)
        c.setFont("DejaVuSans", 10)
        c.drawCentredString(self.width/2, y_cta - 0.35*inch, "50% OFF — Limited Time Holiday Special")
        
        c.setFillColor(GOLD)
        c.setFont("DejaVuSans", 9)
        c.drawCentredString(self.width/2, y_cta - 0.6*inch, "✓ Instant Delivery  ✓ 30-Day Guarantee")
    
    # ==================== BUILD ====================
    def build(self):
        """Generate the complete book"""
        self.create_cover()
        self.create_intro_page()
        self.create_birth_chart_page()
        self.create_big_three_page()
        self.create_sun_sign_page()
        self.create_moon_sign_page()
        self.create_love_page()
        self.create_career_page()
        self.create_predictions_page()
        self.create_cta_page()
        
        self.c.save()
        print(f"✅ Book generated: {self.output_path}")
        return self.output_path


# Generate books
if __name__ == "__main__":
    print("🌟 Generating Orastria Sample Books v2...")
    
    # Taylor Swift
    taylor = {
        'name': 'Taylor Swift',
        'birth_date': 'December 13, 1989',
        'birth_time': '5:17 AM',
        'birth_place': 'Reading, Pennsylvania',
        'sun_sign': 'Sagittarius',
        'moon_sign': 'Cancer',
        'rising_sign': 'Scorpio',
        'venus': 'Aquarius',
        'mars': 'Scorpio',
        'mercury': 'Capricorn',
    }
    
    book1 = OrastriaBookV2('/home/claude/orastria_taylor_v2.pdf', taylor)
    book1.build()
    
    # Emma Mitchell
    emma = {
        'name': 'Emma Mitchell',
        'birth_date': 'October 15, 1996',
        'birth_time': '3:42 PM',
        'birth_place': 'Chicago, Illinois',
        'sun_sign': 'Libra',
        'moon_sign': 'Pisces',
        'rising_sign': 'Aquarius',
        'venus': 'Scorpio',
        'mars': 'Leo',
        'mercury': 'Libra',
    }
    
    book2 = OrastriaBookV2('/home/claude/orastria_emma_v2.pdf', emma)
    book2.build()
    
    print("\n✨ Done!")
