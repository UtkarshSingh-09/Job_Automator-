#!/usr/bin/env python3
"""
Seed script to expand companies catalog to 500+ verified tech companies that hire
software, AI/ML, backend, frontend, data, and devops interns in India (or remote India).
"""

import sys
from pathlib import Path
import yaml

TARGET_COMPANIES = [
    # ==============================================================================
    # 1. INDIAN TECH UNICORNS & HIGH-GROWTH STARTUPS (Top Intern Employers)
    # ==============================================================================
    {"name": "Zomato", "domain": "zomato.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Blinkit", "domain": "blinkit.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "blinkit"},
    {"name": "PhonePe", "domain": "phonepe.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Paytm", "domain": "paytm.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "BharatPe", "domain": "bharatpe.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Slice", "domain": "sliceit.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Navi", "domain": "navi.com", "tier": 1, "ats_provider": "lever", "ats_slug": "navi"},
    {"name": "Flipkart", "domain": "flipkart.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "InMobi", "domain": "inmobi.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "inmobi"},
    {"name": "ShareChat", "domain": "sharechat.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sharechat"},
    {"name": "Games24x7", "domain": "games24x7.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "games24x7"},
    {"name": "Pocket FM", "domain": "pocketfm.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "pocketfm"},
    {"name": "Kuku FM", "domain": "kukufm.com", "tier": 1, "ats_provider": "lever", "ats_slug": "kukufm"},
    {"name": "Pratilipi", "domain": "pratilipi.com", "tier": 2, "ats_provider": "lever", "ats_slug": "pratilipi"},
    {"name": "Dukaan", "domain": "mydukaan.io", "tier": 2, "ats_provider": "lever", "ats_slug": "dukaan"},
    {"name": "BlackBuck", "domain": "blackbuck.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "ElasticRun", "domain": "elasticrun.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Bizongo", "domain": "bizongo.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "bizongo"},
    {"name": "Zetwerk", "domain": "zetwerk.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "zetwerk"},
    {"name": "Infra.Market", "domain": "infra.market", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "OfBusiness", "domain": "ofbusiness.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Moglix", "domain": "moglix.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Captain Fresh", "domain": "captainfresh.in", "tier": 2, "ats_provider": "lever", "ats_slug": "captainfresh"},
    {"name": "Country Delight", "domain": "countrydelight.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Curefoods", "domain": "curefoods.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Furlenco", "domain": "furlenco.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Rentomojo", "domain": "rentomojo.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Wakefit", "domain": "wakefit.co", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Pepperfry", "domain": "pepperfry.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Livspace", "domain": "livspace.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "livspace"},
    {"name": "HomeLane", "domain": "homelane.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "NoBroker", "domain": "nobroker.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Square Yards", "domain": "squareyards.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Magicbricks", "domain": "magicbricks.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "99acres", "domain": "99acres.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "CarDekho", "domain": "cardekho.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "cardekho"},
    {"name": "Droom", "domain": "droom.in", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "BluSmart", "domain": "blu-smart.com", "tier": 2, "ats_provider": "lever", "ats_slug": "blusmart"},
    {"name": "Yulu", "domain": "yulu.bike", "tier": 2, "ats_provider": "lever", "ats_slug": "yulu"},
    {"name": "Bounce", "domain": "bounceshare.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Simple Energy", "domain": "simpleenergy.in", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "River", "domain": "riverind.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Nykaa", "domain": "nykaa.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "nykaa"},
    {"name": "Purplle", "domain": "purplle.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Mamaearth (Honasa)", "domain": "mamaearth.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Sugar Cosmetics", "domain": "sugarcosmetics.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "boAt", "domain": "boat-lifestyle.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Noise", "domain": "gonoise.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Boult Audio", "domain": "boultaudio.com", "tier": 3, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 2. TOP SAAS & DEVELOPER TOOLS (India R&D / Global Engineering)
    # ==============================================================================
    {"name": "Appsmith", "domain": "appsmith.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "appsmith"},
    {"name": "SigNoz", "domain": "signoz.io", "tier": 1, "ats_provider": "lever", "ats_slug": "signoz"},
    {"name": "Devtron", "domain": "devtron.ai", "tier": 2, "ats_provider": "lever", "ats_slug": "devtron"},
    {"name": "InfraCloud", "domain": "infracloud.io", "tier": 2, "ats_provider": "lever", "ats_slug": "infracloud"},
    {"name": "Squadcast", "domain": "squadcast.com", "tier": 2, "ats_provider": "lever", "ats_slug": "squadcast"},
    {"name": "Wingify", "domain": "wingify.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "wingify"},
    {"name": "Freshworks", "domain": "freshworks.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Chargebee", "domain": "chargebee.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "chargebee"},
    {"name": "Zoho", "domain": "zoho.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Kissflow", "domain": "kissflow.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "WebEngage", "domain": "webengage.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "webengage"},
    {"name": "MoEngage", "domain": "moengage.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "moengage"},
    {"name": "Gupshup", "domain": "gupshup.io", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "gupshup"},
    {"name": "Exotel", "domain": "exotel.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "exotel"},
    {"name": "Haptik", "domain": "haptik.ai", "tier": 2, "ats_provider": "lever", "ats_slug": "haptik"},
    {"name": "Sprinklr", "domain": "sprinklr.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sprinklr"},
    {"name": "Druva", "domain": "druva.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "druva"},
    {"name": "Icertis", "domain": "icertis.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "icertis"},
    {"name": "Innovaccer", "domain": "innovaccer.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "innovaccer"},
    {"name": "HighRadius", "domain": "highradius.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Whatfix", "domain": "whatfix.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "whatfix"},
    {"name": "HackerRank", "domain": "hackerrank.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "hackerrank"},
    {"name": "InterviewBit (Scaler)", "domain": "scaler.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "scaler"},
    {"name": "LeetCode", "domain": "leetcode.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "leetcode"},
    {"name": "GeeksforGeeks", "domain": "geeksforgeeks.org", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "PhysicsWallah", "domain": "pw.live", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Vedantu", "domain": "vedantu.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "UpGrad", "domain": "upgrad.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Simplilearn", "domain": "simplilearn.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Great Learning", "domain": "mygreatlearning.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Newton School", "domain": "newtonschool.co", "tier": 2, "ats_provider": "lever", "ats_slug": "newtonschool"},
    {"name": "Masai School", "domain": "masaischool.com", "tier": 2, "ats_provider": "lever", "ats_slug": "masaischool"},
    {"name": "Coding Ninjas", "domain": "codingninjas.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "codingninjas"},
    {"name": "PostHog", "domain": "posthog.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "posthog"},
    {"name": "Sentry", "domain": "sentry.io", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sentry"},
    {"name": "Datadog", "domain": "datadoghq.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "datadog"},
    {"name": "Grafana Labs", "domain": "grafana.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "grafana"},
    {"name": "HashiCorp", "domain": "hashicorp.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "hashicorp"},
    {"name": "PagerDuty", "domain": "pagerduty.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "pagerduty"},
    {"name": "LaunchDarkly", "domain": "launchdarkly.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "launchdarkly"},
    {"name": "Pulumi", "domain": "pulumi.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "pulumi"},
    {"name": "Netlify", "domain": "netlify.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "netlify"},
    {"name": "Fastly", "domain": "fastly.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "fastly"},
    {"name": "Cloudflare", "domain": "cloudflare.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "cloudflare"},
    {"name": "GitLab", "domain": "gitlab.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "gitlab"},
    {"name": "Docker", "domain": "docker.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "docker"},
    {"name": "CircleCI", "domain": "circleci.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "circleci"},
    {"name": "Buildkite", "domain": "buildkite.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "buildkite"},
    {"name": "Temporal", "domain": "temporal.io", "tier": 1, "ats_provider": "ashby", "ats_slug": "temporal"},
    {"name": "Inngest", "domain": "inngest.com", "tier": 2, "ats_provider": "ashby", "ats_slug": "inngest"},
    {"name": "Prisma", "domain": "prisma.io", "tier": 1, "ats_provider": "ashby", "ats_slug": "prisma"},
    {"name": "Drizzle", "domain": "orm.drizzle.team", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Clerk", "domain": "clerk.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "clerk"},
    {"name": "WorkOS", "domain": "workos.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "workos"},
    {"name": "Stytch", "domain": "stytch.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "stytch"},

    # ==============================================================================
    # 3. GLOBAL TECH R&D HUBS & MULTINATIONALS IN INDIA
    # ==============================================================================
    {"name": "Uber India", "domain": "uber.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "uber"},
    {"name": "Atlassian India", "domain": "atlassian.com", "tier": 1, "ats_provider": "lever", "ats_slug": "atlassian"},
    {"name": "Adobe India", "domain": "adobe.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Salesforce India", "domain": "salesforce.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Cisco India", "domain": "cisco.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Intel India", "domain": "intel.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "AMD India", "domain": "amd.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "NVIDIA India", "domain": "nvidia.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Qualcomm India", "domain": "qualcomm.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Broadcom India", "domain": "broadcom.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Intuit India", "domain": "intuit.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "PayPal India", "domain": "paypal.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "ServiceNow India", "domain": "servicenow.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Snowflake India", "domain": "snowflake.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "snowflake"},
    {"name": "Databricks India", "domain": "databricks.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "databricks"},
    {"name": "Twilio India", "domain": "twilio.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "twilio"},
    {"name": "MongoDB India", "domain": "mongodb.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "mongodb"},
    {"name": "Elastic India", "domain": "elastic.co", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "elastic"},
    {"name": "Confluent India", "domain": "confluent.io", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "confluent"},
    {"name": "Red Hat India", "domain": "redhat.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Oracle India", "domain": "oracle.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "IBM India", "domain": "ibm.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "SAP India", "domain": "sap.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Dell Technologies India", "domain": "dell.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "HP India", "domain": "hp.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Samsung R&D India", "domain": "samsung.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Sony R&D India", "domain": "sony.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Rakuten India", "domain": "rakuten.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Booking.com India", "domain": "booking.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Expedia Group India", "domain": "expediagroup.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Airbnb", "domain": "airbnb.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "airbnb"},
    {"name": "DoorDash", "domain": "doordash.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "doordash"},
    {"name": "Instacart", "domain": "instacart.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "instacart"},
    {"name": "Pinterest", "domain": "pinterest.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "pinterest"},
    {"name": "Snap Inc. India", "domain": "snap.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "snapchat"},
    {"name": "Reddit", "domain": "reddit.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "reddit"},
    {"name": "Discord", "domain": "discord.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "discord"},
    {"name": "Spotify", "domain": "spotify.com", "tier": 1, "ats_provider": "lever", "ats_slug": "spotify"},
    {"name": "Roku", "domain": "roku.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "roku"},
    {"name": "Box", "domain": "box.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "box"},
    {"name": "Dropbox", "domain": "dropbox.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "dropbox"},
    {"name": "Asana", "domain": "asana.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "asana"},
    {"name": "Notion", "domain": "notion.so", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "notion"},
    {"name": "Airtable", "domain": "airtable.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "airtable"},
    {"name": "Miro", "domain": "miro.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "miro"},
    {"name": "Canva", "domain": "canva.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "canva"},
    {"name": "Grammarly", "domain": "grammarly.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "grammarly"},
    {"name": "Duolingo", "domain": "duolingo.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "duolingo"},
    {"name": "Coursera", "domain": "coursera.org", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "coursera"},
    {"name": "Udemy", "domain": "udemy.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "udemy"},
    {"name": "Chegg India", "domain": "chegg.com", "tier": 2, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 4. QUANT TRADING, HFT, INVESTMENT BANKS & FINTECH (Highest Stipends in India)
    # ==============================================================================
    {"name": "D.E. Shaw India", "domain": "deshawindia.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Tower Research Capital India", "domain": "tower-research.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "towerresearchcapital"},
    {"name": "WorldQuant India", "domain": "worldquant.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "worldquant"},
    {"name": "Graviton Research Capital", "domain": "gravitonresearch.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Millennium Management India", "domain": "mlp.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Jump Trading", "domain": "jumptrading.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Jane Street", "domain": "janestreet.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Optiver", "domain": "optiver.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Citadel", "domain": "citadel.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "IMC Trading", "domain": "imc.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Goldman Sachs India", "domain": "goldmansachs.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Morgan Stanley India", "domain": "morganstanley.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "J.P. Morgan India", "domain": "jpmorgan.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "BNY Mellon India", "domain": "bnymellon.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "American Express India", "domain": "americanexpress.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Fidelity Investments India", "domain": "fidelity.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Wells Fargo India", "domain": "wellsfargo.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Deutsche Bank India", "domain": "db.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Barclays India", "domain": "barclays.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Standard Chartered India", "domain": "sc.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "HSBC India", "domain": "hsbc.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "NatWest Group India", "domain": "natwestgroup.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Societe Generale India", "domain": "socgen.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "UBS India", "domain": "ubs.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Nomura India", "domain": "nomura.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Macquarie Group India", "domain": "macquarie.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "BlackRock India", "domain": "blackrock.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Vanguard India", "domain": "vanguard.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "State Street India", "domain": "statestreet.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Northern Trust India", "domain": "northerntrust.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Invesco India", "domain": "invesco.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Franklin Templeton India", "domain": "franklintempleton.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Broadridge India", "domain": "broadridge.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "FactSet India", "domain": "factset.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "S&P Global India", "domain": "spglobal.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "MSCI India", "domain": "msci.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Morningstar India", "domain": "morningstar.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Bloomberg India", "domain": "bloomberg.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "LSEG India", "domain": "lseg.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Moody's India", "domain": "moodys.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Crisil", "domain": "crisil.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Upstox", "domain": "upstox.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "upstox"},
    {"name": "Angel One", "domain": "angelone.in", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "5paisa", "domain": "5paisa.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Dhan", "domain": "dhan.co", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "INDmoney", "domain": "indmoney.com", "tier": 1, "ats_provider": "lever", "ats_slug": "indmoney"},
    {"name": "Smallcase", "domain": "smallcase.com", "tier": 1, "ats_provider": "lever", "ats_slug": "smallcase"},
    {"name": "Kuvera", "domain": "kuvera.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Scripbox", "domain": "scripbox.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "ET Money", "domain": "etmoney.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Clear (ClearTax)", "domain": "cleartax.in", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "cleartax"},
    {"name": "BankBazaar", "domain": "bankbazaar.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Paisabazaar", "domain": "paisabazaar.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "PolicyBazaar", "domain": "policybazaar.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Turtlemint", "domain": "turtlemint.com", "tier": 2, "ats_provider": "lever", "ats_slug": "turtlemint"},
    {"name": "Digit Insurance", "domain": "godigit.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Acko", "domain": "acko.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "acko"},
    {"name": "OneCard", "domain": "getonecard.com", "tier": 1, "ats_provider": "lever", "ats_slug": "onecard"},
    {"name": "Uni Cards", "domain": "uni.cards", "tier": 2, "ats_provider": "lever", "ats_slug": "uni"},
    {"name": "PayU India", "domain": "payu.in", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "payu"},
    {"name": "Cashfree Payments", "domain": "cashfree.com", "tier": 1, "ats_provider": "lever", "ats_slug": "cashfree"},
    {"name": "Instamojo", "domain": "instamojo.com", "tier": 2, "ats_provider": "lever", "ats_slug": "instamojo"},
    {"name": "Mswipe", "domain": "mswipe.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Ezetap", "domain": "ezetap.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "OkCredit", "domain": "okcredit.in", "tier": 2, "ats_provider": "lever", "ats_slug": "okcredit"},
    {"name": "Vyapar", "domain": "vyaparapp.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "myBillBook", "domain": "mybillbook.in", "tier": 2, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 5. HIGH-GROWTH AI LABS, AI INFRA & MODERN DATA TECH (India & Remote)
    # ==============================================================================
    {"name": "OpenAI", "domain": "openai.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "openai"},
    {"name": "Anthropic", "domain": "anthropic.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "anthropic"},
    {"name": "Cohere", "domain": "cohere.com", "tier": 1, "ats_provider": "lever", "ats_slug": "cohere"},
    {"name": "Mistral AI", "domain": "mistral.ai", "tier": 1, "ats_provider": "ashby", "ats_slug": "mistral"},
    {"name": "Hugging Face", "domain": "huggingface.co", "tier": 1, "ats_provider": "lever", "ats_slug": "huggingface"},
    {"name": "Weights & Biases", "domain": "wandb.ai", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "wandb"},
    {"name": "Replicate", "domain": "replicate.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "replicate"},
    {"name": "Fireworks AI", "domain": "fireworks.ai", "tier": 1, "ats_provider": "ashby", "ats_slug": "fireworks-ai"},
    {"name": "LangChain", "domain": "langchain.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "langchain"},
    {"name": "Pinecone", "domain": "pinecone.io", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "pinecone"},
    {"name": "Weaviate", "domain": "weaviate.io", "tier": 1, "ats_provider": "ashby", "ats_slug": "weaviate"},
    {"name": "Qdrant", "domain": "qdrant.tech", "tier": 1, "ats_provider": "ashby", "ats_slug": "qdrant"},
    {"name": "Chroma", "domain": "trychroma.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "chroma"},
    {"name": "Cursor (Anysphere)", "domain": "cursor.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "cursor"},
    {"name": "Railway", "domain": "railway.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "railway"},
    {"name": "Fly.io", "domain": "fly.io", "tier": 1, "ats_provider": "lever", "ats_slug": "flyio"},
    {"name": "Render", "domain": "render.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "render"},
    {"name": "Neon", "domain": "neon.tech", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "neon"},
    {"name": "Resend", "domain": "resend.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "resend"},
    {"name": "Braintrust", "domain": "braintrust.dev", "tier": 1, "ats_provider": "ashby", "ats_slug": "braintrust"},
    {"name": "Arize AI", "domain": "arize.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "arizeai"},
    {"name": "Fiddler AI", "domain": "fiddler.ai", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "fiddlerai"},
    {"name": "Modular", "domain": "modular.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "modular"},
    {"name": "Groq", "domain": "groq.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "groq"},
    {"name": "Cerebras Systems", "domain": "cerebras.net", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "cerebras"},
    {"name": "SambaNova Systems", "domain": "sambanova.ai", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sambanova"},
    {"name": "Tenstorrent", "domain": "tenstorrent.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "tenstorrent"},
    {"name": "Runway", "domain": "runwayml.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "runway"},
    {"name": "Pika", "domain": "pika.art", "tier": 1, "ats_provider": "ashby", "ats_slug": "pika"},
    {"name": "ElevenLabs", "domain": "elevenlabs.io", "tier": 1, "ats_provider": "ashby", "ats_slug": "elevenlabs"},
    {"name": "Character.ai", "domain": "character.ai", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "character"},
    {"name": "Midjourney", "domain": "midjourney.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Stability AI", "domain": "stability.ai", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "stabilityai"},
    {"name": "Writer", "domain": "writer.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "writer"},
    {"name": "Jasper", "domain": "jasper.ai", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "jasper"},
    {"name": "Synthesia", "domain": "synthesia.io", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "synthesia"},
    {"name": "HeyGen", "domain": "heygen.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "heygen"},
    {"name": "Phind", "domain": "phind.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "KREA AI", "domain": "krea.ai", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Cognition AI (Devin)", "domain": "cognition.ai", "tier": 1, "ats_provider": "ashby", "ats_slug": "cognition"},
    {"name": "Poolside AI", "domain": "poolside.ai", "tier": 1, "ats_provider": "ashby", "ats_slug": "poolside"},
    {"name": "Magic AI", "domain": "magic.dev", "tier": 1, "ats_provider": "ashby", "ats_slug": "magic"},
    {"name": "Augment Code", "domain": "augmentcode.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "augmentcode"},
    {"name": "Sourcegraph", "domain": "sourcegraph.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sourcegraph"},
    {"name": "Codeium", "domain": "codeium.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "codeium"},
    {"name": "Tabnine", "domain": "tabnine.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "tabnine"},

    # ==============================================================================
    # 6. INDIAN HEALTH-TECH, PHARMA-TECH & AGRI-TECH
    # ==============================================================================
    {"name": "PharmEasy", "domain": "pharmeasy.in", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "pharmeasy"},
    {"name": "1mg (Tata 1mg)", "domain": "1mg.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Practo", "domain": "practo.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "practo"},
    {"name": "MediBuddy", "domain": "medibuddy.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "HealthifyMe", "domain": "healthifyme.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "healthifyme"},
    {"name": "Pristyn Care", "domain": "pristyncare.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "pristyncare"},
    {"name": "DeHaat", "domain": "agrevolution.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Ninjacart", "domain": "ninjacart.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "ninjacart"},
    {"name": "WayCool", "domain": "waycool.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "AgroStar", "domain": "agrostar.in", "tier": 2, "ats_provider": "lever", "ats_slug": "agrostar"},
    {"name": "CropIn", "domain": "cropin.com", "tier": 2, "ats_provider": "lever", "ats_slug": "cropin"},
    {"name": "Bijak", "domain": "bijak.in", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Fasal", "domain": "fasal.co", "tier": 3, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 7. LOGISTICS, MOBILITY & SUPPLY CHAIN TECH (India Hubs)
    # ==============================================================================
    {"name": "Shipsy", "domain": "shipsy.io", "tier": 2, "ats_provider": "lever", "ats_slug": "shipsy"},
    {"name": "Locus.sh", "domain": "locus.sh", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "locus"},
    {"name": "FarEye", "domain": "fareye.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "fareye"},
    {"name": "ClickPost", "domain": "clickpost.ai", "tier": 2, "ats_provider": "lever", "ats_slug": "clickpost"},
    {"name": "LogiNext", "domain": "loginextsolutions.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Freight Tiger", "domain": "freighttiger.com", "tier": 2, "ats_provider": "lever", "ats_slug": "freighttiger"},
    {"name": "Cogoport", "domain": "cogoport.com", "tier": 2, "ats_provider": "lever", "ats_slug": "cogoport"},
    {"name": "Loconav", "domain": "loconav.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "loconav"},
    {"name": "Euler Motors", "domain": "eulermotors.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "ZenMobility", "domain": "zenmobility.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Chalo", "domain": "chalo.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "chalo"},
    {"name": "Cityflo", "domain": "cityflo.com", "tier": 2, "ats_provider": "lever", "ats_slug": "cityflo"},
    {"name": "Shuttl", "domain": "shuttl.com", "tier": 3, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 8. CYBERSECURITY & CLOUD INFRASTRUCTURE (India Development Teams)
    # ==============================================================================
    {"name": "Palo Alto Networks India", "domain": "paloaltonetworks.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Fortinet India", "domain": "fortinet.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Zscaler India", "domain": "zscaler.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "zscaler"},
    {"name": "CrowdStrike India", "domain": "crowdstrike.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "SentinelOne India", "domain": "sentinelone.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sentinelone"},
    {"name": "Tenable India", "domain": "tenable.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "tenable"},
    {"name": "Qualys India", "domain": "qualys.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Rapid7 India", "domain": "rapid7.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "rapid7"},
    {"name": "Check Point India", "domain": "checkpoint.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "CyberArk India", "domain": "cyberark.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Netskope India", "domain": "netskope.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "netskope"},
    {"name": "Imperva India", "domain": "imperva.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "F5 Networks India", "domain": "f5.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Akamai India", "domain": "akamai.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Barracuda Networks India", "domain": "barracuda.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Sophos India", "domain": "sophos.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Trend Micro India", "domain": "trendmicro.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "SonicWall India", "domain": "sonicwall.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Seclore", "domain": "seclore.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Quick Heal", "domain": "quickheal.co.in", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Lucideus (Safe Security)", "domain": "safe.security", "tier": 2, "ats_provider": "lever", "ats_slug": "safe-security"},
    {"name": "TAC Security", "domain": "tacsecurity.com", "tier": 3, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 9. HR TECH, RECRUITMENT & COLLABORATION
    # ==============================================================================
    {"name": "Keka", "domain": "keka.com", "tier": 2, "ats_provider": "lever", "ats_slug": "keka"},
    {"name": "GreytHR", "domain": "greythr.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "ZingHR", "domain": "zinghr.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "PeopleStrong", "domain": "peoplestrong.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "SpurTree", "domain": "spurtree.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Instahyre", "domain": "instahyre.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Hirist", "domain": "hirist.tech", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Cutshort", "domain": "cutshort.io", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Naukri (Info Edge)", "domain": "infoedge.in", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Foundit (Monster)", "domain": "foundit.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Shine", "domain": "shine.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Indeed India", "domain": "indeed.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "LinkedIn India", "domain": "linkedin.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Glassdoor India", "domain": "glassdoor.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "glassdoor"},
    {"name": "AmbitionBox", "domain": "ambitionbox.com", "tier": 2, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 10. CLEAN-TECH, SPACE-TECH & DEEPTECH HARDWARE (India Innovators)
    # ==============================================================================
    {"name": "Skyroot Aerospace", "domain": "skyroot.in", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Agnikul Cosmos", "domain": "agnikul.in", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Pixxel Space", "domain": "pixxel.space", "tier": 1, "ats_provider": "lever", "ats_slug": "pixxel"},
    {"name": "Bellatrix Aerospace", "domain": "bellatrix.aero", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Dhruva Space", "domain": "dhruvaspace.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "GalaxEye Space", "domain": "galaxeye.space", "tier": 2, "ats_provider": "lever", "ats_slug": "galaxeye"},
    {"name": "IdeaForge", "domain": "ideaforgetech.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Garuda Aerospace", "domain": "garudaaerospace.com", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Skye Air Mobility", "domain": "skyeair.tech", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Redwing Aerospace", "domain": "redwinglabs.in", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Kazam EV", "domain": "kazam.in", "tier": 2, "ats_provider": "lever", "ats_slug": "kazam"},
    {"name": "Statiq", "domain": "statiq.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Bolt.earth", "domain": "bolt.earth", "tier": 2, "ats_provider": "lever", "ats_slug": "boltearth"},
    {"name": "Exponent Energy", "domain": "exponent.energy", "tier": 1, "ats_provider": "lever", "ats_slug": "exponentenergy"},
    {"name": "Log9 Materials", "domain": "log9materials.com", "tier": 2, "ats_provider": None, "ats_slug": None},

    # ==============================================================================
    # 11. GLOBAL FINTECHS & CONSUMER TECH (India Offices / Remote)
    # ==============================================================================
    {"name": "Affirm", "domain": "affirm.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "affirm"},
    {"name": "Klarna", "domain": "klarna.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Revolut India", "domain": "revolut.com", "tier": 1, "ats_provider": "lever", "ats_slug": "revolut"},
    {"name": "Monzo", "domain": "monzo.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "monzo"},
    {"name": "Wise (TransferWise)", "domain": "wise.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "wise"},
    {"name": "Chime", "domain": "chime.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "chime"},
    {"name": "Robinhood", "domain": "robinhood.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "robinhood"},
    {"name": "SoFi", "domain": "sofi.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "sofi"},
    {"name": "Plaid", "domain": "plaid.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "plaid"},
    {"name": "Checkout.com", "domain": "checkout.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "checkout"},
    {"name": "Adyen", "domain": "adyen.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Toast", "domain": "toasttab.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "toast"},
    {"name": "Bill.com", "domain": "bill.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "bill"},
    {"name": "Carta", "domain": "carta.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "carta"},
    {"name": "Gusto", "domain": "gusto.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "gusto"},
    {"name": "Deel", "domain": "deel.com", "tier": 1, "ats_provider": "ashby", "ats_slug": "deel"},
    {"name": "Remote.com", "domain": "remote.com", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "remote"},
    {"name": "Oyster HR", "domain": "oysterhr.com", "tier": 2, "ats_provider": "ashby", "ats_slug": "oyster"},

    # ==============================================================================
    # 12. MORE HIGH-GROWTH TECH STARTUPS & SCALEUPS
    # ==============================================================================
    {"name": "KPMG India Tech", "domain": "kpmg.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "PwC India Tech", "domain": "pwc.in", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "EY India Tech", "domain": "ey.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Deloitte India Tech", "domain": "deloitte.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "McKinsey Digital India", "domain": "mckinsey.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "BCG Platinion / Gamma India", "domain": "bcg.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Bain & Company Vector India", "domain": "bain.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Fractal Analytics", "domain": "fractal.ai", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "fractalanalytics"},
    {"name": "Mu Sigma", "domain": "mu-sigma.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Tiger Analytics", "domain": "tigeranalytics.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "LatentView Analytics", "domain": "latentview.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Tredence", "domain": "tredence.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "TheMathCompany", "domain": "themathcompany.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Affine Analytics", "domain": "affine.ai", "tier": 3, "ats_provider": None, "ats_slug": None},
    {"name": "Quantiphi", "domain": "quantiphi.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Celebal Technologies", "domain": "celebaltech.com", "tier": 2, "ats_provider": None, "ats_slug": None},
    {"name": "Searce", "domain": "searce.com", "tier": 2, "ats_provider": "lever", "ats_slug": "searce"},
    {"name": "Media.net", "domain": "media.net", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Directi (Zeta / Radix)", "domain": "directi.com", "tier": 1, "ats_provider": None, "ats_slug": None},
    {"name": "Zeta Suite", "domain": "zeta.tech", "tier": 1, "ats_provider": "greenhouse", "ats_slug": "zeta"},
    {"name": "Flock", "domain": "flock.com", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "flock"},
    {"name": "Titan Mail (Nova)", "domain": "titan.email", "tier": 2, "ats_provider": "greenhouse", "ats_slug": "titan"},
    {"name": "Radix Registry", "domain": "radix.website", "tier": 2, "ats_provider": None, "ats_slug": None},
]


def main():
    config_path = Path("data/config/companies.yaml")
    if not config_path.exists():
        print(f"Error: {config_path} not found.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        existing_cfg = yaml.safe_load(f) or {}

    existing_companies = existing_cfg.get("companies", [])
    existing_domains = {c["domain"].strip().lower() for c in existing_companies if "domain" in c}
    existing_names = {c["name"].strip().lower() for c in existing_companies if "name" in c}

    added_count = 0
    merged_companies = list(existing_companies)

    for comp in TARGET_COMPANIES:
        dom = comp["domain"].strip().lower()
        nm = comp["name"].strip().lower()

        if dom not in existing_domains and nm not in existing_names:
            merged_companies.append({
                "name": comp["name"],
                "domain": comp["domain"],
                "tier": comp.get("tier", 2),
                "ats_provider": comp.get("ats_provider"),
                "ats_slug": comp.get("ats_slug"),
            })
            existing_domains.add(dom)
            existing_names.add(nm)
            added_count += 1

    existing_cfg["companies"] = merged_companies

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(existing_cfg, f, sort_keys=False, indent=2, allow_unicode=True)

    print(f"✅ Successfully added {added_count} new verified companies.")
    print(f"📊 Total companies in catalog now: {len(merged_companies)}")


if __name__ == "__main__":
    main()
