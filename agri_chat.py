LANGUAGES = ["English", "తెలుగు", "தமிழ்", "हिन्दी", "ಕನ್ನಡ", "മലയാളം"]

RESPONSES = {
"English": {
"welcome":"Namaste! 🌱 Tell me your crop, village and farming question. I can help with weather, irrigation, soil, pests, crop planning, profit and equipment.",
"weather":"Search your village in Weather & Alerts. AgriWise connects that place to online weather data and shows today's condition, temperature, rain chance and farm alerts.",
"irrigation":"Tell me your crop, soil type, growth stage and acres. I can estimate irrigation using crop demand, soil water holding and the latest forecast.",
"crop":"Tell me your soil, available water, season and village or district. I can suggest practical crop options.",
"soil":"Tell me the soil type and crop. I can explain water holding, irrigation method and soil-test considerations.",
"pest":"Tell me the crop and symptoms such as spots, curling, holes, yellowing, wilting or insects. I can help narrow down likely causes.",
"profit":"Give me crop, acres, expected yield, selling price and major costs. I can calculate revenue, cost, profit, ROI and break-even.",
"equipment":"Tell me the work and field size. I can help choose a tractor, tiller, pump, sprayer or harvester.",
"greeting":"Namaste! 🌾 What are you growing?"
},
"తెలుగు": {
"welcome":"నమస్తే! 🌱 మీ పంట, గ్రామం మరియు వ్యవసాయ ప్రశ్నను చెప్పండి. వాతావరణం, నీటిపారుదల, నేల, తెగుళ్లు, పంట ప్రణాళిక మరియు లాభం గురించి సహాయం చేస్తాను.",
"weather":"Weather & Alerts లో మీ గ్రామం పేరును వెతకండి. AgriWise ఆ ప్రాంతానికి ఆన్‌లైన్ వాతావరణ సమాచారాన్ని తీసుకుని ఈరోజు వాతావరణం, ఉష్ణోగ్రత, వర్షం అవకాశం మరియు రైతు హెచ్చరికలను చూపిస్తుంది.",
"irrigation":"పంట, నేల రకం, పెరుగుదల దశ మరియు ఎకరాలు చెప్పండి. పంట అవసరం, నేల నీటి నిల్వ మరియు తాజా వాతావరణాన్ని ఉపయోగించి నీటిపారుదల సూచన ఇస్తాను.",
"crop":"మీ నేల, నీటి లభ్యత, సీజన్ మరియు గ్రామం లేదా జిల్లా చెప్పండి. సరిపోయే పంటలను సూచిస్తాను.",
"soil":"నేల రకం మరియు పంట చెప్పండి. నీటి నిల్వ, నీటిపారుదల విధానం మరియు నేల పరీక్ష గురించి వివరిస్తాను.",
"pest":"పంటలో మచ్చలు, ఆకులు ముడుచుకోవడం, రంధ్రాలు, పసుపు రంగు, వాడిపోవడం లేదా పురుగులు వంటి లక్షణాలు చెప్పండి.",
"profit":"పంట, ఎకరాలు, దిగుబడి, అమ్మకపు ధర మరియు ఖర్చులు చెప్పండి. ఆదాయం, ఖర్చు, లాభం, ROI మరియు break-even లెక్కిస్తాను.",
"equipment":"ఏ పని చేయాలో మరియు పొలం పరిమాణం చెప్పండి. ట్రాక్టర్, టిల్లర్, పంప్, స్ప్రేయర్ లేదా హార్వెస్టర్ ఎంచుకోవడంలో సహాయం చేస్తాను.",
"greeting":"నమస్తే! 🌾 మీరు ఏ పంట పండిస్తున్నారు?"
},
"தமிழ்": {
"welcome":"வணக்கம்! 🌱 உங்கள் பயிர், கிராமம் மற்றும் விவசாய கேள்வியை சொல்லுங்கள். வானிலை, பாசனம், மண், பூச்சி, பயிர் திட்டம் மற்றும் லாபம் பற்றி உதவுகிறேன்.",
"weather":"Weather & Alerts பகுதியில் உங்கள் கிராமத்தைத் தேடுங்கள். AgriWise அந்த இடத்தின் ஆன்லைன் வானிலை தகவலைக் கொண்டு இன்று நிலை, வெப்பநிலை, மழை வாய்ப்பு மற்றும் விவசாய எச்சரிக்கைகளை காட்டும்.",
"irrigation":"பயிர், மண் வகை, வளர்ச்சி நிலை மற்றும் ஏக்கரை சொல்லுங்கள். வானிலை மற்றும் மண் நீர் தாங்கும் திறனை வைத்து பாசன ஆலோசனை தருகிறேன்.",
"crop":"மண், நீர் வசதி, பருவம் மற்றும் கிராமம் அல்லது மாவட்டத்தை சொல்லுங்கள். பொருத்தமான பயிர்களை பரிந்துரைக்கிறேன்.",
"soil":"மண் வகை மற்றும் பயிரை சொல்லுங்கள். நீர் தாங்கும் திறன் மற்றும் பாசன முறையை விளக்குகிறேன்.",
"pest":"பயிரில் புள்ளிகள், இலை சுருட்டல், துளைகள், மஞ்சள் நிறம், வாடுதல் அல்லது பூச்சிகள் இருந்தால் சொல்லுங்கள்.",
"profit":"பயிர், ஏக்கர், விளைச்சல், விற்பனை விலை மற்றும் செலவுகளை சொல்லுங்கள். வருமானம், செலவு, லாபம் மற்றும் ROI கணக்கிடுகிறேன்.",
"equipment":"வேலை மற்றும் வயல் அளவை சொல்லுங்கள். டிராக்டர், டில்லர், பம்ப், ஸ்ப்ரேயர் அல்லது ஹார்வெஸ்டர் தேர்வில் உதவுகிறேன்.",
"greeting":"வணக்கம்! 🌾 நீங்கள் எந்த பயிர் செய்கிறீர்கள்?"
},
"हिन्दी": {
"welcome":"नमस्ते! 🌱 अपनी फसल, गांव और खेती का सवाल बताइए। मैं मौसम, सिंचाई, मिट्टी, कीट, फसल योजना और लाभ में मदद करूंगा।",
"weather":"Weather & Alerts में अपने गांव का नाम खोजें। AgriWise उस जगह का ऑनलाइन मौसम लेकर आज का मौसम, तापमान, बारिश की संभावना और खेती के अलर्ट दिखाएगा।",
"irrigation":"फसल, मिट्टी, विकास अवस्था और एकड़ बताइए। मौसम और मिट्टी की पानी रोकने की क्षमता के आधार पर सिंचाई सलाह दूंगा।",
"crop":"मिट्टी, पानी, मौसम और गांव या जिले का नाम बताइए। मैं उपयुक्त फसल सुझाऊंगा।",
"soil":"मिट्टी और फसल बताइए। मैं पानी रोकने की क्षमता और सिंचाई विधि समझाऊंगा।",
"pest":"पत्तियों पर दाग, मुड़ना, छेद, पीलापन, मुरझाना या कीड़े जैसे लक्षण बताइए।",
"profit":"फसल, एकड़, उपज, बिक्री मूल्य और खर्च बताइए। मैं आय, लागत, लाभ, ROI और break-even निकाल दूंगा।",
"equipment":"काम और खेत का आकार बताइए। ट्रैक्टर, टिलर, पंप, स्प्रेयर या हार्वेस्टर चुनने में मदद करूंगा।",
"greeting":"नमस्ते! 🌾 आप कौन सी फसल उगा रहे हैं?"
},
"ಕನ್ನಡ": {
"welcome":"ನಮಸ್ಕಾರ! 🌱 ನಿಮ್ಮ ಬೆಳೆ, ಗ್ರಾಮ ಮತ್ತು ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ತಿಳಿಸಿ. ಹವಾಮಾನ, ನೀರಾವರಿ, ಮಣ್ಣು, ಕೀಟಗಳು, ಬೆಳೆ ಯೋಜನೆ ಮತ್ತು ಲಾಭದ ಬಗ್ಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.",
"weather":"Weather & Alerts ನಲ್ಲಿ ನಿಮ್ಮ ಗ್ರಾಮದ ಹೆಸರನ್ನು ಹುಡುಕಿ. AgriWise ಆ ಸ್ಥಳದ ಆನ್‌ಲೈನ್ ಹವಾಮಾನವನ್ನು ಪಡೆದು ಇಂದಿನ ಹವಾಮಾನ, ಮಳೆ ಸಾಧ್ಯತೆ ಮತ್ತು ಕೃಷಿ ಎಚ್ಚರಿಕೆಗಳನ್ನು ತೋರಿಸುತ್ತದೆ.",
"irrigation":"ಬೆಳೆ, ಮಣ್ಣು, ಬೆಳವಣಿಗೆ ಹಂತ ಮತ್ತು ಎಕರೆಗಳನ್ನು ತಿಳಿಸಿ. ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ನೀರು ಹಿಡಿದಿಡುವ ಸಾಮರ್ಥ್ಯದ ಆಧಾರದ ಮೇಲೆ ನೀರಾವರಿ ಸಲಹೆ ನೀಡುತ್ತೇನೆ.",
"crop":"ಮಣ್ಣು, ನೀರಿನ ಲಭ್ಯತೆ, ಋತು ಮತ್ತು ಗ್ರಾಮ ಅಥವಾ ಜಿಲ್ಲೆಯನ್ನು ತಿಳಿಸಿ. ಸೂಕ್ತ ಬೆಳೆಗಳನ್ನು ಸೂಚಿಸುತ್ತೇನೆ.",
"soil":"ಮಣ್ಣು ಮತ್ತು ಬೆಳೆ ತಿಳಿಸಿ. ನೀರು ಹಿಡಿದಿಡುವ ಸಾಮರ್ಥ್ಯ ಮತ್ತು ನೀರಾವರಿ ವಿಧಾನವನ್ನು ವಿವರಿಸುತ್ತೇನೆ.",
"pest":"ಎಲೆ ಕಲೆ, ಮಡಚಿಕೊಳ್ಳುವುದು, ರಂಧ್ರ, ಹಳದಿ ಬಣ್ಣ, ಒಣಗುವುದು ಅಥವಾ ಕೀಟಗಳ ಲಕ್ಷಣಗಳನ್ನು ತಿಳಿಸಿ.",
"profit":"ಬೆಳೆ, ಎಕರೆ, ಇಳುವರಿ, ಮಾರಾಟ ಬೆಲೆ ಮತ್ತು ವೆಚ್ಚಗಳನ್ನು ತಿಳಿಸಿ. ಆದಾಯ, ವೆಚ್ಚ, ಲಾಭ ಮತ್ತು ROI ಲೆಕ್ಕಿಸುತ್ತೇನೆ.",
"equipment":"ಕೆಲಸ ಮತ್ತು ಹೊಲದ ಗಾತ್ರ ತಿಳಿಸಿ. ಟ್ರ್ಯಾಕ್ಟರ್, ಟಿಲ್ಲರ್, ಪಂಪ್, ಸ್ಪ್ರೇಯರ್ ಅಥವಾ ಹಾರ್ವೆಸ್ಟರ್ ಆಯ್ಕೆ ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.",
"greeting":"ನಮಸ್ಕಾರ! 🌾 ನೀವು ಯಾವ ಬೆಳೆ ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ?"
},
"മലയാളം": {
"welcome":"നമസ്കാരം! 🌱 നിങ്ങളുടെ വിള, ഗ്രാമം, കൃഷി ചോദ്യം പറയൂ. കാലാവസ്ഥ, ജലസേചനം, മണ്ണ്, കീടങ്ങൾ, വിള പദ്ധതി, ലാഭം എന്നിവയിൽ സഹായിക്കാം.",
"weather":"Weather & Alerts ൽ നിങ്ങളുടെ ഗ്രാമത്തിന്റെ പേര് തിരയൂ. AgriWise ആ സ്ഥലത്തെ ഓൺലൈൻ കാലാവസ്ഥ ഉപയോഗിച്ച് ഇന്നത്തെ അവസ്ഥ, താപനില, മഴ സാധ്യത, കൃഷി മുന്നറിയിപ്പുകൾ എന്നിവ കാണിക്കും.",
"irrigation":"വിള, മണ്ണിന്റെ തരം, വളർച്ചാ ഘട്ടം, ഏക്കർ എന്നിവ പറയൂ. കാലാവസ്ഥയും മണ്ണിന്റെ ജലധാരണ ശേഷിയും ഉപയോഗിച്ച് ജലസേചന നിർദേശം നൽകാം.",
"crop":"മണ്ണ്, ജലലഭ്യത, സീസൺ, ഗ്രാമം അല്ലെങ്കിൽ ജില്ല പറയൂ. അനുയോജ്യമായ വിളകൾ നിർദേശിക്കാം.",
"soil":"മണ്ണിന്റെ തരവും വിളയും പറയൂ. ജലധാരണ ശേഷിയും ജലസേചന രീതിയും വിശദീകരിക്കാം.",
"pest":"ഇല പാടുകൾ, ചുരുളൽ, തുളകൾ, മഞ്ഞനിറം, വാടൽ അല്ലെങ്കിൽ കീടങ്ങൾ പോലുള്ള ലക്ഷണങ്ങൾ പറയൂ.",
"profit":"വിള, ഏക്കർ, വിളവ്, വിൽപ്പന വില, ചെലവുകൾ പറയൂ. വരുമാനം, ചെലവ്, ലാഭം, ROI എന്നിവ കണക്കാക്കാം.",
"equipment":"ജോലിയും വയലിന്റെ വലുപ്പവും പറയൂ. ട്രാക്ടർ, ടില്ലർ, പമ്പ്, സ്പ്രേയർ അല്ലെങ്കിൽ ഹാർവസ്റ്റർ തിരഞ്ഞെടുക്കാൻ സഹായിക്കാം.",
"greeting":"നമസ്കാരം! 🌾 നിങ്ങൾ ഏത് വിളയാണ് കൃഷി ചെയ്യുന്നത്?"
}
}

