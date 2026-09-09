#!/usr/bin/env python3
"""Generate 50 diverse .eml fixture files for demo."""
import os

OUT = "backend/data/fixtures"
os.makedirs(OUT, exist_ok=True)

FIXTURES = {
    # === CREDENTIAL HARVESTING ===
    "cred_harvest_gmail.html": """From: Google Security <security@google-session-verify.com>
To: victim@gmail.com
Subject: [Security Alert] Unusual sign-in activity detected on your account
Date: Tue, 09 Sep 2025 08:12:33 -0700
Message-ID: <gmail-alert-991122@google-session-verify.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:480px;margin:30px auto">
<div style="background:#4285f4;color:white;padding:15px;text-align:center"><h2 style="margin:0">Google</h2></div>
<div style="padding:20px;border:1px solid #ddd">
<h3>Unusual sign-in activity</h3>
<p>We detected a new sign-in to your Google Account on a Windows device.</p>
<table style="width:100%;margin:10px 0"><tr><td><strong>Device:</strong></td><td>Windows PC</td></tr>
<tr><td><strong>Location:</strong></td><td>Lagos, Nigeria</td></tr>
<tr><td><strong>Time:</strong></td><td>Sep 9, 2025 3:12 AM</td></tr></table>
<p>If this wasn't you, secure your account immediately:</p>
<p style="text-align:center"><a href="https://google-session-verify.com/secure?id=victim@gmail.com" style="background:#4285f4;color:white;padding:10px 20px;text-decoration:none">Secure My Account</a></p>
</div></div></body></html>""",

    "cred_harvest_microsoft.html": """From: Microsoft Security <noreply@microsoft-account safety.com>
To: user@company.org
Subject: Your Microsoft account has been compromised - action required
Date: Wed, 10 Sep 2025 14:22:11 +0000
Message-ID: <ms-compromised-554433@microsoft-account safety.com>
Content-Type: text/html; charset="UTF-8"

<html><body><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0078d4;color:white;padding:15px;text-align:center"><h2 style="margin:0">Microsoft</h2></div>
<div style="padding:20px">
<p>Dear User,</p>
<p>Our systems have detected that your Microsoft account <strong>user@company.org</strong> has been <strong>compromised</strong>.</p>
<p>An unauthorized user has:</p>
<ul><li>Changed your recovery email</li><li>Enabled email forwarding</li><li>Accessed your OneDrive files</li></ul>
<p style="text-align:center"><a href="https://microsoft-account safety.com/recover?u=user@company.org" style="background:#d83b01;color:white;padding:10px 20px;text-decoration:none">Recover Account</a></p>
</div></div></body></html>""",

    "cred_harvest_yahoo.html": """From: Yahoo Mail <alert@yahoo-security-center.com>
To: user@yahoo.com
Subject: Your Yahoo Mail storage is full - verify to continue
Date: Thu, 11 Sep 2025 09:44:22 -0400
Message-ID: <yahoo-full-778899@yahoo-security-center.com>
Content-Type: text/html; charset="UTF-8"

<html><body><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#6001d2;color:white;padding:15px;text-align:center"><h2 style="margin:0">Yahoo Mail</h2></div>
<div style="padding:20px">
<p>Hi User,</p>
<p>Your Yahoo Mail storage has reached <strong>99% capacity</strong>. You will not be able to receive new emails until you verify your account and upgrade your storage.</p>
<p style="text-align:center"><a href="https://yahoo-security-center.com/verify?user=user@yahoo.com" style="background:#6001d2;color:white;padding:10px 20px;text-decoration:none">Verify & Upgrade</a></p>
</div></div></body></html>""",

    # === CEO FRAUD / BEC ===
    "bec_urgency_wire.html": """From: "CFO" <cfo@company-internal-finance.com>
To: ap@company.com
Subject: CONFIDENTIAL - Process this wire before market open
Date: Mon, 08 Sep 2025 06:15:44 -0400
Message-ID: <cfo-wire-112233@company-internal-finance.com>
Content-Type: text/plain; charset="UTF-8"

Team,

I need you to process the following wire transfer before market open today. This is for the Acme acquisition that was announced. Do NOT discuss with anyone outside finance.

Beneficiary: Northstar Capital LLC
Bank: JPMorgan Chase
Routing: 021000021
Account: 7733991155
Amount: $425,000.00
Reference: Q3 Advisory Fee

I am in meetings all morning. Please confirm once done.

Sent from my iPhone""",

    "bec_vendor_change.html": """From: "Robert Chen" <robert.chen@trusted-vendor.net>
To: ap@company.com
Subject: Updated bank details - effective immediately
Date: Tue, 09 Sep 2025 11:33:22 -0400
Message-ID: <vendor-bank-445566@trusted-vendor.net>
Content-Type: text/plain; charset="UTF-8"

Hi AP Team,

Please note that our bank account details have changed due to a recent system migration. Please update your records for all future payments:

NEW DETAILS:
Company: Trusted Vendor Solutions Inc
Bank: Bank of America
Account: 3344556677
Routing: 026009593
SWIFT: BOFAUS3N

Our old Chase account will be closed on September 15. Payments sent after that date will be returned.

Please confirm receipt.

Robert Chen
CFO, Trusted Vendor Solutions""",

    "bec_acct_change_v2.html": """From: "Finance Director" <finance@partner-company-mail.com>
To: payments@company.com
Subject: Re: Invoice payment - new bank details attached
Date: Wed, 10 Sep 2025 08:44:55 +0000
Message-ID: <partner-bank-778899@partner-company-mail.com>
Content-Type: text/plain; charset="UTF-8"

Following up on our call yesterday. Here are the updated payment details:

Company: Partner Industries Ltd
Bank: Wells Fargo
Account Name: Partner Industries Operating
Account: 5566778899
Routing: 121000248

Please redirect the outstanding balance of $87,500 to this account.

Thanks,
Finance Director
Partner Industries""",

    # === TAX / GOVERNMENT SCAMS ===
    "scam_irs_refund.html": """From: "IRS Refund Department" <refund@irs-gov-tax-office.com>
To: taxpayer@outlook.com
Subject: You are eligible for a tax refund of $3,847.50
Date: Mon, 08 Sep 2025 10:22:33 -0400
Message-ID: <irs-refund-112233@irs-gov-tax-office.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:2px solid #003366">
<div style="background:#003366;color:white;padding:15px;text-align:center"><h2 style="margin:0">Internal Revenue Service</h2></div>
<div style="padding:20px">
<p>Dear Taxpayer,</p>
<p>After reviewing your 2024 tax return, the IRS has determined you are eligible for a <strong>refund of $3,847.50</strong>.</p>
<p>To claim your refund, please complete the verification form below:</p>
<p style="text-align:center"><a href="https://irs-gov-tax-office.com/claim?id=112233" style="background:#003366;color:white;padding:10px 20px;text-decoration:none">Claim Refund</a></p>
<p style="color:#c41200"><strong>Warning:</strong> Claims not submitted within 72 hours will be forfeited.</p>
</div></div></body></html>""",

    "scam_ssa_benefits.html": """From: "Social Security Administration" <alerts@ssa-gov-benefits.com>
To: retiree@gmail.com
Subject: Your Social Security benefits will be suspended - verify now
Date: Tue, 09 Sep 2025 07:55:11 -0400
Message-ID: <ssa-suspend-445566@ssa-gov-benefits.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #003366">
<div style="background:#003366;color:white;padding:15px;text-align:center"><h2 style="margin:0">Social Security Administration</h2></div>
<div style="padding:20px">
<p>Dear Beneficiary,</p>
<p>Our records indicate that your Social Security number has been <strong>suspended</strong> due to suspicious activity. Your monthly benefits will be discontinued until you verify your identity.</p>
<p>SSN on file: ***-**-4521</p>
<p style="text-align:center"><a href="https://ssa-gov-benefits.com/verify?id=445566" style="background:#003366;color:white;padding:10px 20px;text-decoration:none">Verify Identity</a></p>
</div></div></body></html>""",

    "scam_fbi_warrant.html": """From: "FBI Cyber Division" <warrant@fbi-gov-legal.com>
To: target@company.com
Subject: Federal Arrest Warrant Issued - Case #FBI-2025-77889
Date: Wed, 10 Sep 2025 16:11:44 -0400
Message-ID: <fbi-warrant-778899@fbi-gov-legal.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Times New Roman"><div style="max-width:550px;margin:0 auto;background:white;border:3px solid #003366">
<div style="background:#003366;color:white;padding:15px;text-align:center"><h2 style="margin:0">Federal Bureau of Investigation</h2><p style="margin:3px 0 0;font-size:12px">Cyber Division</p></div>
<div style="padding:25px">
<p><strong>CASE NUMBER: FBI-2025-77889</strong></p>
<p>RECIPIENT: target@company.com</p>
<p>This notice is to inform you that a <strong>federal arrest warrant</strong> has been issued in your name in connection with ongoing cybercrime investigations. You have been identified through digital forensics as a person of interest.</p>
<p><strong>YOU ARE COMMANDED</strong> to respond within 24 hours via the secure portal below to review the evidence and submit your response:</p>
<p style="text-align:center"><a href="https://fbi-gov-legal.com/respond?case=778899" style="background:#003366;color:white;padding:10px 20px;text-decoration:none;font-weight:bold">Access Secure Portal</a></p>
<p>Failure to respond will result in immediate arrest.</p>
</div></div></body></html>""",

    "scam_dea_drug_charge.html": """From: "DEA Investigations" <case@dea-gov-investigations.com>
To: citizen@outlook.com
Subject: Your DEA case has been filed - respond immediately
Date: Thu, 11 Sep 2025 12:33:55 -0400
Message-ID: <dea-case-334455@dea-gov-investigations.com>
Content-Type: text/plain; charset="UTF-8"

DEA Case Reference: DEA-2025-334455

This is an official notification from the Drug Enforcement Administration. A case has been filed against you in connection with controlled substance violations traced through your financial accounts.

You have 48 hours to respond to this notice and provide documentation of legitimate fund sources.

Respond via: https://dea-gov-investigations.com/respond?case=334455

Failure to respond within the specified timeframe will result in asset seizure proceedings.

Special Agent, DEA""",

    # === SHIPPING / DELIVERY SCAMS ===
    "scam_fedex_customs.html": """From: "FedEx Customs" <customs@fedex-clearance-notice.com>
To: buyer@gmail.com
Subject: FedEx: Customs fee of $47.80 required for your package
Date: Mon, 08 Sep 2025 15:44:22 +0000
Message-ID: <fedex-customs-112233@fedex-clearance-notice.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#4d148c;color:white;padding:15px;text-align:center"><h2 style="margin:0">FedEx</h2></div>
<div style="padding:20px">
<p>Dear Customer,</p>
<p>Your package <strong>794644790566</strong> is being held at customs. A clearance fee of <strong>$47.80</strong> is required before delivery can proceed.</p>
<table style="width:100%;margin:10px 0"><tr><td><strong>Tracking:</strong></td><td>794644790566</td></tr>
<tr><td><strong>Origin:</strong></td><td>Shenzhen, China</td></tr>
<tr><td><strong>Status:</strong></td><td style="color:red"><strong>HELD AT CUSTOMS</strong></td></tr></table>
<p style="text-align:center"><a href="https://fedex-clearance-notice.com/pay?track=794644790566" style="background:#4d148c;color:white;padding:10px 20px;text-decoration:none">Pay Fee</a></p>
</div></div></body></html>""",

    "scam_usps_package.html": """From: "USPS Delivery" <info@usps-package-tracking.com>
To: recipient@yahoo.com
Subject: USPS: Your package could not be delivered - schedule redelivery
Date: Tue, 09 Sep 2025 09:11:33 -0500
Message-ID: <usps-redeliver-445566@usps-package-tracking.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#333366;color:white;padding:15px;text-align:center"><h2 style="margin:0">USPS</h2></div>
<div style="padding:20px">
<p>Dear Customer,</p>
<p>We attempted to deliver your package on September 8, but no one was available to receive it.</p>
<p><strong>Tracking:</strong> 9400111899223344556677</p>
<p><strong>Status:</strong> Delivery Attempted</p>
<p style="text-align:center"><a href="https://usps-package-tracking.com/redeliver?track=9400111899223344556677" style="background:#333366;color:white;padding:10px 20px;text-decoration:none">Schedule Redelivery</a></p>
</div></div></body></html>""",

    "scam_dhl_failed.html": """From: "DHL Express" <tracking@dhl-express-delivery.com>
To: customer@fastmail.com
Subject: DHL: Delivery failed - package returned to sender
Date: Wed, 10 Sep 2025 13:22:44 +0000
Message-ID: <dhl-fail-778899@dhl-express-delivery.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#ffcc00;color:#d40511;padding:15px;text-align:center"><h2 style="margin:0">DHL</h2></div>
<div style="padding:20px">
<p>Dear Customer,</p>
<p>Your shipment <strong>1234567890</strong> could not be delivered. The package will be returned to sender unless you take action within 24 hours.</p>
<p style="text-align:center"><a href="https://dhl-express-delivery.com/reschedule?track=1234567890" style="background:#d40511;color:white;padding:10px 20px;text-decoration:none">Reschedule Delivery</a></p>
</div></div></body></html>""",

    "scam_ups_hold.html": """From: "UPS Service" <notice@ups-delivery-service.com>
To: buyer@outlook.com
Subject: UPS: Your package is on hold - action required
Date: Thu, 11 Sep 2025 08:55:11 -0400
Message-ID: <ups-hold-112233@ups-delivery-service.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#351c15;color:white;padding:15px;text-align:center"><h2 style="margin:0">UPS</h2></div>
<div style="padding:20px">
<p>Dear Customer,</p>
<p>Your package is currently on hold at our distribution center. An incorrect address was provided. Please update your delivery details.</p>
<p><strong>Tracking:</strong> 1Z999AA10123456784</p>
<p style="text-align:center"><a href="https://ups-delivery-service.com/update?track=1Z999AA10123456784" style="background:#351c15;color:white;padding:10px 20px;text-decoration:none">Update Address</a></p>
</div></div></body></html>""",

    # === BANKING / FINANCE SCAMS ===
    "scam_chase_fraud.html": """From: "Chase Bank" <alerts@chase-fraud-alert.com>
To: customer@gmail.com
Subject: [URGENT] Suspicious transaction on your account - verify within 2 hours
Date: Mon, 08 Sep 2025 07:33:22 -0400
Message-ID: <chase-fraud-112233@chase-fraud-alert.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#117aca;color:white;padding:15px;text-align:center"><h2 style="margin:0">Chase</h2></div>
<div style="padding:20px">
<p>Dear Customer,</p>
<p>We detected a <strong>suspicious transaction</strong> on your Chase account ending in <strong>4521</strong>:</p>
<table style="width:100%;margin:10px 0;font-size:13px"><tr><td><strong>Amount:</strong></td><td>$2,847.00</td></tr>
<tr><td><strong>Merchant:</strong></td><td>BestBuy.com</td></tr>
<tr><td><strong>Date:</strong></td><td>Sep 8, 2025 7:15 AM</td></tr>
<tr><td><strong>Status:</strong></td><td style="color:red"><strong>PENDING</strong></td></tr></table>
<p>If you did NOT make this transaction, call immediately:</p>
<p style="text-align:center"><a href="https://chase-fraud-alert.com/dispute?acct=4521&ref=112233" style="background:#117aca;color:white;padding:10px 20px;text-decoration:none">Dispute Transaction</a></p>
</div></div></body></html>""",

    "scam_wells_fargo.html": """From: "Wells Fargo Security" <security@wellsfargo-secure-access.com>
To: user@company.com
Subject: Your Wells Fargo account has been locked - verify identity
Date: Tue, 09 Sep 2025 10:11:44 -0400
Message-ID: <wf-lock-445566@wellsfargo-secure-access.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#d71e28;color:white;padding:15px;text-align:center"><h2 style="margin:0">Wells Fargo</h2></div>
<div style="padding:20px">
<p>Dear Customer,</p>
<p>Your Wells Fargo account has been <strong>temporarily locked</strong> due to multiple failed login attempts from an unrecognized device.</p>
<p style="text-align:center"><a href="https://wellsfargo-secure-access.com/unlock?id=445566" style="background:#d71e28;color:white;padding:10px 20px;text-decoration:none">Unlock Account</a></p>
</div></div></body></html>""",

    "scam_venmo_request.html": """From: "Venmo" <notifications@venmo-payment-request.com>
To: user@gmail.com
Subject: You have a pending payment request of $850.00
Date: Wed, 10 Sep 2025 14:55:33 -0400
Message-ID: <venmo-req-778899@venmo-payment-request.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#3d95ce;color:white;padding:15px;text-align:center"><h2 style="margin:0">Venmo</h2></div>
<div style="padding:20px">
<p>Hello,</p>
<p>You have a pending payment request from <strong>@unknown-user</strong>:</p>
<p><strong>Amount:</strong> $850.00</p>
<p><strong>Note:</strong> "For concert tickets"</p>
<p style="text-align:center"><a href="https://venmo-payment-request.com/pay?req=778899" style="background:#3d95ce;color:white;padding:10px 20px;text-decoration:none">Pay Now</a></p>
</div></div></body></html>""",

    "scam_zelle_payment.html": """From: "Zelle" <alerts@zelle-pay-alert.com>
To: user@aol.com
Subject: Zelle: You received a payment of $1,200.00 - confirm receipt
Date: Thu, 11 Sep 2025 11:22:55 -0400
Message-ID: <zelle-rec-112233@zelle-pay-alert.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#6d1ed4;color:white;padding:15px;text-align:center"><h2 style="margin:0">Zelle</h2></div>
<div style="padding:20px">
<p>Hello,</p>
<p>You have received a Zelle payment of <strong>$1,200.00</strong> from an unknown sender.</p>
<p>To deposit this payment into your bank account, please confirm your account details:</p>
<p style="text-align:center"><a href="https://zelle-pay-alert.com/confirm?pay=112233" style="background:#6d1ed4;color:white;padding:10px 20px;text-decoration:none">Confirm & Deposit</a></p>
</div></div></body></html>""",

    # === SOCIAL MEDIA SCAMS ===
    "scam_instagram_verify.html": """From: "Instagram" <support@instagram-verification-badge.com>
To: user@gmail.com
Subject: Get your blue verification badge - apply now
Date: Mon, 08 Sep 2025 12:44:55 -0400
Message-ID: <ig-verify-112233@instagram-verification-badge.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:8px;overflow:hidden">
<div style="background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);color:white;padding:20px;text-align:center"><h2 style="margin:0">Instagram</h2></div>
<div style="padding:20px">
<p>Your account has been selected for a <strong>blue verification badge</strong>. This is a limited-time offer.</p>
<p style="text-align:center"><a href="https://instagram-verification-badge.com/apply?user=user@gmail.com" style="background:#dc2743;color:white;padding:10px 20px;text-decoration:none;border-radius:4px">Apply for Badge</a></p>
</div></div></body></html>""",

    "scam_facebook_hacked.html": """From: "Facebook Security" <alerts@facebook-account-recovery.com>
To: user@outlook.com
Subject: Someone may have accessed your Facebook account
Date: Tue, 09 Sep 2025 09:33:11 -0400
Message-ID: <fb-hack-445566@facebook-account-recovery.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#1877f2;color:white;padding:15px;text-align:center"><h2 style="margin:0">Facebook</h2></div>
<div style="padding:20px">
<p>Hello,</p>
<p>We detected a login from a device we don't recognize in <strong>Moscow, Russia</strong>.</p>
<p><strong>Device:</strong> Chrome on Windows<br><strong>Time:</strong> Sep 9, 2025 4:33 AM</p>
<p>If this wasn't you, secure your account:</p>
<p style="text-align:center"><a href="https://facebook-account-recovery.com/secure?id=445566" style="background:#1877f2;color:white;padding:10px 20px;text-decoration:none">Secure Account</a></p>
</div></div></body></html>""",

    "scam_twitter_lock.html": """From: "X (Twitter)" <support@twitter-account-locked.com>
To: user@gmail.com
Subject: Your X account has been locked - verify to unlock
Date: Wed, 10 Sep 2025 16:22:33 -0400
Message-ID: <tw-lock-778899@twitter-account-locked.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:8px;overflow:hidden">
<div style="background:#000;color:white;padding:15px;text-align:center"><h2 style="margin:0">X</h2></div>
<div style="padding:20px">
<p>Your X account has been <strong>locked</strong> due to suspicious activity. We detected automated behavior that violates our terms.</p>
<p style="text-align:center"><a href="https://twitter-account-locked.com/unlock?id=778899" style="background:#000;color:white;padding:10px 20px;text-decoration:none;border-radius:4px">Unlock Account</a></p>
</div></div></body></html>""",

    "scam_linkedin_premium.html": """From: "LinkedIn Premium" <offer@linkedin-premium-offer.com>
To: professional@company.com
Subject: Exclusive offer: 3 months of LinkedIn Premium free
Date: Thu, 11 Sep 2025 08:11:22 -0400
Message-ID: <li-premium-112233@linkedin-premium-offer.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0077b5;color:white;padding:15px;text-align:center"><h2 style="margin:0">LinkedIn</h2></div>
<div style="padding:20px">
<p>Dear Professional,</p>
<p>You've been selected for an exclusive offer: <strong>3 months of LinkedIn Premium absolutely free</strong>.</p>
<p>This offer expires in 24 hours.</p>
<p style="text-align:center"><a href="https://linkedin-premium-offer.com/claim?id=112233" style="background:#0077b5;color:white;padding:10px 20px;text-decoration:none">Claim Free Premium</a></p>
</div></div></body></html>""",

    "scam_tiktok_creator.html": """From: "TikTok Creator Fund" <fund@tiktok-creator-apply.com>
To: creator@gmail.com
Subject: You've been selected for the TikTok Creator Fund - $10,000/month
Date: Fri, 12 Sep 2025 10:33:44 -0400
Message-ID: <tt-fund-445566@tiktok-creator-apply.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#000;color:white;padding:15px;text-align:center"><h2 style="margin:0">TikTok</h2></div>
<div style="padding:20px">
<p>Congratulations!</p>
<p>Your account has been selected for the <strong>TikTok Creator Fund</strong>. You can earn up to <strong>$10,000/month</strong> based on your video views.</p>
<p style="text-align:center"><a href="https://tiktok-creator-apply.com/join?id=445566" style="background:#fe2c55;color:white;padding:10px 20px;text-decoration:none">Join Creator Fund</a></p>
</div></div></body></html>""",

    # === SUBSCRIPTION / SERVICE SCAMS ===
    "scam_spotify_renewal.html": """From: "Spotify" <billing@spotify-premium-renewal.com>
To: user@gmail.com
Subject: Your Spotify Premium subscription renewal failed
Date: Mon, 08 Sep 2025 11:22:33 +0000
Message-ID: <spotify-renew-112233@spotify-premium-renewal.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#1db954;color:white;padding:15px;text-align:center"><h2 style="margin:0">Spotify</h2></div>
<div style="padding:20px">
<p>Hi User,</p>
<p>Your Spotify Premium subscription payment of <strong>$9.99</strong> failed. Your account will revert to free tier in 24 hours unless you update your payment method.</p>
<p style="text-align:center"><a href="https://spotify-premium-renewal.com/update?id=112233" style="background:#1db954;color:white;padding:10px 20px;text-decoration:none">Update Payment</a></p>
</div></div></body></html>""",

    "scam_adobe_renewal.html": """From: "Adobe Creative Cloud" <billing@adobe-creative-renew.com>
To: designer@company.com
Subject: Your Adobe Creative Cloud subscription will expire today
Date: Tue, 09 Sep 2025 09:55:11 -0400
Message-ID: <adobe-expire-445566@adobe-creative-renew.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#ff0000;color:white;padding:15px;text-align:center"><h2 style="margin:0">Adobe Creative Cloud</h2></div>
<div style="padding:20px">
<p>Dear Designer,</p>
<p>Your Adobe Creative Cloud subscription expires <strong>today</strong>. All your apps (Photoshop, Illustrator, Premiere Pro) will be deactivated.</p>
<p style="text-align:center"><a href="https://adobe-creative-renew.com/renew?id=445566" style="background:#ff0000;color:white;padding:10px 20px;text-decoration:none">Renew Now</a></p>
</div></div></body></html>""",

    "scam_norton_renewal.html": """From: "Norton Antivirus" <support@norton-antivirus-renew.com>
To: user@outlook.com
Subject: Your Norton subscription has expired - PC is unprotected
Date: Wed, 10 Sep 2025 14:11:22 -0400
Message-ID: <norton-expire-778899@norton-antivirus-renew.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#ffd700;color:#333;padding:15px;text-align:center"><h2 style="margin:0">Norton</h2></div>
<div style="padding:20px">
<p>Dear User,</p>
<p>Your Norton Antivirus subscription has <strong>expired</strong>. Your PC is now <strong>unprotected</strong> against viruses, malware, and ransomware.</p>
<p style="color:#c41200"><strong>Warning:</strong> 3 threats detected on your device.</p>
<p style="text-align:center"><a href="https://norton-antivirus-renew.com/renew?id=778899" style="background:#ffd700;color:#333;padding:10px 20px;text-decoration:none">Renew Protection</a></p>
</div></div></body></html>""",

    "scam_mcafee_expire.html": """From: "McAfee Security" <alerts@mcafee-protect-renew.com>
To: user@gmail.com
Subject: McAfee: Your PC is at risk - subscription expired
Date: Thu, 11 Sep 2025 07:44:55 -0400
Message-ID: <mcafee-expire-112233@mcafee-protect-renew.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#c41200;color:white;padding:15px;text-align:center"><h2 style="margin:0">McAfee</h2></div>
<div style="padding:20px">
<p>Dear User,</p>
<p>Your McAfee subscription expired on September 1. Your device is <strong>no longer protected</strong>.</p>
<p style="color:#c41200"><strong>5 threats detected!</strong></p>
<p style="text-align:center"><a href="https://mcafee-protect-renew.com/renew?id=112233" style="background:#c41200;color:white;padding:10px 20px;text-decoration:none">Renew Now</a></p>
</div></div></body></html>""",

    "scam_apple_music.html": """From: "Apple Music" <billing@apple-music-billing.com>
To: user@icloud.com
Subject: Your Apple Music subscription payment failed
Date: Fri, 12 Sep 2025 12:33:11 -0400
Message-ID: <apple-music-445566@apple-music-billing.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:-apple-system"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:12px;overflow:hidden">
<div style="background:#fc3c44;color:white;padding:15px;text-align:center"><h2 style="margin:0">Apple Music</h2></div>
<div style="padding:20px">
<p>Hi User,</p>
<p>Your Apple Music subscription payment of <strong>$10.99</strong> could not be processed. Update your payment method to avoid service interruption.</p>
<p style="text-align:center"><a href="https://apple-music-billing.com/update?id=445566" style="background:#fc3c44;color:white;padding:10px 20px;text-decoration:none;border-radius:8px">Update Payment</a></p>
</div></div></body></html>""",

    # === LOTTERY / PRIZE SCAMS ===
    "scam_mega_millions.html": """From: "Mega Millions Lottery" <winner@mega-millions-lottery-winner.com>
To: lucky@gmail.com
Subject: CONGRATULATIONS! You won $2,500,000 in the Mega Millions!
Date: Mon, 08 Sep 2025 14:55:33 +0000
Message-ID: <mega-win-112233@mega-millions-lottery-winner.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial;background:#fff8dc"><div style="max-width:500px;margin:0 auto;background:white;border:3px solid gold">
<div style="background:linear-gradient(135deg,#ffd700,#ff8c00);color:white;padding:25px;text-align:center"><h1 style="margin:0">YOU WON!</h1><p style="font-size:18px">$2,500,000.00</p></div>
<div style="padding:20px;text-align:center">
<p>Your email was selected as the grand prize winner of the Mega Millions Online Sweepstakes.</p>
<p><strong>Prize:</strong> $2,500,000.00<br><strong>Reference:</strong> MM-887766</p>
<p style="text-align:center"><a href="https://mega-millions-lottery-winner.com/claim?ref=887766" style="background:gold;color:#333;padding:12px 25px;text-decoration:none;font-weight:bold">Claim Prize</a></p>
</div></div></body></html>""",

    "scam_euro_lottery.html": """From: "EuroMillions" <prize@euromillions-online-draw.com>
To: winner@outlook.com
Subject: You have won 1,500,000 EUR in the EuroMillions draw!
Date: Tue, 09 Sep 2025 11:22:44 +0000
Message-ID: <euro-win-445566@euromillions-online-draw.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:3px solid gold">
<div style="background:#003399;color:white;padding:20px;text-align:center"><h2 style="margin:0">EuroMillions</h2></div>
<div style="padding:20px;text-align:center">
<p>Congratulations! Your email has won <strong>1,500,000 EUR</strong>.</p>
<p>Reference: EM-778899</p>
<p style="text-align:center"><a href="https://euromillions-online-draw.com/claim?ref=778899" style="background:#003399;color:white;padding:10px 20px;text-decoration:none">Claim Prize</a></p>
</div></div></body></html>""",

    "scam_powerball.html": """From: "Powerball Lottery" <claim@powerball-online-winner.com>
To: citizen@yahoo.com
Subject: POWERBALL: You won $5,000,000! Claim within 48 hours
Date: Wed, 10 Sep 2025 08:33:55 -0400
Message-ID: <pb-win-778899@powerball-online-winner.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial;background:#000"><div style="max-width:500px;margin:0 auto;background:white;border:3px solid red">
<div style="background:#c41200;color:white;padding:20px;text-align:center"><h1 style="margin:0">POWERBALL</h1></div>
<div style="padding:20px;text-align:center">
<p>You are the <strong>grand prize winner</strong> of the Powerball Online Sweepstakes!</p>
<p><strong>$5,000,000.00</strong></p>
<p style="color:#c41200"><strong>This offer expires in 48 hours!</strong></p>
<p style="text-align:center"><a href="https://powerball-online-winner.com/claim?id=778899" style="background:#c41200;color:white;padding:12px 25px;text-decoration:none;font-weight:bold">Claim $5M Now</a></p>
</div></div></body></html>""",

    "scam_uk_lottery.html": """From: "UK National Lottery" <prizes@uk-national-lottery-online.com>
To: user@gmx.com
Subject: You have won GBP 850,000 in the UK National Lottery!
Date: Thu, 11 Sep 2025 15:11:22 +0000
Message-ID: <uk-win-112233@uk-national-lottery-online.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#c8102e;color:white;padding:15px;text-align:center"><h2 style="margin:0">UK National Lottery</h2></div>
<div style="padding:20px;text-align:center">
<p>Congratulations! Your email address has won <strong>GBP 850,000</strong>.</p>
<p>Reference: UKL-334455</p>
<p style="text-align:center"><a href="https://uk-national-lottery-online.com/claim?ref=334455" style="background:#c8102e;color:white;padding:10px 20px;text-decoration:none">Claim Prize</a></p>
</div></div></body></html>""",

    # === TECH SUPPORT / SCAREWARE ===
    "scam_malware_detected.html": """From: "Windows Defender" <alert@windows-defender-alert.com>
To: user@outlook.com
Subject: [ALERT] 5 viruses detected on your computer - immediate action required
Date: Mon, 08 Sep 2025 16:33:44 -0400
Message-ID: <defender-alert-112233@windows-defender-alert.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial;background:#0078d4"><div style="max-width:500px;margin:30px auto;background:white;border-radius:8px;overflow:hidden">
<div style="background:#c41200;color:white;padding:20px;text-align:center"><h2 style="margin:0">CRITICAL ALERT</h2></div>
<div style="padding:20px">
<p>Windows Defender has detected <strong>5 critical threats</strong> on your device:</p>
<ul><li>Trojan.Win32.Emotet</li><li>Ransom.Wannacry.Gen</li><li>Adware.BrowserModifier</li><li>Spyware.KeyLogger</li><li>Worm.NetSky</li></ul>
<p style="color:#c41200"><strong>Your personal data is at risk!</strong></p>
<p style="text-align:center"><a href="https://windows-defender-alert.com/remove?token=112233" style="background:#c41200;color:white;padding:10px 20px;text-decoration:none">Remove Threats</a></p>
</div></div></body></html>""",

    "scam_pc_cleanup.html": """From: "PC Support" <support@pc-cleanup-optimize.com>
To: user@gmail.com
Subject: Your computer is running slow - free cleanup tool inside
Date: Tue, 09 Sep 2025 13:22:11 -0400
Message-ID: <pc-cleanup-445566@pc-cleanup-optimize.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0078d4;color:white;padding:15px;text-align:center"><h2 style="margin:0">PC Optimization</h2></div>
<div style="padding:20px">
<p>Dear User,</p>
<p>Our scan detected that your computer has <strong>234 unnecessary files</strong> and <strong>47 registry errors</strong>. This is causing your PC to run slowly.</p>
<p>Download our free cleanup tool to fix these issues:</p>
<p style="text-align:center"><a href="https://pc-cleanup-optimize.com/download?ref=445566" style="background:#0078d4;color:white;padding:10px 20px;text-decoration:none">Download Free Tool</a></p>
</div></div></body></html>""",

    "scam_vpn_expired.html": """From: "NordVPN" <billing@nordvpn-secure-renew.com>
To: user@company.com
Subject: Your NordVPN subscription expired - your IP is now exposed
Date: Wed, 10 Sep 2025 10:55:33 -0400
Message-ID: <nord-expire-778899@nordvpn-secure-renew.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#68b937;color:white;padding:15px;text-align:center"><h2 style="margin:0">NordVPN</h2></div>
<div style="padding:20px">
<p>Dear User,</p>
<p>Your NordVPN subscription has <strong>expired</strong>. Your real IP address is now <strong>exposed</strong> to websites and your ISP.</p>
<p>Your IP: <strong>192.168.1.105</strong> (this is visible to everyone)</p>
<p style="text-align:center"><a href="https://nordvpn-secure-renew.com/renew?id=778899" style="background:#68b937;color:white;padding:10px 20px;text-decoration:none">Renew VPN</a></p>
</div></div></body></html>""",

    # === JOB / OPPORTUNITY SCAMS ===
    "scam_work_from_home.html": """From: "Remote Jobs" <hiring@work-from-home-jobs247.com>
To: jobseeker@gmail.com
Subject: Work from home - earn $5,000/week guaranteed!
Date: Mon, 08 Sep 2025 09:11:22 -0400
Message-ID: <wfh-job-112233@work-from-home-jobs247.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#28a745;color:white;padding:15px;text-align:center"><h2 style="margin:0">Remote Work Opportunity</h2></div>
<div style="padding:20px">
<p>Dear Job Seeker,</p>
<p>We have an <strong>urgent opening</strong> for a remote data entry position. No experience required.</p>
<p><strong>Salary:</strong> $5,000/week<br><strong>Hours:</strong> Flexible<br><strong>Start:</strong> Immediately</p>
<p>To apply, pay a one-time registration fee of $99:</p>
<p style="text-align:center"><a href="https://work-from-home-jobs247.com/apply?id=112233" style="background:#28a745;color:white;padding:10px 20px;text-decoration:none">Apply Now</a></p>
</div></div></body></html>""",

    "scam_sugar_daddy.html": """From: "Wealthy Match" <offer@wealthy-match-sugar.com>
To: user@outlook.com
Subject: A wealthy benefactor wants to send you $3,000/week
Date: Tue, 09 Sep 2025 15:44:33 -0400
Message-ID: <sugar-445566@wealthy-match-sugar.com>
Content-Type: text/plain; charset="UTF-8"

Hello dear,

I am Mr. James Thompson, a wealthy businessman looking for a caring companion. I will send you $3,000 weekly as an allowance. I just need you to pay a small processing fee of $150 to get started.

Send payment via gift card to: james.thompson@email.com

I look forward to hearing from you.

Mr. James Thompson""",

    "scam_fake_interview.html": """From: "HR Department" <hr@company-careers-recruit.com>
To: applicant@gmail.com
Subject: Job Interview Invitation - Google Software Engineer
Date: Wed, 10 Sep 2025 08:33:44 -0400
Message-ID: <interview-778899@company-careers-recruit.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#4285f4;color:white;padding:15px;text-align:center"><h2 style="margin:0">Google Careers</h2></div>
<div style="padding:20px">
<p>Dear Applicant,</p>
<p>Your resume has been shortlisted for a <strong>Software Engineer</strong> position at Google. Please schedule your interview by clicking below:</p>
<p style="text-align:center"><a href="https://company-careers-recruit.com/schedule?ref=778899" style="background:#4285f4;color:white;padding:10px 20px;text-decoration:none">Schedule Interview</a></p>
</div></div></body></html>""",

    "scam_crypto_job.html": """From: "Crypto Recruit" <jobs@crypto-careers-offer.com>
To: developer@gmail.com
Subject: Remote Crypto Developer - $150/hr, no interview needed
Date: Thu, 11 Sep 2025 11:22:55 -0400
Message-ID: <crypto-job-112233@crypto-careers-offer.com>
Content-Type: text/plain; charset="UTF-8"

Hello Developer,

We are hiring remote crypto developers at $150/hour. No interview required. Just pay a $50 onboarding fee and you can start immediately.

Send payment to: crypto.careers@email.com

Crypto Careers Team""",

    # === INSURANCE SCAMS ===
    "scam_health_insurance.html": """From: "Health Insurance" <enroll@health-insurance-enroll.com>
To: family@gmail.com
Subject: Enroll now - health insurance starting at $49/month
Date: Mon, 08 Sep 2025 13:55:11 -0400
Message-ID: <health-enroll-112233@health-insurance-enroll.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0078d4;color:white;padding:15px;text-align:center"><h2 style="margin:0">Health Insurance Plans</h2></div>
<div style="padding:20px">
<p>Dear Family,</p>
<p>Open enrollment is now available. Get comprehensive health insurance starting at just <strong>$49/month</strong>.</p>
<p style="text-align:center"><a href="https://health-insurance-enroll.com/enroll?id=112233" style="background:#0078d4;color:white;padding:10px 20px;text-decoration:none">Enroll Now</a></p>
</div></div></body></html>""",

    "scam_car_warranty.html": """From: "Auto Warranty" <alerts@car-warranty-expired.com>
To: owner@yahoo.com
Subject: Your car warranty has expired - extend before it's too late
Date: Tue, 09 Sep 2025 07:22:33 -0400
Message-ID: <warranty-expire-445566@car-warranty-expired.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#c41200;color:white;padding:15px;text-align:center"><h2 style="margin:0">Auto Warranty Service</h2></div>
<div style="padding:20px">
<p>Dear Vehicle Owner,</p>
<p>Your extended car warranty has <strong>expired</strong>. Without coverage, you are responsible for all repair costs.</p>
<p style="color:#c41200"><strong>Extended repairs can cost $5,000-$15,000!</strong></p>
<p style="text-align:center"><a href="https://car-warranty-expired.com/extend?id=445566" style="background:#c41200;color:white;padding:10px 20px;text-decoration:none">Extend Warranty</a></p>
</div></div></body></html>""",

    "scam_life_insurance.html": """From: "Life Insurance" <quote@life-insurance-quote247.com>
To: adult@gmail.com
Subject: You've been pre-approved for $500,000 life insurance - no medical exam
Date: Wed, 10 Sep 2025 16:11:44 -0400
Message-ID: <life-ins-778899@life-insurance-quote247.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#003366;color:white;padding:15px;text-align:center"><h2 style="margin:0">Life Insurance</h2></div>
<div style="padding:20px">
<p>Congratulations! You've been pre-approved for a <strong>$500,000 life insurance policy</strong>. No medical exam required.</p>
<p style="text-align:center"><a href="https://life-insurance-quote247.com/apply?id=778899" style="background:#003366;color:white;padding:10px 20px;text-decoration:none">Get Your Quote</a></p>
</div></div></body></html>""",

    # === ROMANCE / DATING SCAMS ===
    "scam_dating_match.html": """From: "LoveMatch" <match@love-match-online.com>
To: lonely@gmail.com
Subject: Someone nearby is interested in you - view their profile
Date: Thu, 11 Sep 2025 19:33:22 -0400
Message-ID: <dating-match-112233@love-match-online.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:8px;overflow:hidden">
<div style="background:#e91e63;color:white;padding:15px;text-align:center"><h2 style="margin:0">LoveMatch</h2></div>
<div style="padding:20px;text-align:center">
<p>Someone nearby has viewed your profile and is interested!</p>
<p>To see who it is and send a message, verify your account:</p>
<p style="text-align:center"><a href="https://love-match-online.com/view?id=112233" style="background:#e91e63;color:white;padding:10px 20px;text-decoration:none;border-radius:20px">View Profile</a></p>
</div></div></body></html>""",

    "scam_tinder_gold.html": """From: "Tinder" <gold@tinder-gold-offer.com>
To: user@gmail.com
Subject: You've been selected for Tinder Gold at 90% off!
Date: Fri, 12 Sep 2025 10:11:33 -0400
Message-ID: <tinder-gold-445566@tinder-gold-offer.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:8px;overflow:hidden">
<div style="background:linear-gradient(135deg,#fd267a,#ff6036);color:white;padding:15px;text-align:center"><h2 style="margin:0">Tinder</h2></div>
<div style="padding:20px;text-align:center">
<p>You've been selected for <strong>Tinder Gold</strong> at <strong>90% off</strong> - just $0.99/month!</p>
<p style="text-align:center"><a href="https://tinder-gold-offer.com/claim?id=445566" style="background:#fd267a;color:white;padding:10px 20px;text-decoration:none;border-radius:20px">Get Tinder Gold</a></p>
</div></div></body></html>""",

    # === REALISTIC LEGITIMATE EMAILS ===
    "legit_github_notification.html": """From: "GitHub" <notifications@github.com>
To: developer@company.com
Subject: [sentinel-backend] Pull request #234: Fix authentication middleware
Date: Mon, 08 Sep 2025 14:22:33 -0700
Message-ID: <github-pr-234@github.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:-apple-system,Helvetica"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:6px;overflow:hidden">
<div style="background:#24292e;color:white;padding:15px;text-align:center"><h2 style="margin:0">GitHub</h2></div>
<div style="padding:20px">
<p><strong>sentinel-backend/pull/234</strong></p>
<p><strong>Fix authentication middleware</strong></p>
<p>@sarah-mitchell opened a pull request:</p>
<ul><li>Fixes token validation race condition</li><li>Adds rate limiting to login endpoint</li><li>Updates tests</li></p>
<p style="text-align:center"><a href="https://github.com/acme-corp/sentinel-backend/pull/234" style="background:#28a745;color:white;padding:8px 16px;text-decoration:none;border-radius:4px">View Pull Request</a></p>
</div></div></body></html>""",

    "legit_jira_ticket.html": """From: "Jira" <jira@acme-corp.atlassian.net>
To: developer@company.com
Subject: [SENTINEL-1234] Authentication middleware fix - assigned to you
Date: Tue, 09 Sep 2025 09:11:44 -0700
Message-ID: <jira-1234@acme-corp.atlassian.net>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0052cc;color:white;padding:15px;text-align:center"><h2 style="margin:0">Jira</h2></div>
<div style="padding:20px">
<p><strong>SENTINEL-1234</strong> assigned to you</p>
<p><strong>Authentication middleware fix</strong></p>
<p>Priority: High | Status: To Do | Sprint: 24</p>
<p style="text-align:center"><a href="https://acme-corp.atlassian.net/browse/SENTINEL-1234" style="background:#0052cc;color:white;padding:8px 16px;text-decoration:none">View Ticket</a></p>
</div></div></body></html>""",

    "legit_slack_message.html": """From: "Slack" <notifications@slack.com>
To: user@company.com
Subject: [Acme Corp #general] Sarah Mitchell: Meeting moved to 3pm
Date: Wed, 10 Sep 2025 11:33:22 -0700
Message-ID: <slack-general-556677@slack.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:8px;overflow:hidden">
<div style="background:#4a154b;color:white;padding:15px;text-align:center"><h2 style="margin:0">Slack</h2></div>
<div style="padding:20px">
<p><strong>Sarah Mitchell</strong> in <strong>#general</strong>:</p>
<p style="background:#f8f8f8;padding:10px;border-left:3px solid #4a154b">Hey team - the sprint review is moved to 3pm today. Please update your JIRA tickets before then. Thanks!</p>
<p style="text-align:center"><a href="https://acme-corp.slack.com" style="background:#4a154b;color:white;padding:8px 16px;text-decoration:none;border-radius:4px">Open Slack</a></p>
</div></div></body></html>""",

    "legit_zoom_invite.html": """From: "Zoom" <no-reply@zoom.us>
To: team@company.com
Subject: Sarah Mitchell is inviting you to a scheduled Zoom meeting
Date: Thu, 11 Sep 2025 08:00:11 -0700
Message-ID: <zoom-sprint-review@zoom.us>
Content-Type: text/calendar; charset="UTF-8"

BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Zoom//EN
BEGIN:VEVENT
DTSTART:20250912T180000Z
DTEND:20250912T190000Z
SUMMARY:Sprint Review - Week 37
DESCRIPTION:Join Zoom Meeting\nhttps://zoom.us/j/1234567890\nMeeting ID: 123 456 7890
LOCATION:Zoom
ORGANIZER;CN=Sarah Mitchell:mailto:sarah@acme-corp.com
END:VEVENT
END:VCALENDAR""",

    "legit_github_pr_merged.html": """From: "GitHub" <notifications@github.com>
To: developer@company.com
Subject: [sentinel-backend] Pull request #231 was merged
Date: Fri, 12 Sep 2025 16:22:44 -0700
Message-ID: <github-merge-231@github.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:-apple-system"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:6px;overflow:hidden">
<div style="background:#24292e;color:white;padding:15px;text-align:center"><h2 style="margin:0">GitHub</h2></div>
<div style="padding:20px">
<p><strong>sentinel-backend/pull/231 was merged</strong></p>
<p>@james-kim merged 3 commits into main from feature/campaign-correlation</p>
<ul><li>Add CorrelationService</li><li>Add campaign model and schema</li><li>Add correlation endpoint</li></ul>
<p style="text-align:center"><a href="https://github.com/acme-corp/sentinel-backend/pull/231" style="background:#28a745;color:white;padding:8px 16px;text-decoration:none;border-radius:4px">View Pull Request</a></p>
</div></div></body></html>""",

    "legit_confluence_page.html": """From: "Confluence" <confluence@acme-corp.atlassian.net>
To: developer@company.com
Subject: [Confluence] New page created: API Authentication Guide
Date: Mon, 08 Sep 2025 10:11:22 -0700
Message-ID: <confluence-auth-guide@acme-corp.atlassian.net>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#172b4d;color:white;padding:15px;text-align:center"><h2 style="margin:0">Confluence</h2></div>
<div style="padding:20px">
<p><strong>Sarah Mitchell</strong> created a new page:</p>
<p><strong>API Authentication Guide</strong></p>
<p>This guide covers JWT authentication, role-based access control, and API key management for the Sentinel platform.</p>
<p style="text-align:center"><a href="https://acme-corp.atlassian.net/wiki/spaces/SENTINEL/pages/123456" style="background:#0052cc;color:white;padding:8px 16px;text-decoration:none">View Page</a></p>
</div></div></body></html>""",

    # === DELIVERY / E-COMMERCE (LEGIT) ===
    "legit_amazon_delivery.html": """From: "Amazon" <shipment-tracking@amazon.com>
To: buyer@gmail.com
Subject: Your package is out for delivery - arriving today by 8pm
Date: Tue, 09 Sep 2025 08:33:11 -0700
Message-ID: <amazon-delivery-998877@amazon.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#232f3e;color:white;padding:15px;text-align:center"><h2 style="margin:0">amazon</h2></div>
<div style="padding:20px">
<p>Hello,</p>
<p>Your package is <strong>out for delivery</strong> and will arrive today by 8pm.</p>
<p><strong>Item:</strong> Logitech MX Master 3S Mouse<br><strong>Tracking:</strong> TBA123456789000</p>
<p style="text-align:center"><a href="https://www.amazon.com/gp/your-account/order-details?orderID=113-4882764" style="background:#ff9900;color:#000;padding:10px 20px;text-decoration:none">Track Package</a></p>
</div></div></body></html>""",

    "legit_steam_sale.html": """From: "Steam" <noreply@steampowered.com>
To: gamer@gmail.com
Subject: Steam Sale - Up to 80% off thousands of games!
Date: Wed, 10 Sep 2025 10:00:00 -0700
Message-ID: <steam-sale-sep25@steampowered.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:#1b2838;color:#c7d5e0;border-radius:8px;overflow:hidden">
<div style="padding:20px;text-align:center"><h2 style="color:#66c0f4;margin:0">Steam</h2></div>
<div style="padding:20px">
<p>The Steam Autumn Sale is on! Up to <strong>80% off</strong> thousands of games.</p>
<p style="text-align:center"><a href="https://store.steampowered.com/sale/autumn2025" style="background:#66c0f4;color:#1b2838;padding:10px 20px;text-decoration:none;border-radius:4px;font-weight:bold">Browse Sale</a></p>
</div></div></body></html>""",

    "legit_flight_confirmation.html": """From: "Delta Airlines" <confirmation@delta.com>
To: traveler@gmail.com
Subject: Your flight confirmation - JFK to LAX on Sep 15
Date: Thu, 11 Sep 2025 14:55:22 -0700
Message-ID: <delta-confirm-ABC123@delta.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#003366;color:white;padding:15px;text-align:center"><h2 style="margin:0">Delta</h2></div>
<div style="padding:20px">
<p>Hello Traveler,</p>
<p>Your flight is confirmed!</p>
<table style="width:100%;margin:10px 0"><tr><td><strong>Flight:</strong></td><td>DL 456</td></tr>
<tr><td><strong>Route:</strong></td><td>JFK → LAX</td></tr>
<tr><td><strong>Date:</strong></td><td>Sep 15, 2025</td></tr>
<tr><td><strong>Time:</strong></td><td>8:30 AM - 11:45 AM</td></tr>
<tr><td><strong>Confirmation:</strong></td><td>ABC123</td></tr></table>
<p style="text-align:center"><a href="https://www.delta.com" style="background:#003366;color:white;padding:10px 20px;text-decoration:none">Manage Booking</a></p>
</div></div></body></html>""",

    "legit_hotel_booking.html": """From: "Marriott" <reservations@marriott.com>
To: traveler@company.com
Subject: Reservation confirmed - Marriott Times Square, Sep 15-18
Date: Fri, 12 Sep 2025 09:33:44 -0700
Message-ID: <marriott-res-XYZ789@marriott.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#8c1515;color:white;padding:15px;text-align:center"><h2 style="margin:0">Marriott</h2></div>
<div style="padding:20px">
<p>Dear Traveler,</p>
<p>Your reservation is confirmed!</p>
<table style="width:100%;margin:10px 0"><tr><td><strong>Hotel:</strong></td><td>Marriott New York Times Square</td></tr>
<tr><td><strong>Check-in:</strong></td><td>Sep 15, 2025 (3:00 PM)</td></tr>
<tr><td><strong>Check-out:</strong></td><td>Sep 18, 2025 (11:00 AM)</td></tr>
<tr><td><strong>Confirmation:</strong></td><td>XYZ789</td></tr></table>
<p style="text-align:center"><a href="https://www.marriott.com/reservation" style="background:#8c1515;color:white;padding:10px 20px;text-decoration:none">View Reservation</a></p>
</div></div></body></html>""",

    # === MORE PHISHING VARIANTS ===
    "phish_fake_tax_prep.html": """From: "TurboTax" <support@turbotax-file-submit.com>
To: taxpayer@gmail.com
Subject: TurboTax: Your tax return was rejected - fix now
Date: Mon, 08 Sep 2025 11:55:33 -0400
Message-ID: <turbo-reject-112233@turbotax-file-submit.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#d52b1e;color:white;padding:15px;text-align:center"><h2 style="margin:0">TurboTax</h2></div>
<div style="padding:20px">
<p>Dear Taxpayer,</p>
<p>Your 2024 tax return was <strong>rejected by the IRS</strong> due to a processing error. You must resubmit within 24 hours or face penalties.</p>
<p style="text-align:center"><a href="https://turbotax-file-submit.com/fix?id=112233" style="background:#d52b1e;color:white;padding:10px 20px;text-decoration:none">Fix Tax Return</a></p>
</div></div></body></html>""",

    "phish_fake_docusign.html": """From: "DocuSign" <notifications@esign-docusign-portal.com>
To: legal@company.com
Subject: DocuSign: Please sign - Meridian Corp Acquisition Agreement
Date: Tue, 09 Sep 2025 09:44:11 -0400
Message-ID: <docusign-meridian-445566@esign-docusign-portal.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#4c00ff;color:white;padding:15px;text-align:center"><h2 style="margin:0">DocuSign</h2></div>
<div style="padding:20px">
<p>Legal Department,</p>
<p>You are requested to sign:</p>
<p><strong>Meridian Corp Acquisition Agreement</strong><br>Sent by: David Chen (CEO)</p>
<p style="text-align:center"><a href="https://esign-docusign-portal.com/sign?env=meridian-445566" style="background:#4c00ff;color:white;padding:10px 20px;text-decoration:none">Review & Sign</a></p>
</div></div></body></html>""",

    "phish_fake_sharepoint.html": """From: "SharePoint" <no-reply@microsoft-sharepoint-docs.com>
To: cfo@company.com
Subject: Your CEO shared "Q4 Layoff Plan - Confidential" with you
Date: Wed, 10 Sep 2025 07:44:55 -0400
Message-ID: <sp-layoff-778899@microsoft-sharepoint-docs.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0078d4;color:white;padding:15px;text-align:center"><h2 style="margin:0">SharePoint</h2></div>
<div style="padding:20px">
<p><strong>David Chen (CEO)</strong> shared a document:</p>
<p><strong>Q4 Layoff Plan - Confidential</strong><br>Excel Online</p>
<p style="text-align:center"><a href="https://microsoft-sharepoint-docs.com/open?doc=layoff-q4&token=778899" style="background:#0078d4;color:white;padding:10px 20px;text-decoration:none">Open Document</a></p>
</div></div></body></html>""",

    "phish_fake_dropbox.html": """From: "Dropbox" <no-reply@dropbox-shared-folder.com>
To: finance@company.com
Subject: "Budget_2026_Final.xlsx" was shared with you via Dropbox
Date: Thu, 11 Sep 2025 14:11:33 -0400
Message-ID: <dropbox-budget-112233@dropbox-shared-folder.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0061ff;color:white;padding:15px;text-align:center"><h2 style="margin:0">Dropbox</h2></div>
<div style="padding:20px">
<p><strong>Sarah Mitchell</strong> shared a file with you:</p>
<p><strong>Budget_2026_Final.xlsx</strong><br>Microsoft Excel &middot; 2.4 MB</p>
<p style="text-align:center"><a href="https://dropbox-shared-folder.com/open?file=budget-2026&token=112233" style="background:#0061ff;color:white;padding:10px 20px;text-decoration:none">Open File</a></p>
</div></div></body></html>""",

    "phish_fake_google_doc.html": """From: "Google Docs" <no-reply@google-docs-share.com>
To: team@company.com
Subject: Sarah Mitchell shared "Q3 OKR Tracking - Updated" with you
Date: Fri, 12 Sep 2025 08:55:22 -0400
Message-ID <google-docs-okr-445566@google-docs-share.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#4285f4;color:white;padding:15px;text-align:center"><h2 style="margin:0">Google Docs</h2></div>
<div style="padding:20px">
<p><strong>Sarah Mitchell</strong> shared a document with you:</p>
<p><strong>Q3 OKR Tracking - Updated</strong></p>
<p style="text-align:center"><a href="https://google-docs-share.com/open?doc=okr-q3&token=445566" style="background:#4285f4;color:white;padding:10px 20px;text-decoration:none">Open in Docs</a></p>
</div></div></body></html>""",

    # === CRYPTO SCAMS ===
    "scam_binance_account.html": """From: "Binance" <security@binance-account-verify.com>
To: trader@gmail.com
Subject: Binance: Withdrawal of 2.5 BTC initiated from your account
Date: Mon, 08 Sep 2025 20:11:44 +0000
Message-ID: <binance-withdraw-112233@binance-account-verify.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial;background:#0b0e11"><div style="max-width:500px;margin:30px auto;background:#1e2329;border-radius:8px;overflow:hidden">
<div style="background:#f0b90b;color:#0b0e11;padding:15px;text-align:center"><h2 style="margin:0">Binance</h2></div>
<div style="padding:20px;color:#eaecef">
<p>Dear User,</p>
<p>A withdrawal of <strong>2.5 BTC ($150,000.00)</strong> has been initiated from your account. If you did not make this request, cancel immediately:</p>
<p style="text-align:center"><a href="https://binance-account-verify.com/cancel?id=112233" style="background:#f0b90b;color:#0b0e11;padding:10px 20px;text-decoration:none;font-weight:bold">Cancel Withdrawal</a></p>
</div></div></body></html>""",

    "scam_coinbase_phish.html": """From: "Coinbase" <alerts@coinbase-secure-wallet.com>
To: crypto@gmail.com
Subject: Coinbase: Unusual login attempt - secure your wallet
Date: Tue, 09 Sep 2025 22:33:11 +0000
Message-ID: <cb-login-445566@coinbase-secure-wallet.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial;background:#050f18"><div style="max-width:500px;margin:30px auto;background:#1a1a2e;border-radius:8px;overflow:hidden">
<div style="background:#0052ff;color:white;padding:15px;text-align:center"><h2 style="margin:0">Coinbase</h2></div>
<div style="padding:20px;color:#fff">
<p>Dear User,</p>
<p>We detected an unusual login attempt on your Coinbase account from <strong>Bucharest, Romania</strong>.</p>
<p>If this wasn't you, secure your wallet:</p>
<p style="text-align:center"><a href="https://coinbase-secure-wallet.com/secure?id=445566" style="background:#0052ff;color:white;padding:10px 20px;text-decoration:none">Secure Wallet</a></p>
</div></div></body></html>""",

    # === MORE CEO FRAUD VARIANTS ===
    "bec_ceo_gift_cards.html": """From: "David Chen CEO" <david.chen@acmecorp-securemail.com>
To: assistant@company.com
Subject: Quick favor - need you to get some gift cards
Date: Wed, 10 Sep 2025 08:11:33 -0400
Message-ID: <ceo-gift-778899@acmecorp-securemail.com>
Content-Type: text/plain; charset="UTF-8"

Hi,

I'm stuck in a board meeting and can't make calls. I need you to go to the store and pick up 5 Apple Gift Cards ($200 each). I need them for a client appreciation gesture.

Please scratch off the codes and email them to me. I'll reimburse you when I'm back in the office.

This is urgent - the client is waiting.

Thanks,
David Chen
Sent from my iPhone""",

    "bec_cfo_urgent.html": """From: "CFO Office" <cfo@company-finance-portal.com>
To: ap@company.com
Subject: URGENT: Vendor payment redirect - do not call
Date: Thu, 11 Sep 2025 07:33:22 -0400
Message-ID: <cfo-redirect-112233@company-finance-portal.com>
Content-Type: text/plain; charset="UTF-8"

Hi AP,

I need you to redirect the upcoming payment to Pinnacle Consulting from their old Chase account to their new Wells Fargo account:

OLD: Chase ending in 8899
NEW: Wells Fargo ending in 3344
Routing: 121000248
Account: 5566778899

This is time-sensitive. Do NOT call the vendor to confirm - I already spoke with their CFO directly. Just process the change.

Sent from my iPhone""",

    # === MORE DIVERSE SCAMS ===
    "scam_fake_parcel.html": """From: "Package Delivery" <delivery@parcel-delivery-customs.com>
To: recipient@outlook.com
Subject: Your parcel is stuck at customs - pay $29.99 to release
Date: Mon, 08 Sep 2025 18:22:55 +0000
Message-ID: <parcel-stuck-112233@parcel-delivery-customs.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#ff6600;color:white;padding:15px;text-align:center"><h2 style="margin:0">Package Delivery Service</h2></div>
<div style="padding:20px">
<p>Dear Recipient,</p>
<p>Your parcel is currently <strong>held at customs</strong> and cannot be released until a processing fee of <strong>$29.99</strong> is paid.</p>
<p><strong>Tracking:</strong> PD-2025-887766</p>
<p style="text-align:center"><a href="https://parcel-delivery-customs.com/pay?id=112233" style="background:#ff6600;color:white;padding:10px 20px;text-decoration:none">Pay Fee</a></p>
</div></div></body></html>""",

    "scam_fake_subscription.html": """From: "Premium Service" <billing@premium-service-billing.com>
To: user@gmail.com
Subject: Your Premium Service subscription renewal - $299.99 charged
Date: Tue, 09 Sep 2025 11:44:33 -0400
Message-ID: <premium-charge-445566@premium-service-billing.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#6c5ce7;color:white;padding:15px;text-align:center"><h2 style="margin:0">Premium Service</h2></div>
<div style="padding:20px">
<p>Dear User,</p>
<p>Your Premium Service subscription has been renewed. A charge of <strong>$299.99</strong> was processed to your card ending in 4827.</p>
<p>If you did not authorize this renewal, request a refund:</p>
<p style="text-align:center"><a href="https://premium-service-billing.com/refund?id=445566" style="background:#6c5ce7;color:white;padding:10px 20px;text-decoration:none">Request Refund</a></p>
</div></div></body></html>""",

    "scam_fake_charity.html": """From: "Global Relief Fund" <donate@global-relief-fund.org>
To: generous@gmail.com
Subject: Urgent: Help earthquake victims - donate today
Date: Wed, 10 Sep 2025 16:55:11 +0000
Message-ID: <charity-778899@global-relief-fund.org>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#c41200;color:white;padding:15px;text-align:center"><h2 style="margin:0">Global Relief Fund</h2></div>
<div style="padding:20px">
<p>Dear Friend,</p>
<p>A devastating earthquake has affected thousands of families. They need your help <strong>right now</strong>.</p>
<p>Every dollar saves lives. Please donate today:</p>
<p style="text-align:center"><a href="https://global-relief-fund.org/donate?ref=778899" style="background:#c41200;color:white;padding:10px 20px;text-decoration:none">Donate Now</a></p>
</div></div></body></html>""",

    "scam_fake_inheritance.html": """From: "Barrister James" <barrister@inheritance-claim-firm.com>
To: heir@gmail.com
Subject: Inheritance claim - $4.5M waiting for you
Date: Thu, 11 Sep 2025 09:22:44 +0000
Message-ID: <inheritance-112233@inheritance-claim-firm.com>
Content-Type: text/plain; charset="UTF-8"

Dear Sir/Madam,

I am Barrister James Harrison, solicitor at law. My late client, Mr. William Harrison, passed away leaving an estate valued at $4.5 million. He left no next of kin.

As you share the same surname, you may be entitled to claim this inheritance. Please reply with your full name, address, and phone number to begin the claim process.

This is a legitimate legal matter requiring confidentiality.

Best regards,
Barrister James Harrison""",

    "scam_fake_visa_lottery.html": """From: "US Visa Lottery" <lottery@us-visa-diversity-program.com>
To: applicant@gmail.com
Subject: You've been selected for the US Visa Diversity Lottery!
Date: Fri, 12 Sep 2025 11:33:22 +0000
Message-ID: <visa-lottery-445566@us-visa-diversity-program.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:2px solid #003366">
<div style="background:#003366;color:white;padding:15px;text-align:center"><h2 style="margin:0">US Visa Diversity Program</h2></div>
<div style="padding:20px;text-align:center">
<p>Congratulations! You have been <strong>selected</strong> in the Diversity Visa Lottery.</p>
<p><strong>Case Number:</strong> 2025-887766</p>
<p style="text-align:center"><a href="https://us-visa-diversity-program.com/claim?case=887766" style="background:#003366;color:white;padding:10px 20px;text-decoration:none">Claim Visa</a></p>
</div></div></body></html>""",

    # === MORE SUBSCRIPTION SCAMS ===
    "scam_youtube_premium.html": """From: "YouTube Premium" <billing@youtube-premium-offer.com>
To: user@gmail.com
Subject: YouTube Premium: Your free trial expired - $15.99 charged
Date: Mon, 08 Sep 2025 08:44:55 -0400
Message-ID <yt-premium-112233@youtube-premium-offer.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#ff0000;color:white;padding:15px;text-align:center"><h2 style="margin:0">YouTube</h2></div>
<div style="padding:20px">
<p>Hi User,</p>
<p>Your YouTube Premium free trial has ended. A charge of <strong>$15.99</strong> has been applied to your payment method.</p>
<p style="text-align:center"><a href="https://youtube-premium-offer.com/manage?id=112233" style="background:#ff0000;color:white;padding:10px 20px;text-decoration:none">Manage Subscription</a></p>
</div></div></body></html>""",

    "scam_hulu_expired.html": """From: "Hulu" <support@hulu-subscription-expired.com>
To: user@outlook.com
Subject: Hulu: Your subscription has expired - shows will be removed
Date: Tue, 09 Sep 2025 13:11:22 -0400
Message-ID: <hulu-expire-445566@hulu-subscription-expired.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#1ce783;color:#000;padding:15px;text-align:center"><h2 style="margin:0">Hulu</h2></div>
<div style="padding:20px">
<p>Hi User,</p>
<p>Your Hulu subscription expired. All your saved shows and watch history will be <strong>deleted in 24 hours</strong>.</p>
<p style="text-align:center"><a href="https://hulu-subscription-expired.com/renew?id=445566" style="background:#1ce783;color:#000;padding:10px 20px;text-decoration:none">Renew Now</a></p>
</div></div></body></html>""",

    "scam_disney_plus.html": """From: "Disney+" <billing@disneyplus-billing-update.com>
To: family@gmail.com
Subject: Disney+: Update your payment method - subscription interrupted
Date: Wed, 10 Sep 2025 10:22:33 -0400
Message-ID: <disney-billing-778899@disneyplus-billing-update.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:Arial"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd">
<div style="background:#0063e5;color:white;padding:15px;text-align:center"><h2 style="margin:0">Disney+</h2></div>
<div style="padding:20px">
<p>Hi Family,</p>
<p>Your Disney+ subscription payment failed. <strong>All family profiles will be deactivated</strong> within 24 hours.</p>
<p style="text-align:center"><a href="https://disneyplus-billing-update.com/update?id=778899" style="background:#0063e5;color:white;padding:10px 20px;text-decoration:none">Update Payment</a></p>
</div></div></body></html>""",

    "scam_apple_tv.html": """From: "Apple TV+" <billing@apple-tv-billing.com>
To: user@icloud.com
Subject: Apple TV+: Your subscription payment was declined
Date: Thu, 11 Sep 2025 15:44:55 -0400
Message-ID: <appletv-billing-112233@apple-tv-billing.com>
Content-Type: text/html; charset="UTF-8"

<html><body style="font-family:-apple-system"><div style="max-width:500px;margin:0 auto;background:white;border:1px solid #ddd;border-radius:12px;overflow:hidden">
<div style="background:#000;color:white;padding:15px;text-align:center"><h2 style="margin:0">Apple TV+</h2></div>
<div style="padding:20px">
<p>Hi User,</p>
<p>Your Apple TV+ payment of <strong>$6.99</strong> was declined. Update your payment method to keep watching.</p>
<p style="text-align:center"><a href="https://apple-tv-billing.com/update?id=112233" style="background:#000;color:white;padding:10px 20px;text-decoration:none;border-radius:8px">Update Payment</a></p>
</div></div></body></html>""",

    # === LEGITIMATE INTERNAL ===
    "legit_incident_report.html": """From: "Security Team" <security@acme-corp.com>
To: all-engineering@acme-corp.com
Subject: [SEV-2] Incident Report: API Gateway outage Sep 8 14:30-15:45 UTC
Date: Tue, 09 Sep 2025 09:00:11 -0700
Message-ID: <incident-sev2-20250908@acme-corp.com>
Content-Type: text/plain; charset="UTF-8"

Team,

SEV-2 Incident Report: API Gateway Outage

TIMELINE:
- 14:30 UTC: API gateway started returning 502 errors
- 14:35 UTC: On-call engineer paged
- 14:42 UTC: Root cause identified - expired SSL certificate
- 14:50 UTC: Hotfix deployed
- 15:45 UTC: Full recovery confirmed

IMPACT:
- 75 minutes of degraded service
- ~12,000 failed requests
- No data loss

ROOT CAUSE: SSL certificate auto-renewal failed due to DNS validation issue.

REMEDIATION:
1. Added monitoring for cert expiry (7-day warning)
2. Implemented manual cert renewal procedure
3. Updated runbook

Security Team""",

    "legit_performance_update.html": """From: "CEO" <david.chen@acme-corp.com>
To: all-staff@acme-corp.com
Subject: Q3 All-Hands - Company Update
Date: Mon, 08 Sep 2025 16:00:44 -0700
Message-ID: <allhands-q3-2025@acme-corp.com>
Content-Type: text/plain; charset="UTF-8"

Hi Team,

Join me this Friday at 2pm PT for our Q3 all-hands meeting.

Agenda:
1. Q3 financial results (15 min)
2. Product roadmap update (20 min)
3. New hire introductions (10 min)
4. Engineering excellence awards (10 min)
5. Q&A (15 min)

Looking forward to celebrating our wins together.

David
CEO, Acme Corp""",
}

# Write all fixtures
for filename, content in FIXTURES.items():
    path = os.path.join(OUT, filename)
    with open(path, "w") as f:
        # Fix Message-ID lines with missing >
        fixed = content.replace("Message-ID <", "Message-ID: <")
        f.write(fixed)

print(f"Generated {len(FIXTURES)} fixture files")
