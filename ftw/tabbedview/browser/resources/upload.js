jq(function(){

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

  loadUploader = function() {
    var ulContainer = jQuery('#uploadbox');
    ulContainer.each(function(){
      var uploadUrl =  jQuery('.uploadUrl', this).val();
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

  var uploadbox = jq('#uploadbox');
  uploadbox.css('display', 'none');

  jq('.tabbedview_view').live('dragover', function(event){
    uploadbox.show();
    jq('.qq-upload-button').hide();
    jq('.pannelHeader').hide();
    jq('#label-upload').hide();
  });

  jq('.tabbedview_view').live('dragleave', function(event){
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
    jq('#label-upload').hide();
    tabbedview.reload_view();
  };
});
