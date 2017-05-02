var express = require('express');
var pyshell = require('python-shell');
var child_process = require('child_process');
var fs = require('fs');
var ini = require('ini');
var router = express.Router();

var shairport_ps = child_process.spawn('shairport', ['-a', 'SquidRadio']);
var lightshow_ps = false;

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', {});
});

/* GET shairport */
router.get('/shairport', function(req, res, next) {
  res.send({is_on: !!shairport_ps});
});

/* POST turn on/off shairport */
router.post('/shairport', function(req, res, next) {
  if (req.body.is_on && !shairport_ps)
  {
    shairport_ps = child_process.spawn('shairport', ['-a', 'SquidRadio']);
  }
  else if (!req.body.is_on && !!shairport_ps)
  {
    shairport_ps.kill('SIGINT');
    shairport_ps = false;
  }

  res.send({is_on: !!shairport_ps});
});

/* GET lightshow */
router.get('/lightshow', function(req, res, next) {
  res.send({is_on: !!lightshow_ps});
});

/* POST turn on/off light show */
router.post('/lightshow', function(req, res, next) {
  if (req.body.is_on && !lightshow_ps)
  {
    lightshow_ps = new pyshell('../lightshow.py');
  }
  else if (!req.body.is_on && !!lightshow_ps)
  {
    lightshow_ps.send('kill');
    lightshow_ps = false;
  }

  res.send({is_on: !!lightshow_ps});
});

/* GET channels */
router.get('/channels', function(req, res, next) {
  var config = ini.parse(fs.readFileSync('../config/temp.ini', 'utf-8'));
  var channels = [];
  Object.keys(config).forEach(function(key) {
    var channel = config[key];
    channel.leds = config[key].leds.split(', ').map(function(x) { return parseInt(x); });
    channel.rank = parseInt(config[key].rank);
    channel.min = parseInt(config[key].min);
    channel.max = parseInt(config[key].max);
    channel.threshold = parseInt(100 * parseFloat(config[key].threshold));
    channel.key = key;
    channels.push(channel);
  });
  res.send(channels);
});

/* POST channel */
router.post('/channel', function(req, res, next) {
  var config = ini.parse(fs.readFileSync('../config/temp.ini', 'utf-8'));
  var channel = req.body;
  var key = channel.key;
  config[key].leds = channel.leds.join(', ') + ',';
  config[key].rank = channel.rank;
  config[key].min = channel.min;
  config[key].max = channel.max;
  config[key].threshold = parseFloat(channel.threshold) / 100;
  config[key].color = channel.color;
  fs.writeFileSync('../config/temp.ini', ini.stringify(config));
  res.sendStatus(200);
});

module.exports = router;
