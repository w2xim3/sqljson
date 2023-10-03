import json
import sys
from io import StringIO

from sqljson.main import run_query, main


def test_run_query_select_all():
    data = json.load(open("nested.json"))
    result = run_query(data, 'select * from this')
    expected = ['John', 30, 'home', '123-456-7890', 'work', '098-765-4321', 'john.doe@example.com', True, 'dog', 'Rex', 'cat', 'Whiskers', '123 Main St', 'Anytown', 'CA', '12345']  # flattened expected result
    assert result[0] == expected


def test_describe_option_with_mocking():
    mock_data = json.dumps(json.load(open("crt.sh.json", "r")))
    sys.stdin = StringIO(mock_data)
    sys.stdout = result = StringIO()
    sys.argv = ["main.py", "-d"]
    main()
    captured_output = result.getvalue()
    assert captured_output == """issuer_ca_id\nissuer_name\ncommon_name\nname_value\nid\nentry_timestamp\nnot_before\nnot_after\nserial_number\n"""