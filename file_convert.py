import codecs

# Read the file with UTF-16 encoding and write it back with UTF-8 encoding
input_file = 'requirements.txt'
output_file = 'requirements-utf8.txt'

try:
    with codecs.open(input_file, 'r', 'utf-16') as f:
        content = f.read()
    with codecs.open(output_file, 'w', 'utf-8') as f:
        f.write(content)
    print(f"File converted successfully to {output_file}.")
except Exception as e:
    print(f"Error: {e}")
