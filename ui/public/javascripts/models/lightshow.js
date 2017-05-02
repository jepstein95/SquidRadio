module.exports = Backbone.Model.extend({
  
  urlRoot: '/lightshow',

  defaults: {
    is_on: false
  },

  initialize: function() {
    this.fetch();
  },

  toggle: function() {
    this.attributes.is_on = !this.attributes.is_on;
    this.save();
  }
});