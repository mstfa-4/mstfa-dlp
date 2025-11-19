import re
from .common import InfoExtractor
from ..utils import (
    parse_duration,
    parse_count,
    str_to_int,
    unified_strdate,
    url_or_none,
)

class PimpBunnyIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?pimpbunny\.com/videos/(?P<id>[^/?#&]+)'
    _TESTS = [{
        'url': 'https://pimpbunny.com/videos/arina-fox-sex-and-massage/',
        'info_dict': {
            'id': 'arina-fox-sex-and-massage',
            'ext': 'mp4',
            'title': 'Arina Fox Sex And Massage',
            'age_limit': 18,
        },
        'params': {
            'skip_download': True,
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # 1. استخراج عنوان ویدیو
        # از تگ h1 با کلاس pb-video-title استفاده می‌کنیم
        title = self._html_search_regex(
            r'<h1[^>]+class=["\']pb-video-title["\'][^>]*>([^<]+)</h1>',
            webpage, 'title', default=None
        ) or self._html_search_meta(['og:title', 'twitter:title'], webpage, 'title')

        # 2. استخراج لینک‌های دانلود (کیفیت‌های مختلف)
        formats = []
        
        # جستجو در بخش پاپ‌آپ دانلود که در فایل شما مشاهده شد
        # الگو: <a class="pb-small-heading" href="...">MP4 1080p</a>
        download_links = re.findall(
            r'<a[^>]+class=["\']pb-small-heading["\'][^>]+href=["\']([^"\']+)["\'][^>]*>MP4\s+(\d+p)</a>',
            webpage
        )

        for video_url, height_str in download_links:
            height = int(height_str.replace('p', ''))
            formats.append({
                'url': video_url,
                'format_id': height_str,
                'height': height,
                'ext': 'mp4',
            })

        # اگر لینک‌های دانلود پیدا نشد، تلاش برای پیدا کردن تگ <video> اصلی
        if not formats:
            video_src = self._search_regex(
                r'<video[^>]+src=["\']([^"\']+)["\']', webpage, 'video src', default=None
            )
            if video_src:
                formats.append({
                    'url': video_src,
                    'format_id': 'source',
                    'ext': 'mp4',
                })

        # self._sort_formats(formats)

        # 3. استخراج متادیتای دیگر
        thumbnail = self._html_search_meta(['og:image', 'twitter:image'], webpage, 'thumbnail')
        
        # مدت زمان از متاتگ video:duration (در ثانیه)
        duration = parse_duration(self._html_search_meta('video:duration', webpage))
        
        # تعداد بازدید از کلاس pb-video-views
        view_count_str = self._html_search_regex(
            r'<div[^>]+class=["\']pb-video-views["\'][^>]*>.*?<span>([\d.,]+[Kk]?)</span>',
            webpage, 'view count', fatal=False
        )
        view_count = parse_count(view_count_str) if view_count_str else None

        # آپلود کننده (مدل)
        uploader = self._html_search_regex(
            r'<a[^>]+class=["\']pb-uploaded-name[^"\']*["\'][^>]*>([^<]+)</a>',
            webpage, 'uploader', fatal=False
        )

        # دسته‌بندی‌ها (Categories)
        categories = []
        for cat in re.findall(r'<a[^>]+href=["\'][^"\']*categories[^"\']*["\'][^>]*><span[^>]*>([^<]+)</span>', webpage):
            categories.append(cat)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'thumbnail': thumbnail,
            'duration': duration,
            'view_count': view_count,
            'uploader': uploader,
            'categories': categories,
            'age_limit': 18,
            'http_headers': {
                'Referer': url,
            }
        }
