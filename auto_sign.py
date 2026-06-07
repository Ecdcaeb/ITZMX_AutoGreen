import os
import re
import sys
import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def get_accounts():
    """解析 ITZMX_COOKIE 环境变量，返回 {name: cookie_str} 字典"""
    raw = os.environ.get("ITZMX_COOKIE")
    if not raw:
        print("❌ 环境变量 ITZMX_COOKIE 未设置", file=sys.stderr)
        sys.exit(1)

    raw = raw.strip()
    # 兼容纯字符串模式（单账号），自动包装为 default
    if not raw.startswith("{"):
        print("ℹ️  检测到单账号 cookie 格式，已自动命名为 'default'")
        return {"default": raw.strip("'\"")}

    try:
        accounts = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ ITZMX_COOKIE 不是合法的 JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(accounts, dict):
        print("❌ ITZMX_COOKIE 必须是 JSON 对象（例如 {\"name\":\"cookie...\"}）", file=sys.stderr)
        sys.exit(1)

    # 清理每个 cookie 值两端的引号/空格
    cleaned = {}
    for name, cookie in accounts.items():
        cleaned[name] = cookie.strip().strip("'\"")
    return cleaned


def parse_formhash(html):
    m = re.search(r'name="formhash"\s+value="([a-f0-9]+)"', html)
    if not m:
        raise RuntimeError("未找到 formhash，Cookie 可能已失效")
    return m.group(1)


def sign(session, cookie_str, name):
    print(f"[{name}] 📌 开始签到...")
    url = "https://bbs.itzmx.com/dsu_paulsign-sign.html"
    post_url = "https://bbs.itzmx.com/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1"

    resp = session.get(url, headers={**HEADERS, "Cookie": cookie_str})
    resp.encoding = "gbk"
    html = resp.text

    if "今天已签到" in html:
        print(f"[{name}] ✅ 今天已经签到过了")
        return

    formhash = parse_formhash(html)
    print(f"[{name}]    formhash = {formhash}")

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
        print(f"[{name}] ✅ 签到成功！")
    else:
        msg = re.search(r'<div class="c">(.*?)</div>', resp2.text, re.DOTALL)
        err = msg.group(1).strip() if msg else "未知错误"
        raise RuntimeError(f"签到失败：{err}")


def apply_task(session, cookie_str, name):
    print(f"[{name}] 📌 开始处理红包任务...")
    view_url = "https://m.itzmx.com/home.php?mod=task&do=view&id=2"
    apply_url = "https://m.itzmx.com/home.php?mod=task&do=apply&id=2"

    resp = session.get(view_url, headers={**HEADERS, "Cookie": cookie_str})
    resp.encoding = "gbk"
    html = resp.text

    if "已完成" in html:
        print(f"[{name}] ✅ 红包任务已完成")
        return
    if "现在可以再次申请" not in html and "立即申请" not in html:
        print(f"[{name}] ⏸️  当前不可申请（已申请或未到时间）")
        return

    formhash = parse_formhash(html)
    print(f"[{name}]    formhash = {formhash}")

    resp2 = session.post(apply_url, data={"formhash": formhash},
                         headers={**HEADERS, "Cookie": cookie_str, "Referer": view_url})
    resp2.encoding = "gbk"

    if any(kw in resp2.text for kw in ("任务申请成功", "恭喜您，任务已成功完成")):
        print(f"[{name}] 🎉 红包任务领取成功！")
    else:
        msg = re.search(r'<div class="c">(.*?)</div>', resp2.text, re.DOTALL)
        err = msg.group(1).strip() if msg else "未知错误"
        raise RuntimeError(f"任务领取失败：{err}")


def main():
    accounts = get_accounts()
    failed = []

    for name, cookie in accounts.items():
        print(f"\n{'='*40}")
        print(f"▶ 正在处理账户: {name}")
        with requests.Session() as session:
            try:
                sign(session, cookie, name)
            except Exception as e:
                print(f"[{name}] ❌ 签到异常: {e}", file=sys.stderr)
                failed.append((name, "签到", str(e)))
                # 签到失败后仍尝试任务？（一般没必要，直接继续下一个账户）
                continue

            try:
                apply_task(session, cookie, name)
            except Exception as e:
                print(f"[{name}] ❌ 任务异常: {e}", file=sys.stderr)
                failed.append((name, "任务", str(e)))

    if failed:
        print("\n❌ 以下账户操作失败，请检查 Cookie 是否有效：")
        for name, step, reason in failed:
            print(f"   - [{name}] {step}: {reason}")
        sys.exit(1)
    else:
        print("\n🎉 所有账户签到 & 红包处理完成！")


if __name__ == "__main__":
    main()
