"""
rules.py - Knowledge base for HackOrHiccup.

Everything the expert system "knows" lives here as DATA (no if/else logic).
The inference engine (engine.py) is completely separate.

Rule format:
  id      : auto-numbered (R01, R02, ...)
  group   : Battery / Data / Apps / Accounts / SIM / Privacy
  if      : list of conditions. "x" = fact x must be present,
            "!x" = fact x must be ABSENT (only allowed on user-reported facts)
  derive  : (optional) new fact asserted when the rule fires -> enables chaining
  verdict : (optional) verdict that receives points when the rule fires
  points  : evidence points added to that verdict
  why     : plain-English explanation shown in the "Why this result?" panel
"""

# ---------------------------------------------------------------- symptoms
SYMPTOM_GROUPS = {
    "🔋 Battery & Heat": [
        ("battery_drain_fast", "Battery drains much faster than it used to"),
        ("phone_hot_idle", "Phone gets hot even when idle (not charging, not in use)"),
        ("phone_hot_charging_or_gaming", "Heat appears only while charging, gaming or using the camera"),
        ("screen_wakes_alone", "Screen lights up / phone wakes by itself"),
        ("phone_slow_laggy", "Phone feels slow and laggy"),
        ("shutdown_random", "Phone shuts down randomly"),
        ("battery_swollen", "Battery looks swollen or the back panel is bulging"),
        ("recent_drop_water", "Phone was recently dropped or exposed to water"),
    ],
    "🌐 Data & Network": [
        ("data_spike", "Mobile data / Wi-Fi usage spiked unexpectedly"),
        ("idle_data_use", "Apps use data in the background while the phone sits idle"),
        ("unknown_balance_deduction", "Balance / credit deducted for services you did not buy"),
        ("wifi_slow_everywhere", "Internet is slow on ALL devices at home, not just the phone"),
    ],
    "📱 Apps & Permissions": [
        ("unknown_app", "An app you do not remember installing"),
        ("hidden_app", "An app with no icon or a generic name like 'System Service'"),
        ("apk_from_link", "Installed an APK from a WhatsApp / SMS / Facebook link (e.g. 'Wedding.apk')"),
        ("play_protect_off", "Play Protect / security scanning is turned off (Android)"),
        ("admin_accessibility_granted", "An unfamiliar app has Device Admin or Accessibility permission"),
        ("ads_popups", "Pop-up ads or browser redirects outside of apps"),
        ("homescreen_changed", "Homescreen, default browser or search engine changed by itself"),
        ("apps_crash", "Apps crash or freeze often"),
        ("app_wont_uninstall", "An app cannot be uninstalled or keeps coming back"),
        ("rooted_jailbroken", "Phone is rooted / jailbroken"),
        ("recent_update_done", "OS or app update was installed in the last week"),
        ("storage_full", "Storage is almost full"),
    ],
    "🔑 Accounts & OTP": [
        ("otp_not_requested", "Received OTPs / verification codes you did not request"),
        ("new_login_alert", "'New device login' alerts you do not recognise"),
        ("whatsapp_logged_out", "WhatsApp / Telegram suddenly logged you out"),
        ("password_changed_not_me", "Password was changed or reset and it was not you"),
        ("recovery_info_changed", "Recovery email / phone number changed on an account"),
        ("friends_got_spam", "Friends received strange messages or links from you"),
        ("bank_wallet_txn", "Unknown transaction on bank / JazzCash / Easypaisa"),
        ("reused_passwords", "You use the same password on several accounts"),
        ("no_2fa", "No two-factor authentication on your main accounts"),
        ("clicked_phishing_link", "Clicked / entered details on a suspicious link recently"),
    ],
    "📶 SIM & Calls": [
        ("sudden_no_signal", "SIM suddenly lost signal ('No Service' / 'Emergency calls only')"),
        ("others_have_signal", "People next to you on the same network still have signal"),
        ("calls_sms_missing", "Calls / SMS you expect are not arriving"),
        ("sim_replaced_notice", "Message about a SIM replacement / new SIM you did not request"),
        ("phishing_call", "Got a call from 'telco / bank / PTA / BISP' asking for CNIC, OTP or SIM details"),
        ("shared_cnic_or_otp", "You shared your CNIC, OTP or SIM details with that caller"),
    ],
    "🕵️ Privacy & Access": [
        ("someone_had_physical_access", "Someone (partner, ex, relative, colleague) had your unlocked phone"),
        ("shared_phone", "Phone is shared, or others know your passcode"),
        ("someone_knows_private_info", "Someone knows your chats / locations without you telling them"),
        ("location_on_unknown", "Location / mic / camera permission is on for apps you do not recognise"),
        ("camera_mic_indicator", "Camera / mic indicator lights up when you are not using them"),
        ("strange_call_noises", "Clicks, echo or background noise during calls"),
    ],
}

