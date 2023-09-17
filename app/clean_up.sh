mephisto_data_root="/mephisto/data"

mephisto_script_root="/mephisto/scripts"

task_path_prefix="$mephisto_data_root/data/runs/NO_PROJECT/"

db_path="$mephisto_data_root/database.db"

task_path=$task_path_prefix$(ls -t $task_path_prefix | head -1)

python_exec=$(which python3)

csv_path=$(echo $task_path | sed 's/NO_PROJECT/parsed/g')"-csv"

cd $mephisto_script_root/mephisto-data-parser/src

echo "Running data parser on task: $task_path"

echo "Saving output to: $csv_path"

$python_exec main.py $task_path $db_path $csv_path