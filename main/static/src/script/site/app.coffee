$ ->
  init_common()

$ -> $('html.auth').each ->
  init_auth()

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()

$ -> $('html.resource-list').each ->
  init_resource_list()

$ -> $('html.resource-view').each ->
  init_resource_view()

$ -> $('html.resource-upload').each ->
  init_resource_upload()

$ -> $('html.album-view').each ->
  init_album_resource_view()

$ -> $('html.album-update').each ->
  init_album_resource_view()
  init_resource_upload()
  init_delete_album_resource_button()

$ -> $('html.welcome').each ->
  init_carousel_resource_upload()
  init_delete_carousel_resource_button()
  init_carousel_fullscreen()
