# MovieBox Streaming API

API للبحث عن الأفلام والمسلسلات والحصول على روابط البث المباشر.

## الميزات

- 🔍 البحث عن الأفلام والمسلسلات
- 📺 الحصول على روابط البث المباشر
- 🎬 دعم المسلسلات مع الموسم والحلقة
- 📱 API سهل الاستخدام

## النشر على Vercel

### الطريقة الأولى: استخدام Vercel CLI

1. قم بتثبيت Vercel CLI:
```bash
npm i -g vercel
```

2. قم بتسجيل الدخول:
```bash
vercel login
```

3. انشر التطبيق:
```bash
vercel
```

### الطريقة الثانية: النشر من GitHub

1. ارفع الكود إلى GitHub
2. اذهب إلى [vercel.com](https://vercel.com)
3. اضغط على "New Project"
4. اختر المستودع من GitHub
5. اضغط على "Deploy"

## استخدام API

بعد النشر، ستجد URL للتطبيق. يمكنك استخدام النقاط التالية:

- `GET /` - الصفحة الرئيسية
- `GET /search?query=اسم_الفيلم` - البحث عن فيلم
- `GET /streams?subject_id=...&detail_path=...&title=...` - الحصول على روابط البث
- `GET /docs` - توثيق Swagger

## مثال على الاستخدام

```bash
# البحث عن فيلم
curl "https://your-app.vercel.app/search?query=The Matrix"

# الحصول على روابط البث
curl "https://your-app.vercel.app/streams?subject_id=123&detail_path=the-matrix&title=The Matrix"
```

## المتطلبات

- Python 3.9+
- FastAPI
- Requests
- Pydantic
