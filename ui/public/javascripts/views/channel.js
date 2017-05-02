var ColorView = require('./color.js');
var LedsView  = require('./leds.js');

module.exports = Backbone.View.extend({

  template: require('../../../views/partials/channel.html'),

  events: {
    'change input[name=rank]': 'change_rank',
    'change input[name=threshold]': 'change_threshold',
    'change input[name=min]': 'change_min',
    'change input[name=max]': 'change_max',
    'click span.change-color': 'change_color',
    'click a[rel=leds]': 'change_leds'
  },

  initialize: function() {
    this.render();
    this.model.on('change', this.render, this);
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    $('[data-toggle=tooltip]').tooltip();
  },

  change_min: function(e) {
    var val = $(e.target).val();
    this.model.set('min', parseInt(val));
  },

  change_max: function(e) {
    var val = $(e.target).val();
    this.model.set('min', parseInt(val));
  },

  change_rank: function(e) {
    var val = $(e.target).val();
    this.model.set('rank', parseInt(val));
  },

  change_threshold: function(e) {
    var val = $(e.target).val();
    this.model.set('threshold', parseInt(val));
  },

  change_color: function() {
    $('body').append('<div class="modal"></div>');
    var color_view = new ColorView({model: this.model});
  },

  change_leds: function(e) {
    e.preventDefault();
    $('body').append('<div class="modal"></div>');
    var leds_view = new LedsView({model: this.model});
  }
})