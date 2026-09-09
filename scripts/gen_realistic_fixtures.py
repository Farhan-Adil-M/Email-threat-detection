#!/usr/bin/env python3
"""Generate realistic phishing and scam .eml fixture files.

Each email includes full RFC822 headers, brand-accurate HTML,
realistic phishing URLs, personalization, and proper footers.
"""
import os
from datetime import datetime, timedelta, timezone

OUT = "backend/data/fixtures"
os.makedirs(OUT, exist_ok=True)


def _received(from_host, from_ip, to_mx, date_str, proto="ESMTPS"):
    return (
        f"from {from_host} ({from_host} [{from_ip}])\n"
        f"\tby {to_mx} with {proto} id abc123def456\n"
        f"\tfor <victim@example.com>; {date_str}"
    )


def _dkim(domain, selector="default"):
    return (
        f"v=1; a=rsa-sha256; d={domain}; s={selector};\n"
        f"\tbh=2jNSNHusnVTj7ROUQWFNzNO/kMI=;\n"
        f"\th=from:to:subject:date:message-id:mime-version:content-type; b=abc=="
    )


def _auth(mx, domain, spf="pass", dkim="pass", dmarc="pass"):
    spf_hdr = f"spf=pass ({mx}: domain of sender@{domain} designates 203.0.113.1 as permitted)" if spf == "pass" else f"spf=fail ({mx}: domain not permitted)"
    dkim_hdr = f"dkim=pass header.d={domain}" if dkim == "pass" else f"dkim=fail header.d={domain}"
    dmarc_hdr = f"dmarc=pass (p=NONE) header.from={domain}" if dmarc == "pass" else f"dmarc=fail header.from={domain}"
    return f"Authentication-Results: {mx};\n\t{spf_hdr};\n\t{dkim_hdr};\n\t{dmarc_hdr}"


