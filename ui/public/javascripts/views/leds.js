module.exports = Backbone.View.extend({

  el: '.modal',

  template: require('../../../views/partials/leds.html'),

  leds_old: [],

  events: {
    'click button.btn-save': 'save',
    'click button.close': 'close',
    'change input[type=checkbox]': 'toggle_led'
  },

  initialize: function() {
    this.render();
    this.leds_old = this.model.get('leds');
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    $('input[type=checkbox]').bootstrapToggle();
    $('.modal').show();
  },

  toggle_led: function(e) {
    var leds = [];
    $(this.el).find('input[type=checkbox]').each(function(i) {
      if ($(this).prop('checked'))
      {
        leds.push(i + 1);
      }
    });
    this.model.set('leds', leds);
  },

  save: function() {
    this.remove();
  },

  close: function() {
    this.model.set('leds', this.leds_old);
    this.remove();
  }
});