# Path to your original requirements.txt file
input_file_path = 'requirements.txt'
# Path to the output file (can be the same as input to overwrite)
output_file_path = 'requirements_without_versions.txt'

# Open the original file and create/update the new one
with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    for line in input_file:
        # Split the line at '==' and take the first part (the package name)
        package_name = line.split('==')[0]
        # Write the package name to the new file
        output_file.write(package_name + '\n')

print(f"Updated requirements written to {output_file_path}")
