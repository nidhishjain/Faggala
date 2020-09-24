odoo.define('partial_payment.payment', function (require) {
'use strict';
var ajax = require('web.ajax');

    $(document).ready(function (e) {
        $('#used_wallet').prop('checked', true);
        if($("#wallet_amount").val() > 0){
            ajax.jsonRpc("/sale/partial_pay/price", 'call', {
                    'amount': ($("#wallet_amount").val())
                })
        }
        $('#used_wallet_invoice').prop('checked', true);
        if ($("#wallet_invoice_amount").val() > 0){
            ajax.jsonRpc("/invoice/partial_pay/price", 'call', {
                    'amount': ($("#wallet_invoice_amount").val()),
                    'invoice': ($("#invoice_id").val())
                })
        }
        $("#used_wallet").change(function(){
            if($(this).is(':checked')){
                ajax.jsonRpc("/sale/partial_pay/price", 'call', {
                    'amount': ($("#wallet_amount").val())
                })
            }
            else{
                ajax.jsonRpc("/sale/partial_pay/price", 'call', {
                    'amount': 0.0,
                })
            }
        });
        $("#used_wallet_invoice").change(function(){
            if($(this).is(':checked')){
                ajax.jsonRpc("/invoice/partial_pay/price", 'call', {
                    'amount': ($("#wallet_invoice_amount").val()),
                    'invoice': ($("#invoice_id").val())
                })
            }
            else{
                ajax.jsonRpc("/invoice/partial_pay/price", 'call', {
                    'amount': 0.0,
                    'invoice': ($("#invoice_id").val())
                })
            }
        });
    });
});
