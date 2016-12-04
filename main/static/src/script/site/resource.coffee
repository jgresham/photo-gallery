window.init_resource_list = () ->
  init_delete_resource_button()

window.init_resource_view = () ->
  init_delete_resource_button()

window.init_resource_upload = () ->
  if window.File and window.FileList and window.FileReader
    window.file_uploader = new FileUploader
      upload_handler: upload_handler
      selector: $('.file')
      drop_area: $('.drop-area')
      confirm_message: 'Files are still being uploaded.'
      upload_url: $('.file').data('get-upload-url')
      allowed_types: []
      max_size: 1024 * 1024 * 1024

upload_handler =
  preview: (file) ->
    $resource = $ """
        <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
          <div class="thumbnail">
            <div class="preview"></div>
            <h5>#{file.name}</h5>
            <div class="progress">
              <div class="progress-bar" style="width: 0%;"></div>
              <div class="progress-text"></div>
            </div>
          </div>
        </div>
      """
    $preview = $('.preview', $resource)

    if file_uploader.active_files < 16 and file.type.indexOf("image") is 0
      reader = new FileReader()
      reader.onload = (e) =>
        $preview.css('background-image', "url(#{e.target.result})")
      reader.readAsDataURL(file)
    else
      $preview.text(file.type or 'application/octet-stream')

    $('.resource-uploads').prepend($resource)

    (progress, resource, error) =>
      if error
        $('.progress-bar', $resource).css('width', '100%')
        $('.progress-bar', $resource).addClass('progress-bar-danger')
        if error == 'too_big'
          $('.progress-text', $resource).text("Failed! Too big, max: #{size_human(file_uploader.max_size)}.")
        else if error == 'wrong_type'
          $('.progress-text', $resource).text("Failed! Wrong file type.")
        else
          $('.progress-text', $resource).text('Failed!')
        return

      if progress == 100.0 and resource
        $('.progress-bar', $resource).addClass('progress-bar-success')
        $('.progress-text', $resource).text("Success #{size_human(file.size)}")
        if resource.image_url and $preview.text().length > 0
          $preview.css('background-image', "url(#{resource.image_url})")
          $preview.text('')
      else if progress == 100.0
        $('.progress-bar', $resource).css('width', '100%')
        $('.progress-text', $resource).text("100% - Processing..")
      else
        $('.progress-bar', $resource).css('width', "#{progress}%")
        $('.progress-text', $resource).text("#{progress}% of #{size_human(file.size)}")

window.init_carousel_resource_upload = () ->
  # $('.btn-delete').click (event) ->
  #   target = $(event.target)
  #   colToDelete = target.closest(".col-carousel_resource")
  #   if colToDelete
  #     colToDelete.remove()
  #   event.preventDefault()

  if window.File and window.FileList and window.FileReader
    window.file_uploader = new FileUploader
      upload_handler: carousel_resource_upload_handler
      selector: $('.file')
      drop_area: $('.drop-area')
      confirm_message: 'Files are still being uploaded.'
      upload_url: $('.file').data('get-upload-url')
      allowed_types: []
      max_size: 1024 * 1024 * 1024

carousel_resource_upload_handler =
  preview: (file) ->
    $resource = $ """
        <div class="col-xs-12 col-md-4 col-lg-3">
          <div class="image-preview carousel-edit-image">
            <div class="img-responsive img-thumbnail preview"></div>
          </div>
        </div>
      """
    $preview = $('.preview', $resource)

    if file_uploader.active_files < 16 and file.type.indexOf("image") is 0
      reader = new FileReader()
      reader.onload = (e) =>
        $preview.css('background-image', "url(#{e.target.result})")
      reader.readAsDataURL(file)
    else
      $preview.text(file.type or 'application/octet-stream')

    $('.resource-uploads > div:nth-child(1)').after($resource)

    (progress, resource, error) =>
      if error
        $('.progress-bar', $resource).css('width', '100%')
        $('.progress-bar', $resource).addClass('progress-bar-danger')
        if error == 'too_big'
          $('.progress-text', $resource).text("Failed! Too big, max: #{size_human(file_uploader.max_size)}.")
        else if error == 'wrong_type'
          $('.progress-text', $resource).text("Failed! Wrong file type.")
        else
          $('.progress-text', $resource).text('Failed!')
        return

      if progress == 100.0 and resource
        if resource.image_url and $preview.text().length > 0
          $preview.css('background-image', "url(#{resource.image_url})")
          $preview.text('')
      else if progress == 100.0
        $('.progress-bar', $resource).css('width', '100%')
        $('.progress-text', $resource).text("100% - Processing..")
      else
        $('.progress-bar', $resource).css('width', "#{progress}%")
        $('.progress-text', $resource).text("#{progress}% of #{size_human(file.size)}")

window.init_delete_carousel_resource_button = () ->
  $('body').on 'click', '.btn-delete', (e) ->
    e.preventDefault()
    api_call 'DELETE', $(this).data('api-url'), (err, result) =>
      if err
        $(this).removeAttr('disabled')
        LOG 'Something went terribly wrong during delete!', err
        return
      target = $(this).data('target')
      colToDelete = $(this).closest(".col-carousel_resource")
      if colToDelete
        colToDelete.remove()

window.init_delete_resource_button = () ->
  $('body').on 'click', '.btn-delete', (e) ->
    e.preventDefault()
    if confirm('Press OK to delete the resource')
      $(this).attr('disabled', 'disabled')
      api_call 'DELETE', $(this).data('api-url'), (err, result) =>
        if err
          $(this).removeAttr('disabled')
          LOG 'Something went terribly wrong during delete!', err
          return
        target = $(this).data('target')
        redirect_url = $(this).data('redirect-url')
        if target
          $("#{target}").remove()
        if redirect_url
          window.location.href = redirect_url

window.init_carousel_fullscreen = () ->
  $item = $('.carousel .item')
  $wHeight = $(window).height()
  $item.eq(0).addClass('active')
  $item.height($wHeight)
  $item.addClass('full-screen')

  $(window).on 'resize', () ->
    $wHeight = $(window).height()
    $item.height($wHeight)

  $('.album-image-a').hover (->
    $(this).find('.caption').fadeIn 250
    #.slideDown(250)
    return
  ), ->
    $(this).find('.caption').fadeOut 250
    #.slideUp(205)
    return

window.addEventListener 'scroll', (->
  if window.scrollY > 10
    $('.navbar').fadeOut()
  else
    $('.navbar').fadeIn()
  return
), false
