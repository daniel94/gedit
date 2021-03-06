# -*- coding: UTF-8 -*-
#    Gedit External Tools plugin
#    Copyright (C) 2005-2006  Steve Frécinaux <steve@istique.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gi.repository import GLib, Gio, GObject, Gtk, Gedit
from .library import ToolLibrary
import os

class ToolMenu(object):
    def __init__(self, library, menu):
        super(ToolMenu, self).__init__()
        self._library = library
        self._menu = menu
        self._action_tools = {}

        self.update()

    def deactivate(self):
        self.remove()

    def remove(self):
        self._menu.remove_all()

        for name, tool in self._action_tools.items():
            if tool.shortcut:
                app = Gio.Application.get_default()
                app.remove_accelerator(tool.shortcut)

    def _insert_directory(self, directory, menu):
        for d in sorted(directory.subdirs, key=lambda x: x.name.lower()):
            submenu = Gio.Menu()
            menu.append_submenu(d.name.replace('_', '__'), submenu)
            section = Gio.Menu()
            submenu.append_section(None, section)

            self._insert_directory(d, section)

        for tool in sorted(directory.tools, key=lambda x: x.name.lower()):
            # FIXME: find a better way to share the action name
            action_name = 'external-tool_%X_%X' % (id(tool), id(tool.name))
            item = Gio.MenuItem.new(tool.name.replace('_', '__'), "win.%s" % action_name)
            item.set_attribute_value("hidden-when", GLib.Variant.new_string("action-disabled"))
            menu.append_item(item)

            if tool.shortcut:
                app = Gio.Application.get_default()
                app.add_accelerator(tool.shortcut, "win.%s" % action_name, None)

    def update(self):
        self.remove()
        self._insert_directory(self._library.tree, self._menu)


class AppActivatable(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = "ExternalToolsAppActivatable"

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)
        self.menu = None

    def do_activate(self):
        self._library = ToolLibrary()
        self._library.set_locations(os.path.join(self.plugin_info.get_data_dir(), 'tools'))

        self.menu_ext = self.extend_menu("appmenuext2")
        item = Gio.MenuItem.new(_("Manage _External Tools..."), "win.manage-tools")
        self.menu_ext.append_menu_item(item)

        self.submenu_ext = self.extend_menu("ext9")
        external_tools_submenu = Gio.Menu()
        item = Gio.MenuItem.new_submenu(_("External _Tools"), external_tools_submenu)
        self.submenu_ext.append_menu_item(item)
        external_tools_submenu_section = Gio.Menu()
        external_tools_submenu.append_section(None, external_tools_submenu_section)

        self.menu = ToolMenu(self._library, external_tools_submenu_section)

    def do_deactivate(self):
        self.menu.deactivate()
        self.menu_ext = None
        self.submenu_ext = None

# ex:ts=4:et:
