# Copyright (C) 2006-2007 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import dbus
import logging

from sugar.presence import presenceservice

import OverlayWindow

class ActivityChatWindow(gtk.Window):
    def __init__(self, gdk_window, chat_widget):
        gtk.Window.__init__(self)

        self.realize()
        self.set_decorated(False)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.set_accept_focus(True)        
        self.window.set_transient_for(gdk_window)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_default_size(600, 450)

        self.add(chat_widget)

class ActivityHost:
    def __init__(self, model):
        self._model = model
        self._window = model.get_window()
        self._gdk_window = gtk.gdk.window_foreign_new(self.get_xid())

        try:
            self._overlay_window = OverlayWindow.OverlayWindow(self._gdk_window)
            win = self._overlay_window.window
        except RuntimeError:
            self._overlay_window = None
            win = self._gdk_window

        #self._chat_widget = ActivityChat.ActivityChat(self)
        self._chat_widget = gtk.HBox()
        self._chat_window = ActivityChatWindow(win, self._chat_widget)

        self._frame_was_visible = False

    def get_id(self):
        return self._model.get_activity_id()

    def get_xid(self):
        return self._window.get_xid()

    def get_model(self):
        return self._model

    def invite(self, buddy_model):
        service = self._model.get_service()
        if service:
            buddy = buddy_model.get_buddy()
            service.Invite(buddy.props.key)
        else:
            logging.error('Invite failed, activity service not ')

    def toggle_fullscreen(self):
        fullscreen = not self._window.is_fullscreen()
        self._window.set_fullscreen(fullscreen)

    def present(self):
        # wnck.Window.activate() expects a timestamp, but we don't
        # always have one, and libwnck will complain if we pass "0",
        # and matchbox doesn't look at the timestamp anyway. So we
        # just always pass "1".
        self._window.activate(1)

    def close(self):
        # The "1" is a fake timestamp as with present()
        self._window.close(1)

    def show_dialog(self, dialog):
        dialog.show()
        dialog.window.set_transient_for(self._gdk_window)

    def chat_show(self, frame_was_visible):
        if self._overlay_window:
            self._overlay_window.appear()
        self._chat_window.show_all()
        self._frame_was_visible = frame_was_visible

    def chat_hide(self):
        self._chat_window.hide()
        if self._overlay_window:
            self._overlay_window.disappear()
        wasvis = self._frame_was_visible
        self._frame_was_visible = False
        return wasvis

    def is_chat_visible(self):
        return self._chat_window.get_property('visible')

    def set_active(self, active):
        if not active:
            self.chat_hide()
            self._frame_was_visible = False

    def destroy(self):
        self._chat_window.destroy()
        self._frame_was_visible = False