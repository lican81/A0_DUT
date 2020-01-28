from flexx import flx
from line import plot_line


class MainComponent(flx.PyComponent):
    def init(self):
        # super.init()
        with flx.VBox(flex=1):
            with flx.HBox(flex=1) as self.hbox_ser:
                self.edit_usb = flx.LineEdit(
                    placeholder_text='Serial port name: (COMx for Windows)', flex=1)

            with flx.HBox(flex=1) as self.hbox_cmd:
                self.edit_cmd = flx.LineEdit(
                    placeholder_text='Command to send', flex=8)
                self.but_send = flx.Button(text='Send', flex=2)

            with flx.HBox(flex=8):
                self.lab_cmd = flx.Label()

    @flx.reaction('but_send.pointer_click', 'edit_cmd.submit')
    def _send_cmd(self, *events):
        serUSB = self.edit_usb.text
        cmd = self.edit_cmd.text
        print(f'serUSB={serUSB}, cmd={cmd}')
        self.lab_cmd.set_text(f'serUSB={serUSB}, cmd={cmd}')
        plot_line()

    # @flx.reaction('but2.pointer_click')
    # def but2_clicked(self, *events):
    #     print('but2 clicked')


class MainApp(flx.PyComponent):
    def init(self):
        MainComponent()


app = flx.App(MainApp)
app.launch('app')  # to run as a desktop app
flx.run()  # mainloop will exit when the app is closed
