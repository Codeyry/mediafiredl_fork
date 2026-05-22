# mediafiredl_fork

A simple Python package for downloading files from MediaFire links.

This fork adds small changes to make requests look more like a normal browser and exposes progress data so it can be used in CLI apps, Telegram bots, Discord bots, and other tools.

## Features

- Get the file name from a MediaFire link
- Get the direct download link
- Get the file size
- Convert bytes to megabytes
- Download one file
- Download multiple files
- Read live download progress data

## Installation

```bash
pip install mediafiredl-fork
```

## Requirements

- `beautifulsoup4==4.14.3`
- `requests==2.33.1`
- `urllib3==2.6.3`

## Usage

```python
from mediafiredl_fork import Download, GetName, GetFileLink, GetFileSize, AsMegabytes

url = "https://www.mediafire.com/file/ipnyzofjcwri357/test-10mb.bin/file"

file_name = GetName(url)
file_link = GetFileLink(url)
file_size = GetFileSize(url)
file_size_mb = AsMegabytes(file_size)

print(file_name)
print(file_link)
print(file_size_mb)
```

## Download A File

```python
from mediafiredl_fork import Download

url = "https://www.mediafire.com/file/ipnyzofjcwri357/test-10mb.bin/file"

for progress in Download(url):
    filename, percentage, speed, eta, downloaded_mb, total_mb = progress
    print(filename, percentage, speed, eta, downloaded_mb, total_mb)
```

## Custom Output

```python
from mediafiredl_fork import Download

url = "https://www.mediafire.com/file/ipnyzofjcwri357/test-10mb.bin/file"

for progress in Download(url, output="C:\\Users\\User\\Desktop"):
    print(progress)
```

## Bulk Download

```python
from mediafiredl_fork import BulkDownload

bulk_urls = [
    "url1",
    "url2",
    "url3",
]

BulkDownload(bulk_urls)
```

## Contact

- Telegram: `Codeyry`
- GitHub: `Codeyry`

## License

This project is free to use, edit, and fork for personal, educational, and non-commercial use.

You cannot sell this project, sell modified versions, use it in paid/commercial products, remove author credit, or use it for illegal activity. See [LICENSE](LICENSE) for details.

## Note

Use this package only for files you are allowed to download.
