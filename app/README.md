# Introduction :book:
This README provides an overview for the deployment flow for the project generated from https://github.com/d-lab/mephisto template.

# Prerequisites :white_check_mark:
Before deploying, you must set the following variables/secrets in your Github Actions environment:

- DOTNETRC (Heroku .netrc file content with "" wrapped)
- HEROKU_API_KEY (Heroku API key)
- MTURK_ACCESS_KEY_ID (Mturk access key)
- MTURK_SECRET_ACCESS_KEY (Mturk secret key)
- PRIVATE_KEY (Private key for ssh access)
- AWS_ACCESS_KEY_ID (Key for uploading data to S3)
- AWS_SECRET_ACCESS_KEY (Key for uploading data to S3)

You also need to install the following tools:
- Docker (Desktop)

# Notes :notebook:
Please read the below notes carefully before starting your work:

- The practical deployment flow: local -> test -> prod
  - branch `deployment-test` for test/staging env
  - branch `deployment-prod` for production env 

- Refer to https://mephisto.ai/docs/guides/tutorials/first_task/ for other configuration details

- Please ensure that you have changed the taskname in hydra_config in test.yml and prod.yml. 
Note that Heroku app names for each cannot be duplicated and cannot exceed 30 characters ().
- There are some configs in hydra_config that are very sensitive and related to cost.
Please discuss with your manager before changing them.
  - `units_per_assignment`: number of units per assignment
  - `task_reward`: reward per unit

# How to start :triangular_flag_on_post:
1. Create a new repo from d-lab/mephisto template with `deployment` branch
2. Clone the new repo to your local machine
3. Switch to the `deployment` branch

## How to configure environment variables in github actions
1. You must be the owner of the repo to configure the environment variables
2. Go to Settings -> Secrets and variables -> Actions
3. New repository secret

## Local Deployment :hammer:
1. Start from the `deployment` branch
2. cd to `app` directory
3. Run `make build` to freshly build the docker image for the first time
4. Run `make run` to start the local server
5. Run `make watch` to build and watch the frontend
6. Start implementing your task in webapp/src

## Test Deployment :test_tube:
1. Once you are happy with your local version.
2. Make sure to config the hydra_config in **test.yml** and environment variables in github actions
3. Create a new branch from your current `deployment` branch and name it `deployment-test`
4. Push your changes to `deployment-test` branch to remote
5. View your deployment status in github actions

## Production Deployment :rocket:
1. Make sure to config the hydra_config in **prod.yml** and environment variables in github actions
2. Create a new branch from your current `deployment` branch and name it `deployment-prod`
3. Push your changes to `deployment-prod` branch to remote
4. Check github actions log for the deployment status and the production path to access the task
