import os
import re
import subprocess

def convert_obsidian_to_standard_markdown(content):
    # Example conversion rules
    content = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', r'[\2](\1)', content)  # Convert [[link|text]] to [text](link)
    content = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](\1)', content)  # Convert [[link]] to [link](link)
    
    # Fix image with width pattern
    content = re.sub(r'!\[(\d+)\]\(([^\)]+)\)', r'![](\2){width=\1px}', content)  # Convert ![width](image) to ![](image){width=Xpx}
    
    # Handle Obsidian-style images
    content = re.sub(r'!\[\[([^|\]]+)\|(\d+)\]\]', r'![](\1){width=\2px}', content)  # Convert ![[image|width]] to ![](image){width=Xpx}
    content = re.sub(r'!\[\[([^\]]+)\]\]', r'![](\1)', content)  # Convert ![[image]] to ![](image)
    
    content = re.sub(r'> \[!(TIP|Tip|tip)\] (.+)', r'> \2', content, flags=re.IGNORECASE)  # Convert [!tip] block to standard blockquote (case insensitive)
    content = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', content, flags=re.MULTILINE)  # Ensure space after # in headers
    
    # Process headers - ensure empty lines around headers and force line break after header
    lines = content.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        # Check if line is a header (starts with # after trimming)
        is_header = line.lstrip().startswith('#')
        
        # Add empty line before header if needed
        if is_header and i > 0 and processed_lines and processed_lines[-1].strip():
            processed_lines.append('')
            
        processed_lines.append(line)
        
        # Always add empty line after header
        if is_header:
            processed_lines.append('')
    
    content = '\n'.join(processed_lines)
    
    # Process lists - add empty lines before and after each list item (both bullet and numbered lists)
    lines = content.split('\n')
    processed_lines = []
    prev_line_was_list = False
    
    for i, line in enumerate(lines):
        # Check for bullet lists or numbered lists
        current_line_is_list = (line.lstrip().startswith('- ') or 
                               re.match(r'^\s*\d+[\)\.]\s', line.lstrip()))
        
        # Add empty line before list item if needed
        if current_line_is_list and not prev_line_was_list and i > 0:
            processed_lines.append('')
            
        processed_lines.append(line)
        
        # Add empty line after list item if next line is not a list
        if current_line_is_list and i < len(lines)-1:
            next_line_is_list = (lines[i+1].lstrip().startswith('- ') or 
                                re.match(r'^\s*\d+[\)\.]\s', lines[i+1].lstrip()))
            if not next_line_is_list:
                processed_lines.append('')
                
        prev_line_was_list = current_line_is_list
    
    content = '\n'.join(processed_lines)
    return content

def run_pandoc(markdown_file, output_dir):
    original_dir = os.getcwd()
    try:
        os.chdir(output_dir)
        pdf_filename = os.path.splitext(markdown_file)[0] + '.pdf'
        
        # Get path to local eisvogel template
        template_path = os.path.join(os.path.dirname(__file__), "eisvogel.tex")
        
        # Run pandoc command with local eisvogel template and additional options for better image handling
        cmd = (f'pandoc "{markdown_file}" -o "{pdf_filename}" '
               f'--from markdown --template="{template_path}" '
               f'--listings --pdf-engine=xelatex '
               f'--wrap=preserve '  # Preserve line wrapping
               f'--extract-media=. '  # Extract embedded images
               f'-f markdown-implicit_figures')  # Disable implicit figures
        
        subprocess.run(cmd, shell=True, check=True)
        print(f"PDF generated: {pdf_filename}")
    
    finally:
        os.chdir(original_dir)

def process_markdown_file(input_filepath):
    with open(input_filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    converted_content = convert_obsidian_to_standard_markdown(content)

    output_dir = os.path.join(os.path.dirname(input_filepath), 'Attachments')
    os.makedirs(output_dir, exist_ok=True)

    input_filename = os.path.basename(input_filepath)
    output_filename = f"{os.path.splitext(input_filename)[0]} pandoc export.md"
    output_filepath = os.path.join(output_dir, output_filename)

    try:
        # Write temporary markdown file
        with open(output_filepath, 'w', encoding='utf-8') as file:
            file.write(converted_content)

        # Run pandoc to generate PDF
        run_pandoc(output_filename, output_dir)

    finally:
        # Clean up temporary markdown file
        if os.path.exists(output_filepath):
            os.remove(output_filepath)
            print(f"Cleaned up temporary markdown file: {output_filepath}")

    print(f"Converted file saved to: {output_filepath}")

if __name__ == "__main__":
    input_filepath = r".\\010 Masterstudium\\Manufacturing and Robotics\\1. Semester\\VU Robot Challenge\\Lecture Notes\\L1 - Challenges of HRI in Manufacturing.md"  # Hardcoded file path
    process_markdown_file(input_filepath)

