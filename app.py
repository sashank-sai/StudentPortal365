import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from models import db, login_manager, User, Bookmark, Rating

# ═══════════════════════════════════════════════════════════════════════════════
#  APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///studenthub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)

# ─── File-Based Logging ───────────────────────────────────────────────────────
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

file_handler = RotatingFileHandler(
    os.path.join(log_dir, "studenthub.log"),
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,
)
file_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
))
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info("StudentHub application started")

# ─── Create DB tables on first run ────────────────────────────────────────────
with app.app_context():
    db.create_all()
    app.logger.info("Database tables created/verified")


# ═══════════════════════════════════════════════════════════════════════════════
#  TOOL & MARKETPLACE DATA
# ═══════════════════════════════════════════════════════════════════════════════
TOOLS = {
    "Utilities": {
        "icon": "bi-tools",
        "color": "#6366f1",
        "tools": [
            {
                "name": "iLovePDF",
                "description": "Merge, split, compress, and convert PDFs — every PDF tool you need, 100% free.",
                "url": "https://www.ilovepdf.com",
                "icon": "bi-file-earmark-pdf-fill",
            },
            {
                "name": "QuillBot",
                "description": "AI-powered paraphrasing tool to rewrite and enhance your essays and articles.",
                "url": "https://quillbot.com",
                "icon": "bi-pencil-square",
            },
            {
                "name": "Notion",
                "description": "All-in-one workspace for notes, tasks, wikis, and project management.",
                "url": "https://www.notion.so",
                "icon": "bi-journal-bookmark-fill",
            },
            {
                "name": "Canva",
                "description": "Design stunning presentations, posters, and social media graphics effortlessly.",
                "url": "https://www.canva.com",
                "icon": "bi-palette-fill",
            },
            {
                "name": "Grammarly",
                "description": "AI writing assistant that checks grammar, punctuation, and writing style in real-time.",
                "url": "https://www.grammarly.com",
                "icon": "bi-spellcheck",
            },
        ],
    },
    "DSA & Coding": {
        "icon": "bi-code-slash",
        "color": "#06b6d4",
        "tools": [
            {
                "name": "LeetCode",
                "description": "Practice coding problems and prepare for technical interviews with 2500+ challenges.",
                "url": "https://leetcode.com",
                "icon": "bi-braces",
            },
            {
                "name": "NeetCode",
                "description": "Curated roadmaps and video explanations to master Data Structures & Algorithms.",
                "url": "https://neetcode.io",
                "icon": "bi-map-fill",
            },
            {
                "name": "GeeksforGeeks",
                "description": "Comprehensive tutorials, practice problems, and articles on computer science topics.",
                "url": "https://www.geeksforgeeks.org",
                "icon": "bi-book-half",
            },
            {
                "name": "HackerRank",
                "description": "Coding challenges and competitions to sharpen your programming skills.",
                "url": "https://www.hackerrank.com",
                "icon": "bi-trophy-fill",
            },
            {
                "name": "GitHub",
                "description": "Host, review, and collaborate on code. The world's largest developer platform.",
                "url": "https://github.com",
                "icon": "bi-github",
            },
        ],
    },
    "Research & AI": {
        "icon": "bi-robot",
        "color": "#8b5cf6",
        "tools": [
            {
                "name": "Papers with Code",
                "description": "Free resource linking machine learning papers with their official code implementations.",
                "url": "https://paperswithcode.com",
                "icon": "bi-file-earmark-code-fill",
            },
            {
                "name": "Google Scholar",
                "description": "Search across scholarly articles, theses, books, and conference papers.",
                "url": "https://scholar.google.com",
                "icon": "bi-mortarboard-fill",
            },
            {
                "name": "Semantic Scholar",
                "description": "AI-powered academic search engine for finding relevant research papers faster.",
                "url": "https://www.semanticscholar.org",
                "icon": "bi-search-heart",
            },
            {
                "name": "ChatGPT",
                "description": "AI assistant for brainstorming, explanations, writing help, and code debugging.",
                "url": "https://chat.openai.com",
                "icon": "bi-chat-dots-fill",
            },
            {
                "name": "Wolfram Alpha",
                "description": "Computational knowledge engine for math, physics, chemistry, and data analysis.",
                "url": "https://www.wolframalpha.com",
                "icon": "bi-calculator-fill",
            },
        ],
    },
    "Learning Platforms": {
        "icon": "bi-play-circle-fill",
        "color": "#10b981",
        "tools": [
            {
                "name": "Coursera",
                "description": "World-class courses from top universities, with free auditing and financial aid.",
                "url": "https://www.coursera.org",
                "icon": "bi-mortarboard-fill",
            },
            {
                "name": "MIT OpenCourseWare",
                "description": "Free lecture notes, exams, and videos from the Massachusetts Institute of Technology.",
                "url": "https://ocw.mit.edu",
                "icon": "bi-building",
            },
            {
                "name": "Khan Academy",
                "description": "Free courses on math, science, computing, economics, and test prep.",
                "url": "https://www.khanacademy.org",
                "icon": "bi-lightbulb-fill",
            },
            {
                "name": "freeCodeCamp",
                "description": "Learn to code for free with interactive lessons and earn certifications.",
                "url": "https://www.freecodecamp.org",
                "icon": "bi-laptop",
            },
        ],
    },
    "Productivity": {
        "icon": "bi-lightning-charge-fill",
        "color": "#f59e0b",
        "tools": [
            {
                "name": "Todoist",
                "description": "Organize your life with smart task management and natural language scheduling.",
                "url": "https://todoist.com",
                "icon": "bi-check2-square",
            },
            {
                "name": "Google Calendar",
                "description": "Schedule classes, deadlines, and events with smart reminders and sharing.",
                "url": "https://calendar.google.com",
                "icon": "bi-calendar-event-fill",
            },
            {
                "name": "Trello",
                "description": "Visual project management with boards, lists, and cards for team collaboration.",
                "url": "https://trello.com",
                "icon": "bi-kanban-fill",
            },
            {
                "name": "Forest",
                "description": "Stay focused and beat procrastination by growing virtual trees while you study.",
                "url": "https://www.forestapp.cc",
                "icon": "bi-tree-fill",
            },
        ],
    },
}