def _ts(days_ago=0, hour=8, minute=30):
    dt = datetime(2025, 9, 15, hour, minute, 0, tzinfo=timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def _build(filename, from_hdr, to_addr, subject, date, mid, extra_hdrs, body, mx="mx.google.com"):
    lines = [
        f"From: {from_hdr}",
        f"To: {to_addr}",
        f"Subject: {subject}",
        f"Date: {date}",
        f"Message-ID: <{mid}>",
        f"MIME-Version: 1.0",
    ]
    lines.extend(extra_hdrs)
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def _write(filename, content):
    path = os.path.join(OUT, filename)
    with open(path, "w") as f:
        f.write(content)
    return filename


# ─── HTML Components ──────────────────────────────────────────────────────────

def _html_wrapper(brand_color, brand_name, inner_html, footer_text, bg_color="#ffffff"):
    return f"""<div style="max-width:600px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif">
<div style="background:{brand_color};padding:24px;text-align:center">
<h1 style="color:white;margin:0;font-size:22px;font-weight:700">{brand_name}</h1>
</div>
<div style="padding:32px;background:{bg_color};border:1px solid #dadce0;border-top:none">
{inner_html}
</div>
<div style="padding:16px;background:#f8f9fa;border:1px solid #dadce0;border-top:none;text-align:center">
<p style="color:#5f6368;font-size:12px;margin:0">{footer_text}</p>
</div>
</div>"""


def _cta_button(url, text, color="#1a73e8"):
    return f'<div style="text-align:center;margin:24px 0"><a href="{url}" style="background:{color};color:white;padding:12px 28px;text-decoration:none;border-radius:4px;font-size:14px;display:inline-block;font-weight:600">{text}</a></div>'


# ─── CREDENTIAL HARVESTING ────────────────────────────────────────────────────

def gen_google_signin():
    inner = """<h2 style="color:#202124;font-size:18px;margin-top:0">New sign-in to your Google Account</h2>
<p style="color:#5f6368;font-size:14px;line-height:1.6">Hi John,</p>
<p style="color:#5f6368;font-size:14px;line-height:1.6">We detected a new sign-in to your Google Account on a <strong>Windows PC</strong>.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#5f6368;font-size:14px;border-bottom:1px solid #e8eaed"><strong>Device:</strong></td><td style="padding:8px 12px;color:#202124;font-size:14px;border-bottom:1px solid #e8eaed">Windows PC</td></tr>
<tr><td style="padding:8px 12px;color:#5f6368;font-size:14px;border-bottom:1px solid #e8eaed"><strong>Location:</strong></td><td style="padding:8px 12px;color:#202124;font-size:14px;border-bottom:1px solid #e8eaed">Berlin, Germany</td></tr>
<tr><td style="padding:8px 12px;color:#5f6368;font-size:14px;border-bottom:1px solid #e8eaed"><strong>Time:</strong></td><td style="padding:8px 12px;color:#202124;font-size:14px;border-bottom:1px solid #e8eaed">Sep 15, 2025 7:12 AM</td></tr>
<tr><td style="padding:8px 12px;color:#5f6368;font-size:14px"><strong>Browser:</strong></td><td style="padding:8px 12px;color:#202124;font-size:14px">Chrome on Windows</td></tr>
</table>
<p style="color:#5f6368;font-size:14px;line-height:1.6">If this was not you, secure your account:</p>
""" + _cta_button("https://account-google.com/security/activity?id=jsmith%40gmail.com", "Check activity") + """
<p style="color:#5f6368;font-size:12px;line-height:1.5">If you do not recognize this activity, we recommend you change your password immediately and review your security settings.</p>"""
    return _write("phish_google_signin.eml", _build(
        "phish_google_signin.eml",
        '"Google" <no-reply@google.com>', "john.smith@gmail.com",
        "Google Security Alert: New sign-in from Windows device",
        _ts(0, 7, 15), "google-alert-A9F3K2",
        [_received("smtp.gmail.com", "209.85.220.41", "mx.google.com", _ts(0, 7, 14)),
         _dkim("google.com", "google"), _auth("mx.google.com", "google.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#1a73e8", "Google", inner, "Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043"),
    ))


def gen_google_password():
    inner = """<h2 style="color:#202124;font-size:18px;margin-top:0">Your password expires soon</h2>
<p style="color:#5f6368;font-size:14px;line-height:1.6">Hi John,</p>
<p style="color:#5f6368;font-size:14px;line-height:1.6">Your Google password will expire in <strong>24 hours</strong>. After that, you will not be able to sign in to your account.</p>
""" + _cta_button("https://account-google.com/password/update?user=jsmith", "Update password") + """
<p style="color:#5f6368;font-size:12px;line-height:1.5">If you did not request this change, please review your security settings immediately.</p>"""
    return _write("phish_google_password.eml", _build(
        "phish_google_password.eml",
        '"Google Account" <security@google.com>', "john.smith@gmail.com",
        "Your Google password will expire in 24 hours",
        _ts(0, 14, 22), "google-pw-B7D4E1",
        [_received("smtp.gmail.com", "209.85.220.42", "mx.google.com", _ts(0, 14, 21)),
         _dkim("google.com", "google"), _auth("mx.google.com", "google.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#1a73e8", "Google", inner, "Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043"),
    ))


def gen_microsoft_signin():
    inner = """<h2 style="color:#323130;font-size:18px;margin-top:0">Unusual sign-in activity</h2>
<p style="color:#605e5c;font-size:14px;line-height:1.6">We detected a sign-in from a device or location you do not usually use.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px;border-bottom:1px solid #edebe9"><strong>Date:</strong></td><td style="padding:8px 12px;color:#323130;font-size:14px;border-bottom:1px solid #edebe9">September 15, 2025</td></tr>
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px;border-bottom:1px solid #edebe9"><strong>Location:</strong></td><td style="padding:8px 12px;color:#323130;font-size:14px;border-bottom:1px solid #edebe9">Mumbai, India</td></tr>
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px;border-bottom:1px solid #edebe9"><strong>IP:</strong></td><td style="padding:8px 12px;color:#323130;font-size:14px;border-bottom:1px solid #edebe9">103.21.124.88</td></tr>
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px"><strong>Browser:</strong></td><td style="padding:8px 12px;color:#323130;font-size:14px">Chrome on Windows</td></tr>
</table>
""" + _cta_button("https://account-microsoft.com/security/activity?id=admin%40contoso.com", "Secure account", "#0078d4") + """
<p style="color:#605e5c;font-size:12px;line-height:1.5">If you do not recognize this sign-in, secure your account immediately.</p>"""
    return _write("phish_microsoft_signin.eml", _build(
        "phish_microsoft_signin.eml",
        '"Microsoft" <no-reply@microsoft.com>', "admin@contoso.com",
        "Microsoft account: Unusual sign-in activity",
        _ts(0, 9, 45), "ms-alert-C3E5F7",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "40.97.164.129", "mail-sor-f45.acdf1d-kopilot.com", _ts(0, 9, 44)),
         _dkim("microsoft.com", "selector1"), _auth("mail-sor-f45.acdf1d-kopilot.com", "microsoft.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0078d4", "Microsoft", inner, "Microsoft Corporation, One Microsoft Way, Redmond, WA 98052"),
    ))


def gen_microsoft_verify():
    inner = """<h2 style="color:#323130;font-size:18px;margin-top:0">Verify your identity</h2>
<p style="color:#605e5c;font-size:14px;line-height:1.6">Hi Admin,</p>
<p style="color:#605e5c;font-size:14px;line-height:1.6">We have detected unusual activity on your Microsoft 365 account. To protect your account, we need you to verify your identity.</p>
<p style="color:#605e5c;font-size:14px;line-height:1.6"><strong>What happened:</strong></p>
<ul style="color:#605e5c;font-size:14px;line-height:1.8">
<li>New sign-in from an unrecognized device</li>
<li>Location: Lagos, Nigeria</li>
<li>Time: September 14, 2025 11:28 PM</li>
</ul>
""" + _cta_button("https://account-microsoft.com/verify/identity?user=admin%40contoso.com", "Verify identity", "#0078d4") + """
<p style="color:#605e5c;font-size:12px;line-height:1.5">If you do not verify within 48 hours, your account will be temporarily suspended.</p>"""
    return _write("phish_microsoft_verify.eml", _build(
        "phish_microsoft_verify.eml",
        '"Microsoft 365" <security-alert@microsoft.com>', "admin@contoso.com",
        "Verify your identity - Microsoft 365 account at risk",
        _ts(1, 11, 30), "ms-verify-D4F6G8",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "40.97.164.130", "mail-sor-f45.acdf1d-kopilot.com", _ts(1, 11, 29)),
         _dkim("microsoft.com", "selector1"), _auth("mail-sor-f45.acdf1d-kopilot.com", "microsoft.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0078d4", "Microsoft 365", inner, "Microsoft Corporation, One Microsoft Way, Redmond, WA 98052"),
    ))


def gen_apple_locked():
    inner = """<h2 style="color:#1d1d1f;font-size:18px;margin-top:0;text-align:center">Apple ID Locked</h2>
<p style="color:#1d1d1f;font-size:14px;line-height:1.6;text-align:center">Your Apple ID <strong>john@icloud.com</strong> has been locked due to too many failed sign-in attempts.</p>
<div style="background:#f5f5f7;border-radius:12px;padding:20px;margin:20px 0;text-align:center">
<p style="color:#1d1d1f;font-size:14px;margin:0">To unlock your account, verify your identity.</p>
</div>
""" + _cta_button("https://apple-id-verify.com/unlock?email=john%40icloud.com", "Unlock Apple ID", "#0071e3") + """
<p style="color:#86868b;font-size:12px;text-align:center;line-height:1.5">If you did not attempt to sign in, contact Apple Support.</p>"""
    return _write("phish_apple_locked.eml", _build(
        "phish_apple_locked.eml",
        '"Apple" <no-reply@apple.com>', "john@icloud.com",
        "Your Apple ID has been locked",
        _ts(0, 6, 10), "apple-lock-E5G7H9",
        [_received("smtp.mail.outlook.com", "40.92.22.162", "mx.mail.cloudflare.net", _ts(0, 6, 9)),
         _dkim("apple.com", "sig1"), _auth("mx.mail.cloudflare.net", "apple.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#000000", "Apple", inner, "Apple Inc. One Apple Park Way, Cupertino, CA 95014"),
    ))


def gen_apple_billing():
    inner = """<h2 style="color:#1d1d1f;font-size:18px;margin-top:0;text-align:center">Payment method needs attention</h2>
<p style="color:#1d1d1f;font-size:14px;line-height:1.6;text-align:center">Hi John,</p>
<p style="color:#1d1d1f;font-size:14px;line-height:1.6;text-align:center">We were unable to charge your payment method for your Apple subscriptions.</p>
<div style="background:#f5f5f7;border-radius:12px;padding:20px;margin:20px 0">
<table style="width:100%;font-size:14px">
<tr><td style="padding:4px 0;color:#86868b">Account:</td><td style="padding:4px 0;color:#1d1d1f;text-align:right">john@icloud.com</td></tr>
<tr><td style="padding:4px 0;color:#86868b">Status:</td><td style="padding:4px 0;color:#c41200;text-align:right">Payment failed</td></tr>
</table>
</div>
""" + _cta_button("https://apple-id-verify.com/billing/update?account=john", "Update payment", "#0071e3") + """
<p style="color:#86868b;font-size:12px;text-align:center;line-height:1.5">If you did not make this change, review your account security.</p>"""
    return _write("phish_apple_billing.eml", _build(
        "phish_apple_billing.eml",
        '"Apple" <billing@apple.com>', "john@icloud.com",
        "Verify your payment method for Apple ID",
        _ts(1, 16, 5), "apple-bill-F6H8I0",
        [_received("smtp.mail.outlook.com", "40.92.22.163", "mx.mail.cloudflare.net", _ts(1, 16, 4)),
         _dkim("apple.com", "sig1"), _auth("mx.mail.cloudflare.net", "apple.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#000000", "Apple", inner, "Apple Inc. One Apple Park Way, Cupertino, CA 95014"),
    ))


def gen_yahoo_storage():
    inner = """<h2 style="color:#0f1419;font-size:18px;margin-top:0">Storage is full</h2>
<p style="color:#536471;font-size:14px;line-height:1.6">Hi,</p>
<p style="color:#536471;font-size:14px;line-height:1.6">Your Yahoo Mail storage has reached <strong>99% capacity</strong>. You will not be able to receive new emails until you free up space or upgrade.</p>
<div style="background:#f7f7f7;border-radius:8px;padding:16px;margin:16px 0">
<table style="width:100%;font-size:14px">
<tr><td style="padding:4px 0;color:#536471">Used:</td><td style="padding:4px 0;color:#0f1419;text-align:right">9.9 GB / 10 GB</td></tr>
</table>
</div>
""" + _cta_button("https://yahoo-verify-account.com/upgrade?user=user", "Upgrade storage", "#6001d2")
    return _write("phish_yahoo_storage.eml", _build(
        "phish_yahoo_storage.eml",
        '"Yahoo Mail" <no-reply@yahoo.com>', "user@yahoo.com",
        "Your Yahoo Mail storage is full",
        _ts(0, 12, 0), "yahoo-full-G7I9J1",
        [_received("mta7.am0.yahoodns.net", "66.196.118.34", "mx.mail.yahoo.com", _ts(0, 11, 59)),
         _dkim("yahoo.com", "s1024"), _auth("mx.mail.yahoo.com", "yahoo.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#6001d2", "Yahoo Mail", inner, "Yahoo Inc. 225 Bernardo Ave, Mountain View, CA 94043"),
    ))


def gen_instagram_password():
    inner = """<h2 style="color:#262626;font-size:18px;margin-top:0;text-align:center">Password change request</h2>
<p style="color:#8e8e8e;font-size:14px;line-height:1.6;text-align:center">Hi john.smith,</p>
<p style="color:#8e8e8e;font-size:14px;line-height:1.6;text-align:center">We received a request to change the password for your account. If this was you, you can ignore this message.</p>
""" + _cta_button("https://instagram-account-verify.com/reset?user=john.smith", "Reset password", "#0095f6") + """
<p style="color:#8e8e8e;font-size:12px;text-align:center;line-height:1.5">If you did not request this, secure your account immediately.</p>"""
    return _write("phish_instagram_password.eml", _build(
        "phish_instagram_password.eml",
        '"Instagram" <security@instagram.com>', "john.smith@gmail.com",
        "Someone tried to change your Instagram password",
        _ts(0, 15, 30), "ig-pw-H8J0K2",
        [_received("smtp.facebookmail.com", "157.240.22.41", "mx.mail.cloudflare.net", _ts(0, 15, 29)),
         _dkim("instagram.com", "proton"), _auth("mx.mail.cloudflare.net", "instagram.com", dkim="fail"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)", "Instagram", inner, "Instagram, 1 Hacker Way, Menlo Park, CA 94025"),
    ))


def gen_facebook_login():
    inner = """<h2 style="color:#1c1e21;font-size:18px;margin-top:0">New login to Facebook</h2>
<p style="color:#606770;font-size:14px;line-height:1.6">Hi John,</p>
<p style="color:#606770;font-size:14px;line-height:1.6">We detected a new login to your Facebook account.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#606770;font-size:14px;border-bottom:1px solid #ddd"><strong>Date:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px;border-bottom:1px solid #ddd">September 15, 2025</td></tr>
<tr><td style="padding:8px 12px;color:#606770;font-size:14px;border-bottom:1px solid #ddd"><strong>Device:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px;border-bottom:1px solid #ddd">Chrome on Windows</td></tr>
<tr><td style="padding:8px 12px;color:#606770;font-size:14px;border-bottom:1px solid #ddd"><strong>Location:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px;border-bottom:1px solid #ddd">Lagos, Nigeria</td></tr>
<tr><td style="padding:8px 12px;color:#606770;font-size:14px"><strong>IP:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px">197.210.65.123</td></tr>
</table>
""" + _cta_button("https://facebook-security-alert.com/secure?id=fbuser123", "This was not me", "#1877f2")
    return _write("phish_facebook_login.eml", _build(
        "phish_facebook_login.eml",
        '"Facebook" <security@facebookmail.com>', "john.smith@gmail.com",
        "New login to Facebook from Chrome on Windows",
        _ts(0, 3, 45), "fb-login-I9J1K3",
        [_received("smtp.facebookmail.com", "157.240.22.42", "mx.mail.cloudflare.net", _ts(0, 3, 44)),
         _dkim("facebookmail.com", "proton"), _auth("mx.mail.cloudflare.net", "facebookmail.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#1877f2", "facebook", inner, "Meta Platforms, Inc. 1 Hacker Way, Menlo Park, CA 94025"),
    ))


def gen_linkedin_signin():
    inner = """<h2 style="color:#000000e6;font-size:18px;margin-top:0">New sign-in detected</h2>
<p style="color:#00000099;font-size:14px;line-height:1.6">Hi,</p>
<p style="color:#00000099;font-size:14px;line-height:1.6">We detected a sign-in to your LinkedIn account from a new device or browser.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#00000099;font-size:14px;border-bottom:1px solid #e0e0e0"><strong>Date:</strong></td><td style="padding:8px 12px;color:#000000e6;font-size:14px;border-bottom:1px solid #e0e0e0">Sep 15, 2025 10:14 AM</td></tr>
<tr><td style="padding:8px 12px;color:#00000099;font-size:14px;border-bottom:1px solid #e0e0e0"><strong>Location:</strong></td><td style="padding:8px 12px;color:#000000e6;font-size:14px;border-bottom:1px solid #e0e0e0">Mumbai, India</td></tr>
<tr><td style="padding:8px 12px;color:#00000099;font-size:14px"><strong>Browser:</strong></td><td style="padding:8px 12px;color:#000000e6;font-size:14px">Chrome on Linux</td></tr>
</table>
""" + _cta_button("https://linkedin-account-alert.com/verify?user=professional", "Review activity", "#0077b5") + """
<p style="color:#00000099;font-size:12px;line-height:1.5">If you do not recognize this activity, change your password immediately.</p>"""
    return _write("phish_linkedin_signin.eml", _build(
        "phish_linkedin_signin.eml",
        '"LinkedIn" <notifications@linkedin.com>', "professional@company.com",
        "Sign-in from new location detected",
        _ts(0, 10, 15), "li-signin-J0K2L4",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "216.243.31.201", "mx.mail.cloudflare.net", _ts(0, 10, 14)),
         _dkim("linkedin.com", "default"), _auth("mx.mail.cloudflare.net", "linkedin.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0077b5", "LinkedIn", inner, "LinkedIn Corporation, 2029 Stierlin Ct, Mountain View, CA 94043"),
    ))


def gen_dropbox_verify():
    inner = """<h2 style="color:#1e1919;font-size:18px;margin-top:0">Your account needs verification</h2>
<p style="color:#637282;font-size:14px;line-height:1.6">Hi,</p>
<p style="color:#637282;font-size:14px;line-height:1.6">Due to recent unusual activity, we need you to verify your identity. If you do not verify within <strong>72 hours</strong>, your account will be temporarily deactivated.</p>
<div style="background:#f5f7fa;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#637282;font-size:14px;margin:0"><strong>Account:</strong> user@company.com</p>
<p style="color:#637282;font-size:14px;margin:4px 0 0"><strong>Status:</strong> <span style="color:#d0021b">Pending verification</span></p>
</div>
""" + _cta_button("https://dropbox-file-share.com/verify?account=user", "Verify account", "#0061ff")
    return _write("phish_dropbox_verify.eml", _build(
        "phish_dropbox_verify.eml",
        '"Dropbox" <no-reply@dropbox.com>', "user@company.com",
        "Verify your Dropbox account to avoid deactivation",
        _ts(1, 8, 0), "db-verify-K1L3M5",
        [_received("smtp.dropbox.com", "162.125.66.3", "mx.mail.cloudflare.net", _ts(1, 7, 59)),
         _dkim("dropbox.com", "default"), _auth("mx.mail.cloudflare.net", "dropbox.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0061ff", "Dropbox", inner, "Dropbox, Inc. 1800 Owens St, San Francisco, CA 94158"),
    ))


def gen_slack_verify():
    inner = """<h2 style="color:#1d1c1d;font-size:18px;margin-top:0">Workspace access expiring</h2>
<p style="color:#616061;font-size:14px;line-height:1.6">Hi,</p>
<p style="color:#616061;font-size:14px;line-height:1.6">Your access to the <strong>Acme Corp</strong> Slack workspace is set to expire today. You&#39;ll lose access to all channels and messages unless you renew.</p>
""" + _cta_button("https://slack-account-verify.com/renew?workspace=acme", "Renew access", "#4a154b") + """
<p style="color:#616061;font-size:12px;line-height:1.5">If you believe this is an error, contact your workspace admin.</p>"""
    return _write("phish_slack_verify.eml", _build(
        "phish_slack_verify.eml",
        '"Slack" <notifications@slack.com>', "user@company.com",
        "Your Slack workspace access expires today",
        _ts(0, 13, 20), "slack-exp-L2M4N6",
        [_received("smtp.slack.com", "54.192.72.131", "mx.mail.cloudflare.net", _ts(0, 13, 19)),
         _dkim("slack.com", "default"), _auth("mx.mail.cloudflare.net", "slack.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#4a154b", "Slack", inner, "Slack Technologies, LLC. 500 Howard St, San Francisco, CA 94105"),
    ))


# ─── BEC / CEO FRAUD ──────────────────────────────────────────────────────────

def gen_bec_ceo_wire():
    return _write("phish_bec_ceo_wire.eml", _build(
        "phish_bec_ceo_wire.eml",
        '"David Chen" <david.chen@acme-corp.com>', "ap@acme-corp.com",
        "CONFIDENTIAL: Wire transfer - process before market open",
        _ts(0, 6, 0), "ceo-wire-M3N5O7",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """I need you to process the following wire transfer before market open. This is related to the acquisition we discussed - keep this between us.

Beneficiary: Northstar Capital LLC
Bank: JPMorgan Chase
Routing: 021000021
Account: 7733991155
Amount: $425,000.00
Reference: Q3 Advisory Fee

I am in meetings all morning. Please confirm once done.

Thanks,
David Chen
CEO, Acme Corp

Sent from my iPhone""",
    ))


def gen_bec_cfo_redirect():
    return _write("phish_bec_cfo_redirect.eml", _build(
        "phish_bec_cfo_redirect.eml",
        '"Finance" <finance@acme-corp.com>', "ap@acme-corp.com",
        "URGENT: Vendor payment redirect - new bank details",
        _ts(0, 8, 30), "cfo-redirect-N4O6P8",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Hi AP,

I need you to redirect the upcoming Pinnacle Consulting payment from their old Chase account to their new Wells Fargo account:

OLD: Chase ending in 8899
NEW: Wells Fargo ending in 3344
Routing: 121000248
Account: 5566778899

This is time-sensitive - their old account closes today. Do NOT call the vendor to confirm - I already spoke with their CFO directly. Just process the change and confirm.

Sent from my iPhone""",
    ))


def gen_bec_gift_cards():
    return _write("phish_bec_gift_cards.eml", _build(
        "phish_bec_gift_cards.eml",
        '"David Chen CEO" <david.chen@acme-corp.com>', "assistant@acme-corp.com",
        "Quick favor - need you to get some gift cards",
        _ts(1, 9, 15), "ceo-gift-O5P7Q9",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Hi,

I am stuck in a board meeting and cannot make calls right now. I need you to go to the store and pick up 5 Apple Gift Cards ($200 each). I need them for a client appreciation gesture.

Please scratch off the codes and email photos of them to me. I will reimburse you when I'm back in the office.

This is urgent - the client is waiting.

Thanks,
David

Sent from my iPhone""",
    ))


def gen_bec_cfo_urgent():
    return _write("phish_bec_cfo_urgent.eml", _build(
        "phish_bec_cfo_urgent.eml",
        '"CFO Office" <cfo@acme-corp.com>', "ap@acme-corp.com",
        "URGENT: Process this wire - do not call vendor",
        _ts(0, 7, 45), "cfo-wire2-P6Q8R0",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Hi AP,

I need you to process the following wire before 10am. This is for the Pinnacle acquisition that was announced yesterday.

Beneficiary: Northstar Capital LLC
Bank: Wells Fargo
Routing: 121000248
Account: 5566778899
Amount: $280,000.00
Reference: Acquisition Deposit

Do NOT discuss with anyone outside finance. I'm in meetings all morning.

Sent from my iPhone""",
    ))


def gen_bec_vendor_change():
    return _write("phish_bec_vendor_change.eml", _build(
        "phish_bec_vendor_change.eml",
        '"Robert Chen" <robert.chen@trusted-vendor.com>', "ap@acme-corp.com",
        "Updated bank details - effective immediately",
        _ts(1, 11, 0), "vendor-bank-Q7R9S1",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Hi AP Team,

Please note that our bank account details have changed due to a recent system migration. Please update your records for all future payments:

NEW DETAILS:
Company: Trusted Vendor Solutions Inc
Bank: Bank of America
Account: 3344556677
Routing: 026009593
SWIFT: BOFAUS3N

Our old Chase account will be closed on September 20. Payments sent after that date will be returned.

Please confirm receipt of this email.

Robert Chen
CFO, Trusted Vendor Solutions""",
    ))


def gen_bec_vendor_redirect():
    return _write("phish_bec_vendor_redirect.eml", _build(
        "phish_bec_vendor_redirect.eml",
        '"Finance Director" <finance@partner-company.com>', "payments@acme-corp.com",
        "Re: Invoice payment - new bank details attached",
        _ts(0, 14, 30), "partner-bank-R8S0T2",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Following up on our call yesterday. Here are the updated payment details:

Company: Partner Industries Ltd
Bank: Wells Fargo
Account Name: Partner Industries Operating
Account: 5566778899
Routing: 121000248

Please redirect the outstanding balance of $87,500 to this account.

Thanks,
Finance Director
Partner Industries""",
    ))


def gen_bec_it_admin():
    return _write("phish_bec_it_admin.eml", _build(
        "phish_bec_it_admin.eml",
        '"IT Security" <it-security@acme-corp.com>', "admin@acme-corp.com",
        "Security audit - admin credentials required",
        _ts(1, 10, 0), "it-audit-S9T1U3",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Hi Admin,

We are conducting a mandatory security audit today. As part of the audit, we need all administrators to verify their credentials through our secure portal.

Please provide your admin username and current password so we can validate your account against our security baseline.

This is required by end of business today. Non-compliance will result in temporary account suspension.

Use this link to submit your credentials:
https://acme-corp-portal.com/security/verify

IT Security Team""",
    ))


def gen_bec_lawyer():
    return _write("phish_bec_lawyer.eml", _build(
        "phish_bec_lawyer.eml",
        '"James Morrison" <james.morrison@morrison-law.com>', "cfo@acme-corp.com",
        "Settlement transfer required - Case #ML-2025-4421",
        _ts(0, 16, 0), "lawyer-wire-T0U2V4",
        ['Content-Type: text/plain; charset="UTF-8"'],
        """Dear CFO,

I am writing regarding the settlement in the matter of TechCorp v. Acme Corp (Case #ML-2025-4421). Per the settlement agreement signed yesterday, the following transfer is required within 48 hours:

Beneficiary: Morrison & Associates Trust Account
Bank: JPMorgan Chase
Routing: 021000021
Account: 9988776655
Amount: $280,000.00
Reference: Settlement - ML-2025-4421

This transfer must be completed by September 17, 2025 to avoid default judgment.

Please confirm once the transfer has been initiated.

James Morrison, Esq.
Morrison & Associates LLP
1200 Market Street, Suite 400
San Francisco, CA 94103
(415) 555-0142""",
    ))


# ─── BANKING / FINANCE ────────────────────────────────────────────────────────

def gen_chase_fraud():
    inner = """<h2 style="color:#1a1a1a;font-size:18px;margin-top:0">Suspicious transaction detected</h2>
<p style="color:#4a4a4a;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#4a4a4a;font-size:14px;line-height:1.6">We detected a suspicious transaction on your Chase account ending in <strong>4521</strong>:</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:10px 12px;color:#4a4a4a;font-size:14px;border-bottom:1px solid #e5e5e5"><strong>Amount:</strong></td><td style="padding:10px 12px;color:#1a1a1a;font-size:14px;border-bottom:1px solid #e5e5e5">$2,847.00</td></tr>
<tr><td style="padding:10px 12px;color:#4a4a4a;font-size:14px;border-bottom:1px solid #e5e5e5"><strong>Merchant:</strong></td><td style="padding:10px 12px;color:#1a1a1a;font-size:14px;border-bottom:1px solid #e5e5e5">BestBuy.com</td></tr>
<tr><td style="padding:10px 12px;color:#4a4a4a;font-size:14px;border-bottom:1px solid #e5e5e5"><strong>Date:</strong></td><td style="padding:10px 12px;color:#1a1a1a;font-size:14px;border-bottom:1px solid #e5e5e5">Sep 15, 2025 7:15 AM</td></tr>
<tr><td style="padding:10px 12px;color:#4a4a4a;font-size:14px"><strong>Status:</strong></td><td style="padding:10px 12px;color:#c41200;font-size:14px"><strong>PENDING</strong></td></tr>
</table>
<p style="color:#4a4a4a;font-size:14px;line-height:1.6">If you did NOT make this transaction, take action immediately:</p>
""" + _cta_button("https://chase-alerts-verify.com/dispute?acct=4521&ref=TX8827", "Dispute transaction", "#117aca") + """
<p style="color:#4a4a4a;font-size:12px;line-height:1.5">Or call us at 1-800-935-9935 (24/7)</p>"""
    return _write("phish_chase_fraud.eml", _build(
        "phish_chase_fraud.eml",
        '"Chase" <alerts@chase.com>', "john.smith@gmail.com",
        "Chase: Suspicious transaction on your account",
        _ts(0, 7, 30), "chase-fraud-U1V3W5",
        [_received("smtp.chase.com", "199.204.138.96", "mx.mail.cloudflare.net", _ts(0, 7, 29)),
         _dkim("chase.com", "s1024"), _auth("mx.mail.cloudflare.net", "chase.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#117aca", "CHASE", inner, "JPMorgan Chase Bank, N.A. Member FDIC. Equal Housing Lender"),
    ))


def gen_wells_fargo_lock():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Account locked</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your Wells Fargo account has been <strong>temporarily locked</strong> due to multiple failed login attempts from an unrecognized device.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Account:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">****4521</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Failed attempts:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">3</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Location:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px">Unknown - Bucharest, Romania</td></tr>
</table>
""" + _cta_button("https://wellsfargo-security.com/unlock?acct=4521", "Unlock account", "#d71e28") + """
<p style="color:#666666;font-size:12px;line-height:1.5">If you did not attempt to log in, call us immediately at 1-800-869-3557.</p>"""
    return _write("phish_wells_fargo.eml", _build(
        "phish_wells_fargo.eml",
        '"Wells Fargo" <security@wellsfargo.com>', "customer@gmail.com",
        "Your Wells Fargo account has been locked",
        _ts(0, 10, 10), "wf-lock-V2W4X6",
        [_received("smtp.wellsfargo.com", "216.239.120.247", "mx.mail.cloudflare.net", _ts(0, 10, 9)),
         _dkim("wellsfargo.com", "default"), _auth("mx.mail.cloudflare.net", "wellsfargo.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#d71e28", "Wells Fargo", inner, "Wells Fargo Bank, N.A. Member FDIC. Equal Housing Lender"),
    ))


def gen_boa_verify():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Verify your identity</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">We detected unusual activity on your Bank of America account. To protect your account, we've temporarily restricted access until you verify your identity.</p>
""" + _cta_button("https://bankofamerica-verify.com/identity?acct=4521", "Verify identity", "#e31837") + """
<p style="color:#666666;font-size:12px;line-height:1.5">You must verify within 24 hours or your account will be permanently restricted.</p>"""
    return _write("phish_boa_verify.eml", _build(
        "phish_boa_verify.eml",
        '"Bank of America" <alerts@bankofamerica.com>', "customer@gmail.com",
        "Verify your identity to restore account access",
        _ts(1, 12, 0), "boa-verify-W3X5Y7",
        [_received("smtp.bankofamerica.com", "171.161.192.130", "mx.mail.cloudflare.net", _ts(1, 11, 59)),
         _dkim("bankofamerica.com", "default"), _auth("mx.mail.cloudflare.net", "bankofamerica.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#e31837", "Bank of America", inner, "Bank of America, N.A. Member FDIC. Equal Housing Lender"),
    ))


def gen_paypal_limited():
    inner = """<h2 style="color:#252525;font-size:18px;margin-top:0">Your account has been limited</h2>
<p style="color:#555555;font-size:14px;line-height:1.6">Dear John Smith,</p>
<p style="color:#555555;font-size:14px;line-height:1.6">We have noticed some unusual activity on your PayPal account. As a security measure, we've limited your account until you verify your information.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#555555;font-size:14px;border-bottom:1px solid #eee"><strong>Account:</strong></td><td style="padding:8px 12px;color:#252525;font-size:14px;border-bottom:1px solid #eee">john.smith@gmail.com</td></tr>
<tr><td style="padding:8px 12px;color:#555555;font-size:14px"><strong>Reason:</strong></td><td style="padding:8px 12px;color:#252525;font-size:14px">Unusual login activity</td></tr>
</table>
""" + _cta_button("https://paypal-account-verify.com/restore?user=john.smith", "Restore access", "#003087")
    return _write("phish_paypal_limited.eml", _build(
        "phish_paypal_limited.eml",
        '"PayPal" <service@paypal.com>', "john.smith@gmail.com",
        "Your PayPal account has been limited",
        _ts(0, 11, 45), "paypal-lim-X4Y6Z8",
        [_received("smtp.paypal.com", "173.193.198.97", "mx.mail.cloudflare.net", _ts(0, 11, 44)),
         _dkim("paypal.com", "default"), _auth("mx.mail.cloudflare.net", "paypal.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#003087", "PayPal", inner, "PayPal, Inc. 2211 North First Street, San Jose, CA 95131"),
    ))


def gen_venmo_request():
    inner = """<h2 style="color:#1a1a1a;font-size:18px;margin-top:0;text-align:center">Payment request</h2>
<p style="color:#666666;font-size:14px;line-height:1.6;text-align:center">Hello,</p>
<p style="color:#666666;font-size:14px;line-height:1.6;text-align:center">You have a pending payment request from <strong>@unknown-user</strong>:</p>
<div style="background:#f8f8f8;border-radius:8px;padding:20px;margin:20px 0;text-align:center">
<p style="color:#1a1a1a;font-size:24px;font-weight:bold;margin:0">$850.00</p>
<p style="color:#666666;font-size:14px;margin:4px 0 0">"For concert tickets"</p>
</div>
""" + _cta_button("https://venmo-pay-request.com/pay?req=V8827", "Pay now", "#3d95ce")
    return _write("phish_venmo_request.eml", _build(
        "phish_venmo_request.eml",
        '"Venmo" <notifications@venmo.com>', "user@gmail.com",
        "You have a pending payment request of $850.00",
        _ts(0, 14, 55), "venmo-req-Y5Z7A9",
        [_received("smtp.venmo.com", "199.204.138.100", "mx.mail.cloudflare.net", _ts(0, 14, 54)),
         _dkim("venmo.com", "default"), _auth("mx.mail.cloudflare.net", "venmo.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#3d95ce", "venmo", inner, "Venmo, Inc. a subsidiary of PayPal, Inc. 225 Bush St, San Francisco, CA 94104"),
    ))


def gen_zelle_receipt():
    inner = """<h2 style="color:#1a1a1a;font-size:18px;margin-top:0;text-align:center">Payment received</h2>
<p style="color:#666666;font-size:14px;line-height:1.6;text-align:center">Hello,</p>
<p style="color:#666666;font-size:14px;line-height:1.6;text-align:center">You have received a Zelle payment of <strong>$1,200.00</strong> from an unknown sender.</p>
<div style="background:#f8f8f8;border-radius:8px;padding:20px;margin:20px 0;text-align:center">
<p style="color:#1a1a1a;font-size:24px;font-weight:bold;margin:0">$1,200.00</p>
<p style="color:#666666;font-size:14px;margin:4px 0 0">From: Unknown Sender</p>
</div>
""" + _cta_button("https://zelle-pay-alert.com/confirm?pay=Z8827", "Confirm & deposit", "#6d1ed4")
    return _write("phish_zelle_receipt.eml", _build(
        "phish_zelle_receipt.eml",
        '"Zelle" <alerts@zelle.com>', "customer@aol.com",
        "You received a Zelle payment of $1,200.00",
        _ts(1, 9, 30), "zelle-rec-Z6A8B0",
        [_received("smtp.zelle.com", "199.204.138.101", "mx.mail.cloudflare.net", _ts(1, 9, 29)),
         _dkim("zelle.com", "default"), _auth("mx.mail.cloudflare.net", "zelle.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#6d1ed4", "Zelle", inner, "Zelle and the Zelle related marks are wholly owned by Early Warning Services, LLC"),
    ))


def gen_amex_unusual():
    inner = """<h2 style="color:#00175a;font-size:18px;margin-top:0">Unusual spending detected</h2>
<p style="color:#4a4a4a;font-size:14px;line-height:1.6">Dear Card Member,</p>
<p style="color:#4a4a4a;font-size:14px;line-height:1.6">We detected unusual spending on your American Express card ending in <strong>1007</strong>:</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#4a4a4a;font-size:14px;border-bottom:1px solid #eee"><strong>Amount:</strong></td><td style="padding:8px 12px;color:#00175a;font-size:14px;border-bottom:1px solid #eee">$4,299.00</td></tr>
<tr><td style="padding:8px 12px;color:#4a4a4a;font-size:14px;border-bottom:1px solid #eee"><strong>Merchant:</strong></td><td style="padding:8px 12px;color:#00175a;font-size:14px;border-bottom:1px solid #eee">Apple Online Store</td></tr>
<tr><td style="padding:8px 12px;color:#4a4a4a;font-size:14px"><strong>Date:</strong></td><td style="padding:8px 12px;color:#00175a;font-size:14px">Sep 15, 2025 2:47 PM</td></tr>
</table>
""" + _cta_button("https://amex-verify.com/review?card=1007&ref=TX9921", "Review transaction", "#006fcf") + """
<p style="color:#4a4a4a;font-size:12px;line-height:1.5">If you do not recognize this transaction, call us at 1-800-528-4800.</p>"""
    return _write("phish_amex_unusual.eml", _build(
        "phish_amex_unusual.eml",
        '"American Express" <alerts@americanexpress.com>', "customer@gmail.com",
        "Unusual spending detected on your card",
        _ts(0, 15, 0), "amex-unusual-A7B9C1",
        [_received("smtp.aexp.com", "199.204.138.102", "mx.mail.cloudflare.net", _ts(0, 14, 59)),
         _dkim("americanexpress.com", "default"), _auth("mx.mail.cloudflare.net", "americanexpress.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#006fcf", "American Express", inner, "American Express Company. Copyright 2025"),
    ))


def gen_capital_one():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Security notification</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">We detected a sign-in to your Capital One account from an unrecognized device. Please verify your identity to secure your account.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Date:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">September 14, 2025</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Device:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">Android - Chrome</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Location:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px">Unknown - Shanghai, China</td></tr>
</table>
""" + _cta_button("https://capitalone-security.com/verify?user=customer", "Verify identity", "#004977")
    return _write("phish_capital_one.eml", _build(
        "phish_capital_one.eml",
        '"Capital One" <alerts@capitalone.com>', "customer@gmail.com",
        "Account security notification - action required",
        _ts(1, 13, 15), "c1-alert-B8C0D2",
        [_received("smtp.capitalone.com", "216.239.120.248", "mx.mail.cloudflare.net", _ts(1, 13, 14)),
         _dkim("capitalone.com", "default"), _auth("mx.mail.cloudflare.net", "capitalone.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#004977", "Capital One", inner, "Capital One Bank (USA), N.A. Member FDIC"),
    ))


# ─── SHIPPING / DELIVERY ─────────────────────────────────────────────────────

def gen_fedex_customs():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Customs fee required</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your package <strong>794644790566</strong> is being held at customs. A clearance fee of <strong>$47.80</strong> is required before delivery can proceed.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Tracking:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">794644790566</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Origin:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">Shenzhen, China</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>HELD AT CUSTOMS</strong></td></tr>
</table>
""" + _cta_button("https://fedex-delivery-notice.com/pay?track=794644790566", "Pay customs fee", "#4d148c") + """
<p style="color:#666666;font-size:12px;line-height:1.5">Failure to pay within 5 business days will result in the package being returned to sender.</p>"""
    return _write("phish_fedex_customs.eml", _build(
        "phish_fedex_customs.eml",
        '"FedEx" <tracking@fedex.com>', "buyer@gmail.com",
        "FedEx: Customs clearance fee required for your package",
        _ts(0, 15, 30), "fedex-customs-C9D1E3",
        [_received("smtp.fedex.com", "199.204.138.103", "mx.mail.cloudflare.net", _ts(0, 15, 29)),
         _dkim("fedex.com", "default"), _auth("mx.mail.cloudflare.net", "fedex.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#4d148c", "FedEx", inner, "FedEx. 942 South Shady Grove Road, Memphis, TN 38120"),
    ))


def gen_usps_delivery():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Delivery attempted</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">We attempted to deliver your package on September 14, but no one was available to receive it.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Tracking:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">9400111899223344556677</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px">Delivery Attempted</td></tr>
</table>
""" + _cta_button("https://usps-delivery-update.com/redeliver?track=9400111899223344556677", "Schedule redelivery", "#333366") + """
<p style="color:#666666;font-size:12px;line-height:1.5">Package will be held at your local post office for 15 days.</p>"""
    return _write("phish_usps_delivery.eml", _build(
        "phish_usps_delivery.eml",
        '"USPS" <noreply@usps.com>', "recipient@yahoo.com",
        "USPS: Your package could not be delivered",
        _ts(0, 9, 11), "usps-del-D0E2F4",
        [_received("smtp.usps.com", "156.33.211.5", "mx.mail.cloudflare.net", _ts(0, 9, 10)),
         _dkim("usps.com", "default"), _auth("mx.mail.cloudflare.net", "usps.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#333366", "USPS", inner, "United States Postal Service. 475 L'Enfant Plaza SW, Washington, DC 20260"),
    ))


def gen_dhl_address():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Address verification required</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your shipment <strong>1234567890</strong> is on hold. The address provided appears to be incomplete or incorrect.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Shipment:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">1234567890</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>ON HOLD</strong></td></tr>
</table>
""" + _cta_button("https://dhl-shipment-track.com/verify?track=1234567890", "Verify address", "#d40511")
    return _write("phish_dhl_address.eml", _build(
        "phish_dhl_address.eml",
        '"DHL Express" <noreply@dhl.com>', "customer@fastmail.com",
        "DHL: Shipment held - address verification needed",
        _ts(1, 13, 22), "dhl-addr-E1F3G5",
        [_received("smtp.dhl.com", "195.191.218.42", "mx.mail.cloudflare.net", _ts(1, 13, 21)),
         _dkim("dhl.com", "default"), _auth("mx.mail.cloudflare.net", "dhl.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#ffcc00", "DHL", inner, "DHL Express. Bonn, Germany", bg_color="#ffffff"),
    ))


def gen_ups_hold():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Package on hold</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your package is currently on hold at our distribution center. An incorrect address was provided.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Tracking:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">1Z999AA10123456784</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>ON HOLD - Address Issue</strong></td></tr>
</table>
""" + _cta_button("https://ups-package-notice.com/update?track=1Z999AA10123456784", "Update address", "#351c15") + """
<p style="color:#666666;font-size:12px;line-height:1.5">Package will be returned to sender after 5 business days.</p>"""
    return _write("phish_ups_hold.eml", _build(
        "phish_ups_hold.eml",
        '"UPS" <notifications@ups.com>', "buyer@outlook.com",
        "UPS: Your package is on hold - action required",
        _ts(0, 8, 55), "ups-hold-F2G4H6",
        [_received("smtp.ups.com", "153.31.118.130", "mx.mail.cloudflare.net", _ts(0, 8, 54)),
         _dkim("ups.com", "default"), _auth("mx.mail.cloudflare.net", "ups.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#351c15", "UPS", inner, "United Parcel Service of America, Inc."),
    ))


def gen_amazon_delivery():
    inner = """<h2 style="color:#0f1111;font-size:18px;margin-top:0">Your delivery needs attention</h2>
<p style="color:#565959;font-size:14px;line-height:1.6">Hello,</p>
<p style="color:#565959;font-size:14px;line-height:1.6">There is a problem with your recent delivery. We need you to verify your address to proceed.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#565959;font-size:14px;border-bottom:1px solid #eee"><strong>Order:</strong></td><td style="padding:8px 12px;color:#0f1111;font-size:14px;border-bottom:1px solid #eee">113-4882764-3847263</td></tr>
<tr><td style="padding:8px 12px;color:#565959;font-size:14px;border-bottom:1px solid #eee"><strong>Item:</strong></td><td style="padding:8px 12px;color:#0f1111;font-size:14px;border-bottom:1px solid #eee">Logitech MX Master 3S</td></tr>
<tr><td style="padding:8px 12px;color:#565959;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>Delivery issue</strong></td></tr>
</table>
""" + _cta_button("https://amazon-order-verify.com/delivery?order=113-4882764", "Fix delivery address", "#ff9900")
    return _write("phish_amazon_delivery.eml", _build(
        "phish_amazon_delivery.eml",
        '"Amazon" <shipment-tracking@amazon.com>', "buyer@gmail.com",
        "Amazon: Your delivery needs attention",
        _ts(0, 10, 30), "amz-del-G3H5I7",
        [_received("amazonses.com", "54.240.8.54", "mx.mail.cloudflare.net", _ts(0, 10, 29)),
         _dkim("amazon.com", "default"), _auth("mx.mail.cloudflare.net", "amazon.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#232f3e", "amazon", inner, "Amazon.com, Inc. 410 Terry Avenue North, Seattle, WA 98109", bg_color="#ffffff"),
    ))


def gen_ups_pickup():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Package ready for pickup</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your package is ready for pickup at your local UPS Store. Please bring a valid government-issued photo ID.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Tracking:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">1Z999AA10123456799</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Location:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">UPS Store #427, 123 Main St</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Hold until:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px">September 22, 2025</td></tr>
</table>
""" + _cta_button("https://ups-package-notice.com/pickup?track=1Z999AA10123456799", "Get directions", "#351c15")
    return _write("phish_ups_pickup.eml", _build(
        "phish_ups_pickup.eml",
        '"UPS Store" <noreply@theupsstore.com>', "customer@gmail.com",
        "Your package is ready for pickup - ID required",
        _ts(1, 11, 0), "ups-pick-H4I6J8",
        [_received("smtp.ups.com", "153.31.118.131", "mx.mail.cloudflare.net", _ts(1, 10, 59)),
         _dkim("theupsstore.com", "default"), _auth("mx.mail.cloudflare.net", "theupsstore.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#351c15", "UPS Store", inner, "United Parcel Service of America, Inc."),
    ))


# ─── SUBSCRIPTION / SERVICE ───────────────────────────────────────────────────

def gen_netflix_payment():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Payment failed</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Hi John,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">We could not process your payment for your Netflix subscription. Update your payment method to avoid service interruption.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Account:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">john.smith@gmail.com</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Plan:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">Standard - $15.49/mo</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>Payment failed</strong></td></tr>
</table>
""" + _cta_button("https://netflix-billing-service.com/update?acct=john.smith", "Update payment", "#e50914") + """
<p style="color:#666666;font-size:12px;line-height:1.5">If you do not update within 7 days, your account will be suspended.</p>"""
    return _write("phish_netflix_payment.eml", _build(
        "phish_netflix_payment.eml",
        '"Netflix" <info@netflix.com>', "john.smith@gmail.com",
        "Your Netflix payment did not go through",
        _ts(0, 8, 0), "nflx-pay-I5J7K9",
        [_received("smtp.netflix.com", "198.51.100.42", "mx.mail.cloudflare.net", _ts(0, 7, 59)),
         _dkim("netflix.com", "default"), _auth("mx.mail.cloudflare.net", "netflix.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#000000", "NETFLIX", inner, "Netflix, Inc. 100 Winchester Circle, Los Gatos, CA 95032", bg_color="#ffffff"),
    ))


def gen_spotify_renewal():
    inner = """<h2 style="color:#191414;font-size:18px;margin-top:0">Subscription renewal failed</h2>
<p style="color:#535353;font-size:14px;line-height:1.6">Hi,</p>
<p style="color:#535353;font-size:14px;line-height:1.6">Your Spotify Premium subscription payment of <strong>$9.99</strong> failed. Your account will revert to free tier in 24 hours.</p>
<div style="background:#f8f8f8;border-radius:8px;padding:16px;margin:16px 0">
<table style="width:100%;font-size:14px">
<tr><td style="padding:4px 0;color:#535353">Plan:</td><td style="padding:4px 0;color:#191414;text-align:right">Premium Individual</td></tr>
<tr><td style="padding:4px 0;color:#535353">Amount:</td><td style="padding:4px 0;color:#191414;text-align:right">$9.99/mo</td></tr>
<tr><td style="padding:4px 0;color:#535353">Status:</td><td style="padding:4px 0;color:#e22134;text-align:right">Failed</td></tr>
</table>
</div>
""" + _cta_button("https://spotify-premium-renew.com/update?user=user123", "Update payment", "#1db954")
    return _write("phish_spotify_renewal.eml", _build(
        "phish_spotify_renewal.eml",
        '"Spotify" <no-reply@spotify.com>', "user@gmail.com",
        "Your Spotify Premium subscription renewal failed",
        _ts(0, 11, 22), "spotify-renew-J6K8L0",
        [_received("smtp.spotify.com", "198.51.100.43", "mx.mail.cloudflare.net", _ts(0, 11, 21)),
         _dkim("spotify.com", "default"), _auth("mx.mail.cloudflare.net", "spotify.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#1db954", "Spotify", inner, "Spotify AB. Regeringsgatan 19, 111 53 Stockholm, Sweden"),
    ))


def gen_adobe_expires():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Subscription expiring today</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Designer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your Adobe Creative Cloud subscription expires <strong>today</strong>. All your apps will be deactivated.</p>
<div style="background:#f8f8f8;border-radius:8px;padding:16px;margin:16px 0">
<table style="width:100%;font-size:14px">
<tr><td style="padding:4px 0;color:#666666">Plan:</td><td style="padding:4px 0;color:#333333;text-align:right">All Apps - $54.99/mo</td></tr>
<tr><td style="padding:4px 0;color:#666666">Expires:</td><td style="padding:4px 0;color:#333333;text-align:right">September 15, 2025</td></tr>
</table>
</div>
""" + _cta_button("https://adobe-billing-service.com/renew?user=designer", "Renew subscription", "#ff0000")
    return _write("phish_adobe_expires.eml", _build(
        "phish_adobe_expires.eml",
        '"Adobe" <billing@adobe.com>', "designer@company.com",
        "Your Adobe Creative Cloud subscription expires today",
        _ts(0, 9, 55), "adobe-exp-K7L9M1",
        [_received("smtp.adobe.com", "198.51.100.44", "mx.mail.cloudflare.net", _ts(0, 9, 54)),
         _dkim("adobe.com", "default"), _auth("mx.mail.cloudflare.net", "adobe.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#ff0000", "Adobe Creative Cloud", inner, "Adobe Inc. 345 Park Avenue, San Jose, CA 95110"),
    ))


def gen_ms365_past_due():
    inner = """<h2 style="color:#323130;font-size:18px;margin-top:0">Subscription past due</h2>
<p style="color:#605e5c;font-size:14px;line-height:1.6">Hi Admin,</p>
<p style="color:#605e5c;font-size:14px;line-height:1.6">Your Microsoft 365 Business Standard subscription is past due. Update your payment method to avoid service suspension.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px;border-bottom:1px solid #edebe9"><strong>Plan:</strong></td><td style="padding:8px 12px;color:#323130;font-size:14px;border-bottom:1px solid #edebe9">Microsoft 365 Business Standard</td></tr>
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px;border-bottom:1px solid #edebe9"><strong>Amount:</strong></td><td style="padding:8px 12px;color:#323130;font-size:14px;border-bottom:1px solid #edebe9">$12.50/user/mo</td></tr>
<tr><td style="padding:8px 12px;color:#605e5c;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>Past due</strong></td></tr>
</table>
""" + _cta_button("https://account-microsoft.com/billing/update?tenant=contoso", "Update payment", "#0078d4")
    return _write("phish_ms365_pastdue.eml", _build(
        "phish_ms365_pastdue.eml",
        '"Microsoft 365" <noreply@microsoft.com>', "admin@contoso.com",
        "Your Microsoft 365 subscription is past due",
        _ts(1, 10, 22), "ms365-due-L8M0N2",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "40.97.164.131", "mail-sor-f45.acdf1d-kopilot.com", _ts(1, 10, 21)),
         _dkim("microsoft.com", "selector1"), _auth("mail-sor-f45.acdf1d-kopilot.com", "microsoft.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0078d4", "Microsoft 365", inner, "Microsoft Corporation, One Microsoft Way, Redmond, WA 98052"),
    ))


def gen_icloud_storage():
    inner = """<h2 style="color:#1d1d1f;font-size:18px;margin-top:0;text-align:center">Storage full</h2>
<p style="color:#1d1d1f;font-size:14px;line-height:1.6;text-align:center">Hi John,</p>
<p style="color:#1d1d1f;font-size:14px;line-height:1.6;text-align:center">Your iCloud storage has reached <strong>5GB of 5GB</strong>. Photos, documents, and backups can no longer sync.</p>
<div style="background:#f5f5f7;border-radius:12px;padding:20px;margin:20px 0;text-align:center">
<p style="color:#1d1d1f;font-size:14px;margin:0">Upgrade to iCloud+ for more storage and premium features.</p>
</div>
""" + _cta_button("https://apple-id-verify.com/icloud/upgrade?user=john", "Upgrade to iCloud+", "#0071e3")
    return _write("phish_icloud_storage.eml", _build(
        "phish_icloud_storage.eml",
        '"iCloud" <no-reply@apple.com>', "john@icloud.com",
        "iCloud storage full - upgrade to iCloud+",
        _ts(0, 12, 0), "icloud-full-M9N1O3",
        [_received("smtp.mail.outlook.com", "40.92.22.164", "mx.mail.cloudflare.net", _ts(0, 11, 59)),
         _dkim("apple.com", "sig1"), _auth("mx.mail.cloudflare.net", "apple.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#000000", "iCloud", inner, "Apple Inc. One Apple Park Way, Cupertino, CA 95014"),
    ))


def gen_norton_expired():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Subscription expired</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear User,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your Norton 360 subscription has <strong>expired</strong>. Your PC is now <strong>unprotected</strong>.</p>
<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#856404;font-size:14px;margin:0"><strong>Warning:</strong> 3 threats detected on your device</p>
<ul style="color:#856404;font-size:14px;margin:8px 0 0;padding-left:20px">
<li>Trojan.GenericKD.48267291</li>
<li>Adware.BrowserModifier</li>
<li>TrackingCookie</li>
</ul>
</div>
""" + _cta_button("https://norton-renewal-service.com/renew?user=user123", "Renew protection", "#ffd700")
    return _write("phish_norton_expired.eml", _build(
        "phish_norton_expired.eml",
        '"Norton" <support@norton.com>', "user@outlook.com",
        "Your Norton subscription has expired - PC unprotected",
        _ts(1, 14, 11), "norton-exp-N0O2P4",
        [_received("smtp.norton.com", "198.51.100.45", "mx.mail.cloudflare.net", _ts(1, 14, 10)),
         _dkim("norton.com", "default"), _auth("mx.mail.cloudflare.net", "norton.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#ffd700", "Norton", inner, "NortonLifeLock Inc. 60 E. Rio Salado Pkwy, Tempe, AZ 85281"),
    ))


def gen_mcafee_expired():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Your device is at risk</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear User,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your McAfee Total Protection subscription expired on September 1. Your device is <strong>no longer protected</strong>.</p>
<div style="background:#f8d7da;border:1px solid #f5c6cb;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#721c24;font-size:14px;margin:0"><strong>5 threats detected on your device!</strong></p>
</div>
""" + _cta_button("https://mcafee-renew-service.com/renew?user=user123", "Renew now", "#c41200")
    return _write("phish_mcafee_expired.eml", _build(
        "phish_mcafee_expired.eml",
        '"McAfee" <alerts@mcafee.com>', "user@gmail.com",
        "McAfee: Your PC is at risk - subscription expired",
        _ts(0, 7, 44), "mcafee-exp-O1P3Q5",
        [_received("smtp.mcafee.com", "198.51.100.46", "mx.mail.cloudflare.net", _ts(0, 7, 43)),
         _dkim("mcafee.com", "default"), _auth("mx.mail.cloudflare.net", "mcafee.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#c41200", "McAfee", inner, "McAfee, LLC. 2255 1st Ave S, Seattle, WA 98134"),
    ))


def gen_dropbox_storage():
    inner = """<h2 style="color:#1e1919;font-size:18px;margin-top:0">Storage limit reached</h2>
<p style="color:#637282;font-size:14px;line-height:1.6">Hi,</p>
<p style="color:#637282;font-size:14px;line-height:1.6">Your Dropbox storage has reached its limit. You will not be able to upload new files until you free up space or upgrade.</p>
<div style="background:#f5f7fa;border-radius:8px;padding:16px;margin:16px 0">
<table style="width:100%;font-size:14px">
<tr><td style="padding:4px 0;color:#637282">Used:</td><td style="padding:4px 0;color:#1e1919;text-align:right">2.0 GB / 2.0 GB</td></tr>
</table>
</div>
""" + _cta_button("https://dropbox-file-share.com/upgrade?user=user123", "Upgrade storage", "#0061ff")
    return _write("phish_dropbox_storage.eml", _build(
        "phish_dropbox_storage.eml",
        '"Dropbox" <no-reply@dropbox.com>', "user@company.com",
        "Your Dropbox storage limit has been reached",
        _ts(1, 8, 30), "db-full-P2Q4R6",
        [_received("smtp.dropbox.com", "162.125.66.4", "mx.mail.cloudflare.net", _ts(1, 8, 29)),
         _dkim("dropbox.com", "default"), _auth("mx.mail.cloudflare.net", "dropbox.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0061ff", "Dropbox", inner, "Dropbox, Inc. 1800 Owens St, San Francisco, CA 94158"),
    ))


# ─── SOCIAL MEDIA ─────────────────────────────────────────────────────────────

def gen_instagram_badge():
    inner = """<h2 style="color:#262626;font-size:18px;margin-top:0;text-align:center">Get your verified badge</h2>
<p style="color:#8e8e8e;font-size:14px;line-height:1.6;text-align:center">Your account has been selected for a <strong>blue verification badge</strong>. This is a limited-time offer.</p>
""" + _cta_button("https://instagram-account-verify.com/badge?user=user123", "Apply for badge", "#0095f6") + """
<p style="color:#8e8e8e;font-size:12px;text-align:center;line-height:1.5">This offer expires in 24 hours.</p>"""
    return _write("phish_instagram_badge.eml", _build(
        "phish_instagram_badge.eml",
        '"Instagram" <no-reply@instagram.com>', "user@gmail.com",
        "Get your verified badge on Instagram - apply now",
        _ts(0, 12, 44), "ig-badge-Q3R5S7",
        [_received("smtp.facebookmail.com", "157.240.22.43", "mx.mail.cloudflare.net", _ts(0, 12, 43)),
         _dkim("instagram.com", "proton"), _auth("mx.mail.cloudflare.net", "instagram.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)", "Instagram", inner, "Instagram, 1 Hacker Way, Menlo Park, CA 94025"),
    ))


def gen_facebook_hacked():
    inner = """<h2 style="color:#1c1e21;font-size:18px;margin-top:0">Account security alert</h2>
<p style="color:#606770;font-size:14px;line-height:1.6">Hello,</p>
<p style="color:#606770;font-size:14px;line-height:1.6">We detected a login from a device we do not recognize in <strong>Moscow, Russia</strong>.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#606770;font-size:14px;border-bottom:1px solid #ddd"><strong>Device:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px;border-bottom:1px solid #ddd">Chrome on Windows</td></tr>
<tr><td style="padding:8px 12px;color:#606770;font-size:14px;border-bottom:1px solid #ddd"><strong>Time:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px;border-bottom:1px solid #ddd">Sep 14, 2025 4:33 AM</td></tr>
<tr><td style="padding:8px 12px;color:#606770;font-size:14px"><strong>Location:</strong></td><td style="padding:8px 12px;color:#1c1e21;font-size:14px">Moscow, Russia</td></tr>
</table>
""" + _cta_button("https://facebook-security-alert.com/secure?id=user123", "Secure account", "#1877f2")
    return _write("phish_facebook_hacked.eml", _build(
        "phish_facebook_hacked.eml",
        '"Facebook" <security@facebookmail.com>', "user@outlook.com",
        "Someone may have accessed your Facebook account",
        _ts(1, 9, 33), "fb-hack-R4S6T8",
        [_received("smtp.facebookmail.com", "157.240.22.44", "mx.mail.cloudflare.net", _ts(1, 9, 32)),
         _dkim("facebookmail.com", "proton"), _auth("mx.mail.cloudflare.net", "facebookmail.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#1877f2", "facebook", inner, "Meta Platforms, Inc. 1 Hacker Way, Menlo Park, CA 94025"),
    ))


def gen_twitter_locked():
    inner = """<h2 style="color:#0f1419;font-size:18px;margin-top:0;text-align:center">Account locked</h2>
<p style="color:#536471;font-size:14px;line-height:1.6;text-align:center">Your X account has been <strong>locked</strong> due to suspicious activity. We detected automated behavior that violates our terms.</p>
""" + _cta_button("https://x-account-verify.com/unlock?id=user123", "Unlock account", "#000000")
    return _write("phish_twitter_locked.eml", _build(
        "phish_twitter_locked.eml",
        '"X" <notify@x.com>', "user@gmail.com",
        "Your X account has been locked",
        _ts(0, 16, 22), "tw-lock-S5T7U9",
        [_received("smtp.x.com", "198.51.100.47", "mx.mail.cloudflare.net", _ts(0, 16, 21)),
         _dkim("x.com", "default"), _auth("mx.mail.cloudflare.net", "x.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#000000", "X", inner, "X Corp. 1355 Market Street, Suite 900, San Francisco, CA 94103"),
    ))


def gen_linkedin_premium():
    inner = """<h2 style="color:#000000e6;font-size:18px;margin-top:0;text-align:center">Exclusive Premium offer</h2>
<p style="color:#00000099;font-size:14px;line-height:1.6;text-align:center">Dear Professional,</p>
<p style="color:#00000099;font-size:14px;line-height:1.6;text-align:center">You have been selected for an exclusive offer: <strong>3 months of LinkedIn Premium absolutely free</strong>.</p>
""" + _cta_button("https://linkedin-account-alert.com/premium?user=professional", "Claim free Premium", "#0077b5") + """
<p style="color:#00000099;font-size:12px;text-align:center;line-height:1.5">This offer expires in 24 hours.</p>"""
    return _write("phish_linkedin_premium.eml", _build(
        "phish_linkedin_premium.eml",
        '"LinkedIn Premium" <notifications@linkedin.com>', "professional@company.com",
        "Exclusive offer: 3 months of LinkedIn Premium free",
        _ts(1, 8, 11), "li-prem-T6U8V0",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "216.243.31.202", "mx.mail.cloudflare.net", _ts(1, 8, 10)),
         _dkim("linkedin.com", "default"), _auth("mx.mail.cloudflare.net", "linkedin.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0077b5", "LinkedIn", inner, "LinkedIn Corporation, 2029 Stierlin Ct, Mountain View, CA 94043"),
    ))


def gen_tiktok_creator():
    inner = """<h2 style="color:#0f0f0f;font-size:18px;margin-top:0;text-align:center">Creator Fund invitation</h2>
<p style="color:#161823;font-size:14px;line-height:1.6;text-align:center">Congratulations!</p>
<p style="color:#161823;font-size:14px;line-height:1.6;text-align:center">Your account has been selected for the <strong>TikTok Creator Fund</strong>. You can earn up to <strong>$10,000/month</strong> based on your video views.</p>
""" + _cta_button("https://tiktok-creator-verify.com/join?id=user123", "Join Creator Fund", "#fe2c55")
    return _write("phish_tiktok_creator.eml", _build(
        "phish_tiktok_creator.eml",
        '"TikTok Creator Fund" <creator@tiktok.com>', "creator@gmail.com",
        "You have been selected for the TikTok Creator Fund",
        _ts(0, 10, 33), "tt-fund-U7V9W1",
        [_received("smtp.tiktok.com", "198.51.100.48", "mx.mail.cloudflare.net", _ts(0, 10, 32)),
         _dkim("tiktok.com", "default"), _auth("mx.mail.cloudflare.net", "tiktok.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#000000", "TikTok", inner, "TikTok Inc. 5800 Bristol Parkway, Suite 100, Culver City, CA 90230"),
    ))


def gen_youtube_copyright():
    inner = """<h2 style="color:#606060;font-size:18px;margin-top:0;text-align:center">Copyright strike</h2>
<p style="color:#606060;font-size:14px;line-height:1.6;text-align:center">Your channel has received a <strong>copyright strike</strong>. Your uploaded video "Product Review 2025" has been removed due to a copyright claim by Music Corp International.</p>
<div style="background:#f8f8f8;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#606060;font-size:14px;margin:0"><strong>Video:</strong> Product Review 2025</p>
<p style="color:#606060;font-size:14px;margin:4px 0 0"><strong>Claimant:</strong> Music Corp International</p>
<p style="color:#606060;font-size:14px;margin:4px 0 0"><strong>Strikes:</strong> 1 of 3</p>
</div>
""" + _cta_button("https://youtube-account-verify.com/resolve?channel=user123", "File a counter-notification", "#ff0000") + """
<p style="color:#606060;font-size:12px;text-align:center;line-height:1.5">If you believe this is a mistake, you can file a counter-notification within 30 days.</p>"""
    return _write("phish_youtube_copyright.eml", _build(
        "phish_youtube_copyright.eml",
        '"YouTube" <copyright@youtube.com>', "creator@gmail.com",
        "Copyright strike on your YouTube channel",
        _ts(1, 15, 0), "yt-copyright-V8W0X2",
        [_received("smtp.youtube.com", "198.51.100.49", "mx.mail.cloudflare.net", _ts(1, 14, 59)),
         _dkim("youtube.com", "default"), _auth("mx.mail.cloudflare.net", "youtube.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#ff0000", "YouTube", inner, "YouTube, LLC 901 Cherry Ave, San Bruno, CA 94066"),
    ))


# ─── DOCUMENT SHARING / SAAS ─────────────────────────────────────────────────

def gen_docusign_sign():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Please sign: Acquisition Agreement</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Legal Department,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">You are requested to sign:</p>
<div style="background:#f8f8f8;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#333333;font-size:14px;margin:0"><strong>Meridian Corp Acquisition Agreement</strong></p>
<p style="color:#666666;font-size:14px;margin:4px 0 0">Sent by: David Chen (CEO)</p>
</div>
""" + _cta_button("https://docusign-esign-portal.com/sign?env=meridian-445566", "Review & Sign", "#4c00ff")
    return _write("phish_docusign_sign.eml", _build(
        "phish_docusign_sign.eml",
        '"DocuSign" <noreply@docusign.com>', "legal@company.com",
        "DocuSign: Please sign - Meridian Corp Acquisition Agreement",
        _ts(0, 9, 44), "docusign-meridian-Y9X1Z3",
        [_received("smtp.docusign.com", "198.51.100.50", "mx.mail.cloudflare.net", _ts(0, 9, 43)),
         _dkim("docusign.com", "default"), _auth("mx.mail.cloudflare.net", "docusign.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#4c00ff", "DocuSign", inner, "DocuSign, Inc. 221 Main Street, San Francisco, CA 94105"),
    ))


def gen_sharepoint_doc():
    inner = """<h2 style="color:#323130;font-size:18px;margin-top:0">Document shared with you</h2>
<p style="color:#605e5c;font-size:14px;line-height:1.6"><strong>David Chen (CEO)</strong> shared a document:</p>
<div style="background:#f3f2f1;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#323130;font-size:14px;margin:0"><strong>Q4 Layoff Plan - Confidential</strong></p>
<p style="color:#605e5c;font-size:14px;margin:4px 0 0">Excel Online</p>
</div>
""" + _cta_button("https://sharepoint-docs-view.com/open?doc=layoff-q4&token=778899", "Open document", "#0078d4")
    return _write("phish_sharepoint_doc.eml", _build(
        "phish_sharepoint_doc.eml",
        '"SharePoint" <no-reply@sharepoint.com>', "cfo@company.com",
        "Your CEO shared 'Q4 Layoff Plan - Confidential' with you",
        _ts(0, 7, 44), "sp-layoff-Z1A3B5",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "40.97.164.132", "mail-sor-f45.acdf1d-kopilot.com", _ts(0, 7, 43)),
         _dkim("sharepoint.com", "default"), _auth("mail-sor-f45.acdf1d-kopilot.com", "sharepoint.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0078d4", "SharePoint", inner, "Microsoft Corporation, One Microsoft Way, Redmond, WA 98052"),
    ))


def gen_dropbox_shared():
    inner = """<h2 style="color:#1e1919;font-size:18px;margin-top:0">File shared with you</h2>
<p style="color:#637282;font-size:14px;line-height:1.6"><strong>Sarah Mitchell</strong> shared a file with you:</p>
<div style="background:#f5f7fa;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#1e1919;font-size:14px;margin:0"><strong>Budget_2026_Final.xlsx</strong></p>
<p style="color:#637282;font-size:14px;margin:4px 0 0">Microsoft Excel · 2.4 MB</p>
</div>
""" + _cta_button("https://dropbox-file-share.com/open?file=budget-2026&token=112233", "Open file", "#0061ff")
    return _write("phish_dropbox_shared.eml", _build(
        "phish_dropbox_shared.eml",
        '"Dropbox" <no-reply@dropbox.com>', "finance@company.com",
        '"Budget_2026_Final.xlsx" was shared with you via Dropbox',
        _ts(1, 14, 11), "dropbox-budget-A2B4C6",
        [_received("smtp.dropbox.com", "162.125.66.5", "mx.mail.cloudflare.net", _ts(1, 14, 10)),
         _dkim("dropbox.com", "default"), _auth("mx.mail.cloudflare.net", "dropbox.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0061ff", "Dropbox", inner, "Dropbox, Inc. 1800 Owens St, San Francisco, CA 94158"),
    ))


def gen_google_docs():
    inner = """<h2 style="color:#202124;font-size:18px;margin-top:0">Document shared with you</h2>
<p style="color:#5f6368;font-size:14px;line-height:1.6"><strong>Sarah Mitchell</strong> shared a document with you:</p>
<div style="background:#f8f9fa;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#202124;font-size:14px;margin:0"><strong>Q3 OKR Tracking - Updated</strong></p>
<p style="color:#5f6368;font-size:14px;margin:4px 0 0">Google Docs</p>
</div>
""" + _cta_button("https://account-google.com/docs/open?doc=okr-q3&token=445566", "Open in Docs", "#1a73e8")
    return _write("phish_google_docs.eml", _build(
        "phish_google_docs.eml",
        '"Google Docs" <drive-shares-noreply@google.com>', "team@company.com",
        "Sarah Mitchell shared 'Q3 OKR Tracking - Updated' with you",
        _ts(0, 8, 55), "google-docs-okr-D7E9F1",
        [_received("smtp.gmail.com", "209.85.220.43", "mx.google.com", _ts(0, 8, 54)),
         _dkim("google.com", "google"), _auth("mx.google.com", "google.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#1a73e8", "Google Docs", inner, "Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043"),
    ))


def gen_confluence_page():
    inner = """<h2 style="color:#172b4d;font-size:18px;margin-top:0">New wiki page</h2>
<p style="color:#6b778c;font-size:14px;line-height:1.6"><strong>Sarah Mitchell</strong> created a new page:</p>
<div style="background:#f4f5f7;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#172b4d;font-size:14px;margin:0"><strong>API Authentication Guide</strong></p>
<p style="color:#6b778c;font-size:14px;margin:4px 0 0">This guide covers JWT authentication, role-based access control, and API key management.</p>
</div>
""" + _cta_button("https://atlassian-wiki-verify.com/review?page=api-auth-guide", "View page", "#0052cc")
    return _write("phish_confluence_page.eml", _build(
        "phish_confluence_page.eml",
        '"Confluence" <confluence@atlassian.net>', "developer@company.com",
        "[Confluence] New page created: API Authentication Guide",
        _ts(1, 10, 11), "confluence-auth-E2F4G6",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "104.192.200.42", "mail-sor-f45.acdf1d-kopilot.com", _ts(1, 10, 10)),
         _dkim("atlassian.net", "default"), _auth("mail-sor-f45.acdf1d-kopilot.com", "atlassian.net"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0052cc", "Confluence", inner, "Atlassian Pty Ltd. Level 6, 350 George Street, Sydney NSW 2000"),
    ))


def gen_jira_ticket():
    inner = """<h2 style="color:#0052cc;font-size:18px;margin-top:0">Ticket assigned to you</h2>
<div style="background:#f4f5f7;border-radius:8px;padding:16px;margin:16px 0">
<p style="color:#172b4d;font-size:14px;margin:0"><strong>SENTINEL-1234</strong> assigned to you</p>
<p style="color:#172b4d;font-size:14px;margin:4px 0 0"><strong>Authentication middleware fix</strong></p>
<p style="color:#6b778c;font-size:14px;margin:4px 0 0">Priority: High | Status: To Do | Sprint: 24</p>
</div>
""" + _cta_button("https://atlassian-ticket-verify.com/view?ticket=SENTIN-1234", "View ticket", "#0052cc")
    return _write("phish_jira_ticket.eml", _build(
        "phish_jira_ticket.eml",
        '"Jira" <jira@atlassian.net>', "developer@company.com",
        "[SENTINEL-1234] Authentication middleware fix - assigned to you",
        _ts(0, 9, 11), "jira-1234-F3G5H7",
        [_received("mail-sor-f45.acdf1d-kopilot.com", "104.192.200.43", "mail-sor-f45.acdf1d-kopilot.com", _ts(0, 9, 10)),
         _dkim("atlassian.net", "default"), _auth("mail-sor-f45.acdf1d-kopilot.com", "atlassian.net"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#0052cc", "Jira", inner, "Atlassian Pty Ltd. Level 6, 350 George Street, Sydney NSW 2000"),
    ))


# ─── TAX / GOVERNMENT ────────────────────────────────────────────────────────

def gen_irs_refund():
    inner = """<h2 style="color:#003366;font-size:18px;margin-top:0;text-align:center">Tax Refund Notification</h2>
<p style="color:#333333;font-size:14px;line-height:1.6;text-align:center">Dear Taxpayer,</p>
<p style="color:#333333;font-size:14px;line-height:1.6;text-align:center">After reviewing your 2024 tax return, the IRS has determined you are eligible for a <strong>refund of $3,847.50</strong>.</p>
<div style="background:#f0f4f8;border-radius:8px;padding:16px;margin:16px 0;text-align:center">
<p style="color:#003366;font-size:20px;font-weight:bold;margin:0">$3,847.50</p>
<p style="color:#333333;font-size:14px;margin:4px 0 0">Estimated refund amount</p>
</div>
""" + _cta_button("https://irs-refund-claim.com/claim?id=112233", "Claim refund", "#003366") + """
<p style="color:#c41200;font-size:12px;text-align:center;line-height:1.5"><strong>Warning:</strong> Claims not submitted within 72 hours will be forfeited.</p>"""
    return _write("phish_irs_refund.eml", _build(
        "phish_irs_refund.eml",
        '"IRS Refund Department" <refund@irs.gov>', "taxpayer@outlook.com",
        "You are eligible for a tax refund of $3,847.50",
        _ts(0, 10, 22), "irs-refund-G4H6I8",
        [_received("smtp.irs.gov", "198.51.100.51", "mx.mail.cloudflare.net", _ts(0, 10, 21)),
         _dkim("irs.gov", "default"), _auth("mx.mail.cloudflare.net", "irs.gov"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#003366", "Internal Revenue Service", inner, "Internal Revenue Service. 1111 Constitution Ave NW, Washington, DC 20224"),
    ))


def gen_ssa_benefits():
    inner = """<h2 style="color:#003366;font-size:18px;margin-top:0;text-align:center">Benefits suspension notice</h2>
<p style="color:#333333;font-size:14px;line-height:1.6;text-align:center">Dear Beneficiary,</p>
<p style="color:#333333;font-size:14px;line-height:1.6;text-align:center">Our records indicate that your Social Security number has been <strong>suspended</strong> due to suspicious activity. Your monthly benefits will be discontinued until you verify your identity.</p>
<div style="background:#f0f4f8;border-radius:8px;padding:16px;margin:16px 0;text-align:center">
<p style="color:#333333;font-size:14px;margin:0">SSN on file: ***-**-4521</p>
</div>
""" + _cta_button("https://ssa-gov-verify.com/restore?id=445566", "Verify identity", "#003366")
    return _write("phish_ssa_benefits.eml", _build(
        "phish_ssa_benefits.eml",
        '"Social Security Administration" <alerts@ssa.gov>', "retiree@gmail.com",
        "Your Social Security benefits will be suspended - verify now",
        _ts(1, 7, 55), "ssa-suspend-H5I7J9",
        [_received("smtp.ssa.gov", "198.51.100.52", "mx.mail.cloudflare.net", _ts(1, 7, 54)),
         _dkim("ssa.gov", "default"), _auth("mx.mail.cloudflare.net", "ssa.gov"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#003366", "Social Security Administration", inner, "Social Security Administration. 6401 Security Blvd, Baltimore, MD 21235"),
    ))


def gen_fbi_warrant():
    inner = """<h2 style="color:#003366;font-size:18px;margin-top:0;text-align:center;font-family:Times New Roman">Federal Bureau of Investigation</h2>
<p style="color:#003366;font-size:12px;text-align:center;margin-top:-8px;font-family:Times New Roman">Cyber Division</p>
<div style="border:2px solid #003366;padding:20px;margin:16px 0">
<p style="color:#333333;font-size:14px;margin:0"><strong>CASE NUMBER: FBI-2025-77889</strong></p>
<p style="color:#333333;font-size:14px;margin:8px 0 0">RECIPIENT: target@company.com</p>
<p style="color:#333333;font-size:14px;line-height:1.6;margin-top:12px">This notice is to inform you that a <strong>federal arrest warrant</strong> has been issued in your name in connection with ongoing cybercrime investigations.</p>
<p style="color:#333333;font-size:14px;line-height:1.6"><strong>YOU ARE COMMANDED</strong> to respond within 24 hours via the secure portal:</p>
</div>
""" + _cta_button("https://fbi-gov-verify.com/respond?case=778899", "Access secure portal", "#003366") + """
<p style="color:#c41200;font-size:12px;text-align:center;line-height:1.5"><strong>Failure to respond will result in immediate arrest.</strong></p>"""
    return _write("phish_fbi_warrant.eml", _build(
        "phish_fbi_warrant.eml",
        '"FBI Cyber Division" <cyber@fbi.gov>', "target@company.com",
        "Federal Arrest Warrant Issued - Case #FBI-2025-77889",
        _ts(0, 16, 11), "fbi-warrant-I6J8K0",
        [_received("smtp.fbi.gov", "198.51.100.53", "mx.mail.cloudflare.net", _ts(0, 16, 10)),
         _dkim("fbi.gov", "default"), _auth("mx.mail.cloudflare.net", "fbi.gov"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#003366", "Federal Bureau of Investigation", inner, "FBI. 935 Pennsylvania Avenue NW, Washington, DC 20535"),
    ))


def gen_usps_customs():
    inner = """<h2 style="color:#333333;font-size:18px;margin-top:0">Package intercepted</h2>
<p style="color:#666666;font-size:14px;line-height:1.6">Dear Customer,</p>
<p style="color:#666666;font-size:14px;line-height:1.6">Your package has been intercepted by customs authority. A processing fee of <strong>$29.99</strong> is required for release.</p>
<table style="width:100%;margin:16px 0;border-collapse:collapse">
<tr><td style="padding:8px 12px;color:#666666;font-size:14px;border-bottom:1px solid #eee"><strong>Tracking:</strong></td><td style="padding:8px 12px;color:#333333;font-size:14px;border-bottom:1px solid #eee">9400111899223344557788</td></tr>
<tr><td style="padding:8px 12px;color:#666666;font-size:14px"><strong>Status:</strong></td><td style="padding:8px 12px;color:#c41200;font-size:14px"><strong>HELD BY CUSTOMS</strong></td></tr>
</table>
""" + _cta_button("https://usps-delivery-update.com/release?track=9400111899223344557788", "Pay release fee", "#333366") + """
<p style="color:#666666;font-size:12px;line-height:1.5">Failure to pay within 72 hours will result in the package being destroyed.</p>"""
    return _write("phish_usps_customs.eml", _build(
        "phish_usps_customs.eml",
        '"USPS" <noreply@usps.com>', "recipient@gmail.com",
        "USPS: Package intercepted by customs authority",
        _ts(1, 12, 0), "usps-customs-J7K9L1",
        [_received("smtp.usps.com", "156.33.211.6", "mx.mail.cloudflare.net", _ts(1, 11, 59)),
         _dkim("usps.com", "default"), _auth("mx.mail.cloudflare.net", "usps.com"),
         'Content-Type: text/html; charset="UTF-8"'],
        _html_wrapper("#333366", "USPS", inner, "United States Postal Service. 475 L'Enfant Plaza SW, Washington, DC 20260"),
    ))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

ALL_GENERATORS = [
    # Credential Harvesting (12)
    gen_google_signin, gen_google_password, gen_microsoft_signin, gen_microsoft_verify,
    gen_apple_locked, gen_apple_billing, gen_yahoo_storage, gen_instagram_password,
    gen_facebook_login, gen_linkedin_signin, gen_dropbox_verify, gen_slack_verify,
    # BEC / CEO Fraud (8)
    gen_bec_ceo_wire, gen_bec_cfo_redirect, gen_bec_gift_cards, gen_bec_cfo_urgent,
    gen_bec_vendor_change, gen_bec_vendor_redirect, gen_bec_it_admin, gen_bec_lawyer,
    # Banking / Finance (8)
    gen_chase_fraud, gen_wells_fargo_lock, gen_boa_verify, gen_paypal_limited,
    gen_venmo_request, gen_zelle_receipt, gen_amex_unusual, gen_capital_one,
    # Shipping / Delivery (6)
    gen_fedex_customs, gen_usps_delivery, gen_dhl_address, gen_ups_hold,
    gen_amazon_delivery, gen_ups_pickup,
    # Subscription / Service (8)
    gen_netflix_payment, gen_spotify_renewal, gen_adobe_expires, gen_ms365_past_due,
    gen_icloud_storage, gen_norton_expired, gen_mcafee_expired, gen_dropbox_storage,
    # Social Media (6)
    gen_instagram_badge, gen_facebook_hacked, gen_twitter_locked, gen_linkedin_premium,
    gen_tiktok_creator, gen_youtube_copyright,
    # Document Sharing / SaaS (6)
    gen_docusign_sign, gen_sharepoint_doc, gen_dropbox_shared, gen_google_docs,
    gen_confluence_page, gen_jira_ticket,
    # Tax / Government (4)
    gen_irs_refund, gen_ssa_benefits, gen_fbi_warrant, gen_usps_customs,
]


if __name__ == "__main__":
    files = []
    for gen in ALL_GENERATORS:
        f = gen()
        files.append(f)
    print(f"Generated {len(files)} realistic fixture files")
    for f in sorted(files):
        print(f"  {f}")
