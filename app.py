# ==============================================================================
# Twitter Scraper Pro - A GUI-based Twitter Data Scraping Tool
#
# Author: Ameer Alshuga
# GitHub: https://github.com/Ameer-Alshuga
# Date: August 2025
#
# Description:
# This application allows users to scrape tweet data from Twitter (X)
# without using the official API. It features a comprehensive GUI,
# advanced filtering, real-time data viewing, and Excel export capabilities.
#
# © 2025 Ameer Alshuga. All rights reserved.
# ==============================================================================

import sys
import os
import asyncio
import random
import pandas as pd
from twikit import Client
from datetime import datetime
import re

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QFormLayout, QLineEdit, QPushButton, QTextEdit,
                             QSpinBox, QDateEdit, QLabel, QMessageBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
                             QAbstractItemView, QMenu, QStatusBar, QFileDialog, QDialog,
                             QDialogButtonBox)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QDate, Qt, QUrl, QPoint
from PyQt6.QtGui import QDesktopServices, QAction

# ==============================================================================
# ---  0. نافذة تسجيل الدخول --- (لا تغيير هنا)
# ==============================================================================
class LoginDialog(QDialog):
    # الكود هنا لم يتغير
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("تسجيل الدخول إلى تويتر"); self.setMinimumWidth(400); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QVBoxLayout(self); form_layout = QFormLayout()
        self.username_input = QLineEdit(); self.email_input = QLineEdit(); self.password_input = QLineEdit(); self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.status_label = QLabel("الرجاء إدخال معلومات حساب تويتر (تجريبي).")
        form_layout.addRow("اسم المستخدم:", self.username_input); form_layout.addRow("البريد الإلكتروني (اختياري):", self.email_input); form_layout.addRow("كلمة المرور:", self.password_input)
        layout.addLayout(form_layout); layout.addWidget(self.status_label)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.attempt_login); self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    def attempt_login(self):
        username = self.username_input.text().strip(); email = self.email_input.text().strip(); password = self.password_input.text().strip()
        if not username or not password: QMessageBox.warning(self, "خطأ", "يجب إدخال اسم المستخدم وكلمة المرور."); return
        self.status_label.setText("جاري تسجيل الدخول... الرجاء الانتظار."); self.button_box.setEnabled(False); QApplication.processEvents()
        try: asyncio.run(self.login_async(username, email, password)); self.accept()
        except Exception as e:
            self.status_label.setText("فشل تسجيل الدخول."); QMessageBox.critical(self, "فشل تسجيل الدخول", f"حدث خطأ:\n{e}\n\nتأكد من المعلومات أو سجل دخولك من المتصفح أولاً."); self.button_box.setEnabled(True)
    async def login_async(self, username, email, password):
        client = Client('en-US'); await client.login(auth_info_1=username, auth_info_2=email, password=password); client.save_cookies('my_cookies.json')

