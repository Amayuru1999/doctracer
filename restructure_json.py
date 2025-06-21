import argparse
import json

def restructure_json(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as infile:
        # Read all content
        file_content = infile.read().strip()

        # If there's more than one JSON object in the file, handle them
        if file_content.startswith("{"):
            # Ensure it's wrapped in square brackets to form a valid array
            data = [json.loads(file_content)]
        else:
            # If it's already a valid array, load the JSON as a list
            data = json.loads(f'[{file_content}]')

    # Restructure the JSON data
    structured_data = {
        "gazette_id": data[0]["gazette_id"],  # Assuming all JSON objects have the same gazette_id and date
        "published_date": data[0]["published_date"],
        "ministers": []
    }

    for entry in data:
        for minister in entry["ministers"]:
            structured_data["ministers"].append({
                "name": minister["name"],
                "functions": minister["functions"],
                "departments": minister["departments"],
                "laws": minister["laws"]
            })

    # Write the restructured JSON to the output file
    with open(output_file, 'w') as outfile:
        json.dump(structured_data, outfile, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Restructure multiple JSON objects into a single JSON structure.')
    parser.add_argument('input_file', type=str, help='Path to the input JSON file containing multiple JSON objects')
    parser.add_argument('output_file', type=str, help='Path to the output JSON file')

    args = parser.parse_args()

    restructure_json(args.input_file, args.output_file)
    print(f'Restructured JSON saved to {args.output_file}')

if __name__ == '__main__':
    main()
