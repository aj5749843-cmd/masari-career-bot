# مصدر الفيديوهات الترويجية

الفيديوهات الثلاثة في `assets/videos/` مصنوعة بالكامل بالكود: رسوم متحركة بـ HTML وCSS (منها مشاهد ثلاثية الأبعاد)، تُلتقط إطاراً إطاراً بـ Playwright، ثم تُجمع بـ ffmpeg. والموسيقى والمؤثرات مولّدة برمجياً بـ Python، فهي خالية من حقوق النشر.

| الفيديو | المصدر | الصوت | التصدير |
|---|---|---|---|
| `masari-linkedin-4x5.mp4` | `promo.html` | بدون صوت | `render.py` |
| `masari-x-16x9.mp4` | `promo_x.html` | `audio.py` | `renderx.py` |
| `masari-3d-film.mp4` | `film.html` | `audio_film.py` | `renderf.py` (مع ضبابية حركة) |

## إعادة التوليد

```bash
npm install                       # الخطوط
pip install playwright numpy scipy qrcode
# أنشئ ملف الأحداث الصوتية من الصفحة، ثم:
python audio_film.py              # يولّد audio_film.wav
python renderf.py                 # يصدّر film_noaudio.mp4
ffmpeg -i film_noaudio.mp4 -i audio_film.wav -c:v copy -c:a aac -shortest masari-3d-film.mp4
```