MARKETPLACE = {
    "Stickers & Decals": {
        "icon": "bi-stickies-fill",
        "color": "#f43f5e",
        "image": "images/stickers.png",
        "products": [
            {"name": "Developer Sticker Pack", "description": "50+ coding-themed vinyl stickers — Git, Python, JS, and more for your laptop.", "price": "₹749", "url": "https://www.redbubble.com/shop/developer+stickers", "icon": "bi-code-slash", "badge": "Popular", "image": "images/stickers.png"},
            {"name": "Science & Math Stickers", "description": "Premium die-cut stickers of equations, atoms, DNA, and STEM motifs.", "price": "₹579", "url": "https://www.redbubble.com/shop/science+stickers", "icon": "bi-calculator", "badge": "", "image": "images/science_stickers.png"},
            {"name": "Motivational Quote Stickers", "description": "Inspiring decals for planners, water bottles, and laptop covers.", "price": "₹449", "url": "https://www.etsy.com/search?q=motivational+stickers", "icon": "bi-chat-quote-fill", "badge": "", "image": "images/science_stickers.png"},
            {"name": "University Logo Stickers", "description": "Custom college logo stickers and mascot decals for school spirit.", "price": "₹399", "url": "https://www.redbubble.com/shop/university+stickers", "icon": "bi-mortarboard-fill", "badge": "", "image": "images/stickers.png"},
        ],
    },
    "Bags & Backpacks": {
        "icon": "bi-backpack-fill",
        "color": "#6366f1",
        "image": "images/backpack.png",
        "products": [
            {"name": "Anti-Theft Laptop Backpack", "description": "Waterproof backpack with USB charging port, fits 15.6\" laptops.", "price": "₹2,899", "url": "https://www.amazon.in/s?k=anti+theft+laptop+backpack+student", "icon": "bi-shield-lock-fill", "badge": "Best Seller", "image": "images/backpack.png"},
            {"name": "Canvas Tote Bag", "description": "Minimalist, reusable canvas tote for books, groceries, and everyday carry.", "price": "₹1,099", "url": "https://www.amazon.in/s?k=canvas+tote+bag+student", "icon": "bi-bag-fill", "badge": "", "image": "images/canvas_tote.png"},
            {"name": "Gym & Sports Duffel", "description": "Compact duffel bag with shoe compartment — gym, travel, and weekend trips.", "price": "₹2,099", "url": "https://www.amazon.in/s?k=gym+duffel+bag", "icon": "bi-dribbble", "badge": "", "image": "images/gym_duffel.png"},
            {"name": "Sling Crossbody Bag", "description": "Lightweight crossbody sling for essentials — phone, wallet, keys, and AirPods.", "price": "₹1,399", "url": "https://www.amazon.in/s?k=crossbody+sling+bag", "icon": "bi-handbag-fill", "badge": "New", "image": "images/sling_crossbody.png"},
        ],
    },
    "Laptops & Tech": {
        "icon": "bi-laptop",
        "color": "#06b6d4",
        "image": "images/laptop.png",
        "products": [
            {"name": "MacBook Air M3", "description": "Apple's ultra-thin laptop with M3 chip — 18-hr battery, perfect for students.", "price": "₹1,14,900", "url": "https://www.apple.com/in/shop/buy-mac/macbook-air", "icon": "bi-apple", "badge": "Top Pick", "image": "images/laptop.png"},
            {"name": "Dell XPS 13", "description": "Compact 13\" ultrabook with InfinityEdge display and Intel Core Ultra.", "price": "₹84,990", "url": "https://www.dell.com/en-in/shop/laptops/sr/laptops/xps-laptops", "icon": "bi-laptop", "badge": "", "image": "images/dell_xps.png"},
            {"name": "iPad Air + Apple Pencil", "description": "Take handwritten notes, annotate PDFs, and sketch diagrams in class.", "price": "₹59,900", "url": "https://www.apple.com/in/shop/buy-ipad/ipad-air", "icon": "bi-pencil", "badge": "Student Fave", "image": "images/ipad_pencil.png"},
            {"name": "Mechanical Keyboard", "description": "Compact 75% mechanical keyboard — perfect for dorm coding sessions.", "price": "₹3,999", "url": "https://www.amazon.in/s?k=mechanical+keyboard+student", "icon": "bi-keyboard-fill", "badge": "", "image": "images/mechanical_keyboard.png"},
            {"name": "Wireless Mouse", "description": "Ergonomic Bluetooth mouse with silent clicks — great for library study sessions.", "price": "₹1,599", "url": "https://www.amazon.in/s?k=wireless+mouse+student", "icon": "bi-mouse-fill", "badge": "", "image": "images/wireless_mouse.png"},
        ],
    },
    "Study Essentials": {
        "icon": "bi-journal-bookmark-fill",
        "color": "#8b5cf6",
        "image": "images/headphones.png",
        "products": [
            {"name": "Noise-Cancelling Headphones", "description": "Block out dorm noise with ANC headphones — focus mode activated.", "price": "₹6,499", "url": "https://www.amazon.in/s?k=noise+cancelling+headphones+student", "icon": "bi-headphones", "badge": "Must Have", "image": "images/headphones.png"},
            {"name": "LED Desk Lamp", "description": "Adjustable LED lamp with USB charging and multiple brightness modes.", "price": "₹1,899", "url": "https://www.amazon.in/s?k=led+desk+lamp+student", "icon": "bi-lamp-fill", "badge": "", "image": "images/desk_lamp.png"},
            {"name": "Reusable Smart Notebook", "description": "Write, scan to cloud, and erase — eco-friendly note-taking with Rocketbook.", "price": "₹2,499", "url": "https://www.amazon.in/s?k=rocketbook+smart+notebook", "icon": "bi-journal-text", "badge": "", "image": "images/smart_notebook.png"},
            {"name": "Highlighter Set", "description": "Pastel highlighters pack — aesthetic, no-bleed markers for textbook annotation.", "price": "₹649", "url": "https://www.amazon.in/s?k=pastel+highlighters+student", "icon": "bi-brush-fill", "badge": "", "image": "images/highlighters.png"},
        ],
    },
    "Student Deals & Discounts": {
        "icon": "bi-tag-fill",
        "color": "#10b981",
        "image": "images/deals.png",
        "products": [
            {"name": "UNiDAYS", "description": "Verified student discounts on tech, fashion, food, and lifestyle brands.", "price": "Free", "url": "https://www.myunidays.com", "icon": "bi-percent", "badge": "Free", "image": "images/deals.png"},
            {"name": "Amazon Prime Student", "description": "6-month free trial with Prime delivery, streaming, and exclusive student deals.", "price": "Free Trial", "url": "https://www.amazon.in/amazonprime", "icon": "bi-box-seam-fill", "badge": "Free Trial", "image": "images/deals.png"},
            {"name": "GitHub Student Pack", "description": "Free developer tools, cloud credits, and domain names for verified students.", "price": "Free", "url": "https://education.github.com/pack", "icon": "bi-gift-fill", "badge": "Free", "image": "images/deals.png"},
            {"name": "Spotify Student", "description": "Premium music streaming at a discounted student rate.", "price": "₹59/mo", "url": "https://www.spotify.com/in/student", "icon": "bi-music-note-beamed", "badge": "50% Off", "image": "images/deals.png"},
            {"name": "Apple Education Store", "description": "Save on Mac, iPad, and accessories with Apple's student pricing.", "price": "Up to ₹15,000 Off", "url": "https://www.apple.com/in/shop/education", "icon": "bi-apple", "badge": "Discount", "image": "images/deals.png"},
            {"name": "Notion Student Plan", "description": "Get Notion's Plus plan completely free with a valid student email address.", "price": "Free", "url": "https://www.notion.so/students", "icon": "bi-journal-bookmark-fill", "badge": "Free", "image": "images/deals.png"},
        ],
    },
}


