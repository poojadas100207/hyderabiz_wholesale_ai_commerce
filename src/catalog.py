"""E-Commerce Product Catalog with realistic products, specs, price history, and reviews."""

from typing import List, Dict, Any, Optional
from datetime import datetime

# Curated High-Definition Product Image URLs from Unsplash
CATALOG_DATA: List[Dict[str, Any]] = [
    {
        "id": "PROD-101",
        "title": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
        "brand": "Sony",
        "category": "Audio & Headphones",
        "price": 348.00,
        "original_price": 399.99,
        "currency": "USD",
        "rating": 4.6,
        "review_count": 3420,
        "stock": 24,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=600&q=80",
        "description": "Industry-leading noise canceling with two processors and 8 microphones. Up to 30 hours of battery life with ultra-comfortable, lightweight design.",
        "specs": {
            "Battery Life": "30 Hours (ANC On)",
            "Weight": "250g",
            "Connectivity": "Bluetooth 5.2 / 3.5mm Aux",
            "Charging": "USB-C Fast Charging (3 min = 3 hours)",
            "Codecs": "LDAC, AAC, SBC",
            "Microphones": "8 Beamforming Mics"
        },
        "tags": ["noise canceling", "anc", "wireless", "over-ear", "travel", "commute", "sony", "audiophile", "bluetooth"],
        "price_history": [
            {"date": "2026-07-01", "price": 399.99},
            {"date": "2026-08-15", "price": 379.99},
            {"date": "2026-09-20", "price": 368.00},
            {"date": "2026-10-18", "price": 348.00}
        ],
        "reviews": [
            {
                "review_id": "REV-101-1",
                "author": "Marcus V.",
                "rating": 5,
                "date": "2026-10-02",
                "verified_purchase": True,
                "title": "Best ANC for transatlantic flights",
                "pros": "Unreal noise cancellation, plush ear cups, auto-pause works like magic",
                "cons": "Does not fold into a tiny ball like the XM4 did",
                "text": "I fly twice a month for business. The XM5 completely deletes engine roar. Soundstage is warm and punchy, and the microphone clarity on Zoom calls is a huge upgrade over the XM4."
            },
            {
                "review_id": "REV-101-2",
                "author": "Elena R.",
                "rating": 4,
                "date": "2026-09-14",
                "verified_purchase": True,
                "title": "Super comfortable, but headband is slightly narrow",
                "pros": "Lightweight, LDAC audio quality is stellar, exceptional battery",
                "cons": "Case is bulky, headband can create a small pressure point after 4 hours",
                "text": "Sound is top notch. The touch controls take an hour to get used to, but then become second nature. If you have a larger head, try them on first."
            },
            {
                "review_id": "REV-101-3",
                "author": "David K.",
                "rating": 3,
                "date": "2026-08-29",
                "verified_purchase": True,
                "title": "Great sound, but case doesn't fit in small backpacks",
                "pros": "Audio fidelity and call quality",
                "cons": "No folding hinges makes the case larger than older generation",
                "text": "They sound incredible, but Sony took away the foldable hinge. Still, ANC is unbeatable."
            }
        ]
    },
    {
        "id": "PROD-102",
        "title": "Bose QuietComfort Ultra Headphones",
        "brand": "Bose",
        "category": "Audio & Headphones",
        "price": 379.00,
        "original_price": 429.00,
        "currency": "USD",
        "rating": 4.7,
        "review_count": 2180,
        "stock": 18,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
        "description": "World-class noise cancellation, breakthrough spatialized audio for immersive listening, and custom sound tailored to your ear shape.",
        "specs": {
            "Battery Life": "24 Hours (Immersive Audio Off)",
            "Weight": "252g",
            "Connectivity": "Bluetooth 5.3 Multipoint",
            "Foldable": "Yes, folds flat and compact",
            "Spatial Audio": "Bose Immersive Audio Mode",
            "Charging": "USB-C"
        },
        "tags": ["bose", "comfort", "anc", "spatial audio", "travel", "foldable", "over-ear", "wireless"],
        "price_history": [
            {"date": "2026-07-10", "price": 429.00},
            {"date": "2026-08-25", "price": 409.00},
            {"date": "2026-09-30", "price": 399.00},
            {"date": "2026-10-15", "price": 379.00}
        ],
        "reviews": [
            {
                "review_id": "REV-102-1",
                "author": "Sarah Jenkins",
                "rating": 5,
                "date": "2026-09-28",
                "verified_purchase": True,
                "title": "The comfort king still wears the crown",
                "pros": "Unmatched comfort, folds into a compact case, Bose Immersive audio is brilliant",
                "cons": "Battery life is 24h vs Sony's 30h",
                "text": "I can wear these for an entire 8-hour workday with zero fatigue. The spatial audio mode makes acoustic tracks sound like you're sitting in a private studio."
            },
            {
                "review_id": "REV-102-2",
                "author": "Kenji T.",
                "rating": 4,
                "date": "2026-09-02",
                "verified_purchase": True,
                "title": "Better folding design than Sony XM5",
                "pros": "Travel friendly, physical volume slider is responsive, crisp vocal clarity",
                "cons": "Bose Music app occasionally takes a moment to sync",
                "text": "I chose these over the Sony XM5 because Bose kept the folding hinges. ANC is virtually identical to Sony, comfort is slightly better."
            }
        ]
    },
    {
        "id": "PROD-103",
        "title": "Anker Soundcore Space Q45 ANC Headphones",
        "brand": "Anker",
        "category": "Audio & Headphones",
        "price": 99.99,
        "original_price": 149.99,
        "currency": "USD",
        "rating": 4.4,
        "review_count": 5120,
        "stock": 45,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=600&q=80",
        "description": "Adaptive noise canceling with up to 98% noise reduction. Incredible 50-hour battery life with ANC on, LDAC hi-res wireless sound.",
        "specs": {
            "Battery Life": "50 Hours (ANC on) / 65 Hours (ANC off)",
            "Weight": "292g",
            "Connectivity": "Bluetooth 5.3 Multipoint / Aux",
            "Value Tier": "Best Budget Flagship Killer",
            "App Support": "Soundcore App with 22 EQ presets"
        },
        "tags": ["budget", "value", "anker", "soundcore", "long battery", "anc", "travel", "sub 100"],
        "price_history": [
            {"date": "2026-07-01", "price": 149.99},
            {"date": "2026-08-10", "price": 129.99},
            {"date": "2026-09-15", "price": 119.99},
            {"date": "2026-10-10", "price": 99.99}
        ],
        "reviews": [
            {
                "review_id": "REV-103-1",
                "author": "Brian P.",
                "rating": 5,
                "date": "2026-10-12",
                "verified_purchase": True,
                "title": "85% of Sony performance at 25% of the price",
                "pros": "Insane 50h battery, comfortable padding, app EQ is deep",
                "cons": "Microphone in windy conditions is average",
                "text": "For under $100, these are ridiculous value. I charged them 3 weeks ago and still have 40% battery left. ANC handles coffee shop murmur easily."
            }
        ]
    },
    {
        "id": "PROD-201",
        "title": "Apple MacBook Air 15-inch (M3 Chip, 16GB RAM, 512GB SSD)",
        "brand": "Apple",
        "category": "Laptops & Computers",
        "price": 1399.00,
        "original_price": 1499.00,
        "currency": "USD",
        "rating": 4.9,
        "review_count": 1890,
        "stock": 14,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "description": "Strikingly thin design with the lightning-fast M3 chip. 15.3-inch Liquid Retina display, 18-hour battery life, and silent fanless operation.",
        "specs": {
            "Processor": "Apple M3 8-core CPU / 10-core GPU",
            "Memory": "16GB Unified RAM",
            "Storage": "512GB High-speed SSD",
            "Display": "15.3-inch Liquid Retina Display (500 nits)",
            "Battery": "Up to 18 Hours",
            "Weight": "1.51 kg (3.3 lbs)",
            "Ports": "MagSafe 3, 2x Thunderbolt / USB 4, Headphone Jack"
        },
        "tags": ["laptop", "macbook", "apple", "m3", "productivity", "students", "programming", "ultrabook", "15-inch"],
        "price_history": [
            {"date": "2026-07-01", "price": 1499.00},
            {"date": "2026-08-20", "price": 1449.00},
            {"date": "2026-09-15", "price": 1419.00},
            {"date": "2026-10-12", "price": 1399.00}
        ],
        "reviews": [
            {
                "review_id": "REV-201-1",
                "author": "Chloe S.",
                "rating": 5,
                "date": "2026-10-05",
                "verified_purchase": True,
                "title": "The sweet spot of screen size and portability",
                "pros": "Zero fan noise, all-day real world battery, gorgeous bright display",
                "cons": "Only two USB-C ports on one side",
                "text": "Moving from a 13-inch to this 15-inch felt like a giant upgrade without any penalty in weight. 16GB unified memory handles Docker, VS Code, and dozens of tabs without flinching."
            },
            {
                "review_id": "REV-201-2",
                "author": "Liam G.",
                "rating": 5,
                "date": "2026-09-18",
                "verified_purchase": True,
                "title": "Battery is truly 16+ hours",
                "pros": "Battery life, build quality, speakers sound shockingly full",
                "cons": "Midnight color still attracts some fingerprints",
                "text": "Best everyday laptop on the market. Left charger at home for a 2-day conference and returned with 28% battery."
            }
        ]
    },
    {
        "id": "PROD-202",
        "title": "Dell XPS 14 Core Ultra 7 (32GB RAM, 1TB SSD, RTX 4050)",
        "brand": "Dell",
        "category": "Laptops & Computers",
        "price": 1749.00,
        "original_price": 1999.00,
        "currency": "USD",
        "rating": 4.5,
        "review_count": 870,
        "stock": 9,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=600&q=80",
        "description": "Futuristic CNC aluminum design, seamless glass touchpad, 3.2K OLED display option, and dedicated NVIDIA GeForce RTX graphics for creators.",
        "specs": {
            "Processor": "Intel Core Ultra 7 155H (16 cores)",
            "Memory": "32GB LPDDR5x",
            "Storage": "1TB PCIe NVMe SSD",
            "Graphics": "NVIDIA GeForce RTX 4050 6GB GDDR6",
            "Display": "14.5-inch 3.2K OLED Touch (120Hz)",
            "Weight": "1.68 kg"
        },
        "tags": ["dell", "xps", "windows", "oled", "creative", "video editing", "rtx", "intel", "premium laptop"],
        "price_history": [
            {"date": "2026-07-01", "price": 1999.00},
            {"date": "2026-08-15", "price": 1899.00},
            {"date": "2026-09-22", "price": 1820.00},
            {"date": "2026-10-14", "price": 1749.00}
        ],
        "reviews": [
            {
                "review_id": "REV-202-1",
                "author": "Carlos M.",
                "rating": 4,
                "date": "2026-09-25",
                "verified_purchase": True,
                "title": "OLED screen is breathtaking for Premiere Pro",
                "pros": "OLED color accuracy, compact footprint, capable RTX GPU",
                "cons": "Capacitive function row takes getting used to",
                "text": "The display is one of the best I have ever witnessed on a laptop. Renders 4K video smoothly. Thermals are controlled well under heavy load."
            }
        ]
    },
    {
        "id": "PROD-301",
        "title": "Nike Air Zoom Pegasus 41 Road Running Shoes",
        "brand": "Nike",
        "category": "Footwear & Apparel",
        "price": 112.00,
        "original_price": 140.00,
        "currency": "USD",
        "rating": 4.7,
        "review_count": 4210,
        "stock": 35,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
        "description": "Responsive daily road running shoes with upgraded dual Air Zoom units and ReactX foam midsole for 13% more energy return.",
        "specs": {
            "Midsole Foam": "Nike ReactX Foam + Forefoot & Heel Air Zoom",
            "Drop": "10mm",
            "Weight": "297g (Men's US 10)",
            "Terrain": "Road, Pavement, Treadmill",
            "Arch Support": "Neutral",
            "Available Sizes": "US 7 - US 13"
        },
        "tags": ["running", "shoes", "sneakers", "nike", "fitness", "daily trainer", "marathon", "cushioning", "sub 120"],
        "price_history": [
            {"date": "2026-07-01", "price": 140.00},
            {"date": "2026-08-10", "price": 130.00},
            {"date": "2026-09-18", "price": 122.00},
            {"date": "2026-10-16", "price": 112.00}
        ],
        "reviews": [
            {
                "review_id": "REV-301-1",
                "author": "Jason W.",
                "rating": 5,
                "date": "2026-10-09",
                "verified_purchase": True,
                "title": "Best daily trainer Nike has made in 5 years",
                "pros": "ReactX foam is noticeably springier, durable waffle outsole, true to size",
                "cons": "A bit warm in extreme summer heat",
                "text": "Logged 120 miles in these over 3 weeks. The ReactX foam gives a plush landing without feeling mushy. Knee pain is completely gone."
            },
            {
                "review_id": "REV-301-2",
                "author": "Samantha B.",
                "rating": 4,
                "date": "2026-09-20",
                "verified_purchase": True,
                "title": "Great shoe, consider half size up if you have wide feet",
                "pros": "Good arch support, snappy toe-off",
                "cons": "Toe box is slightly snug for wide feet",
                "text": "Solid workhorse running shoe. If you have wide feet, order half size up or pick the Wide version."
            }
        ]
    },
    {
        "id": "PROD-302",
        "title": "Hoka Clifton 9 Lightweight Running & Walking Shoes",
        "brand": "Hoka",
        "category": "Footwear & Apparel",
        "price": 145.00,
        "original_price": 145.00,
        "currency": "USD",
        "rating": 4.8,
        "review_count": 6800,
        "stock": 28,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=600&q=80",
        "description": "Maximalist lightweight cushioning designed for long distance runs and 12-hour hospital shifts. Plush collar and engineered knit upper.",
        "specs": {
            "Cushioning": "Maximal EVA Foam",
            "Weight": "248g (Men's US 9)",
            "Heel-to-Toe Drop": "5mm",
            "Orthopedic Seal": "APMA Accepted (American Podiatric Medical Association)",
            "Best For": "Everyday Run, Walking, Nurses, Standing all day"
        },
        "tags": ["hoka", "cushion", "orthopedic", "walking", "running", "nurses", "plush", "joint friendly", "sneakers"],
        "price_history": [
            {"date": "2026-07-01", "price": 145.00},
            {"date": "2026-08-01", "price": 145.00},
            {"date": "2026-09-01", "price": 145.00},
            {"date": "2026-10-01", "price": 145.00}
        ],
        "reviews": [
            {
                "review_id": "REV-302-1",
                "author": "Nurse Danielle",
                "rating": 5,
                "date": "2026-10-01",
                "verified_purchase": True,
                "title": "Saved my back during 12-hour ICU shifts",
                "pros": "Like walking on clouds, zero plantar fasciitis flareups, breathable",
                "cons": "Price rarely drops on sale",
                "text": "These are the gold standard for anyone standing all day. My feet and lower back feel great after a grueling day on the floor."
            }
        ]
    },
    {
        "id": "PROD-303",
        "title": "Patagonia Torrentshell 3L Waterproof Rain Jacket",
        "brand": "Patagonia",
        "category": "Footwear & Apparel",
        "price": 149.00,
        "original_price": 179.00,
        "currency": "USD",
        "rating": 4.8,
        "review_count": 2940,
        "stock": 20,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1548883354-7622d03aca27?auto=format&fit=crop&w=600&q=80",
        "description": "3-layer H2No Performance Standard shell for exceptional waterproof/breathable performance, all-day comfort and long-lasting waterproof durability. 100% recycled nylon.",
        "specs": {
            "Material": "100% Recycled ECONYL Waterproof Nylon",
            "Membrane": "3-Layer H2No Performance Standard",
            "Weight": "400g",
            "Eco Credentials": "Fair Trade Certified, PFC-free DWR",
            "Pit Zips": "Yes, two-way venting pit zips"
        },
        "tags": ["patagonia", "jacket", "waterproof", "raincoat", "hiking", "outdoors", "eco-friendly", "sustainable"],
        "price_history": [
            {"date": "2026-07-01", "price": 179.00},
            {"date": "2026-08-15", "price": 169.00},
            {"date": "2026-09-25", "price": 159.00},
            {"date": "2026-10-15", "price": 149.00}
        ],
        "reviews": [
            {
                "review_id": "REV-303-1",
                "author": "Tobias K.",
                "rating": 5,
                "date": "2026-09-29",
                "verified_purchase": True,
                "title": "Surviving torrential Pacific Northwest storms dry",
                "pros": "100% waterproof, sturdy 3-layer construction, pit zips prevent sweat buildup",
                "cons": "Material is a bit crinkly when brand new",
                "text": "Got caught in a 3-hour storm on Mount Rainier. T-shirt underneath was bone dry. Patagonia warranty guarantees this for life."
            }
        ]
    },
    {
        "id": "PROD-401",
        "title": "Breville Barista Touch Impress Espresso Machine",
        "brand": "Breville",
        "category": "Kitchen & Home",
        "price": 1299.95,
        "original_price": 1499.95,
        "currency": "USD",
        "rating": 4.7,
        "review_count": 1450,
        "stock": 8,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=600&q=80",
        "description": "Step-by-step barista guidance with real-time feedback. Impress Puck System delivers assisted manual tamping with a 7-degree barista twist and 10kg precision.",
        "specs": {
            "Heating System": "ThermoJet 3-second instant heat up",
            "Grinder": "Baratza European Precision Burrs with 30 grind settings",
            "Milk Frothing": "Auto MilQ with settings for Dairy, Oat, Almond, and Soy",
            "Screen": "Color Touchscreen with custom drink presets",
            "Water Tank": "2.0 Liters (67 fl oz)"
        },
        "tags": ["coffee", "espresso", "breville", "kitchen", "latte", "cappuccino", "barista", "luxury", "home cafe"],
        "price_history": [
            {"date": "2026-07-01", "price": 1499.95},
            {"date": "2026-08-20", "price": 1449.00},
            {"date": "2026-09-10", "price": 1399.00},
            {"date": "2026-10-12", "price": 1299.95}
        ],
        "reviews": [
            {
                "review_id": "REV-401-1",
                "author": "Matteo B.",
                "rating": 5,
                "date": "2026-10-10",
                "verified_purchase": True,
                "title": "Cafe quality lattes in under 2 minutes",
                "pros": "Assisted tamping leaves zero mess, auto milk frother produces silky microfoam for oat milk",
                "cons": "Requires regular descaling and filter changes",
                "text": "The assisted tamper is a game changer. No espresso powder flying all over the counter. My morning flat white tastes better than the cafe down the street."
            }
        ]
    },
    {
        "id": "PROD-402",
        "title": "Ninja Foodi 10-in-1 XL Pro Air Fry Oven",
        "brand": "Ninja",
        "category": "Kitchen & Home",
        "price": 229.99,
        "original_price": 299.99,
        "currency": "USD",
        "rating": 4.6,
        "review_count": 8920,
        "stock": 30,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1584269600519-112d071b35e6?auto=format&fit=crop&w=600&q=80",
        "description": "True Surround Convection with up to 10X the convection power of a traditional oven. Air fry, roast, whole roast, bake, dehydrate, and broil with 2-level cooking.",
        "specs": {
            "Capacity": "Fits a 12-lb turkey or two 12-inch pizzas",
            "Functions": "10-in-1 (Air Fry, Roast, Broil, Bake, Toast, Dehydrate, Reheat)",
            "Power": "1800 Watts",
            "Heating": "Surround Convection Airflow",
            "Dimensions": "17.09 x 20.22 x 13.34 inches"
        },
        "tags": ["ninja", "air fryer", "oven", "kitchen", "cooking", "meal prep", "family", "countertop", "sub 250"],
        "price_history": [
            {"date": "2026-07-01", "price": 299.99},
            {"date": "2026-08-10", "price": 269.99},
            {"date": "2026-09-15", "price": 249.99},
            {"date": "2026-10-05", "price": 229.99}
        ],
        "reviews": [
            {
                "review_id": "REV-402-1",
                "author": "Rebecca L.",
                "rating": 5,
                "date": "2026-09-22",
                "verified_purchase": True,
                "title": "Replaced my main oven entirely",
                "pros": "Heats up in 90 seconds, makes chicken wings super crispy without oil, fits 2 sheet pans",
                "cons": "Takes up meaningful counter real estate",
                "text": "We haven't turned on our large oven in 4 months. Crispy fries, salmon, roasted vegetables, and homemade sourdough all cook faster and taste better."
            }
        ]
    },
    {
        "id": "PROD-501",
        "title": "Dyson V12 Detect Slim Cordless Vacuum Cleaner",
        "brand": "Dyson",
        "category": "Smart Home & Cleaning",
        "price": 549.99,
        "original_price": 649.99,
        "currency": "USD",
        "rating": 4.6,
        "review_count": 3120,
        "stock": 16,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1558317374-067fb5f30001?auto=format&fit=crop&w=600&q=80",
        "description": "Dyson's lightest intelligent cordless vacuum. Fluffy Optic cleaner head reveals invisible dust on hard floors, piezo sensor measures microscopic particles.",
        "specs": {
            "Weight": "2.2 kg (5.2 lbs) - Dyson's lightest full-power vacuum",
            "Suction Power": "150 AW",
            "Run Time": "Up to 60 Minutes",
            "Laser Technology": "Illuminates invisible dust on wood/tile",
            "Bin Volume": "0.1 Gallon with no-touch hygienic ejection",
            "Switch": "Single-button power control (no trigger hold needed)"
        },
        "tags": ["dyson", "vacuum", "cleaning", "cordless", "lightweight", "pet hair", "smart home", "laser"],
        "price_history": [
            {"date": "2026-07-01", "price": 649.99},
            {"date": "2026-08-20", "price": 599.99},
            {"date": "2026-09-25", "price": 579.99},
            {"date": "2026-10-14", "price": 549.99}
        ],
        "reviews": [
            {
                "review_id": "REV-501-1",
                "author": "Gregory T.",
                "rating": 5,
                "date": "2026-10-04",
                "verified_purchase": True,
                "title": "The green illumination laser is both gross and addictive",
                "pros": "Push button on/off (no finger fatigue), lightweight, green laser shows every pet hair",
                "cons": "Bin is on the smaller side, need to empty every 2-3 rooms if you have 2 dogs",
                "text": "The push button switch is so much better than the old trigger model. The green light shows dirt you can't see with regular lights on. Essential if you have hardwood floors."
            },
            {
                "review_id": "REV-501-2",
                "author": "Hannah M.",
                "rating": 4,
                "date": "2026-09-11",
                "verified_purchase": True,
                "title": "Great suction, wish the canister was 20% larger",
                "pros": "Maneuverability, battery indicator with countdown minutes",
                "cons": "Dust canister fills quickly with heavy shedding pets",
                "text": "Wonderful machine for apartments and medium homes. For massive multi-level homes with heavy carpet, consider the V15 instead."
            }
        ]
    },
    {
        "id": "PROD-502",
        "title": "Kindle Paperwhite Signature Edition (32GB, Wireless Charging)",
        "brand": "Amazon",
        "category": "Electronics & Gadgets",
        "price": 149.99,
        "original_price": 189.99,
        "currency": "USD",
        "rating": 4.8,
        "review_count": 14200,
        "stock": 50,
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
        "description": "6.8-inch glare-free display with adjustable warm light, auto-adjusting light sensors, 32GB storage, and wireless Qi charging. Weeks of battery life.",
        "specs": {
            "Display": "6.8-inch Paperwhite E-ink display (300 ppi)",
            "Storage": "32 GB (Thousands of books/audiobooks)",
            "Battery": "Up to 10 Weeks on a single charge",
            "Waterproofing": "IPX8 (Waterproof in up to 2m fresh water)",
            "Lighting": "Adjustable Warm Light & Auto-brightness"
        },
        "tags": ["kindle", "ereader", "books", "reading", "waterproof", "battery life", "glare-free", "sub 150"],
        "price_history": [
            {"date": "2026-07-01", "price": 189.99},
            {"date": "2026-08-01", "price": 179.99},
            {"date": "2026-09-10", "price": 164.99},
            {"date": "2026-10-18", "price": 149.99}
        ],
        "reviews": [
            {
                "review_id": "REV-502-1",
                "author": "Samantha Claire",
                "rating": 5,
                "date": "2026-10-14",
                "verified_purchase": True,
                "title": "Warm light makes bedtime reading effortless",
                "pros": "Warm amber backlight is easy on eyes, waterproof for the bath, battery lasts forever",
                "cons": "No physical page-turn buttons",
                "text": "I read 30+ books a year. The warm light adjustment completely eliminated eyestrain before sleeping. Dropped it into the bathtub once, dried off, perfectly fine."
            }
        ]
    }
]


