#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة البحث التفاعلية عن الأفلام باستخدام MovieBox API
Interactive Movie Search Tool using MovieBox API
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
try:
    import brotli
except ImportError:
    brotli = None

class MovieBoxSearcher:
    """
    فئة للبحث عن الأفلام باستخدام MovieBox API
    """
    
    def __init__(self):
        self.base_url = "https://moviebox.ph/wefeed-h5-bff/web/subject/search"
        self.session = requests.Session()
        self.setup_headers()
    
    def setup_headers(self):
        """
        إعداد الـ Headers الأساسية
        """
        self.headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "application/json",
            "cookie": "i18n_lang=en; account=7687286686308878808|0|H5|1753483183|",
            "origin": "https://moviebox.ph",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "x-client-info": '{"timezone":"Africa/Casablanca"}'
        }
    
    def generate_watch_link(self, subject_id: str, detail_path: str, title: str) -> Dict[str, str]:
        """
        إنشاء رابط المشاهدة المباشر
        """
        fmovies_link = f"https://fmoviesunblocked.net/spa/videoPlayPage/movies/{detail_path}?id={subject_id}&type=/movie/detail"
        moviebox_link = f"https://moviebox.ph/web/detail/{detail_path}"
        streaming_api = f"https://fmoviesunblocked.net/wefeed-h5-bff/web/subject/play?subjectId={subject_id}&se=0&ep=0"
        
        return {
            "fmovies": fmovies_link,
            "moviebox": moviebox_link,
            "streaming_api": streaming_api,
            "title": title
        }
    
    def get_streaming_data(self, subject_id: str, detail_path: str, title: str, season: int = 0, episode: int = 0) -> Optional[Dict[str, Any]]:
        """
        الحصول على بيانات البث المباشر من API
        """
        streaming_url = f"https://fmoviesunblocked.net/wefeed-h5-bff/web/subject/play?subjectId={subject_id}&se={season}&ep={episode}"
        referer = f"https://fmoviesunblocked.net/spa/videoPlayPage/movies/{detail_path}?id={subject_id}&type=/movie/detail"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Referer": referer,
            "Accept": "application/json",
            "Origin": "https://fmoviesunblocked.net",
            "x-client-info": '{"timezone":"Africa/Casablanca"}'
        }
        
        try:
            response = requests.get(streaming_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None

    def search_movies(self, keyword: str, page: int = 1, per_page: int = 24, subject_type: int = 0) -> Optional[Dict[str, Any]]:
        """
        البحث عن الأفلام
        """
        safe_keyword = keyword.replace(" ", "%20")
        referer = f"https://moviebox.ph/web/searchResult?keyword={safe_keyword}&utm_source=h5seo_www.google.com"
        self.headers["referer"] = referer
        
        payload = {
            "keyword": keyword,
            "page": page,
            "perPage": per_page,
            "subjectType": subject_type
        }
        
        try:
            response = self.session.post(
                self.base_url, 
                headers=self.headers, 
                json=payload, 
                timeout=15
            )
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    if brotli and 'br' in response.headers.get('content-encoding', ''):
                        decompressed = brotli.decompress(response.content)
                        return json.loads(decompressed.decode('utf-8'))
                    return None
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def find_best_match(self, keyword: str, items: list) -> Optional[Dict[str, Any]]:
        """
        البحث عن أفضل تطابق للكلمة المفتاحية
        """
        if not items:
            return None
        
        clean_keyword = keyword.lower().strip()
        scored_items = []
        
        for item in items:
            title = item.get('title', '').lower()
            score = 0
            if clean_keyword == title:
                score += 100
            elif clean_keyword in title:
                score += 80
            scored_items.append((item, score))
        
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        if scored_items and scored_items[0][1] > 0:
            return scored_items[0][0]
        
        return items[0] if items else None