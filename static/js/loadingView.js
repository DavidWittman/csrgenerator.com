
/**
 * @author: Ademola Aina (debascoguy@gmail.com)
 * =============================================
 * UNLICENSED VERSION
 *
 * @params options = {} of the following parameters.
 * @param selector
 * @param state		[Either true|false : denotes whether to show loadingView OR disable loadingView]
 * @param loadingImage	[optional image you would like to use in the loading view]
 * @param imageStyle	[css inline-css style you would to add to the loading image...e.g: to reduce the size...Use fn: addImageStyle() | setImageStyle() to add/set/change inline-css of loadingView image]
 * @returns
 */

var LoadingView = (typeof LoadingView === 'undefined') ? {} : LoadingView;

LoadingView = function(options) {
	var defaultOption = {};

	defaultOption.selector = "body";
	defaultOption.state = true;
	defaultOption.image = "loadingImage.gif";			//You can change this anytime anyday based on your image location.
	defaultOption.imageClassName = "loadingImage";
	defaultOption.imageStyle = "position:absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);";

	 if (typeof options === 'undefined') {
	        options = defaultOption;
	 }

	 var getOption = function(field){
	        return (typeof options[field] === 'undefined' || undefined === options[field] || null===options[field] || "" === options[field] ) ? defaultOption[field] : options[field];
	 };

	 this.selector = getOption('selector');
	 this.state = getOption('state');
	 this.image = getOption('image');
	 this.imageClassName = getOption('imageClassName');
	 this.imageStyle = getOption('imageStyle');


	 //Set Option Functions
	 this.setState = function(state){
		 this.state = state;
	 }

	 this.setLoadingImage = function(image){
		 this.image = image;
	 }

	 this.setState = function(state){
		 this.state = state;
	 }

	 this.setImageClassName = function(imageClassName){
		 this.imageClassName = imageClassName;
	 }

	 this.addImageClassName = function(imageClassName){
		 this.imageClassName += ' '+imageClassName;
	 }

	 this.setImageStyle = function(imageStyle) {
		 this.imageStyle = imageStyle;
	 }

	 this.addImageStyle = function(imageStyle) {
		 this.imageStyle += ' '+imageStyle;
	 }


	 this.loading = function() {
			if (this.state){
				$(this.selector).css({"opacity": "0.5",
									"filter": "alpha(opacity=50)", /* For IE8 and earlier */
									"position": "relative"});

				$(this.selector).append("<img class='"+this.imageClassName+"' style='"+this.imageStyle+"' src='"+this.image+"' alt='loading...' />");
			}
			else{
				$(this.selector).css({"opacity": "", "filter": "", "position": ""});
				$(this.selector).find("."+this.imageClassName).remove();
			}
	 }

}

/**
 * Using Direct JS - Function Call
 * @param selector
 * @param state
 * @param loadingImage
 * @param imageClassName
 * @param imageInlineStyle
 * @returns
 */
function setLoadingView(selector, state, loadingImage, imageClassName, imageInlineStyle)
{
	var call	=	new LoadingView({'selector':selector,
								'state':state,
								'image':loadingImage,
								'imageClassName':imageClassName,
								'imageStyle':imageInlineStyle
					});
	call.loading();
}



/**
 * Minimal Direct JS - Function Call
 * @param selector
 * @param state
 * @param loadingImage
 * @returns
 */
function setElementLoading(selector, state, loadingImage)
{
	setLoadingView(selector, state, loadingImage);
}


//Using jQuery
/**
    $('.body').loadingView();			//start loadingView
    $('.selector').loadingView({'state':true});		//Or start loadingView
    $('.selector').loadingView({'state':false}); 	//Stop LoadingView
*/
(function($) {

    $.fn.loadingView = function (newOptions) {
        return $.loadingView(this, newOptions);
    };

    $.loadingView = function (selector, newOptions) {
        newOptions['selector'] = selector;
        var call = new LoadingView(newOptions);
        call.loading();
        return call;
    };

})(jQuery);


