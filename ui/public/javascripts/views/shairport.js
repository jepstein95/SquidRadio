var ShairportModel = require('../models/shairport.js');

module.exports = Backbone.View.extend({
  
  el: '.shairport',

  template: require('../../../views/partials/shairport.html'),

  model: new ShairportModel(),

  events: {
    'change .toggle-shairport': 'toggle'
  },

  initialize: function() {
    this.render();
    this.model.on('change', this.render.bind(this));
  },

  render: function() {
    $(this.el).html(this.template(this.model.toJSON()));
    $('.toggle-shairport').bootstrapToggle();
  },

  toggle: function() {
    this.model.toggle();
  }
});