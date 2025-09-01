# gui.py - EchoBoot GTK Interface (Scaffold v0.1)
# Requirements: pip install pygobject

import gi
import subprocess
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class EchoBootGUI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="EchoBoot - Liminal Flame Edition")
        self.set_border_width(10)
        self.set_default_size(480, 300)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Drive selection label + combo box
        self.drive_label = Gtk.Label(label="Select USB Drive:")
        vbox.pack_start(self.drive_label, False, False, 0)

        self.drive_combo = Gtk.ComboBoxText()
        self.populate_drives()
        vbox.pack_start(self.drive_combo, False, False, 0)

        # Action buttons
        self.format_button = Gtk.Button(label="Ignite EchoBoot")
        self.format_button.connect("clicked", self.on_ignite_clicked)
        vbox.pack_start(self.format_button, False, False, 0)

        self.scan_button = Gtk.Button(label="Scan for ISOs + Generate Boot Entries")
        self.scan_button.connect("clicked", self.on_scan_clicked)
        vbox.pack_start(self.scan_button, False, False, 0)

        # Status label
        self.status_label = Gtk.Label(label="Ready.")
        vbox.pack_end(self.status_label, False, False, 0)

    def populate_drives(self):
        # Stub: Populate with placeholder drives (to be wired to core.get_removable_drives())
        self.drive_combo.append_text("/dev/sdX - EchoDrive 32GB")
        self.drive_combo.append_text("/dev/sdY - FlameDisk 64GB")
        self.drive_combo.set_active(0)

    def on_ignite_clicked(self, widget):
        selected = self.drive_combo.get_active_text()
        self.status_label.set_text(f"Formatting {selected}...")
        # TODO: Call core.partition_and_format(selected)
        # TODO: Call core.install_bootloaders(selected)
        self.status_label.set_text("Drive ignited successfully!")

    def on_scan_clicked(self, widget):
        self.status_label.set_text("Scanning for ISOs...")
        # TODO: Call core.update_boot_entries()
        self.status_label.set_text("Boot entries updated.")


if __name__ == "__main__":
    win = EchoBootGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()