import re
import argparse

def parse_csv_line(line):
    """
    Parses a single line from 剪辑模型统计结果.csv file.
    """
    # Regex pattern to capture all fields in the CSV line
    pattern = r"companyId:\s*(?P<companyId>\d+),\s*industryId:\s*(?P<industryId>\d+),\s*" + \
              r"startDate:\s*(?P<startDate>[\d-]+ \d+:\d+:\d+),\s*endDate:\s*(?P<endDate>[\d-]+ \d+:\d+:\d+),\s*" + \
              r"modelName:(?P<modelName>[^:]+)\s+countNum:(?P<countNum>\d+)\s+" + \
              r"areaCountMap:\s*(?P<areaCountMap>\{.*\})"
    
    match = re.match(pattern, line)
    if not match:
        print(f"Warning: Could not parse line: {line.strip()}")
        return None

    data = match.groupdict()
    
    # Clean up the data
    data['modelName'] = data['modelName'].strip()
    data['startDate'] = data['startDate'].split()[0]  # Extract just the date part
    data['endDate'] = data['endDate'].split()[0]  # Extract just the date part
    
    # Parse the areaCountMap
    area_map_str = data['areaCountMap']
    if area_map_str == "{}":
        data['areaCountMap'] = {}
    else:
        # Process the area map string
        processed_map_str = area_map_str[1:-1]  # Remove '{' and '}'
        pairs = processed_map_str.split(', ')  # Split into key-value pairs
        
        area_map = {}
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                area_map[key.strip()] = int(value.strip())
        
        data['areaCountMap'] = area_map
    
    return data

def format_entry_to_table(entry):
    """
    Formats a parsed entry into a nicely formatted table.
    """
    if not entry:
        return ""
    
    lines = []
    key_width = 15
    value_width = 30
    
    # Header section
    lines.append(f"| {'companyId'.ljust(key_width)} | {str(entry['companyId']).ljust(value_width)} |")
    lines.append(f"| {'industryId'.ljust(key_width)} | {str(entry['industryId']).ljust(value_width)} |")
    lines.append(f"|{'-' * (key_width + 2)}|{'-' * (value_width + 2)}|")
    lines.append(f"| {'startDate'.ljust(key_width)} | {str(entry['startDate']).ljust(value_width)} |")
    lines.append(f"| {'endDate'.ljust(key_width)} | {str(entry['endDate']).ljust(value_width)} |")
    lines.append(f"| {'modelName'.ljust(key_width)} | {str(entry['modelName']).ljust(value_width)} |")
    lines.append(f"| {'countNum'.ljust(key_width)} | {str(entry['countNum']).ljust(value_width)} |")
    lines.append(f"| {'area'.ljust(key_width)} | {'count'.ljust(value_width)} |")
    lines.append(f"|{'-' * (key_width + 2)}|{'-' * (value_width + 2)}|")
    
    # Area counts section - sorted by count in descending order
    area_map = entry.get('areaCountMap', {})
    sorted_areas = sorted(area_map.items(), key=lambda item: item[1], reverse=True)
    
    for area, count in sorted_areas:
        lines.append(f"| {str(area).ljust(key_width)} | {str(count).ljust(value_width)} |")
    
    return "\n".join(lines)

def main(input_file: str, output_file: str):
    
    all_tables = []
    total_countNum = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                parsed_data = parse_csv_line(line)
                if parsed_data:
                    table_str = format_entry_to_table(parsed_data)
                    all_tables.append(table_str)
                    total_countNum += int(parsed_data['countNum'])
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write("\n\n\n".join(all_tables))
            f_out.write(f"\n\n\nTotal countNum: {total_countNum}")
        print(f"Successfully formatted data and wrote to '{output_file}'")
    except IOError:
        print(f"Error: Could not write to output file '{output_file}'.")

def parse_args():
    parser = argparse.ArgumentParser(description="Format model statistics CSV into tables")
    parser.add_argument("-i", "--input", default="剪辑模型统计结果.csv", help="Input CSV file")
    parser.add_argument("-o", "--output", default="剪辑模型统计结果_formatted.txt", help="Output formatted text file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.output)
