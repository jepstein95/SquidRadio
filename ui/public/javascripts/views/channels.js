var ChannelsCollection = require('../collections/channels.js');
var ChannelView        = require('../views/channel.js');

module.exports = Backbone.View.extend({
  
  el: '.channels',

  collection: new ChannelsCollection(),

  channel_views: {},

  initialize: function() {
    this.render();
    this.collection.on('change', this.change, this);
    this.collection.on('sync', this.render, this);
  },

  render: function() {
    this.collection.models.forEach(function(model) {
      $(this.el).append('<div id="channel-' + model.get('key') + '"></div>');
      var channel_view = new ChannelView({model: model, el: '#channel-' + model.get('key')});
      this.channel_views[model.get('key')] = channel_view;
    }.bind(this));
  },

  change: function(model, val) {
    console.log(model.toJSON());
  }
});