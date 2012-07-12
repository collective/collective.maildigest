var maildigest = {};

maildigest.initoverlay = function(){
	jQuery('#digest-form-link').prepOverlay({
	    subtype: 'ajax',
	    filter: common_content_filter,
	    closeselector: '[name=form.button.Cancel]',
	    formselector: '#digest-form form',
        noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
    	redirect: function () {return location.href;}
	});
}

jQuery(document).ready(maildigest.initoverlay);
