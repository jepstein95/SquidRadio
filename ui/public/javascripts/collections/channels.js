var ChannelModel = require('../models/channel.js');

module.exports = Backbone.Collection.extend({

  url: '/channels',

  model: ChannelModel,

  initialize: function() {
    this.fetch({reset: true});
  }
});