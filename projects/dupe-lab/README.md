# 🧬 Dupe Lab — AI Skincare Dupe Finder

A production-ready Django web application that uses machine learning to analyze skincare product ingredient compositions and recommend cheaper alternatives (dupes).

---

## ✨ Features

| Feature | Description |
|---|---|
| **AI Dupe Finder** | TF-IDF + cosine similarity engine finds products with matching ingredient profiles |
| **Budget Dupe Detection** | Highlights products that are ≥75% similar AND cheaper than the original |
| **Dupe Score** | Combined metric: 70% ingredient similarity + 30% price advantage |
| **Ingredient Explorer** | Browse and search a curated ingredient dictionary with benefits, risks, and safety flags |
| **Safety Checker** | Paste any ingredient list — flags fragrances, parabens, sulfates, formaldehyde releasers, etc. |
| **Similarity Map** | Interactive t-SNE scatter plot: products cluster by ingredient similarity |
| **Ingredient Modal** | Click any ingredient chip on a product page to get instant info |
| **Skin Type Filtering** | Filter recommendations by dry / oily / sensitive / combination / normal |
| **REST API** | Full JSON API for all core features |
| **Admin Panel** | Upload CSVs, manage products and ingredients, rebuild similarity cache |

---

## 🚀 Quick Start

### 1. Clone and set up environment

```bash
git clone <repo>
cd ai_skincare_dupe_finder

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY
```

### 3. Initialize database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Load sample data

```bash
# Load the 35-product sample dataset
python manage.py load_products

# Seed ingredient descriptions
python manage.py seed_ingredients

# Build ingredient similarity cache (the ML step)
python manage.py build_similarity_cache
```

### 5. Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
ai_skincare_dupe_finder/
├── manage.py
├── requirements.txt
├── data/
│   └── skincare_products.csv          # Sample dataset (35 products)
│
├── ai_skincare_dupe_finder/
│   ├── settings.py                    # Django settings
│   └── urls.py                        # Root URL config
│
├── apps/
│   ├── products/                      # Core product models, search, views
│   │   ├── models.py                  # Product + SimilarityCache models
│   │   ├── views.py                   # Search, detail, autocomplete
│   │   ├── serializers.py             # DRF serializers
│   │   └── management/commands/
│   │       ├── load_products.py       # CSV import command
│   │       └── build_similarity_cache.py  # ML cache builder
│   │
│   ├── ingredients/                   # Ingredient dictionary + safety
│   │   ├── models.py                  # Ingredient model
│   │   ├── safety.py                  # Safety checker module
│   │   ├── views.py                   # Explorer, detail, safety checker
│   │   └── management/commands/
│   │       └── seed_ingredients.py    # Pre-populate ingredient data
│   │
│   ├── recommendations/               # ML similarity engine
│   │   ├── similarity_engine.py       # TF-IDF + cosine similarity pipeline
│   │   └── views.py                   # Dupe finder views + API
│   │
│   └── visualization/                 # t-SNE map
│       └── views.py                   # Map page + API endpoint
│
└── templates/
    ├── base.html                      # Navigation, styles, shared JS
    ├── products/
    │   ├── home.html                  # Landing page
    │   ├── product_list.html          # Searchable product grid
    │   └── product_detail.html        # Product + ingredients + quick dupes
    ├── recommendations/
    │   └── dupe_finder.html           # Full dupe results page
    ├── ingredients/
    │   ├── explorer.html              # Ingredient browsing
    │   ├── detail.html                # Single ingredient page
    │   └── safety_checker.html        # Safety analysis tool
    └── visualization/
        └── ingredient_map.html        # t-SNE scatter plot
```

---

## 🧠 ML Pipeline

### Similarity Engine (`apps/recommendations/similarity_engine.py`)

```
Raw ingredient text
       │
       ▼
tokenize_ingredients()
  • Lowercase & strip
  • Remove concentrations "(2%)"
  • Apply synonym normalization (aqua→water, glycerol→glycerin, etc.)
  • Filter stopwords
       │
       ▼
build_feature_matrix()
  • TF-IDF vectorizer (unigrams + bigrams)
  • min_df=1, max_df=0.95, sublinear_tf=True
  • Output: sparse matrix (n_products × n_features)
       │
       ▼
compute_similarity()
  • Pairwise cosine similarity
  • Output: n×n float32 matrix
       │
       ▼
find_top_similar_products()       find_cheaper_dupes()
  • Filter by min_similarity          • similarity ≥ 0.75
  • Optional skin type filter          • price < original
  • Sort by dupe_score                 • Sort by dupe_score
       │
       ▼
dupe_score = similarity(0.7) + price_advantage(0.3) × 100
```

### t-SNE Map
- TF-IDF matrix → TruncatedSVD (50 components) → t-SNE (2D)
- Rendered as Chart.js scatter plot with custom tooltips
- Color-coded by product category

---

## 🔌 REST API

| Endpoint | Method | Description |
|---|---|---|
| `/api/search-product/` | GET | Search products by name/brand |
| `/api/products/<id>/` | GET | Full product detail |
| `/recommendations/api/get-similar-products/` | GET | Similar products (ML) |
| `/recommendations/api/get-cheaper-dupes/` | GET | Budget dupes only |
| `/api/ingredient-info/` | GET | Ingredient info by name |
| `/api/safety-check/` | POST | Safety analysis |
| `/visualization/api/ingredient-map-data/` | GET | t-SNE coordinates |

### Example: Find dupes for product ID 1
```bash
curl "http://127.0.0.1:8000/recommendations/api/get-cheaper-dupes/?product_id=1"
```

---

## 📊 Loading Your Own Dataset

Your CSV should have these columns:

```csv
product_category, brand, product_name, price, rank, ingredients, skin_type
moisturizer, CeraVe, Moisturizing Cream, 16.99, 4.7, "Water, Glycerin, Niacinamide...", dry|sensitive
```

- `skin_type`: pipe-separated flags (`dry|oily|sensitive|normal|combination`)
- `ingredients`: comma-separated INCI ingredient list

```bash
python manage.py load_products --csv /path/to/your/dataset.csv --clear
python manage.py build_similarity_cache
```

---

## 🗄️ Database

Default: **SQLite** (zero setup, perfect for development)

For production, set `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/dupe_lab
```

---

## ⚙️ Environment Variables (`.env`)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=                          # Leave blank for SQLite
```

---

## 🏭 Production Deployment

```bash
DEBUG=False
python manage.py collectstatic --no-input
gunicorn ai_skincare_dupe_finder.wsgi:application --workers 4
```

Static files are served by **WhiteNoise** (configured in settings).

---

## 🛠️ Admin Panel

Visit `/admin/` and log in with your superuser account.

Admin actions:
- **Products**: Add, edit, import products; rebuild similarity cache
- **Ingredients**: Manage ingredient dictionary, risk levels, flags
- **Similarity Cache**: View computed similarity pairs

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `Django 4.2` | Web framework |
| `djangorestframework` | REST API |
| `scikit-learn` | TF-IDF, cosine similarity, t-SNE |
| `pandas` | Data manipulation for CSV import |
| `numpy` | Numerical operations |
| `whitenoise` | Static file serving |
| `Chart.js` (CDN) | t-SNE scatter plot |
| `Tailwind CSS` (CDN) | Utility-first styling |

---

## 🧪 Running Tests

```bash
python manage.py test apps.products apps.ingredients apps.recommendations
```

---

## 📝 License

MIT — free to use and modify for personal and commercial projects.

---

*Built with ❤️ for skincare nerds and budget-conscious beauty enthusiasts.*
