# ITZMX_AutoGreen
Auto Green for itzmx.com

---

## 一、获取完整的登录 Cookie

1. 用 Edge 浏览器打开论坛并登录，然后进入签到页面：  
   `https://bbs.itzmx.com/dsu_paulsign-sign.html`
2. 按 `F12` 打开开发者工具，切换到 **网络（Network）** 标签页。
3. 刷新页面（`F5`），在左侧请求列表中找到第一个请求（通常是 `dsu_paulsign-sign.html`），点击它。
4. 在右侧面板中找到 **请求标头（Request Headers）**，找到 `Cookie:` 开头的行。
5. **完整复制** `Cookie:` 后面的整个字符串（不要复制“Cookie: ”这个单词本身），例如：
   ```
   UpTn_8a61_smile=20D1; UpTn_8a61_auth=xxxxx; UpTn_8a61_saltkey=yyyy; ...
   ```
   这串值会很长，一定全部复制。
6. 这就是需要保存的 Cookie，稍后会存入 GitHub Secrets。
7. 格式：`{"昵称或标签": "该账号的完整cookie", "第二个账号": "第二个cookie"}`  
例如：
```json
{"大号":"UpTn_8a61_auth=abc; UpTn_8a61_saltkey=xyz; ...", "小号":"UpTn_8a61_auth=def; ..."}
```
- **键名（name）** 用来在日志中区分账户，可任意命名。
- **值** 就是每个账号对应的 Cookie 字符串，不要外加引号。
- 注意 JSON 语法：用英文双引号，字符串内若有双引号需要转义（通常 cookie 不会包含双引号）。

---

## 二、将 Cookie 存入 GitHub Secrets

1. 打开你的 GitHub 仓库页面，点击 **Settings** 选项卡。
2. 左侧菜单选择 **Secrets and variables** → **Actions**。
3. 点击 **New repository secret** 按钮。
4. `Name` 填写：`ITZMX_COOKIE`  
   `Value` 粘贴：刚才复制的完整 Json 字符串（**不要加引号，前后无空格**）。
5. 点击 **Add secret** 保存。

---

## 三、注意事项

- **Cookie 保密**：务必使用 Secrets 存储，不要将 Cookie 硬编码在代码中或上传到公共仓库。
- **Cookie 有效期**：论坛的登录 Cookie 可能会过期（如修改密码、长期未登录），若签到失败请及时更新 Secret。
- **执行时间偏差**：GitHub Actions 的 `schedule` 可能在整点附近有几分钟延迟，属于正常现象。
- **每月额度**：公开仓库 Actions 使用免费，私有仓库有 2000 分钟/月额度，此脚本消耗极少。

至此，宝宝你的论坛每日自动签到+领红包服务就已经部署完成。


已按要求改造：支持多个账户（`ITZMX_COOKIE` 为 JSON 对象），逐个执行签到和任务，失败时输出账户名，所有账户执行后只要有失败就退出 1。

---

## 🔔 运行效果示例

成功时输出：
```
========================================
▶ 正在处理账户: 大号
[大号] 📌 开始签到...
[大号]    formhash = ce2f9c0f
[大号] ✅ 签到成功！
[大号] 📌 开始处理红包任务...
[大号]    formhash = ce2f9c0f
[大号] 🎉 红包任务领取成功！
========================================
▶ 正在处理账户: 小号
[小号] 📌 开始签到...
[小号]    formhash = a1b2c3d4
[小号] ✅ 签到成功！
[小号] 📌 开始处理红包任务...
[小号] ⏸️  当前不可申请（已申请或未到时间）

🎉 所有账户签到 & 红包处理完成！
```

若某个账户 Cookie 失效，最终会退出 1 并打印：
```
❌ 以下账户操作失败，请检查 Cookie 是否有效：
   - [小号] 签到: 签到失败：未登录
```

这样你就能精准定位是哪个账号需要更新 Cookie。
