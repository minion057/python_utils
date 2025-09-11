#!/bin/bash

# [Information]
# Command execution example: bash script.sh file_list.txt
# how to make file list: find {absolute path} -name "*.ipynb" | sort > file_list.txt
# [Important Notice]
# Text files must always end with a blank line to be executed completely. 

# [Argument: Option]
# 1. path of `txt` file: Path to the text file consisting of absolute paths of files to be executed.  
FILE_LIST_PATH=""
# 2. List of CPU cores to use. 
# For example: 1, 10-55, "no input" or if not entered, default value is applied.  
TASKSET_LIST="no input"
# 3. Variables required in Python. 
GPU_FLAG=""
VF_FLAG=""
BOOL_FLAG=""

# [Parameter]
# 1. Code path
WORKSPACE="/home/user/Code"
RUN_FILE="$WORKSPACE/runfile/train_pytorch_lightning.py"
# 2. Execution time
TOTAL_RUNTIME=0

# [Step 1]
# Assign the received options to each variable.
while [[ $# -gt 0 ]]; do
    case "$1" in
        -f)
            FILE_LIST_PATH="$2"
            shift 2
            ;;
        -c)
            TASKSET_LIST="$2"
            shift 2
            ;;
        -g)
            GPU_FLAG="--device $2 -n 1"
            shift 2
            ;;
        -vf)
            VF_FLAG="--val_fold $2"
            shift 2
            ;;
        -b)
            BOOL_FLAG="$2"
            shift 2
            ;;
        *)
            echo "[ERROR] Unknown option: $1"
            exit 1
            ;;
    esac
done

# [Step 2]
# Read a text file line by line and check if the file path exists.  
if [ ! -f "$FILE_LIST_PATH" ]; then
    echo "[ERROR] File list path is not valid: $FILE_LIST_PATH"
    exit 1
fi

# [Step 3]
# According to the received options, configure the variables and commands to be used in Python as arrays.  
BASE_COMMAND=(python3 -u "$RUN_FILE")
# Split options containing spaces into arrays. 
if [ -n "$GPU_FLAG" ]; then
    read -ra GPU_ARGS <<< "$GPU_FLAG"
    BASE_COMMAND+=("${GPU_ARGS[@]}")
fi
if [ -n "$VF_FLAG" ]; then
    read -ra VF_ARGS <<< "$VF_FLAG"
    BASE_COMMAND+=("${VF_ARGS[@]}")
fi
# Options that are just entered, like store_true, are simply added. 
if [ -n "$BOOL_FLAG" ]; then
    BASE_COMMAND+=("$BOOL_FLAG")
fi
# Add things other than Python commands.  
if [ "$TASKSET_LIST" != "no input" ]; then
    COMMAND=(taskset -c "$TASKSET_LIST" "${BASE_COMMAND[@]}")
else
    COMMAND=("${BASE_COMMAND[@]}")
fi
# Print the final options and commands. 
echo "[INFO] -------------------- ARGS --------------------"
echo "[INFO] FILE_LIST_PATH: $FILE_LIST_PATH"
echo "[INFO] TASKSET_LIST: $TASKSET_LIST"
echo "[INFO] GPU_FLAG: $GPU_FLAG"
echo "[INFO] SEED: $SEED"
echo "[INFO] VALFOLD_FLAG: $VF_FLAG"
echo "[INFO] MODEL_FLAG: $MO_FLAG"
echo "[INFO] SCALER_FLAG: $SC_FLAG"
echo "[INFO] GCBIAS_FLAG: $GCBIAS_FLAG"
echo "[INFO] ----------------------------------------------"
echo "[INFO] COMMAND: ${COMMAND[*]}"
echo "[INFO] RUN!!!"
echo ""

# [Step 3]
# Write the necessary functions for Python. 
train() {
    local config_path="$1"
    local output
    local status

    output=$("${COMMAND[@]}" -c "$config_path")
    status=$?
    if [ $status -ne 0 ]; then
        echo "[ERROR] Error occurred while training and processing the file: $config_path"
        exit 1
    fi
    echo "$output"
}

test_file() {
    local test_model_path="$1"
    local status

    "${COMMAND[@]}" -r "$test_model_path" -te -ot
    status=$?
    if [ $status -ne 0 ]; then
        echo "[ERROR] Error occurred while testing and processing the file: $test_model_path"
        exit 1
    fi
}

# [Step 4]
# Execute commands for each file path. 
while IFS= read -r FILE_PATH; do
    if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" == \#* ]] || [[ "$FILE_PATH" == '//'* ]]; then
        continue # Skip lines that are blank or start with # or // without executing the command.
    fi

    echo "[INFO] Processing file: $FILE_PATH"

    START=$(date +%s)

    # Check the file extension.
    # If the file extension is json, treat it as a config and perform training; otherwise, perform model testing.  
    EXT="${FILE_PATH##*.}"
    if [ "$EXT" == "json" ]; then
        TEST_MODEL_PATH=$(train "$FILE_PATH")
        echo "[INFO] Train output: $TEST_MODEL_PATH"

        if [ -e "$TEST_MODEL_PATH" ]; then
            echo "[INFO] Test file: $TEST_MODEL_PATH"
        else
            echo "[WARN] Test file not found: $TEST_MODEL_PATH"
            exit 1
        fi
        test_file "$TEST_MODEL_PATH"
    else
        test_file "$FILE_PATH"
    fi
    END=$(date +%s)
    RUNTIME=$((END - START))

    HOURS=$((RUNTIME / 3600))
    MINUTES=$(((RUNTIME % 3600) / 60))
    SECONDS=$((RUNTIME % 60))

    # Print the time taken for each file execution.
    echo "[INFO] Start Time: $(date -d @"$START" '+%Y-%m-%d %H:%M:%S')"
    echo "[INFO] End Time: $(date -d @"$END" '+%Y-%m-%d %H:%M:%S')"
    echo "[INFO] Runtime: $HOURS hours, $MINUTES minutes, $SECONDS seconds"
    echo ""

    TOTAL_RUNTIME=$((TOTAL_RUNTIME + RUNTIME))
done < "$FILE_LIST_PATH"

# Print the total time taken for all files. 
TOTAL_HOURS=$((TOTAL_RUNTIME / 3600))
TOTAL_MINUTES=$(((TOTAL_RUNTIME % 3600) / 60))
TOTAL_SECONDS=$((TOTAL_RUNTIME % 60))
echo "[INFO] Total Runtime: $TOTAL_HOURS hours, $TOTAL_MINUTES minutes, $TOTAL_SECONDS seconds"