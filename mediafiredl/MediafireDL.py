# Import HTML parser
from bs4 import BeautifulSoup

# Import required modules
import requests
import os
import sys

# Import retry system
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Create reusable session
# Session keeps connections alive and behaves more browser-like
session = requests.Session()


# Fake browser headers
# Very important because MediaFire blocks simple python requests sometimes
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


# Configure retry logic
# Helps recover from random SSL disconnects
retry = Retry(
    total=5, # retry 5 times
    backoff_factor=1, # wait time between retries
    allowed_methods=["GET"] # retry GET requests only
)


# Attach retry handler to HTTPS requests
adapter = HTTPAdapter(max_retries=retry)

# Mount adapter into session
session.mount("https://", adapter)


# Get file name from URL
def GetName(url: str):

    # Take second last part of URL
    return url.split('/')[-2]


# Extract real MediaFire download link
def GetFileLink(url: str):

    try:

        # Download HTML page with headers + timeout
        response = session.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        # Raise exception if failed
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Find download button
        link = soup.find(id="downloadButton").get("href")

        return link

    except Exception as e:

        # Print error
        print(f"[GetFileLink Error] {e}")

        return e


# Get remote file size
def GetFileSize(url: str):

    try:

        # Get direct link first
        direct_link = GetFileLink(url)

        # Request file headers only
        with session.get(
            direct_link,
            headers=HEADERS,
            stream=True,
            timeout=30,
            verify=True # keep SSL verification enabled
        ) as r:

            # Raise error if request failed
            r.raise_for_status()

            # Return file size
            return int(r.headers.get('content-length', 0))

    except Exception as e:

        print(f"[GetFileSize Error] {e}")

        return 0


# Convert bytes into megabytes
def AsMegabytes(bytes: int):

    return round(bytes / 1024 / 1024, 2)


# Download multiple files
def BulkDownload(urls: list):

    # Count total files
    total_files = len(urls)

    print("[Bulk downloading files]")
    print(f"Total files: {total_files}")

    # Initial progress text
    sys.stdout.write("Total size: Analyzing...")

    total_bulk_size = 0

    # Calculate total size
    for url in urls:

        total_bulk_size += GetFileSize(url)

        sys.stdout.write(
            f"\x1b[2K\rTotal size: {AsMegabytes(total_bulk_size)}mb"
        )

        sys.stdout.flush()

    sys.stdout.write("\n")

    # Download files one by one
    for url in urls:

        Download(url)


# Main download function
def Download(url: str, output="", filename=""):

    # Auto filename if empty
    if not filename:

        filename = GetName(url)

    # Get real direct link
    url = GetFileLink(url)

    # Use current folder if output empty
    if not output:

        output = os.path.dirname(os.path.realpath(__file__))

    try:

        # Open download stream
        with session.get(
            url,
            headers=HEADERS,
            stream=True,
            timeout=30
        ) as r:

            # Raise error if failed
            r.raise_for_status()

            # Open local output file
            with open(f"{output}/{filename}", "wb") as f:

                # Get total file size
                total_length = int(
                    r.headers.get('content-length', 0)
                )

                # Current downloaded size
                download_progress = 0

                # Download chunks
                for chunk in r.iter_content(chunk_size=1024 * 64):

                    # Skip empty chunks
                    if not chunk:

                        continue

                    # Update downloaded bytes
                    download_progress += len(chunk)

                    # Write chunk into file
                    f.write(chunk)

                    # Calculate progress %
                    percentage = int(
                        100 * download_progress / total_length
                    ) if total_length else 0

                    # Current downloaded MB
                    mb_progress = round(
                        download_progress / 1024 / 1024,
                        2
                    )

                    # Total MB
                    mb_total_progress = round(
                        total_length / 1024 / 1024,
                        2
                    )

                    # Print progress
                    sys.stdout.write(
                        f"\r[Downloading {filename}] "
                        f"{percentage}% "
                        f"({mb_progress}mb/{mb_total_progress}mb)"
                    )

                    sys.stdout.flush()

        sys.stdout.write("\n")

        return f"{output}/{filename}"

    except Exception as e:

        print(f"\n[Download Error] {e}")

        return e
