# SQLJSON
A powerful tool that allows users to query JSON data using SQL-like syntax. Effortlessly search, filter, and manipulate your JSON data with familiar SQL queries.

This tool support:
select, where ,or ,and.

Note: I added "from this" as default table to To remain consistent with the SQL syntax, however, the double '==' is represented by a '='.

## Installation

```bash
pip install sqljson
```
# Usage example:

```bash
usage: sqljson [-h] [-q QUERY] [-s SEPARATOR] [-d]

Run SQL-like queries against JSON data.

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        SQL-like query Ex: select
  -s SEPARATOR, --separator SEPARATOR
                        Output format separator
  -d, --describe        Display all column names
```

## Describe json like a describe table
```bash
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | sqljson -d
issuer_ca_id
issuer_name
common_name
name_value
id
entry_timestamp
not_before
not_after
serial_number
```

## Select

```bash
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | sqljson -q 'select not_before,common_name from this'
2007-11-02T16:04:00,portailgmr.recyc-quebec.gouv.qc.ca
2012-07-26T19:41:37,quewlc02.mri.gouv.qc.ca
2009-04-07T13:20:59,divulgation.gouv.qc.ca
2009-02-19T19:54:26,services.immigration-quebec.gouv.qc.ca
2009-05-27T19:37:37,www.cse.gouv.qc.ca
2009-01-06T16:24:38,www.agencesss12.gouv.qc.ca
```

```bash 
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | sqljson -q 'select not_before,common_name from this where not_before > "2012"'
2012-07-26T19:41:37,quewlc02.mri.gouv.qc.ca
2014-05-04T09:33:46,blackberry.clp.gouv.qc.ca
2012-10-11T15:54:26,www.pag.cldc.cspq.gouv.qc.ca
```

## Support nested json

```json
cat nested.json 
{
  "name": "John",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postalCode": "12345"
  },
  "phones": [
    {
      "type": "home",
      "number": "123-456-7890"
    },
    {
      "type": "work",
      "number": "098-765-4321"
    }
  ],
  "email": "john.doe@example.com",
  "hasPets": true,
  "pets": [
    {
      "type": "dog",
      "name": "Rex"
    },
    {
      "type": "cat",
      "name": "Whiskers"
    }
  ]
}
```

```bash
cat nested.json | sqljson -q 'select address.city from this'
Anytown
```