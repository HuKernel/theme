// 复制提示词使用记录：localStorage 本地计数，无后端、不上传
// 每张卡的「复制提示词」按钮右侧显示「已复制 N 次」（N>0 时才出现）
var ThemeStats = {
  KEY: 'theme_stats_v1',
  _all: function() {
    try { return JSON.parse(localStorage.getItem(this.KEY) || '[]'); } catch (e) { return []; }
  },
  count: function(name) {
    var n = 0;
    this._all().forEach(function(e) { if (e.n === name) n++; });
    return n;
  },
  log: function(name) {
    try {
      var d = this._all();
      d.push({ n: name, t: Date.now() });
      if (d.length > 5000) d = d.slice(-5000); // ponytail: 上限裁剪防 localStorage 撑爆，要完整历史时改导出
      localStorage.setItem(this.KEY, JSON.stringify(d));
    } catch (e) { /* 隐私模式 / 存储被禁时静默跳过，不影响复制本身 */ }
    return this.count(name);
  },
  _slot: function(btn) {
    var s = btn.nextElementSibling;
    if (s && s.classList && s.classList.contains('ts-count')) return s;
    s = document.createElement('span');
    s.className = 'ts-count';
    btn.parentNode.insertBefore(s, btn.nextSibling);
    return s;
  },
  set: function(btn, n) {
    var s = this._slot(btn);
    s.textContent = n > 0 ? '已复制 ' + n + ' 次' : '';
    s.hidden = !(n > 0);
  },
  mark: function(btn) {
    var name = btn.closest('article').querySelector('h2').textContent.trim();
    this.set(btn, this.log(name));
  },
  paint: function() {
    var self = this;
    Array.prototype.forEach.call(document.querySelectorAll('.copy-btn'), function(btn) {
      var card = btn.closest('article');
      if (!card) return;
      var n = self.count(card.querySelector('h2').textContent.trim());
      if (n > 0) self.set(btn, n);
    });
  }
};

// 注入标签样式并渲染初始计数（脚本在 body 底部同步加载，DOM 已就绪）
(function() {
  var css = document.createElement('style');
  css.textContent = '.ts-count{display:inline-flex;align-items:center;margin-left:10px;' +
    'font-size:12px;font-weight:600;color:#6E6E78;vertical-align:middle;}' +
    '.ts-count::before{content:"";width:8px;height:8px;border-radius:50%;' +
    'background:#86CCCA;margin-right:5px;border:1.5px solid #16161D;}';
  document.head.appendChild(css);
  ThemeStats.paint();
})();
