# Twitter Scraper Pro

**Developed by: Ameer Alshuga © 2025**

[![GitHub profile](https://img.shields.io/badge/GitHub-Ameer--Alshuga-blue?style=flat&logo=github)](https://github.com/Ameer-Alshuga)

---

## 📜 About The Project

**Twitter Scraper Pro** is a comprehensive desktop application developed with Python and PyQt6, designed to scrape and analyze tweets from Twitter (X) without requiring the paid official API. The application provides a user-friendly graphical interface that allows users to perform advanced searches, filter results, view data in real-time, and export it to Excel files for further analysis.

## ✨ Key Features

-   **Full-Featured GUI:** An intuitive and organized interface built with PyQt6.
-   **Secure Login:** A login dialog appears only once to save the user's session securely.
-   **Advanced Search:** Supports searching by keywords, phrases, hashtags, and from specific users.
-   **Powerful Filtering:**
    -   Filter tweets by a specific date range (start and end dates).
    -   Filter results based on the presence of specific keywords within the tweet's text.
-   **Real-time Data Display:** Tweets are displayed in the data table as soon as they are found.
-   **Professional Data Table:**
    -   Full tweet text display with automatic word wrapping.
    -   Right-to-left layout support for Arabic and other RTL languages.
    -   Sort data by clicking on any column header.
    -   Professional row highlighting for easy reading.
-   **Interactive Features:**
    -   Copy any tweet's text with a simple right-click.
    -   Open the original tweet in a browser with a double-click.
-   **Export to Excel:** Easily export all collected data to a user-selected `.xlsx` file.

## 📸 Application Screenshots

Here's a look at the application in action.

### **1. Secure Login**
On the first run, the application prompts for Twitter credentials (username, email, and password) to create a secure session cookie.

![Login Dialog](https://raw.githubusercontent.com/Ameer-Alshuga/lamo/main/assets/1.png)

---

### **2. Main Interface & Search Settings**
The main control panel where you can define your search term, apply date and keyword filters, set the tweet limit, and monitor the scraping process.

![Main Interface](https://raw.githubusercontent.com/Ameer-Alshuga/lamo/main/assets/2.png)

---

### **3. Data View & Export**
The data tab displays scraped tweets instantly. You can view, sort, and interact with the data, and then export it to a clean, organized Excel file.

![Data View and Export](https://raw.githubusercontent.com/Ameer-Alshuga/lamo/main/assets/3.png)

## 🛠️ Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Ensure you have the following software installed on your system:

-   **Python 3.8+:** [Download Python](https://www.python.org/downloads/)
    -   *Important: During installation, make sure to check the box "Add Python to PATH".*
-   **Git:** [Download Git](https://git-scm.com/downloads/)

### Installation

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/Ameer-Alshuga/lamo.git
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd lamo
    ```

3.  **Install all required libraries with a single command:**
    ```bash
    pip install PyQt6 pandas openpyxl git+https://github.com/d60/twikit.git
    ```

### Running the Application

1.  Make sure you are in the project directory in your terminal.
2.  Run the application using the following command:
    ```bash
    python app.py
    ```
3.  **On the first run only:**
    > **Note:** Before this step, it is highly recommended to first log into your Twitter account using a normal web browser (like Chrome or Firefox). This helps solve any security checks (like CAPTCHAs) that might otherwise block the application's login attempt.

    A dialog will prompt you for your Twitter account credentials. After a successful login, a `my_cookies.json` file will be created, and the main application window will open.
    
4.  **On subsequent runs:** The application will launch directly to the main window.

