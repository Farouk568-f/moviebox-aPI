from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from movie_search_logic import MovieBoxSearcher

# --- تهيئة التطبيق ---
app = FastAPI(
    title="MovieBox Streaming API",
    description="API للبحث عن الأفلام والمسلسلات والحصول على روابط البث المباشر.",
    version="1.0.0"
)

# متغير مطلوب للنشر على Vercel
app.debug = False

# إنشاء نسخة واحدة من الكلاس لإعادة استخدامها في كل الطلبات
searcher = MovieBoxSearcher()

# --- نماذج البيانات (للتوثيق وتحديد نوع المخرجات) ---
class StreamLink(BaseModel):
    format: Optional[str] = None
    url: Optional[str] = None
    resolutions: Optional[str] = None
    size: Optional[str] = None

class StreamingData(BaseModel):
    streams: List[StreamLink]
    hls: List[StreamLink]
    hasResource: bool

class SearchResult(BaseModel):
    title: str
    subjectId: str
    detailPath: str
    releaseDate: Optional[str] = None
    imdbRatingValue: Optional[float] = None
    genre: Optional[str] = None
    description: Optional[str] = None

# --- نقاط النهاية (API Endpoints) ---

@app.get("/", tags=["Root"])
async def read_root():
    """
    نقطة البداية للـ API.
    """
    return {"message": "أهلاً بك في MovieBox API. اذهب إلى /docs لرؤية التوثيق."}

@app.get("/search", response_model=List[SearchResult], tags=["Search"])
async def search_movie_or_series(
    query: str = Query(..., min_length=2, description="اسم الفيلم أو المسلسل للبحث عنه")
):
    """
    ابحث عن فيلم أو مسلسل بالاسم.
    - **query**: اسم الفيلم أو المسلسل (مثال: The Matrix)
    """
    results = searcher.search_movies(keyword=query, page=1, per_page=20)
    
    if not results or results.get('code') != 0:
        raise HTTPException(status_code=404, detail="لم يتم العثور على نتائج للبحث.")
        
    items = results.get('data', {}).get('items', [])
    if not items:
        raise HTTPException(status_code=404, detail=f"لا توجد نتائج لـ '{query}'")
        
    # تنسيق النتائج قبل إرسالها
    formatted_results = [
        SearchResult(**item) for item in items
    ]
    return formatted_results


@app.get("/streams", response_model=StreamingData, tags=["Streaming"])
async def get_streaming_links(
    subject_id: str = Query(..., description="ID الخاص بالفيلم أو المسلسل"),
    detail_path: str = Query(..., description="مسار التفاصيل (detailPath) من نتيجة البحث"),
    title: str = Query(..., description="عنوان الفيلم (لإنشاء Referer صحيح)"),
    season: int = Query(0, description="رقم الموسم (للمسلسلات فقط، 0 للأفلام)"),
    episode: int = Query(0, description="رقم الحلقة (للمسلسلات فقط، 0 للأفلام)")
):
    """
    احصل على روابط البث المباشر لفيلم أو حلقة مسلسل محددة.
    - **subject_id**: احصل عليه من نتيجة البحث.
    - **detail_path**: احصل عليه من نتيجة البحث.
    - **title**: احصل عليه من نتيجة البحث.
    - **season**: للمسلسلات، مثال: 1
    - **episode**: للمسلسلات، مثال: 1
    """
    streaming_data = searcher.get_streaming_data(
        subject_id=subject_id,
        detail_path=detail_path,
        title=title,
        season=season,
        episode=episode
    )
    
    if not streaming_data or streaming_data.get('code') != 0:
        raise HTTPException(status_code=404, detail="فشل في الحصول على روابط البث.")
        
    data = streaming_data.get('data', {})
    if not data.get('hasResource', False):
        raise HTTPException(status_code=404, detail="لا توجد روابط بث متاحة لهذا المحتوى.")
        
    return StreamingData(**data)

# (أضف هذا الكود في نهاية ملف main_api.py قبل أي سطر if __name__ == "__main__":)

@app.get("/search-and-get-episode-streams", tags=["Convenience"])
async def search_and_get_episode_streams(
    query: str = Query(..., min_length=2, description="اسم المسلسل للبحث عنه"),
    season: int = Query(..., gt=0, description="رقم الموسم (يجب أن يكون أكبر من 0)"),
    episode: int = Query(..., gt=0, description="رقم الحلقة (يجب أن يكون أكبر من 0)")
):
    """
    **نقطة نهاية مدمجة للمسلسلات:** تبحث عن مسلسل وتعيد روابط البث لحلقة معينة.
    """
    # 1. البحث عن المسلسل
    search_results = searcher.search_movies(keyword=query, page=1, per_page=10)
    if not search_results or search_results.get('code') != 0:
        raise HTTPException(status_code=404, detail=f"لم يتم العثور على مسلسل باسم '{query}'.")
        
    items = search_results.get('data', {}).get('items', [])
    if not items:
        raise HTTPException(status_code=404, detail=f"لا توجد نتائج لـ '{query}'")

    # 2. اختيار أفضل نتيجة
    best_match = searcher.find_best_match(query, items)
    
    # 3. الحصول على روابط البث للحلقة المحددة
    streaming_data = searcher.get_streaming_data(
        subject_id=best_match['subjectId'],
        detail_path=best_match['detailPath'],
        title=best_match['title'],
        season=season,
        episode=episode
    )
    
    if not streaming_data or streaming_data.get('code') != 0 or not streaming_data.get('data', {}).get('hasResource', False):
        raise HTTPException(status_code=404, detail=f"تم العثور على المسلسل ولكن فشل استخراج روابط البث للموسم {season} الحلقة {episode}.")

    return {
        "search_result": best_match,
        "streaming_links": streaming_data['data']
    }

@app.get("/search-and-get-streams", tags=["Convenience"])
async def search_and_get_first_result_streams(
    query: str = Query(..., min_length=2, description="اسم الفيلم أو المسلسل للبحث عنه")
):
    """
    **نقطة نهاية مدمجة:** تبحث عن فيلم وتعيد روابط البث لأفضل نتيجة مباشرة.
    """
    # 1. البحث عن الفيلم
    search_results = searcher.search_movies(keyword=query, page=1, per_page=10)
    if not search_results or search_results.get('code') != 0:
        raise HTTPException(status_code=404, detail="لم يتم العثور على الفيلم.")
        
    items = search_results.get('data', {}).get('items', [])
    if not items:
        raise HTTPException(status_code=404, detail=f"لا توجد نتائج لـ '{query}'")

    # 2. اختيار أفضل نتيجة
    best_match = searcher.find_best_match(query, items)
    
    # 3. الحصول على روابط البث
    streaming_data = searcher.get_streaming_data(
        subject_id=best_match['subjectId'],
        detail_path=best_match['detailPath'],
        title=best_match['title']
    )
    
    if not streaming_data or streaming_data.get('code') != 0 or not streaming_data.get('data', {}).get('hasResource', False):
        raise HTTPException(status_code=404, detail="تم العثور على الفيلم ولكن فشل استخراج روابط البث.")

    return {
        "search_result": best_match,
        "streaming_links": streaming_data['data']
    }