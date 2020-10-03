import re


def sf(data_rate):
    return re.findall(r"SF\d{1,2}", data_rate)[0]


class Packet:
    def __init__(self, dist, sf, payload_len, rssi, lsnr, freq, cod_rate, payload):
        self.cod_rate = cod_rate
        self.freq = freq
        self.lsnr = lsnr
        self.rssi = rssi
        self.payload_len = payload_len
        self.sf = sf
        self.dist = dist
        self.payload = payload

    @classmethod
    def from_gateway_message(cls, dist, msg, lorawan_message, payload):
        return cls(
            dist=dist,
            sf=sf(msg["datr"]),
            payload_len=len(lorawan_message.payload),
            rssi=msg["rssi"],
            lsnr=msg["lsnr"],
            freq=msg["freq"],
            cod_rate=msg["codr"],
            payload=payload,
        )

    def row(self):
        # TODO: modificare questa funzione per ottenere il formato csv corretto
        return (
            self.sf,
            self.payload_len,
            self.rssi,
            self.lsnr,
            self.cod_rate,
            self.payload,
        )
