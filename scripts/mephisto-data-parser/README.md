# DATA TRACKING APP

Create an app that allow users to track changes on input folder

## Installation
1. Install dependencies
```shell
pip install -r requirements.txt
```
2. Create a `.env` file and add the following variables
```shell
USER_INPUT_PATH=your_user_input_path
DATABASE_PATH=your_database_path
OUTPUT_CSV_PATH=your_output_csv_path

# Example
#USER_INPUT_PATH="./data/data/runs/NO_PROJECT/2"
#DATABASE_PATH="./data/database.db"
#OUTPUT_CSV_PATH="./output"
```
3. Run the app
```shell
python main.py
```