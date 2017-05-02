module.exports = Backbone.Model.extend({
  
  urlRoot: '/channel',

  defaults: {
    key: '',
    color: '',
    rank: 0,
    min: 0,
    max: 0,
    threshold: 1.0,
    leds: []
  },

  initialize: function() {
    this.on('change', function() { this.save(); }, this);
  }
});