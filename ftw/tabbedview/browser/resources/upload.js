$(function(){

    if (jQuery('#uploadbox').length){

      /* ----------------------------------
         Added functionality to the upload box,
         copied from collective.quickupload*/


      // workaround this MSIE bug :
      // https://dev.plone.org/plone/ticket/10894
      if (jQuery.browser.msie) jQuery("#settings").remove();
      var Browser = {};
      Browser.onUploadComplete = function() {
        window.location.reload();
      };

    if ((jQuery.browser.msie && parseInt($.browser.version) < 10)) {
        return;
    } else {
      loadUploader = function() {
        var ulContainer = jQuery('#uploadbox');
        ulContainer.each(function(){
          var uploadUrl =  jQuery('.uploadUrl', this).attr('href');
          var uploadData =  jQuery('.uploadData', this).val();
          var UlDiv = jQuery(this);
          jQuery.ajax({
            type: 'GET',
            url: uploadUrl,
            data: uploadData,
            dataType: 'html',
            contentType: 'text/html; charset=utf-8',
            success: function(html) {
              UlDiv.html(html);
            }
          });
        });
      };
      loadUploader();

      var uploadbox = $('#uploadbox');
      uploadbox.css('display', 'none');

      var dragging_text = false;

      $('body').live('dragstart', function(event) {
          dragging_text = true;
      });

      $('body').live('dragend', function(event) {
          dragging_text = false;
      });

      $('.tabbedview_view').live('dragover', function(event){
          if (!dragging_text) {
              uploadbox.show();
              $('.qq-upload-button').hide();
              $('.pannelHeader').hide();
              $('#label-upload').hide();
            }
      });

      $('.tabbedview_view').live('dragleave', function(event){
        uploadbox.hover(
          function () {
            /* Do nothing*/
          },
          function () {
            var uploading = eval('xhr_' + uploadbox.find('.main-uploader').attr('id')).isUploading();
            var has_errors = uploadbox.find('.main-uploader .qq-upload-fail').length > 0;

            if (! uploading && ! has_errors){
              uploadbox.hide();
            }
          }
        );
      });

          PloneQuickUpload.onAllUploadsComplete = function(event){
              uploadbox.hide();
              $('#label-upload').hide();
              tabbedview.reload_view();
          };
       }
    }
});
