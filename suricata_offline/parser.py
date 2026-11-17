"""Convert Suricata EVE JSON to the project's common event shape."""
import json

def parse_eve(path):
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            value = json.loads(line)
            if value.get("event_type") in {"alert", "flow", "dns", "http", "ssh"}:
                events.append(value)
    return events

def to_common_event(event, index):
    alert = event.get("alert") or {}
    return {"schema_version":"1.0", "event_id":"suricata-" + str(index),
            "source":"suricata-offline-pcap", "is_demo":False,
            "timestamp_utc":event.get("timestamp"), "src_ip":event.get("src_ip"),
            "dst_ip":event.get("dest_ip"), "src_port":event.get("src_port"),
            "dst_port":event.get("dest_port"), "protocol":event.get("proto"),
            "event_type":event.get("event_type"), "severity":alert.get("severity"),
            "signature":alert.get("signature"), "signature_id":alert.get("signature_id"),
            "evidence":[alert.get("signature")] if alert.get("signature") else [],
            "raw_event_type":event.get("event_type")}
