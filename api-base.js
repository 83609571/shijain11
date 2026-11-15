/* ======================================================================
 * API 地址切换器
 * ----------------------------------------------------------------------
 * 本地演示：保持空串（同源调用，什么也不用改）。
 * 云端部署（Render）后：把下面赋值改成云端地址并上传本文件，例如：
 *   window.GANPO_API_BASE = 'https://ganpo-api.onrender.com';
 * 说明：本文件安装一个 fetch 包装器，把页面里所有 '/api/...' 相对调用
 * 自动改写成 'GANPO_API_BASE + /api/...'，跨域由 api_server.py 的
 * CORS 响应头放行。没有云端时留空，行为与从前完全一致。
 * ====================================================================== */
window.GANPO_API_BASE = '';
(function () {
  var B = window.GANPO_API_BASE;
  if (!B) { return; }
  var raw = window.fetch;
  window.fetch = function (u, o) {
    if (typeof u === 'string' && u.charAt(0) === '/') { u = B + u; }
    return raw.call(window, u, o);
  };
})();