# ==============================================================================
# ---  1. منطق العمل (Worker) --- (لا تغيير هنا)
# ==============================================================================
class ScraperWorker(QObject):
    # الكود هنا لم يتغير
    progress = pyqtSignal(str); tweet_found = pyqtSignal(dict); finished = pyqtSignal(str); error = pyqtSignal(str)
    def __init__(self, settings): super().__init__(); self.settings = settings; self.is_running = True
    def run_scraper(self):
        try: asyncio.run(self.main())
        except Exception as e: self.error.emit(f"An unexpected error in thread: {e}")
    async def main(self):
        collected_count = 0; COOKIE_FILE_PATH = 'my_cookies.json'
        if not os.path.exists(COOKIE_FILE_PATH): self.error.emit(f"ERROR: Cookie file not found."); return
        query = self.settings['search_term']
        if self.settings['start_date']: query += f" since:{self.settings['start_date']}"
        if self.settings['end_date']: query += f" until:{self.settings['end_date']}"
        try:
            client = Client('en-US'); client.load_cookies(COOKIE_FILE_PATH)
            self.progress.emit("Successfully loaded login session."); self.progress.emit(f"Executing search: '{query}'")
            if self.settings['keywords']: self.progress.emit(f"Filtering for keywords: {self.settings['keywords']}")
            cursor = None; limit = self.settings['limit']
            while collected_count < limit:
                if not self.is_running: self.progress.emit("Scraping stopped by user."); break
                self.progress.emit(f"Collected {collected_count} of {limit} tweets...")
                search_results = await client.search_tweet(query, 'Latest', cursor=cursor)
                if not search_results: self.progress.emit("Reached end of search results."); break
                for tweet in search_results:
                    if collected_count >= limit: break
                    tweet_text_lower = tweet.text.lower(); keywords = self.settings['keywords']
                    if not keywords or any(keyword.lower() in tweet_text_lower for keyword in keywords):
                        tweet_date = tweet.created_at
                        if isinstance(tweet_date, datetime): formatted_date = tweet_date.strftime('%Y/%#m/%#d') if sys.platform == 'win32' else tweet_date.strftime('%Y/%-m/%-d')
                        else:
                            try:
                                dt_obj = datetime.fromisoformat(str(tweet_date).replace('Z', '+00:00'))
                                formatted_date = dt_obj.strftime('%Y/%#m/%#d') if sys.platform == 'win32' else dt_obj.strftime('%Y/%-m/%-d')
                            except: formatted_date = str(tweet_date).split('T')[0].replace('-', '/')
                        tweet_data = {"Text": tweet.text, "Likes": tweet.favorite_count, "Retweets": tweet.retweet_count, "Username": tweet.user.screen_name, "Date": formatted_date, "URL": f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'}
                        self.tweet_found.emit(tweet_data); collected_count += 1
                cursor = search_results.next_cursor
                if not cursor: self.progress.emit("Reached end of search results."); break
                await asyncio.sleep(random.uniform(5, 10))
        except Exception as e: self.error.emit(f"An error occurred during scraping: {e}"); return
        self.finished.emit(f"Finished. Total tweets collected: {collected_count}")
    def stop(self): self.is_running = False

# ==============================================================================
# --- 2. الواجهة الرسومية الرئيسية (GUI) ---
# ==============================================================================
class ScraperApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Twitter Scraper Pro | أداة جمع وعرض البيانات"); self.setGeometry(100, 100, 1000, 800)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft); QApplication.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.tabs = QTabWidget(); self.setCentralWidget(self.tabs)
        self.settings_tab = QWidget(); self.tabs.addTab(self.settings_tab, "⚙️ الإعدادات والسجل"); self.setup_settings_tab()
        self.data_view_tab = QWidget(); self.tabs.addTab(self.data_view_tab, "📊 عرض البيانات"); self.setup_data_view_tab()
        self.scraper_thread = None; self.worker = None; self.data_df = None
        self.setStatusBar(QStatusBar(self)); self.statusBar().showMessage("جاهز")
    
    def setup_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab); form_layout = QFormLayout()
        self.search_term_input = QLineEdit("#السعودية")
        self.date_filter_checkbox = QCheckBox("تفعيل فلتر التاريخ"); self.date_filter_checkbox.setChecked(True); self.date_filter_checkbox.stateChanged.connect(self.toggle_date_fields)
        self.date_start_input = QDateEdit(calendarPopup=True, displayFormat="yyyy/M/d", date=QDate.currentDate().addMonths(-1))
        self.date_end_input = QDateEdit(calendarPopup=True, displayFormat="yyyy/M/d", date=QDate.currentDate())
        self.keywords_input = QLineEdit("نيوم"); self.limit_input = QSpinBox(minimum=1, maximum=10000, value=100)
        form_layout.addRow(QLabel("<b><font size='4'>إعدادات البحث</font></b>")); form_layout.addRow("مصطلح البحث:", self.search_term_input)
        form_layout.addRow(self.date_filter_checkbox); form_layout.addRow("من تاريخ:", self.date_start_input); form_layout.addRow("إلى تاريخ:", self.date_end_input)
        form_layout.addRow("فلترة بالكلمات:", self.keywords_input); form_layout.addRow("الحد الأقصى للتغريدات:", self.limit_input)
        layout.addLayout(form_layout)
        self.start_button = QPushButton("🚀 ابدأ جمع البيانات"); self.start_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_button, 1, Qt.AlignmentFlag.AlignBottom)
        self.stop_button = QPushButton("🛑 إيقاف"); self.stop_button.clicked.connect(self.stop_scraping); self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        self.log_box = QTextEdit(readOnly=True, placeholderText="ستظهر هنا حالة عملية جمع البيانات..."); layout.addWidget(self.log_box)

    def toggle_date_fields(self):
        is_enabled = self.date_filter_checkbox.isChecked(); self.date_start_input.setEnabled(is_enabled); self.date_end_input.setEnabled(is_enabled)

    def setup_data_view_tab(self):
        layout = QVBoxLayout(self.data_view_tab); self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.table.setWordWrap(True); self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""QTableWidget { background-color: white; gridline-color: #E0E0E0; font-size: 14px; } QHeaderView::section { background-color: #F8F8F8; padding: 8px; border: 1px solid #E0E0E0; font-weight: bold; } QTableWidget::item:selected { background-color: #E8F4FD; color: black; }""")
        layout.addWidget(self.table)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); self.table.customContextMenuRequested.connect(self.show_table_context_menu); self.table.cellDoubleClicked.connect(self.open_link_on_double_click)
        self.export_button = QPushButton("💾 تصدير كملف إكسل (Export to Excel)"); self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setEnabled(False); self.export_button.setStyleSheet("background-color: #1d6f42; color: white; padding: 10px; font-size: 14px; border-radius: 5px; margin-top: 10px;")
        layout.addWidget(self.export_button)

    def start_scraping(self):
        # --- هذا هو الإصلاح ---
        # استخدام .date().toString() للحصول على الصيغة الصحيحة للإرسال
        start_date = self.date_start_input.date().toString('yyyy-MM-dd') if self.date_filter_checkbox.isChecked() else ""
        end_date = self.date_end_input.date().toString('yyyy-MM-dd') if self.date_filter_checkbox.isChecked() else ""
        # --------------------

        settings = {'search_term': self.search_term_input.text(), 'start_date': start_date, 'end_date': end_date, 'keywords': [k.strip() for k in self.keywords_input.text().split(',') if k.strip()], 'limit': self.limit_input.value()}
        
        if not settings['search_term']: QMessageBox.warning(self, "خطأ", "الرجاء إدخال مصطلح البحث."); return
        
        self.log_box.clear(); self.table.setRowCount(0); self.data_df = None
        self.start_button.setEnabled(False); self.stop_button.setEnabled(True); self.export_button.setEnabled(False)
        self.tabs.setCurrentWidget(self.settings_tab)
        headers = ["نص التغريدة", "الإعجابات", "الريتويت", "اسم المستخدم", "التاريخ", "الرابط"]
        self.table.setColumnCount(len(headers)); self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader(); header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6): header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.scraper_thread = QThread()
        self.worker = ScraperWorker(settings)
        self.worker.moveToThread(self.scraper_thread)
        self.scraper_thread.started.connect(self.worker.run_scraper); self.worker.tweet_found.connect(self.add_tweet_to_table)
        self.worker.finished.connect(self.on_scraping_finished); self.worker.error.connect(self.on_scraping_error); self.worker.progress.connect(self.update_log)
        self.scraper_thread.start()

    def update_log(self, message): self.log_box.append(message)
    def add_tweet_to_table(self, tweet_data):
        if self.data_df is None: self.data_df = pd.DataFrame()
        new_row = pd.DataFrame([tweet_data]); self.data_df = pd.concat([self.data_df, new_row], ignore_index=True)
        row_position = self.table.rowCount(); self.table.insertRow(row_position)
        headers_map = {"نص التغريدة": "Text", "الإعجابات": "Likes", "الريتويت": "Retweets", "اسم المستخدم": "Username", "التاريخ": "Date", "الرابط": "URL"}
        for col_idx, header in enumerate(headers_map.keys()):
            cell_value = tweet_data.get(headers_map[header], "")
            if header == "الرابط":
                item = QTableWidgetItem("🔗 افتح الرابط"); item.setForeground(Qt.GlobalColor.blue); item.setToolTip("انقر نقرًا مزدوجًا لفتح الرابط")
            else: item = QTableWidgetItem(str(cell_value))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable); self.table.setItem(row_position, col_idx, item)
        self.table.resizeRowToContents(row_position); self.statusBar().showMessage(f"تم العثور على تغريدة جديدة... ({self.table.rowCount()} in total)", 2000)

    def on_scraping_finished(self, message):
        self.log_box.append(f"\n✅ SUCCESS: {message}")
        if self.data_df is not None and not self.data_df.empty:
            self.export_button.setEnabled(True)
        self._cleanup_thread()
    
    def export_to_excel(self):
        if self.data_df is None or self.data_df.empty: QMessageBox.warning(self, "لا توجد بيانات", "لا توجد بيانات لتصديرها."); return
        search_term_for_filename = re.sub(r'[\\/*?:"<>|#]', "", self.search_term_input.text())
        default_excel_filename = f"{search_term_for_filename}.xlsx"
        filePath, _ = QFileDialog.getSaveFileName(self, "حفظ كملف إكسل", default_excel_filename, "Excel Files (*.xlsx);;All Files (*)")
        if filePath:
            try:
                self.data_df.to_excel(filePath, index=False, engine='openpyxl')
                self.statusBar().showMessage(f"✅ تم تصدير البيانات بنجاح إلى {os.path.basename(filePath)}", 5000)
                QMessageBox.information(self, "نجاح", f"تم تصدير البيانات بنجاح إلى:\n{filePath}")
            except Exception as e: QMessageBox.critical(self, "خطأ في التصدير", f"فشل حفظ ملف الإكسل:\n{e}")

    def show_table_context_menu(self, pos: QPoint):
        if not self.table.selectedItems(): return
        menu = QMenu(); copy_action = QAction("📋 نسخ نص التغريدة", self); copy_action.triggered.connect(self.copy_tweet_text); menu.addAction(copy_action)
        menu.exec(self.table.mapToGlobal(pos))
    def copy_tweet_text(self):
        selected_row = self.table.currentRow();
        if selected_row < 0: return
        tweet_text = self.table.item(selected_row, 0).text()
        clipboard = QApplication.clipboard(); clipboard.setText(tweet_text)
        self.statusBar().showMessage("✅ تم نسخ نص التغريدة بنجاح!", 3000)
    def open_link_on_double_click(self, row, column):
        if column == 5 and self.data_df is not None:
            url = self.data_df.iloc[row]['URL']; QDesktopServices.openUrl(QUrl(url))
    def on_scraping_error(self, message):
        self.log_box.append(f"\n❌ ERROR: {message}"); QMessageBox.critical(self, "Error", message); self._cleanup_thread()
    def stop_scraping(self):
        if self.worker: self.worker.stop()
        if self.scraper_thread: self.scraper_thread.quit(); self.scraper_thread.wait()
        self.start_button.setEnabled(True); self.stop_button.setEnabled(False); self.log_box.append("\nProcess stopped by user.")
    def _cleanup_thread(self):
        self.start_button.setEnabled(True); self.stop_button.setEnabled(False)
        if self.scraper_thread and self.scraper_thread.isRunning():
            self.scraper_thread.quit(); self.scraper_thread.wait()
    def closeEvent(self, event): self.stop_scraping(); event.accept()

# ==============================================================================
# --- 3. نقطة انطلاق البرنامج --- (لا تغيير هنا)
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not os.path.exists('my_cookies.json'):
        login_dialog = LoginDialog()
        if not login_dialog.exec():
            sys.exit(0)
    window = ScraperApp()
    window.show()
    sys.exit(app.exec())