STUDENT_OFFERS = [
    {"title": "Amazon Prime Student", "subtitle": "6 Months Free Trial", "description": "Free Prime delivery, ad-free streaming, and exclusive student deals for 6 months.", "discount": "FREE", "coupon_code": "AUTO-APPLIED", "url": "https://www.amazon.in/amazonprime", "icon": "bi-box-seam-fill", "color": "#ff9900", "valid_till": "Ongoing"},
    {"title": "GitHub Student Developer Pack", "subtitle": "₹50,000+ in Free Tools", "description": "Free domains, cloud credits, CI/CD tools, and 90+ developer tools for students.", "discount": "100% FREE", "coupon_code": "STUDENT-VERIFIED", "url": "https://education.github.com/pack", "icon": "bi-github", "color": "#8b5cf6", "valid_till": "While Enrolled"},
    {"title": "Spotify Premium Student", "subtitle": "Half-Price Music Streaming", "description": "Ad-free music, offline downloads, and podcast access at 50% off for students.", "discount": "50% OFF", "coupon_code": "AUTO-APPLIED", "url": "https://www.spotify.com/in/student/", "icon": "bi-spotify", "color": "#1db954", "valid_till": "Up to 4 Years"},
    {"title": "Apple Education Pricing", "subtitle": "Save on Mac & iPad", "description": "Special education pricing on MacBook, iPad, and accessories with free AirPods.", "discount": "Up to ₹15,000 OFF", "coupon_code": "EDUCATION-STORE", "url": "https://www.apple.com/in/shop/education", "icon": "bi-apple", "color": "#555555", "valid_till": "Ongoing"},
    {"title": "Notion Plus — Free for Students", "subtitle": "Full Plus Plan at ₹0", "description": "Unlimited blocks, file uploads, and team features — completely free with .edu email.", "discount": "100% FREE", "coupon_code": "EDU-EMAIL", "url": "https://www.notion.so/students", "icon": "bi-journal-bookmark-fill", "color": "#e16259", "valid_till": "While Enrolled"},
    {"title": "Canva Pro Student", "subtitle": "Premium Design Tools Free", "description": "Access premium templates, brand kits, magic resize, and background remover for free.", "discount": "100% FREE", "coupon_code": "EDU-VERIFIED", "url": "https://www.canva.com/education/", "icon": "bi-palette-fill", "color": "#06b6d4", "valid_till": "While Enrolled"},
]


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER — compute average ratings for tools
# ═══════════════════════════════════════════════════════════════════════════════
def get_ratings_map():
    """Return {tool_name: {avg, count}} for all rated tools."""
    results = (
        db.session.query(
            Rating.tool_name,
            db.func.avg(Rating.score).label("avg"),
            db.func.count(Rating.id).label("count"),
        )
        .group_by(Rating.tool_name)
        .all()
    )
    return {r.tool_name: {"avg": round(r.avg, 1), "count": r.count} for r in results}