KEYWORDS = {
"weather":["weather","rain","rainy","sunny","cloudy","forecast","వర్ష","వాతావరణ","மழை","வானிலை","बारिश","मौसम","ಹವಾಮಾನ","മഴ"],
"irrigation":["irrigation","water","watering","నీరు","నీటిపారుదల","பாசனம்","सिंचाई","ನೀರಾವರಿ","ജലസേചനം"],
"soil":["soil","fertilizer","manure","nutrient","నేల","ఎరువు","மண்","உரம்","मिट्टी","खाद","ಮಣ್ಣು","വളം"],
"pest":["pest","disease","insect","fungus","తెగులు","పురుగు","பூச்சி","நோய்","कीट","रोग","ಕೀಟ","കീടം"],
"profit":["profit","price","income","market","లాభం","ధర","ఆదాయం","லாபம்","விலை","मुनाफा","भाव","ಲಾಭ","വില"],
"equipment":["tractor","harvester","pump","sprayer","equipment","ట్రాక్టర్","పరికరం","டிராக்டர்","उपकरण","ಟ್ರ್ಯಾಕ್ಟರ್","ട്രാക്ടർ"],
"crop":["crop","plant","sow","seed","పంట","విత్తనం","பயிர்","விதை","फसल","बीज","ಬೆಳೆ","വിള"]
}

