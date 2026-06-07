import os
import re
import sys
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def get_cookie():
    cookie = os.environ.get("ITZMX_COOKIE")
    if not cookie:
        print("❌ 环境变量 ITZMX_COOKIE 未设置", file=sys.stderr)
        sys.exit(1)
    return cookie.strip().strip("'\"")

def parse_formhash(html):
    m = re.search(r'name="formhash"\s+value="([a-f0-9]+)"', html)
    if not m:
        raise RuntimeError("未找到 formhash，Cookie 可能已失效")
    return m.group(1)

def sign(session, cookie_str):
    print("📌 开始签到...")
    url = "https://bbs.itzmx.com/dsu_paulsign-sign.html"
    post_url = "https://bbs.itzmx.com/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1"

    resp = session.get(url, headers={**HEADERS, "Cookie": cookie_str})
    resp.encoding = "gbk"
    html = resp.text

    if "今天已签到" in html:
        print("✅ 今天已经签到过了，跳过")
        return

    formhash = parse_formhash(html)
    print(f"   formhash = {formhash}")

    data = {
        "formhash": formhash,
        "qdxq": "kx",
        "qdmode": "1",
        "todaysay": "签到",
    }
    resp2 = session.post(post_url, data=data,
                         headers={**HEADERS, "Cookie": cookie_str, "Referer": url})
    resp2.encoding = "gbk"

    if any(kw in resp2.text for kw in ("签到成功", "恭喜你签到成功")):
        print("✅ 签到成功！")
    else:
        msg = re.search(r'<div class="c">(.*?)</div>', resp2.text, re.DOTALL)
        err_msg = msg.group(1).strip() if msg else "未知错误"
        print(f"❌ 签到失败：{err_msg}", file=sys.stderr)
        sys.exit(1)

def apply_task(session, cookie_str):
    print("📌 开始处理红包任务...")
    view_url = "https://m.itzmx.com/home.php?mod=task&do=view&id=2"
    apply_url = "https://m.itzmx.com/home.php?mod=task&do=apply&id=2"

    resp = session.get(view_url, headers={**HEADERS, "Cookie": cookie_str})
    resp.encoding = "gbk"
    html = resp.text

    if "已完成" in html:
        print("✅ 红包任务已完成，无需重复申请")
        return
    if "现在可以再次申请" not in html and "立即申请" not in html:
        print("⏸️ 当前不可申请（可能已申请过或未到时间）")
        return

    formhash = parse_formhash(html)
    print(f"   formhash = {formhash}")

    resp2 = session.post(apply_url, data={"formhash": formhash},
                         headers={**HEADERS, "Cookie": cookie_str, "Referer": view_url})
    resp2.encoding = "gbk"

    if any(kw in resp2.text for kw in ("任务申请成功", "恭喜您，任务已成功完成")):
        print("🎉 红包任务领取成功！")
    else:
        msg = re.search(r'<div class="c">(.*?)</div>', resp2.text, re.DOTALL)
        err_msg = msg.group(1).strip() if msg else "未知错误"
        print(f"❌ 任务领取失败：{err_msg}", file=sys.stderr)
        sys.exit(1)

def main():
    cookie_str = get_cookie()
    with requests.Session() as session:
        try:
            sign(session, cookie_str)
        except Exception as e:
            print(f"❌ 签到异常：{e}", file=sys.stderr)
            sys.exit(1)

        try:
            apply_task(session, cookie_str)
        except Exception as e:
            print(f"❌ 任务异常：{e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
