module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    watch: {
      js: {
        files: ['public/javascripts/models/*.js', 'public/javascripts/views/*.js', 'public/javascripts/collections/*.js', 'views/**/*.html'],
        tasks: ['browserify']
      }
    },
    browserify: {
      options: {
        transform: ['node-underscorify'],
        debug: true,
        external: ['jquery', 'underscore', 'backbone']
      },
      files: {
        src: ['public/javascripts/views/app.js'],
        dest: 'public/javascripts/app.js'
      },
    }
  });

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-browserify');
  grunt.registerTask('default', ['watch', 'browserify']);
}
