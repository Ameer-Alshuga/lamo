# File: scraper.py (Version with Date and Keyword Filters)

import asyncio
import pandas as pd
from twikit import Client
import os
import random

# ==============================================================================
# --- SETTINGS: قم بتعديل هذه القيم حسب حاجتك ---
# ==============================================================================

# 1. مصطلح البحث الأساسي (هاشتاج، كلمة، أو من مستخدم معين)
SEARCH_TERM = "#السعودية"

# 2. فلتر التاريخ (اتركه فارغًا "" لتعطيله)
#    - الصيغة يجب أن تكون "YYYY-MM-DD"
START_DATE = "2023-12-01"  # مثال: البدء من 1 ديسمبر 2023
END_DATE = "2023-12-31"    # مثال: الانتهاء في 31 ديسمبر 2023

# 3. فلتر الكلمات الرئيسية (بعد جمع البيانات)
#    - سيتم حفظ التغريدة فقط إذا كانت تحتوي على واحدة من هذه الكلمات.
#    - اتركه فارغًا هكذا [] لحفظ كل شيء.
KEYWORD_FILTER = [
    
]

# 4. الحد الأقصى لعدد التغريدات المطلوب جمعها (بعد الفلترة)
limit = 10

# 5. اسم الملف الناتج
output_filename = "filtered_saudi_tweets.csv"

# ==============================================================================
# --- (لا تقم بتعديل أي شيء تحت هذا الخط) ---
# ==============================================================================

COOKIE_FILE_PATH = 'my_cookies.json'

async def main():
    tweets_list = []
    if not os.path.exists(COOKIE_FILE_PATH):
        print(f"ERROR: Cookie file not found at '{COOKIE_FILE_PATH}'")
        return

    # بناء نص البحث النهائي مع التواريخ
    query = SEARCH_TERM
    if START_DATE:
        query += f" since:{START_DATE}"
    if END_DATE:
        query += f" until:{END_DATE}"
        
    try:
        client = Client('en-US')
        client.load_cookies(COOKIE_FILE_PATH)
        print("Successfully loaded login session from cookies.")
        print(f"Executing search with query: '{query}'")
        if KEYWORD_FILTER:
            print(f"Filtering results for keywords: {KEYWORD_FILTER}")

        cursor = None
        while len(tweets_list) < limit:
            print(f"Collected {len(tweets_list)} of {limit} tweets...", end='\r')
            search_results = await client.search_tweet(query, 'Latest', cursor=cursor)

            if not search_results:
                print("\nReached the end of the search results.")
                break

            for tweet in search_results:
                # تطبيق فلتر الكلمات الرئيسية
                tweet_text_lower = tweet.text.lower()
                
                # التحقق: إما أن يكون فلتر الكلمات فارغًا، أو أن النص يحتوي على إحدى الكلمات
                if not KEYWORD_FILTER or any(keyword.lower() in tweet_text_lower for keyword in KEYWORD_FILTER):
                    tweets_list.append([
                        tweet.created_at, tweet.id, tweet.text,
                        tweet.user.screen_name, tweet.favorite_count,
                        tweet.retweet_count,
                        f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
                    ])
                
                # التوقف إذا وصلنا إلى الحد المطلوب بعد الفلترة
                if len(tweets_list) >= limit:
                    break
            
            # الخروج من الحلقة الخارجية إذا وصلنا للحد
            if len(tweets_list) >= limit:
                break
            
            cursor = search_results.next_cursor
            if not cursor:
                print("\nReached the end of the search results.")
                break

            wait_time = random.uniform(3, 7)
            await asyncio.sleep(wait_time)
    
    except Exception as e:
        print(f"\nAn error occurred: {e}")

    finally:
        final_tweets = tweets_list[:limit]
        print(f"\nFinished collecting {len(final_tweets)} tweets.")
        if final_tweets:
            df = pd.DataFrame(final_tweets, columns=['Datetime', 'Tweet ID', 'Text', 'Username', 'Likes', 'Retweets', 'URL'])
            df.to_csv(output_filename, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to: {output_filename}")

if __name__ == '__main__':
    asyncio.run(main())