SYMPTOMS = {sid: (grp, label) for grp, items in SYMPTOM_GROUPS.items() for sid, label in items}
SYMPTOM_LABELS = {sid: label for sid, (_, label) in SYMPTOMS.items()}

# facts that come from the two context selectors in the UI
CONTEXT_FACTS = {"new_device", "mid_device", "old_device", "android", "iphone"}

# ---------------------------------------------------------------- verdicts
VERDICTS = {
    "MALWARE": {
        "title": "Malware / Adware infection", "icon": "🦠", "severity": "High",
        "summary": "Your phone shows the pattern of a malicious or ad-injecting app working in the background.",
        "steps": [
            "Turn off mobile data and Wi-Fi to stop data leaving the phone.",
            "Remove Device Admin / Accessibility permission from unknown apps first (Settings > Security), then uninstall them.",
            "If an app will not uninstall, reboot into Safe Mode and remove it there.",
            "Run a scan with Google Play Protect (and one reputable scanner).",
            "From a DIFFERENT, clean device change passwords for email, banking and social accounts.",
            "If symptoms continue: back up photos/contacts only (not apps) and factory reset.",
        ]},
    "STALKERWARE": {
        "title": "Stalkerware / covert monitoring", "icon": "🕵️", "severity": "Critical",
        "summary": "Signs suggest someone with physical access may have installed a monitoring app on your phone.",
        "steps": [
            "SAFETY FIRST: removing the app may alert the person monitoring you. Think about your safety before acting.",
            "Use a different, trusted device for sensitive chats and for searching for help.",
            "Check Device Admin, Accessibility and 'special app access' for apps you do not recognise.",
            "Set a new passcode that nobody knows and stop sharing the phone.",
            "A factory reset removes most stalkerware. Change all account passwords afterwards from the clean phone.",
            "If you are being harassed or threatened, report to FIA Cybercrime Wing (NR3C, helpline 1991) and keep screenshots as evidence.",
        ]},
    "SIM_SWAP": {
        "title": "SIM swap / SIM takeover", "icon": "📵", "severity": "Critical",
        "summary": "Someone may have moved your number to another SIM so they receive your calls, SMS and OTPs.",
        "steps": [
            "Call your network from another phone RIGHT NOW and ask them to block the SIM and stop any replacement.",
            "Visit a franchise with your CNIC for biometric verification and a fresh SIM.",
            "Call your bank, JazzCash and Easypaisa to freeze or monitor your accounts.",
            "Change passwords of email, WhatsApp and banking; move 2FA from SMS to an authenticator app.",
            "Check how many SIMs are registered on your CNIC through PTA's SIM-check service (SMS CNIC to 668) and report unknown ones.",
            "Report to FIA Cybercrime Wing (NR3C, helpline 1991) if money was lost.",
        ]},
    "ACCOUNT_HIJACK": {
        "title": "Account hijack / credential theft", "icon": "🔐", "severity": "High",
        "summary": "Your accounts are probably compromised through stolen or guessed credentials. The phone itself may be fine.",
        "steps": [
            "From a clean device, change the password of the affected account, then your email (the master key).",
            "Use 'Sign out of all devices' and review connected apps and devices.",
            "Check and undo changes to recovery email, phone number and mail-forwarding rules.",
            "Turn on 2FA using an authenticator app, not SMS.",
            "Use a different password for every account (a password manager helps).",
            "Warn your contacts not to click anything sent from you in the last days.",
        ]},
    "FAKE_APK": {
        "title": "Fake / malicious APK installed", "icon": "📦", "severity": "High",
        "summary": "An app installed outside the Play Store (often through a WhatsApp link) is likely stealing data, OTPs or money.",
        "steps": [
            "Uninstall the APK immediately and do not open it again.",
            "Revoke any Accessibility / Device Admin / SMS permission it was given.",
            "Call your bank and wallet providers to block cards / accounts if any transaction looks unfamiliar.",
            "Change passwords and re-enable Google Play Protect.",
            "Install apps only from the Play Store or the official site of the company.",
            "Report the sender / link to FIA Cybercrime (NR3C, 1991) if money was lost.",
        ]},
    "NORMAL_FAULT": {
        "title": "Normal fault - not a hack", "icon": "🔧", "severity": "Low",
        "summary": "Your symptoms are better explained by ageing hardware, heavy use, an update, storage, or your internet provider.",
        "steps": [
            "Restart the phone, install pending updates and check Settings > Battery for the top draining apps.",
            "Free up storage (target at least 15-20% free) and uninstall apps you do not use.",
            "Old battery? Replace it at an authorised service centre to restore battery life and stability.",
            "If the internet is slow on all devices, restart the router and call your ISP.",
            "If the battery is swollen: stop charging and using the phone and take it to a service centre today (fire risk).",
        ]},
    "INCONCLUSIVE": {
        "title": "Inconclusive - weak or no evidence", "icon": "❓", "severity": "Info",
        "summary": "The selected symptoms are too few or too weak to blame an attack or a specific fault.",
        "steps": [
            "Add any other symptoms you have noticed in the tabs above and diagnose again.",
            "Meanwhile: update the phone, review app permissions and turn on 2FA.",
        ]},
}
ATTACK_VERDICTS = ["MALWARE", "STALKERWARE", "SIM_SWAP", "ACCOUNT_HIJACK", "FAKE_APK"]

