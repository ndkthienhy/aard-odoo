odoo.define('mail.chatter.UnfoldAttach', function (require) {
"use strict";

var Chatter = require('mail.Chatter');
var Widget = require('web.Widget');

// The purpose of this widget is to display the chatter area below the form view
//
// Defaul unfold attachment

var UnfoldAttach = Chatter.include({
    init: function () {
        this._super.apply(this, arguments);
        
        /*Default unfold attachment */
        this._onClickAttachmentButton();  
    },
});

return UnfoldAttach;

});
