#!/usr/bin/env python

from gnuradio import gr
from gnuradio import qtgui
from PyQt4 import QtGui, QtCore
import sys, sip

class dialog_box(QtGui.QWidget):
    def __init__(self, display, control):
        QtGui.QWidget.__init__(self, None)
        self.setWindowTitle('PyQt Test GUI')

        self.boxlayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, self)
        self.boxlayout.addWidget(display, 1)
        self.boxlayout.addWidget(control)

        self.resize(800, 500)

class control_box(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Control Panel')

        self.setToolTip('Control the signals')
        QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))

        self.layout = QtGui.QFormLayout(self)

        # Control the first signal
        self.freq1Edit = QtGui.QLineEdit(self)
        self.freq1Edit.setMinimumWidth(100)
        self.layout.addRow("Signal 1 Frequency:", self.freq1Edit)
        self.connect(self.freq1Edit, QtCore.SIGNAL("editingFinished()"),
                     self.freq1EditText)

        self.amp1Edit = QtGui.QLineEdit(self)
        self.amp1Edit.setMinimumWidth(100)
        self.layout.addRow("Signal 1 Amplitude:", self.amp1Edit)
        self.connect(self.amp1Edit, QtCore.SIGNAL("editingFinished()"),
                     self.amp1EditText)


        # Control the second signal
        self.freq2Edit = QtGui.QLineEdit(self)
        self.freq2Edit.setMinimumWidth(100)
        self.layout.addRow("Signal 2 Frequency:", self.freq2Edit)
        self.connect(self.freq2Edit, QtCore.SIGNAL("editingFinished()"),
                     self.freq2EditText)


        self.amp2Edit = QtGui.QLineEdit(self)
        self.amp2Edit.setMinimumWidth(100)
        self.layout.addRow("Signal 2 Amplitude:", self.amp2Edit)
        self.connect(self.amp2Edit, QtCore.SIGNAL("editingFinished()"),
                     self.amp2EditText)

        self.quit = QtGui.QPushButton('Close', self)
        self.quit.setMinimumWidth(100)
        self.layout.addWidget(self.quit)

        self.connect(self.quit, QtCore.SIGNAL('clicked()'),
                     QtGui.qApp, QtCore.SLOT('quit()'))

    def attach_signal1(self, signal):
        self.signal1 = signal
        self.freq1Edit.setText(QtCore.QString("%1").arg(self.signal1.frequency()))
        self.amp1Edit.setText(QtCore.QString("%1").arg(self.signal1.amplitude()))

    def attach_signal2(self, signal):
        self.signal2 = signal
        self.freq2Edit.setText(QtCore.QString("%1").arg(self.signal2.frequency()))
        self.amp2Edit.setText(QtCore.QString("%1").arg(self.signal2.amplitude()))

    def freq1EditText(self):
        try:
            newfreq = float(self.freq1Edit.text())
            self.signal1.set_frequency(newfreq)
        except ValueError:
            print "Bad frequency value entered"

    def amp1EditText(self):
        try:
            newamp = float(self.amp1Edit.text())
            self.signal1.set_amplitude(newamp)
        except ValueError:
            print "Bad amplitude value entered"

        
    def freq2EditText(self):
        try:
            newfreq = float(self.freq2Edit.text())
            self.signal2.set_frequency(newfreq)
        except ValueError:
            print "Bad frequency value entered"

    def amp2EditText(self):
        try:
            newamp = float(self.amp2Edit.text())
            self.signal2.set_amplitude(newamp)
        except ValueError:
            print "Bad amplitude value entered"


class my_top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        Rs = 8000
        f1 = 100
        f2 = 200

        npts = 2048

        self.qapp = QtGui.QApplication(sys.argv)
        
        src1 = gr.sig_source_c(Rs, gr.GR_SIN_WAVE, f1, 0.1, 0)
        src2 = gr.sig_source_c(Rs, gr.GR_SIN_WAVE, f2, 0.1, 0)
        src  = gr.add_cc()
        channel = gr.channel_model(0.01)
        thr = gr.throttle(gr.sizeof_gr_complex, 100*npts)
        self.snk1 = qtgui.time_sink_c(npts, Rs,
                                      "Complex Time Example", 3)

        self.connect(src1, (src,0))
        self.connect(src2, (src,1))
        self.connect(src,  channel, thr, (self.snk1, 0))
        self.connect(src1, (self.snk1, 1))
        self.connect(src2, (self.snk1, 2))

        self.ctrl_win = control_box()
        self.ctrl_win.attach_signal1(src1)
        self.ctrl_win.attach_signal2(src2)

        # Get the reference pointer to the SpectrumDisplayForm QWidget
        pyQt  = self.snk1.pyqwidget()

        # Wrap the pointer as a PyQt SIP object
        # This can now be manipulated as a PyQt4.QtGui.QWidget
        pyWin = sip.wrapinstance(pyQt, QtGui.QWidget)

        # Example of using signal/slot to set the title of a curve
        pyWin.connect(pyWin, QtCore.SIGNAL("setTitle(int, QString)"),
                      pyWin, QtCore.SLOT("setTitle(int, QString)"))
        pyWin.emit(QtCore.SIGNAL("setTitle(int, QString)"), 0, "Re{sum}")
        self.snk1.set_title(1, "Im{Sum}")
        self.snk1.set_title(2, "Re{src1}")
        self.snk1.set_title(3, "Im{src1}")
        self.snk1.set_title(4, "Re{src2}")
        self.snk1.set_title(5, "Im{src2}")

        # Can also set the color of a curve
        #self.snk1.set_color(5, "blue")

        #pyWin.show()
        self.main_box = dialog_box(pyWin, self.ctrl_win)
        self.main_box.show()
        
if __name__ == "__main__":
    tb = my_top_block();
    tb.start()
    tb.qapp.exec_()
    tb.stop()
    
