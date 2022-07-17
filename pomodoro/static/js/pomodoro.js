/*
    Based on code from
    https://www.sitepoint.com/build-javascript-countdown-timer-no-dependencies/
    */

class Countdown {
  constructor(ele, endtime) {
    this.clock = ele;
    this.defaultClass = this.clock.className;

    this.endtime = new Date(ele.dataset.countdown);

    this.daysSpan = this.clock.querySelector(".days");
    this.hoursSpan = this.clock.querySelector(".hours");
    this.minutesSpan = this.clock.querySelector(".minutes");
    this.secondsSpan = this.clock.querySelector(".seconds");

    // Call updateClock once to get things started
    this.updateClock();

    // Update our countdown every second
    var t = this;
    var timeinterval = setInterval(function () {
      t.updateClock();
    }, 1000);
  }

  getTimeRemaining() {
    var current = Date.now();
    var diff = this.endtime - current;
    var t = Math.abs(diff);

    return {
      diff: diff / 1000,
      total: t / 1000,
      days: Math.floor(t / (1000 * 60 * 60 * 24)),
      hours: Math.floor((t / (1000 * 60 * 60)) % 24),
      minutes: Math.floor((t / 1000 / 60) % 60),
      seconds: Math.floor((t / 1000) % 60),
    };
  }

  color(time) {
    if (time > 0) return "success";
    if (time < -300) return "danger";
    return "warning";
  }
  updateElement(ele, t, value, padded) {
    var span = ele.querySelector("span");
    var div = ele.querySelector("div");

    span.innerHTML = padded ? ("0" + value).slice(-2) : value;
    span.className = `bg-${this.color(t.diff)}`;
    div.className = `smalltext text-${this.color(t.diff)}`;
  }

  updateClock() {
    var t = this.getTimeRemaining(this.endtime);

    this.updateElement(this.daysSpan, t, t.days, false);
    this.updateElement(this.hoursSpan, t, t.hours, true);
    this.updateElement(this.minutesSpan, t, t.minutes, true);
    this.updateElement(this.secondsSpan, t, t.seconds, true);
    this.clock.className = `${this.defaultClass} card-${this.color(t.diff)}`;
  }
}

document.querySelectorAll("[data-countdown]").forEach(function (ele) {
  new Countdown(ele);
});
