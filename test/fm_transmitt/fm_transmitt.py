#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Fm Transmitt
# Author: aruncs
# GNU Radio version: 3.10.11.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import threading



class fm_transmitt(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Fm Transmitt", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Fm Transmitt")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "fm_transmitt")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.volume_adjst = volume_adjst = 5
        self.samp_rate = samp_rate = int(44e3)
        self.fc = fc = int(100e6)

        ##################################################
        # Blocks
        ##################################################

        self._volume_adjst_range = qtgui.Range(5, 100, 1, 5, 200)
        self._volume_adjst_win = qtgui.RangeWidget(self._volume_adjst_range, self.set_volume_adjst, "'volume_adjst'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_adjst_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=100,
                decimation=5,
                taps=[],
                fractional_bw=0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('192.168.2.1' if '192.168.2.1' else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(int(1e6))
        self.iio_pluto_sink_0.set_frequency(int(100e6))
        self.iio_pluto_sink_0.set_samplerate(int(1e6))
        self.iio_pluto_sink_0.set_attenuation(0, 5)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/aruncs/Music/chammak.wav', False)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(0)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.band_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                300,
                int(16e3),
                1,
                window.WIN_HAMMING,
                6.76))
        self.audio_sink_0 = audio.sink(samp_rate, '', True)
        self.analog_sig_source_x_0 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, 5e3, (1e-2), 0, 0)
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=int(48e3),
        	quad_rate=int(192e3),
        	tau=(75e-6),
        	max_dev=5e3,
        	fh=(-1.0),
                )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_tx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.audio_sink_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_wavfile_source_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.iio_pluto_sink_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "fm_transmitt")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_volume_adjst(self):
        return self.volume_adjst

    def set_volume_adjst(self, volume_adjst):
        self.volume_adjst = volume_adjst

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, 300, int(16e3), 1, window.WIN_HAMMING, 6.76))

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc




def main(top_block_cls=fm_transmitt, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
