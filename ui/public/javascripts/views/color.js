module.exports = Backbone.View.extend({

  el: '.modal',

  template: require('../../../views/partials/color.html'),

  color_old: '',

  events: {
    'click button.btn-save': 'save',
    'click button.close': 'close',
    'change.spectrum   .color-picker': 'change_color',
    'dragstop.spectrum .color-picker': 'change_color',
    'click .display .old': 'revert_color'
  },

  initialize: function() {
    this.render();
    this.color_old = this.model.get('color');
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    var color = 'rgb(' + this.model.get('color') + ')';
    $('.color-picker').spectrum({
      color: color,
      flat: true,
      showInput: true,
      preferredFormat: 'rgb',
      showButtons: false
    });
    $('.modal').show();
  },

  change_color: function(e) {
    var color  = $(e.target).spectrum('get');
    var r = Math.round(color._r);
    var g = Math.round(color._g);
    var b = Math.round(color._b);
    var rgb = r + ', ' + g + ', ' + b;
    this.model.set('color', rgb);
    $(this.el).find('.display .new').css({'background-color': 'rgb(' + rgb + ')'});
  },

  revert_color: function() {
    var color = this.color_old.toString();
    this.model.set('color', this.color_old);
    $(this.el).find('.display .new').css({'background-color': 'rgb(' + this.color_old + ')'});
    $('.color-picker').spectrum('set', 'rgb(' + color + ')');
  },

  save: function() {
    this.remove();
  },

  close: function() {
    this.model.set('color', this.color_old);
    this.remove();
  }
});