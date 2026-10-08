// 全站复制计数：聚合所有访客，数据在服务器端（theme.lhxl.chat/api）
// 卡片「复制提示词」按钮右侧显示「共复制 N 次」（N>0 时才出现）
// file:// 本地打开时 API 不可达，静默不显示，不影响复制功能
var ThemeStats = {
  counts: {},        // paint() 成功后保存全量计数 {风格名: N}
  onupdate: null,    // counts 更新后的回调（目录页用它触发重排）
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
    s.textContent = n > 0 ? '共复制 ' + n + ' 次' : '';
    s.hidden = !(n > 0);
  },
  mark: function(btn) {
    var name = btn.closest('article').querySelector('h2').textContent.trim();
    var self = this;
    fetch('/api/count', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name })
    }).then(function(r) { return r.json(); })
      .then(function(d) {
        if (d && d.count > 0) {
          self.counts[name] = d.count;
          self.set(btn, d.count);
        }
      })
      .catch(function() {});
  },
  paint: function() {
    var self = this;
    fetch('/api/counts')
      .then(function(r) { return r.json(); })
      .then(function(map) {
        self.counts = map || {};
        Array.prototype.forEach.call(document.querySelectorAll('.copy-btn'), function(btn) {
          var card = btn.closest('article');
          if (!card) return;
          var n = self.counts[card.querySelector('h2').textContent.trim()] || 0;
          if (n > 0) self.set(btn, n);
        });
        if (self.onupdate) self.onupdate();
      })
      .catch(function() {});
  }
};

// 注入标签样式并渲染初始计数（脚本在 body 底部同步加载，DOM 已就绪）
(function() {
  var css = document.createElement('style');
  css.textContent = '.ts-count{display:inline-flex;align-items:center;margin-left:10px;' +
    'font-size:12px;font-weight:600;color:#6E6E78;vertical-align:middle;}' +
    '.ts-count::before{content:"";width:8px;height:8px;border-radius:50%;' +
    'background:#FF71CE;margin-right:5px;border:1.5px solid #16161D;}';
  document.head.appendChild(css);
  ThemeStats.paint();
})();
