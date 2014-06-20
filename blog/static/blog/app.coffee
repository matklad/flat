window.App = Em.Application.create()

App.Router.map ->
  @resource 'posts', path: '/'

App.ApplicationAdapter = DS.RESTAdapter.extend
  namespace: 'api'


App.Post = DS.Model.extend
  title: DS.attr 'string'
  text: DS.attr 'string'

  comments: DS.hasMany 'comments', async: true

  n_comments: Em.computed.alias('comments.length')


App.Comment = DS.Model.extend
  text: DS.attr 'string'
  n_likes: DS.attr 'number'

  post: DS.belongsTo 'post', async: true


App.PostsRoute = Em.Route.extend
  model: ->
    @store.find 'post'

