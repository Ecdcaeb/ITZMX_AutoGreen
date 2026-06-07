# ITZMX_AutoGreen
Auto Green for itzmx.com

下面为你提供一套完整的 **GitHub Actions 自动签到+领红包** 方案，包括：

1. 获取完整 Cookie 的教程  
2. 仓库 Secrets 配置方法  
3. 可直接使用的 Python 脚本  
4. 定时触发（北京时间 00:00）的 Workflow 文件  

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

---

## 二、将 Cookie 存入 GitHub Secrets

1. 打开你的 GitHub 仓库页面，点击 **Settings** 选项卡。
2. 左侧菜单选择 **Secrets and variables** → **Actions**。
3. 点击 **New repository secret** 按钮。
4. `Name` 填写：`ITZMX_COOKIE`  
   `Value` 粘贴：刚才复制的完整 Cookie 字符串（**不要加引号，前后无空格**）。
5. 点击 **Add secret** 保存。

---

## 三、注意事项

- **Cookie 保密**：务必使用 Secrets 存储，不要将 Cookie 硬编码在代码中或上传到公共仓库。
- **Cookie 有效期**：论坛的登录 Cookie 可能会过期（如修改密码、长期未登录），若签到失败请及时更新 Secret。
- **执行时间偏差**：GitHub Actions 的 `schedule` 可能在整点附近有几分钟延迟，属于正常现象。
- **每月额度**：公开仓库 Actions 使用免费，私有仓库有 2000 分钟/月额度，此脚本消耗极少。

至此，你的论坛每日自动签到+领红包服务就已经部署完成。
