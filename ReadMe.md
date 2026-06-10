📋 Pentest Suite Pro - Snelle Handleiding

🎯 Wat is het?

Een professionele security testing toolkit met 3 tools:

· URL Fuzzer - Ontdek verborgen mappen & bestanden
· API Scanner - Vind API kwetsbaarheden
· People Hunter - OSINT informatie verzameling

🚀 Snel Starten (3 stappen)

1. Installeren

```bash
pip install -r requirements.txt
```

2. Starten

```bash
python app.py
```

3. Gebruiken

Open browser → http://localhost:5000

🛠️ Tools Overzicht

🔍 URL Fuzzer

Optie Uitleg
Gentle 20 paden, snel testen
Normal 50 paden, standaard
Aggressive 100+ paden, grondig
Threads Aantal gelijktijdige requests (1-50)

Output: Toont alle gevonden URL's met status codes (200=OK, 403=Blocked, 301=Redirect)

🔌 API Scanner

Test Wat het doet
IDOR Checkt of je andermans data kan zien
Rate Limit Test of API brute-force bescherming heeft
Auth Controleert authenticatie beveiliging

Output: Lijst van kwetsbaarheden met ernst (HIGH/MEDIUM/LOW)

👥 People Hunter

Bron Vindt
WHOIS Domein eigenaar
DNS Subdomeinen, mail servers
GitHub Ontwikkelaars accounts
Email patterns Werk email adressen

Output: Email lijst, medewerkers, technologie stack

⚡ Belangrijkste Features

Feature Werking
Live scanning Ziet resultaten in real-time
Export Download resultaten als .txt
Limiet 10 scans per dag (gratis)
Multi-threaded Snel door gelijktijdige requests

📊 Status Codes Uitleg

Code Betekenis Actie
200 ✅ Gevonden Onderzoeken!
301 🔄 Redirect Volgen
403 🔒 Geblokkeerd Kan gevoelig zijn
404 ❌ Niet gevonden Negeren

🎮 Voorbeelden

URL Fuzzer voorbeeld:

```
Target: https://testsite.com
Mode: Normal
Resultaat: /admin (200), /backup.zip (200), /config (403)
```

API Scanner voorbeeld:

```
Target: https://api.testsite.com
Bevindingen: 
- IDOR kwetsbaarheid in /users/1 (HIGH)
- Geen rate limiting op /login (MEDIUM)
```

People Hunter voorbeeld:

```
Domain: testsite.com
Resultaten:
- Emails: admin@testsite.com, security@testsite.com
- Medewerkers: John (CTO via LinkedIn)
- Technologie: Nginx server
```

🔧 Problemen Oplossen

Probleem Oplossing
"Connection refused" Check of target online is
"Too many requests" Verlaag threads naar 5
Geen resultaten Probeer Aggressive mode
SSL error Gebruik HTTP i.p.v. HTTPS

⚠️ Belangrijk!

Alleen gebruiken op systemen waar je TOESTEMMING voor hebt!

```bash
# ✅ Goed: 
- Je eigen website testen
- Toestemming van klant
- CTF / Lab omgeving

# ❌ Fout:
- Zonder toestemming scannen
- Overheidsdomeinen
- Concurrentie bespioneren
```

📁 Bestanden Overzicht

```
pentest-suite/
├── app.py           # Backend server
├── index.html       # Frontend interface  
├── style.css        # Styling
├── script.js        # Frontend logic
└── requirements.txt # Python packages
```

💡 Pro Tips

1. Begin altijd met Gentle mode - Test eerst of je target reageert
2. Gebruik "Follow redirects" - Ontdek omleidingen naar andere systemen
3. Exporteer resultaten - Bewaar bewijs van je scan
4. Respecteer robots.txt - Sommige paden willen niet gescand worden
5. Monitor je eigen resources - Hoge threads kunnen je eigen systeem belasten

🎓 Leercurve

Niveau Tijd Wat je kunt
Beginner 10 min Basis scans uitvoeren
Intermediate 1 uur Resultaten interpreteren
Advanced 1 dag Eigen wordlists, geavanceerde opties

📞 Hulp Nodig?

· Geen resultaten → Verhoog intensiteit naar Aggressive
· Te langzaam → Verhoog threads naar 20
· Te veel false positives → Verlaag threads, gebruik Normal mode
· API scanner vindt niets → API heeft mogelijk goede beveiliging!

---

Samengevat: Installeer → Start → Scan → Rapporteer ✅

Vergeet niet: Met grote macht komt grote verantwoordelijkheid. Scan alleen wat je mag scannen! 🛡️
