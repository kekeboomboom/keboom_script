import re
import ast

def parse_log_line(line):
    """
    Parses a single line from rawLog.txt.
    """
    # Regex to capture fields, allowing for flexible spacing and robust taskName capture
    match = re.match(
        r"taskId:\s*(?P<taskId>\d+),\s*"
        r"taskName:\s*(?P<taskName>.*?)\s+mobileListSize:\s*(?P<mobileListSize>\d+)\s*"
        r"areaSumCount:\s*(?P<areaSumCount>\d+)\s*"
        r"areaCountMap:\s*(?P<areaCountMap>\{.*\})",
        line
    )
    if not match:
        print(f"Warning: Could not parse line: {line.strip()}") # Added strip() for cleaner warning
        return None

    data = match.groupdict()
    # Crucially, strip whitespace from taskName as it's caught by '.*?'
    data['taskName'] = data['taskName'].strip() 
    
    area_map_str = data['areaCountMap']
    if area_map_str == "{}": # Handle empty map
        data['areaCountMap'] = {}
    else:
        # Preprocess area_map_str: '{key1=val1, key2=val2}' to '{"key1":"val1", "key2":"val2"}'
        # 1. Remove '{' and '}'
        processed_map_str = area_map_str[1:-1]
        # 2. Split into "key=value" pairs
        pairs = processed_map_str.split(', ') # Assuming consistent ", " delimiter
        
        formatted_pairs = []
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                # Add quotes around key and value (value is an int, but literal_eval can handle 'str_int')
                formatted_pairs.append(f"'{key.strip()}': '{value.strip()}'")
            else:
                # Handle potential malformed pair, or if a key has no value (though not expected by format)
                print(f"Warning: Malformed pair in areaCountMap for taskId {data.get('taskId')}: '{pair}'")

        final_map_str = "{" + ", ".join(formatted_pairs) + "}"
        
        try:
            data['areaCountMap'] = ast.literal_eval(final_map_str)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing areaCountMap for taskId {data.get('taskId')} after preprocessing: {e}")
            print(f"Original map string: {area_map_str}")
            print(f"Processed map string: {final_map_str}")
            data['areaCountMap'] = {} # Fallback to empty dict
    return data

def format_entry_to_table(entry):
    """
    Formats a parsed log entry into the specified table string.
    """
    if not entry:
        return ""

    lines = []
    key_width = 13
    value_width = 30 # Adjusted for a pipe character

    lines.append(f"| {'taskId'.ljust(key_width)} | {str(entry['taskId']).ljust(value_width)} |")
    lines.append(f"|{'-' * (key_width + 2)}|{'-' * (value_width + 2)}|")
    lines.append(f"| {'taskName'.ljust(key_width)} | {str(entry['taskName']).ljust(value_width)} |")
    lines.append(f"| {'areaSumCount'.ljust(key_width)} | {str(entry['areaSumCount']).ljust(value_width)} |")
    lines.append(f"| {'Area'.ljust(key_width)} | {'Count'.ljust(value_width)} |")
    lines.append(f"|{'-' * (key_width + 2)}|{'-' * (value_width + 2)}|")

    area_map = entry.get('areaCountMap', {})
    # Sort by count (descending), then by original order if counts are equal (Python's sort is stable)
    sorted_areas = sorted(area_map.items(), key=lambda item: int(item[1]), reverse=True)

    if not sorted_areas and not any(int(v) for v in area_map.values()): # if all counts are zero or map is empty
        # Keep original order if all counts are zero, as per rule.
        # ast.literal_eval preserves dict order from string in Python 3.7+
        # If specific original order (pre-dict string) is critical and varies, this might need adjustment.
        # For now, using items() which is insertion order for Py 3.7+
        original_order_areas = list(area_map.items())
        for area, count in original_order_areas:
            lines.append(f"| {str(area).ljust(key_width)} | {str(count).ljust(value_width)} |")
    else:
        for area, count in sorted_areas:
            lines.append(f"| {str(area).ljust(key_width)} | {str(count).ljust(value_width)} |")
    
    return "\n".join(lines)

def main():
    input_file = "rawLog.txt"
    output_file = "log_formated_result.txt"
    
    all_tables = []
    city_sum = {}
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                parsed_data = parse_log_line(line)
                ## every parsed_data areaCountMap the key is city, the value is number. Now i want to statistic all city's number and sum them up.
                if parsed_data:
                    table_str = format_entry_to_table(parsed_data)
                    all_tables.append(table_str)
                    ## statistic all city's number and sum them up.
                    for city, count in parsed_data['areaCountMap'].items():
                        if city in city_sum:
                            city_sum[city] += int(count)
                        else:
                            city_sum[city] = int(count)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return

    ## sort city_sum by value, descending
    sorted_city_sum = sorted(city_sum.items(), key=lambda item: item[1], reverse=True)
    formatted_city_sum = "\n".join([f"{city}: {count}" for city, count in sorted_city_sum])
    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write("\n\n\n".join(all_tables))
            f_out.write("\n\n\n")
            f_out.write(f"city_sum: \n{formatted_city_sum}")
        print(f"Successfully formatted log and wrote to '{output_file}'")
    except IOError:
        print(f"Error: Could not write to output file '{output_file}'.")

if __name__ == "__main__":
    main() 