# ---------------------------------------------------------------- rules
RULES = []


def _add(group, conds, why, derive=None, verdict=None, pts=0):
    RULES.append({"id": f"R{len(RULES) + 1:02d}", "group": group, "if": conds,
                  "derive": derive, "verdict": verdict, "points": pts, "why": why})


# ===== Stage 1: derivation rules (build intermediate facts, no points) =====
_add("Data", ["idle_data_use", "unknown_app"], "Background data use plus an unfamiliar app suggests hidden activity.", derive="background_activity_suspicious")
_add("Data", ["idle_data_use", "hidden_app"], "Background data use plus a hidden app suggests hidden activity.", derive="background_activity_suspicious")
_add("Data", ["data_spike", "background_activity_suspicious"], "A data spike on top of suspicious background activity looks like data leaving the phone.", derive="data_exfiltration_pattern")
_add("Apps", ["hidden_app", "app_wont_uninstall"], "A hidden app that resists removal behaves like a stealth app.", derive="stealth_app_present")
_add("Apps", ["unknown_app", "admin_accessibility_granted"], "An unfamiliar app with powerful permissions is dangerous.", derive="dangerous_app_permissions")
_add("Apps", ["hidden_app", "admin_accessibility_granted"], "A hidden app with powerful permissions is dangerous.", derive="dangerous_app_permissions")
_add("Apps", ["android", "apk_from_link", "play_protect_off"], "Sideloading an APK with Play Protect off removes the safety net.", derive="sideload_exposure")
_add("Privacy", ["someone_had_physical_access"], "Stalkerware needs someone to touch the phone first.", derive="physical_access_risk")
_add("Privacy", ["shared_phone"], "A shared phone or known passcode gives physical access.", derive="physical_access_risk")
_add("Privacy", ["someone_knows_private_info", "location_on_unknown"], "Someone knows private details and an unknown app can read location/mic.", derive="covert_monitoring_signs")
_add("Privacy", ["someone_knows_private_info", "physical_access_risk"], "Someone knows private details and had access to the phone.", derive="covert_monitoring_signs")
_add("SIM", ["sudden_no_signal", "others_have_signal"], "Your SIM died while the network works for others - the problem is your SIM, not the area.", derive="sim_signal_anomaly")
_add("SIM", ["sim_signal_anomaly", "otp_not_requested"], "SIM anomaly plus unrequested OTPs is the classic SIM-swap pattern.", derive="sim_swap_pattern")
_add("SIM", ["phishing_call", "shared_cnic_or_otp"], "You gave identity or OTP details to a suspicious caller.", derive="social_engineering_victim")
_add("Accounts", ["password_changed_not_me", "recovery_info_changed"], "Password AND recovery details changed - a takeover signature.", derive="account_takeover_signs")
_add("Accounts", ["new_login_alert", "whatsapp_logged_out"], "Unknown login plus forced logout points to someone else holding your session.", derive="account_takeover_signs")
_add("Accounts", ["reused_passwords", "no_2fa"], "Reused passwords without 2FA make accounts easy to take over.", derive="weak_account_security")
_add("Battery", ["old_device", "battery_drain_fast"], "Old phone plus fast drain: the battery is probably worn out.", derive="hardware_aging")
_add("Battery", ["old_device", "shutdown_random"], "Old phone plus random shutdowns: worn battery.", derive="hardware_aging")
_add("Battery", ["phone_hot_charging_or_gaming"], "Heat during charging or heavy use is normal.", derive="benign_heat_context")
_add("Data", ["wifi_slow_everywhere"], "Slowness on every device points to the ISP or router.", derive="isp_issue")
_add("Apps", ["storage_full", "phone_slow_laggy"], "Full storage commonly makes phones slow.", derive="phone_overloaded")
_add("Apps", ["recent_update_done", "apps_crash"], "Crashes right after an update are usually update side-effects.", derive="post_update_effects")
_add("Apps", ["recent_update_done", "battery_drain_fast"], "Battery drain right after an update is usually temporary re-indexing.", derive="post_update_effects")

