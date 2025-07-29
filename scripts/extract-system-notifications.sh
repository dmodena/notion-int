#!/bin/bash

echo "Starting..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

EN_INPUT_FILE="$SCRIPT_DIR/../src/assets/i18n/en.json"
NO_INPUT_FILE="$SCRIPT_DIR/../src/assets/i18n/no.json"
EN_OUTPUT_FILE="$SCRIPT_DIR/../tmp/en-system-notifications.csv"
NO_OUTPUT_FILE="$SCRIPT_DIR/../tmp/no-system-notifications.csv"

if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install jq first."
  exit 1
fi

if [ ! -f "$EN_INPUT_FILE" ]; then
  echo "Error: English input file '$EN_INPUT_FILE' not found."
  exit 1
fi


if [ ! -f "$NO_INPUT_FILE" ]; then
  echo "Error: Norwegian input file '$NO_INPUT_FILE' not found."
  exit 1
fi

mkdir -p "$SCRIPT_DIR/../tmp"

process_language_file() {
  local input_file="$1"
  local output_file="$2"
  local language="$3"

  echo "Processing $languge file..."

  echo "Type,Code,Summary,Detail" > "$output_file"

  jq -r '
  .SystemNotifications |
  to_entries[] |
  select(.key as $type | .value | type == "object") |
  .key as $type |
  .value |
  to_entries[] |
  [$type, .key, .value.Summary, .value.Detail] |
  @csv
  ' "$input_file" >> "$output_file"

  echo "SystemNotifications extracted to '$output_file'"
}

process_language_file "$EN_INPUT_FILE" "$EN_OUTPUT_FILE" "English"
process_language_file "$NO_INPUT_FILE" "$NO_OUTPUT_FILE" "Norwegian"

echo "Processing complete."
