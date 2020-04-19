/*
    Based on code from
    https://www.sitepoint.com/build-javascript-countdown-timer-no-dependencies/
    */

function getTimeRemaining(endtime) {
  var current = Date.now();
  diff = endtime - current;
  t = Math.abs(diff);

  return {
    diff: diff / 1000,
    total: t / 1000,
    days: Math.floor(t / (1000 * 60 * 60 * 24)),
    hours: Math.floor((t / (1000 * 60 * 60)) % 24),
    minutes: Math.floor((t / 1000 / 60) % 60),
    seconds: Math.floor((t / 1000) % 60),
  };
}

function color(time) {
  if (time > 0) return "success";
  if (time < -300) return "danger";
  return "warning";
}

function updateElement(ele, t, value, padded) {
  span = ele.querySelector("span");
  div = ele.querySelector("div");

  span.innerHTML = padded ? ("0" + value).slice(-2) : value;
  span.className = `bg-${color(t.diff)}`;
  div.className = `smalltext text-${color(t.diff)}`;
}

function initializeClock(id, endtime) {
  var clock = document.getElementById(id);
  var daysSpan = clock.querySelector(".days");
  var hoursSpan = clock.querySelector(".hours");
  var minutesSpan = clock.querySelector(".minutes");
  var secondsSpan = clock.querySelector(".seconds");

  function updateClock() {
    var t = getTimeRemaining(endtime);

    updateElement(daysSpan, t, t.days, false);
    updateElement(hoursSpan, t, t.hours, true);
    updateElement(minutesSpan, t, t.minutes, true);
    updateElement(secondsSpan, t, t.seconds, true);

    clock.className = `card card-${color(t.diff)}`;
  }

  updateClock(); // run function once at first to avoid delay
  var timeinterval = setInterval(updateClock, 1000);
}
