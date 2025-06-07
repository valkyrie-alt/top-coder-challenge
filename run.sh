#!/bin/bash

# Black Box Challenge - Python Implementation
# This script takes three parameters and outputs the reimbursement amount
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

# Call the Python implementation - outputs only the number
python3 calculate_reimbursement_final.py "$1" "$2" "$3"
