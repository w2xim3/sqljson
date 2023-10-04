# SQLJSON
A powerful tool that allows users to query JSON data using SQL-like syntax. Effortlessly search, filter, and manipulate your JSON data with familiar SQL queries.

This tool was created solely to simplify searching. While jq works very well, remembering its syntax can become more cumbersome as the query becomes more complex. That's the reason this tool exists. 

Lazy mode was implemented.
![img_1.png](img_1.png)

```bash
cat file.json | \
jq '.[] | select((.not_before > "2012") or (.id == "1")) | {not_before, common_name}'

cat file.json | \
sqljson 'select not_before,common_name from this where not_before > "2012" or id ="1"' 

# Lazymode remove select and from you only chose what you want ans condition

cat file.json | \
sqljson 'not_before,common_name where not_before > "2012" or id ="1"'

cat file.json | sqljson not_before,common_name
```

This tool support:
select, where ,or ,and.

Note: I added "from this" as default table to To remain consistent with the SQL syntax, however, the double '==' is represented by a '='.

## Installation

```bash
pip install sqljson
```
# Usage example:

```bash
usage: sqljson [-h] [-s SEPARATOR] [-d] [-dv] [-v] [-nc] [-V] [query]

Run SQL-like queries against JSON data.

positional arguments:
  query                 SQL-like query or columns for lazy mode

options:
  -h, --help            show this help message and exit
  -s SEPARATOR, --separator SEPARATOR
                        Output format separator
  -d, --describe        Display all column names
  -dv, --describe_value
                        Display all column names with sample values
  -v, --debug           Enable detailed error messages
  -nc, --no-color       Disable colored output
  -V, --version         Show the version number and exit.
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
## Describe column and sample of value
```bash
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | sqljson -dv
Column Name     | Sample Value
----------------+-------------------------------
issuer_ca_id    | 101
issuer_name     | C=US, O=Equifax Secure Inc., CN=Equifax Secure Global eBusiness CA-1
common_name     | portailgmr.recyc-quebec.gouv.qc.ca
name_value      | portailgmr.recyc-quebec.gouv.qc.ca
id              | 2387331592
entry_timestamp | 2020-01-29T02:52:52.6
not_before      | 2007-11-02T16:04:00
not_after       | 2010-11-02T16:04:00
serial_number   | 071436

```

## Select

```bash
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | \
sqljson 'select not_before,common_name from this'
2007-11-02T16:04:00,portailgmr.recyc-quebec.gouv.qc.ca
2012-07-26T19:41:37,quewlc02.mri.gouv.qc.ca
2009-04-07T13:20:59,divulgation.gouv.qc.ca
2009-02-19T19:54:26,services.immigration-quebec.gouv.qc.ca
2009-05-27T19:37:37,www.cse.gouv.qc.ca
2009-01-06T16:24:38,www.agencesss12.gouv.qc.ca
```

```bash 
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | \
sqljson 'select not_before,common_name from this where not_before > "2012"'
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
cat nested.json | sqljson 'select address.city from this'
cat nested.json | sqljson address.city # Lazy mode
Anytown
```
## Lazy mode
```bash
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | \
sqljson common_name | \
httpx -title -silent -j | \
sqljson url,title

http://divulgation.gouv.qc.ca,Not Found
https://www.agencesss12.gouv.qc.ca,Oops, an error occurred!
http://www.mri.gouv.qc.ca,Document Moved
https://courriel.sdbj.gouv.qc.ca,Zimbra Web Client Sign In
https://www.cse.gouv.qc.ca,Accueil - CSE Conseil supérieur de l'éducation CSE
```

```bash
curl -s 'https://crt.sh?o=gouv.qc.ca&output=json' | \
sqljson common_name | \
httpx -title -silent -j | \
sqljson 'url,title where title = "Zimbra Web Client Sign In"'

https://courriel.sdbj.gouv.qc.ca,Zimbra Web Client Sign In
```