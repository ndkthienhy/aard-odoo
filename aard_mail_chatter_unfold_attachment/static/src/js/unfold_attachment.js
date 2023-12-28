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
        //this._isAttachmentBoxOpen = true;
        this._onClickAttachmentButton();
    },

    //--------------------------------------------------------------------------
    // Overrite
    //--------------------------------------------------------------------------

    /**
     * @param {Object} record
     * @param {integer} [record.res_id=undefined]
     * @param {Object[]} [fieldNames=undefined]
     */
    update: function (record, fieldNames) {
        var self = this;

        // close the composer if we switch to another record as it is record dependent
        if (this.record.res_id !== record.res_id) {
            this._closeComposer(true);
        }

        // update the state
        this._setState(record);

        // detach the thread and activity widgets (temporarily force the height to prevent flickering)
        // keep the followers in the DOM as it has a synchronous pre-rendering
        this.$el.height(this.$el.height());
        if (this.fields.activity) {
            this.fields.activity.$el.detach();
        }
        if (this.fields.thread) {
            this.fields.thread.$el.detach();
        }

        // reset and re-append the widgets (and reset 'height: auto' rule)
        // if fieldNames is given, only reset those fields, otherwise reset all fields
        var fieldsToReset;
        if (fieldNames) {
            fieldsToReset = _.filter(this.fields, function (field) {
                return _.contains(fieldNames, field.name);
            });
        } else {
            fieldsToReset = this.fields;
        }
        var fieldDefs = _.invoke(fieldsToReset, 'reset', record);
        var def = this._dp.add($.when.apply($, fieldDefs));
        this._render(def).then(function () {
            self.$el.height('auto');
            self._updateMentionSuggestions();
        });
        this._updateAttachmentCounter();

        this._isAttachmentBoxOpen = false;
        this._areAttachmentsLoaded = false;
        this.attachments = {};
        this._onClickAttachmentButton();
    },
});

return UnfoldAttach;

});
