import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "farmprofit-dev-secret-change-me")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

raw_db_url = os.environ.get("DATABASE_URL", "").strip()
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url or (
    "sqlite:///" + os.path.join(INSTANCE_DIR, "farmprofit.db")
)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "error"


# Planning profiles use common Indian farm units: yield is quintals/acre and
# market price is INR/quintal. Farmers can replace these starting estimates.
SITE_LANGUAGES = ["English", "తెలుగు", "தமிழ்", "हिन्दी", "ಕನ್ನಡ", "മലയാളം"]

SITE_TEXT = {
    "English": {"dashboard":"Dashboard","weather":"Weather & Alerts","soil":"Soil & Irrigation","equipment":"Equipment Rental","rentals":"My Rentals","assistant":"Agri AI Chatbot","profit":"Profit Predictor","whatif":"What-if Simulator","compare":"Compare Crops","history":"History","reports":"Reports","logout":"Logout","language":"Language"},
    "తెలుగు": {"dashboard":"డాష్‌బోర్డ్","weather":"వాతావరణం & హెచ్చరికలు","soil":"నేల & నీటిపారుదల","equipment":"పరికరాల అద్దె","rentals":"నా అద్దెలు","assistant":"అగ్రి AI చాట్‌బాట్","profit":"లాభ అంచనా","whatif":"ఏమైతే సిమ్యులేటర్","compare":"పంటల పోలిక","history":"చరిత్ర","reports":"రిపోర్టులు","logout":"లాగ్ అవుట్","language":"భాష"},
    "தமிழ்": {"dashboard":"டாஷ்போர்டு","weather":"வானிலை & எச்சரிக்கைகள்","soil":"மண் & பாசனம்","equipment":"விவசாய கருவி வாடகை","rentals":"என் வாடகைகள்","assistant":"அக்ரி AI சாட்பாட்","profit":"லாப கணிப்பு","whatif":"என்ன ஆகும் சிமுலேட்டர்","compare":"பயிர் ஒப்பீடு","history":"வரலாறு","reports":"அறிக்கைகள்","logout":"வெளியேறு","language":"மொழி"},
    "हिन्दी": {"dashboard":"डैशबोर्ड","weather":"मौसम और अलर्ट","soil":"मिट्टी और सिंचाई","equipment":"कृषि उपकरण किराया","rentals":"मेरी बुकिंग","assistant":"एग्री AI चैटबॉट","profit":"लाभ अनुमान","whatif":"व्हाट-इफ सिम्युलेटर","compare":"फसल तुलना","history":"इतिहास","reports":"रिपोर्ट","logout":"लॉग आउट","language":"भाषा"},
    "ಕನ್ನಡ": {"dashboard":"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್","weather":"ಹವಾಮಾನ & ಎಚ್ಚರಿಕೆಗಳು","soil":"ಮಣ್ಣು & ನೀರಾವರಿ","equipment":"ಕೃಷಿ ಉಪಕರಣ ಬಾಡಿಗೆ","rentals":"ನನ್ನ ಬಾಡಿಗೆಗಳು","assistant":"ಅಗ್ರಿ AI ಚಾಟ್‌ಬಾಟ್","profit":"ಲಾಭ ಅಂದಾಜು","whatif":"ವಾಟ್-ಇಫ್ ಸಿಮ್ಯುಲೇಟರ್","compare":"ಬೆಳೆ ಹೋಲಿಕೆ","history":"ಇತಿಹಾಸ","reports":"ವರದಿಗಳು","logout":"ಲಾಗ್ ಔಟ್","language":"ಭಾಷೆ"},
    "മലയാളം": {"dashboard":"ഡാഷ്ബോർഡ്","weather":"കാലാവസ്ഥ & മുന്നറിയിപ്പുകൾ","soil":"മണ്ണ് & ജലസേചനം","equipment":"കാർഷിക ഉപകരണ വാടക","rentals":"എന്റെ വാടകകൾ","assistant":"അഗ്രി AI ചാറ്റ്ബോട്ട്","profit":"ലാഭ പ്രവചനം","whatif":"വാട്ട്-ഇഫ് സിമുലേറ്റർ","compare":"വിള താരതമ്യം","history":"ചരിത്രം","reports":"റിപ്പോർട്ടുകൾ","logout":"ലോഗ് ഔട്ട്","language":"ഭാഷ"}
}

@app.context_processor
def inject_site_language():
    language = session.get("site_language", "English")
    if language not in SITE_LANGUAGES:
        language = "English"
    return {"site_language": language, "site_languages": SITE_LANGUAGES, "site_text": SITE_TEXT[language]}

@app.post("/set-language")
@login_required
def set_language():
    language = request.form.get("language", "English")
    if language in SITE_LANGUAGES:
        session["site_language"] = language
        session["agri_language"] = language
    return redirect(request.form.get("next") or url_for("dashboard"))

