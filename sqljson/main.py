#!/usr/bin/env python3
import json
import re
import pandas as pd
import sys
import argparse


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

def run_query(json_data, query):
    try:
        df = pd.json_normalize(json_data)

        if "*" in query.split("from")[0].lower():
            select_cols = df.columns.tolist()
        else:
            select_cols = [col.strip() for col in query.split("from")[0].replace("select", "").strip().split(",")]

        if not query.lower().startswith("select"):
            raise ValueError("Only SELECT queries are supported.")

        if "where" in query.lower():
            condition_part = query.split("where")[1].strip().replace("this", "df")
            condition = process_conditions(condition_part, df)
            condition = re.sub(r'(?<!=)=(?!=)', '==', condition)
            result = df.query(condition)[select_cols]
        else:
            result = df[select_cols]

        # Flatten the resulting data
        flattened_results = [flatten_data(row) for row in result.values.tolist()]
        return flattened_results

    except pd.errors.UndefinedVariableError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Run SQL-like queries against JSON data.')
    parser.add_argument('-q', '--query', help='SQL-like query Ex: select ')
    parser.add_argument('-s', '--separator', default=",", help='Output format separator')
    parser.add_argument('-d', '--describe', action='store_true', help='Display all column names')
    args = parser.parse_args()


    json_data = json.load(sys.stdin)
    if args.describe:
        df = pd.json_normalize(json_data)
        print("\n".join(df.columns))
        return

    if args.query:
        results = run_query(json_data, args.query)
        for row in results:
            print(args.separator.join(map(str, row)))


if __name__ == "__main__":
    main()
