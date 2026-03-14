# StudentPortal365 (StudentHub)

A comprehensive portal designed to empower students by providing a curated directory of essential academic and productivity tools, an exclusive student marketplace, and a hub for student deals. Built with Flask, this application features user authentication, personalized bookmarking, and community ratings.

## 🚀 Features


- **Resource Directory**: A categorized collection of tools covering Utilities, DSA & Coding, Research & AI, Learning Platforms, and Productivity.
- **Student Marketplace**: Discover curated products tailored for student life, including study essentials, laptops, and backpacks.
- **Exclusive Offers**: Centralized spot to find the best student discounts from brands like Amazon, GitHub, Spotify, Apple, and Notion.
- **User Authentication**: Secure user registration, login, and session management.
- **Personalized Profiles**: Users can bookmark their favorite tools and products, and write reviews/ratings for tools they use.
- **Dynamic Theming**: Aesthetic and sleek UI with full support for Dark and Light modes.

## 🛠️ Tech Stack

- **Backend Framework**: Python, Flask
- **Database**: SQLite (using Flask-SQLAlchemy)
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3 (Custom properties for theming), Vanilla JavaScript
- **Deployment & Server**: Gunicorn (Ready)

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sashank-sai/StudentPortal365.git
   cd StudentPortal365
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   > **Note:** The SQLite database (`studenthub.db`) and necessary tables will be created automatically upon the first run.

5. **Access the application:**
   Open your favorite web browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## 📁 Project Structure

```text
📦 StudentPortal365
 ┣ 📂 instance        # Auto-generated SQLite database storage
 ┣ 📂 logs            # File-based application logs
 ┣ 📂 static          # Static assets
 ┃ ┣ 📂 css           # Thematic style sheets
 ┃ ┣ 📂 js            # Frontend scripts
 ┃ ┗ 📂 images        # Product and application images
 ┣ 📂 templates       # HTML files (Jinja2 templates)
 ┣ 📜 app.py          # Main application logic and routing
 ┣ 📜 models.py       # SQLAlchemy database schema definition
 ┣ 📜 requirements.txt# Python package dependencies
 ┗ 📜 README.md       # Project documentation
```

## 🤝 Contributing
Contributions, bug reports, and feature requests are always welcome! Feel free to fork the repository and submit pull requests.

## 📝 Logging
The application uses Python's built-in `logging` setup with a `RotatingFileHandler`. All logs (info, warnings, registrations, etc.) are securely stored inside the `/logs` directory for easy debugging and auditing.
