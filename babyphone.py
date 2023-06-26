import gi
import RPi.GPIO as GPIO
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# GPIO-Pin für den Taster festlegen
BUTTON_PIN = 17

class BabyPhone:
    def __init__(self, target_ip):
        Gst.init(None)
        self.pipeline = Gst.Pipeline()

        # Elemente erstellen
        self.asrc = Gst.ElementFactory.make("alsasrc", "audio-source")
        self.audioconvert = Gst.ElementFactory.make("audioconvert", "audio-convert")
        self.audioresample = Gst.ElementFactory.make("audioresample", "audio-resample")
        self.speexenc = Gst.ElementFactory.make("speexenc", "speex-encoder")
        self.rtpspeexpay = Gst.ElementFactory.make("rtpspeexpay", "rtp-speex-pay")
        self.udpsink = Gst.ElementFactory.make("udpsink", "udp-sink")
        self.udpsrc = Gst.ElementFactory.make("udpsrc", "udp-source")
        self.rtpjitterbuffer = Gst.ElementFactory.make("rtpjitterbuffer", "rtp-jitter-buffer")
        self.rtpspeexdepay = Gst.ElementFactory.make("rtpspeexdepay", "rtp-speex-depay")
        self.speexdec = Gst.ElementFactory.make("speexdec", "speex-decoder")
        self.audioconvert2 = Gst.ElementFactory.make("audioconvert", "audio-convert-2")
        self.audioresample2 = Gst.ElementFactory.make("audioresample", "audio-resample-2")
        self.tee = Gst.ElementFactory.make("tee", "tee")
        self.queue1 = Gst.ElementFactory.make("queue", "queue1")
        self.queue2 = Gst.ElementFactory.make("queue", "queue2")
        self.sink = Gst.ElementFactory.make("alsasink", "audio-sink")

        # Elemente zur Pipeline hinzufügen
        self.pipeline.add(self.asrc)
        self.pipeline.add(self.audioconvert)
        self.pipeline.add(self.audioresample)
        self.pipeline.add(self.speexenc)
        self.pipeline.add(self.rtpspeexpay)
        self.pipeline.add(self.udpsink)
        self.pipeline.add(self.udpsrc)
        self.pipeline.add(self.rtpjitterbuffer)
        self.pipeline.add(self.rtpspeexdepay)
        self.pipeline.add(self.speexdec)
        self.pipeline.add(self.audioconvert2)
        self.pipeline.add(self.audioresample2)
        self.pipeline.add(self.tee)
        self.pipeline.add(self.queue1)
        self.pipeline.add(self.queue2)
        self.pipeline.add(self.sink)

        # Elemente verbinden
        self.asrc.link(self.audioconvert)
        self.audioconvert.link(self.audioresample)
        self.audioresample.link(self.speexenc)
        self.speexenc.link(self.rtpspeexpay)
        self.rtpspeexpay.link(self.udpsink)

        self.udpsrc.link(self.rtpjitterbuffer)
        self.rtpjitterbuffer.link(self.rtpspeexdepay)
        self.rtpspeexdepay.link(self.speexdec)
        self.speexdec.link(self.audioconvert2)
        self.audioconvert2.link(self.audioresample2)
        self.audioresample2.link(self.queue1)
        self.audioresample2.link(self.queue2)
        self.queue1.link(self.sink)

        # Taster-Interrupt hinzufügen
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=self.button_callback, bouncetime=300)

        # Ziel-IP-Adresse setzen
        self.udpsink.set_property("host", target_ip)
        self.udpsink.set_property("port", 6666)

        # Tasterstatus initialisieren
        self.is_speaking = False

    def button_callback(self, channel):
        # Taster wurde gedrückt
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            if not self.is_speaking:
                self.start_speaking()
            else:
                self.stop_speaking()

    def start_speaking(self):
        self.is_speaking = True
        self.queue2.unlink(self.sink)
        self.queue1.link(self.tee)
        self.tee.link(self.audioconvert2)

    def stop_speaking(self):
        self.is_speaking = False
        self.tee.unlink(self.audioconvert2)
        self.queue1.unlink(self.tee)
        self.queue2.link(self.sink)

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)

        try:
            GObject.MainLoop().run()
        except KeyboardInterrupt:
            pass

        self.pipeline.set_state(Gst.State.NULL)
        GPIO.cleanup()

if __name__ == "__main__":
    target_ip = "<Ziel-IP-Adresse>"
    baby_phone = BabyPhone(target_ip)
    baby_phone.run()
