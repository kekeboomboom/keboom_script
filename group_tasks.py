import re
from collections import defaultdict
import os
import argparse

def get_model_series(task_name):
    """
    Extracts the model series from a task name based on a set of predefined regex patterns.
    The patterns are ordered from most specific to most general to ensure correct matching.
    """
    patterns = [
        # Explicit groups for xm_jj and gzy (should take precedence)
        (re.compile(r'yx_gzy_jj'), 'gzy'),      # e.g., yx_gzy_jj_* -> gzy
        (re.compile(r'xm_jj'), 'xm_jj'),        # e.g., xm_jj_* -> xm_jj
        # Custom overrides for Uncategorized items requested by user
        # Map specific jj series
        (re.compile(r'jj_A\d+'), 'jj_A'),  # e.g., jj_A01_* -> jj_A
        # Map Y-series for dates 0725/0726/0727 to jj_Y
        (re.compile(r'xm_jj_Y\d+_072[5-7]'), 'jj_Y'),
        # Map jy-series for dates 0716 and 0724 to jj_jy
        (re.compile(r'xm_jj_jy_07(16|24)'), 'jj_jy'),
        # lt_LKltjja Series (e.g., lt_LKltjja20-3)
        (re.compile(r'lt_LKltjja[\d-]+'), 'full_match'),
        # lt_LXjja Series (e.g., lt_LXjja25-1, lt_LXjja25-2)
        (re.compile(r'lt_LXjja[\d-]+'), 'full_match'),
        # lt_LKjja Series (e.g., lt_LKjja20-3)
        (re.compile(r'lt_LKjja[\d-]+'), 'full_match'),
        # lt_jja Series (e.g., lt_jja22-3, lt_jja22-2-9)
        (re.compile(r'lt_jja[\d.-]+'), 'full_match'),
        # lt_ltjja Series (e.g., lt_ltjja20-3, lt_ltjja20-2)
        (re.compile(r'lt_ltjja[\d-]+'), 'full_match'),
        # LKXjja Series (e.g., LKXjja22-3)
        (re.compile(r'LKXjja[\d-]+'), 'full_match'),
        # LKjja Series (e.g., LKjja20-3)
        (re.compile(r'LKjja[\d-]+'), 'full_match'),
        # Lk12a20-1 (very specific case)
        (re.compile(r'Lk12a20-1'), 'full_match'),
        # jja Series (e.g., jja20-3, jja20-2)
        (re.compile(r'jja[\d-]+'), 'full_match'),
        # LXda Series (e.g., LXda11-1 -> LXda11)
        (re.compile(r'LXda\d+'), 'full_match'),
        # LXd Series (e.g., LXd10-1, LXd10-2 -> LXd10)
        (re.compile(r'LXd\d+'), 'full_match'),
        # x Series (e.g., x210)
        (re.compile(r'x\d+'), 'full_match'),
        # u Series (e.g., u260, u244)
        (re.compile(r'u\d+'), 'full_match'),
        # rt_dj Series (handles variants like rt_dj and rt-dj)
        (re.compile(r'rt[_-]dj'), 'rt_dj'),
        # rz_dj Series
        (re.compile(r'rz_dj'), 'static'),
        # rz_bc Series (handles both rz_bc and rz-bc)
        (re.compile(r'rz[_-]bc'), 'rz_bc'),
        # apbc Series (e.g., apbc1, apbc33)
        (re.compile(r'apbc\d+'), 'full_match'),
        # bc-v Series (e.g., bc-v22 -> v22, bc_v20 -> v20, kj-bc-v20 -> v20)
        (re.compile(r'(?<=bc[_-])v\d+'), 'full_match'),
        # Standalone v20 entries (e.g., v20-0610, v20-bc-0612)
        (re.compile(r'v20(?=[-_]|\s)'), 'v20'),
        # Special case for 0611-bc (should be bc series)
        (re.compile(r'\d{4}-bc'), 'bc'),
        # bc01 Series (including date prefixes like 0628_bc01)
        (re.compile(r'bc0\d+'), 'full_match'),
        # rt_bc Series (e.g., rt_bc_0626)
        (re.compile(r'rt_bc'), 'static'),
        # bc Series (e.g., bc_0420 -> bc)
        (re.compile(r'bc(?=_)'), 'static'),
    ]

    for pattern, match_type in patterns:
        match = pattern.search(task_name)
        if match:
            if match_type == 'full_match':
                return match.group(0)
            elif match_type == 'static':
                return pattern.pattern
            else:
                # Handle custom return values like 'rt_dj'
                return match_type
    return None

def group_tasks_by_series(input_file):
    """
    Reads task names from a file, groups them by model series, and returns a dictionary.
    """
    task_groups = defaultdict(list)
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                task_name = line.strip()
                if not task_name:
                    continue
                series = get_model_series(task_name)
                if series:
                    task_groups[series].append(task_name)
                else:
                    task_groups['Uncategorized'].append(task_name)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return None
    return task_groups

def write_groups_to_markdown(task_groups, output_file):
    """
    Writes the grouped tasks to a markdown file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Model Series Groups\n\n")
        # Sort series alphabetically, but handle 'Uncategorized' last.
        sorted_series = sorted(
            task_groups.keys(),
            key=lambda x: (x == 'Uncategorized', x)
        )
        for series in sorted_series:
            f.write(f"## Series: {series}\n\n")
            for task_name in sorted(task_groups[series]):
                f.write(f"- `{task_name}`\n")
            f.write('\n')

def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description="Group task names by model series from an input file and write to a markdown file.")
    parser.add_argument("input_file", help="Path to the input file with task names.")
    parser.add_argument("output_file", help="Path for the output markdown file.")
    args = parser.parse_args()
    
    task_groups = group_tasks_by_series(args.input_file)
    if task_groups:
        write_groups_to_markdown(task_groups, args.output_file)
        print(f"Successfully grouped tasks from '{args.input_file}' and created '{os.path.abspath(args.output_file)}'")

if __name__ == "__main__":
    main() 
