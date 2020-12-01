odoo.define('theme_fgalaa.slider_range', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.slider_range = publicWidget.Widget.extend({
        selector: ".oe_website_sale",
        events: {
            'change input.ept_price_min, input.sliderValue, input.ept_price_max':'changeInputValSlider',
            'click .price_filter_reset':'resetFilterSlider',
            'click #price_slider_filter':'applyFilterSlider',
        },
        start: function () {
            this.initSliderRange();
        },
        initSliderRange: function() {
            /* This method is called for initialize the price slider in at shop page. */
            var searchParams = new URLSearchParams(window.location.search);
            var minValue = parseFloat($("#price_slider_min").val());
            var maxValue = parseFloat($("#price_slider_max").val());
            var urlMinVal = parseFloat(searchParams.get('min_price'));
            var urlMaxVal = parseFloat(searchParams.get('max_price'));
            var inputMinVal = parseFloat($("input.ept_price_min").val());
            var inputMaxVal = parseFloat($("input.ept_price_max").val());
            var showMinVal;
            var showMaxVal;
            if(urlMinVal && urlMaxVal)
            {
            console.log('-------------------------')
                showMinVal = urlMinVal;
                showMaxVal = urlMaxVal;
                $("input.ept_price_min").val(urlMinVal);
                $("input.ept_price_max").val(urlMaxVal);
            }else {
            console.log('-------------------------else')
                showMinVal = minValue;
                showMaxVal = maxValue;
            }
            $("#slider-range").slider({
                range: true,
                step: 1,
                min: minValue,
                max:maxValue,
                values: [showMinVal, showMaxVal],
                slide: function(event, ui) {
                    for (var i = 0; i < ui.values.length; ++i) {
                        $("input.sliderValue[data-index=" + i + "]").val(ui.values[i]);
                    }
                }
            });
            if(inputMinVal != minValue || inputMaxVal != maxValue) {
                $(".price_filter_reset").show();
                $(".te_pricerange_content").show();
                $(".price_filter_head").toggleClass("te_fa-minus te_fa-plus")
            }else {
                $(".price_filter_reset").hide();
            }
        },
        changeInputValSlider: function (event) {
            /* This method is called for set the slider data while change the slider inputs */
            var target = event.currentTarget;
            $("#slider-range").slider("values", $(target).data("index"), $(target).val());
        },
        resetFilterSlider: function (event) {
            /* This method is called for reset the price slider */
            var minValue = parseFloat($("#price_slider_min").val());
            var maxValue = parseFloat($("#price_slider_max").val());
            $("input.ept_price_min").val(minValue);
            $("input.ept_price_max").val(maxValue);
            $( "#slider-range" ).slider("values",[minValue,maxValue]);
            this.applyFilterSlider();
        },
        applyFilterSlider: function (event) {
            /* This method is called for filter the price data on click the apply filter button */
            var minValue = parseFloat($("#price_slider_min").val());
            var maxValue = parseFloat($("#price_slider_max").val());
            var inputMinVal = parseFloat($("input.ept_price_min").val());
            var inputMaxVal = parseFloat($("input.ept_price_max").val());
            if (inputMinVal == "" || inputMaxVal == "" ||
                isNaN(inputMinVal) || isNaN(inputMaxVal) ||
             inputMinVal < minValue || inputMaxVal > maxValue ||
              inputMinVal > maxValue || inputMaxVal > maxValue ||
               inputMaxVal < minValue || inputMaxVal < inputMinVal) {
                $('.slider-range_error').addClass("price_error_message").html('Invalid Input');
                return false
            }
            var loadThroughAjax = new publicWidget.registry.load_ajax();
            if($(".load_products_through_ajax").length)
            {
                var through_ajax = $(".load_products_through_ajax").val();
                if(through_ajax == 'True')
                {
                    loadThroughAjax.sendAjaxToFilter(event);
                }
            }else {
                $("form.js_attributes input,form.js_attributes select").closest("form").submit();
            }
        },

    });
});