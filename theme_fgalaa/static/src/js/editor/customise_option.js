//--------------------------------------------------------------------------
//Customise Option file included
//--------------------------------------------------------------------------
odoo.define('theme_fgalaa.options', function (require) {
'use strict';

var core = require('web.core');
var QWeb = core.qweb;

QWeb.add_template('/theme_fgalaa/static/src/xml/customise_option.xml');

})
