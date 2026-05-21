# Import HTML parser
from bs4 import BeautifulSoup

# Import required modules
import requests
import os
import time
import sys

# Import retry system
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Create reusable session
session = requests.Session()


# Fake browser headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


# Retry config
retry = Retry(
    total=5, # retry failed requests 5 times
    backoff_factor=1, # delay between retries
    allowed_methods=["GET"] # retry only GET requests
)


# Enable retries for HTTPS
adapter = HTTPAdapter(max_retries=retry)

# Mount adapter into session
session.mount("https://", adapter)


# Get filename from MediaFire page URL
def GetName(url: str):

    # Split URL and take second last part
    return url.split("/")[-2]


# Extract real MediaFire direct link
def GetFileLink(url: str):

    try:

        # Download MediaFire HTML page
        response = session.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        # Raise error if request failed
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        # Find download button href
        link = soup.find(
            id="downloadButton"
        ).get("href")

        return link

    except Exception as e:

        print(f"[GetFileLink Error] {e}")

        return None


# Get remote file size
def GetFileSize(url: str):

    try:

        # Get direct download URL
        direct_link = GetFileLink(url)

        # Request file headers
        with session.get(
            direct_link,
            headers=HEADERS,
            stream=True,
            timeout=30
        ) as r:

            # Raise HTTP errors
            r.raise_for_status()

            # Return content length
            return int(
                r.headers.get(
                    "content-length",
                    0
                )
            )

    except Exception as e:

        print(f"[GetFileSize Error] {e}")

        return 0


# Convert bytes into MB
def AsMegabytes(bytes: int):

    return round(
        bytes / 1024 / 1024,
        2
    )


# Download multiple files
def BulkDownload(urls: list):

    # Count total files
    total_files = len(urls)

    print("[Bulk downloading files]")
    print(f"Total files: {total_files}")

    # Show analyzing text
    sys.stdout.write(
        "Total size: Analyzing..."
    )

    total_bulk_size = 0

    # Calculate total size
    for url in urls:

        total_bulk_size += GetFileSize(url)

        sys.stdout.write(
            f"\x1b[2K\rTotal size: "
            f"{AsMegabytes(total_bulk_size)}mb"
        )

        sys.stdout.flush()

    sys.stdout.write("\n")

    # Download all files
    for url in urls:

        Download(url)


# Main download function
def Download(
    url: str,
    output="",
    filename=""
):

    # Auto filename
    if not filename:

        filename = GetName(url)

    # Get real download URL
    url = GetFileLink(url)

    # Use current directory if output empty
    if not output:

        output = os.path.dirname(
            os.path.realpath(__file__)
        )

    try:

        # Open download request
        with session.get(
            url,
            headers=HEADERS,
            stream=True,
            timeout=30
        ) as r:

            # Raise HTTP errors
            r.raise_for_status()

            # Total file size
            total_length = int(
                r.headers.get(
                    "content-length",
                    0
                )
            )

            # Downloaded bytes counter
            download_progress = 0

            # Start timer ONCE
            start = time.time()

            # Open output file
            with open(
                f"{output}/{filename}",
                "wb"
            ) as f:

                # Download chunks
                for chunk in r.iter_content(
                    chunk_size=1024 * 64
                ):

                    # Skip empty chunks
                    if not chunk:

                        continue

                    # Save chunk
                    f.write(chunk)

                    # Increase progress
                    download_progress += len(chunk)

                    # Elapsed seconds
                    elapsed = (
                        time.time() - start
                    )

                    # Prevent divide by zero
                    if elapsed <= 0:

                        elapsed = 0.001

                    # Percentage
                    percentage = int(
                        (
                            download_progress /
                            total_length
                        ) * 100
                    ) if total_length else 0

                    # Current downloaded MB
                    mb_progress = round(
                        download_progress /
                        1024 / 1024,
                        2
                    )

                    # Total MB
                    mb_total_progress = round(
                        total_length /
                        1024 / 1024,
                        2
                    )

                    # Bytes per second
                    bytes_speed = (
                        download_progress /
                        elapsed
                    )

                    # Speed MB/s
                    speed = round(
                        bytes_speed /
                        1024 / 1024,
                        2
                    )

                    # ETA seconds
                    eta = round(
                        (
                            total_length -
                            download_progress
                        ) / bytes_speed,
                        2
                    ) if bytes_speed > 0 else 0

                    # Console progress
                    sys.stdout.write(
                        f"\r[Downloading {filename}] "
                        f"{percentage}% "
                        f"({mb_progress}mb/"
                        f"{mb_total_progress}mb) "
                        f"{speed} MB/s "
                        f"ETA: {eta}s"
                    )

                    sys.stdout.flush()

                    # Return live data
                    yield (
                        filename,
                        percentage,
                        speed,
                        eta,
                        mb_progress,
                        mb_total_progress
                    )

        # New line after download
        sys.stdout.write("\n")

        # Return final filepath
        return f"{output}/{filename}"

    except Exception as e:

        print(f"\n[Download Error] {e}")

        return e
