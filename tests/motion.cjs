// Exercise the shipped enhancement script under both system motion preferences.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('main.js', 'utf8');
function mount(reduced) {
  const classes = new Set();
  const events = {};
  const media = { matches: reduced, addEventListener(_, fn) { this.onChange = fn; } };
  const diagram = { offsetWidth: 500, classList: { add: name => classes.add(name), remove: name => classes.delete(name) } };
  const replay = { hidden: true, addEventListener(name, fn) { events[name] = fn; } };
  let observer;
  class Observer {
    constructor(fn) { this.callback = fn; observer = this; }
    observe(target) { this.target = target; }
    disconnect() { this.disconnected = true; }
  }
  const document = {
    querySelector(selector) { return selector === '.construction' ? diagram : replay; },
    querySelectorAll() { return []; },
    addEventListener() {}
  };
  vm.runInNewContext(source, { document, window: { matchMedia: () => media, IntersectionObserver: Observer }, IntersectionObserver: Observer });
  return { classes, replay, media, events, observer, diagram };
}
let app = mount(true);
app.observer.callback([{ isIntersecting: true }]);
assert.equal(app.replay.hidden, true, 'Reduced motion hides replay');
assert.equal(app.classes.size, 0, 'Reduced motion never starts a drawing');
app.events.click();
assert.equal(app.classes.size, 0, 'Reduced motion also suppresses manual replay');
app = mount(false);
assert.equal(app.classes.size, 0, 'Animation waits until the diagram is visible');
app.observer.callback([{ isIntersecting: false }]);
assert.equal(app.classes.size, 0, 'Offscreen observation does not start animation');
app.observer.callback([{ isIntersecting: true }]);
assert.ok(app.classes.has('is-drawing'), 'Visible diagram starts its reveal');
assert.equal(app.observer.disconnected, true, 'Automatic reveal runs only once');
app.media.matches = true;
app.media.onChange();
assert.equal(app.replay.hidden, true, 'Changing the preference hides replay');
assert.equal(app.classes.size, 0, 'Changing the preference stops the animation');
console.log('Motion preference checks passed (9 assertions).');
