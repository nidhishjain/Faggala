odoo.define('aspl_website_customer_wallet.main', function(require) {
    "use strict";
    var core = require('web.core')
    var qweb = core.qweb;
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var session = require('web.session');
    $("#set_pin").attr("disabled", true);
    var $btn = $('#set_pin');
//    $btn.prop('disabled', true);

    $(document).ready(function(e) {

        if ($('#transaction').val()) {
            let data = $('#transaction').val();
            ajax.jsonRpc("/wallet/data/selection", 'call', {
                    'data': data
                })
                .then(function(result) {
                    if (result) {
                        var render_fir = true
                        transaction_data_fun(result, render_fir)

                    }
                });
        }

        $('.my_passbook').click(function() {
            let data = $('#transaction').val();
            ajax.jsonRpc("/wallet/passbook", 'call', {
                    'data': 'mypassbook',
                    'transaction': data
                })
                .then(function(result) {
                    $('#wallet_body').html('')
                    $('#wallet_body').html(result['data'])
                    transaction_data_fun(result['trans'], false)
                })
        })

        $('.add_my_wallet').click(function() {
            ajax.jsonRpc("/add/money", 'call', {
                    'data': 'wallet'
                })
                .then(function(result) {
                    $('#wallet_body').html('')
                    $('#wallet_body').html(result['data'])
                })
        })

        $('.change_password').click(function() {
            ajax.jsonRpc("/change/pin", 'call', {
                    'data': 'password'
                })
                .then(function(result) {
                    $('#wallet_body').html('')
                    $('#wallet_body').html(result['data'])
                })
        });

        $('#newpin').on("change", function(){
            var old_pin = $("#oldpin").val();
            var new_pin = $("#newpin").val();
            console.log("----log----", old_pin, new_pin)
            if (old_pin != '' && new_pin != '') {
                $btn.removeAttr('disabled');
            } else {
                $btn.prop('disabled', true);
            }
        });

        $("#oldpin").on("change", function(){
            var old_pin = $("#oldpin").val();
            var new_pin = $("#newpin").val();
            if (old_pin != '' && new_pin != '') {
                $btn.removeAttr('disabled');
            } else {
                $btn.prop('disabled', true);
            }
        });
        $("#add_money").keypress(function(e) {
            console.log("-------log----", e)
            //if the letter is not digit then display error and don't type anything
            if (e.which != 8 && e.which != 0 && e.which != 46 && (e.which < 48 || e.which > 57)) {
                return false;
            }
        });

        $('.setpin').click(function() {
            var old_pin = $("#oldpin").val();
            var new_pin = $("#newpin").val();
            var user = session.user_id;
            rpc.query({
                    model: 'res.users',
                    method: 'read',
                    args: [
                        [user],
                        ['customer_password']
                    ],
                })
                .then(function(result) {
                    var old_pwd = result[0]['customer_password']
                    if (old_pin == old_pwd) {
                        ajax.jsonRpc("/change/pin/process", 'call', {
                                'oldpin': old_pin,
                                'newpin': new_pin
                            })
                            .then(function(result) {
                                $('#wallet_body').html('')
                                $('body').html(result['data'])
                            })
                    } else {
                        ajax.jsonRpc("/change/pin/process", 'call', {
                                'oldpin': old_pin,
                                'newpin': new_pin
                            })
                            .then(function(result) {
                                $('#wallet_body').html('')
                                $('#wallet_body').html(result['data'])
                            })
                    }
                })
        })

        function transaction_data_fun(result, d1) {
            if (d1) {
                var transactions = JSON.parse(result);
            } else {
                var transactions = result;
            }
            $('#foo-table').html("");
            $('.filter-form-here').html("");
            let head = `<thead>
                                    <tr>
                                        <th class="text-center" style="width: 30%;">
                                            Date
                                        </th>
                                        <th class="text-center" style="width: 30%;">
                                            Type
                                        </th>
                                        <th class="text-right" style="width: 20%;">
                                            Amount
                                        </th>
                                    </tr>
                                </thead>`;

            let body = "<tbody>";
            transactions.forEach((trans) => {
                body += `<tr>
                                    <td class="text-center" style="width: 30%;">
                                        ${trans.date}
                                    </td>
                                    <td class="text-center" style="width: 30%;">
                                        ${trans.transaction_type}
                                    </td>
                                    <td class="text-right" style="width: 20%;">
                                        <span style="margin-right: 3px; margin-left: 5px;" class="text-right">
                                            ${trans.currency}${trans.amount.toFixed(2)}
                                        </span>
                                    </td>
                                </tr>`;
            });
            body += "</tbody>";
            $('#foo-table').html(head + body);
            $('#foo-table').footable();
        }

        $("#transaction").change(function() {
            let data = $('#transaction').val();
            ajax.jsonRpc("/wallet/data/selection", 'call', {
                    'data': data
                })
                .then(function(result) {
                    if (result) {
                        var render_fir = true
                        transaction_data_fun(result, render_fir)
                    }
                });
        });
    })
});