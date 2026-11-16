/* ======================================================================
 * API 地址切换器（v2 自动识别）
 * ----------------------------------------------------------------------
 * 规则：
 *   - 页面跑在 github.io（线上静态站）→ 自动走云端 API（PythonAnywhere）
 *   - 页面跑在本地 127.0.0.1/localhost → 保持空串（同源调用本地引擎）
 *   - 云端地址不可用时，各页面自带降级逻辑，灯显示离线
 * 说明：本文件安装一个 fetch 包装器，把页面里所有 '/api/...' 相对调用
 * 自动改写成 'GANPO_API_BASE + /api/...'，跨域由 api_server.py 的
 * CORS 响应头放行。
 * ====================================================================== */
(function () {
  var host = window.location.hostname || '';
  var isCloudPage = /github\.io$/.test(host) || host.indexOf('pythonanywhere') !== -1;
  var B = isCloudPage ? 'https://ganpo.pythonanywhere.com' : '';
  window.GANPO_API_BASE = B;
  if (!B) { return; }
  var raw = window.fetch;
  window.fetch = function (u, o) {
    if (typeof u === 'string' && u.charAt(0) === '/') { u = B + u; }
    return raw.call(window, u, o);
  };
})();
