MAPPING_TEMPLATE = {
    "properties": {
        "@timestamp": {"type": "date"},
        "amount": {"type": "double"},
        "candidate": {
            "properties": {
                "district": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "filerId": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "office": {
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
        "contributionId": {"type": "keyword"},
        "contributionDate": {"type": "date", "format": "iso8601"},
        "employer": {"type": "text"},
        "filer": {
            "properties": {
                "filerId": {
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
        "jobTitle": {"type": "keyword"},
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