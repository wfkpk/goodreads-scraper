# %%
import os
import json
import uuid
import zipfile
import requests

# %%
import requests
from bs4 import BeautifulSoup
import json

def scrape_website(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Error retrieving website. Status code: {response.status_code}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape the description
    description_element = soup.find('div', class_='DetailsLayoutRightParagraph__widthConstrained')
    description = description_element.get_text(strip=True) if description_element else ''

    # Scrape the genre list
    genre_list_element = soup.find('div', class_='BookPageMetadataSection__genres')
    genre_items = genre_list_element.find_all('a', class_='Button--tag-inline') if genre_list_element else []
    genres = [item.get_text(strip=True) for item in genre_items]

    # Create a dictionary with the scraped data
    data = {
        'description': description,
        'genres': genres
    }

    # Convert the dictionary to JSON
    json_data = json.dumps(data, indent=4)

    return json_data


# %%

i = 1

# Specify the filepath of the text file
filepath = r"C:\Users\krpra\Downloads\popular.txt"

# Read the file contents
with open(filepath, 'r') as file:
    contents = file.read()

# Split the file contents into words
words = contents.split()

# Store the JSON objects
json_objects = []

# Process each word
for word in words:
    if len(word) >= 3:
        # Call the API with the word as the query
        api_url = f"https://www.goodreads.com/book/auto_complete?format=json&q={word}"
        response = requests.get(api_url)

        # Process the API response
        if response.status_code == 200:
            api_data = response.json()
            # Process each object within the API response
            for obj in api_data:
                old_image_url = obj['imageUrl']
                # Remove the ending part between dots in the image URL
                image_url_parts = old_image_url.split('.')
                image_url = ".".join(image_url_parts[:-2]) + ".jpg"
                # Replace the image URL with the original URL
                obj['imageUrl'] = image_url

                # Remove unnecessary fields from the JSON object
                obj.pop('workId', None)
                obj.pop('qid', None)
                obj.pop('rank', None)

                # Generate a UUID for the object
                obj['id'] = str(uuid.uuid4())

                book_url=obj['bookUrl']
                print(book_url)
                # Scrape the website and extract description and genres
                json_data = scrape_website(f"https://www.goodreads.com{book_url}")
                book_data = json.loads(json_data)
                obj['description'] = book_data['description']
                obj['genres'] = book_data['genres']
                # Append the API object to the JSON objects list
                json_objects.append(obj)

        else:
            print(f"Error calling API for '{word}': {response.status_code}")

        # Check if the desired number of JSON objects is reached
        if len(json_objects) >= 2:
            # Create a new JSON file and save the objects
            file_name = f"D:/fs_{i}.json"  # Save to D: drive
            i = i + 1
            with open(file_name, 'w') as file:
                json.dump(json_objects, file)
            print(json_objects)
            # Clear the JSON objects list
            json_objects = []

# Check if there are any remaining JSON objects
if len(json_objects) > 0:
    # Create a new JSON file and save the remaining objects
    file_name = f"D:/fs_{i}.json"  # Save to D: drive
    with open(file_name, 'w') as file:
        json.dump(json_objects, file)

# Create a zip archive of the JSON files
zip_filename = "D:/json_files.zip"  # Save to D: drive
with zipfile.ZipFile(zip_filename, 'w') as zip_file:
    for filename in os.listdir('D:/'):
        if filename.startswith("fs_") and filename.endswith(".json"):
            zip_file.write(f"D:/{filename}")  # Save to D: drive

print("JSON files created and zip archive created successfully!")


# %%