# ===== Stage 2: scoring rules =====
# --- MALWARE
_add("Data", ["data_exfiltration_pattern"], "Data is leaving the phone through a suspicious background app.", verdict="MALWARE", pts=30)
_add("Apps", ["dangerous_app_permissions", "ads_popups"], "A powerful unknown app plus pop-up ads is typical adware/trojan behaviour.", verdict="MALWARE", pts=25)
_add("Apps", ["ads_popups", "homescreen_changed"], "Ads plus changed homescreen/browser indicates a browser or launcher hijacker.", verdict="MALWARE", pts=25)
_add("Apps", ["unknown_app", "ads_popups"], "Unknown app and pop-up ads often come together.", verdict="MALWARE", pts=15)
_add("Battery", ["battery_drain_fast", "phone_hot_idle", "unknown_app"], "Hot, draining phone with an unknown app suggests hidden processes (e.g. mining).", verdict="MALWARE", pts=20)
_add("Data", ["unknown_balance_deduction", "unknown_app"], "Unexpected balance loss plus an unknown app suggests a premium-SMS trojan.", verdict="MALWARE", pts=20)
_add("Apps", ["app_wont_uninstall", "ads_popups"], "An app that resists removal while showing ads is malicious.", verdict="MALWARE", pts=20)
_add("Battery", ["phone_hot_idle", "idle_data_use", "!phone_hot_charging_or_gaming"], "Heat and data use while idle, with no heavy use to explain them.", verdict="MALWARE", pts=15)
_add("Apps", ["rooted_jailbroken", "unknown_app"], "Rooted phones with unknown apps are far easier to compromise.", verdict="MALWARE", pts=15)
# --- STALKERWARE
_add("Privacy", ["covert_monitoring_signs", "stealth_app_present"], "Signs of being watched plus a stealth app is the strongest stalkerware pattern.", verdict="STALKERWARE", pts=40)
_add("Privacy", ["covert_monitoring_signs"], "Someone seems to know what only the phone could tell them.", verdict="STALKERWARE", pts=25)
_add("Privacy", ["physical_access_risk", "hidden_app"], "Someone had access and a hidden app exists.", verdict="STALKERWARE", pts=30)
_add("Privacy", ["camera_mic_indicator", "physical_access_risk"], "Camera/mic activity with possible physical access.", verdict="STALKERWARE", pts=25)
_add("Privacy", ["strange_call_noises", "physical_access_risk"], "Call noises with possible physical access (weak but supporting).", verdict="STALKERWARE", pts=15)
_add("Battery", ["screen_wakes_alone", "physical_access_risk", "battery_drain_fast"], "Screen waking, battery drain and past access - remote activity.", verdict="STALKERWARE", pts=15)
_add("Privacy", ["location_on_unknown", "admin_accessibility_granted"], "Unknown app with location access and admin rights can track you.", verdict="STALKERWARE", pts=25)
_add("Privacy", ["camera_mic_indicator", "unknown_app"], "Mic/camera indicator with an unknown app installed.", verdict="STALKERWARE", pts=20)
_add("Privacy", ["someone_knows_private_info"], "Someone knowing private info is suspicious on its own (but could be social).", verdict="STALKERWARE", pts=15)
# --- SIM SWAP
_add("SIM", ["sim_swap_pattern"], "SIM died, OTPs not requested by you - classic SIM swap.", verdict="SIM_SWAP", pts=40)
_add("SIM", ["sim_signal_anomaly", "calls_sms_missing"], "Calls and SMS vanish while your SIM is dead - they may be going to another SIM.", verdict="SIM_SWAP", pts=25)
_add("SIM", ["sim_replaced_notice"], "A SIM replacement notice you did not request is direct evidence.", verdict="SIM_SWAP", pts=35)
_add("SIM", ["social_engineering_victim", "sudden_no_signal"], "You were socially engineered and then lost signal.", verdict="SIM_SWAP", pts=30)
_add("SIM", ["sim_swap_pattern", "bank_wallet_txn"], "Money moved right after the SIM pattern - attacker is cashing out.", verdict="SIM_SWAP", pts=25)
_add("SIM", ["social_engineering_victim"], "Giving CNIC/OTP to a caller is how SIM swaps start.", verdict="SIM_SWAP", pts=15)
_add("Accounts", ["whatsapp_logged_out", "sim_signal_anomaly"], "WhatsApp logout with a dead SIM - number may have been re-registered.", verdict="SIM_SWAP", pts=20)
# --- ACCOUNT HIJACK
_add("Accounts", ["account_takeover_signs"], "Credentials and recovery details were changed by someone else.", verdict="ACCOUNT_HIJACK", pts=40)
_add("Accounts", ["password_changed_not_me"], "A password change you did not make is a strong hijack sign.", verdict="ACCOUNT_HIJACK", pts=25)
_add("Accounts", ["new_login_alert", "weak_account_security"], "Unknown login on accounts with reused passwords and no 2FA.", verdict="ACCOUNT_HIJACK", pts=25)
_add("Accounts", ["friends_got_spam", "clicked_phishing_link"], "You clicked a phishing link and your contacts got spam from you.", verdict="ACCOUNT_HIJACK", pts=30)
_add("Accounts", ["bank_wallet_txn", "clicked_phishing_link"], "Money moved after you entered details on a suspicious link.", verdict="ACCOUNT_HIJACK", pts=30)
_add("Accounts", ["otp_not_requested", "new_login_alert"], "Someone is trying to log in with your details.", verdict="ACCOUNT_HIJACK", pts=25)
_add("Accounts", ["recovery_info_changed"], "Recovery details changed - the attacker is locking you out.", verdict="ACCOUNT_HIJACK", pts=30)
_add("Accounts", ["friends_got_spam"], "Contacts getting spam from you suggests a hijacked account.", verdict="ACCOUNT_HIJACK", pts=20)
_add("Accounts", ["otp_not_requested"], "Unrequested OTPs mean someone is probing your accounts.", verdict="ACCOUNT_HIJACK", pts=10)
# --- FAKE APK
_add("Apps", ["sideload_exposure", "unknown_app"], "Sideloaded APK with protection off and an unknown app installed.", verdict="FAKE_APK", pts=35)
_add("Apps", ["android", "apk_from_link", "admin_accessibility_granted"], "APK from a link asking for admin/accessibility rights is a banking-trojan pattern.", verdict="FAKE_APK", pts=35)
_add("Apps", ["apk_from_link", "bank_wallet_txn"], "Money moved after installing an APK from a link.", verdict="FAKE_APK", pts=30)
_add("Apps", ["apk_from_link", "unknown_balance_deduction"], "Balance deducted after installing an APK from a link.", verdict="FAKE_APK", pts=25)
_add("Apps", ["apk_from_link", "otp_not_requested"], "Malicious APKs read and forward OTP messages.", verdict="FAKE_APK", pts=25)
_add("Apps", ["android", "apk_from_link"], "Any APK from a chat link is risky.", verdict="FAKE_APK", pts=15)
_add("Apps", ["apk_from_link", "hidden_app"], "Installed APK now hides itself.", verdict="FAKE_APK", pts=25)
# --- NORMAL FAULT
_add("Battery", ["hardware_aging"], "An old battery explains the symptoms - no attacker needed.", verdict="NORMAL_FAULT", pts=30)
_add("Battery", ["benign_heat_context", "!phone_hot_idle"], "Heat only under load is normal.", verdict="NORMAL_FAULT", pts=25)
_add("Data", ["isp_issue"], "Slow on every device means ISP / router problem.", verdict="NORMAL_FAULT", pts=30)
_add("Apps", ["phone_overloaded"], "Full storage plus lag is a common non-attack cause.", verdict="NORMAL_FAULT", pts=30)
_add("Apps", ["post_update_effects"], "Problems started after an update.", verdict="NORMAL_FAULT", pts=25)
_add("Battery", ["battery_swollen"], "A swollen battery is a hardware failure (and a safety risk).", verdict="NORMAL_FAULT", pts=40)
_add("Battery", ["recent_drop_water", "battery_drain_fast"], "Physical damage explains the drain.", verdict="NORMAL_FAULT", pts=25)
_add("Battery", ["recent_drop_water", "shutdown_random"], "Physical damage explains random shutdowns.", verdict="NORMAL_FAULT", pts=25)
_add("Apps", ["apps_crash", "!unknown_app", "!hidden_app", "!ads_popups"], "Crashes with no suspicious apps or ads are a software glitch.", verdict="NORMAL_FAULT", pts=15)
_add("Data", ["data_spike", "!idle_data_use", "!unknown_app"], "A spike with no background use or unknown app is usually streaming or updates.", verdict="NORMAL_FAULT", pts=20)
_add("Battery", ["battery_drain_fast", "!phone_hot_idle", "!unknown_app", "!idle_data_use"], "Drain with no heat, no unknown app and no background data is ordinary wear.", verdict="NORMAL_FAULT", pts=20)
_add("SIM", ["sudden_no_signal", "!others_have_signal"], "Nobody nearby has signal either - area outage, not a SIM attack.", verdict="NORMAL_FAULT", pts=20)
_add("Apps", ["phone_slow_laggy", "old_device"], "Old phones slow down naturally.", verdict="NORMAL_FAULT", pts=15)

