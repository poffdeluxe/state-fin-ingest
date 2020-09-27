MAPPING_TEMPLATE = {
    "properties": {
        "amount": {"type": "double"},
        "candidate": {
            "properties": {
                "district": {"type": "short"},
                "candidate_id": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "house": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "party": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "status": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
            }
        },
        "city": {"type": "keyword"},
        "contribution_id": {"type": "keyword"},
        "contribution_date": {"type": "date", "format": "iso8601"},
        "employer": {"type": "text"},
        "filer": {
            "properties": {
                "filer_id": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "type": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
            }
        },
        "job_title": {"type": "keyword"},
        "memo": {"type": "keyword"},
        "name": {
            "type": "text",
            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
        },
        "occupation": {"type": "keyword"},
        "state": {"type": "keyword"},
        "type": {"type": "keyword"},
        "zip": {"type": "keyword"},
        "addtl_data": {"type": "object"},
    }
}