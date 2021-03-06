from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from .. import conf

class StatusBox(BoxLayout):
    def update(self, dt):
        data = conf.plugin._printer.get_current_data()

        self.ids.status.text = data['state']['text']

        file = data['job']['file']['name']
        if file == None:
            file = ""
        self.ids.file.text = file

class TemperatureLabel(BoxLayout):
    actual = StringProperty("--")
    target = StringProperty("--")
    title = StringProperty("")
    name = StringProperty("")

    def update(self, dt):
        temps = conf.plugin._printer.get_current_temperatures()

        if self.name in temps.keys():
            self.actual = str("%3.1f" % temps[self.name]['actual']) if temps[self.name]['actual'] > 1 else "--"
            self.target = str("%3.1f" % temps[self.name]['target']) if temps[self.name]['target'] > 1 else "--"
        else:
            self.actual = "--"
            self.target = "--"

class FilamentLabel(BoxLayout):
    length = StringProperty(" - - ")
    volume = StringProperty(" - - ")
    title = StringProperty("")
    name = StringProperty("")

    def update(self, filament):

        if filament != None and self.name in filament.keys():
            self.length = str("%.2f" % (filament[self.name]['length']/1000))
            self.volume = str("%3.2f" % filament[self.name]['volume'])
        else:
            self.length = " - - "
            self.volume = " - - "

class StatusTab(BoxLayout):

    tempBox = ObjectProperty(None)
    filaBox = ObjectProperty(None)

    profile = None
    oldProfile = None

    def update(self, dt):

        self.profile = conf.plugin._printer.get_current_connection()[3]

        if self.profile != self.oldProfile:
            self.tempBox.clear_widgets()
            self.filaBox.clear_widgets()
            if self.profile != None:
                if self.profile['heatedBed']:
                    bed_widget = TemperatureLabel()
                    bed_widget.title = "Bed:"
                    bed_widget.name = 'bed'
                    self.tempBox.add_widget(bed_widget)
                if self.profile['extruder']['count'] == 1:
                    extuder_widget = TemperatureLabel()
                    extuder_widget.title = "Tool:"
                    extuder_widget.name = 'tool0'
                    self.tempBox.add_widget(extuder_widget)

                    fila_widget = FilamentLabel()
                    fila_widget.title = "Usage:"
                    fila_widget.name = 'tool0'
                    self.filaBox.add_widget(fila_widget)

                else:
                    for i in range(self.profile['extruder']['count']):
                        extuder_widget = TemperatureLabel()
                        extuder_widget.title = "Tool " + str(i) + ":"
                        extuder_widget.name = 'tool' + str(i)
                        self.tempBox.add_widget(extuder_widget)

                        fila_widget = FilamentLabel()
                        fila_widget.title = "Tool " + str(i) + " Usage:"
                        fila_widget.name = 'tool' + str(i)
                        self.filaBox.add_widget(fila_widget)
            else:
                pass
            self.oldProfile = self.profile

        for i in self.tempBox.children:
            if isinstance(i, TemperatureLabel):
                i.update(dt)

        for i in self.filaBox.children:
            if isinstance(i, FilamentLabel):
                i.update(conf.plugin._printer.get_current_data()['job']['filament'])

        data = conf.plugin._printer.get_current_data()

        self.ids.status_label.text = data['state']['text']

        if data['state']['flags']['printing'] :
            self.ids.print_button.text = "Print"
            self.ids.pause_button.text = "Pause"

            self.ids.print_button.disabled = True
            self.ids.pause_button.disabled = False
            self.ids.cancel_button.disabled = False
        elif data['state']['flags']['paused']:
            self.ids.print_button.text = "Restart"
            self.ids.pause_button.text = "Resume"

            self.ids.print_button.disabled = False
            self.ids.pause_button.disabled = False
            self.ids.cancel_button.disabled = False
        else:
            self.ids.print_button.text = "Print"
            self.ids.pause_button.text = "Pause"

            if data['job']['file']['name'] == None:
                self.ids.print_button.disabled = True
            else:
                self.ids.print_button.disabled = False

            self.ids.pause_button.disabled = True
            self.ids.cancel_button.disabled = True

        file = data['job']['file']['name']
        if file == None:
            file = "No File Loaded"
        self.ids.file_label.text = file

        timein = data['progress']['printTime']

        if not timein == None:
            m, s = divmod(int(timein), 60)
            h, m = divmod(m, 60)
        else:
            h, m, s = 0, 0, 0

        self.ids.time_in.time = str("%02d:%02d:%02d" % (h, m, s))

        timeleft = data['progress']['printTimeLeft']

        if not timeleft == None:
            m, s = divmod(int(timeleft), 60)
            h, m = divmod(m, 60)
        else:
            h, m, s = 0, 0, 0

        self.ids.time_remaining.time = str("%02d:%02d:%02d" % (h, m, s))

        timetotal = data['job']['lastPrintTime']

        if timetotal == None:
            timetotal = data['job']['estimatedPrintTime']

        if not timetotal == None:
            m, s = divmod(int(timetotal), 60)
            h, m = divmod(m, 60)
        else:
            h, m, s = 0, 0, 0

        self.ids.time_total.time = str("%02d:%02d:%02d" % (h, m, s))

        prog = data['progress']['completion']

        if prog == None:
            prog = 0

        self.ids.progress.value = prog
