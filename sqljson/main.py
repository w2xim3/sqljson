#!/usr/bin/env python3
import json
import re
import pandas as pd
import sys
import argparse
from termcolor import colored, cprint

VERSION = "0.1.7"
def gradient_color(value, total):
    """ Create a rainbow gradient transitioning from red to blue """
    segments = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (127, 255, 0),  # Chartreuse
        (0, 255, 0),    # Green
        (0, 255, 127),  # Spring Green
        (0, 255, 255),  # Cyan
        (0, 127, 255),  # Azure
        (0, 0, 255)     # Blue
    ]

    segment_length = total / (len(segments) - 1)

    start_segment = int(value // segment_length)
    t = (value % segment_length) / segment_length  # Normalized value within the segment

    if start_segment == len(segments) - 1:
        return segments[-1]

    # Interpolate between two segment colors
    r = int(segments[start_segment][0] + t * (segments[start_segment + 1][0] - segments[start_segment][0]))
    g = int(segments[start_segment][1] + t * (segments[start_segment + 1][1] - segments[start_segment][1]))
    b = int(segments[start_segment][2] + t * (segments[start_segment + 1][2] - segments[start_segment][2]))

    return r, g, b


def colored_row(row):
    row = list(row)
    colored_items = []
    total_items = len(row)
    for idx, item in enumerate(row):
        r, g, b = gradient_color(idx, total_items)
        colored_item = f"\033[38;2;{r};{g};{b}m{item}"
        colored_items.append(colored_item)
    return colored_items
def process_conditions(condition_part, df):
    conditions = re.split(r'\s+(and|or)\s+', condition_part)
    adjusted_conditions = []

    for i in range(0, len(conditions), 2):
        condition = adjust_condition_to_dtype(conditions[i].strip(), df)
        for column in df.columns:
            if "." in column:
                condition = condition.replace(column, f"`{column}`")
        adjusted_conditions.append(condition)

        if i + 1 < len(conditions):
            adjusted_conditions.append(conditions[i + 1])

    return " ".join(adjusted_conditions)


def process_input():
    """Yield each JSON object from stdin."""
    buffer = ""
    for line in sys.stdin:
        buffer += line
        try:
            yield json.loads(buffer)
            buffer = ""
        except json.JSONDecodeError:
            continue


def adjust_condition_to_dtype(condition, df):
    parts = condition.split()
    if parts[0] in df.columns:
        column_dtype = df[parts[0]].dtype
        if "int" in str(column_dtype) and parts[2].startswith('"') and parts[2].endswith('"'):
            parts[2] = parts[2].strip('"')
    return ' '.join(parts)


def process_conditions(condition_part, df):
    conditions = re.split(r'\s+(and|or)\s+', condition_part)
    adjusted_conditions = []

    for i in range(0, len(conditions), 2):
        condition = adjust_condition_to_dtype(conditions[i].strip(), df)

        for column in df.columns:
            if "." in column:
                condition = condition.replace(column, f"`{column}`")

        adjusted_conditions.append(condition)

        if i + 1 < len(conditions):
            adjusted_conditions.append(conditions[i + 1])

    return " ".join(adjusted_conditions)


def flatten_data(data):
    output = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                output.extend(flatten_data(value))
            else:
                output.append(value)
    elif isinstance(data, list):
        for item in data:
            output.extend(flatten_data(item))
    else:
        output.append(data)
    return output


def run_query(json_data, query, debug=False):
    try:
        df = pd.json_normalize(json_data)

        # Trim and split columns
        if "select" not in query.lower() and "from" not in query.lower() and "," in query:
            # Lazy Mode
            parts = query.split(" where ")
            select_cols = [col.strip() for col in parts[0].split(",")]
            if len(parts) > 1:
                condition_part = parts[1].replace("this", "df")
                condition = process_conditions(condition_part, df)
                condition = re.sub(r'(?<!=)=(?!=)', '==', condition)
                result = df.query(condition)[select_cols]
            else:
                result = df[select_cols]
        elif "*" in query.split("from")[0].lower():
            select_cols = df.columns.tolist()
            result = df[select_cols]
        else:
            select_cols = [col.strip() for col in query.split("from")[0].replace("select", "").strip().split(",")]
            if "where" in query.lower():
                condition_part = query.split("where")[1].strip().replace("this", "df")
                condition = process_conditions(condition_part, df)
                condition = re.sub(r'(?<!=)=(?!=)', '==', condition)
                result = df.query(condition)[select_cols]
            else:
                result = df[select_cols]

        for col in select_cols:
            if col not in df.columns:
                raise KeyError(f"Column '{col}' not found in data.")

        flattened_results = [flatten_data(row) for row in result.values.tolist()]
        return flattened_results

    except (pd.errors.UndefinedVariableError, KeyError, Exception) as e:
        if debug:
            if isinstance(e, KeyError):
                print(f"Error: {e}")
            elif isinstance(e, pd.errors.UndefinedVariableError):
                print(f"Error: {e}")
                sys.exit(1)
            else:
                print(f"Unexpected Error: {e}")
                sys.exit(1)
        return []


def main():
    parser = argparse.ArgumentParser(description='Run SQL-like queries against JSON data.')
    parser.add_argument('query', nargs='?',help='SQL-like query or columns for lazy mode')  # nargs='?' makes it optional
    parser.add_argument('-s', '--separator', default=",", help='Output format separator')
    parser.add_argument('-d', '--describe', action='store_true', help='Display all column names')
    parser.add_argument('-dv', '--describe_value', action='store_true',help='Display all column names with sample values')
    parser.add_argument('-v', '--debug', action='store_true', help='Enable detailed error messages')
    parser.add_argument('-nc', '--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {VERSION}",help="Show the version number and exit.")

    args = parser.parse_args()
    if not args.query and not any([args.describe, args.describe_value]):
        parser.error("You need to provide a query or use one of the flags (-d, -dv)")

    for json_data in process_input():
        if args.describe:
            df = pd.json_normalize(json_data)
            print("\n".join(df.columns))
        elif args.describe_value:
            if isinstance(json_data, list) and len(json_data) > 0:
                df_sample = pd.json_normalize(json_data[0])
            elif isinstance(json_data, dict):
                df_sample = pd.json_normalize(json_data)
            else:
                df_sample = pd.DataFrame()  # Empty DataFrame

            max_column_width = max([len(col) for col in df_sample.columns] + [12])  # 12 is the length of "Column Name"
            sample_values = df_sample.iloc[0] if not df_sample.empty else []

            print(colored(f"{'Column Name'.ljust(max_column_width)} | Sample Value", 'cyan'))
            print(colored('-' * max_column_width + "-+-" + '-' * 30,
                          'cyan'))  # Adjust 30 based on expected max sample value length

            for column in df_sample.columns:
                value = str(sample_values[column]) if column in sample_values else ''
                print(colored(f"{column.ljust(max_column_width)} | {value}", 'green'))
            break
        elif args.query:
            results = run_query(json_data, args.query, debug=args.debug)
            for row in results:
                if args.no_color:
                    print(args.separator.join(map(str, row)))
                else:
                    if sys.stdout.isatty():
                        cprint(args.separator.join(colored_row(map(str, row))))
                    else:
                        print(args.separator.join(map(str, row)))
                        pass



if __name__ == "__main__":
    main()