def get_user_bookmarks():
    """Return set of bookmarked item names for the current user."""
    if current_user.is_authenticated:
        return {b.item_name for b in Bookmark.query.filter_by(user_id=current_user.id).all()}
    return set()


def get_user_ratings():
    """Return {tool_name: score} for the current user."""
    if current_user.is_authenticated:
        return {r.tool_name: r.score for r in Rating.query.filter_by(user_id=current_user.id).all()}
    return {}


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    ratings_map = get_ratings_map()
    user_bookmarks = get_user_bookmarks()
    user_ratings = get_user_ratings()
    app.logger.info(f"Home page loaded | user={'anonymous' if not current_user.is_authenticated else current_user.username}")
    return render_template(
        "index.html",
        tools=TOOLS,
        ratings_map=ratings_map,
        user_bookmarks=user_bookmarks,
        user_ratings=user_ratings,
    )


@app.route("/marketplace")
def marketplace():
    user_bookmarks = get_user_bookmarks()
    app.logger.info(f"Marketplace loaded | user={'anonymous' if not current_user.is_authenticated else current_user.username}")
    return render_template(
        "marketplace.html",
        marketplace=MARKETPLACE,
        offers=STUDENT_OFFERS,
        user_bookmarks=user_bookmarks,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("signup.html", username=username, email=email)

        user = User(username=username, email=email, auth_provider="local")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        app.logger.info(f"New user registered: {username} ({email})")
        flash("Account created! Please sign in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            app.logger.info(f"User signed in: {user.username}")
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            app.logger.warning(f"Failed login attempt for: {email}")
            flash("Invalid email or password.", "danger")
            return render_template("signin.html", email=email)

    return render_template("signin.html")


@app.route("/logout")
@login_required
def logout():
    app.logger.info(f"User signed out: {current_user.username}")
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))


