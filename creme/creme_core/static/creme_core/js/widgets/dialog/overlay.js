/*******************************************************************************
    Creme is a free/open-source Customer Relationship Management software
    Copyright (C) 2009-2013  Hybird

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*******************************************************************************/

creme.dialog = creme.dialog || {};

creme.dialog.Overlay = creme.component.Component.sub({
    _init_: function(options)
    {
        var options = options || {};
        var self = this;

        this._content = $('<div/>').addClass('overlay-content');
        this._overlay = $('<div/>').addClass('ui-creme-overlay')
                                   .append(this._content);

        this._timeout = new creme.component.TimeoutAction();
        this._timeout.onDone(function(event, options) {
            self.update(options.visible, options.status);
        });
    },

    update: function(visible, status, delay)
    {
        var self = this;

        this._timeout.cancel();

        if (delay > 0) {
            this._timeout.start({delay:delay, visible:visible, status:status});
            return;
        }

        this.visible(visible || false);

        if (status === undefined) {
            this._overlay.removeAttr('status');
        } else {
            this._overlay.attr('status', status);
        }
    },

    addClass: function() {
        this._overlay.addClass.apply(this._overlay, arguments);
        return this;
    },

    removeClass: function() {
        this._overlay.removeClass.apply(this._overlay, arguments);
        return this;
    },

    toggleClass: function() {
        this._overlay.toggleClass.apply(this._overlay, arguments);
        return this;
    },

    content: function(content)
    {
        if (content === undefined)
            return this._content;

        this._content.html(content);
        return this;
    },

    visible: function(visible)
    {
        if (visible === undefined)
            return this._overlay.hasClass('overlay-active');

        var visible = visible || false;

        if (!this.isBound() || this.visible() === visible)
            return this;

        this._overlay.toggleClass('overlay-active', visible);

        if (visible)
        {
            /* IE Hack : remove overflow of container in order to prevent issues with unexpected 
             * vertical scrollbars.
             */ 
            this._targetOverflowX = this._target.css('overflow-x');
            this._targetOverflowY = this._target.css('overflow-y');
            this._targetPosition = this._target.css('position');

            this.resize();

            this._target.css({
                             'overflow-x': 'hidden',
                             'overflow-y': 'hidden',
                             'position':   'relative'
                         });

            this._target.append(this._overlay);
        } else {
            this._overlay.remove();
            this._target.css({
                             'overflow-x': this._targetOverflowX,
                             'overflow-y': this._targetOverflowY,
                             'position':   this._targetPosition
                         });
        }

        return this;
    },

    resize: function()
    {
        if (!this.isBound() || !this.visible())
            return this;
        
        var padding = $.browser.mozilla ? 1 : 0;

        this._overlay.css('width', this._target.outerWidth() + padding)  // fix an outerWidth issue in firefox.
                     .css('height', this._target.height());

        return this;
    },

    bind: function(element)
    {
        var self = this;

        if (this.isBound()) {
            throw new Error('Overlay is already bound.');
        }

        this._target = element;
        this._target.bind('resize', function() {self.resize()});

        return this;
    },

    unbind: function(element)
    {
        if (!this.isBound()) {
            throw new Error('Overlay is not bound.');
        }

        this.visible(false);
        this._overlay.detach();
        this._target = undefined;

        return this;
    },

    isBound: function() {
        return Object.isNone(this._target) === false;
    },

    state: function() {
        return this._overlay.attr('status');
    }
});