def get_all_products() -> List[Dict[str, Any]]:
    """Return all products in the catalog."""
    return CATALOG_DATA


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Lookup product by ID or title substring."""
    clean_id = product_id.strip().upper()
    for p in CATALOG_DATA:
        if p["id"].upper() == clean_id:
            return p
    # Fuzzy match on title or ID
    for p in CATALOG_DATA:
        if clean_id in p["id"].upper() or clean_id in p["title"].upper():
            return p
    return None


def get_categories() -> List[str]:
    """Return distinct categories available."""
    return sorted(list({p["category"] for p in CATALOG_DATA}))


def get_brands() -> List[str]:
    """Return distinct brands available."""
    return sorted(list({p["brand"] for p in CATALOG_DATA}))


def search_products(
    query: str = "",
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "relevance",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search and filter product catalog with multi-attribute filtering."""
    results = CATALOG_DATA.copy()

    # Category Filter
    if category and category.lower() != "all":
        results = [p for p in results if p["category"].lower() == category.lower()]

    # Brand Filter
    if brand and brand.lower() != "all":
        results = [p for p in results if p["brand"].lower() == brand.lower()]

    # Price Filter
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]

    # Rating Filter
    if min_rating is not None:
        results = [p for p in results if p["rating"] >= min_rating]

    # Text Query Matching
    if query and query.strip():
        q_tokens = [tok.lower().strip() for tok in query.split() if len(tok.strip()) > 1]
        
        def match_score(product: Dict[str, Any]) -> int:
            score = 0
            title = product["title"].lower()
            desc = product["description"].lower()
            tags = [t.lower() for t in product["tags"]]
            brand = product["brand"].lower()
            category = product["category"].lower()

            for token in q_tokens:
                if token in title:
                    score += 5
                if token in brand:
                    score += 4
                if any(token in tag for tag in tags):
                    score += 3
                if token in category:
                    score += 2
                if token in desc:
                    score += 1
            return score

        scored_results = []
        for p in results:
            s = match_score(p)
            if s > 0 or not q_tokens:
                scored_results.append((s, p))
        
        # Sort primarily by query relevance score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored_results]

    # Sorting
    if sort_by == "price_asc":
        results.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        results.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        results.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "popularity":
        results.sort(key=lambda x: x["review_count"], reverse=True)

    return results[:limit]


def update_product_price(product_id: str, new_price: float) -> Optional[Dict[str, Any]]:
    """Update product price dynamically to simulate price changes and trigger price drop alerts."""
    product = get_product_by_id(product_id)
    if product:
        old_price = product["price"]
        product["price"] = round(new_price, 2)
        product["price_history"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "price": round(new_price, 2),
            "simulated": True
        })
        return {
            "product": product,
            "old_price": old_price,
            "new_price": product["price"],
            "difference": round(product["price"] - old_price, 2)
        }
    return None