@app.route("/profile")
@login_required
def profile():
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).order_by(Bookmark.created_at.desc()).all()
    ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.created_at.desc()).all()
    app.logger.info(f"Profile viewed: {current_user.username}")
    return render_template("profile.html", bookmarks=bookmarks, ratings=ratings)


# ═══════════════════════════════════════════════════════════════════════════════
#  API ROUTES (AJAX)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/api/bookmark", methods=["POST"])
@login_required
def toggle_bookmark():
    data = request.get_json()
    item_name = data.get("item_name", "")
    item_type = data.get("item_type", "tool")
    category = data.get("category", "")

    existing = Bookmark.query.filter_by(
        user_id=current_user.id, item_name=item_name, item_type=item_type
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        app.logger.info(f"Bookmark removed: {item_name} by {current_user.username}")
        return jsonify({"bookmarked": False})
    else:
        bm = Bookmark(
            user_id=current_user.id,
            item_name=item_name,
            item_type=item_type,
            category=category,
        )
        db.session.add(bm)
        db.session.commit()
        app.logger.info(f"Bookmark added: {item_name} by {current_user.username}")
        return jsonify({"bookmarked": True})


@app.route("/api/rate", methods=["POST"])
@login_required
def submit_rating():
    data = request.get_json()
    tool_name = data.get("tool_name", "")
    score = data.get("score", 0)
    review_text = data.get("review", "").strip()

    if not tool_name or not (1 <= score <= 5):
        return jsonify({"error": "Invalid rating"}), 400

    existing = Rating.query.filter_by(
        user_id=current_user.id, tool_name=tool_name
    ).first()

    if existing:
        existing.score = score
        existing.review_text = review_text
        existing.created_at = datetime.utcnow()
        app.logger.info(f"Rating updated: {tool_name} = {score} by {current_user.username}")
    else:
        rating = Rating(
            user_id=current_user.id,
            tool_name=tool_name,
            score=score,
            review_text=review_text,
        )
        db.session.add(rating)
        app.logger.info(f"New rating: {tool_name} = {score} by {current_user.username}")

    db.session.commit()

    # Return updated average
    avg_result = db.session.query(
        db.func.avg(Rating.score), db.func.count(Rating.id)
    ).filter_by(tool_name=tool_name).first()

    return jsonify({
        "success": True,
        "avg": round(avg_result[0], 1) if avg_result[0] else score,
        "count": avg_result[1],
        "user_score": score,
    })


@app.route("/api/reviews/<tool_name>")
def get_reviews(tool_name):
    reviews = (
        Rating.query.filter_by(tool_name=tool_name)
        .filter(Rating.review_text != "")
        .order_by(Rating.created_at.desc())
        .limit(20)
        .all()
    )
    return jsonify([
        {
            "username": r.user.username,
            "score": r.score,
            "review": r.review_text,
            "date": r.created_at.strftime("%b %d, %Y"),
        }
        for r in reviews
    ])


# ═══════════════════════════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True)