# ---------------------------------------------------------------- demo / test scenarios
SCENARIOS = {
    "📵 SIM died + OTPs": {"symptoms": ["sudden_no_signal", "others_have_signal", "otp_not_requested", "bank_wallet_txn", "phishing_call", "shared_cnic_or_otp"], "age": "1-2 years", "platform": "Android", "expect": "SIM_SWAP"},
    "📦 Installed 'Wedding.apk'": {"symptoms": ["apk_from_link", "play_protect_off", "unknown_app", "bank_wallet_txn", "otp_not_requested"], "age": "Under 1 year", "platform": "Android", "expect": "FAKE_APK"},
    "🔐 Locked out of Gmail": {"symptoms": ["password_changed_not_me", "recovery_info_changed", "new_login_alert", "reused_passwords", "no_2fa", "friends_got_spam"], "age": "1-2 years", "platform": "iPhone", "expect": "ACCOUNT_HIJACK"},
    "🦠 Pop-ups + data spike": {"symptoms": ["data_spike", "idle_data_use", "unknown_app", "ads_popups", "homescreen_changed", "phone_hot_idle", "battery_drain_fast"], "age": "1-2 years", "platform": "Android", "expect": "MALWARE"},
    "🔋 3-year-old phone dying": {"symptoms": ["battery_drain_fast", "shutdown_random"], "age": "3+ years", "platform": "Android", "expect": "NORMAL_FAULT"},
    "🌐 Slow net everywhere": {"symptoms": ["wifi_slow_everywhere", "data_spike"], "age": "1-2 years", "platform": "Android", "expect": "NORMAL_FAULT"},
    "🔥 Hot while gaming": {"symptoms": ["phone_hot_charging_or_gaming"], "age": "1-2 years", "platform": "Android", "expect": "NORMAL_FAULT"},
}
