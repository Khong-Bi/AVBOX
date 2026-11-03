# -*- coding: utf-8 -*-
# 51md.me - TVBox Python 爬虫版 By AVBOX
# 适配 TVBox FongMi / qiaoji / Takagen99 Python版

import re
import requests
from urllib.parse import quote

class Spider:
    def __init__(self):
        self.host = "https://51md.me"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.host + "/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.session = requests.Session()

    def getName(self):
        return "51麻豆"

    def init(self, extend=""):
        if extend:
            self.host = extend.rstrip('/')
        return []

    def homeContent(self, filter):
        # 分类写死，网站分类ID不变
        classes = [
            {"type_id": "1", "type_name": "麻豆原创"},
            {"type_id": "2", "type_name": "天美传媒"},
            {"type_id": "3", "type_name": "蜜桃传媒"},
            {"type_id": "4", "type_name": "91制片厂"},
            {"type_id": "5", "type_name": "精东影业"},
            {"type_id": "6", "type_name": "海角社区"},
            {"type_id": "7", "type_name": "杏吧原创"},
            {"type_id": "8", "type_name": "糖心Vlog"},
        ]
        # 首页推荐
        try:
            r = self.session.get(self.host, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            html = r.text
            # 解析 ul.vod-list li
            pattern = r'<li.*?><a href="(/vod-detail/id/\d+\.html)" title="(.*?)".*?<img.*?data-original="(.*?)".*?<div class="text">(.*?)</div>'
            vids = re.findall(pattern, html, re.S)
            videos = []
            for link, title, pic, remark in vids[:20]:
                videos.append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": pic if pic.startswith('http') else self.host + pic,
                    "vod_remarks": remark.strip()
                })
            return {"class": classes, "list": videos}
        except Exception as e:
            return {"class": classes, "list": []}

    def categoryContent(self, tid, pg, filter, extend):
        url = f"{self.host}/vod-show/id/{tid}/page/{pg}.html"
        try:
            r = self.session.get(url, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            html = r.text
            pattern = r'<li.*?><a href="(/vod-detail/id/\d+\.html)" title="(.*?)".*?<img.*?data-original="(.*?)".*?<div class="text">(.*?)</div>'
            vids = re.findall(pattern, html, re.S)
            videos = []
            for link, title, pic, remark in vids:
                videos.append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": pic if pic.startswith('http') else self.host + pic,
                    "vod_remarks": remark.strip()
                })
            # 判断有没有下一页
            has_more = '下一页' in html or f'page/{int(pg)+1}' in html
            return {"list": videos, "page": int(pg), "pagecount": 9999 if has_more else int(pg), "limit": 24, "total": 99999}
        except:
            return {"list": [], "page": int(pg)}

    def detailContent(self, array):
        vid = array[0]  # /vod-detail/id/123.html
        url = self.host + vid if vid.startswith('/') else vid
        try:
            r = self.session.get(url, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            html = r.text
            title = re.search(r'<h1.*?>(.*?)</h1>', html)
            title = title.group(1).strip() if title else "51md"
            pic = re.search(r'class="vod-img".*?data-original="(.*?)"', html, re.S)
            pic = pic.group(1) if pic else ""
            if pic and not pic.startswith('http'):
                pic = self.host + pic
            content = re.search(r'<div class="content">(.*?)</div>', html, re.S)
            content = re.sub(r'<[^>]+>', '', content.group(1)).strip() if content else ""
            
            # 解析播放列表
            # 这种站一般是 "url":"https://...m3u8" 藏在JS里
            play_url = re.search(r'"url"\s*:\s*"(https[^"]+\.m3u8)"', html)
            if play_url:
                m3u8 = play_url.group(1).replace('\\/', '/').replace('\\', '')
            else:
                # 备用，从 iframe 拿
                iframe = re.search(r'<iframe.*?src="(.*?)"', html)
                m3u8 = ""
                if iframe:
                    iframe_url = iframe.group(1)
                    if not iframe_url.startswith('http'):
                        iframe_url = self.host + iframe_url
                    r2 = self.session.get(iframe_url, headers=self.headers, timeout=10)
                    m2 = re.search(r'(https[^\s"\'<>]+\.m3u8)', r2.text)
                    if m2:
                        m3u8 = m2.group(1)
            
            vod = {
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": content,
                "vod_play_from": "51麻豆",
                "vod_play_url": f"正片${m3u8 if 'm3u8' in locals() else url}"
            }
            return {"list": [vod]}
        except Exception as e:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/vod-search/wd/{quote(key)}/page/{pg}.html"
        return self.categoryContent("", pg, {}, {}) if False else self._search(url)

    def _search(self, url):
        try:
            r = self.session.get(url, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            html = r.text
            pattern = r'<li.*?><a href="(/vod-detail/id/\d+\.html)" title="(.*?)".*?<img.*?data-original="(.*?)".*?<div class="text">(.*?)</div>'
            vids = re.findall(pattern, html, re.S)
            videos = []
            for link, title, pic, remark in vids:
                videos.append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": pic if pic.startswith('http') else self.host + pic,
                    "vod_remarks": remark.strip()
                })
            return {"list": videos, "page": 1}
        except:
            return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        # id 就是 m3u8 链接
        return {"parse": 0, "url": id, "header": self.headers}

    def localProxy(self, param):
        return [200, "video/mp2t", "", ""]
