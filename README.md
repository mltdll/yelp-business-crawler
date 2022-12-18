# yelp-business-crawler
A utility for scraping businesses from yelp.com written with scrapy. 

## Installation

### Prerequisites
* Python 3.10+

### Steps to install
1. Clone the repository:
   ```shell
   git clone https://github.com/mltdll/yelp-business-crawler.git
   ```
2. Install requirements:
   ```shell
   pip install -r requirements.txt
   ```

## Usage
### Running the script
1. Run the spider (`-o business.json` in the example saves results
   to the `business.json` file):
   ```shell
   scrapy crawl business -o businesses.json 
   ```
2. Input category, location, and the number of pages to scrap as prompted.

### Example output
![output_file_image.jpeg](examples%2Foutput_file_image.jpeg)