import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

class BackendBabyPhone:
    def __init__(self):
        Gst.init(None)
        self.pipeline = Gst.Pipeline()

        # Elemente erstellen
        self.udpsrc = Gst.ElementFactory.make("udpsrc", "udp-source")
        caps = Gst.Caps.from_string("application/x-rtp, media=(string)audio, clock-rate=(int)16000, encoding-name=(string)SPEEX, encoding-params=(string)1, payload=(int)110")
        self.udpsrc.set_property("caps", caps)
        self.rtpjitterbuffer = Gst.ElementFactory.make("rtpjitterbuffer", "rtp-jitter-buffer")
        self.rtpspeexdepay = Gst.ElementFactory.make("rtpspeexdepay", "rtp-speex-depay")
        self.speexdec = Gst.ElementFactory.make("speexdec", "speex-decoder")
        self.audioconvert = Gst.ElementFactory.make("audioconvert", "audio-convert")
        self.audioresample = Gst.ElementFactory.make("audioresample", "audio-resample")
        self.alsasink = Gst.ElementFactory.make("alsasink", "alsa-sink")

        # Elemente zur Pipeline hinzufügen
        self.pipeline.add(self.udpsrc)
        self.pipeline.add(self.rtpjitterbuffer)
        self.pipeline.add(self.rtpspeexdepay)
        self.pipeline.add(self.speexdec)
        self.pipeline.add(self.audioconvert)
        self.pipeline.add(self.audioresample)
        self.pipeline.add(self.alsasink)

        # Elemente verbinden
        self.udpsrc.link(self.rtpjitterbuffer)
        self.rtpjitterbuffer.link(self.rtpspeexdepay)
        self.rtpspeexdepay.link(self.speexdec)
        self.speexdec.link(self.audioconvert)
        self.audioconvert.link(self.audioresample)
        self.audioresample.link(self.alsasink)

    def start(self):
        # Pipeline starten
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        # Pipeline stoppen und aufräumen
        self.pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    backend = BackendBabyPhone()
    backend.start()
