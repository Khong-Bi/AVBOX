# -*- coding: utf-8 -*-
# 51md.me 接口版 - 绕过CF验证
import requests, re, json, sys
from urllib.parse import quote

class Spider:
    def __init__(self):
        # 51md的主站域名经常变，这里做个容灾列表
        self.hosts = [
            "https://51md.me",
            "https://51md.cfd",
            "https://51md.buzz",
        ]
        self.host = self.hosts[0]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://51md.me/",
        }
        self.session = requests.Session()
    
    def init(self, extend=""):
        if extend and extend.startswith('http'):
            self.host = extend.rstrip('/')
        # 自动找可用域名
        for h in self.hosts:
            try:
                r = self.session.get(h, headers=self.headers, timeout=5)
                if r.status_code == 200 and 'vod' in r.text:
                    self.host = h
                    break
            except:
                continue
        return []

    def getName(self):
        return "51麻豆"

    def homeContent(self, filter):
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
        # 首页用分类1的最新数据做推荐，避免请求首页被CF拦
        data = self.categoryContent("1", "1", {}, {})
        return {"class": classes, "list": data.get("list", [])}

    def categoryContent(self, tid, pg, filter, extend):
        # 核心：走 /api.php/provide/vod/ 这个是MACCMS标准API，不走网页
        apis = [
            f"{self.host}/api.php/provide/vod/at/json?ac=list&t={tid}&pg={pg}&h=24",
            f"{self.host}/api.php/provide/vod/?ac=list&t={tid}&pg={pg}",
        ]
        videos = []
        for api_url in apis:
            try:
                r = self.session.get(api_url, headers=self.headers, timeout=10)
                if r.status_code != 200:
                    continue
                # 有些返回的是JSONP
                text = r.text.strip()
                if text.startswith('{'):
                    j = json.loads(text)
                else:
                    # 兼容网页版解析
                    html = text
                    pattern = r'href="(/vod-detail/id/\d+\.html)" title="(.*?)".*?data-original="(.*?)"'
                    vids = re.findall(pattern, html, re.S)
                    for link, title, pic in vids:
                        videos.append({
                            "vod_id": link,
                            "vod_name": title,
                            "vod_pic": pic if pic.startswith('http') else self.host+pic,
                            "vod_remarks": "最新"
                        })
                    if videos:
                        break
                    continue

                for item in j.get('list', []):
                    videos.append({
                        "vod_id": f"/vod-detail/id/{item.get('vod_id')}.html",
                        "vod_name": item.get('vod_name'),
                        "vod_pic": item.get('vod_pic'),
                        "vod_remarks": item.get('vod_remarks') or item.get('vod_time')
                    })
                if videos:
                    break
            except Exception as e:
                print(f"api error {api_url}: {e}", file=sys.stderr)
                continue
        
        # 如果API也失败，降级爬网页
        if not videos:
            try:
                url = f"{self.host}/vod-show/id/{tid}/page/{pg}.html"
                r = self.session.get(url, headers=self.headers, timeout=10)
                r.encoding='utf-8'
                pattern = r'<a href="(/vod-detail/id/\d+\.html)" title="(.*?)".*?data-original="(.*?)"'
                vids = re.findall(pattern, r.text, re.S)
                for link, title, pic in vids:
                    videos.append({
                        "vod_id": link,
                        "vod_name": title,
                        "vod_pic": pic if pic.startswith('http') else self.host+pic,
                        "vod_remarks": ""
                    })
            except:
                pass

        return {"list": videos, "page": int(pg), "pagecount": 99, "limit": 24, "total": 9999}

    def detailContent(self, array):
        vid = array[0]
        url = self.host + vid if vid.startswith('/') else vid
        try:
            r = self.session.get(url, headers=self.headers, timeout=10)
            html = r.text
            m3u8 = ""
            m = re.search(r'"url"\s*:\s*"(https[^"]+\.m3u8)"', html)
            if m:
                m3u8 = m.group(1).replace('\\/', '/')
            else:
                m2 = re.search(r'(https[^\s"\'<>]+\.m3u8)', html)
                if m2:
                    m3u8 = m2.group(1)
            
            title = re.search(r'<h1>(.*?)</h1>', html)
            title = title.group(1) if title else "51md"
            return {"list": [{
                "vod_id": vid,
                "vod_name": title,
                "vod_play_from": "播放",
                "vod_play_url": f"在线${m3u8 or url}"
            }]}
        except:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/vod-search/wd/{quote(key)}/page/{pg}.html"
        try:
            r = self.session.get(url, headers=self.headers, timeout=10)
            r.encoding='utf-8'
            pattern = r'href="(/vod-detail/id/\d+\.html)" title="(.*?)".*?data-original="(.*?)"'
            vids = re.findall(pattern, r.text, re.S)
            videos = []
            for link, title, pic in vids:
                videos.append({
                    "vod_id": link, "vod_name": title,
                    "vod_pic": pic if pic.startswith('http') else self.host+pic
                })
            return {"list": videos, "page": int(pg)}
        except:
            return {"list": []}

    def playerContent(self, flag, id, vipFlags):
        return {"parse": 0, "url": id, "header": self.headers}