def _entities(question, history=None):
    text = " ".join([str(x.get("text","")) for x in (history or []) if isinstance(x, dict)] + [question or ""]).lower()
    crops = ["tomato","rice","wheat","maize","cotton","sugarcane","potato","groundnut"]
    soils = ["black soil","black","loamy","loam","clay","sandy","sandy loam","silty","red soil","red"]
    stages = ["establishment","vegetative","flowering","fruiting","grain","bulking","maturity"]
    crop = next((x for x in crops if x in text), None)
    soil = next((x for x in soils if x in text), None)
    stage = next((x for x in stages if x in text), None)
    return crop, soil, stage

def classify(question):
    q=(question or "").lower()
    for topic, words in KEYWORDS.items():
        if any(w in q for w in words):
            return topic
    if any(w in q for w in ["hello","hi","namaste","నమస్తే","வணக்கம்","नमस्ते","ನಮಸ್ಕಾರ","നമസ്കാരം"]):
        return "greeting"
    return "welcome"

def reply(language, question, history=None):
    language = language if language in RESPONSES else "English"
    topic = classify(question)
    crop, soil, stage = _entities(question, history)

    if language == "English":
        q=(question or "").lower()
        if topic == "irrigation" and crop and soil:
            soil_name = "Black soil" if soil in ("black","black soil") else ("Loamy" if soil in ("loam","loamy") else soil.title())
            interval = {"Black soil":"4–6 days","Loamy":"3–4 days","Clay":"5–7 days","Sandy":"1–2 days","Sandy loam":"2–3 days"}.get(soil_name,"depends on field moisture")
            demand = {"tomato":"about 4 mm/day before adjusting for growth stage, heat, humidity and rainfall","rice":"about 6 mm/day","wheat":"about 4 mm/day","maize":"about 5 mm/day","cotton":"about 5 mm/day"}.get(crop,"crop demand varies by stage")
            method = "drip irrigation is usually a good choice for tomato"
            return f"For {crop.title()} on {soil_name}, start with {demand}. {soil_name} holds water relatively well, so avoid frequent heavy watering. A practical starting interval is {interval}, then adjust using actual soil moisture and rainfall. For tomato, {method}. During flowering and fruiting, check moisture more often. If you tell me the field area and growth stage, I can estimate litres and timing."
        if topic == "soil" and soil:
            soil_name = "Black soil" if soil in ("black","black soil") else ("Loamy" if soil in ("loam","loamy") else soil.title())
            crops_for = {"Black soil":"cotton, soybean, wheat, sorghum, maize, chickpea and some vegetables with good drainage","Loamy":"tomato, maize, wheat, groundnut, vegetables and many field crops","Clay":"rice, wheat and crops tolerant of heavier soils","Sandy":"groundnut, watermelon, carrot and other well-drained crops"}
            return f"{soil_name} generally has {('high water-holding capacity and can become waterlogged if over-irrigated' if soil_name=='Black soil' else 'moderate water-holding capacity' if soil_name=='Loamy' else 'higher drainage needs' if soil_name=='Sandy' else 'high water-holding capacity')}. Suitable crop options include {crops_for.get(soil_name,'several crops depending on climate and drainage')}. A soil test is still important for pH and nutrients."
        if topic == "crop" and soil:
            soil_name = "Black soil" if soil in ("black","black soil") else ("Loamy" if soil in ("loam","loamy") else soil.title())
            return f"For {soil_name}, crop choice should also consider season, rainfall and irrigation availability. Common options include " + {"Black soil":"cotton, soybean, wheat, maize, sorghum and chickpea","Loamy":"tomato, maize, wheat, groundnut and vegetables","Clay":"rice and wheat","Sandy":"groundnut, watermelon and other well-drained crops"}.get(soil_name,"several locally adapted crops") + ". Tell me your season and water availability and I can narrow it down."
        if topic == "pest":
            return "I can help diagnose it step by step. Tell me the crop, plant age, affected part, and symptoms (spots, curling, holes, yellowing, wilting or insects). If possible, share a clear photo. I’ll separate likely causes from safe control options and avoid recommending unnecessary pesticide use."
    return RESPONSES[language][topic]
