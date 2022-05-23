# Data-Collection-Pipeline



## Milestone 1

- Created methods to navigate pages in [depop.com](https://www.depop.com/) with Selenium. The intention is to collect data of from produc listings that show up on the top of search pages.

- Methods created can be used to navigating to a search page, navigate to a store front on depop, going back to the previous webpage, scrolling, openening tabs, switching tabs, closing tabs etc.

## Milestone 2

- Additional methods were added to expand the functionality of the class.

- These new methods allow scrapping data (including downloading images) from a specific product lising on depop, as well as scrapping data from depop stores.

- Scrapped data is then stores with a unique ID, adn stored in a dictionary.

## Milestone 3

- Docstrings are added to methods created.

- Unit tests are created for all implemented methods.

## Milestone 4

- Additional methods are created to: upload scraped data and images to AWS S3, and upload tabular data to AWS RDS.

## Milestone 5

- Created methods to check if scraped data is already stored locally or on AWS, to prevent storing duplicates.

- Created a Docker image that runs the scraper.

## Milestone 6

- Ran Docker image on the AWS EC2 instance,

- Set up a Prometheus container to monitor scraper on EC2, as well as a node-exporter to monitor hardware metrics of the EC2.

- Created a Grafana dashboard to visualise these metrics

## Milestone 7

- Set up a CI/CD pipeline for the created Docker image, that automatically builds a new docker image and pushes it to Dockerhub whenever a oush action is triggered on the main branch of the github repository.

- Created a crojob that restarts the scraper every day.
