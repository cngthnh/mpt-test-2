#!/bin/sh

rm -rf node_modules
rm package-lock.json
current_dir=$(pwd)

# Link the mephisto-task package
cd /mephisto/packages/mephisto-task
npm link

# Link the annotator-tracker package
cd /mephisto/packages/annotated/annotator-tracker
npm link

cd $current_dir
npm link mephisto-task @annotated/annotator-tracker
npm install
