import argparse
import json

from xsd2json_schemey import xsd_to_json_schema


def main():
    parser = argparse.ArgumentParser(description="Xsd2JsonSchemey")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=None)
    args, _ = parser.parse_known_args()
    input_ = args.input
    output = args.output
    if output is None:
        output = input_ + ".json"
    schema = xsd_to_json_schema(input_)
    with open(output, "w") as f:
        json.dump(schema, f, indent=2)


if __name__ == "__main__":
    main()
