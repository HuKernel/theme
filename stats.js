// 全站复制计数 + 在线人数：数据在服务器端（theme.lhxl.chat/api）
// - 有复制按钮的页面显示「共复制 N 次」（N>0 时才出现）
// - 所有页面心跳统计在线人数，在 .ts-online 元素处显示「N 人在线」
// file:// 本地打开时 API 不可达，静默跳过，不影响页面本身
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
    if (!document.querySelector('.copy-btn')) return; // 样张页无复制按钮，不拉计数
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
  },
  sid: function() {
    var sid;
    try {
      sid = localStorage.getItem('theme_sid');
      if (!sid) {
        sid = 's' + Date.now() + Math.random().toString(36).slice(2, 10);
        localStorage.setItem('theme_sid', sid);
      }
      return sid;
    } catch (e) {
      return 's' + Date.now() + Math.random().toString(36).slice(2, 10);
    }
  },
  paintOnline: function(n) {
    Array.prototype.forEach.call(document.querySelectorAll('.ts-online'), function(el) {
      el.textContent = n > 0 ? n + ' 人在线' : '';
      el.hidden = !(n > 0);
    });
  },
  online: function() {
    var self = this;
    var beat = function() {
      fetch('/api/heartbeat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sid: self.sid() })
      }).then(function(r) { return r.json(); })
        .then(function(d) { if (d && d.online > 0) self.paintOnline(d.online); })
        .catch(function() {});
    };
    beat();
    setInterval(beat, 60000);
    setInterval(function() {
      fetch('/api/online').then(function(r) { return r.json(); })
        .then(function(d) { if (d && d.online > 0) self.paintOnline(d.online); })
        .catch(function() {});
    }, 30000);
  }
};

// 注入样式并启动（脚本在 body 底部同步加载，DOM 已就绪）
(function() {
  var css = document.createElement('style');
  css.textContent = '.ts-count{display:inline-flex;align-items:center;margin-left:10px;' +
    'font-size:12px;font-weight:600;color:#6E6E78;vertical-align:middle;}' +
    '.ts-count::before{content:"";width:8px;height:8px;border-radius:50%;' +
    'background:#FF71CE;margin-right:5px;border:1.5px solid #16161D;}' +
    '.ts-online{display:inline-flex;align-items:center;font-size:12px;font-weight:600;' +
    'color:#6E6E78;border:1.5px solid rgba(22,22,29,.18);border-radius:999px;' +
    'padding:3px 12px;background:#fff;vertical-align:middle;}' +
    '.ts-online::before{content:"";width:8px;height:8px;border-radius:50%;' +
    'background:#3FB950;margin-right:6px;}';
  document.head.appendChild(css);
  ThemeStats.paint();
  ThemeStats.online();
})();
