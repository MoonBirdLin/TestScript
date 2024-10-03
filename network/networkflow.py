import mitmproxy.http
from mitmproxy.connection import Server
from mitmproxy.net.server_spec import ServerSpec
from mitmproxy import ctx
import hashlib
import json
import urllib.parse
import chardet
import time


class Log:

    bad_domain = {}

    def __init__(self):
        self.num = 0
        self.output = "+++++"

    def request(self, flow: mitmproxy.http.HTTPFlow):
        self.num = self.num + 1

        parsed_result= urllib.parse.urlsplit(flow.request.url)
        if parsed_result.netloc in Log.bad_domain:
            return

        time_local = time.localtime(flow.request.timestamp_start)
        dt = time.strftime("%Y-%m-%d_%H%M%S",time_local)

        key = dt
        # key = str(flow.request.timestamp_start) + hashlib.md5(flow.request.raw_content).hexdigest()[:18]
        
        h = {}
        referrer = "-"
        header = flow.request.headers
        for k in header.keys():
            value = header.get_all(k)
            vstr = value[0]
            if len(value) > 1:
                for i in range(1,len(value)-1):
                    vstr = vstr + value[i]
            h[k] = vstr
            if k=="referrer": 
                referrer = vstr

        
        uri = ""
        if parsed_result.query != "":
            uri = parsed_result.path + "?" + parsed_result.query
        if parsed_result.fragment != "":
            uri = uri + "#" + parsed_result.fragment

        try:
            flow.request.decode()
        except:
            pass

        encoding = chardet.detect(flow.request.content)['encoding']
        if encoding == None: encoding = "utf-8"

        try:
            post_body = flow.request.content.decode(encoding)
        except:
            post_body = str(flow.request.content)

        content = {
            "domain" : parsed_result.netloc,
            "host" : flow.request.host,
            "platform" : "android",
            "headers" : h,
            "method" : flow.request.method,
            "referrer" : referrer,
            "uri" : uri,
            "ts" : flow.request.timestamp_start,
            "post_body" : post_body,
            "label" : []
        }

        # 本地储存的json文件地址
        with open(self.output,'r+') as f:
            initial = None
            try:
                initial = json.load(f)
            except:
                initial = {}
            initial[key] = content
            f.seek(0)
            f.truncate()
            json.dump(initial, f, indent=4)

        ctx.log.info("We've seen %d flows" % self.num)

        # 转发到vpn的端口
        # address = ('127.0.0.1', 7890)  
        # is_proxy_change = address != flow.server_conn.via
        # server_connection_already_open = flow.server_conn.timestamp_start is not None
        # if is_proxy_change and server_connection_already_open:
        # # server_conn already refers to an existing connection (which cannot be modified),
        # # so we need to replace it with a new server connection object.
        #     flow.server_conn = Server(address=flow.server_conn.address)
        #     flow.server_conn.via = ServerSpec("http", address)


addons = [
    Log()
]