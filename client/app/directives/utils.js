import debug from 'debug';

export const logger = debug('redash:directives');


// https://javascript.ruanyifeng.com/htmlapi/requestanimationframe.html
// 类似 setTimeOut,但是利用了屏幕默认的60hz刷新频率,效果更好

export const requestAnimationFrame = window.requestAnimationFrame ||
  window.webkitRequestAnimationFrame ||
  window.mozRequestAnimationFrame ||
  window.msRequestAnimationFrame ||
  function requestAnimationFrameFallback(callback) {
    setTimeout(callback, 10);
    // 1000ms/60 = 16ms, 采用10.
    // 主流屏幕, 一秒刷新60次，平均一次16ms.
    // 动画变换，一次间隔16ms
  };



