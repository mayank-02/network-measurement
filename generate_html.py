# Define the repetitive content
paragraph = "<p>" + "This is a test paragraph. " * 500 + "</p>\n"

# Open the file for writing
with open("large_file_4gb.html", "w") as file:
    # Start the HTML structure
    file.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Large HTML File</title>
</head>
<body>
    <h1>Testing Large HTML File</h1>
""")
    
    # Write paragraphs incrementally
    for _ in range(330000):  # Adjust the number of repetitions for 4 GB file
        file.write(paragraph)

    # End the HTML structure
    file.write("""
</body>
</html>
""")

print("4 GB HTML file generated successfully!")

