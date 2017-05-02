var LightshowModel = require('../models/lightshow.js');

module.exports = Backbone.View.extend({
  
  el: '.lightshow',

  template: require('../../../views/partials/lightshow.html'),

  model: new LightshowModel(),

  events: {
    'change .toggle-lightshow': 'toggle'
  },

  initialize: function() {
    this.render();
    this.model.on('change', this.render.bind(this));
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    $('.toggle-lightshow').bootstrapToggle();
  },

  toggle: function() {
    this.model.toggle();
  }
});