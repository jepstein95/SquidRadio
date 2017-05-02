var ShairportView = require('./shairport.js');
var LightshowView = require('./lightshow.js');
var ChannelsView  = require('./channels.js');

var AppView = Backbone.View.extend({

  el: '.app',

  template: require('../../../views/partials/app.html'),

  events: {
    'click .navbar-nav a': 'change_tab'
  },

  shairport_view: null,
  lightshow_view: null,
  channels_view:  null, 

  initialize: function() {
    this.render();
    this.shairport_view = new ShairportView();
    this.lightshow_view = new LightshowView();
    this.channels_view  = new ChannelsView();
  },

  render: function() {
    $(this.el).html(this.template());
  },

  change_tab: function(e) {
    e.preventDefault();
    var rel = $(e.target).attr('rel');
    $('.tab-content').hide();
    $('.tab-content.' + rel).show();
    $('.navbar-nav li').removeClass('active');
    $(e.target).parent().addClass('active');
  }
});

module.exports = new AppView();