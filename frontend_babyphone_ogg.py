import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

class FrontendBabyPhone:
    def __init__(self, target_ip):
        Gst.init(None)
        self.pipeline = Gst.Pipeline()

        # Elemente erstellen
        self.filesrc = Gst.ElementFactory.make("filesrc", "file-source")
        self.wavparse = Gst.ElementFactory.make("wavparse", "wav-parser")
        self.audioconvert = Gst.ElementFactory.make("audioconvert", "audio-convert")
        self.audioresample = Gst.ElementFactory.make("audioresample", "audio-resample")
        self.speexenc = Gst.ElementFactory.make("speexenc", "speex-encoder")
        self.rtpspeexpay = Gst.ElementFactory.make("rtpspeexpay", "rtp-speex-pay")
        self.udpsink = Gst.ElementFactory.make("udpsink", "udp-sink")

        # Elemente zur Pipeline hinzufügen
        self.pipeline.add(self.filesrc)
        self.pipeline.add(self.wavparse)
        self.pipeline.add(self.audioconvert)
        self.pipeline.add(self.audioresample)
        self.pipeline.add(self.speexenc)
        self.pipeline.add(self.rtpspeexpay)
        self.pipeline.add(self.udpsink)

        # Elemente verbinden
        self.filesrc.link(self.wavparse)
        self.wavparse.link(self.audioconvert)
        self.audioconvert.link(self.audioresample)
        self.audioresample.link(self.speexenc)
        self.speexenc.link(self.rtpspeexpay)
        self.rtpspeexpay.link(self.udpsink)

        # Parameter setzen
        self.udpsink.set_property("host", target_ip)
        self.udpsink.set_property("port", 6666)

    def start(self, file_path):
        # Parameter für filesrc setzen
        self.filesrc.set_property("location", file_path)

        # Pipeline starten
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        # Pipeline stoppen und aufräumen
        self.pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    frontend = FrontendBabyPhone("<target-IP>")
    frontend.start("<Pfad_zur_OGG_Datei>")
