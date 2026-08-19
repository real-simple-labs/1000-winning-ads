"""Brand to niche mapping for the swipe file sidebar and filters."""

CATEGORIES = {
    "Supplements & Wellness": [
        "AG1", "ARMRA", "Alice Mushrooms", "Ancient Nutrition", "Arrae", "Auri Nutrition",
        "Beam", "Bioma", "Bloom Nutrition", "Create Wellness", "Cymbiotika", "David Protein",
        "Dr. Anna Cabeca", "Everyday Dose", "Four Sigmatic", "Function Health", "Garden of Life",
        "Goli", "Grüns", "Happy Mammoth", "Hone Health", "IM8", "Ka'Chava", "Kindra",
        "Laird Superfood", "Legion Athletics", "Lemme", "LMNT", "Magic Mind",
        "Midi Health", "Momentous", "Moon Juice", "MUD\\WTR", "Needed", "Norse Organics",
        "Nutrafol", "O Positiv", "OLLY", "Obvi Health", "Onnit", "Pendulum", "Perelel",
        "Primal Queen", "RYZE Superfoods", "Ritual", "Seed", "Serene Herbs", "SmartyPants Vitamins",
        "Space Goods", "Thesis", "Thorne", "Timeline Longevity", "Transparent Labs",
        "Try BRĒZ", "Vital Proteins", "Mars Men",
    ],
    "Beauty & Skincare": [
        "Billie", "Curology", "Drunk Elephant", "Glossier", "Glow Recipe", "Hero Cosmetics",
        "IL MAKIAGE", "ILIA", "Jones Road Beauty", "Kosas", "Laura Geller", "Merit",
        "Milk Makeup", "Naturium", "Nécessaire", "OSEA", "Paula's Choice", "Quasi",
        "Rare Beauty", "Rhode", "Saie", "Sol de Janeiro", "Starface",
        "Summer Fridays", "Supergoop", "Tatcha", "The Ordinary", "Vacation",
        "Youth To The People", "e.l.f. Cosmetics",
    ],
    "Haircare": [
        "Crown Affair", "Divi", "K18", "Living Proof", "OUAI", "Olaplex", "Prose",
        "Vegamour", "amika",
    ],
    "Food & Snacks": [
        "Banza", "Brightland", "Catalina Crunch", "Chomps", "Graza", "Kodiak Cakes",
        "Huel", "Magic Spoon", "RXBAR", "Serenity Kids", "SkinnyPop", "Thrive Market",
    ],
    "Drinks": [
        "Athletic Brewing", "Ghia", "HOP WTR", "OLIPOP", "Poppi",
    ],
    "Apparel": [
        "Alo Yoga", "Aritzia", "Bombas", "Buck Mason", "Cuts Clothing", "Fabletics",
        "Gymshark", "Knix", "Mack Weldon", "Marine Layer", "MeUndies", "Outdoor Voices",
        "Rhone", "Ten Thousand", "Tommy John", "True Classic", "Vuori",
    ],
    "Footwear & Bags": [
        "Allbirds", "Beis", "Cariuma", "HIKE Footwear", "Kizik", "Rothy's", "Vessi",
    ],
    "Home & Kitchen": [
        "Blueland", "Boll & Branch", "Brooklinen", "Buffy", "Caraway", "Cozy Earth",
        "Earth Breeze", "Grove Collaborative", "Hedley & Bennett", "HexClad",
        "Made In Cookware", "Our Place", "Public Goods", "Quince", "Ruggable",
        "The Ridge", "Uncommon Goods",
    ],
    "Pets": [
        "BarkBox", "Chewy", "Native Pet", "Ollie", "PetLab Co.", "Pet Honesty", "The Farmer's Dog",
        "Wild One", "Zesty Paws",
    ],
    "Baby & Kids": [
        "Coterie", "Hello Bello", "Hiya", "Lovevery", "Momcozy", "Owlet",
        "The Honest Company",
    ],
    "Oral & Personal Care": [
        "Bite", "Boka", "Carpe", "Dr. Squatch", "HiSmile", "Harry's", "Lume Deodorant",
        "Lumineux", "Manscaped", "Native", "Salt & Stone", "Wild", "quip",
    ],
    "Sleep, Fitness & Recovery": [
        "Casper", "Hatch", "Helix Sleep", "Hyperice", "Nectar Sleep", "Oura", "Purple",
        "Therabody", "Tonal", "WHOOP",
    ],
    "Health & Telehealth": [
        "Hers", "Hims", "Maude", "Ro",
    ],
    "Eyewear": [
        "Warby Parker", "Zenni Optical",
    ],
    "Media & Other": [
        "Flakes", "The Quality Edit",
    ],
}

# brand name -> category
BRAND_CATEGORY = {}
for cat, names in CATEGORIES.items():
    for n in names:
        BRAND_CATEGORY[n] = cat

CATEGORY_ORDER = list(CATEGORIES.keys())


def category_for(name):
    return BRAND_CATEGORY.get(name, "Media & Other")
