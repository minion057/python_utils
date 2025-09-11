#!/bin/bash

# [Information]
# Command execution example: bash script.sh file_list.txt
# how to make file list: find {absolute path} -name "*.ipynb" | sort > file_list.txt
# [Important Notice]
# Text files must always end with a blank line to be executed completely. 

# [Positional Argument]
# 1. path of `txt` file: Path to the text file consisting of absolute paths of files to be executed.  
FILE_LIST_PATH=$1
# 2. List of CPU cores to use. 
# For example: 1, 10-55, "no input" or if not entered, default value is applied.  
TASKSET_LIST=${2:-"no input"}

# [Parameter]
# 1. Command to execute
COMMAND="jupyter nbconvert --execute --to notebook --inplace"
if [ "$TASKSET_LIST" != "no input" ]; then
    COMMAND="taskset -c $TASKSET_LIST jupyter nbconvert --execute --to notebook --inplace"
fi
echo "Using command: $COMMAND"
# 2. Execution time
TOTAL_RUNTIME=0

# [Step 1]
# Read a text file line by line and check if the file path exists.  
if [ ! -f "$FILE_LIST_PATH" ]; then
    echo "Error: File list path is not valid."
    exit 1
fi

# [Step 2]
# Execute commands for each file path. 
while IFS= read -r FILE_PATH; do
    if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" == \#* ]] || [[ "$FILE_PATH" == '//'* ]]; then
        continue # Skip lines that are blank or start with # or // without executing the command.
    fi
    
    echo "Processing file: $FILE_PATH"
    
    START=$(date +%s)
    if ! $COMMAND "$FILE_PATH"; then
        echo "Error occurred while processing the file."
    fi
    END=$(date +%s)
    RUNTIME=$((END - START))
    
    HOURS=$((RUNTIME / 3600))
    MINUTES=$(( (RUNTIME % 3600) / 60 ))
    SECONDS=$((RUNTIME % 60))
    
    # Print the time taken for each file execution.
    echo "Start Time: $(date -d @"$START" '+%Y-%m-%d %H:%M:%S')"
    echo "End Time: $(date -d @"$END" '+%Y-%m-%d %H:%M:%S')"
    echo "Runtime: $HOURS hours, $MINUTES minutes, $SECONDS seconds"
    echo ""
    
    TOTAL_RUNTIME=$((TOTAL_RUNTIME + RUNTIME))
    
    echo ""
done < "$FILE_LIST_PATH"

# Print the total time taken for all files. 
TOTAL_HOURS=$((TOTAL_RUNTIME / 3600))
TOTAL_MINUTES=$(( (TOTAL_RUNTIME % 3600) / 60 ))
TOTAL_SECONDS=$((TOTAL_RUNTIME % 60))
echo "Total Runtime: $TOTAL_HOURS hours, $TOTAL_MINUTES minutes, $TOTAL_SECONDS seconds"
