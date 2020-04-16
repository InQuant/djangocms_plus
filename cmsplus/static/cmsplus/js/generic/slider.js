let cxngSlider = angular.module('cxng.Slider', []);

/*
 * cxng component slider
 *
 * uses pure js lib: glide.js
 */
function cxngSliderCtrl($scope, $element, $attrs, $window) {
    var ctrl = this;

    ctrl.initGlide = function() {
        var gid = '#' + ctrl.glideId;
        console.log('init slider with glide-id: ' + gid);
        var glide = new Glide(gid, {
            perView: parseInt(ctrl.config.n_slides_xl),
            focusAt: 'center',
            type: ctrl.config.type,
            breakpoints: ctrl.config.breakpoints,
            gap: ctrl.config.gap,
            autoplay: ctrl.config.autoplay,
            hoverpause: ctrl.config.hoverpause,
            peek: ctrl.config.peek,

            animationDuration: ctrl.config.animation_duration || 400,
            animationTimingFunc: ctrl.config.animation_timing_func || 'cubic-bezier(0.165, 0.840, 0.440, 1.000)',
        });
        glide.mount();
    }

    ctrl.$onInit = function() {
        console.log(ctrl.config);
    };
}
cxngSlider.component('cxngSlider', {
    bindings: {
        glideId: '@',
        config: '=?',
    },
    transclude: {
        cxngSlides: '?cxngSlides'
    },
    templateUrl: cxngTemplateUrl('generic/slider/slider.html'),
    controller: cxngSliderCtrl,
});

cxngSlider.directive("cxngInitSlider", function() {
    function link(scope, element, attrs) {
        /* sliderCtrl must be initialized from cxng-slider component */
        scope.sliderCtrl.initGlide();
    }

    return {
      link: link,
    }
});